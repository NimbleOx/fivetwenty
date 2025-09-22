"""
Security validation for documentation.

Scans documentation for potential security issues like exposed secrets.
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


class SecurityValidator(FileValidator):  # type: ignore[misc]
    """Validates security aspects of documentation files."""

    def __init__(self) -> None:
        super().__init__(name="security_validator", description="Scans documentation for potential security issues", file_patterns=["docs/**/*.md", "*.md", "**/*.py"])
        self.security_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate security in all files."""
        files = self.get_files_to_validate()
        total_files = len(files)

        for file_path in files:
            self._check_file_security(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.security_issues) == 0 else "failed",
            issues_found=len(self.security_issues),
            total_checked=total_files,
            details={"security_issues": self.security_issues, "files_checked": total_files},
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _get_security_patterns(self) -> list[tuple[str, str, str]]:
        """Get security validation patterns with severity levels."""
        return [
            # (pattern, description, severity)
            (r"\b[0-9a-f]{32}\b", "API Token", "high"),
            (r"\bsk_[a-zA-Z0-9]{24,}\b", "Secret Key", "high"),
            (r"\b[A-Z0-9]{20,}\b", "Potential Token", "medium"),
            (r'password\s*[=:]\s*["\']?\w+', "Password", "high"),
            (r"\bbearer\s+[a-zA-Z0-9._-]{20,}\b", "Bearer Token", "high"),
            (r"\bauthorization:\s*[a-zA-Z0-9._-]{20,}", "Authorization Header", "high"),
            (r'\baws_access_key_id\s*[=:]\s*["\']?[A-Z0-9]{20}', "AWS Access Key", "high"),
            (r'\baws_secret_access_key\s*[=:]\s*["\']?[a-zA-Z0-9/+=]{40}', "AWS Secret Key", "high"),
            (r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", "Private Key", "critical"),
            (r"\bmongo[db]*://[^:\s]+:[^@\s]+@", "MongoDB Connection String with Credentials", "high"),
            (r"\bmysql://[^:\s]+:[^@\s]+@", "MySQL Connection String with Credentials", "high"),
            (r"\bpostgres[ql]*://[^:\s]+:[^@\s]+@", "PostgreSQL Connection String with Credentials", "high"),
        ]

    def _check_file_security(self, file_path: Path) -> None:
        """Check security in a single file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            security_patterns = self._get_security_patterns()

            for pattern, description, severity in security_patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))

                for match in matches:
                    matched_text = match.group()

                    # Skip false positives for "Potential Token" pattern
                    if description == "Potential Token" and self._is_false_positive_token(matched_text, content, match):
                        continue

                    # Find line number
                    line_num = content[: match.start()].count("\n") + 1

                    # Mask sensitive parts of the match for logging
                    masked_text = self._mask_sensitive_data(matched_text)

                    # Get context around the match (masked)
                    start_pos = max(0, match.start() - 30)
                    end_pos = min(len(content), match.end() + 30)
                    context = content[start_pos:end_pos].replace("\n", " ")
                    masked_context = self._mask_sensitive_data(context)

                    issue = {"file": str(file_path), "line": line_num, "type": "security_issue", "severity": severity, "description": description, "matched_text": masked_text, "context": masked_context.strip()}
                    self.security_issues.append(issue)
                    self.add_issue(f"Security issue ({severity}): Potential {description}", str(file_path), line_num)

        except Exception as e:
            issue = {"file": str(file_path), "type": "read_error", "message": f"Could not read file: {e}"}
            self.security_issues.append(issue)
            self.add_issue(f"Error reading file: {e}", str(file_path))

    def _mask_sensitive_data(self, text: str) -> str:
        """Mask sensitive data in text for safe logging."""
        # Mask potential tokens/keys - show first few and last few characters
        masked = text

        # Mask long alphanumeric sequences that could be tokens
        masked = re.sub(r"\b[a-zA-Z0-9]{15,}\b", lambda m: f"{m.group()[:4]}...{m.group()[-4:]}", masked)

        # Mask hex sequences that could be API keys
        masked = re.sub(r"\b[0-9a-f]{20,}\b", lambda m: f"{m.group()[:4]}...{m.group()[-4:]}", masked)

        # Mask passwords
        return re.sub(r'(password\s*[=:]\s*["\']?)(\w+)', r"\1****", masked, flags=re.IGNORECASE)

    def _is_false_positive_token(self, matched_text: str, content: str, match: re.Match[str]) -> bool:
        """Check if a potential token match is likely a false positive."""
        # Common patterns that are not tokens
        false_positive_patterns = [
            # Python class names ending with common suffixes
            r".*Validator$",
            r".*Generator$",
            r".*Exception$",
            r".*Configuration$",
            r".*Documentation$",
            r".*Implementation$",
            r".*Specification$",
            r".*Authentication$",
            r".*Authorization$",
            r".*Factory$",
            r".*Builder$",
            r".*Manager$",
            r".*Handler$",
            r".*Processor$",
            r".*Controller$",
            r".*Service$",
            r".*Repository$",
            r".*Interface$",
            r".*Abstract$",
            r".*Formatter$",
            r".*Converter$",
            r".*Transformer$",
            r".*Descriptor$",
            # Enum values and constants
            r".*Granularity$",
            r".*Direction$",
            r".*InstrumentType$",
            r".*OrderType$",
            r".*TimeInForce$",
            r".*Environment$",
            # Common uppercase words that might appear in docs
            r"^[A-Z][A-Z_]*[A-Z]$",  # All caps constants like "API_VERSION"
        ]

        for pattern in false_positive_patterns:
            if re.match(pattern, matched_text, re.IGNORECASE):
                return True

        # Check context - if it's in an import statement or class definition, likely false positive
        context_start = max(0, match.start() - 50)
        context_end = min(len(content), match.end() + 50)
        context = content[context_start:context_end]

        # Check for import contexts
        if any(keyword in context.lower() for keyword in ["import", "from ", "class ", "def ", "enum "]):
            return True

        # Check if it's in a comment or docstring
        lines_around = context.split('\n')
        for line in lines_around:
            line = line.strip()
            if matched_text in line and (line.startswith('#') or '"""' in line or "'''" in line):
                return True

        return False
