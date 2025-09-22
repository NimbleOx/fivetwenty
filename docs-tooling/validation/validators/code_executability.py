#!/usr/bin/env python3
"""
Code Executability Validator

Validates that code examples in tutorials are actually executable and don't contain
undefined functions, missing imports, or syntax errors that would prevent running.
Based on lessons learned from fixing 169 validation issues in tutorials.
"""

import ast
import re
from pathlib import Path
from typing import Any

from core.base import BaseValidator, ValidationResult


class CodeExecutabilityValidator(BaseValidator):
    """Validate that tutorial code examples are executable."""

    def __init__(self):
        super().__init__("code_executability", "Validates that code examples are executable and complete")
        self.validator_name = "code_executability"
        self.file_patterns = ["docs/tutorials/**/*.md"]
        self.executability_issues: list[dict[str, Any]] = []

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
            "OrderType": "from fivetwenty.models import OrderType"
        }

        # Exception imports
        self.exception_imports = {
            "FiveTwentyError": "from fivetwenty.exceptions import FiveTwentyError",
            "FiveTwentyErrorCode": "from fivetwenty.exceptions import FiveTwentyErrorCode"
        }

    def validate(self) -> ValidationResult:
        """Run code executability validation."""
        tutorial_files = self._find_tutorial_files()
        total_checked = 0

        for file_path in tutorial_files:
            file_issues, blocks_checked = self._validate_file_executability(file_path)
            self.executability_issues.extend(file_issues)
            total_checked += blocks_checked

        status = "passed" if len(self.executability_issues) == 0 else "failed"

        return ValidationResult(
            validator_name=self.validator_name,
            status=status,
            issues_found=len(self.executability_issues),
            total_checked=total_checked,
            details={
                "files_checked": len(tutorial_files),
                "code_blocks_checked": total_checked,
                "executability_issues": self.executability_issues,
                "validation_focus": "Code example executability and completeness"
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _find_tutorial_files(self) -> list[Path]:
        """Find all tutorial files to validate."""
        tutorial_files = []

        for pattern in self.file_patterns:
            tutorial_files.extend(Path().glob(pattern))

        return [f for f in tutorial_files if f.is_file()]

    def _validate_file_executability(self, file_path: Path) -> tuple[list[dict[str, Any]], int]:
        """Validate executability of code blocks in a single file."""
        issues = []
        blocks_checked = 0

        try:
            content = file_path.read_text(encoding='utf-8')

            # Skip index files
            if file_path.name == "index.md":
                return [], 0

            # Extract all Python code blocks
            code_blocks = self._extract_code_blocks(content)
            blocks_checked = len(code_blocks)

            for block_num, (code, line_start) in enumerate(code_blocks, 1):
                # Skip obvious placeholder examples
                if self._is_placeholder_example(code):
                    continue

                # Check syntax
                syntax_issues = self._check_syntax(code, block_num, line_start)
                issues.extend(syntax_issues)

                # Check for undefined functions/variables
                undefined_issues = self._check_undefined_references(code, block_num, line_start)
                issues.extend(undefined_issues)

                # Check import completeness
                import_issues = self._check_import_completeness(code, block_num, line_start)
                issues.extend(import_issues)

                # Check for async/await consistency
                async_issues = self._check_async_consistency(code, block_num, line_start)
                issues.extend(async_issues)

            # Add file path context to all issues
            for issue in issues:
                issue["file"] = str(file_path)

        except Exception as e:
            issues.append({
                "type": "file_error",
                "severity": "error",
                "message": f"Could not validate code executability: {e}",
                "file": str(file_path)
            })

        return issues, blocks_checked

    def _extract_code_blocks(self, content: str) -> list[tuple[str, int]]:
        """Extract Python code blocks with line numbers."""
        blocks = []
        lines = content.split('\n')
        in_python_block = False
        current_block = []
        block_start_line = 0
        indent_level = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Handle indented code blocks (within admonitions)
            if stripped.startswith('```python'):
                in_python_block = True
                current_block = []
                block_start_line = line_num + 1
                indent_level = len(line) - len(line.lstrip())
            elif stripped == '```' and in_python_block:
                if current_block:
                    # Clean up indentation from admonition blocks
                    cleaned_block = self._clean_indentation(current_block, indent_level)
                    blocks.append(('\n'.join(cleaned_block), block_start_line))
                in_python_block = False
            elif in_python_block:
                current_block.append(line)

        return blocks

    def _clean_indentation(self, lines: list[str], base_indent: int) -> list[str]:
        """Clean up indentation from markdown admonition blocks."""
        cleaned = []
        for line in lines:
            if line.strip():  # Non-empty line
                # Remove base indentation from admonition
                if len(line) >= base_indent and line[:base_indent].isspace():
                    cleaned.append(line[base_indent:])
                else:
                    cleaned.append(line)
            else:
                cleaned.append("")
        return cleaned

    def _is_placeholder_example(self, code: str) -> bool:
        """Check if code block is a placeholder/incomplete example."""
        for pattern in self.placeholder_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return True

        # Very short examples (likely incomplete)
        return len(code.strip()) < 10

    def _check_syntax(self, code: str, block_num: int, line_start: int) -> list[dict[str, Any]]:
        """Check Python syntax."""
        issues = []

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "error",
                "message": f"Syntax error in code block {block_num}: {e.msg}",
                "suggestion": f"Fix syntax error at line {e.lineno}: {e.text}",
                "line": line_start + (e.lineno or 1) - 1,
                "block": block_num
            })
        except Exception as e:
            issues.append({
                "type": "parse_error",
                "severity": "error",
                "message": f"Could not parse code block {block_num}: {e}",
                "line": line_start,
                "block": block_num
            })

        return issues

    def _check_undefined_references(self, code: str, block_num: int, line_start: int) -> list[dict[str, Any]]:
        """Check for undefined functions and variables."""
        issues = []

        try:
            tree = ast.parse(code)

            # Extract defined names (functions, variables, imports)
            defined_names: set[str] = set()
            used_names: set[str] = set()

            for node in ast.walk(tree):
                # Track definitions
                if isinstance(node, ast.FunctionDef | ast.ClassDef):
                    defined_names.add(node.name)
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)
                elif isinstance(node, ast.Import | ast.ImportFrom):
                    for alias in node.names:
                        defined_names.add(alias.asname or alias.name)

                # Track usage
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    used_names.add(node.func.id)

            # Built-in names that are always available
            builtins = {"print", "len", "str", "int", "float", "list", "dict", "set",
                       "range", "enumerate", "zip", "any", "all", "min", "max",
                       "abs", "round", "sum", "sorted", "open", "type", "isinstance"}

            # Check for undefined references
            undefined = used_names - defined_names - builtins

            # Filter out known patterns that are likely OK
            filtered_undefined = set()
            for name in undefined:
                # Skip single letters (often used as variables)
                if len(name) == 1:
                    continue
                # Skip common variable names that might be defined elsewhere
                if name in {"account_id", "instrument", "units", "client", "response", "account"}:
                    continue
                # Skip method calls on objects (we can't easily track those)
                if "." in name:
                    continue

                filtered_undefined.add(name)

            if filtered_undefined:
                issues.append({
                    "type": "undefined_references",
                    "severity": "warning",
                    "message": f"Code block {block_num} references undefined names: {', '.join(sorted(filtered_undefined))}",
                    "suggestion": "Ensure all variables and functions are defined or imported",
                    "line": line_start,
                    "block": block_num
                })

        except Exception:
            # If AST parsing fails, we already caught it in syntax check
            pass

        return issues

    def _check_import_completeness(self, code: str, block_num: int, line_start: int) -> list[dict[str, Any]]:
        """Check that all required imports are present."""
        issues = []

        # Combine all import mappings
        all_imports = {**self.required_imports, **self.model_imports, **self.exception_imports}

        for pattern, required_import in all_imports.items():
            if re.search(rf'\b{re.escape(pattern)}\b', code) and required_import not in code:
                # Skip if this looks like an import example or comment
                if any(marker in code.lower() for marker in ["# import", "importing", "import example"]):
                    continue

                issues.append({
                    "type": "missing_import",
                    "severity": "error",
                    "message": f"Code block {block_num} uses '{pattern}' without importing it",
                    "suggestion": f"Add: {required_import}",
                    "line": line_start,
                    "block": block_num
                })

        return issues

    def _check_async_consistency(self, code: str, block_num: int, line_start: int) -> list[dict[str, Any]]:
        """Check async/await consistency."""
        issues = []

        has_async_def = bool(re.search(r'\basync\s+def\b', code))
        has_await = bool(re.search(r'\bawait\b', code))
        has_async_client = bool(re.search(r'\bAsyncClient\b', code))

        # If using AsyncClient, should have await
        if has_async_client and not has_await:
            issues.append({
                "type": "missing_await",
                "severity": "warning",
                "message": f"Code block {block_num} uses AsyncClient but lacks await keywords",
                "suggestion": "Add await before async client method calls",
                "line": line_start,
                "block": block_num
            })

        # If has await but no async def, might be incomplete
        if has_await and not has_async_def and "async def" not in code.lower():
            issues.append({
                "type": "await_without_async",
                "severity": "info",
                "message": f"Code block {block_num} uses await but doesn't define async function",
                "suggestion": "Ensure code is within an async function context",
                "line": line_start,
                "block": block_num
            })

        return issues

    def _log_issues(self, file_path: Path, issues: list[dict[str, Any]]):
        """Log issues found in a file."""
        if not issues:
            return

        print(f"\n🔧 Code Executability Issues in {file_path}:")
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            message = issue.get('message', 'No message')
            suggestion = issue.get('suggestion', '')

            severity_icon = {"error": "❌", "warning": "⚠️", "info": "💡"}.get(severity, "•")
            print(f"  {severity_icon} {issue.get('type', 'unknown')}: {message}")
            if suggestion:
                print(f"      💡 {suggestion}")
            if 'line' in issue and 'block' in issue:
                print(f"      📍 Line {issue['line']}, Block {issue['block']}")
