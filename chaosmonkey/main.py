"""
ChaosMonkey AI - Main Entry Point

MCP-first autonomous chaos engineering platform.

Usage:
    chaosmonkey run <target>     # Run target and analyze crashes (legacy mode)
    chaosmonkey serve            # Start MCP server for AI agents (future)
    chaosmonkey demo             # Demo inject_null_fault tool
    chaosmonkey test             # Test that ChaosMonkey is working
"""

import json
import sys
import typer
from pathlib import Path
from typing import Any

from chaosmonkey.core import FaultExecutor, SystemObserver
from chaosmonkey.core.models import CrashReport
from chaosmonkey.core.remediation import generate_chaos_report
from chaosmonkey.tools import inject_null_fault

app = typer.Typer(
    help="ChaosMonkey AI - Fault injection and reliability testing tool",
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """ChaosMonkey AI - AI-powered fault injection for reliability testing."""
    if ctx.invoked_subcommand is None:
        from rich.console import Console
        console = Console()
        console.print("\n[bold cyan]🔧 ChaosMonkey AI[/bold cyan]")
        console.print("AI-powered fault injection and reliability testing\n")
        console.print("[bold]Available commands:[/bold]")
        console.print("  [cyan]chaos[/cyan]   - Execute chaos engineering flow")
        console.print("  [cyan]demo[/cyan]    - Demo inject_null_fault tool")
        console.print("  [cyan]run[/cyan]     - Run target and analyze crashes")
        console.print("  [cyan]serve[/cyan]   - Start MCP server (future)")
        console.print("  [cyan]test[/cyan]    - Test that ChaosMonkey is working")
        console.print("\n[dim]Run 'chaosmonkey COMMAND --help' for more info[/dim]\n")


@app.command()
def run(
    target: str = typer.Argument(
        ...,
        help="Path to the target Python script to test"
    )
):
    """
    Run a target application and detect crashes (legacy mode).
    
    This command runs the target script and provides crash analysis.
    In the future, this will be replaced by MCP-driven workflows where
    AI agents use tools like inject_fault, read_logs, and analyze_failure.
    """
    target_path = Path(target)
    
    if not target_path.exists():
        typer.echo(f"Error: Target file '{target}' not found", err=True)
        raise typer.Exit(1)
    
    if not target_path.suffix == ".py":
        typer.echo(f"Error: Target must be a Python file (.py)", err=True)
        raise typer.Exit(1)
    
    # Run target and capture crash
    executor = FaultExecutor()
    report = executor.run_target(str(target_path))
    
    # Print crash report
    _print_crash_report(report, str(target_path))
    
    if report.crashed:
        raise typer.Exit(1)


@app.command()
def serve(
    host: str = typer.Option("localhost", help="Server host"),
    port: int = typer.Option(8080, help="Server port")
):
    """
    Start MCP server for AI agents.
    
    This starts the ChaosMonkey MCP server, exposing chaos engineering tools
    to AI agents (Bob, Claude, Codex, etc.) through the Model Context Protocol.
    
    TODO: Implement MCP server
    """
    typer.echo("🚀 Starting ChaosMonkey MCP Server...")
    typer.echo(f"   Host: {host}")
    typer.echo(f"   Port: {port}")
    typer.echo()
    typer.echo("❌ MCP server not yet implemented")
    typer.echo()
    typer.echo("The MCP server will expose these tools:")
    typer.echo("  • inject_fault - Inject faults into applications")
    typer.echo("  • add_latency - Add artificial latency")
    typer.echo("  • corrupt_payload - Corrupt data payloads")
    typer.echo("  • read_logs - Read application logs")
    typer.echo("  • inspect_traceback - Inspect stack traces")
    typer.echo("  • get_metrics - Gather system metrics")
    typer.echo("  • run_tests - Execute test suites")
    typer.echo("  • verify_fix - Verify proposed fixes")

@app.command()
def demo(
    input_json: str = typer.Option(
        None,
        "--input",
        "-i",
        help="JSON input data (or use stdin)"
    ),
    probability: float = typer.Option(
        0.3,
        "--probability",
        "-p",
        help="Probability of injecting null (0.0-1.0)"
    ),
    seed: int = typer.Option(
        None,
        "--seed",
        "-s",
        help="Random seed for deterministic results"
    )
):
    """
    Demo the inject_null_fault tool with before/after visualization.
    
    Examples:
        chaosmonkey demo --input '{"user": {"name": "John", "age": 30}}'
        echo '{"items": [1, 2, 3]}' | chaosmonkey demo
        chaosmonkey demo -i '{"profile": {"name": "Alice"}}' --seed 42
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    
    console = Console()
    
    # Get input data
    if input_json:
        try:
            data = json.loads(input_json)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON input:[/red] {e}")
            raise typer.Exit(1)
    elif not sys.stdin.isatty():
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            console.print(f"[red]Invalid JSON from stdin:[/red] {e}")
            raise typer.Exit(1)
    else:
        # Default example data
        data = {
            "profile": {
                "name": "John Doe",
                "email": "john@example.com",
                "settings": {
                    "theme": "dark",
                    "notifications": True,
                }
            },
            "items": [
                {"id": 1, "title": "First"},
                {"id": 2, "title": "Second"},
                {"id": 3, "title": "Third"},
            ]
        }
        console.print("[yellow]No input provided, using example data[/yellow]\n")
    
    # Inject faults
    mutated = inject_null_fault(data, probability=probability, seed=seed)
    
    # Format JSON with syntax highlighting
    original_json = json.dumps(data, indent=2)
    mutated_json = json.dumps(mutated, indent=2)
    
    original_syntax = Syntax(original_json, "json", theme="monokai", line_numbers=False)
    mutated_syntax = Syntax(mutated_json, "json", theme="monokai", line_numbers=False)
    
    # Display side-by-side
    console.print("\n[bold cyan]🔧 ChaosMonkey Fault Injection Demo[/bold cyan]\n")
    
    console.print(Panel(
        original_syntax,
        title="[green]Original Payload[/green]",
        border_style="green",
    ))
    
    console.print()
    
    console.print(Panel(
        mutated_syntax,
        title="[red]Mutated Payload (with null faults)[/red]",
        border_style="red",
    ))
    
    # Show parameters
    console.print(f"\n[dim]Parameters: probability={probability}, seed={seed}[/dim]")
    
    # Count nulls injected
    def count_nulls(obj: Any) -> int:
        if obj is None:
            return 1
        elif isinstance(obj, dict):
            return sum(count_nulls(v) for v in obj.values())
        elif isinstance(obj, list):
            return sum(count_nulls(item) for item in obj)
        return 0
    
    null_count = count_nulls(mutated)
    console.print(f"[dim]Nulls injected: {null_count}[/dim]\n")

    typer.echo("  • analyze_failure - Analyze failures")
    typer.echo("  • suggest_fix - Suggest fixes")
    typer.echo()
    typer.echo("See ARCHITECTURE.md for details")
    raise typer.Exit(1)


@app.command()
def chaos(
    seed: int = typer.Option(
        None,
        "--seed",
        "-s",
        help="Random seed for deterministic results"
    ),
    probability: float = typer.Option(
        0.3,
        "--probability",
        "-p",
        help="Probability of injecting null (0.0-1.0)"
    ),
    iterations: int = typer.Option(
        20,
        "--iterations",
        "-i",
        help="Number of chaos iterations to run (default: 20)"
    )
):
    """
    Execute chaos engineering flow on target_app.py.
    
    This command demonstrates the complete chaos execution flow:
    1. Generate mutated payload using inject_null_fault
    2. Execute target function with mutated payload
    3. Capture exceptions, traceback, and crash type
    4. Repeat until crash found or iterations exhausted
    5. Print structured chaos report with crashing payload
    
    Examples:
        chaosmonkey chaos
        chaosmonkey chaos --iterations 50
        chaosmonkey chaos --seed 42 --iterations 10
        chaosmonkey chaos --probability 0.5 --seed 123
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    import json
    
    console = Console()
    console.print("\n[bold cyan]🔧 ChaosMonkey Chaos Execution[/bold cyan]\n")
    
    # Import target function
    try:
        from target_app import process_user
    except ImportError:
        console.print("[red]Error: Could not import target_app.process_user[/red]")
        console.print("[yellow]Make sure target_app.py exists in the current directory[/yellow]")
        raise typer.Exit(1)
    
    # Define test payload
    original_payload = {
        "profile": {
            "name": "John Doe",
            "email": "john@example.com",
            "age": 30
        }
    }
    
    # Execute with fault injection
    executor = FaultExecutor()
    observer = SystemObserver()
    
    console.print(f"[dim]Running {iterations} chaos iterations...[/dim]\n")
    
    # Execute and capture crash with iterations
    crash_report, crashing_payload, crash_iteration = executor.execute_with_fault(
        target_function=process_user,
        payload=original_payload,
        fault_probability=probability,
        seed=seed,
        iterations=iterations
    )
    
    # Generate and print chaos report
    if crash_report.crashed and crashing_payload is not None:
        console.print()
        console.print(
            Panel(
                f"[bold red]🔥 CRASH DISCOVERED![/bold red]\n"
                f"Target: [cyan]target_app.process_user[/cyan]\n"
                f"Iteration: [yellow]{crash_iteration}/{iterations}[/yellow]",
                border_style="red",
                title="ChaosMonkey Chaos Report",
            )
        )
        
        # Display error details
        console.print(f"\n[bold red]Error Type:[/bold red] {crash_report.error_type}")
        console.print(f"[bold red]Error Message:[/bold red] {crash_report.error_message}")
        
        # Display crashing payload
        console.print("\n[bold]Crashing Payload:[/bold]")
        crashing_json = json.dumps(crashing_payload, indent=2)
        syntax = Syntax(crashing_json, "json", theme="monokai", line_numbers=False)
        console.print(Panel(syntax, border_style="red", title="[red]Payload that caused crash[/red]"))
        
        # Display traceback
        if crash_report.traceback:
            console.print("\n[bold]Traceback:[/bold]")
            tb_syntax = Syntax(
                crash_report.traceback,
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            )
            console.print(tb_syntax)
        
        # Generate CHAOS_REPORT.md and automatically invoke Bob
        console.print()
        console.print("[bold cyan]📝 Generating crash report...[/bold cyan]")
        
        report_path, remediation_path = generate_chaos_report(
            target_function="target_app.process_user",
            crashing_payload=crashing_payload,
            crash_report=crash_report,
            target_file="target_app.py",
            output_path="CHAOS_REPORT.md",
            auto_invoke_bob=True,
            bob_timeout=120
        )
        
        console.print(f"[green]✓ Crash report: {report_path}[/green]")
        
        if remediation_path:
            console.print(f"[green]✓ Remediation report: {remediation_path}[/green]")
        
        console.print()
        console.print("[yellow]💡 ChaosMonkey successfully discovered a crash![/yellow]")
        console.print("[dim]This demonstrates how repeated fault injection can reveal hidden bugs.[/dim]")
        console.print()
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Review CHAOS_REPORT.md for crash details")
        
        if remediation_path:
            console.print("  2. Review CHAOS_REMEDIATION.md for AI-powered analysis")
            console.print("  3. Implement the suggested fixes")
        else:
            console.print("  2. Use the 'Prompt for IBM Bob' section to get AI-powered analysis")
            console.print("  3. IBM Bob will inspect the code, explain root cause, and propose fixes")
        
        console.print()
        raise typer.Exit(1)
    else:
        console.print()
        console.print(
            Panel(
                f"[bold green]✓ NO CRASHES FOUND[/bold green]\n"
                f"Target: [cyan]target_app.process_user[/cyan]\n"
                f"Iterations: [green]{iterations}[/green]",
                border_style="green",
                title="ChaosMonkey Chaos Report",
            )
        )
        console.print(f"\n[green]✓ No crashes detected after {iterations} iterations[/green]")
        console.print("[dim]Try more iterations, different seeds, or higher probability to find crashes.[/dim]\n")


@app.command()
def test():
    """Test that ChaosMonkey AI is working."""
    typer.echo("✅ ChaosMonkey AI is alive!")
    typer.echo()
    typer.echo("Architecture:")
    typer.echo("  • chaosmonkey/core/     - Core chaos engineering logic")
    typer.echo("  • chaosmonkey/tools/    - MCP tool implementations")
    typer.echo("  • chaosmonkey/mcp/      - MCP server (not yet implemented)")
    typer.echo()
    typer.echo("Run 'chaosmonkey serve' to start the MCP server (future)")
    typer.echo("Run 'chaosmonkey run <target>' to test a Python file (legacy)")
    typer.echo("Run 'chaosmonkey chaos' to execute chaos engineering flow")


def _print_crash_report(report: CrashReport, target_path: str) -> None:
    """Print a simple crash report."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    
    console = Console()
    console.print()
    
    if report.crashed:
        console.print(
            Panel(
                f"[bold red]🔥 CRASH DETECTED[/bold red]\n"
                f"Target: [cyan]{target_path}[/cyan]\n"
                f"Exit Code: [yellow]{report.exit_code}[/yellow]",
                border_style="red",
                title="ChaosMonkey AI",
            )
        )
        
        if report.error_type:
            console.print(f"\n[bold red]Error:[/bold red] {report.error_type}")
            if report.error_message:
                console.print(f"[yellow]{report.error_message}[/yellow]")
        
        if report.traceback:
            console.print("\n[bold]Traceback:[/bold]")
            syntax = Syntax(
                report.traceback,
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            )
            console.print(syntax)
        
        console.print()
        console.print("[dim]💡 In the future, AI agents will use MCP tools to:[/dim]")
        console.print("[dim]   1. inject_fault() - Inject controlled failures[/dim]")
        console.print("[dim]   2. read_logs() - Inspect application logs[/dim]")
        console.print("[dim]   3. analyze_failure() - Identify root causes[/dim]")
        console.print("[dim]   4. suggest_fix() - Propose safe fixes[/dim]")
        console.print("[dim]   5. verify_fix() - Validate fixes work[/dim]")
        console.print()
    else:
        console.print(
            Panel(
                f"[bold green]✓ SUCCESS[/bold green]\n"
                f"Target: [cyan]{target_path}[/cyan]\n"
                f"Exit Code: [green]{report.exit_code}[/green]",
                border_style="green",
                title="ChaosMonkey AI",
            )
        )


if __name__ == "__main__":
    app()

# Made with Bob
