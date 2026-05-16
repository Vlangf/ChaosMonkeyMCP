"""
Bob Shell Integration for ChaosMonkey AI

Automatically invokes IBM Bob CLI after crash detection to generate
AI-powered remediation analysis.
"""

import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class BobIntegrationError(Exception):
    """Raised when Bob CLI integration fails."""
    pass


def check_bob_available() -> bool:
    """
    Check if Bob CLI is available in the system.
    
    Returns:
        bool: True if bob command is available, False otherwise
    """
    try:
        result = subprocess.run(
            ["bob", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def invoke_bob_analysis(
    report_path: Path,
    output_path: Path,
    timeout: int = 120
) -> Tuple[bool, Optional[str]]:
    """
    Invoke Bob CLI to analyze crash report and generate remediation.
    
    Args:
        report_path: Path to CHAOS_REPORT.md
        output_path: Path to save CHAOS_REMEDIATION.md
        timeout: Maximum time to wait for Bob response (seconds)
    
    Returns:
        Tuple of (success: bool, error_message: Optional[str])
    """
    if not report_path.exists():
        return False, f"Report file not found: {report_path}"
    
    # Read the crash report
    try:
        report_content = report_path.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Failed to read report: {e}"
    
    # Extract the Bob prompt section from the report
    prompt = _extract_bob_prompt(report_content)
    
    # Invoke Bob CLI with the prompt
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(
                "[cyan]Invoking IBM Bob for AI-powered analysis...",
                total=None
            )
            
            # Run bob command with the prompt
            result = subprocess.run(
                ["bob", "shell", "--prompt", prompt],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            progress.update(task, completed=True)
        
        if result.returncode != 0:
            error_msg = result.stderr or "Bob CLI returned non-zero exit code"
            return False, f"Bob CLI failed: {error_msg}"
        
        # Save Bob's response to CHAOS_REMEDIATION.md
        remediation_content = _format_remediation_report(
            bob_response=result.stdout,
            original_report=report_content
        )
        
        output_path.write_text(remediation_content, encoding='utf-8')
        
        return True, None
        
    except subprocess.TimeoutExpired:
        return False, f"Bob CLI timed out after {timeout} seconds"
    except FileNotFoundError:
        return False, "Bob CLI not found. Please install IBM Bob."
    except Exception as e:
        return False, f"Unexpected error invoking Bob: {e}"


def invoke_bob_with_fallback(
    report_path: Path,
    output_path: Path,
    timeout: int = 120
) -> bool:
    """
    Invoke Bob CLI with graceful fallback if unavailable.
    
    This function:
    1. Checks if Bob is available
    2. If available, invokes Bob and saves remediation
    3. If unavailable, creates a placeholder remediation file
    4. Always returns True to allow workflow to continue
    
    Args:
        report_path: Path to CHAOS_REPORT.md
        output_path: Path to save CHAOS_REMEDIATION.md
        timeout: Maximum time to wait for Bob response (seconds)
    
    Returns:
        bool: True if Bob was invoked successfully, False if fallback used
    """
    console.print()
    console.print("[bold cyan]🤖 IBM Bob Integration[/bold cyan]")
    
    # Check if Bob is available
    if not check_bob_available():
        console.print("[yellow]⚠ Bob CLI not available[/yellow]")
        console.print("[dim]Install Bob to get AI-powered remediation analysis[/dim]")
        
        # Create placeholder remediation file
        _create_placeholder_remediation(report_path, output_path)
        console.print(f"[dim]Created placeholder: {output_path}[/dim]")
        
        return False
    
    # Invoke Bob
    success, error = invoke_bob_analysis(report_path, output_path, timeout)
    
    if success:
        console.print(f"[green]✓ Bob analysis complete: {output_path}[/green]")
        return True
    else:
        console.print(f"[yellow]⚠ Bob invocation failed: {error}[/yellow]")
        
        # Create placeholder as fallback
        _create_placeholder_remediation(report_path, output_path)
        console.print(f"[dim]Created placeholder: {output_path}[/dim]")
        
        return False


def _extract_bob_prompt(report_content: str) -> str:
    """
    Extract the Bob prompt section from the crash report.
    
    Args:
        report_content: Full content of CHAOS_REPORT.md
    
    Returns:
        Extracted prompt for Bob
    """
    # Find the "Prompt for IBM Bob" section
    marker = "## 🤖 Prompt for IBM Bob"
    
    if marker in report_content:
        # Extract everything after the marker
        parts = report_content.split(marker, 1)
        if len(parts) > 1:
            prompt_section = parts[1].strip()
            
            # Remove the footer if present
            footer_marker = "*This report was generated by ChaosMonkey AI"
            if footer_marker in prompt_section:
                prompt_section = prompt_section.split(footer_marker)[0].strip()
            
            return prompt_section
    
    # Fallback: use entire report
    return report_content


def _format_remediation_report(bob_response: str, original_report: str) -> str:
    """
    Format Bob's response into a structured remediation report.
    
    Args:
        bob_response: Raw response from Bob CLI
        original_report: Original crash report content
    
    Returns:
        Formatted remediation report
    """
    from datetime import datetime
    
    report = f"""# ChaosMonkey Remediation Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Powered by:** IBM Bob AI

---

## 🤖 AI-Powered Analysis

{bob_response.strip()}

---

## 📋 Original Crash Report

<details>
<summary>Click to expand original crash report</summary>

{original_report}

</details>

---

*This remediation was automatically generated by ChaosMonkey AI using IBM Bob.*
"""
    
    return report


def _create_placeholder_remediation(report_path: Path, output_path: Path) -> None:
    """
    Create a placeholder remediation file when Bob is unavailable.
    
    Args:
        report_path: Path to original crash report
        output_path: Path to save placeholder remediation
    """
    from datetime import datetime
    
    try:
        report_content = report_path.read_text(encoding='utf-8')
    except Exception:
        report_content = "Could not read original report"
    
    placeholder = f"""# ChaosMonkey Remediation Report

**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Status:** IBM Bob CLI not available

---

## ⚠️ Manual Analysis Required

IBM Bob CLI was not available to generate automatic remediation analysis.

### To get AI-powered analysis:

1. **Install IBM Bob:**
   ```bash
   # Installation instructions for IBM Bob
   pip install ibm-bob  # (example)
   ```

2. **Run Bob manually:**
   ```bash
   bob shell --prompt "$(cat CHAOS_REPORT.md)"
   ```

3. **Or use the Bob prompt from the crash report:**
   See the "🤖 Prompt for IBM Bob" section in CHAOS_REPORT.md

---

## 📋 Original Crash Report

{report_content}

---

*This placeholder was generated by ChaosMonkey AI. Install IBM Bob for automatic remediation.*
"""
    
    output_path.write_text(placeholder, encoding='utf-8')


# Made with Bob