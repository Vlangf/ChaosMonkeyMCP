# MCP Client Setup Guide

This guide shows how to connect various MCP clients to the ChaosMonkey MCP server for AI-powered chaos engineering and resilience testing.

## Overview

The ChaosMonkey MCP server is a **local stdio-based server** that runs entirely on your machine. No cloud services, backends, or external dependencies are required.

**Command to run:**
```bash
uv run python -m chaosmonkey.mcp.server
```

## Available Tools

The server exposes two primary tools:

1. **`inject_null_fault`** - Inject null/None values into function parameters to test error handling
2. **`run_chaos_test`** - Execute comprehensive chaos engineering tests with fault injection

## Example Prompt

Once configured, you can use prompts like:

> "Use ChaosMonkey to stress-test this project and find resilience issues."

The AI will automatically use the MCP tools to inject faults, observe failures, and generate remediation recommendations.

---

## Configuration Examples

### 1. Claude Desktop

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "chaosmonkey": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "chaosmonkey.mcp.server"
      ],
      "cwd": "/absolute/path/to/chaosmonkey-ai"
    }
  }
}
```

**Steps:**
1. Replace `/absolute/path/to/chaosmonkey-ai` with your actual project path
2. Save the file
3. Restart Claude Desktop
4. Verify the server appears in the MCP section (🔌 icon)

---

### 2. Cursor IDE

**Location:** Cursor Settings → MCP Servers

**Option A: Via Settings UI**
1. Open Cursor Settings (Cmd+, on macOS)
2. Search for "MCP"
3. Add new server with:
   - **Name:** `chaosmonkey`
   - **Command:** `uv`
   - **Args:** `run python -m chaosmonkey.mcp.server`
   - **Working Directory:** `/absolute/path/to/chaosmonkey-ai`

**Option B: Via Config File**

Edit `~/.cursor/mcp_config.json`:

```json
{
  "mcpServers": {
    "chaosmonkey": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "chaosmonkey.mcp.server"
      ],
      "cwd": "/absolute/path/to/chaosmonkey-ai"
    }
  }
}
```

**Steps:**
1. Replace `/absolute/path/to/chaosmonkey-ai` with your actual project path
2. Save and restart Cursor
3. Check the MCP panel to verify connection

---

### 3. Generic MCP Client (Python)

For custom integrations or testing:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "python", "-m", "chaosmonkey.mcp.server"],
        cwd="/absolute/path/to/chaosmonkey-ai"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print("Available tools:", [t.name for t in tools.tools])
            
            # Call inject_null_fault
            result = await session.call_tool(
                "inject_null_fault",
                arguments={
                    "target_file": "target_app.py",
                    "function_name": "process_data",
                    "param_name": "data"
                }
            )
            print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
```

---

### 4. Zed Editor

**Location:** `~/.config/zed/settings.json`

```json
{
  "mcp": {
    "servers": {
      "chaosmonkey": {
        "command": "uv",
        "args": [
          "run",
          "python",
          "-m",
          "chaosmonkey.mcp.server"
        ],
        "cwd": "/absolute/path/to/chaosmonkey-ai"
      }
    }
  }
}
```

---

### 5. IBM Bob (Local MCP Server)

IBM Bob can connect to the ChaosMonkey MCP server as a local tool for AI-powered chaos engineering analysis.

**Location:** `~/.config/bob/config.json` (Linux/macOS) or `%APPDATA%\bob\config.json` (Windows)

```json
{
  "mcp": {
    "servers": {
      "chaosmonkey": {
        "command": "uv",
        "args": [
          "run",
          "python",
          "-m",
          "chaosmonkey.mcp.server"
        ],
        "cwd": "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai"
      }
    }
  }
}
```

**Alternative: Using Bob Shell with ChaosMonkey Reports**

If you prefer to use Bob's shell mode directly with generated reports:

```bash
# After running chaos tests
uv run python -m chaosmonkey.main chaos

# Use Bob to analyze the generated report
bob shell --prompt "$(cat CHAOS_REPORT.md)"
```

**Programmatic Integration:**

```python
import subprocess
from pathlib import Path

def analyze_with_bob(report_path: Path) -> str:
    """Invoke Bob CLI to analyze chaos report."""
    result = subprocess.run(
        ["bob", "shell", "--prompt", report_path.read_text()],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout

# Usage
report = Path("CHAOS_REPORT.md")
remediation = analyze_with_bob(report)
print(remediation)
```

