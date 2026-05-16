# ChaosMonkey AI - MCP Tools Documentation

Production-ready MCP tools for autonomous fault injection and crash discovery.

## Overview

**Scope:** ChaosMonkey performs autonomous fault injection and crash discovery ONLY. It does NOT fix code, write files, create branches, or open PRs.

ChaosMonkey AI exposes four core MCP tools designed for AI agents (Claude, Bob, Cursor, Codex) to inject faults, run tests, detect crashes, and generate structured resilience reports:

1. **inject_null_fault** - Mutate data structures to simulate missing data
2. **run_chaos_test** - Execute chaos tests and capture crashes
3. **run_command** - Execute shell commands for running tests across any stack
4. **read_file** - Safely read local reports and logs after chaos runs

These tools enable AI agents to discover bugs through fault injection, not fix them.

## Tool 1: inject_null_fault

### Description

Inject null faults into nested data structures to simulate missing data, null pointer scenarios, and incomplete API responses. Returns mutated payload with metadata about mutations.

### Use Cases

- Testing null pointer handling
- Simulating incomplete API responses
- Finding missing data validation bugs
- Chaos testing data pipelines

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": "string",
      "description": "JSON string of input dictionary to mutate",
      "required": true
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
}
```

### Output Schema

```json
{
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
}
```

### Examples

#### Example 1: Basic Mutation

**Input:**
```json
{
  "data": "{\"user\": {\"name\": \"John\", \"age\": 30}}",
  "probability": 0.5,
  "seed": 42
}
```

**Output:**
```json
{
  "success": true,
  "mutated_data": {"user": {"name": null, "age": 30}},
  "mutations": 1,
  "probability": 0.5,
  "seed": 42
}
```

#### Example 2: Array Mutation

**Input:**
```json
{
  "data": "{\"items\": [1, 2, 3], \"total\": 6}",
  "probability": 0.3
}
```

**Output:**
```json
{
  "success": true,
  "mutated_data": {"items": [1, null, 3], "total": null},
  "mutations": 2,
  "probability": 0.3,
  "seed": null
}
```

#### Example 3: Error Handling

**Input:**
```json
{
  "data": "invalid json",
  "probability": 0.3
}
```

**Output:**
```json
{
  "success": false,
  "mutated_data": null,
  "mutations": null,
  "probability": null,
  "seed": null,
  "error": "JSONDecodeError",
  "message": "Invalid JSON input: Expecting value: line 1 column 1 (char 0)"
}
```

---

## Tool 2: run_chaos_test

### Description

Run chaos test by injecting null faults into payload and executing target Python application. Captures crashes, errors, tracebacks, and identifies which mutated payload caused the failure. Essential for finding null pointer bugs and missing data handling issues.

### Use Cases

- Finding null pointer bugs in production code
- Testing error handling and resilience
- Identifying missing data validation
- Generating regression tests from crashes
- Root cause analysis of production incidents

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "target_path": {
      "type": "string",
      "description": "Path to target Python file (relative to workspace)",
      "required": true
    },
    "payload": {
      "type": "string",
      "description": "JSON string of input data to mutate and pass to target",
      "required": true
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
}
```

### Output Schema

```json
{
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
}
```

### Examples

#### Example 1: Crash Detected

**Input:**
```json
{
  "target_path": "target_app.py",
  "payload": "{\"user\": {\"profile\": {\"name\": \"John\"}}}",
  "probability": 0.5,
  "seed": 42
}
```

**Output:**
```json
{
  "success": true,
  "crash_detected": true,
  "error_type": "AttributeError",
  "error_message": "'NoneType' object has no attribute 'lower'",
  "crashing_payload": {"user": {"profile": null}},
  "traceback": "Traceback (most recent call last):\n  File \"target_app.py\", line 10, in process_user\n    name = user['profile']['name'].lower()\nAttributeError: 'NoneType' object has no attribute 'lower'",
  "iteration": 1,
  "exit_code": 1,
  "stdout": "",
  "stderr": "Traceback..."
}
```

