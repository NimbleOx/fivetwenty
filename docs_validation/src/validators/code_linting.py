"""Code linting validator for documentation code blocks."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class CodeLintingValidator(BaseValidator):
    """Validates Python code examples in documentation using ruff linter."""

    def __init__(self) -> None:
        super().__init__(name="code_linting", description="Validates Python code examples follow linting standards using ruff")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate code linting in file content."""
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
                            issues.extend(
                                self._lint_python_code(
                                    code_block_lines,
                                    code_block_start + 1,
                                    file_info.path,
                                    options,
                                )
                            )

                    # Reset for next block
                    code_block_lines = []
                    code_block_language = ""
            elif in_code_block:
                # Collect code block content
                code_block_lines.append(line)

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _lint_python_code(self, code_lines: list[str], start_line: int, file_path: Path, options: dict[str, Any]) -> list[ValidationIssue]:
        """Lint Python code using ruff."""
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
            # Don't lint syntactically invalid code
            return issues

        # Create temporary file for ruff
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(code)
            temp_path = temp_file.name

        try:
            # Build ruff command with options
            ruff_cmd = ["ruff", "check", "--output-format=json", "--select=ALL", temp_path]

            # Add ignore rules if specified in options
            ignore_rules = options.get("ignore_rules", [])
            if ignore_rules:
                ignore_str = ",".join(ignore_rules)
                ruff_cmd.extend(["--ignore", ignore_str])

            # Run ruff check
            result = subprocess.run(ruff_cmd, check=False, capture_output=True, text=True, timeout=10)

            if result.returncode == 0:
                # No linting issues
                return issues

            # Parse ruff JSON output
            try:
                import json

                ruff_issues = json.loads(result.stdout)
            except (json.JSONDecodeError, ValueError):
                # Fallback to text parsing if JSON fails
                return self._parse_ruff_text_output(result.stdout, code_lines, start_line, file_path)

            # Convert ruff issues to validation issues
            for ruff_issue in ruff_issues:
                if ruff_issue.get("filename", "").endswith(temp_path):
                    line_in_code = ruff_issue.get("location", {}).get("row", 1)
                    doc_line = start_line + line_in_code - 1

                    # Get the actual line content
                    context = ""
                    if 1 <= line_in_code <= len(code_lines):
                        context = code_lines[line_in_code - 1].strip()

                    # All issues are errors in strict mode
                    rule_code = ruff_issue.get("code", "")
                    severity = IssueSeverity.ERROR

                    issues.append(
                        ValidationIssue(
                            message=f"Linting: {ruff_issue.get('message', 'Unknown linting issue')} ({rule_code})", file_path=file_path, line=doc_line, severity=severity, rule_id=f"code_lint_{rule_code.lower()}", context=context, suggestion=self._get_suggestion_for_rule(rule_code, ruff_issue.get("message", ""))
                        )
                    )

        except subprocess.TimeoutExpired:
            issues.append(ValidationIssue(message="Linting timeout - code block too complex", file_path=file_path, line=start_line, severity=IssueSeverity.WARNING, rule_id="code_lint_timeout", context="", suggestion="Simplify code example or split into smaller blocks"))
        except (subprocess.SubprocessError, FileNotFoundError):
            # ruff not available or other subprocess error
            pass
        finally:
            # Clean up temporary file
            try:
                Path(temp_path).unlink()
            except (OSError, FileNotFoundError):
                pass

        return issues

    def _parse_ruff_text_output(self, output: str, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Parse ruff text output as fallback."""
        issues: list[ValidationIssue] = []

        # Parse ruff text output (format: filename:line:col: rule message)
        for line in output.strip().split("\n"):
            if not line.strip():
                continue

            # Match pattern: filename:line:col: CODE message
            match = re.match(r".+:(\d+):(\d+):\s*([A-Z]\d+)\s*(.+)", line)
            if match:
                line_num, _col_num, rule_code, message = match.groups()
                doc_line = start_line + int(line_num) - 1

                context = ""
                if 1 <= int(line_num) <= len(code_lines):
                    context = code_lines[int(line_num) - 1].strip()

                severity = IssueSeverity.ERROR

                issues.append(ValidationIssue(message=f"Linting: {message} ({rule_code})", file_path=file_path, line=doc_line, severity=severity, rule_id=f"code_lint_{rule_code.lower()}", context=context, suggestion=self._get_suggestion_for_rule(rule_code, message)))

        return issues

    def _get_suggestion_for_rule(self, rule_code: str, message: str) -> str:
        """Get suggestion for fixing a rule violation."""
        return f"Fix linting issue: {message}"

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
                    if any(pattern in line for pattern in ["validation: skip", "validation: skip-all", "fragment:", "partial:", "example:", "skip-lint", "no-lint"]):
                        return True

                    # Skip only linting (but allow typing)
                    if any(pattern in line for pattern in ["validation: skip-linting", "skip-linting", "no-linting"]):
                        return True

        return False

    def _is_placeholder_code(self, code: str) -> bool:
        """Check if code is clearly a placeholder/example that shouldn't be linted."""
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

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
