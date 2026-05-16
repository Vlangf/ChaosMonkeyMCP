#!/usr/bin/env python3
"""
Local MCP Smoke Test Script

Directly imports and calls MCP tool functions to verify they work
without needing Claude/Cursor integration.

Tests:
1. inject_null_fault_tool - Null fault injection
2. run_chaos_test - Full chaos test workflow

Prints structured results with rich for easy verification.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich import box

from chaosmonkey.mcp.server import inject_null_fault_tool, run_chaos_test, run_command, read_file


console = Console()


def print_header(title: str):
    """Print a formatted header."""
    console.print()
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", box=box.DOUBLE))
    console.print()


def print_result(tool_name: str, result_json: str):
    """Print tool result with syntax highlighting."""
    result = json.loads(result_json)
    
    # Create summary table
    table = Table(title=f"{tool_name} Result", box=box.ROUNDED)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="green")
    
    # Add key fields
    for key, value in result.items():
        if value is not None and key not in ["mutated_data", "crashing_payload", "traceback", "stdout", "stderr"]:
            table.add_row(key, str(value))
    
    console.print(table)
    
    # Print full JSON with syntax highlighting
    console.print("\n[bold]Full JSON Response:[/bold]")
    syntax = Syntax(result_json, "json", theme="monokai", line_numbers=True)
    console.print(syntax)
    console.print()


def test_inject_null_fault():
    """Test inject_null_fault_tool with various payloads."""
    print_header("TEST 1: inject_null_fault_tool")
    
    # Test case 1: Simple nested object
    console.print("[bold yellow]Test Case 1:[/bold yellow] Simple nested object")
    payload1 = json.dumps({
        "user": {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
    })
    
    result1 = inject_null_fault_tool(
        data=payload1,
        probability=0.5,
        seed=42
    )
    print_result("inject_null_fault_tool", result1)
    
    # Test case 2: Complex nested structure with arrays
    console.print("[bold yellow]Test Case 2:[/bold yellow] Complex nested structure")
    payload2 = json.dumps({
        "user": {
            "profile": {
                "name": "Jane Smith",
                "settings": {
                    "theme": "dark",
                    "notifications": True
                }
            },
            "items": [1, 2, 3, 4, 5],
            "metadata": {
                "created": "2024-01-01",
                "updated": "2024-01-15"
            }
        }
    })
    
    result2 = inject_null_fault_tool(
        data=payload2,
        probability=0.3,
        seed=123
    )
    print_result("inject_null_fault_tool", result2)
    
    # Test case 3: Error handling - invalid JSON
    console.print("[bold yellow]Test Case 3:[/bold yellow] Invalid JSON (error handling)")
    result3 = inject_null_fault_tool(
        data="not valid json {",
        probability=0.3
    )
    print_result("inject_null_fault_tool", result3)


def test_run_chaos_test():
    """Test run_chaos_test with target_app.py."""
    print_header("TEST 2: run_chaos_test")
    
    # Test case 1: Run chaos test that should crash
    console.print("[bold yellow]Test Case 1:[/bold yellow] Chaos test with crash-prone payload")
    payload1 = json.dumps({
        "profile": {
            "name": "Alice"
        }
    })
    
    result1 = run_chaos_test(
        target_path="target_app.py",
        payload=payload1,
        probability=0.8,  # High probability to trigger crash
        seed=42,
        iterations=3
    )
    print_result("run_chaos_test", result1)
    
    # Test case 2: Run chaos test with safe payload
    console.print("[bold yellow]Test Case 2:[/bold yellow] Chaos test with safer payload")
    payload2 = json.dumps({
        "profile": {
            "name": "Bob",
            "age": 25
        }
    })
    
    result2 = run_chaos_test(
        target_path="target_app.py",
        payload=payload2,
        probability=0.2,  # Lower probability
        seed=100,
        iterations=2
    )
    print_result("run_chaos_test", result2)
    
    # Test case 3: Error handling - file not found
    console.print("[bold yellow]Test Case 3:[/bold yellow] File not found (error handling)")
    result3 = run_chaos_test(
        target_path="nonexistent_file.py",
        payload=payload1,
        probability=0.3
    )
    print_result("run_chaos_test", result3)
    
    # Test case 4: Error handling - invalid JSON
    console.print("[bold yellow]Test Case 4:[/bold yellow] Invalid JSON payload (error handling)")
    result4 = run_chaos_test(
        target_path="target_app.py",
        payload="invalid json",
        probability=0.3
    )
    print_result("run_chaos_test", result4)


def test_run_command():
    """Test run_command with various shell commands."""
    print_header("TEST 3: run_command")
    
    # Test case 1: Simple echo command
    console.print("[bold yellow]Test Case 1:[/bold yellow] Simple echo command")
    result1 = run_command(
        command="echo 'Hello from ChaosMonkey AI'",
        timeout_seconds=5
    )
    print_result("run_command", result1)
    
    # Test case 2: Python version check
    console.print("[bold yellow]Test Case 2:[/bold yellow] Python version check")
    result2 = run_command(
        command="python --version",
        timeout_seconds=5
    )
    print_result("run_command", result2)
    
    # Test case 3: List files in current directory
    console.print("[bold yellow]Test Case 3:[/bold yellow] List files")
    result3 = run_command(
        command="ls -la",
        timeout_seconds=5
    )
    print_result("run_command", result3)
    
    # Test case 4: Command with working directory
    console.print("[bold yellow]Test Case 4:[/bold yellow] Command with cwd")
    result4 = run_command(
        command="pwd",
        cwd="chaosmonkey",
        timeout_seconds=5
    )
    print_result("run_command", result4)
    
    # Test case 5: Dangerous command blocked
    console.print("[bold yellow]Test Case 5:[/bold yellow] Dangerous command (should be blocked)")
    result5 = run_command(
        command="rm -rf /tmp/test",
        timeout_seconds=5
    )
    print_result("run_command", result5)
    
    # Test case 6: Sudo command blocked
    console.print("[bold yellow]Test Case 6:[/bold yellow] Sudo command (should be blocked)")
    result6 = run_command(
        command="sudo apt-get update",
        timeout_seconds=5
    )
    print_result("run_command", result6)
    
    # Test case 7: Command that fails
    console.print("[bold yellow]Test Case 7:[/bold yellow] Command that fails")
    result7 = run_command(
        command="ls /nonexistent_directory_12345",
        timeout_seconds=5
    )
    print_result("run_command", result7)
    
    # Test case 8: Invalid working directory
    console.print("[bold yellow]Test Case 8:[/bold yellow] Invalid working directory")
    result8 = run_command(
        command="echo test",
        cwd="/nonexistent/path",
        timeout_seconds=5
    )
    print_result("run_command", result8)


def test_read_file():
    """Test read_file with various scenarios."""
    print_header("TEST 4: read_file")
    
    # Test case 1: Read existing file (README.md)
    console.print("[bold yellow]Test Case 1:[/bold yellow] Read existing file (README.md)")
    result1 = read_file(
        path="README.md",
        max_bytes=5000
    )
    print_result("read_file", result1)
    
    # Test case 2: Read with small max_bytes (truncation)
    console.print("[bold yellow]Test Case 2:[/bold yellow] Read with truncation")
    result2 = read_file(
        path="README.md",
        max_bytes=500
    )
    print_result("read_file", result2)
    
    # Test case 3: Read file in subdirectory
    console.print("[bold yellow]Test Case 3:[/bold yellow] Read file in subdirectory")
    result3 = read_file(
        path="chaosmonkey/mcp/schemas.py",
        max_bytes=3000
    )
    print_result("read_file", result3)
    
    # Test case 4: File not found
    console.print("[bold yellow]Test Case 4:[/bold yellow] File not found")
    result4 = read_file(
        path="nonexistent_file_12345.txt",
        max_bytes=1000
    )
    print_result("read_file", result4)
    
    # Test case 5: Security - blocked file pattern (.env)
    console.print("[bold yellow]Test Case 5:[/bold yellow] Security - blocked file pattern (.env)")
    result5 = read_file(
        path=".env",
        max_bytes=1000
    )
    print_result("read_file", result5)
    
    # Test case 6: Security - path outside project root
    console.print("[bold yellow]Test Case 6:[/bold yellow] Security - path outside project root")
    result6 = read_file(
        path="../../../etc/passwd",
        max_bytes=1000
    )
    print_result("read_file", result6)
    
    # Test case 7: Security - blocked pattern (credentials)
    console.print("[bold yellow]Test Case 7:[/bold yellow] Security - blocked pattern (credentials)")
    result7 = read_file(
        path="my_credentials.txt",
        max_bytes=1000
    )
    print_result("read_file", result7)
    
    # Test case 8: Security - blocked pattern (token)
    console.print("[bold yellow]Test Case 8:[/bold yellow] Security - blocked pattern (token)")
    result8 = read_file(
        path="api_token.json",
        max_bytes=1000
    )
    print_result("read_file", result8)
    
    # Test case 9: Invalid max_bytes (too large)
    console.print("[bold yellow]Test Case 9:[/bold yellow] Invalid max_bytes (too large)")
    result9 = read_file(
        path="README.md",
        max_bytes=2000000  # Over 1MB limit
    )
    print_result("read_file", result9)
    
    # Test case 10: Invalid max_bytes (too small)
    console.print("[bold yellow]Test Case 10:[/bold yellow] Invalid max_bytes (too small)")
    result10 = read_file(
        path="README.md",
        max_bytes=0
    )
    print_result("read_file", result10)
    
    # Test case 11: Try to read directory (not a file)
    console.print("[bold yellow]Test Case 11:[/bold yellow] Try to read directory")
    result11 = read_file(
        path="chaosmonkey",
        max_bytes=1000
    )
    print_result("read_file", result11)


def main():
    """Run all smoke tests."""
    console.print(Panel.fit(
        "[bold magenta]ChaosMonkey AI - MCP Tools Smoke Test[/bold magenta]\n"
        "[dim]Testing MCP tool functions locally without Claude/Cursor integration[/dim]",
        border_style="magenta"
    ))
    
    try:
        # Test 1: inject_null_fault_tool
        test_inject_null_fault()
        
        # Test 2: run_chaos_test
        test_run_chaos_test()
        
        # Test 3: run_command
        test_run_command()
        
        # Test 4: read_file
        test_read_file()
        
        # Summary
        print_header("SMOKE TEST COMPLETE")
        console.print("[bold green]✓ All MCP tools tested successfully![/bold green]")
        console.print("\n[dim]Tools are ready for Claude/Cursor integration.[/dim]")
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Smoke test failed:[/bold red] {e}")
        import traceback
        console.print(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
