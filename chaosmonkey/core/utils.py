"""
ChaosMonkey AI - Core Utilities

Shared utility functions for the core module.
"""

from pathlib import Path
from typing import Optional


def validate_python_file(file_path: str) -> bool:
    """
    Validate that a file is a Python file and exists.
    
    Args:
        file_path: Path to file to validate
        
    Returns:
        True if file is valid Python file
    """
    path = Path(file_path)
    return path.exists() and path.suffix == ".py"


def parse_error_line(error_line: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse error type and message from error line.
    
    Args:
        error_line: Last line of traceback containing error
        
    Returns:
        Tuple of (error_type, error_message)
    """
    if ':' in error_line:
        parts = error_line.split(':', 1)
        error_type = parts[0].strip()
        error_message = parts[1].strip() if len(parts) > 1 else ""
        return error_type, error_message
    return None, None


def format_confidence(confidence: str) -> str:
    """
    Format confidence level for display.
    
    Args:
        confidence: Confidence level ("high", "medium", "low")
        
    Returns:
        Formatted confidence string
    """
    emoji_map = {
        "high": "🟢",
        "medium": "🟡",
        "low": "🔴"
    }
    emoji = emoji_map.get(confidence.lower(), "⚪")
    return f"{emoji} {confidence.upper()}"

# Made with Bob