#### Example 2: No Crash (Resilient Code)

**Input:**
```json
{
  "target_path": "api_handler.py",
  "payload": "{\"request\": {\"headers\": {\"auth\": \"token123\"}}}",
  "probability": 0.3,
  "iterations": 5
}
```

**Output:**
```json
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
```

#### Example 3: File Not Found Error

**Input:**
```json
{
  "target_path": "nonexistent.py",
  "payload": "{\"data\": \"test\"}"
}
```

**Output:**
```json
{
  "success": false,
  "crash_detected": null,
  "error_type": null,
  "error_message": null,
  "crashing_payload": null,
  "traceback": null,
  "iteration": null,
  "exit_code": null,
  "stdout": null,
  "stderr": null,
  "error": "FileNotFoundError",
  "message": "Target file not found: nonexistent.py"
}
```

---

## Tool 3: run_command

### Description

Execute shell commands in the project environment for running tests, builds, and other development tasks. Returns exit code, stdout, stderr, and execution duration. Designed for local trusted development environments only.

### Use Cases

- Running project-specific test commands (pytest, npm test, cargo test, go test)
- Building projects (npm run build, cargo build, mvn package)
- Running linters and formatters (eslint, black, rustfmt)
- Executing custom scripts and development tasks
- Cross-stack testing support (Python, JavaScript, Rust, Go, Java, etc.)

### Safety Features

This tool includes comprehensive safety checks to prevent dangerous operations:

**Blocked Commands:**
- File system destruction: `rm -rf`, `rm -r`, `mkfs`, `dd if=`
- System control: `shutdown`, `reboot`, `halt`, `poweroff`
- Privilege escalation: `sudo` commands (except safe ones like `sudo -v`)
- Fork bombs and malicious patterns
- Dangerous file operations on system directories

**Note:** This tool is designed for LOCAL TRUSTED DEVELOPMENT ENVIRONMENTS ONLY.

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "command": {
      "type": "string",
      "description": "Shell command to execute (e.g., 'pytest tests/', 'npm test', 'cargo build')",
      "required": true
    },
    "cwd": {
      "type": "string",
      "description": "Optional working directory relative to workspace (default: workspace root)"
    },
    "timeout_seconds": {
      "type": "integer",
      "description": "Optional timeout in seconds (default: 30, max: 300)",
      "minimum": 1,
      "maximum": 300,
      "default": 30
    }
  },
  "required": ["command"]
}
```

### Output Schema

```json
{
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
}
```

### Examples

#### Example 1: Python Tests (pytest)

**Input:**
```json
{
  "command": "pytest tests/test_app.py -v",
  "timeout_seconds": 60
}
```

**Output:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "===== test session starts =====\ntests/test_app.py::test_example PASSED\n===== 1 passed in 0.05s =====",
  "stderr": "",
  "duration_ms": 1250,
  "command": "pytest tests/test_app.py -v",
  "cwd": null
}
```

#### Example 2: JavaScript Tests (npm)

**Input:**
```json
{
  "command": "npm test",
  "cwd": "frontend"
}
```

**Output:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "PASS  src/App.test.js\n✓ renders without crashing (25ms)\n\nTest Suites: 1 passed, 1 total\nTests:       1 passed, 1 total",
  "stderr": "",
  "duration_ms": 3420,
  "command": "npm test",
  "cwd": "frontend"
}
```

#### Example 3: Rust Tests (cargo)

**Input:**
```json
{
  "command": "cargo test",
  "timeout_seconds": 120
}
```

**Output:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "running 5 tests\ntest tests::test_add ... ok\ntest tests::test_subtract ... ok\ntest tests::test_multiply ... ok\ntest tests::test_divide ... ok\ntest tests::test_modulo ... ok\n\ntest result: ok. 5 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out",
  "stderr": "",
  "duration_ms": 8750,
  "command": "cargo test",
  "cwd": null
}
```

#### Example 4: Failed Test

**Input:**
```json
{
  "command": "pytest tests/test_failing.py"
}
```

