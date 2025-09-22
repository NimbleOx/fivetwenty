"""Code executability validation checks."""

import ast
import re
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationIssue, ValidationResult


class CodeExecutabilityCheck(ContentCheck):
    """Check that tutorial code examples are executable and complete."""

    def __init__(self) -> None:
        super().__init__(
            name="code_executability",
            description="Validates that code examples are executable and complete",
            file_patterns=["docs/tutorials/**/*.md"],
            required_extensions=[".md"],
        )

        # Known placeholders that indicate incomplete examples
        self.placeholder_patterns = [
            r"# \.\.\.", r"pass\s*#.*implementation", r"\.\.\..*",
            r"# TODO", r"# FIXME", r"your_.*_here", r"<.*>",
            r"undefined_function\(\)", r"refresh_token\(\)"
        ]

        # Critical imports that must be present for FiveTwenty code
        self.required_imports = {
            "AsyncClient": "from fivetwenty import AsyncClient",
            "Client": "from fivetwenty import Client",
            "Environment": "from fivetwenty import Environment",
            "AccountConfig": "from fivetwenty import AccountConfig",
            "Decimal": "from decimal import Decimal",
            "datetime": "from datetime import datetime",
            "os.environ": "import os"
        }

        # Model imports
        self.model_imports = {
            "MarketOrderRequest": "from fivetwenty.models import MarketOrderRequest",
            "LimitOrderRequest": "from fivetwenty.models import LimitOrderRequest",
            "StopLossOrderRequest": "from fivetwenty.models import StopLossOrderRequest",
            "InstrumentName": "from fivetwenty.models import InstrumentName",
            "TimeInForce": "from fivetwenty.models import TimeInForce",
            "OrderType": "from fivetwenty.models import OrderType",
            "Side": "from fivetwenty.models import Side",
        }

        # Common undefined functions we've found in tutorials
        self.undefined_functions = [
            "refresh_token", "get_new_token", "setup_client", "initialize_trading",
            "custom_strategy", "your_function_here", "placeholder_function"
        ]

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check code blocks for executability issues."""
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
                block_start_line = line_num + 1
            elif line.strip() == "```" and in_python_block:
                if current_block_lines:
                    blocks.append({
                        "content": "\n".join(current_block_lines),
                        "start_line": block_start_line,
                        "end_line": line_num - 1,
                        "lines": current_block_lines
                    })
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
        """Validate a single code block for executability."""
        code = block_info["content"]
        start_line = block_info["start_line"]

        # Check for placeholder patterns
        self._check_placeholders(file_path, code, start_line, result)

        # Check for undefined functions
        self._check_undefined_functions(file_path, code, start_line, result)

        # Check for missing imports
        self._check_missing_imports(file_path, code, start_line, result)

        # Check for syntax issues
        self._check_syntax(file_path, code, start_line, result)

        # Check for incomplete async patterns
        self._check_async_patterns(file_path, code, start_line, result)

    def _check_placeholders(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for placeholder patterns that indicate incomplete code."""
        lines = code.split('\n')

        for line_offset, line in enumerate(lines):
            for pattern in self.placeholder_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    result.add_issue(
                        message="Code contains placeholder that prevents execution",
                        file_path=str(file_path),
                        line=start_line + line_offset,
                        severity=IssueSeverity.ERROR,
                        suggestion="Replace placeholder with actual implementation",
                        context={"line": line.strip()},
                    )

    def _check_undefined_functions(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for calls to undefined functions."""
        lines = code.split('\n')

        for line_offset, line in enumerate(lines):
            for func_name in self.undefined_functions:
                pattern = rf"\b{func_name}\s*\("
                if re.search(pattern, line):
                    result.add_issue(
                        message=f"Call to undefined function: {func_name}",
                        file_path=str(file_path),
                        line=start_line + line_offset,
                        severity=IssueSeverity.ERROR,
                        suggestion="Define the function or remove the call",
                        context={"line": line.strip()},
                    )

    def _check_missing_imports(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for missing imports for used symbols."""
        # Combine all import patterns
        all_imports = {**self.required_imports, **self.model_imports}

        for symbol, import_stmt in all_imports.items():
            # Check if symbol is used but not imported
            if re.search(rf"\b{symbol}\b", code) and import_stmt not in code:
                # Find the line where the symbol is first used
                lines = code.split('\n')
                for line_offset, line in enumerate(lines):
                    if re.search(rf"\b{symbol}\b", line):
                        result.add_issue(
                            message=f"Missing import for: {symbol}",
                            file_path=str(file_path),
                            line=start_line + line_offset,
                            severity=IssueSeverity.ERROR,
                            suggestion=f"Add: {import_stmt}",
                            context={"line": line.strip()},
                        )
                        break

    def _check_syntax(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for basic Python syntax errors."""
        try:
            ast.parse(code)
        except SyntaxError as e:
            result.add_issue(
                message=f"Syntax error: {e.msg}",
                file_path=str(file_path),
                line=start_line + (e.lineno or 1) - 1,
                severity=IssueSeverity.ERROR,
                suggestion="Fix the syntax error",
                context={"line": e.text.strip() if e.text else ""},
            )

    def _check_async_patterns(
        self,
        file_path: Path,
        code: str,
        start_line: int,
        result: ValidationResult,
    ) -> None:
        """Check for incomplete async patterns."""
        lines = code.split('\n')

        # Check for async client usage without proper context or await
        if "AsyncClient" in code:
            has_async_with = "async with" in code
            has_async_def = "async def" in code or "await " in code

            if not (has_async_with or has_async_def):
                result.add_issue(
                    message="AsyncClient used without proper async context",
                    file_path=str(file_path),
                    line=start_line,
                    severity=IssueSeverity.WARNING,
                    suggestion="Use 'async with AsyncClient()' or ensure code is in async function",
                    context={"line": ""},
                )

        # Check for await without async function
        for line_offset, line in enumerate(lines):
            if "await " in line and "async def" not in code and "async with" not in line:
                result.add_issue(
                    message="await used outside async function",
                    file_path=str(file_path),
                    line=start_line + line_offset,
                    severity=IssueSeverity.ERROR,
                    suggestion="Wrap in async function or use sync Client",
                    context={"line": line.strip()},
                )