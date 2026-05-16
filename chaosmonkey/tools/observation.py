"""
ChaosMonkey AI - Observation Tools

MCP tools for observing system state and collecting diagnostic information.
"""

from typing import Dict, Any, List, Optional

from chaosmonkey.core.observer import SystemObserver
from chaosmonkey.core.models import CrashReport


def read_logs(
    target: str,
    lines: int = 50,
    filter_pattern: Optional[str] = None
) -> Dict[str, Any]:
    """
    Read application logs from target.
    
    AI agents use this to inspect application output and error logs.
    
    Args:
        target: Path to target application or log file
        lines: Number of lines to read (default: 50)
        filter_pattern: Optional regex pattern to filter logs
        
    Returns:
        Dictionary with log data:
        {
            "success": bool,
            "logs": List[str],
            "line_count": int,
            "filtered": bool
        }
        
    Example:
        >>> read_logs(target="app.py", lines=100, filter_pattern="ERROR")
        {
            "success": True,
            "logs": ["ERROR: Connection failed", ...],
            "line_count": 15,
            "filtered": True
        }
    """
    observer = SystemObserver()
    
    try:
        logs = observer.read_logs(target, lines, filter_pattern)
        return {
            "success": True,
            "logs": logs,
            "line_count": len(logs),
            "filtered": filter_pattern is not None
        }
    except Exception as e:
        return {
            "success": False,
            "logs": [],
            "line_count": 0,
            "filtered": False,
            "error": str(e)
        }


def inspect_traceback(
    crash_report: Optional[Dict[str, Any]] = None,
    traceback_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Inspect and parse traceback information.
    
    AI agents use this to analyze stack traces and error details.
    
    Args:
        crash_report: Optional crash report dictionary
        traceback_text: Optional raw traceback text
        
    Returns:
        Dictionary with parsed traceback:
        {
            "success": bool,
            "traceback": str,
            "error_type": str,
            "error_message": str,
            "file_path": str,
            "line_number": int,
            "function_name": str
        }
        
    Example:
        >>> inspect_traceback(traceback_text="Traceback (most recent call last)...")
        {
            "success": True,
            "traceback": "...",
            "error_type": "AttributeError",
            "error_message": "'NoneType' object has no attribute 'name'",
            ...
        }
    """
    observer = SystemObserver()
    
    # Convert dict to CrashReport if provided
    if crash_report:
        report = CrashReport(**crash_report)
        traceback = observer.inspect_traceback(report)
    else:
        traceback = traceback_text
    
    if not traceback:
        return {
            "success": False,
            "error": "No traceback provided"
        }
    
    # TODO: Parse traceback for structured information
    # For now, return raw traceback
    return {
        "success": True,
        "traceback": traceback,
        "error_type": None,  # TODO: Parse from traceback
        "error_message": None,  # TODO: Parse from traceback
        "file_path": None,  # TODO: Parse from traceback
        "line_number": None,  # TODO: Parse from traceback
        "function_name": None  # TODO: Parse from traceback
    }


def get_metrics(
    target: str,
    metric_type: str = "all"
) -> Dict[str, Any]:
    """
    Gather system metrics for target application.
    
    AI agents use this to understand resource usage and performance.
    
    Args:
        target: Path to target application
        metric_type: Type of metrics ("cpu", "memory", "network", "disk", "all")
        
    Returns:
        Dictionary with metrics:
        {
            "success": bool,
            "metrics": {
                "cpu_percent": float,
                "memory_mb": float,
                "network_io": dict,
                "disk_io": dict
            },
            "timestamp": str
        }
        
    Example:
        >>> get_metrics(target="app.py", metric_type="memory")
        {
            "success": True,
            "metrics": {"memory_mb": 125.5},
            "timestamp": "2026-05-16T18:34:00Z"
        }
    """
    observer = SystemObserver()
    
    try:
        metrics = observer.get_metrics(target, metric_type)
        return {
            "success": True,
            "metrics": metrics,
            "timestamp": None  # TODO: Add timestamp
        }
    except Exception as e:
        return {
            "success": False,
            "metrics": {},
            "error": str(e)
        }

# Made with Bob