**Automatic Bob Integration:**

ChaosMonkey automatically invokes Bob after crash detection if available:

```python
# In chaosmonkey/core/bob_integration.py
from chaosmonkey.core.bob_integration import invoke_bob_with_fallback

# Automatically called after chaos execution
success = invoke_bob_with_fallback(
    report_path=Path("CHAOS_REPORT.md"),
    output_path=Path("CHAOS_REMEDIATION.md"),
    timeout=120
)
```

**Bob Configuration Options:**

```json
{
  "mcp": {
    "servers": {
      "chaosmonkey": {
        "command": "uv",
        "args": ["run", "python", "-m", "chaosmonkey.mcp.server"],
        "cwd": "/absolute/path/to/chaosmonkey-ai",
        "env": {
          "CHAOS_PROBABILITY": "0.3",
          "CHAOS_SEED": "42"
        }
      }
    }
  },
  "bob": {
    "model": "watsonx/granite-3.1-8b-instruct",
    "temperature": 0.7,
    "max_tokens": 4096
  }
}
```

**Steps:**
1. Replace `/absolute/path/to/chaosmonkey-ai` with your actual project path
2. Ensure Bob CLI is installed: `bob --version`
3. Save the configuration file
4. Restart Bob or reload configuration
5. Verify with: `bob mcp list`

**Example Bob Prompts:**

```bash
# Analyze specific crash
bob shell --prompt "Analyze this crash and suggest fixes: $(cat CHAOS_REPORT.md)"

# Generate remediation plan
bob shell --prompt "Create a remediation plan for: $(cat CHAOS_REPORT.md)"

# Verify proposed fix
bob shell --prompt "Review this fix for safety: $(cat proposed_fix.py)"
```

---

## Verification

After configuration, verify the server is working:

1. **Check server startup:**
   ```bash
   uv run python -m chaosmonkey.mcp.server
   ```
   Should output: `ChaosMonkey MCP Server running on stdio`

2. **Test with MCP Inspector:**
   ```bash
   npx @modelcontextprotocol/inspector uv run python -m chaosmonkey.mcp.server
   ```

3. **In your AI client:**
   - Look for the ChaosMonkey server in the MCP panel
   - Try the example prompt above
   - Verify tools are available: `inject_null_fault`, `run_chaos_test`

---

## Troubleshooting

### Server not appearing in client

- **Check path:** Ensure `cwd` points to the correct project directory
- **Check uv:** Verify `uv` is installed: `uv --version`
- **Check Python:** Ensure Python 3.11+ is available
- **Restart client:** Fully quit and restart your AI client

### "Command not found: uv"

Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Permission errors

Ensure the project directory is readable:
```bash
chmod -R u+r /path/to/chaosmonkey-ai
```

### Server crashes on startup

Check dependencies:
```bash
cd /path/to/chaosmonkey-ai
uv sync
```

---

## Usage Examples

### Basic Fault Injection

> "Inject a null fault into the `process_data` function in `target_app.py` and observe what happens."

### Comprehensive Testing

> "Run a full chaos test suite on this project. Focus on error handling and resilience."

### Targeted Analysis

> "Use ChaosMonkey to test the `calculate_total` function with null inputs and generate a remediation plan."

---

## Architecture Notes

- **Local-only:** All processing happens on your machine
- **Stdio protocol:** Uses standard input/output for communication
- **No network:** No external API calls or cloud dependencies
- **IBM Bob integration:** Automatically uses IBM Bob MCP for AI-powered analysis (if configured)
- **Safe execution:** Runs in isolated Python environments via `uv`

---

## Next Steps

1. Configure your preferred client using the examples above
2. Try the example prompt to verify functionality
3. Review [`MCP_TOOLS.md`](./MCP_TOOLS.md) for detailed tool documentation
4. Check [`CHAOS_REMEDIATION.md`](./CHAOS_REMEDIATION.md) for remediation workflows

---

## Support

For issues or questions:
- Check [`README.md`](./README.md) for project overview
- Review [`ARCHITECTURE.md`](./ARCHITECTURE.md) for technical details
- Test with MCP Inspector for debugging