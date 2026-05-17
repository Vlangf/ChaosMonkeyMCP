**User:**

<task>
uv run python -m chaosmonkey.main chaos

🔧 ChaosMonkey Chaos Execution

Running 20 chaos iterations...

Iteration 1/20... ✗ CRASH!

╭─────────────────────────────────────── ChaosMonkey Chaos Report ────────────────────────────────────────╮
│ 🔥 CRASH DISCOVERED!                                                                                    │
│ Target: target_app.process_user                                                                         │
│ Iteration: 1/20                                                                                         │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Error Type: AttributeError
Error Message: 'NoneType' object has no attribute 'lower'

Crashing Payload:
╭─────────────────────────────────────── Payload that caused crash ───────────────────────────────────────╮
│ {                                                                                                       │
│   "profile": {                                                                                          │
│     "name": null,                                                                                       │
│     "email": "john@example.com",                                                                        │
│     "age": null                                                                                         │
│   }                                                                                                     │
│ }                                                                                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────╯

Traceback:
Traceback (most recent call last):                                                                         
  File "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai/chaosmonkey/core/executor.py", line 152, in 
execute_with_fault                                                                                         
    last_result = target_function(mutated_payload)                                                         
  File "/Users/valentin/PycharmProjects/ibm_bob/chaosmonkey-ai/target_app.py", line 3, in process_user     
    return user["profile"]["name"].lower()                                                                 
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                                                                   
AttributeError: 'NoneType' object has no attribute 'lower'                                                 
                                                                                                           

💡 ChaosMonkey successfully discovered a crash!
This demonstrates how repeated fault injection can reveal hidden bugs.
</task>
<environment_details>
# VSCode Visible Files
chaosmonkey/main.py

# VSCode Open Tabs
chaosmonkey/core/observer.py,chaosmonkey/tools/fault_injection.py,README.md,chaosmonkey/core/executor.py,chaosmonkey/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T19:08:55.608Z
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
ARCHITECTURE.md
MIGRATION.md
pyproject.toml
README.md
target_app.py
test_inject_null.py
uv.lock
chaosmonkey/
chaosmonkey/analyzer.py
chaosmonkey/engine.py
chaosmonkey/faults.py
chaosmonkey/main.py
chaosmonkey/models.py
chaosmonkey/core/
chaosmonkey/core/__init__.py
chaosmonkey/core/executor.py
chaosmonkey/core/models.py
chaosmonkey/core/observer.py
chaosmonkey/core/utils.py
chaosmonkey/mcp/
chaosmonkey/mcp/__init__.py
chaosmonkey/mcp/schemas.py
chaosmonkey/mcp/server.py
chaosmonkey/tools/
chaosmonkey/tools/__init__.py
chaosmonkey/tools/analysis.py
chaosmonkey/tools/fault_injection.py
chaosmonkey/tools/observation.py
chaosmonkey/tools/testing.py
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

