"""Base classes for validation checks."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult, ValidationStatus


class BaseCheck(ABC):
    """Base class for all validation checks."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, context: ValidationContext) -> ValidationResult:
        """Run the validation check."""

    def create_result(
        self,
        context: ValidationContext,
        status: ValidationStatus = ValidationStatus.PASSED,
        files_checked: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """Create a validation result."""
        return ValidationResult(
            check_name=self.name,
            status=status,
            files_checked=files_checked,
            metadata=metadata or {},
        )


class FileCheck(BaseCheck):
    """Base class for checks that operate on files."""

    def __init__(
        self,
        name: str,
        description: str,
        file_patterns: list[str] | None = None,
        required_extensions: list[str] | None = None,
    ) -> None:
        super().__init__(name, description)
        self.file_patterns = file_patterns or []
        self.required_extensions = required_extensions or []

    def run(self, context: ValidationContext) -> ValidationResult:
        """Run file-based validation."""
        start_time = datetime.now()
        result = self.create_result(context)

        try:
            # Get files to check
            files_to_check = self.get_files_to_check(context)
            result.files_checked = len(files_to_check)

            if not files_to_check:
                result.status = ValidationStatus.SKIPPED
                result.metadata["reason"] = "No files found matching patterns"
                return result

            # Process each file
            for file_path in files_to_check:
                try:
                    self.check_file(file_path, context, result)
                    context.mark_file_checked(file_path)
                except Exception as e:
                    result.add_issue(
                        message=f"Error checking file: {e}",
                        file_path=str(file_path),
                        severity=IssueSeverity.ERROR,
                    )

            # Determine final status
            if result.issues:
                error_count = len([i for i in result.issues if i.severity == IssueSeverity.ERROR])
                result.status = ValidationStatus.FAILED if error_count > 0 else ValidationStatus.WARNING
            else:
                result.status = ValidationStatus.PASSED

        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.add_issue(
                message=f"Check execution failed: {e}",
                file_path="<check>",
                severity=IssueSeverity.ERROR,
            )

        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

        return result

    def get_files_to_check(self, context: ValidationContext) -> list[Path]:
        """Get list of files to check."""
        if self.file_patterns:
            files = context.config.get_files_for_patterns(self.file_patterns)
        else:
            files = context.get_files_for_validation()

        # Filter by required extensions if specified
        if self.required_extensions:
            files = [f for f in files if any(f.suffix.lower() == ext.lower() for ext in self.required_extensions)]

        return files

    @abstractmethod
    def check_file(self, file_path: Path, context: ValidationContext, result: ValidationResult) -> None:
        """Check a single file. Add issues to result as needed."""


class ContentCheck(FileCheck):
    """Base class for checks that analyze file content."""

    def check_file(self, file_path: Path, context: ValidationContext, result: ValidationResult) -> None:
        """Check file content."""
        try:
            content = context.get_file_content(file_path)
            self.check_content(file_path, content, context, result)
        except UnicodeDecodeError:
            result.add_issue(
                message="File contains non-UTF-8 content",
                file_path=str(file_path),
                severity=IssueSeverity.WARNING,
            )
        except Exception as e:
            result.add_issue(
                message=f"Error reading file: {e}",
                file_path=str(file_path),
                severity=IssueSeverity.ERROR,
            )

    @abstractmethod
    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check file content. Add issues to result as needed."""


class ExternalToolCheck(BaseCheck):
    """Base class for checks that use external tools."""

    def __init__(
        self,
        name: str,
        description: str,
        tool_name: str,
        required: bool = True,
    ) -> None:
        super().__init__(name, description)
        self.tool_name = tool_name
        self.required = required

    def run(self, context: ValidationContext) -> ValidationResult:
        """Run external tool check."""
        start_time = datetime.now()
        result = self.create_result(context)

        try:
            # Check if tool is available
            if not context.check_external_tool(self.tool_name):
                if self.required:
                    result.status = ValidationStatus.ERROR
                    result.add_issue(
                        message=f"Required tool '{self.tool_name}' not found",
                        file_path="<system>",
                        severity=IssueSeverity.ERROR,
                    )
                else:
                    result.status = ValidationStatus.SKIPPED
                    result.metadata["reason"] = f"Optional tool '{self.tool_name}' not available"
                return result

            # Run the tool-specific check
            self.run_tool_check(context, result)

        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.add_issue(
                message=f"Tool check failed: {e}",
                file_path="<tool>",
                severity=IssueSeverity.ERROR,
            )

        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

        return result

    @abstractmethod
    def run_tool_check(self, context: ValidationContext, result: ValidationResult) -> None:
        """Run the tool-specific check."""
