"""
AI-powered crash analysis for ChaosMonkey AI.

This module provides a provider-agnostic interface for analyzing crashes
and generating remediation recommendations. Designed to support multiple
AI providers (IBM Bob, Claude, OpenAI, etc.) through a plugin architecture.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from chaosmonkey.core.models import CrashReport


@dataclass
class AnalysisResult:
    """Structured analysis result from AI analyzer."""
    
    root_cause: str
    suspected_bug: str
    minimal_fix: str
    regression_test: str
    confidence: str  # "high", "medium", "low"
    provider: str  # e.g., "mock", "ibm-bob", "claude"


class BaseAnalyzer(ABC):
    """
    Abstract base class for crash analyzers.
    
    All analyzer implementations must inherit from this class and implement
    the analyze() method. This ensures a consistent interface regardless of
    the underlying AI provider.
    """
    
    @abstractmethod
    def analyze(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str] = None
    ) -> AnalysisResult:
        """
        Analyze a crash and generate remediation recommendations.
        
        Args:
            crash_report: Structured crash report from engine
            target_path: Path to the crashed file
            source_code: Optional source code of the crashed file
            
        Returns:
            AnalysisResult with AI-generated recommendations
        """
        pass


class MockAnalyzer(BaseAnalyzer):
    """
    Mock analyzer for testing and development.
    
    Generates realistic-looking analysis without calling external APIs.
    Useful for:
    - Development and testing
    - Demos and presentations
    - Fallback when real providers are unavailable
    """
    
    def analyze(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str] = None
    ) -> AnalysisResult:
        """Generate mock analysis based on crash report patterns."""
        
        # Pattern-match common error types for realistic mock responses
        if crash_report.error_type == "AttributeError":
            return self._analyze_attribute_error(crash_report, target_path, source_code)
        elif crash_report.error_type == "KeyError":
            return self._analyze_key_error(crash_report, target_path, source_code)
        elif crash_report.error_type == "TypeError":
            # Check if it's a None subscript error (common pattern)
            if crash_report.error_message and "NoneType" in crash_report.error_message and "subscriptable" in crash_report.error_message:
                return self._analyze_none_subscript_error(crash_report, target_path, source_code)
            return self._analyze_type_error(crash_report, target_path, source_code)
        elif crash_report.error_type == "ZeroDivisionError":
            return self._analyze_zero_division(crash_report, target_path, source_code)
        else:
            return self._analyze_generic(crash_report, target_path, source_code)
    
    def _analyze_attribute_error(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze AttributeError crashes."""
        
        # Extract attribute name from error message if possible
        attr_name = "unknown"
        if crash_report.error_message and "'" in crash_report.error_message:
            parts = crash_report.error_message.split("'")
            if len(parts) >= 2:
                attr_name = parts[1]
        
        return AnalysisResult(
            root_cause=f"Attempted to access attribute '{attr_name}' on a None object or object without that attribute.",
            suspected_bug=f"The code assumes an object exists and has the '{attr_name}' attribute, but received None or an incompatible type. This is a classic null-safety violation.",
            minimal_fix=f"""Add defensive null check before accessing '{attr_name}':

```python
if obj is not None and hasattr(obj, '{attr_name}'):
    result = obj.{attr_name}
else:
    # Handle None case appropriately
    result = default_value  # or raise meaningful error
```

Or use optional chaining pattern:
```python
result = getattr(obj, '{attr_name}', default_value) if obj else default_value
```""",
            regression_test=f"""```python
def test_handles_none_object():
    \"\"\"Ensure function handles None gracefully.\"\"\"
    result = process_user({{"profile": None}})
    assert result is not None or result == expected_default
    
def test_handles_missing_attribute():
    \"\"\"Ensure function handles missing attributes.\"\"\"
    result = process_user({{"profile": {{}}}})
    assert result is not None
```""",
            confidence="high",
            provider="mock"
        )
    
    def _analyze_none_subscript_error(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze NoneType subscript errors (e.g., None['key'])."""
        
        return AnalysisResult(
            root_cause="Attempted to access a dictionary key or index on a None object. The code assumes an object exists but received None instead.",
            suspected_bug="Missing null check before dictionary/list access. The data structure is None when the code expects a valid dict or list. This is a classic null-safety violation.",
            minimal_fix="""Add defensive null check before accessing:

```python
# Option 1: Check for None explicitly
if obj is not None:
    result = obj["key"]
else:
    # Handle None case
    result = default_value

# Option 2: Use get() with default for dicts
result = obj.get("key", default_value) if obj else default_value

# Option 3: Early return pattern
if obj is None:
    return default_value
result = obj["key"]
```

For the specific case in [`target_app.py`](target_app.py:3):
```python
def process_user(user):
    # Add null check for profile
    if user.get("profile") is None:
        return "unknown"  # or raise meaningful error
    
    return user["profile"]["name"].lower()
```""",
            regression_test="""```python
def test_handles_none_profile():
    \"\"\"Ensure function handles None profile gracefully.\"\"\"
    user = {"profile": None}
    result = process_user(user)
    assert result == "unknown"  # or whatever default is appropriate
    
def test_handles_missing_profile():
    \"\"\"Ensure function handles missing profile key.\"\"\"
    user = {}
    result = process_user(user)
    assert result == "unknown"

def test_handles_valid_profile():
    \"\"\"Ensure function works with valid data.\"\"\"
    user = {"profile": {"name": "Alice"}}
    result = process_user(user)
    assert result == "alice"
```""",
            confidence="high",
            provider="mock"
        )
    
    def _analyze_key_error(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze KeyError crashes."""
        
        return AnalysisResult(
            root_cause="Attempted to access a dictionary key that doesn't exist.",
            suspected_bug="The code assumes a specific key exists in the dictionary without validation. This breaks when the data structure doesn't match expectations.",
            minimal_fix="""Use .get() with default value or validate keys first:

```python
# Option 1: Use .get() with default
value = data.get('key', default_value)

# Option 2: Check key existence
if 'key' in data:
    value = data['key']
else:
    # Handle missing key
    value = default_value
```""",
            regression_test="""```python
def test_handles_missing_key():
    \"\"\"Ensure function handles missing dictionary keys.\"\"\"
    incomplete_data = {"other_key": "value"}
    result = process_data(incomplete_data)
    assert result is not None
```""",
            confidence="high",
            provider="mock"
        )
    
    def _analyze_type_error(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze TypeError crashes."""
        
        return AnalysisResult(
            root_cause="Operation performed on incompatible type or wrong number of arguments passed to function.",
            suspected_bug="Type mismatch between expected and actual data types. The code doesn't validate input types before operations.",
            minimal_fix="""Add type validation and conversion:

```python
# Validate type before operation
if not isinstance(value, expected_type):
    raise ValueError(f"Expected {expected_type}, got {type(value)}")

# Or convert safely
try:
    converted = expected_type(value)
except (ValueError, TypeError):
    # Handle conversion failure
    converted = default_value
```""",
            regression_test="""```python
def test_handles_wrong_type():
    \"\"\"Ensure function validates input types.\"\"\"
    with pytest.raises(ValueError):
        process_data(wrong_type_input)
        
def test_type_conversion():
    \"\"\"Ensure function converts types safely.\"\"\"
    result = process_data("123")
    assert isinstance(result, int)
```""",
            confidence="medium",
            provider="mock"
        )
    
    def _analyze_zero_division(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze ZeroDivisionError crashes."""
        
        return AnalysisResult(
            root_cause="Division by zero occurred in calculation.",
            suspected_bug="The code doesn't validate divisor before division operation. Edge case where divisor can be zero was not handled.",
            minimal_fix="""Add zero-check before division:

```python
if divisor != 0:
    result = numerator / divisor
else:
    # Handle zero divisor case
    result = 0  # or float('inf'), or raise meaningful error
```""",
            regression_test="""```python
def test_handles_zero_divisor():
    \"\"\"Ensure function handles division by zero.\"\"\"
    result = calculate(10, 0)
    assert result == 0 or result == float('inf')
```""",
            confidence="high",
            provider="mock"
        )
    
    def _analyze_generic(
        self,
        crash_report: CrashReport,
        target_path: str,
        source_code: Optional[str]
    ) -> AnalysisResult:
        """Analyze generic crashes."""
        
        error_type = crash_report.error_type or "Unknown"
        
        return AnalysisResult(
            root_cause=f"{error_type} occurred during execution. Specific cause requires deeper analysis of the traceback and source code.",
            suspected_bug="The error suggests an unhandled edge case or invalid assumption in the code logic.",
            minimal_fix="""Add comprehensive error handling:

```python
try:
    # Risky operation
    result = perform_operation()
except SpecificError as e:
    # Handle specific error
    logger.error(f"Operation failed: {e}")
    result = safe_default
```""",
            regression_test="""```python
def test_error_handling():
    \"\"\"Ensure function handles errors gracefully.\"\"\"
    result = function_under_test(edge_case_input)
    assert result is not None
```""",
            confidence="low",
            provider="mock"
        )


# TODO: Future analyzer implementations
# class IBMBobAnalyzer(BaseAnalyzer):
#     """IBM Bob MCP-powered analyzer."""
#     pass
#
# class ClaudeAnalyzer(BaseAnalyzer):
#     """Anthropic Claude API analyzer."""
#     pass
#
# class OpenAIAnalyzer(BaseAnalyzer):
#     """OpenAI API analyzer."""
#     pass

# Made with Bob
