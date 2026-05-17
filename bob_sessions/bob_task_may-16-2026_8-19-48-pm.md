**User:**

<task>
We are building ChaosMonkey AI.

Goal:

Create a Python-based autonomous chaos engineering agent.

Current state:

- There is a target_app.py that crashes with:

  TypeError: 'NoneType' object is not subscriptable

We need the first engine step:

1. Run target_app.py

2. Capture stdout/stderr

3. Detect crashes

4. Print a structured crash report

Implement:

- chaosmonkey/engine.py

- update chaosmonkey/main.py

Requirements:

- use subprocess

- use rich for pretty output

- keep implementation minimal

- do not add AI yet

- do not install new dependencies

- keep it CLI-first
</task>
<environment_details>
# VSCode Visible Files
chaosmonkey/engine.py

# VSCode Open Tabs
chaosmonkey/main.py,target_app.py,chaosmonkey/engine.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:17:46.027Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>


# Current Workspace Directory (/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai) Files
.gitignore
.python-version
pyproject.toml
README.md
target_app.py
uv.lock
chaosmonkey/
chaosmonkey/engine.py
chaosmonkey/faults.py
chaosmonkey/main.py
chaosmonkey/models.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll analyze the current state and implement the chaos engineering engine step by step.

<read_file>
<args>
  <file>
    <path>target_app.py</path>
  </file>
  <file>
    <path>chaosmonkey/main.py</path>
  </file>
  <file>
    <path>chaosmonkey/engine.py</path>
  </file>
  <file>
    <path>pyproject.toml</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 4 files] Result:
<files>
<file><path>target_app.py</path>
<content lines="1-13">
 1 | def process_user(user):
 2 | 
 3 |     return user["profile"]["name"].lower()
 4 | 
 5 | if __name__ == "__main__":
 6 | 
 7 |     user = {
 8 | 
 9 |         "profile": None
10 | 
11 |     }
12 | 
13 |     print(process_user(user))
</content>
</file>
<file><path>chaosmonkey/main.py</path>
<content lines="1-13">
 1 | import typer
 2 | 
 3 | app = typer.Typer()
 4 | 
 5 | @app.command()
 6 | 
 7 | def test():
 8 | 
 9 |     print("ChaosMonkey AI alive")
10 | 
11 | if __name__ == "__main__":
12 | 
13 |     app()
</content>
</file>
<file><path>chaosmonkey/engine.py</path>
<content/><notice>File is empty</notice>
</file>
<file><path>pyproject.toml</path>
<content lines="1-11">
 1 | [project]
 2 | name = "chaosmonkey-ai"
 3 | version = "0.1.0"
 4 | description = "Add your description here"
 5 | readme = "README.md"
 6 | requires-python = ">=3.14"
 7 | dependencies = [
 8 |     "pydantic>=2.13.4",
 9 |     "rich>=15.0.0",
10 |     "typer>=0.25.1",
11 | ]
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
chaosmonkey/engine.py

# VSCode Open Tabs
chaosmonkey/main.py,target_app.py,chaosmonkey/engine.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:17:56.441Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.04

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[-] Implement chaosmonkey/engine.py with crash detection
[ ] Update chaosmonkey/main.py to use the engine
[ ] Test the implementation with target_app.py
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
chaosmonkey/engine.py

# VSCode Open Tabs
chaosmonkey/main.py,target_app.py,chaosmonkey/engine.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:18:00.571Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.07

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | In Progress |
| 2 | Update chaosmonkey/main.py to use the engine | Pending |
| 3 | Test the implementation with target_app.py | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<write_to_file>
<path>chaosmonkey/engine.py</path>
<content>import subprocess
import sys
from dataclasses import dataclass
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


@dataclass
class CrashReport:
    """Structured crash report from target application."""
    
    exit_code: int
    stdout: str
    stderr: str
    crashed: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    traceback: Optional[str] = None


def run_target(target_path: str) -> CrashReport:
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
            timeout=30
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


