"""Financial precision validation checks."""

import re
from pathlib import Path

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult


class FinancialPrecisionCheck(ContentCheck):
    """Check for proper financial precision in documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="financial_precision",
            description="Validates financial examples use Decimal instead of float",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

        # Patterns for financial contexts
        self.financial_contexts = [
            "price", "amount", "balance", "stop_loss", "take_profit",
            "daily_loss_limit", "spread", "margin", "units", "quantity",
            "cost", "fee", "commission", "profit", "loss",
        ]

        # Pattern for detecting float usage in financial contexts
        self.float_patterns = [
            # Variable assignment: price = 1.23
            r'({contexts})\s*=\s*(\d+\.\d+)(?!["\'])',
            # Function calls: set_price(1.23)
            r'(?:set_|get_|calculate_)?({contexts})\s*\(\s*(\d+\.\d+)(?!["\'])',
            # Mathematical operations: price * 1.5
            r'({contexts})\s*[*/+-]\s*(\d+\.\d+)(?!["\'])',
        ]

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check content for financial precision issues."""
        lines = content.split("\n")

        # Check each line in code blocks
        in_code_block = False
        code_language = ""

        for line_num, line in enumerate(lines, 1):
            # Track code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    in_code_block = False
                    code_language = ""
                else:
                    in_code_block = True
                    # Extract language
                    lang_match = re.match(r"```(\w+)", line.strip())
                    code_language = lang_match.group(1) if lang_match else ""
                continue

            # Only check Python code blocks
            if in_code_block and code_language == "python":
                self._check_line_for_float_usage(file_path, line, line_num, result)

    def _check_line_for_float_usage(
        self,
        file_path: Path,
        line: str,
        line_num: int,
        result: ValidationResult,
    ) -> None:
        """Check a single line for problematic float usage."""
        contexts_pattern = "|".join(self.financial_contexts)

        for pattern_template in self.float_patterns:
            pattern = pattern_template.format(contexts=contexts_pattern)

            for match in re.finditer(pattern, line, re.IGNORECASE):
                financial_term = match.group(1)
                float_value = match.group(2)

                # Skip if it's already in a string or Decimal call
                if self._is_safe_usage(line, match):
                    continue

                suggestion = self._generate_decimal_suggestion(line, match, float_value)

                result.add_issue(
                    message=f"Use Decimal instead of float for financial value: {financial_term} = {float_value}",
                    file_path=str(file_path),
                    line=line_num,
                    severity=IssueSeverity.ERROR,
                    rule="financial_precision",
                    suggestion=suggestion,
                    context={
                        "financial_term": financial_term,
                        "float_value": float_value,
                        "line_content": line.strip(),
                    },
                )

    def _is_safe_usage(self, line: str, match: re.Match) -> bool:
        """Check if the float usage is already safe (in string, Decimal, etc.)."""
        start, end = match.span()

        # Check if inside quotes
        before_match = line[:start]
        in_string = (before_match.count('"') % 2 == 1) or (before_match.count("'") % 2 == 1)

        # Check if already using Decimal
        if "Decimal(" in line:
            return True

        # Check if in a comment
        if "#" in before_match:
            return True

        return in_string

    def _generate_decimal_suggestion(self, line: str, match: re.Match, float_value: str) -> str:
        """Generate a suggestion for fixing the float usage."""
        # Replace the float value with Decimal version
        start, end = match.span()
        before = line[:start]
        after = line[end:]

        # Find the float value in the match and replace it
        match_text = match.group(0)
        decimal_version = match_text.replace(float_value, f'Decimal("{float_value}")')

        suggestion = before + decimal_version + after

        # Add import suggestion if not present
        if "from decimal import Decimal" not in line:
            suggestion = "from decimal import Decimal\n" + suggestion

        return suggestion.strip()


class FinancialTerminologyCheck(ContentCheck):
    """Check for consistent financial terminology."""

    def __init__(self) -> None:
        super().__init__(
            name="financial_terminology",
            description="Validates consistent financial terminology usage",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

        # Preferred terms (preferred -> [deprecated alternatives])
        self.terminology_rules = {
            "spread": ["bid-ask spread", "bid/ask spread"],
            "position": ["trade position", "open position"],
            "pip": ["point", "basis point"],
            "currency pair": ["forex pair", "FX pair"],
            "base currency": ["primary currency", "first currency"],
            "quote currency": ["counter currency", "second currency"],
            "stop loss": ["stop-loss", "stoploss", "stop_loss"],
            "take profit": ["take-profit", "takeprofit", "take_profit"],
            "market order": ["market_order", "marketorder"],
            "limit order": ["limit_order", "limitorder"],
        }

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check content for terminology consistency."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()

            for preferred_term, alternatives in self.terminology_rules.items():
                for alternative in alternatives:
                    if alternative.lower() in line_lower:
                        # Make sure it's a whole word match
                        if re.search(rf"\b{re.escape(alternative.lower())}\b", line_lower):
                            result.add_issue(
                                message=f"Use '{preferred_term}' instead of '{alternative}'",
                                file_path=str(file_path),
                                line=line_num,
                                severity=IssueSeverity.WARNING,
                                rule="financial_terminology",
                                suggestion=f"Replace '{alternative}' with '{preferred_term}'",
                                context={
                                    "preferred_term": preferred_term,
                                    "found_term": alternative,
                                    "line_content": line.strip(),
                                },
                            )
