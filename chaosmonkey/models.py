"""
DEPRECATED: This module is deprecated and will be removed.

Data models have been moved to:
- chaosmonkey.core.models for core data models
- chaosmonkey.mcp.schemas for MCP tool schemas

See ARCHITECTURE.md for details.
"""

# Legacy imports for backward compatibility
from chaosmonkey.core.models import (
    FaultConfig,
    FaultType,
    CrashReport,
    ObservationResult,
    AnalysisResult,
    TestResult,
    FixProposal,
)

__all__ = [
    "FaultConfig",
    "FaultType",
    "CrashReport",
    "ObservationResult",
    "AnalysisResult",
    "TestResult",
    "FixProposal",
]

# Made with Bob
