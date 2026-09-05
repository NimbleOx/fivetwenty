"""Code type checking validator for documentation code blocks."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult
from .code_blocks import iter_fenced_blocks
from .fragments import FragmentTarget, find_fragment_marker, fragment_metadata, implicit_skip_metadata, is_placeholder_code, marker_skip_metadata


class CodeTypingValidator(BaseValidator):
    """Validates Python code examples in documentation using mypy type checker."""

    def __init__(self) -> None:
        super().__init__(name="code_typing", description="Validates Python code examples for type safety using mypy")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate code typing in file content."""
        issues: list[ValidationIssue] = []

        lines = content.splitlines()
        skipped_blocks: list[dict[str, Any]] = []
        for block in iter_fenced_blocks(content):
            if not block.is_python:
                continue
            if not block.closed:
                issues.append(ValidationIssue(file_path=file_info.path, line=block.fence_line, rule_id="code_typing_unclosed_block", message="Unclosed Python code fence"))
                continue
            if not block.code.strip():
                continue
            marker = find_fragment_marker(lines, block.fence_line, FragmentTarget.TYPING)
            if marker is not None:
                skipped_blocks.append(marker_skip_metadata(marker, block.fence_line))
            elif self._is_placeholder_code(block.code):
                skipped_blocks.append(implicit_skip_metadata(block.fence_line, "Standalone ellipsis marks an incomplete example"))
            else:
                issues.extend(self._type_check_python_code(block.code.splitlines(), block.fence_line + 1, file_info.path, options))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues, metadata=fragment_metadata(skipped_blocks))

    def _type_check_python_code(self, code_lines: list[str], start_line: int, file_path: Path, options: dict[str, Any]) -> list[ValidationIssue]:
        """Type check Python code using mypy."""
        issues: list[ValidationIssue] = []

        if not code_lines or all(not line.strip() for line in code_lines):
            return issues

        code = "\n".join(code_lines)

        # Check if code is syntactically valid first
        try:
            ast.parse(code)
        except SyntaxError as exc:
            return [ValidationIssue(message=f"Cannot check invalid Python: {exc.msg}", file_path=file_path, line=start_line + (exc.lineno or 1) - 1, severity=IssueSeverity.ERROR, rule_id="code_typing_syntax")]

        # Create temporary file for mypy
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            # Add common imports for FiveTwenty code blocks
            enhanced_code = self._enhance_code_with_imports(code)
            temp_file.write(enhanced_code)
            temp_path = temp_file.name

        try:
            # Build mypy command
            mypy_args = [
                "mypy",
                "--show-error-codes",
                "--no-error-summary",
                "--show-column-numbers",
            ]

            # Always run in strict mode to capture all type issues
            mypy_args.extend(["--strict", "--warn-return-any", "--warn-unused-ignores"])

            mypy_args.append(temp_path)

            # Run mypy
            timeout_seconds = float(options.get("timeout_seconds", 8.0))
            result = subprocess.run(mypy_args, check=False, capture_output=True, text=True, timeout=timeout_seconds)

            if result.returncode == 0:
                # No type issues
                return issues

            # Parse mypy output
            issues.extend(self._parse_mypy_output(result.stdout, code_lines, start_line, file_path, enhanced_code))
            if not issues:
                issues.append(ValidationIssue(message=f"mypy exited with status {result.returncode}: {result.stderr.strip() or result.stdout.strip()}", file_path=file_path, line=start_line, severity=IssueSeverity.ERROR, rule_id="code_typing_failed"))

        except subprocess.TimeoutExpired:
            issues.append(
                ValidationIssue(message=f"Type checking timeout after {timeout_seconds:g}s - code block too complex", file_path=file_path, line=start_line, severity=IssueSeverity.ERROR, rule_id="code_typing_timeout", context="", suggestion="Simplify code example or increase the code_typing timeout_seconds option")
            )
        except (subprocess.SubprocessError, OSError) as exc:
            issues.append(ValidationIssue(message=f"mypy could not run: {exc}", file_path=file_path, line=start_line, severity=IssueSeverity.ERROR, rule_id="code_typing_unavailable", suggestion="Install the development dependencies and put their executables on PATH"))
        finally:
            # Clean up temporary file
            try:
                Path(temp_path).unlink()
            except (OSError, FileNotFoundError):
                pass

        return issues

    def _enhance_code_with_imports(self, code: str) -> str:
        """Enhance code with common FiveTwenty imports and type hints."""
        lines = code.strip().split("\n")

        # Check if imports are already present
        has_fivetwenty_imports = any("from fivetwenty import" in line or "import fivetwenty" in line for line in lines)
        has_typing_imports = any("from typing import" in line or "import typing" in line for line in lines)

        enhanced_lines = []

        # Add common imports if not present
        if not has_typing_imports and ("List[" in code or "Dict[" in code or "Optional[" in code):
            enhanced_lines.append("from typing import List, Dict, Optional, Any")
            enhanced_lines.append("")

        if not has_fivetwenty_imports and ("AsyncClient" in code or "Client" in code):
            enhanced_lines.append("from fivetwenty import AsyncClient, Client, Environment, AccountConfig")
            enhanced_lines.append("from fivetwenty.models import InstrumentName")
            enhanced_lines.append("")

        # Add the original code
        enhanced_lines.extend(lines)

        return "\n".join(enhanced_lines)

    def _parse_mypy_output(self, output: str, code_lines: list[str], start_line: int, file_path: Path, enhanced_code: str) -> list[ValidationIssue]:
        """Parse mypy output and convert to validation issues."""
        issues: list[ValidationIssue] = []

        # Calculate line offset due to added imports
        original_code = "\n".join(code_lines)
        line_offset = len(enhanced_code.split("\n")) - len(original_code.split("\n"))

        for line in output.strip().split("\n"):
            if not line.strip():
                continue

            # Parse mypy output format: filename:line:col: error: message [error-code]
            match = re.match(r".+:(\d+):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[([^\]]+)\])?$", line)
            if match:
                line_num, _col_num, _level, message, error_code = match.groups()

                # Adjust line number for original code
                original_line_num = int(line_num) - line_offset
                if original_line_num <= 0:
                    # Issue is in added imports, skip it
                    continue

                doc_line = start_line + original_line_num - 1

                # Get context from original code
                context = ""
                if 1 <= original_line_num <= len(code_lines):
                    context = code_lines[original_line_num - 1].strip()

                # All issues are errors in strict mode
                severity = IssueSeverity.ERROR

                issues.append(
                    ValidationIssue(
                        message=f"Type checking: {message}" + (f" [{error_code}]" if error_code else ""),
                        file_path=file_path,
                        line=doc_line,
                        severity=severity,
                        rule_id=f"code_typing_{error_code.lower().replace('-', '_') if error_code else 'generic'}",
                        context=context,
                        suggestion=self._get_suggestion_for_error(error_code, message),
                    )
                )

        return issues

    def _get_suggestion_for_error(self, error_code: str | None, message: str) -> str:
        """Get suggestion for fixing a mypy error."""
        return f"Fix type issue: {message}"

    def _is_placeholder_code(self, code: str) -> bool:
        """Recognize explicit Python stub statements without matching string contents."""
        return is_placeholder_code(code)

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
