"""Terminology validation for documentation consistency."""

import re
from pathlib import Path
from typing import Any

from validation.checks.base import ContentCheck
from validation.core.context import ValidationContext
from validation.core.results import IssueSeverity, ValidationResult


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
            # Project naming consistency - ESSENTIAL
            (r"\bfive-twenty\b", 'Use "FiveTwenty" or "fivetwenty" instead of "five-twenty"'),
            (r"pip install FiveTwenty", 'Use "pip install fivetwenty" (lowercase package name)'),

            # Company names - ESSENTIAL
            (r"\bOanda\b", 'Use "OANDA" (all caps) for the company name'),
            (r"\boanda\b", 'Use "OANDA" (all caps) for the company name'),

            # Language names - IMPORTANT (but not in commands or code blocks)
            (r"(?<!```)\bpython\b(?!\s*-m)(?!\s*cli\.py)(?!\s*```)", 'Use "Python" (capitalize) when referring to the language'),
            (r"\bjavascript\b", 'Use "JavaScript" (proper capitalization)'),
            (r"\btypescript\b", 'Use "TypeScript" (proper capitalization)'),

            # Common misspellings - HELPFUL
            (r"\brecieve\b", 'Use "receive" (correct spelling)'),
            (r"\bseperate\b", 'Use "separate" (correct spelling)'),
            (r"\bdefinately\b", 'Use "definitely" (correct spelling)'),

            # Technical acronyms - MODERATE VALUE
            (r"\bapi\b", 'Use "API" (all caps) when referring to application programming interface'),
            (r"\bjson\b", 'Use "JSON" (all caps) when referring to the format'),
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
