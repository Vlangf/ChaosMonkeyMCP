"""
ChaosMonkey AI - MCP Server Implementation

Production-ready MCP server for autonomous fault injection and crash discovery.

Scope: ChaosMonkey performs fault injection and crash discovery ONLY.
It does NOT fix code, write files, create branches, or open PRs.

Exposes 4 core tools:
- inject_null_fault: Mutate data structures with null values
- run_chaos_test: Execute chaos tests and capture crashes
- run_command: Execute shell commands for testing
- read_file: Safely read reports and logs

Designed for integration with Claude, Bob, Cursor, and Codex.
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from fastmcp import FastMCP

from chaosmonkey.tools.fault_injection import inject_null_fault
from chaosmonkey.core.executor import FaultExecutor
from chaosmonkey.mcp.schemas import (
    INJECT_NULL_FAULT_METADATA,
    RUN_CHAOS_TEST_METADATA,
    RUN_COMMAND_METADATA,
    READ_FILE_METADATA,
    InjectNullFaultInput,
    InjectNullFaultOutput,
    RunChaosTestInput,
    RunChaosTestOutput,
    RunCommandInput,
    RunCommandOutput,
    ReadFileInput,
    ReadFileOutput,
)


# Initialize FastMCP server
mcp = FastMCP("chaosmonkey-ai")


@mcp.tool()
def inject_null_fault_tool(
    data: str,
    probability: float = 0.3,
    seed: Optional[int] = None,
) -> str:
    """
    Inject null faults into nested data structures for crash discovery.
    
    Mutates Python payloads by randomly replacing nested values with None
    to simulate missing data, null pointer scenarios, and incomplete API responses.
    
    Use this tool to discover bugs through fault injection:
    - Test null pointer handling
    - Simulate incomplete API responses
    - Find missing data validation bugs
    - Discover resilience issues in data pipelines
    
    Args:
        data: JSON string of input dictionary to mutate
        probability: Chance (0.0-1.0) of replacing any given value with None (default: 0.3)
        seed: Optional random seed for deterministic behavior
        
    Returns:
        JSON string with structured output:
        {
            "success": bool,
            "mutated_data": dict,  # The mutated payload
            "mutations": int,      # Count of None values
            "probability": float,
            "seed": int | None
        }
        
    Examples:
        Input: '{"user": {"name": "John", "age": 30}}'
        Output: {
            "success": true,
            "mutated_data": {"user": {"name": null, "age": 30}},
            "mutations": 1,
            "probability": 0.3,
            "seed": null
        }
        
        Input: '{"items": [1, 2, 3], "total": 6}'
        Output: {
            "success": true,
            "mutated_data": {"items": [1, null, 3], "total": null},
            "mutations": 2,
            "probability": 0.3,
            "seed": null
        }
    
    Error Handling:
        Returns {"success": false, "error": "...", "message": "..."} on failure
    """
    try:
        # Parse input JSON
        input_data = json.loads(data)
        
        # Apply null fault injection
        mutated_data = inject_null_fault(
            input_data,
            probability=probability,
            seed=seed
        )
        
        # Count mutations (simple heuristic)
        def count_nones(obj):
            if obj is None:
                return 1
            elif isinstance(obj, dict):
                return sum(count_nones(v) for v in obj.values())
            elif isinstance(obj, list):
                return sum(count_nones(item) for item in obj)
            return 0
        
        mutations = count_nones(mutated_data)
        
        result: InjectNullFaultOutput = {
            "success": True,
            "mutated_data": mutated_data,
            "mutations": mutations,
            "probability": probability,
            "seed": seed,
            "error": None,
            "message": None
        }
        
        return json.dumps(result, indent=2)
        
    except json.JSONDecodeError as e:
        json_error_result: InjectNullFaultOutput = {
            "success": False,
            "mutated_data": None,
            "mutations": None,
            "probability": None,
            "seed": None,
            "error": "JSONDecodeError",
            "message": f"Invalid JSON input: {str(e)}"
        }
        return json.dumps(json_error_result, indent=2)
    except Exception as e:
        exception_error_result: InjectNullFaultOutput = {
            "success": False,
            "mutated_data": None,
            "mutations": None,
            "probability": None,
            "seed": None,
            "error": type(e).__name__,
            "message": str(e)
        }
        return json.dumps(exception_error_result, indent=2)


@mcp.tool()
def run_chaos_test(
    target_path: str,
    payload: str,
    probability: float = 0.3,
    seed: Optional[int] = None,
    iterations: int = 1
) -> str:
    """
    Run chaos test by injecting faults and executing target application.
    
    This tool orchestrates autonomous fault injection and crash discovery:
    1. Injects null faults into the provided payload
    2. Executes the target Python application with mutated data
    3. Captures crashes, errors, and tracebacks
    4. Returns structured crash report for AI analysis
    
    Use this tool to discover bugs:
    - Find null pointer bugs in production code
    - Test error handling and resilience
    - Identify missing data validation
    - Generate structured crash reports
    - Enable root cause analysis
    
    Note: This tool discovers bugs, it does NOT fix them.
    
    Args:
        target_path: Path to target Python file (relative to workspace)
        payload: JSON string of input data to mutate
        probability: Chance (0.0-1.0) of replacing values with None (default: 0.3)
        seed: Optional random seed for deterministic behavior
        iterations: Number of chaos iterations to run (default: 1)
        
    Returns:
        JSON string with structured output:
        {
            "success": bool,
            "crash_detected": bool,
            "error_type": str,           # e.g., "AttributeError", "KeyError"
            "error_message": str,
            "crashing_payload": dict,    # The mutated payload that caused crash
            "traceback": str,            # Full Python traceback
            "iteration": int,            # Which iteration crashed (1-based)
            "exit_code": int,
            "stdout": str,
            "stderr": str
        }
        
    Examples:
        Input:
            target_path: "target_app.py"
            payload: '{"user": {"profile": {"name": "John"}}}'
            probability: 0.5
            seed: 42
            
        Output (crash detected):
            {
                "success": true,
                "crash_detected": true,
                "error_type": "AttributeError",
                "error_message": "'NoneType' object has no attribute 'lower'",
                "crashing_payload": {"user": {"profile": null}},
                "traceback": "Traceback (most recent call last):\\n  File ...",
                "iteration": 1,
                "exit_code": 1,
                "stdout": "",
                "stderr": "Traceback..."
            }
            
        Output (no crash):
            {
                "success": true,
                "crash_detected": false,
                "error_type": null,
                "error_message": null,
                "crashing_payload": null,
                "traceback": null,
                "iteration": null,
                "exit_code": 0,
                "stdout": "Success",
                "stderr": ""
            }
    
    Error Handling:
        Returns {"success": false, "error": "...", "message": "..."} on:
        - FileNotFoundError: Target file doesn't exist
        - InvalidTarget: Target is not a .py file
        - InvalidPayload: Payload is not valid JSON
        - ImportError: Cannot load target module
        - NoFunctionFound: No testable function in target
    """
    try:
        # Validate target path
        target = Path(target_path)
        if not target.exists():
            file_error_result: RunChaosTestOutput = {
                "success": False,
                "crash_detected": None,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "error": "FileNotFoundError",
                "message": f"Target file not found: {target_path}"
            }
            return json.dumps(file_error_result, indent=2)
        
        if target.suffix != ".py":
            target_error_result: RunChaosTestOutput = {
                "success": False,
                "crash_detected": None,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "error": "InvalidTarget",
                "message": f"Target must be a Python file (.py): {target_path}"
            }
            return json.dumps(target_error_result, indent=2)
        
        # Parse payload
        try:
            input_data = json.loads(payload)
        except json.JSONDecodeError as e:
            payload_error_result: RunChaosTestOutput = {
                "success": False,
                "crash_detected": None,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "error": "InvalidPayload",
                "message": f"Invalid JSON payload: {str(e)}"
            }
            return json.dumps(payload_error_result, indent=2)
        
        # Import target module dynamically
        import importlib.util
        spec = importlib.util.spec_from_file_location("target_module", target)
        if spec is None or spec.loader is None:
            import_error_result: RunChaosTestOutput = {
                "success": False,
                "crash_detected": None,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "error": "ImportError",
                "message": f"Could not load target module: {target_path}"
            }
            return json.dumps(import_error_result, indent=2)
        
        target_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(target_module)
        
        # Find the main function to test (assume first function or 'process_user')
        target_function = None
        for name in dir(target_module):
            obj = getattr(target_module, name)
            if callable(obj) and not name.startswith('_'):
                target_function = obj
                break
        
        if target_function is None:
            function_error_result: RunChaosTestOutput = {
                "success": False,
                "crash_detected": None,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "error": "NoFunctionFound",
                "message": f"No testable function found in {target_path}"
            }
            return json.dumps(function_error_result, indent=2)
        
        # Execute chaos test
        executor = FaultExecutor()
        crash_report, crashing_payload, iteration = executor.execute_with_fault(
            target_function=target_function,
            payload=input_data,
            fault_probability=probability,
            seed=seed,
            iterations=iterations
        )
        
        # Build result
        result: RunChaosTestOutput = {
            "success": True,
            "crash_detected": crash_report.crashed,
            "error_type": crash_report.error_type,
            "error_message": crash_report.error_message,
            "crashing_payload": crashing_payload,
            "traceback": crash_report.traceback,
            "iteration": iteration,
            "exit_code": crash_report.exit_code,
            "stdout": crash_report.stdout,
            "stderr": crash_report.stderr,
            "error": None,
            "message": None
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        import traceback as tb
        final_error_result: RunChaosTestOutput = {
            "success": False,
            "crash_detected": None,
            "error_type": None,
            "error_message": None,
            "crashing_payload": None,
            "traceback": None,
            "iteration": None,
            "exit_code": None,
            "stdout": None,
            "stderr": None,
            "error": type(e).__name__,
            "message": str(e)
        }
        return json.dumps(final_error_result, indent=2)


# Dangerous command patterns to block
DANGEROUS_PATTERNS = [
    "rm -rf",
    "rm -fr",
    "rm -r",
    "rm -f",
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "init 0",
    "init 6",
    "mkfs",
    "dd if=",
    ":(){ :|:& };:",  # Fork bomb
    "> /dev/sda",
    "mv /* ",
    "chmod -R 777 /",
    "chown -R",
    "sudo rm",
    "sudo shutdown",
    "sudo reboot",
    "sudo halt",
    "sudo poweroff",
    "sudo mkfs",
    "sudo dd",
]

# Security: Blocked file patterns for read_file
BLOCKED_FILE_PATTERNS = [
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "credentials",
    "credential",
    "token",
    "tokens",
    "secret",
    "secrets",
    ".pem",
    ".key",
    "password",
    "passwords",
    "passwd",
    ".aws/credentials",
    ".ssh/",
    "private_key",
    "api_key",
    "apikey",
]


def is_command_safe(command: str) -> tuple[bool, Optional[str]]:
    """
    Check if a command is safe to execute.
    
    Returns:
        (is_safe, reason) - True if safe, False with reason if dangerous
    """
    command_lower = command.lower().strip()
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if pattern.lower() in command_lower:
            return False, f"Blocked dangerous pattern: {pattern}"
    
    # Block commands that start with sudo (unless it's safe commands like sudo -v)
    if command_lower.startswith("sudo ") and not command_lower.startswith("sudo -v"):
        # Allow some safe sudo commands
        safe_sudo_commands = ["sudo -v", "sudo -l", "sudo whoami"]
        if not any(command_lower.startswith(safe) for safe in safe_sudo_commands):
            return False, "Blocked sudo command for safety"
    
    return True, None


@mcp.tool()
def run_command(
    command: str,
    cwd: Optional[str] = None,
    timeout_seconds: int = 30
) -> str:
    """
    Execute shell commands for running tests and verifying resilience.
    
    This tool enables cross-stack testing for chaos engineering:
    - Python: pytest, unittest, tox
    - JavaScript/TypeScript: npm test, jest, vitest
    - Rust: cargo test
    - Go: go test
    - Java: mvn test, gradle test
    
    Use this tool to verify application resilience after discovering crashes.
    
    SAFETY: Designed for LOCAL TRUSTED DEVELOPMENT ENVIRONMENTS ONLY.
    Dangerous commands (rm -rf, shutdown, sudo, etc.) are blocked.
    
    Args:
        command: Shell command to execute (e.g., "pytest tests/", "npm test")
        cwd: Optional working directory relative to workspace (default: workspace root)
        timeout_seconds: Optional timeout in seconds (default: 30, max: 300)
        
    Returns:
        JSON string with structured output:
        {
            "success": bool,
            "exit_code": int,           # 0 = success, non-zero = failure
            "stdout": str,              # Standard output
            "stderr": str,              # Standard error
            "duration_ms": int,         # Execution time in milliseconds
            "command": str,             # Echo of executed command
            "cwd": str | None           # Echo of working directory
        }
        
    Examples:
        Input: command="pytest tests/test_app.py -v"
        Output: {
            "success": true,
            "exit_code": 0,
            "stdout": "===== 1 passed in 0.05s =====",
            "stderr": "",
            "duration_ms": 1250,
            "command": "pytest tests/test_app.py -v",
            "cwd": null
        }
        
        Input: command="npm test", cwd="frontend"
        Output: {
            "success": true,
            "exit_code": 0,
            "stdout": "PASS  src/App.test.js",
            "stderr": "",
            "duration_ms": 3420,
            "command": "npm test",
            "cwd": "frontend"
        }
    
    Error Handling:
        Returns {"success": false, "error": "...", "message": "..."} on:
        - DangerousCommand: Command contains blocked patterns
        - InvalidDirectory: Working directory doesn't exist
        - TimeoutExpired: Command exceeded timeout
        - CommandFailed: Command execution failed
    """
    try:
        # Validate timeout
        if timeout_seconds < 1 or timeout_seconds > 300:
            timeout_error: RunCommandOutput = {
                "success": False,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "duration_ms": None,
                "command": command,
                "cwd": cwd,
                "error": "InvalidTimeout",
                "message": f"Timeout must be between 1 and 300 seconds, got {timeout_seconds}"
            }
            return json.dumps(timeout_error, indent=2)
        
        # Safety check
        is_safe, reason = is_command_safe(command)
        if not is_safe:
            safety_error: RunCommandOutput = {
                "success": False,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "duration_ms": None,
                "command": command,
                "cwd": cwd,
                "error": "DangerousCommand",
                "message": f"Command blocked for safety: {reason}"
            }
            return json.dumps(safety_error, indent=2)
        
        # Validate working directory if provided
        if cwd:
            cwd_path = Path(cwd)
            if not cwd_path.exists():
                dir_error: RunCommandOutput = {
                    "success": False,
                    "exit_code": None,
                    "stdout": None,
                    "stderr": None,
                    "duration_ms": None,
                    "command": command,
                    "cwd": cwd,
                    "error": "InvalidDirectory",
                    "message": f"Working directory does not exist: {cwd}"
                }
                return json.dumps(dir_error, indent=2)
        
        # Execute command
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Build success result
            success_result: RunCommandOutput = {
                "success": True,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": duration_ms,
                "command": command,
                "cwd": cwd,
                "error": None,
                "message": None
            }
            
            return json.dumps(success_result, indent=2)
            
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            timeout_expired_error: RunCommandOutput = {
                "success": False,
                "exit_code": None,
                "stdout": None,
                "stderr": None,
                "duration_ms": duration_ms,
                "command": command,
                "cwd": cwd,
                "error": "TimeoutExpired",
                "message": f"Command exceeded timeout of {timeout_seconds} seconds"
            }
            return json.dumps(timeout_expired_error, indent=2)
            
    except Exception as e:
        exception_error: RunCommandOutput = {
            "success": False,
            "exit_code": None,
            "stdout": None,
            "stderr": None,
            "duration_ms": None,
            "command": command,
            "cwd": cwd,
            "error": type(e).__name__,
            "message": str(e)
        }
        return json.dumps(exception_error, indent=2)


def is_path_safe(file_path: Path, project_root: Path) -> tuple[bool, Optional[str]]:
    """
    Check if a file path is safe to read.
    
    Security checks:
    - Path must be within project root (no directory traversal)
    - Path must not match blocked file patterns (secrets, credentials, etc.)
    
    Args:
        file_path: Path to check
        project_root: Project root directory
        
    Returns:
        (is_safe, error_message) - True if safe, False with reason if blocked
    """
    try:
        # Resolve to absolute path
        abs_path = file_path.resolve()
        abs_root = project_root.resolve()
        
        # Check if path is within project root (prevent directory traversal)
        try:
            abs_path.relative_to(abs_root)
        except ValueError:
            return False, f"Access denied: path outside project root ({abs_root})"
        
        # Check for blocked file patterns
        path_str = str(abs_path).lower()
        path_name = abs_path.name.lower()
        
        for pattern in BLOCKED_FILE_PATTERNS:
            # Check both full path and filename
            if pattern in path_str or pattern in path_name:
                return False, f"Access denied: blocked file pattern '{pattern}'"
        
        return True, None
        
    except Exception as e:
        return False, f"Path validation error: {str(e)}"


@mcp.tool()
def read_file(
    path: str,
    max_bytes: int = 20000
) -> str:
    """
    Safely read local files (reports, logs, chaos results) after chaos runs.
    
    This tool enables AI agents to read structured crash reports and logs
    generated during fault injection and crash discovery. Includes comprehensive
    security checks to prevent reading sensitive files or paths outside project root.
    
    Use this tool for:
    - Reading chaos test reports and crash details
    - Analyzing application logs after chaos runs
    - Inspecting crash dumps and error logs
    - Post-chaos analysis and insights generation
    
    Note: This tool reads crash reports, it does NOT generate fixes.
    
    Security Features:
    - Blocks reading outside project root (prevents directory traversal)
    - Blocks sensitive files (.env, credentials, private keys, tokens, etc.)
    - Returns structured errors for security violations
    - Limits file size to prevent memory issues
    
    Args:
        path: Path to file (relative to project root)
        max_bytes: Maximum bytes to read (default: 20000, max: 1000000)
        
    Returns:
        JSON string with structured output:
        {
            "success": bool,
            "path": str,              # Echo of requested path
            "content": str,           # File content (None if error)
            "truncated": bool,        # True if content was truncated
            "size_bytes": int,        # Total file size in bytes
            "error": str | None,      # Error type if success=False
            "message": str | None     # Error message if success=False
        }
        
    Examples:
        Input: path="chaos_report.json", max_bytes=10000
        Output: {
            "success": true,
            "path": "chaos_report.json",
            "content": '{"crash_detected": true, "error_type": "AttributeError", ...}',
            "truncated": false,
            "size_bytes": 1234
        }
        
        Input: path="logs/chaos_run.log", max_bytes=5000
        Output: {
            "success": true,
            "path": "logs/chaos_run.log",
            "content": "[2024-01-15 10:30:00] Starting chaos test...",
            "truncated": true,
            "size_bytes": 15000
        }
        
        Input: path="../../../etc/passwd"
        Output: {
            "success": false,
            "path": "../../../etc/passwd",
            "content": null,
            "truncated": false,
            "size_bytes": 0,
            "error": "SecurityError",
            "message": "Access denied: path outside project root"
        }
        
        Input: path=".env"
        Output: {
            "success": false,
            "path": ".env",
            "content": null,
            "truncated": false,
            "size_bytes": 0,
            "error": "SecurityError",
            "message": "Access denied: blocked file pattern '.env'"
        }
    
    Error Handling:
        Returns {"success": false, "error": "...", "message": "..."} on:
        - SecurityError: Path outside project root or blocked file pattern
        - FileNotFoundError: File doesn't exist
        - NotAFileError: Path is a directory, not a file
        - PermissionError: No permission to read file
        - BinaryFileError: File is binary, not text
        - InvalidMaxBytes: max_bytes out of valid range
    """
    try:
        # Validate max_bytes
        if max_bytes < 1 or max_bytes > 1000000:
            max_bytes_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "InvalidMaxBytes",
                "message": f"max_bytes must be between 1 and 1000000, got {max_bytes}"
            }
            return json.dumps(max_bytes_error, indent=2)
        
        # Get project root (current working directory)
        project_root = Path.cwd()
        
        # Convert to Path and resolve
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = project_root / file_path
        
        # Security check
        is_safe, error_msg = is_path_safe(file_path, project_root)
        if not is_safe:
            security_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "SecurityError",
                "message": error_msg
            }
            return json.dumps(security_error, indent=2)
        
        # Check if file exists
        if not file_path.exists():
            not_found_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "FileNotFoundError",
                "message": f"File not found: {path}"
            }
            return json.dumps(not_found_error, indent=2)
        
        # Check if it's a file (not a directory)
        if not file_path.is_file():
            not_file_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "NotAFileError",
                "message": f"Path is not a file: {path}"
            }
            return json.dumps(not_file_error, indent=2)
        
        # Get file size
        size_bytes = file_path.stat().st_size
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(max_bytes)
            
            # Check if truncated
            truncated = size_bytes > max_bytes
            
            # Build success result
            success_result: ReadFileOutput = {
                "success": True,
                "path": path,
                "content": content,
                "truncated": truncated,
                "size_bytes": size_bytes,
                "error": None,
                "message": None
            }
            
            return json.dumps(success_result, indent=2)
            
        except UnicodeDecodeError:
            binary_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": size_bytes,
                "error": "BinaryFileError",
                "message": "File is not a text file (binary content detected)"
            }
            return json.dumps(binary_error, indent=2)
            
        except PermissionError:
            permission_error: ReadFileOutput = {
                "success": False,
                "path": path,
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "PermissionError",
                "message": f"Permission denied: {path}"
            }
            return json.dumps(permission_error, indent=2)
            
    except Exception as e:
        exception_error: ReadFileOutput = {
            "success": False,
            "path": path,
            "content": None,
            "truncated": False,
            "size_bytes": 0,
            "error": type(e).__name__,
            "message": str(e)
        }
        return json.dumps(exception_error, indent=2)


# Tool metadata for MCP introspection
TOOL_METADATA = {
    "inject_null_fault": INJECT_NULL_FAULT_METADATA,
    "run_chaos_test": RUN_CHAOS_TEST_METADATA,
    "run_command": RUN_COMMAND_METADATA,
    "read_file": READ_FILE_METADATA,
}


if __name__ == "__main__":
    # Run the MCP server in stdio mode without the FastMCP ASCII banner.
    # Some MCP clients, including IBM Bob, treat any non-protocol stdout as an error.
    mcp.run(show_banner=False)

# Made with Bob
