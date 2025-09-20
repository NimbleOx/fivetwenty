"""
Structured error handling for validation operations.

Provides consistent error reporting and categorization across validators.
"""

from enum import Enum
from pathlib import Path
from typing import Any


class ValidationErrorCode(Enum):
    """Enumeration of validation error codes for consistent categorization."""

    FILE_READ_ERROR = "FILE_READ"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    NETWORK_ERROR = "NETWORK"
    NETWORK_TIMEOUT = "NETWORK_TIMEOUT"
    PARSING_ERROR = "PARSING"
    CONFIGURATION_ERROR = "CONFIG"
    SYNTAX_ERROR = "SYNTAX"
    SECURITY_ISSUE = "SECURITY"
    LINK_BROKEN = "LINK_BROKEN"
    TERMINOLOGY_INCONSISTENCY = "TERMINOLOGY"


class ValidationError(Exception):
    """
    Structured validation error with metadata.

    Provides consistent error information across all validators
    including error codes, file locations, and context.
    """

    def __init__(self, code: ValidationErrorCode, message: str, file_path: Path | None = None, line_number: int | None = None, context: dict[str, Any] | None = None):
        """
        Initialize validation error.

        Args:
            code: Error classification code
            message: Human-readable error description
            file_path: Path to file where error occurred
            line_number: Line number in file (if applicable)
            context: Additional error context
        """
        self.code = code
        self.file_path = file_path
        self.line_number = line_number
        self.context = context or {}

        super().__init__(message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for serialization."""
        return {"code": self.code.value, "message": str(self), "file": str(self.file_path) if self.file_path else None, "line": self.line_number, "context": self.context}

    def __str__(self) -> str:
        """Format error as human-readable string."""
        parts = [super().__str__()]

        if self.file_path:
            location = str(self.file_path)
            if self.line_number:
                location += f":{self.line_number}"
            parts.append(f"({location})")

        return " ".join(parts)


def create_file_error(message: str, file_path: Path, line_number: int | None = None, error_code: ValidationErrorCode = ValidationErrorCode.FILE_READ_ERROR) -> ValidationError:
    """
    Create a file-related validation error.

    Convenience function for creating common file errors.
    """
    return ValidationError(code=error_code, message=message, file_path=file_path, line_number=line_number)


def create_network_error(message: str, url: str, status_code: int | None = None, timeout: bool = False) -> ValidationError:
    """
    Create a network-related validation error.

    Convenience function for creating common network errors.
    """
    code = ValidationErrorCode.NETWORK_TIMEOUT if timeout else ValidationErrorCode.NETWORK_ERROR
    context: dict[str, Any] = {"url": url}
    if status_code is not None:
        context["status_code"] = status_code

    return ValidationError(code=code, message=message, context=context)
