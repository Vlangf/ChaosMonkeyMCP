"""
ChaosMonkey AI - MCP Tool Schemas

Production-ready type definitions and schemas for autonomous fault injection
and crash discovery tools.

Scope: ChaosMonkey performs fault injection and crash discovery ONLY.
It does NOT fix code, write files, create branches, or open PRs.

Designed for Claude, Bob, Cursor, and Codex integration.
"""

from typing import TypedDict, Optional, List, Literal, Any


# ============================================================================
# INJECT_NULL_FAULT TOOL SCHEMAS
# ============================================================================

class InjectNullFaultInput(TypedDict):
    """
    Input schema for inject_null_fault tool.
    
    This tool mutates Python payloads for fault injection and crash discovery.
    Randomly replaces nested values with None to simulate missing data scenarios.
    
    Fields:
        data: JSON string of input dictionary to mutate
        probability: Chance (0.0-1.0) of replacing any given value with None (default: 0.3)
        seed: Optional random seed for deterministic behavior
    """
    data: str  # JSON string
    probability: Optional[float]  # 0.0 to 1.0, default 0.3
    seed: Optional[int]  # For deterministic results


class InjectNullFaultOutput(TypedDict):
    """
    Output schema for inject_null_fault tool.
    
    Returns structured results with mutated data and metadata about the mutations.
    """
    success: bool
    mutated_data: Optional[Any]  # The mutated payload (None if error)
    mutations: Optional[int]  # Count of values replaced with None
    probability: Optional[float]  # Echo of input probability
    seed: Optional[int]  # Echo of input seed
    error: Optional[str]  # Error type if success=False
    message: Optional[str]  # Error message if success=False


# ============================================================================
# RUN_CHAOS_TEST TOOL SCHEMAS
# ============================================================================

class RunChaosTestInput(TypedDict):
    """
    Input schema for run_chaos_test tool.
    
    This tool performs autonomous fault injection and crash discovery by injecting
    faults and executing target applications. Returns structured crash reports.
    
    Fields:
        target_path: Path to target Python file (relative to workspace)
        payload: JSON string of input data to mutate
        probability: Chance (0.0-1.0) of replacing values with None (default: 0.3)
        seed: Optional random seed for deterministic behavior
        iterations: Number of chaos iterations to run (default: 1)
    """
    target_path: str  # Path to .py file
    payload: str  # JSON string
    probability: Optional[float]  # 0.0 to 1.0, default 0.3
    seed: Optional[int]  # For deterministic results
    iterations: Optional[int]  # Default 1


class RunChaosTestOutput(TypedDict):
    """
    Output schema for run_chaos_test tool.
    
    Returns structured crash report for AI analysis. Does NOT include fixes or remediation.
    """
    success: bool
    crash_detected: Optional[bool]  # True if application crashed
    error_type: Optional[str]  # e.g., "AttributeError", "KeyError"
    error_message: Optional[str]  # Human-readable error message
    crashing_payload: Optional[Any]  # The mutated payload that caused crash
    traceback: Optional[str]  # Full Python traceback
    iteration: Optional[int]  # Which iteration crashed (1-based)
    exit_code: Optional[int]  # Process exit code
    stdout: Optional[str]  # Standard output from target
    stderr: Optional[str]  # Standard error from target
    error: Optional[str]  # Error type if success=False
    message: Optional[str]  # Error message if success=False


# ============================================================================
# TOOL METADATA
# ============================================================================

INJECT_NULL_FAULT_METADATA = {
    "name": "inject_null_fault",
    "description": (
        "Inject null faults into nested data structures for crash discovery. "
        "Simulates missing data, null pointer scenarios, and incomplete API responses. "
        "Returns mutated payload with metadata. Use this to discover bugs, not fix them."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "data": {
                "type": "string",
                "description": "JSON string of input dictionary to mutate"
            },
            "probability": {
                "type": "number",
                "description": "Chance (0.0-1.0) of replacing any value with None",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.3
            },
            "seed": {
                "type": "integer",
                "description": "Optional random seed for deterministic behavior"
            }
        },
        "required": ["data"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "mutated_data": {"description": "The mutated payload"},
            "mutations": {"type": "integer", "description": "Count of None values"},
            "probability": {"type": "number"},
            "seed": {"type": "integer"},
            "error": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["success"]
    },
    "examples": [
        {
            "input": {
                "data": '{"user": {"name": "John", "age": 30}}',
                "probability": 0.5,
                "seed": 42
            },
            "output": {
                "success": True,
                "mutated_data": {"user": {"name": None, "age": 30}},
                "mutations": 1,
                "probability": 0.5,
                "seed": 42
            }
        },
        {
            "input": {
                "data": '{"items": [1, 2, 3], "total": 6}',
                "probability": 0.3
            },
            "output": {
                "success": True,
                "mutated_data": {"items": [1, None, 3], "total": None},
                "mutations": 2,
                "probability": 0.3,
                "seed": None
            }
        }
    ]
}

