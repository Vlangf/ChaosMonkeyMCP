"""
ChaosMonkey AI - Fault Injection Tools

MCP tools for injecting faults into target applications.
Includes both file-based injection (MCP) and data mutation tools.
"""

import random
import copy
from typing import Dict, Any, Optional

from chaosmonkey.core.models import FaultConfig, FaultType


# ============================================================================
# DATA MUTATION TOOLS (Chaos Engine Foundation)
# ============================================================================

def inject_null_fault(
    data: Dict[str, Any],
    probability: float = 0.3,
    seed: int | None = None,
) -> Dict[str, Any]:
    """
    Inject null faults into nested data structures.
    
    This is the foundation chaos engine tool that mutates Python payloads
    by randomly replacing nested values with None to simulate missing data,
    null pointer scenarios, and incomplete API responses.
    
    Args:
        data: Input dictionary to mutate
        probability: Chance (0.0-1.0) of replacing any given value with None
        seed: Optional random seed for deterministic behavior
        
    Returns:
        Mutated copy of the input data with some values replaced by None
        
    Examples:
        >>> inject_null_fault({"user": {"name": "John"}}, seed=42)
        {"user": None}
        
        >>> inject_null_fault({"items": [1, 2, 3]}, probability=0.5, seed=42)
        {"items": [None, 2, None]}
    """
    if seed is not None:
        random.seed(seed)
    
    # Work on a deep copy to preserve original
    mutated = copy.deepcopy(data)
    
    def _inject_recursive(obj: Any, depth: int = 0) -> Any:
        """Recursively inject nulls into nested structures."""
        # Randomly decide to nullify at this level
        if depth > 0 and random.random() < probability:
            return None
        
        # Recurse into dictionaries
        if isinstance(obj, dict):
            return {
                key: _inject_recursive(value, depth + 1)
                for key, value in obj.items()
            }
        
        # Recurse into lists
        elif isinstance(obj, list):
            return [
                _inject_recursive(item, depth + 1)
                for item in obj
            ]
        
        # Return primitives unchanged (unless already nullified above)
        else:
            return obj
    
    return _inject_recursive(mutated)


# ============================================================================
# FILE-BASED INJECTION TOOLS (MCP Integration - Future)
# ============================================================================


def inject_fault(
    target: str,
    fault_type: str,
    target_function: Optional[str] = None,
    target_line: Optional[int] = None,
    probability: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Inject a specific fault into the target application.
    
    This is the primary MCP tool for fault injection. AI agents use this to
    introduce controlled failures into the system.
    
    Args:
        target: Path to target Python file
        fault_type: Type of fault to inject (null_pointer, key_error, etc.)
        target_function: Optional specific function to target
        target_line: Optional specific line number to target
        probability: Probability of fault occurring (0.0 to 1.0)
        metadata: Optional additional configuration
        
    Returns:
        Dictionary with injection result:
        {
            "success": bool,
            "message": str,
            "fault_id": str,
            "config": dict
        }
        
    Example:
        >>> inject_fault(
        ...     target="app.py",
        ...     fault_type="null_pointer",
        ...     target_function="process_user",
        ...     probability=1.0
        ... )
        {
            "success": True,
            "message": "Fault injected successfully",
            "fault_id": "fault_123",
            "config": {...}
        }
    """
    # TODO: Implement actual fault injection via MCP
    # For now, return a structured response
    
    try:
        fault_type_enum = FaultType(fault_type)
    except ValueError:
        return {
            "success": False,
            "message": f"Invalid fault type: {fault_type}",
            "fault_id": None,
            "config": None
        }
    
    config = FaultConfig(
        fault_type=fault_type_enum,
        target_path=target,
        target_function=target_function,
        target_line=target_line,
        probability=probability,
        metadata=metadata
    )
    
    # TODO: Actually inject the fault using FaultExecutor
    # executor = FaultExecutor()
    # success = executor.inject_fault(config)
    
    return {
        "success": False,  # Will be True once implemented
        "message": "Fault injection not yet implemented - MCP integration pending",
        "fault_id": None,
        "config": {
            "fault_type": config.fault_type.value,
            "target_path": config.target_path,
            "target_function": config.target_function,
            "target_line": config.target_line,
            "probability": config.probability
        }
    }


def add_latency(
    target: str,
    duration_ms: int,
    probability: float = 1.0,
    target_function: Optional[str] = None
) -> Dict[str, Any]:
    """
    Add artificial latency to target application.
    
    Simulates slow network, disk I/O, or processing delays.
    
    Args:
        target: Path to target Python file
        duration_ms: Latency duration in milliseconds
        probability: Probability of latency occurring (0.0 to 1.0)
        target_function: Optional specific function to target
        
    Returns:
        Dictionary with injection result
        
    Example:
        >>> add_latency(
        ...     target="api.py",
        ...     duration_ms=500,
        ...     target_function="fetch_data"
        ... )
    """
    return inject_fault(
        target=target,
        fault_type="network_latency",
        target_function=target_function,
        probability=probability,
        metadata={"duration_ms": duration_ms}
    )


def corrupt_payload(
    target: str,
    corruption_type: str = "random",
    target_function: Optional[str] = None,
    probability: float = 1.0
) -> Dict[str, Any]:
    """
    Corrupt data payloads in target application.
    
    Simulates data corruption, malformed inputs, or encoding issues.
    
    Args:
        target: Path to target Python file
        corruption_type: Type of corruption ("random", "truncate", "encoding")
        target_function: Optional specific function to target
        probability: Probability of corruption occurring (0.0 to 1.0)
        
    Returns:
        Dictionary with injection result
        
    Example:
        >>> corrupt_payload(
        ...     target="parser.py",
        ...     corruption_type="truncate",
        ...     target_function="parse_json"
        ... )
    """
    return inject_fault(
        target=target,
        fault_type="corrupt_data",
        target_function=target_function,
        probability=probability,
        metadata={"corruption_type": corruption_type}
    )

# Made with Bob