def print_crash_report(report: CrashReport, target_path: str) -> None:
    """
    Print a structured crash report using rich formatting.
    
    Args:
        report: CrashReport to display
        target_path: Path to the target that was executed
    """
    console.print()
    
    if report.crashed:
        # Crash header
        console.print(
            Panel(
                f"[bold red]🔥 CRASH DETECTED[/bold red]\n"
                f"Target: [cyan]{target_path}[/cyan]\n"
                f"Exit Code: [yellow]{report.exit_code}[/yellow]",
                border_style="red",
                title="ChaosMonkey AI",
            )
        )
        
        # Error details table
        if report.error_type:
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="bold cyan")
            table.add_column("Value")
            
            table.add_row("Error Type", f"[red]{report.error_type}[/red]")
            if report.error_message:
                table.add_row("Error Message", f"[yellow]{report.error_message}[/yellow]")
            
            console.print(table)
            console.print()
        
        # Traceback
        if report.traceback:
            console.print("[bold]Traceback:[/bold]")
            syntax = Syntax(
                report.traceback,
                "python",
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            )
            console.print(syntax)
            console.print()
        
        # Stdout if present
        if report.stdout.strip():
            console.print("[bold]Standard Output:[/bold]")
            console.print(Panel(report.stdout, border_style="dim"))
            console.print()
            
    else:
        # Success
        console.print(
            Panel(
                f"[bold green]✓ SUCCESS[/bold green]\n"
                f"Target: [cyan]{target_path}[/cyan]\n"
                f"Exit Code: [green]{report.exit_code}[/green]",
                border_style="green",
                title="ChaosMonkey AI",
            )
        )
        
        if report.stdout.strip():
            console.print("[bold]Output:[/bold]")
            console.print(Panel(report.stdout, border_style="dim"))
            console.print()
</content>
<line_count>165</line_count>
</write_to_file>

---

**User:**

[write_to_file for 'chaosmonkey/engine.py'] Result:
<file_write_result>
<path>chaosmonkey/engine.py</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<environment_details>
# VSCode Visible Files
chaosmonkey/engine.py

# VSCode Open Tabs
chaosmonkey/main.py,target_app.py,chaosmonkey/engine.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
chaosmonkey/engine.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:18:18.328Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.11

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | In Progress |
| 2 | Update chaosmonkey/main.py to use the engine | Pending |
| 3 | Test the implementation with target_app.py | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Implement chaosmonkey/engine.py with crash detection
[-] Update chaosmonkey/main.py to use the engine
[ ] Test the implementation with target_app.py
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
chaosmonkey/engine.py

# VSCode Open Tabs
chaosmonkey/main.py,target_app.py,chaosmonkey/engine.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:18:21.642Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.16

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | In Progress |
| 3 | Test the implementation with target_app.py | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<apply_diff>
<path>chaosmonkey/main.py</path>
<diff>
<<<<<<< SEARCH
:start_line:1
-------
import typer

app = typer.Typer()

@app.command()

def test():

    print("ChaosMonkey AI alive")

if __name__ == "__main__":

    app()
=======
import typer
from pathlib import Path

from chaosmonkey.engine import run_target, print_crash_report

app = typer.Typer()


@app.command()
def run(
    target: str = typer.Argument(
        ...,
        help="Path to the target Python script to test"
    )
):
    """
    Run a target application and detect crashes.
    
    ChaosMonkey AI will execute the target script, capture output,
    and provide a structured crash report if failures occur.
    """
    target_path = Path(target)
    
    if not target_path.exists():
        typer.echo(f"Error: Target file '{target}' not found", err=True)
        raise typer.Exit(1)
    
    if not target_path.suffix == ".py":
        typer.echo(f"Error: Target must be a Python file (.py)", err=True)
        raise typer.Exit(1)
    
    # Run target and capture crash
    report = run_target(str(target_path))
    
    # Print structured report
    print_crash_report(report, str(target_path))
    
    # Exit with appropriate code
    if report.crashed:
        raise typer.Exit(1)


@app.command()
def test():
    """Test that ChaosMonkey AI is working."""
    print("ChaosMonkey AI alive")


if __name__ == "__main__":
    app()
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'chaosmonkey/main.py'] Result:
<file_write_result>
<path>chaosmonkey/main.py</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:18:38.827Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.20

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | In Progress |
| 3 | Test the implementation with target_app.py | Pending |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Implement chaosmonkey/engine.py with crash detection
[x] Update chaosmonkey/main.py to use the engine
[-] Test the implementation with target_app.py
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:06.287Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.25

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<execute_command>
<command>python -m chaosmonkey.main run target_app.py</command>
</execute_command>

