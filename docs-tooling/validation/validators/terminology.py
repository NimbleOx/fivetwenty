"""
Terminology validation for documentation.

Validates consistent terminology usage in documentation files.
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


class TerminologyValidator(FileValidator):  # type: ignore[misc]
    """Validates terminology consistency in markdown files."""

    def __init__(self) -> None:
        super().__init__(name="terminology_validator", description="Validates consistent terminology usage", file_patterns=["docs/**/*.md", "*.md"])
        self.terminology_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate terminology in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)

        for file_path in files:
            self._check_file_terminology(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.terminology_issues) == 0 else "failed",
            issues_found=len(self.terminology_issues),
            total_checked=total_files,
            details={"terminology_issues": self.terminology_issues, "files_checked": total_files},
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _get_terminology_rules(self) -> list[tuple[str, str]]:
        """Get terminology validation rules."""
        return [
            (r"\bfive-twenty\b", 'Use "FiveTwenty" or "fivetwenty" instead of "five-twenty"'),
            (r"\bFiveTwenty SDK\b", 'Use "FiveTwenty" instead of "FiveTwenty SDK"'),
            (r"pip install FiveTwenty", 'Use "pip install fivetwenty" (lowercase package name)'),
            # Additional terminology rules can be added here
            (r"\bOANDA\s+api\b", 'Use "OANDA API" (capitalize API)'),
            (r"\bapi key\b", 'Use "API key" (capitalize API)'),
            (r"\brest api\b", 'Use "REST API" (capitalize REST API)'),
            (r"\bwebsocket\b", 'Use "WebSocket" (proper capitalization)'),
            (r"\bjson\b", 'Use "JSON" when referring to the format'),
            (r"\bhttp\b", 'Use "HTTP" when referring to the protocol'),
            (r"\bhttps\b", 'Use "HTTPS" when referring to the protocol'),
        ]

    def _check_file_terminology(self, file_path: Path) -> None:
        """Check terminology in a single file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            terminology_rules = self._get_terminology_rules()

            for pattern, message in terminology_rules:
                # For API-related patterns, use case-sensitive matching to avoid false positives
                if "api" in pattern.lower() and "API" in message:
                    matches = list(re.finditer(pattern, content))  # Case-sensitive
                else:
                    matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    # Find line number
                    line_num = content[: match.start()].count("\n") + 1
                    matched_text = match.group()

                    # Get context around the match
                    start_pos = max(0, match.start() - 20)
                    end_pos = min(len(content), match.end() + 20)
                    context = content[start_pos:end_pos].replace("\n", " ")

                    issue = {"file": str(file_path), "line": line_num, "type": "terminology_inconsistency", "message": message, "matched_text": matched_text, "context": context.strip()}
                    self.terminology_issues.append(issue)
                    self.add_issue(f"Terminology issue: {matched_text} - {message}", str(file_path), line_num)

        except Exception as e:
            issue = {"file": str(file_path), "type": "read_error", "message": f"Could not read file: {e}"}
            self.terminology_issues.append(issue)
            self.add_issue(f"Error reading file: {e}", str(file_path))
