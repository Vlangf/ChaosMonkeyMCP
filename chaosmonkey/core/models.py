"""
ChaosMonkey AI - Core Data Models

Data models for fault injection, observation, analysis, and testing.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any, List


class FaultType(str, Enum):
    """Types of faults that can be injected."""
    
    NULL_POINTER = "null_pointer"
    KEY_ERROR = "key_error"
    TYPE_ERROR = "type_error"
    ZERO_DIVISION = "zero_division"
    NETWORK_LATENCY = "network_latency"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    CORRUPT_DATA = "corrupt_data"
    TIMEOUT = "timeout"
    EXCEPTION = "exception"


@dataclass
class FaultConfig:
    """Configuration for fault injection."""
    
    fault_type: FaultType
    target_path: str
    target_function: Optional[str] = None
    target_line: Optional[int] = None
    probability: float = 1.0  # 0.0 to 1.0
    duration_ms: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


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
    timestamp: Optional[str] = None


@dataclass
class ObservationResult:
    """Result of system observation."""
    
    logs: List[str]
    traceback: Optional[str]
    metrics: Dict[str, Any]
    crash_report: Optional[CrashReport] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.metrics is None:
            self.metrics = {}


@dataclass
class AnalysisResult:
    """AI-generated analysis of a failure."""
    
    root_cause: str
    suspected_bug: str
    minimal_fix: str
    regression_test: str
    confidence: str  # "high", "medium", "low"
    provider: str  # e.g., "mock", "ibm-bob", "claude"
    blast_radius: Optional[str] = None
    affected_files: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.affected_files is None:
            self.affected_files = []


@dataclass
class TestResult:
    """Result of test execution."""
    
    passed: bool
    test_count: int
    failure_count: int
    error_count: int
    duration_ms: float
    output: str
    failed_tests: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.failed_tests is None:
            self.failed_tests = []


@dataclass
class FixProposal:
    """Proposed fix for a detected issue."""
    
    file_path: str
    original_code: str
    fixed_code: str
    explanation: str
    confidence: str
    test_case: Optional[str] = None

# Made with Bob
