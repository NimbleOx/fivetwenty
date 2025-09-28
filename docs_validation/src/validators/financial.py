"""Financial precision validator for trading documentation."""

import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class FinancialPrecisionValidator(BaseValidator):
    """Validates proper use of Decimal types and financial precision in code examples."""

    def __init__(self) -> None:
        super().__init__(name="financial_precision", description="Validates financial values use Decimal type and proper precision")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown and Python files."""
        return file_path.suffix.lower() in {".md", ".py"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate financial precision in file content."""
        issues: list[ValidationIssue] = []
        # Always use strict mode for financial precision validation

        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Check for float usage with financial values
            issues.extend(self._check_float_usage(line, line_num, file_info.path))

            # Check for hardcoded financial values
            issues.extend(self._check_hardcoded_values(line, line_num, file_info.path))

            # Check for proper Decimal imports
            if "from decimal import Decimal" in line or "import decimal" in line:
                # This is good - no issue
                pass

        # Check for missing Decimal imports in Python files
        if file_info.path.suffix == ".py":
            if any("float" in line and ("price" in line.lower() or "amount" in line.lower()) for line in lines):
                if not any("decimal" in line.lower() for line in lines):
                    issues.append(ValidationIssue(message="File uses float for financial values but doesn't import Decimal", file_path=file_info.path, severity=IssueSeverity.ERROR, rule_id="financial_precision_import", suggestion="Add 'from decimal import Decimal' and use Decimal instead of float"))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _check_float_usage(self, line: str, line_num: int, file_path: Path) -> list[ValidationIssue]:
        """Check for problematic float usage with financial terms."""
        issues: list[ValidationIssue] = []

        # Patterns that suggest financial float usage
        financial_float_patterns = [
            r"float\s*\(\s*[^)]*(?:price|amount|balance|cost|fee|commission|profit|loss|pnl)\s*\)",
            r"(?:price|amount|balance|cost|fee|commission|profit|loss|pnl)\s*=\s*float\s*\(",
            r"(?:price|amount|balance|cost|fee|commission|profit|loss|pnl)\s*:\s*float",
        ]

        issues.extend(
            [
                ValidationIssue(message="Use Decimal instead of float for financial calculations", file_path=file_path, line=line_num, severity=IssueSeverity.ERROR, rule_id="financial_precision_float", context=line.strip(), suggestion="Replace float with Decimal from the decimal module")
                for pattern in financial_float_patterns
                if re.search(pattern, line, re.IGNORECASE)
            ]
        )

        return issues

    def _check_hardcoded_values(self, line: str, line_num: int, file_path: Path) -> list[ValidationIssue]:
        """Check for hardcoded financial values that should be configurable - always use strict mode."""
        issues: list[ValidationIssue] = []

        # Always flag hardcoded monetary values in strict mode
        # Look for hardcoded monetary values (but allow common examples)
        monetary_pattern = r"(?:price|amount|balance|cost|fee)\s*=\s*(\d+\.\d{5,}|\d{4,}\.?\d*)"
        matches = re.finditer(monetary_pattern, line, re.IGNORECASE)

        for match in matches:
            value = match.group(1)
            # Allow common example values
            if value not in {"1.23456", "1000.0", "100.0", "10.0", "1.0"}:
                issues.append(
                    ValidationIssue(
                        message=f"Hardcoded financial value '{value}' should be configurable or use example values",
                        file_path=file_path,
                        line=line_num,
                        severity=IssueSeverity.WARNING,
                        rule_id="financial_precision_hardcoded",
                        context=line.strip(),
                        suggestion="Use configurable values or standard example amounts like 1000.0",
                    )
                )

        return issues

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.py"]
