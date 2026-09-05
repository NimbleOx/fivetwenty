"""Python syntax validator for code examples in documentation."""

import ast
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult
from .code_blocks import iter_fenced_blocks
from .fragments import FragmentTarget, find_fragment_marker, fragment_metadata, marker_skip_metadata


class PythonSyntaxValidator(BaseValidator):
    """Validates Python syntax in code examples and Python files."""

    def __init__(self) -> None:
        super().__init__(name="python_syntax", description="Validates Python syntax in code examples and files")

    def supports_file(self, file_path: Path) -> bool:
        """Support Python files and markdown files with Python code blocks."""
        return file_path.suffix.lower() in {".py", ".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate Python syntax in file content."""
        issues: list[ValidationIssue] = []
        skipped_blocks: list[dict[str, Any]] = []

        if file_info.path.suffix.lower() == ".py":
            # Validate entire Python file
            issues.extend(self._validate_python_file(content, file_info.path))
        else:
            # Extract and validate Python code blocks from markdown
            block_issues, skipped_blocks = self._validate_python_code_blocks(content, file_info.path)
            issues.extend(block_issues)

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues, metadata=fragment_metadata(skipped_blocks))

    def _validate_python_file(self, content: str, file_path: Path) -> list[ValidationIssue]:
        """Validate syntax of a complete Python file."""
        issues: list[ValidationIssue] = []

        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append(ValidationIssue(message=f"Python syntax error: {e.msg}", file_path=file_path, line=e.lineno, column=e.offset, severity=IssueSeverity.ERROR, rule_id="python_syntax_error", context=self._get_line_context(content, e.lineno) if e.lineno else None, suggestion="Fix the Python syntax error"))
        except Exception as e:
            issues.append(ValidationIssue(message=f"Failed to parse Python file: {e}", file_path=file_path, severity=IssueSeverity.ERROR, rule_id="python_parse_error", suggestion="Check file encoding and syntax"))

        return issues

    def _validate_python_code_blocks(self, content: str, file_path: Path) -> tuple[list[ValidationIssue], list[dict[str, Any]]]:
        """Extract and validate Python code blocks from markdown."""
        issues: list[ValidationIssue] = []

        skipped_blocks: list[dict[str, Any]] = []
        lines = content.splitlines()
        for block in iter_fenced_blocks(content):
            if not block.is_python:
                continue
            if not block.closed:
                issues.append(ValidationIssue(file_path=file_path, line=block.fence_line, rule_id="python_unclosed_block", message="Unclosed Python code fence"))
                continue
            if not block.code.strip():
                continue
            marker = find_fragment_marker(lines, block.fence_line, FragmentTarget.PYTHON_SYNTAX)
            if marker is not None:
                skipped_blocks.append(marker_skip_metadata(marker, block.fence_line))
                continue
            # Try to parse the code block
            try:
                ast.parse(block.code)
            except SyntaxError as e:
                # Calculate actual line number in file
                actual_line = block.fence_line + (e.lineno or 1)
                issues.append(
                    ValidationIssue(
                        message=f"Python syntax error in code block: {e.msg}",
                        file_path=file_path,
                        line=actual_line,
                        column=e.offset,
                        severity=IssueSeverity.ERROR,
                        rule_id="python_code_block_syntax",
                        context=self._get_line_context(block.code, e.lineno) if e.lineno else None,
                        suggestion="Fix the Python syntax in the code block",
                    )
                )
            except Exception as e:
                issues.append(ValidationIssue(message=f"Failed to parse Python code block: {e}", file_path=file_path, line=block.fence_line + 1, severity=IssueSeverity.WARNING, rule_id="python_code_block_parse", suggestion="Check the Python code block for syntax issues"))

        return issues, skipped_blocks

    def _get_line_context(self, content: str, line_num: int | None) -> str | None:
        """Get context around a specific line number."""
        if line_num is None:
            return None

        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1].strip()
        return None