RUN_CHAOS_TEST_METADATA = {
    "name": "run_chaos_test",
    "description": (
        "Run chaos test by injecting faults and executing target application. "
        "Captures crashes, errors, tracebacks, and identifies crashing payloads. "
        "Returns structured crash report for AI analysis. Discovers bugs, does NOT fix them."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "target_path": {
                "type": "string",
                "description": "Path to target Python file (relative to workspace)"
            },
            "payload": {
                "type": "string",
                "description": "JSON string of input data to mutate and pass to target"
            },
            "probability": {
                "type": "number",
                "description": "Chance (0.0-1.0) of replacing values with None",
                "minimum": 0.0,
                "maximum": 1.0,
                "default": 0.3
            },
            "seed": {
                "type": "integer",
                "description": "Optional random seed for deterministic behavior"
            },
            "iterations": {
                "type": "integer",
                "description": "Number of chaos iterations to run",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["target_path", "payload"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "crash_detected": {"type": "boolean"},
            "error_type": {"type": "string", "description": "e.g., AttributeError, KeyError"},
            "error_message": {"type": "string"},
            "crashing_payload": {"description": "The mutated payload that caused crash"},
            "traceback": {"type": "string", "description": "Full Python traceback"},
            "iteration": {"type": "integer", "description": "Which iteration crashed"},
            "exit_code": {"type": "integer"},
            "stdout": {"type": "string"},
            "stderr": {"type": "string"},
            "error": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["success"]
    },
    "examples": [
        {
            "input": {
                "target_path": "target_app.py",
                "payload": '{"user": {"profile": {"name": "John"}}}',
                "probability": 0.5,
                "seed": 42
            },
            "output": {
                "success": True,
                "crash_detected": True,
                "error_type": "AttributeError",
                "error_message": "'NoneType' object has no attribute 'lower'",
                "crashing_payload": {"user": {"profile": None}},
                "traceback": "Traceback (most recent call last):\n  File \"target_app.py\", line 10...",
                "iteration": 1,
                "exit_code": 1,
                "stdout": "",
                "stderr": "Traceback..."
            }
        },
        {
            "input": {
                "target_path": "api_handler.py",
                "payload": '{"request": {"headers": {"auth": "token123"}}}',
                "probability": 0.3,
                "iterations": 5
            },
            "output": {
                "success": True,
                "crash_detected": False,
                "error_type": None,
                "error_message": None,
                "crashing_payload": None,
                "traceback": None,
                "iteration": None,
                "exit_code": 0,
                "stdout": "Success",
                "stderr": ""
            }
        }
    ]
}

RUN_COMMAND_METADATA = {
    "name": "run_command",
    "description": (
        "Execute shell commands for running tests and verifying resilience after crash discovery. "
        "Supports cross-stack testing (pytest, npm test, cargo test, go test, etc.). "
        "Returns exit code, stdout, stderr, and duration. Local development environments only."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "Shell command to execute (e.g., 'pytest tests/', 'npm test', 'cargo build')"
            },
            "cwd": {
                "type": "string",
                "description": "Optional working directory relative to workspace (default: workspace root)"
            },
            "timeout_seconds": {
                "type": "integer",
                "description": "Optional timeout in seconds (default: 30)",
                "minimum": 1,
                "maximum": 300,
                "default": 30
            }
        },
        "required": ["command"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "exit_code": {"type": "integer", "description": "Process exit code (0 = success)"},
            "stdout": {"type": "string", "description": "Standard output from command"},
            "stderr": {"type": "string", "description": "Standard error from command"},
            "duration_ms": {"type": "integer", "description": "Execution duration in milliseconds"},
            "command": {"type": "string", "description": "Echo of executed command"},
            "cwd": {"type": "string", "description": "Echo of working directory"},
            "error": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["success"]
    },
    "examples": [
        {
            "input": {
                "command": "pytest tests/test_app.py -v",
                "timeout_seconds": 60
            },
            "output": {
                "success": True,
                "exit_code": 0,
                "stdout": "===== test session starts =====\ntests/test_app.py::test_example PASSED\n===== 1 passed in 0.05s =====",
                "stderr": "",
                "duration_ms": 1250,
                "command": "pytest tests/test_app.py -v",
                "cwd": None
            }
        },
        {
            "input": {
                "command": "npm test",
                "cwd": "frontend"
            },
            "output": {
                "success": True,
                "exit_code": 0,
                "stdout": "PASS  src/App.test.js\n✓ renders without crashing (25ms)",
                "stderr": "",
                "duration_ms": 3420,
                "command": "npm test",
                "cwd": "frontend"
            }
        },
        {
            "input": {
                "command": "cargo test",
                "timeout_seconds": 120
            },
            "output": {
                "success": True,
                "exit_code": 0,
                "stdout": "running 5 tests\ntest result: ok. 5 passed; 0 failed",
                "stderr": "",
                "duration_ms": 8750,
                "command": "cargo test",
                "cwd": None
            }
        }
    ]
}


# ============================================================================
# RUN_COMMAND TOOL SCHEMAS
# ============================================================================

class RunCommandInput(TypedDict):
    """
    Input schema for run_command tool.
    
    This tool executes shell commands for testing and resilience verification
    after fault injection and crash discovery.
    
    Fields:
        command: Shell command to execute
        cwd: Optional working directory (relative to workspace)
        timeout_seconds: Optional timeout in seconds (default: 30)
    """
    command: str  # Shell command to execute
    cwd: Optional[str]  # Working directory
    timeout_seconds: Optional[int]  # Timeout in seconds


class RunCommandOutput(TypedDict):
    """
    Output schema for run_command tool.
    
    Returns execution results including exit code, output, and timing.
    """
    success: bool
    exit_code: Optional[int]  # Process exit code
    stdout: Optional[str]  # Standard output
    stderr: Optional[str]  # Standard error
    duration_ms: Optional[int]  # Execution duration in milliseconds
    command: Optional[str]  # Echo of executed command
    cwd: Optional[str]  # Echo of working directory
    error: Optional[str]  # Error type if success=False
    message: Optional[str]  # Error message if success=False


# ============================================================================
# LEGACY SCHEMAS (for backward compatibility)
# ============================================================================

class InjectFaultInput(TypedDict):
    """Input schema for inject_fault tool (legacy)."""
    target: str
    fault_type: Literal[
        "null_pointer",
        "key_error",
        "type_error",
        "zero_division",
        "network_latency",
        "resource_exhaustion",
        "corrupt_data",
        "timeout",
        "exception"
    ]
    target_function: Optional[str]
    target_line: Optional[int]
    probability: Optional[float]


class AddLatencyInput(TypedDict):
    """Input schema for add_latency tool (legacy)."""
    target: str
    duration_ms: int
    probability: Optional[float]
    target_function: Optional[str]


class CorruptPayloadInput(TypedDict):
    """Input schema for corrupt_payload tool (legacy)."""
    target: str
    corruption_type: Optional[Literal["random", "truncate", "encoding"]]
    target_function: Optional[str]
    probability: Optional[float]


# ============================================================================
# READ_FILE TOOL SCHEMAS
# ============================================================================

class ReadFileInput(TypedDict):
    """
    Input schema for read_file tool.
    
    This tool safely reads crash reports and logs after fault injection runs.
    Includes security checks to prevent reading sensitive files.
    
    Fields:
        path: Path to file (relative to project root)
        max_bytes: Maximum bytes to read (default: 20000)
    """
    path: str  # File path relative to project root
    max_bytes: Optional[int]  # Max bytes to read, default 20000


class ReadFileOutput(TypedDict):
    """
    Output schema for read_file tool.
    
    Returns file content with metadata. Used for reading crash reports, not generating fixes.
    """
    success: bool
    path: str  # Echo of requested path
    content: Optional[str]  # File content (None if error)
    truncated: bool  # True if content was truncated
    size_bytes: int  # Total file size in bytes
    error: Optional[str]  # Error type if success=False
    message: Optional[str]  # Error message if success=False


READ_FILE_METADATA = {
    "name": "read_file",
    "description": (
        "Safely read crash reports and logs after fault injection runs. "
        "Includes security checks to block sensitive files and paths outside project root. "
        "Returns file content for AI analysis. Reads reports, does NOT generate fixes."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Path to file (relative to project root)"
            },
            "max_bytes": {
                "type": "integer",
                "description": "Maximum bytes to read (default: 20000)",
                "minimum": 1,
                "maximum": 1000000,
                "default": 20000
            }
        },
        "required": ["path"]
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "path": {"type": "string", "description": "Echo of requested path"},
            "content": {"type": "string", "description": "File content"},
            "truncated": {"type": "boolean", "description": "True if content was truncated"},
            "size_bytes": {"type": "integer", "description": "Total file size in bytes"},
            "error": {"type": "string"},
            "message": {"type": "string"}
        },
        "required": ["success", "path", "truncated", "size_bytes"]
    },
    "examples": [
        {
            "input": {
                "path": "chaos_report.json",
                "max_bytes": 10000
            },
            "output": {
                "success": True,
                "path": "chaos_report.json",
                "content": '{"crash_detected": true, "error_type": "AttributeError", ...}',
                "truncated": False,
                "size_bytes": 1234
            }
        },
        {
            "input": {
                "path": "logs/chaos_run_2024.log",
                "max_bytes": 5000
            },
            "output": {
                "success": True,
                "path": "logs/chaos_run_2024.log",
                "content": "[2024-01-15 10:30:00] Starting chaos test...\n[2024-01-15 10:30:01] Injecting null faults...",
                "truncated": True,
                "size_bytes": 15000
            }
        },
        {
            "input": {
                "path": "../../../etc/passwd"
            },
            "output": {
                "success": False,
                "path": "../../../etc/passwd",
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "SecurityError",
                "message": "Access denied: path outside project root"
            }
        },
        {
            "input": {
                "path": ".env"
            },
            "output": {
                "success": False,
                "path": ".env",
                "content": None,
                "truncated": False,
                "size_bytes": 0,
                "error": "SecurityError",
                "message": "Access denied: blocked file pattern '.env'"
            }
        }
    ]
}


# Made with Bob
