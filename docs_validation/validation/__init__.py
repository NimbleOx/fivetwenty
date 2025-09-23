"""FiveTwenty Documentation Validation System.

A refactored, high-performance validation system with proper separation of concerns.
"""

from .core.context import ValidationContext
from .core.results import ValidationResult, ValidationSummary
from .validators.registry import ValidatorRegistry

__version__ = "2.0.0"
__all__ = ["ValidationContext", "ValidationResult", "ValidationSummary", "ValidatorRegistry"]
