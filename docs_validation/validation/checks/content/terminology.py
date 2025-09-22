"""Terminology validation for documentation consistency."""

import re
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult


class TerminologyCheck(ContentCheck):
    """Validates consistent terminology usage in documentation."""

    def __init__(self):
        super().__init__(
            name="terminology",
            description="Validates consistent terminology usage",
            file_patterns=["**/*.md"],
        )

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check terminology consistency in content."""
        rules = self._get_terminology_rules()
        lines = content.split("\n")

        for line_number, line in enumerate(lines, 1):
            for pattern, suggestion in rules:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    result.add_issue(
                        message=suggestion,
                        file_path=str(file_path),
                        line=line_number,
                        severity=IssueSeverity.WARNING,
                        context=f"Found: '{match.group()}'",
                        suggestion=suggestion,
                    )

    def _get_terminology_rules(self) -> list[tuple[str, str]]:
        """Get terminology validation rules as (pattern, suggestion) tuples."""
        return [
            # Project naming consistency
            (r"\bfive-twenty\b", 'Use "FiveTwenty" or "fivetwenty" instead of "five-twenty"'),
            (r"\bFiveTwenty SDK\b", 'Use "FiveTwenty" instead of "FiveTwenty SDK"'),
            (r"pip install FiveTwenty", 'Use "pip install fivetwenty" (lowercase package name)'),

            # API terminology
            (r"\bOanda\b", 'Use "OANDA" (all caps) for the company name'),
            (r"\boanda\b", 'Use "OANDA" (all caps) for the company name'),
            (r"\brest api\b", 'Use "REST API" (all caps)'),
            (r"\bapi key\b", 'Use "API key" (capitalize API)'),

            # Financial terminology
            (r"\bcurrency pair\b", 'Use "instrument" for OANDA terminology consistency'),
            (r"\bfx\b", 'Use "forex" or "foreign exchange" instead of "fx"'),
            (r"\bforex pair\b", 'Use "currency instrument" or just "instrument"'),

            # Technical terminology
            (r"\basync/await\b", 'Use "async/await" with proper formatting'),
            (r"\bjson\b", 'Use "JSON" (all caps) when referring to the format'),
            (r"\bhttp\b", 'Use "HTTP" (all caps) when referring to the protocol'),
            (r"\bhttps\b", 'Use "HTTPS" (all caps) when referring to the protocol'),
            (r"\bapi\b", 'Use "API" (all caps) when referring to application programming interface'),

            # Documentation style
            (r"\be\.g\.\s", 'Use "for example" or "such as" instead of "e.g."'),
            (r"\bi\.e\.\s", 'Use "that is" or "in other words" instead of "i.e."'),
            (r"\betc\.\s", 'Use "and so on" or be more specific instead of "etc."'),

            # Code terminology
            (r"\bpython\b", 'Use "Python" (capitalize) when referring to the language'),
            (r"\bjavascript\b", 'Use "JavaScript" (proper capitalization)'),
            (r"\btypescript\b", 'Use "TypeScript" (proper capitalization)'),

            # Common misspellings
            (r"\brecieve\b", 'Use "receive" (correct spelling)'),
            (r"\boccur\b", 'Use "occur" (single "r")'),
            (r"\bseperate\b", 'Use "separate" (correct spelling)'),
            (r"\bdefinately\b", 'Use "definitely" (correct spelling)'),

            # Trading terminology
            (r"\blong position\b", 'Use "buy position" for clarity'),
            (r"\bshort position\b", 'Use "sell position" for clarity'),
            (r"\bspread\b", 'Be specific: "bid-ask spread" or "trading spread"'),
            (r"\bleverage\b", 'Use "margin trading" when referring to OANDA\'s margin system'),

            # Units and formatting
            (r"\b\d+pip\b", 'Use "pips" (plural) or "pip" with proper spacing'),
            (r"\b\d+%\b", "Add space before % symbol for readability"),
            (r"\$\d+USD\b", "Avoid redundant currency notation ($ already implies USD)"),

            # Common documentation issues
            (r"\bplease\b", 'Avoid "please" in technical documentation - be direct'),
            (r"\byou\'ll\b", 'Use "you will" instead of contractions in formal docs'),
            (r"\bcan\'t\b", 'Use "cannot" instead of contractions in formal docs'),
            (r"\bdon\'t\b", 'Use "do not" instead of contractions in formal docs'),
        ]

    def supports_file(self, file_path: Path) -> bool:
        """Check if this validator supports the given file."""
        return file_path.suffix.lower() == ".md"

    def get_check_metadata(self) -> dict[str, Any]:
        """Get metadata about this check for optimization."""
        return {
            "check_type": "io_bound",  # Text processing
            "estimated_files_per_second": 120.0,  # Very fast regex matching
            "memory_usage_mb": 3.0,
            "supports_batching": True,
            "requires_context_isolation": False,
        }