---

**User:**

[execute_command for 'python -m chaosmonkey.main run target_app.py'] Result:
Command executed in terminal  within working directory '/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai'. Command execution was not successful, inspect the cause and adjust as needed.
Exit code: 127
Output:
/bin/sh: python: command not found

<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:22.167Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.30

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<execute_command>
<command>python3 -m chaosmonkey.main run target_app.py</command>
</execute_command>

---

**User:**

[execute_command for 'python3 -m chaosmonkey.main run target_app.py'] Result:
Command executed in terminal  within working directory '/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai'. Command execution was not successful, inspect the cause and adjust as needed.
Exit code: 1
Output:
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai/chaosmonkey/main.py", line 1, in <module>
    import typer
ModuleNotFoundError: No module named 'typer'

<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:27.395Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.34

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<execute_command>
<command>uv sync</command>
</execute_command>

---

**User:**

[execute_command for 'uv sync'] Result:
Command executed in terminal  within working directory '/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai'. Exit code: 0
Output:
Resolved 15 packages in 4ms
Audited 13 packages in 3ms

<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:30.345Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.39

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<execute_command>
<command>uv run python -m chaosmonkey.main run target_app.py</command>
</execute_command>

---

**User:**

[execute_command for 'uv run python -m chaosmonkey.main run target_app.py'] Result:
Command executed in terminal  within working directory '/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai'. Command execution was not successful, inspect the cause and adjust as needed.
Exit code: 1
Output:

╭─────────────────────────────── ChaosMonkey AI ───────────────────────────────╮
│ 🔥 CRASH DETECTED                                                            │
│ Target: target_app.py                                                        │
│ Exit Code: 1                                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
  Error Type       TypeError                               
  Error Message    'NoneType' object is not subscriptable  

Traceback:
Traceback (most recent call last):                                              
  File "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai/target_app.py",  
line 13, in <module>                                                            
    print(process_user(user))                                                   
          ~~~~~~~~~~~~^^^^^^                                                    
  File "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai/target_app.py",  
line 3, in process_user                                                         
    return user["profile"]["name"].lower()                                      
           ~~~~~~~~~~~~~~~^^^^^^^^                                              
TypeError: 'NoneType' object is not subscriptable                               
                                                                                


<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:33.807Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.44

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | In Progress |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<update_todo_list>
<todos>
[x] Implement chaosmonkey/engine.py with crash detection
[x] Update chaosmonkey/main.py to use the engine
[x] Test the implementation with target_app.py
</todos>
</update_todo_list>

---

**User:**

[update_todo_list] Result:
Todo list updated successfully.
<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
target_app.py,chaosmonkey/engine.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T18:19:42.487Z
User time zone: Europe/Belgrade, UTC+2:00

# Current Cost
$0.50

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>reliability-engineer</slug>
<name>Reliability Engineer</name>
====

REMINDERS

Below is your current list of reminders for this task. Keep them updated as you progress.

| # | Content | Status |
|---|---------|--------|
| 1 | Implement chaosmonkey/engine.py with crash detection | Completed |
| 2 | Update chaosmonkey/main.py to use the engine | Completed |
| 3 | Test the implementation with target_app.py | Completed |


IMPORTANT: When task status changes, remember to call the `update_todo_list` tool to update your progress.

</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
ChaosMonkey AI engine implemented successfully.

**Implemented:**
- [`chaosmonkey/engine.py`](chaosmonkey/engine.py:1-165) - Core crash detection engine with:
  - [`run_target()`](chaosmonkey/engine.py:28-91) - Executes target app via subprocess, captures stdout/stderr
  - [`CrashReport`](chaosmonkey/engine.py:14-23) - Structured crash data model
  - [`print_crash_report()`](chaosmonkey/engine.py:94-165) - Rich-formatted crash output

- [`chaosmonkey/main.py`](chaosmonkey/main.py:1-56) - CLI with new [`run`](chaosmonkey/main.py:9-47) command

**Verified:**
The engine successfully detected the crash in [`target_app.py`](target_app.py:3):
- Error Type: `TypeError`
- Error Message: `'NoneType' object is not subscriptable`
- Full traceback captured and displayed with syntax highlighting

**Usage:**
```bash
uv run python -m chaosmonkey.main run target_app.py
```
</result>
</attempt_completion>

