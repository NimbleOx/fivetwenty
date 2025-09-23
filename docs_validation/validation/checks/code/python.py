"""Python code validation checks."""

import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from validation.checks.base import ContentCheck, ExternalToolCheck
from validation.core.context import ValidationContext
from validation.core.results import IssueSeverity, ValidationResult


class PythonSyntaxCheck(ContentCheck):
    """Check Python code blocks for syntax errors."""

    def __init__(self) -> None:
        super().__init__(
            name="python_syntax",
            description="Validates Python code blocks for syntax errors",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check Python code blocks for syntax errors."""
        code_blocks = self._extract_python_code_blocks(content)

        for block_info in code_blocks:
            self._validate_code_block(file_path, block_info, result)

    def _extract_python_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract Python code blocks with metadata."""
        blocks = []
        lines = content.split("\n")
        in_python_block = False
        current_block_lines = []
        block_start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```python"):
                in_python_block = True
                current_block_lines = []
                block_start_line = line_num
            elif line.strip() == "```" and in_python_block:
                if current_block_lines:
                    blocks.append(
                        {
                            "code": "\n".join(current_block_lines),
                            "start_line": block_start_line,
                            "end_line": line_num,
                            "line_count": len(current_block_lines),
                        }
                    )
                in_python_block = False
            elif in_python_block:
                current_block_lines.append(line)

        return blocks

    def _validate_code_block(
        self,
        file_path: Path,
        block_info: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Validate a single Python code block."""
        code = block_info["code"]
        start_line = block_info["start_line"]

        # Check for syntax errors
        try:
            ast.parse(code)
        except SyntaxError as e:
            # Calculate actual line number in file
            error_line = start_line + (e.lineno or 1)

            result.add_issue(
                message=f"Python syntax error: {e.msg}",
                file_path=str(file_path),
                line=error_line,
                severity=IssueSeverity.ERROR,
                rule="python_syntax_error",
                context={
                    "error_type": type(e).__name__,
                    "error_msg": str(e.msg) if e.msg else "Unknown syntax error",
                    "code_block_start": start_line,
                    "code_snippet": code[:100] + "..." if len(code) > 100 else code,
                },
            )

        # Check for common issues
        self._check_common_issues(file_path, code, start_line, result)

    def _is_documentation_file(self, file_path: Path) -> bool:
        """Check if file is documentation where print() is appropriate."""
        doc_patterns = ["/docs/", "/tutorials/", "/examples/", "/guides/", "README", ".md"]
        path_str = str(file_path)
        return any(pattern in path_str for pattern in doc_patterns)

    def _check_common_issues(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for common Python code issues."""
        lines = code.split("\n")

        for line_offset, line in enumerate(lines):
            actual_line = start_line + line_offset + 1

            # Check for common anti-patterns
            if "eval(" in line:
                result.add_issue(
                    message="Avoid using eval() - security risk",
                    file_path=str(file_path),
                    line=actual_line,
                    severity=IssueSeverity.WARNING,
                    rule="dangerous_eval",
                    suggestion="Use ast.literal_eval() for safe evaluation",
                )

            if "exec(" in line:
                result.add_issue(
                    message="Avoid using exec() - security risk",
                    file_path=str(file_path),
                    line=actual_line,
                    severity=IssueSeverity.WARNING,
                    rule="dangerous_exec",
                )

            # Check for print statements (skip in documentation/tutorial files)
            if re.match(r"^\s*print\s*\(", line) and not self._is_documentation_file(file_path):
                result.add_issue(
                    message="Consider using logging instead of print()",
                    file_path=str(file_path),
                    line=actual_line,
                    severity=IssueSeverity.INFO,
                    rule="print_statement",
                    suggestion="Use logging.info() or similar",
                )


class PythonStyleCheck(ExternalToolCheck):
    """Check Python code blocks with ruff for style issues."""

    def __init__(self) -> None:
        super().__init__(
            name="python_style",
            description="Validates Python code blocks with ruff linting",
            tool_name="ruff",
            required=False,
        )

    def run_tool_check(self, context: ValidationContext, result: ValidationResult) -> None:
        """Run ruff on Python code blocks."""
        # Find markdown files
        markdown_files = context.get_files_for_validation()

        for file_path in markdown_files:
            if file_path.suffix.lower() == ".md":
                try:
                    content = context.get_file_content(file_path)
                    self._check_file_python_blocks(file_path, content, result)
                    result.files_checked += 1
                except Exception as e:
                    result.add_issue(
                        message=f"Error processing file: {e}",
                        file_path=str(file_path),
                        severity=IssueSeverity.ERROR,
                    )

    def _check_file_python_blocks(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check Python code blocks in a markdown file."""
        code_blocks = self._extract_python_code_blocks(content)

        for block_info in code_blocks:
            self._run_ruff_on_block(file_path, block_info, result)

    def _extract_python_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract Python code blocks (same as syntax check)."""
        blocks = []
        lines = content.split("\n")
        in_python_block = False
        current_block_lines = []
        block_start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```python"):
                in_python_block = True
                current_block_lines = []
                block_start_line = line_num
            elif line.strip() == "```" and in_python_block:
                if current_block_lines:
                    blocks.append(
                        {
                            "code": "\n".join(current_block_lines),
                            "start_line": block_start_line,
                            "end_line": line_num,
                            "line_count": len(current_block_lines),
                        }
                    )
                in_python_block = False
            elif in_python_block:
                current_block_lines.append(line)

        return blocks

    def _run_ruff_on_block(
        self,
        file_path: Path,
        block_info: dict[str, Any],
        result: ValidationResult,
    ) -> None:
        """Run ruff on a single code block."""
        code = block_info["code"]
        start_line = block_info["start_line"]

        # Skip very short code blocks
        if len(code.strip()) < 10:
            return

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        try:
            # Run ruff
            ruff_result = subprocess.run(
                ["ruff", "check", "--output-format=json", tmp_path],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if ruff_result.returncode != 0 and ruff_result.stdout:
                # Parse ruff JSON output
                try:
                    import json

                    ruff_issues = json.loads(ruff_result.stdout)

                    for issue in ruff_issues:
                        # Map ruff line number to actual markdown line
                        ruff_line = issue.get("location", {}).get("row", 1)
                        actual_line = start_line + ruff_line

                        severity = self._map_ruff_severity(issue.get("code", ""))

                        result.add_issue(
                            message=f"Python style: {issue.get('message', 'Style issue')}",
                            file_path=str(file_path),
                            line=actual_line,
                            severity=severity,
                            rule=f"ruff_{issue.get('code', 'unknown')}",
                            context={
                                "ruff_code": issue.get("code"),
                                "ruff_message": issue.get("message"),
                                "code_block_start": start_line,
                            },
                        )

                except json.JSONDecodeError:
                    # Fallback for non-JSON output
                    result.add_issue(
                        message="Ruff found style issues in Python code block",
                        file_path=str(file_path),
                        line=start_line,
                        severity=IssueSeverity.WARNING,
                        rule="ruff_general",
                        context={"raw_output": ruff_result.stdout[:200]},
                    )

        except subprocess.TimeoutExpired:
            result.add_issue(
                message="Ruff check timed out",
                file_path=str(file_path),
                line=start_line,
                severity=IssueSeverity.WARNING,
                rule="ruff_timeout",
            )

        except Exception as e:
            result.add_issue(
                message=f"Ruff check failed: {e}",
                file_path=str(file_path),
                line=start_line,
                severity=IssueSeverity.INFO,
                rule="ruff_error",
            )

        finally:
            # Clean up temporary file
            try:
                Path(tmp_path).unlink()
            except OSError:
                pass

    def _map_ruff_severity(self, ruff_code: str) -> IssueSeverity:
        """Map ruff error codes to our severity levels."""
        if not ruff_code:
            return IssueSeverity.WARNING

        # Error codes that should be errors
        error_prefixes = ["E9", "F8", "F4"]  # Syntax errors, import errors, etc.

        # Warning codes
        warning_prefixes = ["E", "W", "F"]  # Most style and logical errors

        # Info codes

        if any(ruff_code.startswith(prefix) for prefix in error_prefixes):
            return IssueSeverity.ERROR
        if any(ruff_code.startswith(prefix) for prefix in warning_prefixes):
            return IssueSeverity.WARNING
        return IssueSeverity.INFO
