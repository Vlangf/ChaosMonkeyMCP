# ChaosMonkey AI - MCP-First Architecture

## Overview

ChaosMonkey AI is an autonomous fault injection and crash discovery platform that uses AI agents (Bob, Claude, Codex, etc.) to inject faults, run target applications, detect crashes, and generate structured resilience reports through MCP (Model Context Protocol) tools.

**Scope:** ChaosMonkey performs autonomous fault injection and crash discovery ONLY. It does NOT fix code, write files, create branches, or open PRs.

## Architecture Principles

1. **MCP-First**: All operations exposed as MCP tools
2. **Fault Injection Only**: Focus on finding bugs, not fixing them
3. **Crash Discovery**: Detect and report failures with structured data
4. **Provider-Agnostic**: Works with any MCP-compatible AI agent
5. **Cross-Stack**: Test any language/framework via `run_command`

## Directory Structure

```
chaosmonkey/
├── tools/           # MCP tool implementations
│   ├── __init__.py
│   ├── fault_injection.py    # inject_null_fault
│   ├── observation.py         # Crash observation utilities
│   ├── testing.py             # Test execution helpers
│   └── analysis.py            # Crash analysis utilities
├── core/            # Core chaos engineering logic
│   ├── __init__.py
│   ├── executor.py            # Fault execution engine
│   ├── observer.py            # Crash detection and observation
│   ├── models.py              # Data models (CrashReport, FaultConfig)
│   └── utils.py               # Shared utilities
└── mcp/             # MCP server implementation
    ├── __init__.py
    ├── server.py              # MCP server with 4 core tools
    └── schemas.py             # MCP tool schemas and types
```

## Core Components

### 1. Tools Layer (`chaosmonkey/tools/`)

MCP-exposed tools that AI agents can call:

**Core Tools (Production-Ready):**
- `inject_null_fault(data, probability, seed)` - Mutate data structures with null values
- `run_chaos_test(target_path, payload, probability, seed, iterations)` - Execute chaos tests and capture crashes
- `run_command(command, cwd, timeout_seconds)` - Execute shell commands for testing
- `read_file(path, max_bytes)` - Safely read reports and logs after chaos runs

**Supporting Utilities:**
- Fault injection helpers in `fault_injection.py`
- Crash observation utilities in `observation.py`
- Test execution helpers in `testing.py`
- Crash analysis utilities in `analysis.py`

### 2. Core Layer (`chaosmonkey/core/`)

Business logic for fault injection and crash discovery:

**Executor (`executor.py`):**
- Fault injection mechanisms
- Target function execution
- Crash detection and capture

**Observer (`observer.py`):**
- Crash observation and monitoring
- Traceback extraction
- Error classification

**Models (`models.py`):**
- `FaultConfig` - Fault injection configuration
- `CrashReport` - Crash details and traceback
- `ObservationResult` - System observation data

### 3. MCP Layer (`chaosmonkey/mcp/`)

MCP server implementation:

**Server:**
- Tool registration
- Request handling
- Response formatting

**Schemas:**
- Tool input/output schemas
- Type definitions
- Validation rules

## Workflow

```
AI Agent (Bob/Claude/etc.)
    ↓
MCP Protocol
    ↓
ChaosMonkey MCP Server (4 core tools)
    ↓
Tool Layer (inject_null_fault, run_chaos_test, run_command, read_file)
    ↓
Core Layer (executor, observer)
    ↓
Target Application
    ↓
Structured Crash Report
```

## Example AI Agent Workflow

ChaosMonkey focuses on **fault injection and crash discovery**. Remediation is handled separately.

1. **Inject Fault**: `inject_null_fault(data='{"user": {...}}', probability=0.5, seed=42)`
2. **Run Chaos Test**: `run_chaos_test(target_path="app.py", payload='{"user": {...}}', probability=0.5)`
3. **Read Report**: `read_file(path="chaos_report.json")`
4. **Run Tests**: `run_command(command="pytest tests/test_null_safety.py")`
5. **AI Analysis**: Agent analyzes crash reports and generates insights
6. **Remediation**: Handled by other tools/workflows (not ChaosMonkey's responsibility)

## Core Components Detail

### MCP Server (`chaosmonkey/mcp/server.py`)

Production-ready FastMCP server exposing 4 tools:
- `inject_null_fault_tool` - Data mutation
- `run_chaos_test` - Chaos test execution
- `run_command` - Shell command execution with safety checks
- `read_file` - Secure file reading with path validation

### Schemas (`chaosmonkey/mcp/schemas.py`)

TypedDict schemas for all tool inputs/outputs:
- `InjectNullFaultInput/Output`
- `RunChaosTestInput/Output`
- `RunCommandInput/Output`
- `ReadFileInput/Output`

### Fault Executor (`chaosmonkey/core/executor.py`)

Executes chaos tests:
- Injects faults into payloads
- Runs target functions
- Captures crashes and exceptions
- Returns structured crash reports

### Observer (`chaosmonkey/core/observer.py`)

Monitors execution:
- Detects crashes
- Extracts tracebacks
- Classifies error types

## Security & Safety

**Command Execution Safety:**
- Blocks dangerous patterns (rm -rf, shutdown, sudo, etc.)
- Timeout limits (max 300 seconds)
- Working directory validation

**File Reading Security:**
- Path must be within project root (prevents directory traversal)
- Blocks sensitive files (.env, credentials, private keys, etc.)
- File size limits (max 1MB)
- Binary file detection

## Future Enhancements

- [ ] Additional fault types (latency, corruption, timeouts)
- [ ] Support for more languages (JavaScript, Go, Rust, Java)
- [ ] Integration with Sentry for production incident analysis
- [ ] Integration with IBM Bob MCP for AI-powered crash analysis
- [ ] Integration with watsonx for advanced AI reasoning
- [ ] Distributed system chaos testing support