"""
Code Example validation for documentation.

Validates that Python code blocks in explanation docs are syntactically correct
and use proper imports, types, and SDK patterns.
"""

import ast
import re
import sys
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class CodeExampleValidator(FileValidator):  # type: ignore[misc]
    """Validates code examples in documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="code_example_validator",
            description="Validates Python code examples for syntax and best practices",
            file_patterns=["docs/**/*.md", "*.md"]
        )
        self.code_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate code examples in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)
        total_code_blocks = 0

        for file_path in files:
            total_code_blocks += self._check_file_code_examples(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.code_issues) == 0 else "failed",
            issues_found=len(self.code_issues),
            total_checked=total_code_blocks,
            details={"code_issues": self.code_issues, "files_checked": total_files, "code_blocks_checked": total_code_blocks},
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _check_file_code_examples(self, file_path: Path) -> int:
        """Check code examples in a single file. Returns number of code blocks checked."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Extract Python code blocks
            python_blocks = self._extract_python_code_blocks(content)

            for block_num, (code, line_start) in enumerate(python_blocks, 1):
                self._validate_code_block(file_path, code, line_start, block_num)

            return len(python_blocks)

        except Exception as e:
            self.code_issues.append({
                "file": str(file_path),
                "type": "file_error",
                "message": f"Could not read file: {e}",
                "severity": "error"
            })
            return 0

    def _extract_python_code_blocks(self, content: str) -> list[tuple[str, int]]:
        """Extract Python code blocks from markdown content."""
        blocks = []
        lines = content.split('\n')
        in_python_block = False
        current_block = []
        block_start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('```python'):
                in_python_block = True
                current_block = []
                block_start_line = line_num + 1
            elif line.strip() == '```' and in_python_block:
                if current_block:
                    blocks.append(('\n'.join(current_block), block_start_line))
                in_python_block = False
            elif in_python_block:
                current_block.append(line)

        return blocks

    def _validate_code_block(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Validate a single Python code block."""
        # Skip validation for incomplete examples or comments
        if self._is_incomplete_example(code):
            return

        # Check syntax
        self._check_syntax(file_path, code, line_start, block_num)

        # Check imports
        self._check_imports(file_path, code, line_start, block_num)

        # Check for deprecated patterns
        self._check_deprecated_patterns(file_path, code, line_start, block_num)

        # Check financial precision
        self._check_financial_precision(file_path, code, line_start, block_num)

        # Check async patterns
        self._check_async_patterns(file_path, code, line_start, block_num)

    def _is_incomplete_example(self, code: str) -> bool:
        """Check if this is an incomplete example that shouldn't be validated."""
        incomplete_markers = [
            "# ...", "# ... rest of code", "# ... implementation",
            "pass  # Implementation", "# TODO:", "# FIXME:",
            "# Example output:", "# Output:", "# Result:",
            "...", "# ... more code"
        ]

        # Skip examples marked as BAD or showing incorrect syntax
        bad_example_markers = [
            "# BAD:", "# BAD ", "# WRONG:", "# INCORRECT:",
            "# This is wrong", "# Don't do this"
        ]

        # Also skip very short code snippets
        if len(code.strip()) < 10:
            return True

        # Skip incomplete examples
        if any(marker in code for marker in incomplete_markers):
            return True

        # Skip bad examples (they're meant to show what NOT to do)
        if any(marker in code for marker in bad_example_markers):
            return True

        return False

    def _check_syntax(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check Python syntax of code block."""
        try:
            ast.parse(code)
        except SyntaxError as e:
            self._add_code_issue(
                file_path=file_path,
                issue_type="syntax_error",
                message=f"Syntax error in code block {block_num}: {e.msg}",
                line=line_start + (e.lineno - 1 if e.lineno else 0),
                severity="critical",
                code_snippet=code[:100] + "..." if len(code) > 100 else code
            )

    def _check_imports(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for proper imports in code examples."""
        # Check for ErrorCode vs FiveTwentyErrorCode
        if "ErrorCode" in code and "FiveTwentyErrorCode" not in code:
            # Make sure it's not FiveTwentyErrorCode already
            if re.search(r'\bErrorCode\b', code) and not re.search(r'\bFiveTwentyErrorCode\b', code):
                self._add_code_issue(
                    file_path=file_path,
                    issue_type="incorrect_import",
                    message=f"Code block {block_num} uses 'ErrorCode' instead of 'FiveTwentyErrorCode'",
                    line=line_start,
                    severity="critical",
                    suggestion="Replace 'ErrorCode' with 'FiveTwentyErrorCode'"
                )

        # Check for os.environ usage without import
        if "os.environ" in code and "import os" not in code:
            self._add_code_issue(
                file_path=file_path,
                issue_type="missing_import",
                message=f"Code block {block_num} uses 'os.environ' without 'import os'",
                line=line_start,
                severity="error",
                suggestion="Add 'import os' to the imports"
            )

        # Check for Decimal usage without import
        if "Decimal(" in code and "from decimal import Decimal" not in code:
            self._add_code_issue(
                file_path=file_path,
                issue_type="missing_import",
                message=f"Code block {block_num} uses 'Decimal' without proper import",
                line=line_start,
                severity="error",
                suggestion="Add 'from decimal import Decimal' to the imports"
            )

        # Check for common FiveTwenty imports
        fivetwenty_patterns = [
            (r"AsyncClient", "from fivetwenty import AsyncClient"),
            (r"Client\(", "from fivetwenty import Client"),
            (r"Environment\.", "from fivetwenty import Environment"),
            (r"FiveTwentyError", "from fivetwenty.exceptions import FiveTwentyError"),
        ]

        for pattern, required_import in fivetwenty_patterns:
            if re.search(pattern, code):
                # Check if the import is present (more flexible matching)
                import_base = required_import.split(' import ')[1]  # Get the class name after "import"
                import_patterns = [
                    required_import,  # Exact match
                    f"from fivetwenty import.*{import_base}",  # Multi-import line
                    f"import fivetwenty.*{import_base}",  # Alternative import style
                ]

                has_import = any(re.search(pattern_check, code) for pattern_check in import_patterns)

                if not has_import:
                    # Only flag if this looks like it should have the import
                    if not self._is_import_example(code):
                        self._add_code_issue(
                            file_path=file_path,
                            issue_type="missing_import",
                            message=f"Code block {block_num} may be missing: {required_import}",
                            line=line_start,
                            severity="warning",
                            suggestion=f"Consider adding: {required_import}"
                        )

    def _is_import_example(self, code: str) -> bool:
        """Check if this code block is showing import examples."""
        return any(keyword in code.lower() for keyword in [
            "# import", "# imports", "import example", "importing"
        ])

    def _check_deprecated_patterns(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for deprecated SDK patterns."""
        deprecated_patterns = [
            (r"refresh_token\(\)", "Placeholder function 'refresh_token()' should be replaced with implementation note"),
            (r"notify_operations_team\(", "Placeholder function 'notify_operations_team()' should be replaced with implementation note"),
            (r"undefined_function\(", "Undefined function calls should be replaced with implementation notes"),
            (r"\.create_market_order\(", "Use '.post_market_order()' instead of '.create_market_order()'"),
            (r"\.create_limit_order\(", "Use '.post_limit_order()' instead of '.create_limit_order()'"),
        ]

        for pattern, message in deprecated_patterns:
            if re.search(pattern, code):
                self._add_code_issue(
                    file_path=file_path,
                    issue_type="deprecated_pattern",
                    message=f"Code block {block_num}: {message}",
                    line=line_start,
                    severity="critical"
                )

    def _check_financial_precision(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for proper financial precision in code examples."""
        # Check for float usage in financial contexts
        financial_contexts = [
            r"price\s*=\s*\d+\.\d+",
            r"amount\s*=\s*\d+\.\d+",
            r"spread\s*=\s*\d+\.\d+",
            r"balance\s*=\s*\d+\.\d+",
            r"margin\s*=\s*\d+\.\d+",
            r"units\s*=\s*\d+\.\d+",
        ]

        for pattern in financial_contexts:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                if "Decimal" not in match.group():
                    self._add_code_issue(
                        file_path=file_path,
                        issue_type="financial_precision",
                        message=f"Code block {block_num}: Financial value should use Decimal, not float: {match.group()}",
                        line=line_start,
                        severity="error",
                        suggestion=f"Use Decimal('{match.group().split('=')[1].strip()}') instead"
                    )

        # Check for explicit float() usage
        if re.search(r"float\(\s*['\"]?[\d.]+['\"]?\s*\)", code):
            self._add_code_issue(
                file_path=file_path,
                issue_type="financial_precision",
                message=f"Code block {block_num}: Avoid float() for financial calculations, use Decimal instead",
                line=line_start,
                severity="error"
            )

    def _check_async_patterns(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for proper async/await patterns."""
        # Check for missing await with async client methods
        async_methods = [
            r"client\.accounts\.\w+\(",
            r"client\.orders\.\w+\(",
            r"client\.trades\.\w+\(",
            r"client\.positions\.\w+\(",
            r"client\.pricing\.\w+\(",
        ]

        has_await_keyword = "await" in code
        has_async_def = "async def" in code

        for pattern in async_methods:
            matches = re.finditer(pattern, code)
            for match in matches:
                # Check if this specific call has await
                line_with_call = self._get_line_containing_position(code, match.start())
                if line_with_call and "await" not in line_with_call:
                    # Only flag if this looks like an async context
                    if has_async_def or "AsyncClient" in code:
                        self._add_code_issue(
                            file_path=file_path,
                            issue_type="missing_await",
                            message=f"Code block {block_num}: Async client method call may be missing 'await': {match.group()}",
                            line=line_start,
                            severity="warning",
                            suggestion="Add 'await' before async client method calls"
                        )

    def _get_line_containing_position(self, text: str, position: int) -> str:
        """Get the line containing the given position in text."""
        lines = text[:position + 50].split('\n')  # Get context around position
        return lines[-1] if lines else ""

    def _add_code_issue(self, file_path: Path, issue_type: str, message: str, line: int, severity: str, **kwargs: Any) -> None:
        """Add a code issue to the results."""
        # Try to make path relative to current working directory, fall back to just the filename
        try:
            display_path = str(file_path.relative_to(Path.cwd()))
        except ValueError:
            # If file is not in a subpath of cwd, just use the filename
            display_path = file_path.name

        issue = {
            "file": display_path,
            "line": line,
            "type": issue_type,
            "message": message,
            "severity": severity,
            **kwargs
        }
        self.code_issues.append(issue)
        self.add_issue(message, str(file_path), line)