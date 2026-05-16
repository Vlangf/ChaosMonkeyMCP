"""
ChaosMonkey MCP Server CLI Entry Point

Run with: uv run python -m chaosmonkey.mcp.server
"""

from chaosmonkey.mcp.server import mcp

if __name__ == "__main__":
    mcp.run()

# Made with Bob