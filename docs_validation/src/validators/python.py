"""Python syntax validator for code examples in documentation."""

import ast
import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


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

        if file_info.path.suffix.lower() == ".py":
            # Validate entire Python file
            issues.extend(self._validate_python_file(content, file_info.path))
        else:
            # Extract and validate Python code blocks from markdown
            issues.extend(self._validate_python_code_blocks(content, file_info.path))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

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

    def _validate_python_code_blocks(self, content: str, file_path: Path) -> list[ValidationIssue]:
        """Extract and validate Python code blocks from markdown."""
        issues: list[ValidationIssue] = []

        # Find Python code blocks
        code_blocks = self._extract_python_code_blocks(content)

        for block_start_line, code_block in code_blocks:
            # Try to parse the code block
            try:
                ast.parse(code_block)
            except SyntaxError as e:  # noqa: PERF203
                # Calculate actual line number in file
                actual_line = block_start_line + (e.lineno or 1)
                issues.append(
                    ValidationIssue(
                        message=f"Python syntax error in code block: {e.msg}",
                        file_path=file_path,
                        line=actual_line,
                        column=e.offset,
                        severity=IssueSeverity.ERROR,
                        rule_id="python_code_block_syntax",
                        context=self._get_line_context(code_block, e.lineno) if e.lineno else None,
                        suggestion="Fix the Python syntax in the code block",
                    )
                )
            except Exception as e:
                issues.append(ValidationIssue(message=f"Failed to parse Python code block: {e}", file_path=file_path, line=block_start_line, severity=IssueSeverity.WARNING, rule_id="python_code_block_parse", suggestion="Check the Python code block for syntax issues"))

        return issues

    def _extract_python_code_blocks(self, content: str) -> list[tuple[int, str]]:
        """Extract Python code blocks from markdown content."""
        code_blocks: list[tuple[int, str]] = []
        lines = content.split("\n")

        in_python_block = False
        current_block_lines: list[str] = []
        block_start_line = 0
        skip_next_block = False

        for line_num, line in enumerate(lines, 1):
            # Check for fragment marker (skip validation of next code block)
            if re.search(r"<!--\s*fragment", line, re.IGNORECASE):
                skip_next_block = True
            # Check for start of Python code block
            elif re.match(r"^\s*```\s*python\s*$", line, re.IGNORECASE):
                in_python_block = True
                current_block_lines = []
                block_start_line = line_num + 1  # Code starts on next line
            # Check for end of code block
            elif line.strip() == "```" and in_python_block:
                in_python_block = False
                if current_block_lines and not skip_next_block:
                    code_block = "\n".join(current_block_lines)
                    # Only validate non-empty blocks
                    if code_block.strip():
                        code_blocks.append((block_start_line, code_block))
                skip_next_block = False  # Reset for next block
            # Collect lines within Python block
            elif in_python_block:
                current_block_lines.append(line)

        return code_blocks

    def _get_line_context(self, content: str, line_num: int | None) -> str | None:
        """Get context around a specific line number."""
        if line_num is None:
            return None

        lines = content.split("\n")
        if 1 <= line_num <= len(lines):
            return lines[line_num - 1].strip()
        return None

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.py", "**/*.md", "**/*.markdown"]
