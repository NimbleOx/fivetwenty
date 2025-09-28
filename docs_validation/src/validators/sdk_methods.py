"""SDK methods validator for API documentation completeness."""

import ast
import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class SDKMethodsValidator(BaseValidator):
    """Validates SDK API documentation completeness."""

    def __init__(self) -> None:
        super().__init__(name="sdk_methods", description="Validates SDK API documentation completeness")
        # Cache of SDK methods discovered from source code
        self._sdk_methods: dict[str, set[str]] = {}
        self._discovered_methods = False

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files and Python SDK files."""
        return file_path.suffix.lower() in {".md", ".markdown", ".py"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate SDK methods documentation in file content."""
        issues: list[ValidationIssue] = []

        # First discover SDK methods if not already done
        if not self._discovered_methods:
            self._discover_sdk_methods(file_info.path)

        if file_info.path.suffix.lower() in {".md", ".markdown"}:
            # Validate markdown documentation
            issues.extend(self._check_markdown_documentation(file_info.path, content))
        elif file_info.path.suffix == ".py":
            # Skip Python files for now (could validate docstrings in future)
            pass

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _discover_sdk_methods(self, current_file: Path) -> None:
        """Discover SDK methods from the source code."""
        # Find the project root by looking for fivetwenty package
        project_root = self._find_project_root(current_file)
        sdk_root = project_root / "fivetwenty"

        if not sdk_root.exists():
            self._discovered_methods = True
            return

        # Discover methods from endpoint files
        endpoints_dir = sdk_root / "endpoints"
        if endpoints_dir.exists():
            for py_file in endpoints_dir.glob("*.py"):
                if py_file.name == "__init__.py":
                    continue

                try:
                    with py_file.open("r", encoding="utf-8") as f:
                        source = f.read()

                    # Parse the Python file to extract class and method information
                    tree = ast.parse(source)
                    endpoint_name = py_file.stem

                    methods = set()
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef) and node.name.endswith("Endpoints"):
                            for item in node.body:
                                if (isinstance(item, ast.AsyncFunctionDef) and not item.name.startswith("_")) or (isinstance(item, ast.FunctionDef) and not item.name.startswith("_")):
                                    methods.add(item.name)

                    if methods:
                        self._sdk_methods[endpoint_name] = methods

                except Exception:
                    # Skip files that can't be parsed
                    continue

        self._discovered_methods = True

    def _check_markdown_documentation(self, file_path: Path, content: str) -> list[ValidationIssue]:
        """Check if markdown files properly document SDK methods."""
        issues: list[ValidationIssue] = []

        if not self._sdk_methods:
            return issues

        lines = content.split("\n")

        # Track which SDK methods are mentioned in this file
        mentioned_methods: dict[str, set[str]] = {}
        method_references: dict[str, list[int]] = {}

        for line_num, line in enumerate(lines, 1):
            # Look for SDK method references like client.accounts.get_accounts()
            sdk_pattern = r"client\.(\w+)\.(\w+)\s*\("
            matches = re.finditer(sdk_pattern, line)

            for match in matches:
                endpoint, method = match.groups()

                if endpoint not in mentioned_methods:
                    mentioned_methods[endpoint] = set()
                mentioned_methods[endpoint].add(method)

                # Track line numbers for method references
                ref_key = f"{endpoint}.{method}"
                if ref_key not in method_references:
                    method_references[ref_key] = []
                method_references[ref_key].append(line_num)

        # Check for undocumented methods (only in API reference files)
        if self._is_api_reference_file(file_path):
            for endpoint, methods in self._sdk_methods.items():
                documented_methods = mentioned_methods.get(endpoint, set())
                undocumented = methods - documented_methods

                issues.extend(
                    [
                        ValidationIssue(
                            message=f"SDK method '{endpoint}.{method}' is not documented",
                            file_path=file_path,
                            line=1,  # Place at top of file since we don't know where it should be
                            severity=IssueSeverity.WARNING,
                            rule_id="sdk_undocumented_method",
                            suggestion=f"Add documentation for {endpoint}.{method}() method",
                        )
                        for method in undocumented
                    ]
                )

        # Check for outdated method references
        for endpoint, methods in mentioned_methods.items():
            if endpoint in self._sdk_methods:
                available_methods = self._sdk_methods[endpoint]
                invalid_methods = methods - available_methods

                for method in invalid_methods:
                    ref_key = f"{endpoint}.{method}"
                    line_numbers = method_references.get(ref_key, [1])

                    issues.extend(
                        [
                            ValidationIssue(
                                message=f"Reference to non-existent SDK method '{endpoint}.{method}'",
                                file_path=file_path,
                                line=line_num,
                                severity=IssueSeverity.ERROR,
                                rule_id="sdk_invalid_method_reference",
                                context=lines[line_num - 1] if line_num <= len(lines) else "",
                                suggestion=f"Check if method name is correct or if it has been renamed. Available methods: {', '.join(sorted(available_methods))}",
                            )
                            for line_num in line_numbers
                        ]
                    )

        return issues

    def _is_api_reference_file(self, file_path: Path) -> bool:
        """Check if this file should document SDK methods comprehensively."""
        path_str = str(file_path).lower()
        # Only files specifically named as comprehensive API references
        # Exclude client.md as it's a navigation file, not comprehensive docs
        return any(indicator in path_str for indicator in ["reference/complete-api.md", "api/full-reference.md"])

    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root directory."""
        current = file_path.parent if file_path.is_file() else file_path

        while current != current.parent:
            # Check for common project root indicators
            if any((current / indicator).exists() for indicator in ["pyproject.toml", "setup.py", ".git", "fivetwenty"]):
                return current
            current = current.parent

        # Fallback to current working directory
        return Path.cwd()

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown", "fivetwenty/**/*.py"]
