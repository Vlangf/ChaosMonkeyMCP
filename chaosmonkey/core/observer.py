"""
ChaosMonkey AI - System Observer

Observes system state, collects logs, and gathers metrics during chaos experiments.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from chaosmonkey.core.models import ObservationResult, CrashReport


class SystemObserver:
    """
    Observes system state and collects diagnostic information.
    
    This class handles:
    - Log collection and parsing
    - Traceback extraction
    - Metrics gathering
    - System state monitoring
    """
    
    def __init__(self):
        """Initialize system observer."""
        pass
    
    def read_logs(
        self,
        target_path: str,
        lines: int = 50,
        filter_pattern: Optional[str] = None
    ) -> List[str]:
        """
        Read application logs.
        
        TODO: Implement log reading from various sources:
        - File-based logs
        - stdout/stderr capture
        - System logs
        - Container logs
        
        Args:
            target_path: Path to target application or log file
            lines: Number of lines to read
            filter_pattern: Optional regex pattern to filter logs
            
        Returns:
            List of log lines
        """
        # TODO: Implement log reading
        return []
    
    def inspect_traceback(self, crash_report: CrashReport) -> Optional[str]:
        """
        Extract and format traceback from crash report.
        
        Args:
            crash_report: Crash report containing traceback
            
        Returns:
            Formatted traceback string
        """
        return crash_report.traceback
    
    def get_metrics(
        self,
        target_path: str,
        metric_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Gather system metrics.
        
        TODO: Implement metrics collection:
        - CPU usage
        - Memory usage
        - Network I/O
        - Disk I/O
        - Custom application metrics
        
        Args:
            target_path: Path to target application
            metric_type: Type of metrics to collect ("cpu", "memory", "network", "all")
            
        Returns:
            Dictionary of metrics
        """
        # TODO: Implement metrics collection
        return {}
    
    def observe(
        self,
        crash_report: Optional[CrashReport] = None,
        target_path: Optional[str] = None
    ) -> ObservationResult:
        """
        Perform comprehensive system observation.
        
        Args:
            crash_report: Optional crash report to include
            target_path: Optional target path for log/metric collection
            
        Returns:
            ObservationResult with all collected data
        """
        logs = []
        traceback = None
        metrics = {}
        
        if target_path:
            logs = self.read_logs(target_path)
            metrics = self.get_metrics(target_path)
        
        if crash_report:
            traceback = self.inspect_traceback(crash_report)
        
        return ObservationResult(
            logs=logs,
            traceback=traceback,
            metrics=metrics,
            crash_report=crash_report
        )
    
    def read_source_file(self, file_path: str) -> Optional[str]:
        """
        Read source code from a file.
        
        Args:
            file_path: Path to the source file
            
        Returns:
            Source code as string, or None if file cannot be read
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return None
    
    def generate_chaos_report(
        self,
        crash_report: CrashReport,
        original_payload: Dict[str, Any],
        mutated_payload: Dict[str, Any],
        target_name: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Generate a structured chaos report.
        
        Args:
            crash_report: Crash report from execution
            original_payload: Original input payload
            mutated_payload: Mutated payload with injected faults
            target_name: Name of the target function/module
            
        Returns:
            Structured chaos report dictionary
        """
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "target": target_name,
            "crashed": crash_report.crashed,
            "exit_code": crash_report.exit_code,
            "error": {
                "type": crash_report.error_type,
                "message": crash_report.error_message,
                "traceback": crash_report.traceback
            } if crash_report.crashed else None,
            "payloads": {
                "original": original_payload,
                "mutated": mutated_payload
            },
            "output": {
                "stdout": crash_report.stdout,
                "stderr": crash_report.stderr
            }
        }
    
    def print_chaos_report(
        self,
        report: Dict[str, Any],
        use_rich: bool = True
    ) -> None:
        """
        Print a structured chaos report with rich formatting.
        
        Args:
            report: Chaos report dictionary
            use_rich: Whether to use rich formatting (default: True)
        """
        if use_rich:
            from rich.console import Console
            from rich.panel import Panel
            from rich.syntax import Syntax
            from rich.table import Table
            
            console = Console()
            console.print()
            
            # Header
            if report["crashed"]:
                console.print(
                    Panel(
                        f"[bold red]🔥 CRASH DETECTED[/bold red]\n"
                        f"Target: [cyan]{report['target']}[/cyan]\n"
                        f"Exit Code: [yellow]{report['exit_code']}[/yellow]",
                        border_style="red",
                        title="ChaosMonkey Chaos Report",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"[bold green]✓ NO CRASH[/bold green]\n"
                        f"Target: [cyan]{report['target']}[/cyan]\n"
                        f"Exit Code: [green]{report['exit_code']}[/green]",
                        border_style="green",
                        title="ChaosMonkey Chaos Report",
                    )
                )
            
            # Error details
            if report["crashed"] and report["error"]:
                console.print(f"\n[bold red]Error Type:[/bold red] {report['error']['type']}")
                console.print(f"[bold red]Error Message:[/bold red] {report['error']['message']}")
                
                if report["error"]["traceback"]:
                    console.print("\n[bold]Traceback:[/bold]")
                    syntax = Syntax(
                        report["error"]["traceback"],
                        "python",
                        theme="monokai",
                        line_numbers=False,
                        word_wrap=True
                    )
                    console.print(syntax)
            
            # Payload comparison
            console.print("\n[bold]Payload Comparison:[/bold]")
            
            table = Table(show_header=True, header_style="bold")
            table.add_column("Original", style="green")
            table.add_column("Mutated", style="red")
            
            original_json = json.dumps(report["payloads"]["original"], indent=2)
            mutated_json = json.dumps(report["payloads"]["mutated"], indent=2)
            
            table.add_row(original_json, mutated_json)
            console.print(table)
            
            # Timestamp
            console.print(f"\n[dim]Timestamp: {report['timestamp']}[/dim]\n")
            
        else:
            # Plain text output
            print("\n" + "="*60)
            print("CHAOSMONKEY CHAOS REPORT")
            print("="*60)
            print(f"Target: {report['target']}")
            print(f"Crashed: {report['crashed']}")
            print(f"Exit Code: {report['exit_code']}")
            
            if report["crashed"] and report["error"]:
                print(f"\nError Type: {report['error']['type']}")
                print(f"Error Message: {report['error']['message']}")
                if report["error"]["traceback"]:
                    print("\nTraceback:")
                    print(report["error"]["traceback"])
            
            print("\nOriginal Payload:")
            print(json.dumps(report["payloads"]["original"], indent=2))
            
            print("\nMutated Payload:")
            print(json.dumps(report["payloads"]["mutated"], indent=2))
            
            print(f"\nTimestamp: {report['timestamp']}")
            print("="*60 + "\n")

# Made with Bob
