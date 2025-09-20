"""
SDK Method validation for documentation.

Validates that documentation examples use current SDK method names
and not deprecated method names.
"""

import re
import sys
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class SDKMethodValidator(FileValidator):  # type: ignore[misc]
    """Validates SDK method usage in documentation."""

    def __init__(self) -> None:
        super().__init__(name="sdk_method_validator", description="Validates current SDK method names in documentation", file_patterns=["docs/**/*.md", "*.md"])
        self.method_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate SDK method usage in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)

        for file_path in files:
            self._check_file_methods(file_path)

        # Print detailed results for debugging
        self.print_detailed_results()

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.method_issues) == 0 else "failed",
            issues_found=len(self.method_issues),
            total_checked=total_files,
            details={"method_issues": self.method_issues, "files_checked": total_files},
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _get_deprecated_method_rules(self) -> list[tuple[str, str, str]]:
        """Get deprecated method validation rules.

        Returns tuples of (pattern, replacement, category).
        """
        return [
            # Order methods
            (r"\.orders\.create_market\(", ".orders.post_market_order(", "orders"),
            (r"\.orders\.create_limit\(", ".orders.post_limit_order(", "orders"),
            (r"\.orders\.create_stop\(", ".orders.post_stop_order(", "orders"),
            (r"create_market_order\(", "post_market_order(", "orders"),
            (r"create_limit_order\(", "post_limit_order(", "orders"),
            (r"create_stop_order\(", "post_stop_order(", "orders"),
            # Potential trade method patterns (if they exist)
            (r"\.trades\.create_trade\(", ".trades.post_trade(", "trades"),
            # Position method patterns (if they exist)
            (r"\.positions\.create_position\(", ".positions.post_position(", "positions"),
            # Generic create patterns that should be post
            (r"client\.(\w+)\.create_(\w+)\(", r"client.\1.post_\2(", "generic"),
            # Error code patterns - CRITICAL ISSUE FROM EXPLANATION DOCS
            (r"\bErrorCode\b(?!\.)", "FiveTwentyErrorCode", "error_codes"),
            # Placeholder function patterns from explanation docs
            (r"refresh_token\(\)", "# Implementation needed: token refresh logic", "placeholders"),
            (r"notify_operations_team\(", "# Implementation needed: notification logic", "placeholders"),
            (r"undefined_function\(", "# Implementation needed", "placeholders"),
        ]

    def _get_missing_method_patterns(self) -> list[tuple[str, str, str]]:
        """Get patterns for methods that should exist but might be missing.

        Returns tuples of (pattern, suggestion, category).
        """
        return [
            # Check for potential typos in method names
            (r"\.orders\.post_market_oder\(", ".orders.post_market_order(", "typos"),
            (r"\.orders\.postmarket_order\(", ".orders.post_market_order(", "typos"),
            (r"\.orders\.post_limit_oder\(", ".orders.post_limit_order(", "typos"),
            (r"\.orders\.post_stop_oder\(", ".orders.post_stop_order(", "typos"),
        ]

    def _get_type_inconsistency_patterns(self) -> list[tuple[str, str, str]]:
        """Get patterns for type inconsistencies.

        Returns tuples of (pattern, suggestion, category).
        """
        return [
            # Float vs Decimal usage
            (r"float\(\s*\d+\.?\d*\s*\)", "Decimal('...')", "types"),
            (r"price\s*=\s*\d+\.\d+\s*#.*price", "price = Decimal('...')", "types"),
            (r"amount\s*=\s*\d+\.\d+", "amount = Decimal('...')", "types"),
            (r"spread\s*=\s*\d+\.\d+", "spread = Decimal('...')", "types"),
            (r"balance\s*=\s*\d+\.\d+", "balance = Decimal('...')", "types"),
            # Missing import patterns from explanation docs
            (r"os\.environ\[", "Missing 'import os'", "missing_imports"),
            (r"Decimal\(", "Missing 'from decimal import Decimal'", "missing_imports"),
            (r"FiveTwentyErrorCode\.", "Missing 'from fivetwenty.exceptions import FiveTwentyErrorCode'", "missing_imports"),
            # Import statements
            (r"from\s+decimal\s+import\s+Decimal", "", "imports_good"),  # This is correct
        ]

    def _check_file_methods(self, file_path: Path) -> None:
        """Check SDK method usage in a single file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Skip if this is not a code-containing file
            if "```python" not in content and "```" not in content:
                return

            # Check deprecated methods
            deprecated_rules = self._get_deprecated_method_rules()
            for pattern, replacement, category in deprecated_rules:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    self._add_method_issue(file_path=file_path, content=content, match=match, issue_type="deprecated_method", pattern=pattern, replacement=replacement, category=category)

            # Check missing methods / typos
            missing_rules = self._get_missing_method_patterns()
            for pattern, suggestion, category in missing_rules:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    self._add_method_issue(file_path=file_path, content=content, match=match, issue_type="method_typo", pattern=pattern, replacement=suggestion, category=category)

            # Check type inconsistencies
            type_rules = self._get_type_inconsistency_patterns()
            for pattern, suggestion, category in type_rules:
                if category == "imports_good":
                    continue  # Skip patterns that are actually correct

                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    self._add_method_issue(file_path=file_path, content=content, match=match, issue_type="type_inconsistency", pattern=pattern, replacement=suggestion, category=category)

        except Exception as e:
            self.method_issues.append({"file": str(file_path), "error": f"Failed to check file: {e}", "type": "file_error"})

    def print_detailed_results(self) -> None:
        """Print detailed results to console for debugging."""
        if not self.method_issues:
            print("✅ No SDK method issues found!")
            return

        print(f"\n🔍 DETAILED SDK METHOD VALIDATION RESULTS ({len(self.method_issues)} issues)")
        print("=" * 80)

        by_category = {}
        for issue in self.method_issues:
            category = issue.get("category", "unknown")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(issue)

        for category, issues in by_category.items():
            print(f"\n📂 {category.upper()} ({len(issues)} issues):")
            for issue in issues:
                file_path = issue["file"]
                line = issue.get("line", "?")
                matched_text = issue.get("matched_text", "")
                replacement = issue.get("replacement", "")
                context = issue.get("context", "")

                print(f"  📄 {file_path}:{line}")
                print(f"     ❌ Found: {matched_text}")
                print(f"     ✅ Should be: {replacement}")
                if context:
                    print(f"     📝 Context: {context}")
                print()

    def _add_method_issue(self, file_path: Path, content: str, match: re.Match[str], issue_type: str, pattern: str, replacement: str, category: str) -> None:
        """Add a method issue to the results."""
        # Find line number
        line_num = content[: match.start()].count("\n") + 1
        matched_text = match.group()

        # Get context around the match
        start_pos = max(0, match.start() - 30)
        end_pos = min(len(content), match.end() + 30)
        context = content[start_pos:end_pos].replace("\n", " ")

        self.method_issues.append(
            {"file": str(file_path.relative_to(Path.cwd())), "line": line_num, "issue_type": issue_type, "category": category, "matched_text": matched_text, "pattern": pattern, "replacement": replacement, "context": context.strip(), "severity": "critical" if issue_type == "deprecated_method" else "warning"}
        )
