"""Security validator for detecting exposed secrets and credentials."""

import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class SecurityValidator(BaseValidator):
    """Validates that no secrets, tokens, or credentials are exposed in documentation."""

    def __init__(self) -> None:
        super().__init__(name="security", description="Scans for exposed API tokens, secrets, and credentials")

        # Common patterns for detecting secrets
        self.secret_patterns = [
            # OANDA tokens
            (r"v20-[a-zA-Z0-9]{32,}", "OANDA v20 API token"),
            (r'oanda[_-]?(?:token|key|secret)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "OANDA API credential"),
            # Generic API tokens
            (r'(?:api[_-]?key|token|secret|password)["\']?\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', "API credential"),
            # Common token prefixes
            (r"sk_[a-zA-Z0-9]{20,}", "Secret key (Stripe-like)"),
            (r"pk_[a-zA-Z0-9]{20,}", "Public key (Stripe-like)"),
            # JWT tokens
            (r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*", "JWT token"),
            # Generic long alphanumeric strings that might be tokens
            (r"[a-zA-Z0-9]{32,}", "Potential token (long alphanumeric string)"),
        ]

        # Patterns to exclude (known safe examples)
        self.exclude_patterns = [
            r"example[_-]?(?:token|key|secret)",
            r"your[_-]?(?:token|key|secret)",
            r"demo[_-]?(?:token|key|secret)",
            r"test[_-]?(?:token|key|secret)",
            r"sample[_-]?(?:token|key|secret)",
            r"placeholder",
            r"abc123",
            r"def456",
            r"xyz789",
            r"123456",
            r"YOUR_TOKEN_HERE",
            r"your-api-token",
            r"practice-token",
            r"live-token",
        ]

    def supports_file(self, file_path: Path) -> bool:
        """Support all text files."""
        # Skip binary files and certain extensions
        skip_extensions = {".jpg", ".png", ".gif", ".pdf", ".ico", ".woff", ".woff2", ".ttf"}
        return file_path.suffix.lower() not in skip_extensions

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Scan file content for potential security issues."""
        issues: list[ValidationIssue] = []
        # Always use high severity filtering
        exclude_patterns = options.get("exclude_patterns", [])

        # Combine default and custom exclude patterns
        all_exclude_patterns = self.exclude_patterns + exclude_patterns

        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip lines that match exclude patterns
            if self._should_exclude_line(line, all_exclude_patterns):
                continue

            # Check each secret pattern
            for pattern, description in self.secret_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Additional context checks
                    if self._is_likely_real_secret(match.group(), line):
                        severity = self._get_severity(pattern)
                        if severity:
                            issues.append(ValidationIssue(message=f"Potential {description} detected", file_path=file_info.path, line=line_num, severity=severity, rule_id="security_exposed_secret", context=self._mask_secret(line, match.start(), match.end()), suggestion="Remove or replace with placeholder value"))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _should_exclude_line(self, line: str, exclude_patterns: list[str]) -> bool:
        """Check if line should be excluded from scanning."""
        return any(re.search(pattern, line, re.IGNORECASE) for pattern in exclude_patterns)

    def _is_likely_real_secret(self, matched_text: str, line: str) -> bool:
        """Additional heuristics to reduce false positives."""
        # Skip very common placeholder values
        common_placeholders = {"your-api-token", "your-token", "api-token", "secret-key", "example-token", "demo-token", "test-token", "sample-token"}

        if matched_text.lower() in common_placeholders:
            return False

        # Skip if in comments
        if re.search(r"^\s*#", line.strip()):
            return False

        # Skip if in obvious placeholder context
        if re.search(r"(?:example|demo|test|sample|placeholder|your|token_here)", line, re.IGNORECASE):
            return False

        # For long alphanumeric strings, require some additional context
        if re.match(r"^[a-zA-Z0-9]{32,}$", matched_text):
            # Must have context suggesting it's a token/key
            if not re.search(r"(?:token|key|secret|auth|credential)", line, re.IGNORECASE):
                return False

        return True

    def _get_severity(self, pattern: str) -> IssueSeverity | None:
        """Determine severity based on pattern - always use high severity filtering."""
        # High severity patterns
        high_severity_patterns = [
            r"v20-[a-zA-Z0-9]{32,}",  # OANDA tokens
            r"sk_[a-zA-Z0-9]{20,}",  # Secret keys
            r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*",  # JWT
        ]

        is_high_severity = any(re.match(hp, pattern) for hp in high_severity_patterns)

        # Always use high severity filtering - only report high severity issues
        if not is_high_severity:
            return None

        return IssueSeverity.ERROR

    def _mask_secret(self, line: str, start: int, end: int) -> str:
        """Mask the secret in the context line."""
        before = line[:start]
        after = line[end:]
        masked_length = min(end - start, 20)  # Limit mask length
        mask = "***" + "*" * (masked_length - 6) + "***" if masked_length > 6 else "***"
        return before + mask + after

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*"]