**Output:**
```json
{
  "success": true,
  "exit_code": 1,
  "stdout": "",
  "stderr": "===== FAILURES =====\n_____ test_failing _____\nAssertionError: Expected 2, got 3",
  "duration_ms": 890,
  "command": "pytest tests/test_failing.py",
  "cwd": null
}
```

#### Example 5: Dangerous Command Blocked

**Input:**
```json
{
  "command": "rm -rf /"
}
```

**Output:**
```json
{
  "success": false,
  "exit_code": null,
  "stdout": null,
  "stderr": null,
  "duration_ms": null,
  "command": "rm -rf /",
  "cwd": null,
  "error": "DangerousCommand",
  "message": "Command blocked for safety: Blocked dangerous pattern: rm -rf"
}
```

#### Example 6: Timeout

**Input:**
```json
{
  "command": "sleep 60",
  "timeout_seconds": 5
}
```

**Output:**
```json
{
  "success": false,
  "exit_code": null,
  "stdout": null,
  "stderr": null,
  "duration_ms": 5003,
  "command": "sleep 60",
  "cwd": null,
  "error": "TimeoutExpired",
  "message": "Command exceeded timeout of 5 seconds"
}
```

---

## Tool 4: read_file

### Description

Safely read local files (reports, logs, chaos results) after chaos runs. Includes security checks to block reading outside project root and sensitive files. Returns file content with truncation metadata.

### Use Cases

- Reading chaos test reports and results
- Analyzing application logs after chaos runs
- Inspecting crash dumps and error logs
- Reviewing generated test files
- Post-chaos analysis and debugging

### Security Features

This tool includes comprehensive security checks:

**Blocked Paths:**
- Paths outside project root (prevents directory traversal attacks)
- Sensitive files: `.env`, `credentials`, `id_rsa`, `tokens`, `secrets`, `.pem`, `.key`, `password`, etc.

**Safety Limits:**
- Maximum file size: 1MB (1,000,000 bytes)
- Default read limit: 20KB (20,000 bytes)
- Binary file detection (returns error for non-text files)

### Input Schema

```json
{
  "type": "object",
  "properties": {
    "path": {
      "type": "string",
      "description": "Path to file (relative to project root)",
      "required": true
    },
    "max_bytes": {
      "type": "integer",
      "description": "Maximum bytes to read (default: 20000, max: 1000000)",
      "minimum": 1,
      "maximum": 1000000,
      "default": 20000
    }
  },
  "required": ["path"]
}
```

### Output Schema

```json
{
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
}
```

### Examples

#### Example 1: Read Chaos Report

**Input:**
```json
{
  "path": "chaos_report.json",
  "max_bytes": 10000
}
```

**Output:**
```json
{
  "success": true,
  "path": "chaos_report.json",
  "content": "{\"crash_detected\": true, \"error_type\": \"AttributeError\", \"error_message\": \"'NoneType' object has no attribute 'lower'\", \"crashing_payload\": {\"user\": {\"profile\": null}}, \"traceback\": \"Traceback (most recent call last):\\n  File \\\"target_app.py\\\", line 10...\"}",
  "truncated": false,
  "size_bytes": 1234
}
```

#### Example 2: Read Log File (Truncated)

**Input:**
```json
{
  "path": "logs/chaos_run_2024.log",
  "max_bytes": 5000
}
```

**Output:**
```json
{
  "success": true,
  "path": "logs/chaos_run_2024.log",
  "content": "[2024-01-15 10:30:00] Starting chaos test...\n[2024-01-15 10:30:01] Injecting null faults with probability 0.3\n[2024-01-15 10:30:02] Executing target: target_app.py\n[2024-01-15 10:30:03] Crash detected: AttributeError\n[2024-01-15 10:30:04] Generating report...",
  "truncated": true,
  "size_bytes": 15000
}
```

#### Example 3: Security Error - Path Outside Root

**Input:**
```json
{
  "path": "../../../etc/passwd"
}
```

