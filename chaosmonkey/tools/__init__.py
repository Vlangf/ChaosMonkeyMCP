"""
ChaosMonkey AI - MCP Tools

MCP-exposed tools for AI agents to perform chaos engineering operations.
"""

from chaosmonkey.tools.fault_injection import (
    inject_null_fault,
    inject_fault,
    add_latency,
    corrupt_payload,
)
from chaosmonkey.tools.observation import (
    read_logs,
    inspect_traceback,
    get_metrics,
)
from chaosmonkey.tools.testing import (
    run_tests,
    verify_fix,
)
from chaosmonkey.tools.analysis import (
    analyze_failure,
    suggest_fix,
)

__all__ = [
    # Data mutation (chaos engine foundation)
    "inject_null_fault",
    # File-based fault injection (MCP)
    "inject_fault",
    "add_latency",
    "corrupt_payload",
    # Observation
    "read_logs",
    "inspect_traceback",
    "get_metrics",
    # Testing
    "run_tests",
    "verify_fix",
    # Analysis
    "analyze_failure",
    "suggest_fix",
]

# Made with Bob
