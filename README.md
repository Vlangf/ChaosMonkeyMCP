# ChaosMonkey MCP

Local MCP server for autonomous fault injection and crash discovery.

## Demo

<video src="./chm_ibm_bob_mcp.mov" controls width="100%"></video>

If the video preview is not rendered by your Markdown viewer, open it directly: [chm_ibm_bob_mcp.mp4](./chm_ibm_bob_mcp.mov).

ChaosMonkey MCP exposes provider-agnostic tools that an AI client can use to mutate inputs, run chaos tests, execute local commands, and inspect logs or reports. It is designed for MCP-compatible clients such as IBM Bob, Claude, Cursor, and Codex.

ChaosMonkey MCP does not fix code, modify repositories, create branches, open pull requests, or write patches.

## What it does

ChaosMonkey MCP helps AI agents find resilience issues in local development projects.

It can:

- inject null faults into JSON-like payloads
- run repeated chaos tests against Python targets
- execute local test/build commands with basic safety checks
- read local logs and reports inside the project root
- return structured crash data, tracebacks, stdout, and stderr

It only performs fault injection, command execution, report/log reading, and crash discovery.

## Core tools

`inject_null_fault_tool`

Mutates a JSON payload by replacing nested values with `null`.

Inputs:

- `data`: JSON string
- `probability`: chance of replacing a value, default `0.3`
- `seed`: optional deterministic seed

Returns mutated data, mutation count, and error metadata.

`run_chaos_test`

Injects null faults into a payload and executes a target Python file.

Inputs:

- `target_path`: path to a `.py` file
- `payload`: JSON string passed to the target function after mutation
- `probability`: fault probability, default `0.3`
- `seed`: optional deterministic seed
- `iterations`: number of chaos iterations, default `1`

Returns whether a crash was detected, the crashing payload, traceback, error type, stdout, stderr, and exit code.

`run_command`

Executes a local shell command for tests, builds, or project-specific checks.

Inputs:

- `command`: shell command
- `cwd`: optional working directory
- `timeout_seconds`: command timeout, default `30`, max `300`

Returns exit code, stdout, stderr, duration, and command metadata. Dangerous command patterns such as destructive `rm`, `sudo`, shutdown, reboot, and disk-formatting commands are blocked.

`read_file`

Reads a local text file from the project root.

Inputs:

- `path`: file path relative to the project root
- `max_bytes`: read limit, default `20000`, max `1000000`

Returns file content, truncation status, file size, and error metadata. Paths outside the project root and common secret files are blocked.

## Installation

Requirements:

- Python `>=3.14`
- `uv`

Install dependencies:

```bash
uv sync
```

Check the CLI entrypoint:

```bash
uv run chaosmonkey test
```

## Start MCP server

Run the local stdio MCP server:

```bash
uv run python -m chaosmonkey.mcp.server
```

The server runs locally over stdio. MCP clients start it as a subprocess and communicate with it through the Model Context Protocol.

## MCP client setup

Use the same server command in any MCP-compatible client:

```json
{
  "mcpServers": {
    "chaosmonkey": {
      "command": "uv",
      "args": ["run", "python", "-m", "chaosmonkey.mcp.server"],
      "cwd": "/absolute/path/to/chaosmonkey-ai"
    }
  }
}
```

Set `cwd` to this repository path.

Known compatible clients:

- IBM Bob
- Claude Desktop / Claude Code MCP clients
- Cursor
- Codex MCP clients
- other stdio MCP clients

For local inspection:

```bash
npx @modelcontextprotocol/inspector uv run python -m chaosmonkey.mcp.server
```

## Example AI workflow

Prompt an MCP client connected to the server:

```text
Use ChaosMonkey to test this Python target for null-handling crashes.
Only inject faults, run tests, execute commands, and read logs/reports.
Do not modify files or propose repository changes.
```

A typical agent flow:

1. Inspect the target command or Python entrypoint.
2. Build a representative JSON payload.
3. Call `inject_null_fault_tool` or `run_chaos_test` with deterministic seeds.
4. Use `run_command` to run the relevant test command.
5. Use `read_file` to inspect generated logs or reports.
6. Report crashes, resilience issues, tracebacks, and reproducible inputs.

ChaosMonkey MCP stops at discovery.

## Architecture

```text
chaosmonkey/
├── mcp/
│   ├── server.py      # FastMCP stdio server and tool implementations
│   ├── schemas.py     # Typed tool metadata and response schemas
│   └── __main__.py    # module entrypoint
├── tools/
│   └── fault_injection.py
└── core/
    ├── executor.py    # fault execution and crash capture
    ├── observer.py    # observation utilities
    └── models.py      # crash/fault models
```

Runtime model:

```text
AI client -> local MCP stdio server -> ChaosMonkey tools -> target project
```

The server is local-first and provider-agnostic. It does not call an LLM provider itself.

## Roadmap

- additional fault injectors beyond null mutation
- stronger command sandboxing
- richer crash report formats
- broader target execution adapters
- more MCP client setup examples

## License

MIT