**Output:**
```json
{
  "success": false,
  "path": "../../../etc/passwd",
  "content": null,
  "truncated": false,
  "size_bytes": 0,
  "error": "SecurityError",
  "message": "Access denied: path outside project root (/Users/user/project)"
}
```

#### Example 4: Security Error - Blocked File Pattern

**Input:**
```json
{
  "path": ".env"
}
```

**Output:**
```json
{
  "success": false,
  "path": ".env",
  "content": null,
  "truncated": false,
  "size_bytes": 0,
  "error": "SecurityError",
  "message": "Access denied: blocked file pattern '.env'"
}
```

#### Example 5: File Not Found

**Input:**
```json
{
  "path": "nonexistent_report.json"
}
```

**Output:**
```json
{
  "success": false,
  "path": "nonexistent_report.json",
  "content": null,
  "truncated": false,
  "size_bytes": 0,
  "error": "FileNotFoundError",
  "message": "File not found: nonexistent_report.json"
}
```

#### Example 6: Binary File Error

**Input:**
```json
{
  "path": "image.png"
}
```

**Output:**
```json
{
  "success": false,
  "path": "image.png",
  "content": null,
  "truncated": false,
  "size_bytes": 45678,
  "error": "BinaryFileError",
  "message": "File is not a text file (binary content detected)"
}
```

---

## Integration Guide

### For AI Agents (Claude, Bob, Cursor, Codex)

These tools are designed to be called by AI agents through the MCP protocol. The structured schemas ensure predictable, type-safe interactions.

### Typical Workflow (Fault Injection & Crash Discovery)

ChaosMonkey focuses on **finding bugs, not fixing them**. The workflow is:

1. **Identify Target**: AI agent identifies a Python function to test
2. **Prepare Payload**: AI agent constructs a representative input payload
3. **Run Chaos Test**: Call [`run_chaos_test`](chaosmonkey/mcp/server.py:157) with target and payload
4. **Analyze Crash**: AI agent analyzes crash reports and tracebacks
5. **Read Reports**: Call [`read_file`](chaosmonkey/mcp/server.py:694) to read generated chaos reports
6. **Run Regression Tests**: Call [`run_command`](chaosmonkey/mcp/server.py:478) to verify resilience
7. **Generate Insights**: AI agent generates structured resilience report

**Note:** Remediation (fixing code, creating PRs) is handled by other tools/workflows, not ChaosMonkey.

### Error Handling

All tools return structured error responses with:
- `success: false` flag
- `error`: Error type (e.g., "FileNotFoundError", "JSONDecodeError")
- `message`: Human-readable error message

This ensures AI agents can gracefully handle failures and provide meaningful feedback.

---

## Technical Details

### Implementation

- **Framework**: FastMCP
- **Language**: Python 3.11+
- **Type Safety**: Full TypedDict schemas for input/output
- **Error Handling**: Comprehensive exception handling with structured responses
- **Determinism**: Optional seed parameter for reproducible results

### File Structure

```
chaosmonkey/mcp/
├── server.py          # MCP server with tool implementations
├── schemas.py         # TypedDict schemas and metadata
└── __main__.py        # Entry point for MCP server
```

### Running the MCP Server

```bash
python -m chaosmonkey.mcp.server
```

---

## Future Enhancements

**Completed:**
- [x] Add [`read_file`](chaosmonkey/mcp/server.py:694) tool for reading chaos reports and logs
- [x] Add [`run_command`](chaosmonkey/mcp/server.py:478) tool for cross-stack testing
- [x] Production-ready MCP server with FastMCP
- [x] Comprehensive security checks for file reading and command execution

**Planned:**
- [ ] Additional fault types (latency, corruption, timeouts, boundary conditions)
- [ ] Support for more languages (JavaScript, Go, Rust, Java)
- [ ] Integration with Sentry for production incident analysis
- [ ] Integration with IBM Bob MCP for AI-powered crash analysis
- [ ] Integration with watsonx for advanced AI reasoning
- [ ] Distributed system chaos testing support

---

**Made with Bob** 🤖