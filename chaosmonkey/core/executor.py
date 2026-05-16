"""
ChaosMonkey AI - Fault Executor

Core fault injection engine for executing chaos experiments.
"""

import subprocess
import sys
import traceback
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from chaosmonkey.core.models import FaultConfig, CrashReport, FaultType


class FaultExecutor:
    """
    Executes fault injection and runs target applications.
    
    This class handles the core chaos engineering operations:
    - Running target applications
    - Injecting faults (future implementation)
    - Capturing crashes and errors
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize fault executor.
        
        Args:
            timeout: Maximum execution time in seconds
        """
        self.timeout = timeout
    
    def run_target(self, target_path: str) -> CrashReport:
        """
        Run target application and capture output.
        
        Args:
            target_path: Path to the target Python script
            
        Returns:
            CrashReport with execution details
        """
        try:
            result = subprocess.run(
                [sys.executable, target_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            crashed = result.returncode != 0
            error_type = None
            error_message = None
            traceback = None
            
            # Parse stderr for crash details
            if crashed and result.stderr:
                lines = result.stderr.strip().split('\n')
                # Look for exception type and message in last line
                if lines:
                    last_line = lines[-1]
                    if ':' in last_line:
                        parts = last_line.split(':', 1)
                        error_type = parts[0].strip()
                        error_message = parts[1].strip() if len(parts) > 1 else ""
                traceback = result.stderr
            
            return CrashReport(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                crashed=crashed,
                error_type=error_type,
                error_message=error_message,
                traceback=traceback
            )
            
        except subprocess.TimeoutExpired:
            return CrashReport(
                exit_code=-1,
                stdout="",
                stderr="Process timed out after 30 seconds",
                crashed=True,
                error_type="TimeoutError",
                error_message="Process timed out after 30 seconds",
                traceback=None
            )
        except Exception as e:
            return CrashReport(
                exit_code=-1,
                stdout="",
                stderr=str(e),
                crashed=True,
                error_type=type(e).__name__,
                error_message=str(e),
                traceback=None
            )
    
    def execute_with_fault(
        self,
        target_function: Callable,
        payload: Dict[str, Any],
        fault_probability: float = 0.3,
        seed: Optional[int] = None,
        iterations: int = 1
    ) -> tuple[CrashReport, Optional[Dict[str, Any]], Optional[int]]:
        """
        Execute a target function with fault-injected payload.
        
        This is the core chaos execution flow:
        1. Generate mutated payload using inject_null_fault
        2. Execute target function with mutated payload
        3. Capture exceptions, traceback, and crash type
        4. Repeat for specified iterations until crash found
        
        Args:
            target_function: Function to execute
            payload: Input data to mutate and pass to function
            fault_probability: Probability of injecting null (0.0-1.0)
            seed: Optional random seed for deterministic results
            iterations: Number of times to repeat chaos injection (default: 1)
            
        Returns:
            Tuple of (CrashReport, crashing_payload, iteration_number)
            - CrashReport: Details of the execution
            - crashing_payload: The mutated payload that caused crash (None if no crash)
            - iteration_number: Which iteration crashed (None if no crash)
        """
        from rich.console import Console
        from chaosmonkey.tools.fault_injection import inject_null_fault
        
        console = Console()
        
        last_result = None
        
        for iteration in range(1, iterations + 1):
            # Print progress for multiple iterations
            if iterations > 1:
                console.print(f"[dim]Iteration {iteration}/{iterations}...[/dim]", end=" ")
            
            # Step 1: Generate mutated payload with iteration-specific seed
            iteration_seed = None if seed is None else seed + iteration - 1
            mutated_payload = inject_null_fault(
                payload,
                probability=fault_probability,
                seed=iteration_seed
            )
            
            # Step 2: Execute target function with mutated payload
            try:
                last_result = target_function(mutated_payload)
                
                # Success - no crash
                if iterations > 1:
                    console.print("[green]✓[/green]")
                
            except Exception as e:
                # Step 3: Capture exception details
                tb = traceback.format_exc()
                
                if iterations > 1:
                    console.print("[red]✗ CRASH![/red]")
                
                crash_report = CrashReport(
                    exit_code=1,
                    stdout="",
                    stderr=tb,
                    crashed=True,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    traceback=tb
                )
                
                # Return crash with the payload that caused it
                return crash_report, mutated_payload, iteration
        
        # All iterations completed without crash
        return CrashReport(
            exit_code=0,
            stdout=str(last_result) if last_result is not None else "",
            stderr="",
            crashed=False,
            error_type=None,
            error_message=None,
            traceback=None
        ), None, None
    
    def inject_fault(self, config: FaultConfig) -> bool:
        """
        Inject a fault into the target application.
        
        TODO: Implement fault injection mechanisms:
        - Code instrumentation
        - Runtime manipulation
        - Environment variable injection
        - Network fault injection
        
        Args:
            config: Fault injection configuration
            
        Returns:
            True if fault was successfully injected
        """
        # TODO: Implement fault injection
        # This will be the core MCP tool implementation
        raise NotImplementedError("Fault injection not yet implemented")
    
    def validate_target(self, target_path: str) -> bool:
        """
        Validate that target file exists and is executable.
        
        Args:
            target_path: Path to target file
            
        Returns:
            True if target is valid
        """
        path = Path(target_path)
        return path.exists() and path.suffix == ".py"

# Made with Bob
