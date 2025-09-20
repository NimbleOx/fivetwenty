"""
Base validation classes and utilities.

Provides common functionality for all validation scripts.
"""

import json
import subprocess
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ValidationResult:
    """Standard validation result format."""

    validator_name: str
    status: str  # 'passed', 'failed', 'warning'
    issues_found: int
    total_checked: int
    details: dict[str, Any]
    timestamp: str
    duration_seconds: float

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        if self.total_checked == 0:
            return 100.0
        return ((self.total_checked - self.issues_found) / self.total_checked) * 100.0


class BaseValidator(ABC):
    """Base class for all validation scripts."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.start_time: datetime | None = None
        self.issues: list[dict[str, Any]] = []

    @abstractmethod
    def validate(self) -> ValidationResult:
        """Perform the validation and return results."""

    def run(self) -> ValidationResult:
        """Execute the validation with timing and error handling."""
        self.start_time = datetime.now(timezone.utc)

        try:
            return self.validate()
        except Exception as e:
            return ValidationResult(validator_name=self.name, status="failed", issues_found=1, total_checked=0, details={"error": str(e)}, timestamp=self.start_time.isoformat() if self.start_time else "", duration_seconds=(datetime.now(timezone.utc) - self.start_time).total_seconds() if self.start_time else 0.0)

    def add_issue(self, issue: str, file_path: str | None = None, line_number: int | None = None) -> None:
        """Add an issue to the current validation."""
        issue_data: dict[str, Any] = {"message": issue}
        if file_path:
            issue_data["file"] = file_path
        if line_number is not None:
            issue_data["line"] = line_number
        self.issues.append(issue_data)

    def get_elapsed_time(self) -> float:
        """Get elapsed time since validation started."""
        if self.start_time:
            return (datetime.now(timezone.utc) - self.start_time).total_seconds()
        return 0.0


class FileValidator(BaseValidator):
    """Base class for validators that work with files."""

    def __init__(self, name: str, description: str, file_patterns: list[str]):
        super().__init__(name, description)
        self.file_patterns = file_patterns

    def get_files_to_validate(self) -> list[Path]:
        """Get list of files matching the patterns."""
        files: list[Path] = []
        for pattern in self.file_patterns:
            files.extend(Path().glob(pattern))
        return [f for f in files if f.is_file()]


class SubprocessRunner:
    """Utility for running subprocess commands with consistent error handling."""

    @staticmethod
    def run_command(command: list[str], timeout: int = 60, cwd: str | None = None) -> dict[str, Any]:
        """Run a command and return structured result."""
        try:
            result = subprocess.run(command, check=False, capture_output=True, text=True, timeout=timeout, cwd=cwd)

            return {"success": result.returncode == 0, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "command": " ".join(command)}
        except subprocess.TimeoutExpired:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": f"Command timed out after {timeout} seconds", "command": " ".join(command)}
        except Exception as e:
            return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e), "command": " ".join(command)}


class ReportGenerator:
    """Utility for generating validation reports."""

    @staticmethod
    def save_json_report(result: ValidationResult, output_path: Path) -> None:
        """Save validation result as JSON."""
        report_data = {"validator": result.validator_name, "status": result.status, "timestamp": result.timestamp, "duration_seconds": result.duration_seconds, "issues_found": result.issues_found, "total_checked": result.total_checked, "success_rate": result.success_rate, "details": result.details}

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w") as f:
            json.dump(report_data, f, indent=2)

    @staticmethod
    def generate_summary_report(results: list[ValidationResult]) -> dict[str, Any]:
        """Generate summary report from multiple validation results."""
        total_issues = sum(r.issues_found for r in results)
        total_checked = sum(r.total_checked for r in results)
        passed_validators = sum(1 for r in results if r.status == "passed")

        return {
            "summary": {
                "total_validators": len(results),
                "passed_validators": passed_validators,
                "failed_validators": len(results) - passed_validators,
                "total_issues": total_issues,
                "total_checked": total_checked,
                "overall_success_rate": ((total_checked - total_issues) / total_checked * 100) if total_checked > 0 else 100.0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "validator_results": [{"name": r.validator_name, "status": r.status, "issues": r.issues_found, "total_checked": r.total_checked, "success_rate": r.success_rate, "duration": r.duration_seconds, "details": r.details} for r in results],
        }


class ValidationUtils:
    """Common utility functions for validation scripts."""

    @staticmethod
    def find_markdown_files() -> list[Path]:
        """Find all markdown files in the project."""
        patterns = ["docs/**/*.md", "*.md"]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(Path().glob(pattern))
        return [f for f in files if f.is_file()]

    @staticmethod
    def find_python_files() -> list[Path]:
        """Find all Python files in the project."""
        patterns = ["fivetwenty/**/*.py", "scripts/**/*.py", "tests/**/*.py"]
        files: list[Path] = []
        for pattern in patterns:
            files.extend(Path().glob(pattern))
        return [f for f in files if f.is_file()]

    @staticmethod
    def extract_code_blocks(content: str) -> list[str]:
        """Extract code blocks from markdown content."""
        import re

        return re.findall(r"```(?:python|bash|json|yaml)?\n(.*?)\n```", content, re.DOTALL)

    @staticmethod
    def check_file_age(file_path: Path) -> int:
        """Get file age in days."""
        stat_info = file_path.stat()
        file_time = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)
        return (datetime.now(timezone.utc) - file_time).days
