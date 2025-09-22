"""Validation results and reporting."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ValidationStatus(str, Enum):
    """Validation status enumeration."""

    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"
    ERROR = "error"


class IssueSeverity(str, Enum):
    """Issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    SUGGESTION = "suggestion"


@dataclass
class ValidationIssue:
    """Individual validation issue."""

    message: str
    file_path: str
    line: int | None = None
    column: int | None = None
    severity: IssueSeverity = IssueSeverity.ERROR
    rule: str | None = None
    suggestion: str | None = None
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "message": self.message,
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "severity": self.severity.value,
            "rule": self.rule,
            "suggestion": self.suggestion,
            "context": self.context,
        }


@dataclass
class ValidationResult:
    """Result of a single validation check."""

    check_name: str
    status: ValidationStatus
    issues: list[ValidationIssue] = field(default_factory=list)
    files_checked: int = 0
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime | None = None

    def __post_init__(self) -> None:
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    @property
    def issues_found(self) -> int:
        """Number of issues found."""
        return len(self.issues)

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.files_checked == 0:
            return 100.0
        issues_count = len([i for i in self.issues if i.severity in [IssueSeverity.ERROR, IssueSeverity.WARNING]])
        return max(0.0, ((self.files_checked - issues_count) / self.files_checked) * 100.0)

    @property
    def is_successful(self) -> bool:
        """Check if validation was successful."""
        return self.status in [ValidationStatus.PASSED, ValidationStatus.WARNING]

    def add_issue(
        self,
        message: str,
        file_path: str,
        line: int | None = None,
        severity: IssueSeverity = IssueSeverity.ERROR,
        **kwargs: Any,
    ) -> None:
        """Add an issue to the result."""
        issue = ValidationIssue(
            message=message,
            file_path=file_path,
            line=line,
            severity=severity,
            **kwargs,
        )
        self.issues.append(issue)

    def get_issues_by_severity(self) -> dict[IssueSeverity, list[ValidationIssue]]:
        """Group issues by severity."""
        by_severity: dict[IssueSeverity, list[ValidationIssue]] = {
            severity: [] for severity in IssueSeverity
        }
        for issue in self.issues:
            by_severity[issue.severity].append(issue)
        return by_severity

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "check_name": self.check_name,
            "status": self.status.value,
            "issues_found": self.issues_found,
            "files_checked": self.files_checked,
            "success_rate": self.success_rate,
            "duration_seconds": self.duration_seconds,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "issues": [issue.to_dict() for issue in self.issues],
            "metadata": self.metadata,
        }


@dataclass
class ValidationSummary:
    """Summary of multiple validation results."""

    results: list[ValidationResult] = field(default_factory=list)
    total_duration: float = 0.0
    timestamp: datetime | None = None

    def __post_init__(self) -> None:
        """Calculate summary statistics."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

        if not self.total_duration and self.results:
            self.total_duration = sum(r.duration_seconds for r in self.results)

    @property
    def total_issues(self) -> int:
        """Total number of issues across all results."""
        return sum(r.issues_found for r in self.results)

    @property
    def total_files_checked(self) -> int:
        """Total number of files checked."""
        return sum(r.files_checked for r in self.results)

    @property
    def passed_checks(self) -> int:
        """Number of checks that passed."""
        return len([r for r in self.results if r.status == ValidationStatus.PASSED])

    @property
    def failed_checks(self) -> int:
        """Number of checks that failed."""
        return len([r for r in self.results if r.status == ValidationStatus.FAILED])

    @property
    def overall_success_rate(self) -> float:
        """Overall success rate across all validations."""
        if not self.results:
            return 100.0

        total_successful_files = sum(
            int(r.files_checked * (r.success_rate / 100.0))
            for r in self.results
        )

        if self.total_files_checked == 0:
            return 100.0

        return (total_successful_files / self.total_files_checked) * 100.0

    @property
    def is_successful(self) -> bool:
        """Check if overall validation was successful."""
        return all(r.is_successful for r in self.results)

    def get_issues_by_severity(self) -> dict[IssueSeverity, list[ValidationIssue]]:
        """Get all issues grouped by severity."""
        by_severity: dict[IssueSeverity, list[ValidationIssue]] = {
            severity: [] for severity in IssueSeverity
        }

        for result in self.results:
            for issue in result.issues:
                by_severity[issue.severity].append(issue)

        return by_severity

    def get_results_by_status(self) -> dict[ValidationStatus, list[ValidationResult]]:
        """Group results by status."""
        by_status: dict[ValidationStatus, list[ValidationResult]] = {
            status: [] for status in ValidationStatus
        }

        for result in self.results:
            by_status[result.status].append(result)

        return by_status

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "total_checks": len(self.results),
            "passed_checks": self.passed_checks,
            "failed_checks": self.failed_checks,
            "total_issues": self.total_issues,
            "total_files_checked": self.total_files_checked,
            "overall_success_rate": self.overall_success_rate,
            "total_duration": self.total_duration,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "results": [result.to_dict() for result in self.results],
        }
