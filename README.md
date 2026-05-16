# ChaosMonkey AI

**MCP-First Autonomous Fault Injection & Crash Discovery**

ChaosMonkey AI is an autonomous chaos engineering platform that uses AI agents (Bob, Claude, Codex, etc.) to inject faults, run target applications, detect crashes, and generate structured resilience reports through MCP (Model Context Protocol) tools.

## 🎯 Core Concept

ChaosMonkey performs **autonomous fault injection and crash discovery only**. It does NOT fix code, write files, create branches, or open PRs.

AI agents connect to ChaosMonkey through MCP tools to:

1. **Inject faults** into data structures (`inject_null_fault`)
2. **Run chaos tests** on target applications (`run_chaos_test`)
3. **Execute commands** for testing across any stack (`run_command`)
4. **Read reports** and logs after chaos runs (`read_file`)

## 🏗️ Architecture

```
chaosmonkey/
├── tools/           # MCP tool implementations
│   ├── fault_injection.py    # inject_null_fault
│   ├── observation.py         # Crash observation utilities
│   ├── testing.py             # Test execution helpers
│   └── analysis.py            # Crash analysis utilities
├── core/            # Core chaos engineering logic
│   ├── executor.py            # Fault execution engine
│   ├── observer.py            # Crash detection and observation
│   ├── models.py              # Data models (CrashReport, FaultConfig)
│   └── utils.py               # Utilities
└── mcp/             # MCP server implementation
    ├── server.py              # MCP server with 4 core tools
    └── schemas.py             # Tool schemas
```

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed design.

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Test installation
chaosmonkey test
```

### Chaos Execution Flow

Execute the complete chaos engineering workflow on [`target_app.py`](target_app.py):

```bash
# Run chaos execution with default settings
uv run python -m chaosmonkey.main chaos

# Use deterministic seed for reproducible results
uv run python -m chaosmonkey.main chaos --seed 42

# Control fault injection probability
uv run python -m chaosmonkey.main chaos --probability 0.5 --seed 123
```

**What it does:**
1. Generates mutated payload using `inject_null_fault`
2. Executes target function with mutated payload
3. Captures exceptions, traceback, and crash type
4. Prints structured chaos report with rich formatting

### Demo: Null Fault Injection

Test the `inject_null_fault` tool in isolation:

```bash
# Use example data
uv run python -m chaosmonkey.main demo

# Inject nulls into custom JSON
uv run python -m chaosmonkey.main demo --input '{"user": {"name": "John", "age": 30}}'

# Control probability and use deterministic seed
uv run python -m chaosmonkey.main demo \
  --input '{"profile": {"name": "Alice"}}' \
  --probability 0.5 \
  --seed 42

# Pipe JSON from stdin
echo '{"items": [1, 2, 3]}' | uv run python -m chaosmonkey.main demo
```

**Programmatic Usage:**

```python
from chaosmonkey.tools import inject_null_fault

data = {
    "profile": {
        "name": "John",
        "email": "john@example.com"
    }
}

# Inject nulls with 30% probability
mutated = inject_null_fault(data, probability=0.3, seed=42)

