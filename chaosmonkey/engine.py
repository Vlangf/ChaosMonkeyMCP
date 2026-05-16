"""
DEPRECATED: This module is deprecated and will be removed.

Use the new architecture instead:
- chaosmonkey.core.executor.FaultExecutor for execution
- chaosmonkey.core.observer.SystemObserver for observation
- chaosmonkey.core.models for data models

See ARCHITECTURE.md for details.
"""

# Legacy imports for backward compatibility
from chaosmonkey.core.executor import FaultExecutor
from chaosmonkey.core.observer import SystemObserver
from chaosmonkey.core.models import CrashReport

# Legacy function wrappers
def run_target(target_path: str) -> CrashReport:
    """DEPRECATED: Use FaultExecutor.run_target() instead."""
    executor = FaultExecutor()
    return executor.run_target(target_path)

def read_source_file(file_path: str):
    """DEPRECATED: Use SystemObserver.read_source_file() instead."""
    observer = SystemObserver()
    return observer.read_source_file(file_path)

def print_crash_report(report: CrashReport, target_path: str) -> None:
    """DEPRECATED: Moved to chaosmonkey.main._print_crash_report()"""
    pass

def print_analysis_report(analysis, target_path: str) -> None:
    """DEPRECATED: Analysis reporting moved to tools layer"""
    pass

# Made with Bob
