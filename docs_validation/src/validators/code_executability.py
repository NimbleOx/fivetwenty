"""Code executability validator for testing code examples."""

import ast
import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class CodeExecutabilityValidator(BaseValidator):
    """Validates that Python code examples in documentation are executable."""

    def __init__(self) -> None:
        super().__init__(name="code_executability", description="Validates Python code examples are syntactically correct and importable")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate code executability in file content."""
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

                    # Extract language specification
                    code_block_language = stripped[3:].strip().lower()
                else:
                    # Ending a code block
                    in_code_block = False

                    # Validate the code block if it's Python
                    if code_block_language in ["python", "py", ""] and code_block_lines:
                        issues.extend(
                            self._validate_python_code(
                                code_block_lines,
                                code_block_start + 1,  # +1 because code starts after ```
                                file_info.path,
                            )
                        )

                    # Reset for next block
                    code_block_lines = []
                    code_block_language = ""
            elif in_code_block:
                # Collect code block content
                code_block_lines.append(line)

        # Check for unclosed code blocks
        if in_code_block:
            issues.append(ValidationIssue(message="Unclosed code block detected", file_path=file_info.path, line=code_block_start, severity=IssueSeverity.ERROR, rule_id="code_unclosed_block", suggestion="Add closing ``` to end the code block"))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _validate_python_code(self, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Validate Python code for syntax and basic import errors."""
        issues: list[ValidationIssue] = []

        if not code_lines or all(not line.strip() for line in code_lines):
            return issues

        code = "\n".join(code_lines)

        # Skip code blocks that are clearly examples/placeholders
        if self._is_placeholder_code(code):
            return issues

        # Check syntax
        try:
            ast.parse(code)
        except SyntaxError as e:
            error_line = start_line + (e.lineno - 1) if e.lineno else start_line
            issues.append(ValidationIssue(message=f"Python syntax error: {e.msg}", file_path=file_path, line=error_line, severity=IssueSeverity.ERROR, rule_id="code_syntax_error", context=code_lines[e.lineno - 1] if e.lineno and e.lineno <= len(code_lines) else "", suggestion="Fix the Python syntax error"))
            return issues  # Don't continue if syntax is invalid

        # Check for basic import issues
        issues.extend(self._check_imports(code, code_lines, start_line, file_path))

        # Check for undefined variables (basic check)
        issues.extend(self._check_undefined_variables(code, code_lines, start_line, file_path))

        # Check for FiveTwenty-specific async issues
        issues.extend(self._check_async_patterns(code, code_lines, start_line, file_path))

        return issues

    def _is_placeholder_code(self, code: str) -> bool:
        """Check if code is clearly a placeholder/example that shouldn't be executed."""
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
        ]

        code_lower = code.lower()
        return any(re.search(pattern, code_lower) for pattern in placeholder_patterns)

    def _check_imports(self, code: str, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Check for import-related issues."""
        issues: list[ValidationIssue] = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues  # Already handled in syntax check

        # Find all imports
        imports: list[dict[str, str | int]] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend([{"name": alias.name, "line": node.lineno, "type": "import"} for alias in node.names])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append({"name": node.module, "line": node.lineno, "type": "from_import"})

        # Check if imports are available
        for imp in imports:
            module_name = str(imp["name"]).split(".")[0]  # Get top-level module

            # Skip standard library and common packages that should be available
            if self._is_standard_or_common_module(module_name):
                continue

            # Check for FiveTwenty imports specifically
            if module_name == "fivetwenty":
                # This should be available in the project context
                continue

            # For other imports, check if they're actually importable
            try:
                __import__(module_name)
            except ImportError:
                imp_line = int(imp["line"])
                error_line = start_line + imp_line - 1
                issues.append(
                    ValidationIssue(
                        message=f"Import '{imp['name']}' may not be available",
                        file_path=file_path,
                        line=error_line,
                        severity=IssueSeverity.WARNING,
                        rule_id="code_import_unavailable",
                        context=code_lines[imp_line - 1] if imp_line <= len(code_lines) else "",
                        suggestion=f"Ensure '{module_name}' is installed or document as a requirement",
                    )
                )

        return issues

    def _check_undefined_variables(self, code: str, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Check for obviously undefined variables."""
        issues: list[ValidationIssue] = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Simple undefined variable detection
        defined_vars = set()
        used_vars = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    defined_vars.add(node.id)
                elif isinstance(node.ctx, ast.Load):
                    used_vars.add((node.id, getattr(node, "lineno", 1)))

        # Check for variables used but not defined
        undefined = []
        for var_name, line_no in used_vars:
            if var_name not in defined_vars and not self._is_builtin_or_common(var_name) and not var_name.startswith("_"):  # Skip private variables
                undefined.append((var_name, line_no))

        # Report undefined variables
        for var_name, line_no in undefined:
            error_line = start_line + line_no - 1
            issues.append(
                ValidationIssue(
                    message=f"Variable '{var_name}' may be undefined",
                    file_path=file_path,
                    line=error_line,
                    severity=IssueSeverity.WARNING,
                    rule_id="code_undefined_variable",
                    context=code_lines[line_no - 1] if line_no <= len(code_lines) else "",
                    suggestion=f"Define '{var_name}' before using it or check if it's from a previous example",
                )
            )

        return issues

    def _is_standard_or_common_module(self, module_name: str) -> bool:
        """Check if a module is from standard library or commonly available."""
        standard_modules = {
            "os",
            "sys",
            "time",
            "datetime",
            "json",
            "math",
            "random",
            "re",
            "collections",
            "itertools",
            "functools",
            "pathlib",
            "typing",
            "decimal",
            "asyncio",
            "threading",
            "queue",
            "hashlib",
            "hmac",
            "urllib",
            "http",
            "email",
            "html",
            "xml",
            "csv",
            "sqlite3",
            "logging",
            "argparse",
            "configparser",
            "tempfile",
            "shutil",
            "subprocess",
            "multiprocessing",
            "concurrent",
            "ssl",
            "socket",
            "struct",
            "binascii",
            "base64",
            "zlib",
            "gzip",
            "tarfile",
            "zipfile",
            "platform",
            "gc",
            "weakref",
            "copy",
            "pickle",
            "dataclasses",
            "enum",
            "abc",
            "contextlib",
            "warnings",
        }

        common_packages = {"numpy", "pandas", "requests", "httpx", "aiohttp", "pydantic", "pytest", "click", "rich", "tqdm", "matplotlib", "seaborn", "sklearn", "scipy", "jupyter", "IPython", "notebook", "dotenv"}

        return module_name in standard_modules or module_name in common_packages

    def _is_builtin_or_common(self, var_name: str) -> bool:
        """Check if a variable name is a builtin or commonly available."""
        # Common built-in types and functions
        common_builtins = {
            "str",
            "int",
            "float",
            "bool",
            "list",
            "dict",
            "tuple",
            "set",
            "bytes",
            "type",
            "object",
            "Exception",
            "ValueError",
            "TypeError",
            "KeyError",
            "AttributeError",
            "IndexError",
            "RuntimeError",
            "print",
            "len",
            "range",
            "enumerate",
            "zip",
            "map",
            "filter",
            "sorted",
            "reversed",
            "sum",
            "min",
            "max",
            "abs",
            "round",
            "open",
            "input",
            "format",
        }

        # Common variable names in examples
        common_vars = {
            "self",
            "cls",
            "args",
            "kwargs",
            "client",
            "config",
            "response",
            "data",
            "account",
            "accounts",
            "order",
            "orders",
            "position",
            "positions",
            "price",
            "prices",
            "instrument",
            "instruments",
            "trade",
            "trades",
            "token",
            "account_id",
            "api_key",
            "username",
            "password",
            "key",
            "value",
            "result",
            "results",
            "error",
            "exception",
            "message",
            "service_name",
            "service",
            "name",
            "url",
            "path",
            "file_path",
        }

        return var_name in dir(__builtins__) or var_name in common_builtins or var_name in common_vars

    def _check_async_patterns(self, code: str, code_lines: list[str], start_line: int, file_path: Path) -> list[ValidationIssue]:
        """Check for FiveTwenty-specific async/await pattern issues."""
        issues: list[ValidationIssue] = []

        try:
            tree = ast.parse(code)
        except SyntaxError:
            return issues

        # Track async context and function definitions
        has_async_with = False
        has_await = False
        has_async_function = False
        has_asyncio_run = False

        # Check for specific patterns
        for node in ast.walk(tree):
            # Check for async with statements
            if isinstance(node, ast.AsyncWith):
                has_async_with = True
                # Check if it's AsyncClient usage
                for item in node.items:
                    if isinstance(item.context_expr, ast.Call):
                        if isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == "AsyncClient":
                            # Found AsyncClient usage - check if we're in async function
                            pass

            # Check for await expressions
            elif isinstance(node, ast.Await):
                has_await = True

            # Check for async function definitions
            elif isinstance(node, ast.AsyncFunctionDef):
                has_async_function = True

            # Check for asyncio.run calls
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "asyncio" and node.func.attr == "run":
                        has_asyncio_run = True

        # Issue: async with or await without async function context
        if (has_async_with or has_await) and not has_async_function and not has_asyncio_run:
            # Find the line with async with or await
            for line_num, line in enumerate(code_lines, 1):
                if "async with" in line or "await " in line:
                    error_line = start_line + line_num - 1
                    issues.append(
                        ValidationIssue(
                            message="'async with' or 'await' found outside async function", file_path=file_path, line=error_line, severity=IssueSeverity.ERROR, rule_id="code_async_outside_function", context=line.strip(), suggestion="Wrap async code in 'async def main():' function and call with 'asyncio.run(main())'"
                        )
                    )
                    break

        # Issue: AsyncClient without account_id when providing token
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "AsyncClient":
                has_token = False
                has_account_id = False
                has_config = False

                # Check arguments
                for keyword in node.keywords:
                    if keyword.arg == "token":
                        has_token = True
                    elif keyword.arg == "account_id":
                        has_account_id = True
                    elif keyword.arg == "config":
                        has_config = True

                # If providing token directly but no account_id or config, warn
                if has_token and not has_account_id and not has_config:
                    # Find line number for this call
                    for line_num, line in enumerate(code_lines, 1):
                        if "AsyncClient(" in line and "token=" in line:
                            error_line = start_line + line_num - 1
                            issues.append(
                                ValidationIssue(
                                    message="AsyncClient with token parameter requires account_id parameter", file_path=file_path, line=error_line, severity=IssueSeverity.ERROR, rule_id="code_missing_account_id", context=line.strip(), suggestion="Add account_id='your-account-id' parameter to AsyncClient call"
                                )
                            )
                            break

        return issues

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