# Example output:
# {
#     "profile": {
#         "name": None,
#         "email": "john@example.com"
#     }
# }
```

### Legacy Mode (Current)

Run a Python file and analyze crashes:

```bash
chaosmonkey run target_app.py
```

### MCP Mode (Future)

Start the MCP server for AI agents:

```bash
chaosmonkey serve --host localhost --port 8080
```

> **Note**: MCP server implementation is pending. See [Architecture](#architecture) for details.

## 🛠️ Core MCP Tools

ChaosMonkey exposes 4 production-ready MCP tools for fault injection and crash discovery:

### 1. inject_null_fault
Mutate data structures by randomly replacing nested values with None to simulate missing data, null pointer scenarios, and incomplete API responses.

**Parameters:**
- `data` (string): JSON string of input dictionary to mutate
- `probability` (float): Chance (0.0-1.0) of replacing values with None (default: 0.3)
- `seed` (int, optional): Random seed for deterministic behavior

**Returns:** Mutated payload with metadata about mutations

### 2. run_chaos_test
Execute chaos tests by injecting faults and running target Python applications. Captures crashes, errors, tracebacks, and identifies which mutated payload caused the failure.

**Parameters:**
- `target_path` (string): Path to target Python file
- `payload` (string): JSON string of input data to mutate
- `probability` (float): Fault injection probability (default: 0.3)
- `seed` (int, optional): Random seed for deterministic behavior
- `iterations` (int): Number of chaos iterations (default: 1)

**Returns:** Structured crash report with error details and traceback

### 3. run_command
Execute shell commands for running tests across any stack (pytest, npm test, cargo test, go test, etc.). Includes safety checks to block dangerous commands.

**Parameters:**
- `command` (string): Shell command to execute
- `cwd` (string, optional): Working directory
- `timeout_seconds` (int): Timeout in seconds (default: 30, max: 300)

**Returns:** Exit code, stdout, stderr, and execution duration

### 4. read_file
Safely read local files (reports, logs, chaos results) after chaos runs. Includes security checks to prevent reading sensitive files or paths outside project root.

**Parameters:**
- `path` (string): File path relative to project root
- `max_bytes` (int): Maximum bytes to read (default: 20000, max: 1000000)

**Returns:** File content with truncation metadata

See [`MCP_TOOLS.md`](MCP_TOOLS.md) for detailed documentation.

## 🤖 AI Agent Workflow

ChaosMonkey focuses on **fault injection and crash discovery**. AI agents use the tools to find bugs, not fix them.

```python
# 1. Inject null faults into payload
result = inject_null_fault(
    data='{"user": {"profile": {"name": "John"}}}',
    probability=0.5,
    seed=42
)

# 2. Run chaos test on target application
crash_report = run_chaos_test(
    target_path="target_app.py",
    payload='{"user": {"profile": {"name": "John"}}}',
    probability=0.5,
    seed=42
)

# 3. Read generated crash report
report = read_file(path="chaos_report.json")

# 4. Run regression tests to verify resilience
test_result = run_command(command="pytest tests/test_null_safety.py")

# AI agent analyzes crash reports and generates insights
# Remediation is handled separately by other tools/workflows
```

## 📋 Roadmap

**Completed:**
- [x] Design MCP-first architecture
- [x] Implement `inject_null_fault` tool
- [x] Implement `run_chaos_test` tool
- [x] Implement `run_command` tool
- [x] Implement `read_file` tool
- [x] Add CLI demo and chaos commands
- [x] Implement chaos execution flow (executor + observer)
- [x] Production-ready MCP server with FastMCP

**Future Enhancements:**
- [ ] Additional fault types (latency, corruption, timeouts)
- [ ] Support for more languages (JavaScript, Go, Rust, Java)
- [ ] Integration with Sentry for production incident analysis
- [ ] Integration with IBM Bob MCP for AI-powered crash analysis
- [ ] Integration with watsonx for advanced AI reasoning
- [ ] Distributed system chaos testing support

## 🔧 Development

```bash
# Run tests
pytest

# Type checking
mypy chaosmonkey

# Format code
black chaosmonkey

# Lint
ruff check chaosmonkey
```

## 📚 Documentation

- [`ARCHITECTURE.md`](ARCHITECTURE.md) - Detailed architecture design
- Tool documentation - See individual tool modules in [`chaosmonkey/tools/`](chaosmonkey/tools/)

## 🎯 Design Principles

1. **MCP-First** - All operations exposed as MCP tools
2. **Fault Injection Only** - Focus on finding bugs, not fixing them
3. **Crash Discovery** - Detect and report failures with structured data
4. **Provider-Agnostic** - Works with any MCP-compatible AI agent (Bob, Claude, Cursor, Codex)
5. **Safe** - Controlled fault injection with security checks
6. **Cross-Stack** - Test any language/framework via `run_command`

## 📝 License

MIT

---

**Made with ❤️ for autonomous chaos engineering**