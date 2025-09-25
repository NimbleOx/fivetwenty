"""Core data models for the validation framework."""

from __future__ import annotations

from enum import Enum
from pathlib import Path  # noqa: TC003
from typing import Any

from pydantic import BaseModel, Field


class IssueSeverity(str, Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


class ValidationIssue(BaseModel):
    """A single validation issue found in a file."""

    message: str
    file_path: Path
    line: int | None = None
    column: int | None = None
    severity: IssueSeverity = IssueSeverity.ERROR
    rule_id: str | None = None
    context: str | None = None
    suggestion: str | None = None


class ValidationResult(BaseModel):
    """Result of running a single validator."""

    validator_name: str
    file_path: Path
    passed: bool
    issues: list[ValidationIssue] = Field(default_factory=list)
    duration_ms: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for issue in self.issues if issue.severity == IssueSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for issue in self.issues if issue.severity == IssueSeverity.WARNING)


class ValidatorSummary(BaseModel):
    """Summary statistics for a single validator."""

    name: str
    files_checked: int
    files_passed: int
    files_failed: int
    total_issues: int
    error_count: int
    warning_count: int
    duration_ms: float
    success_rate: float
    enabled: bool = True  # Whether the validator was enabled for this run


class ValidationSummary(BaseModel):
    """Summary of validation run across all files and validators."""

    total_files: int
    total_validators: int
    passed_files: int
    failed_files: int
    total_issues: int
    error_count: int
    warning_count: int
    duration_ms: float
    results: list[ValidationResult] = Field(default_factory=list)
    validator_summaries: list[ValidatorSummary] = Field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Percentage of files that passed validation."""
        if self.total_files == 0:
            return 100.0
        return (self.passed_files / self.total_files) * 100.0

    @property
    def has_errors(self) -> bool:
        """True if any validation errors were found."""
        return self.error_count > 0


class FileInfo(BaseModel):
    """Information about a file to be validated."""

    path: Path
    size_bytes: int
    modified_time: float
    content_hash: str | None = None
