"""Code type checking validator for documentation code blocks."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


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

        lines = content.split("\n")

        # Track code block state
        in_code_block = False
        code_block_lines: list[str] = []
        code_block_start = 0
        code_block_language = ""

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if stripped.startswith("```"):
                if not in_code_block:
                    # Starting a code block
                    in_code_block = True
                    code_block_start = line_num
                    code_block_lines = []
                    code_block_language = stripped[3:].strip().lower()
                else:
                    # Ending a code block
                    in_code_block = False

                    # Validate the code block if it's Python
                    if code_block_language in ["python", "py", ""] and code_block_lines:
                        # Check for validation skip comments before the code block
                        should_skip = self._should_skip_validation(lines, code_block_start - 1)

                        if not should_skip:
                            issues.extend(self._type_check_python_code(code_block_lines, code_block_start + 1, file_info.path))

                    # Reset for next block
                    code_block_lines = []
                    code_block_language = ""
            elif in_code_block:
                # Collect code block content
                code_block_lines.append(line)

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _type_check_python_code(self, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Type check Python code using mypy."""
        issues: list[ValidationIssue] = []

        if not code_lines or all(not line.strip() for line in code_lines):
            return issues

        code = "\n".join(code_lines)

        # Skip code blocks that are clearly examples/placeholders
        if self._is_placeholder_code(code):
            return issues

        # Check if code is syntactically valid first
        try:
            ast.parse(code)
        except SyntaxError:
            # Don't type check syntactically invalid code
            return issues

        # Skip very simple code that doesn't benefit from type checking
        if self._is_simple_code(code):
            return issues

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
            result = subprocess.run(mypy_args, check=False, capture_output=True, text=True, timeout=8)

            if result.returncode == 0:
                # No type issues
                return issues

            # Parse mypy output
            issues.extend(self._parse_mypy_output(result.stdout, code_lines, start_line, file_path, enhanced_code))

        except subprocess.TimeoutExpired:
            issues.append(ValidationIssue(message="Type checking timeout - code block too complex", file_path=file_path, line=start_line, severity=IssueSeverity.WARNING, rule_id="code_typing_timeout", context="", suggestion="Simplify code example or add type: ignore comments"))
        except (subprocess.SubprocessError, FileNotFoundError):
            # mypy not available or other subprocess error
            pass
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
        """Check if code is clearly a placeholder/example that shouldn't be type checked."""
        placeholder_patterns = [
            r"your[-_]token[-_]here",
            r"your[-_]api[-_]key",
            r"your[-_]account[-_]id",
            r"your[-_]practice[-_]token",
            r"your[-_]api[-_]token",
            r"replace[-_]with[-_]your",
            r"<[^>]+>",  # HTML-like placeholders
            r"\.\.\.",  # Ellipsis indicating continuation
            r"# TODO",
            r"# FIXME",
            r"# Your code here",
            r"pass\s*#.*example",
            r"# File: \.env",  # .env file examples
            r"FIVETWENTY_OANDA_TOKEN=your-",  # Environment variable examples
            r"export\s+\w+=",  # Shell export commands
        ]

        code_lower = code.lower()
        return any(re.search(pattern, code_lower) for pattern in placeholder_patterns)

    def _is_simple_code(self, code: str) -> bool:
        """Check if code is too simple to benefit from type checking."""
        # Skip very simple examples
        lines = [line.strip() for line in code.split("\n") if line.strip()]

        # Skip single-line examples
        if len(lines) <= 1:
            return True

        # Skip print-only examples
        if all(line.startswith(("print(", "#")) for line in lines):
            return True

        # Skip variable assignment examples
        simple_patterns = [
            r"^\w+\s*=\s*.+$",  # Simple assignments
            r"^print\(",  # Print statements
            r"^#",  # Comments
        ]

        return all(any(re.match(pattern, line) for pattern in simple_patterns) for line in lines)

    def _should_skip_validation(self, lines: list[str], code_block_start_line: int) -> bool:
        """Check if validation should be skipped based on HTML comments before code block."""
        # Check the few lines before the code block for HTML comments
        check_lines = 3  # Check up to 3 lines before code block
        start_check = max(0, code_block_start_line - check_lines)

        for i in range(start_check, code_block_start_line):
            if i < len(lines):
                line = lines[i].strip().lower()

                # Check for validation skip patterns in HTML comments
                if "<!--" in line:
                    # Skip all validation
                    if any(pattern in line for pattern in ["validation: skip", "validation: skip-all", "fragment:", "partial:", "example:", "skip-type", "no-type"]):
                        return True

                    # Skip only typing (but allow linting)
                    if any(pattern in line for pattern in ["validation: skip-typing", "skip-typing", "no-typing"]):
                        return True

        return False

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
