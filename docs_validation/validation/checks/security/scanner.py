"""Security validation for documentation and code."""

import re
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult


class SecurityCheck(ContentCheck):
    """Scans documentation and code for potential security issues."""

    def __init__(self):
        super().__init__(
            name="security",
            description="Scans documentation for potential security issues",
            file_patterns=["**/*.md", "**/*.py", "**/*.yml", "**/*.yaml", "**/*.json"],
        )

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check content for security issues."""
        patterns = self._get_security_patterns()
        lines = content.split("\n")

        for line_number, line in enumerate(lines, 1):
            for pattern, description, severity_level in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Skip common false positives
                    if self._is_false_positive(match.group(), line, file_path):
                        continue

                    severity = self._map_severity(severity_level)

                    result.add_issue(
                        message=f"Potential {description} detected",
                        file_path=str(file_path),
                        line=line_number,
                        severity=severity,
                        context=f"Found: '{match.group()}'",
                        suggestion=f"Review and remove or redact {description.lower()} if real",
                    )

    def _get_security_patterns(self) -> list[tuple[str, str, str]]:
        """Get security validation patterns with severity levels."""
        return [
            # API Keys and Tokens
            (r"\b[0-9a-f]{32}\b", "API Token", "high"),
            (r"\bsk_[a-zA-Z0-9]{24,}\b", "Secret Key", "high"),
            (r"\bpk_[a-zA-Z0-9]{24,}\b", "Public Key", "medium"),
            (r"\bAKIA[0-9A-Z]{16}\b", "AWS Access Key", "high"),
            (r"\b[0-9a-zA-Z+/]{40}={0,2}\b", "Base64 Encoded Secret", "medium"),

            # OANDA-specific patterns
            (r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", "OANDA Account ID", "high"),
            (r"\bv20-[a-zA-Z0-9]{40,}\b", "OANDA v20 Token", "high"),

            # Private keys and certificates
            (r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----", "Private Key", "high"),
            (r"-----BEGIN\s+CERTIFICATE-----", "Certificate", "medium"),
            (r"ssh-rsa\s+[A-Za-z0-9+/]{300,}", "SSH Public Key", "medium"),
            (r"ssh-dss\s+[A-Za-z0-9+/]{300,}", "SSH DSA Key", "medium"),

            # Passwords and secrets in code
            (r"password\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Password", "high"),
            (r"secret\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Secret", "high"),
            (r"api_key\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded API Key", "high"),
            (r"token\s*=\s*['\"][^'\"]{8,}['\"]", "Hardcoded Token", "high"),

            # Connection strings
            (r"mongodb://[^\\s]+:[^\\s]+@", "MongoDB Connection String", "high"),
            (r"postgres://[^\\s]+:[^\\s]+@", "PostgreSQL Connection String", "high"),
            (r"mysql://[^\\s]+:[^\\s]+@", "MySQL Connection String", "high"),

            # Cloud service credentials
            (r"\b[0-9]{12}\.apps\.googleusercontent\.com\b", "Google OAuth Client ID", "medium"),
            (r"\bxoxb-[0-9]+-[0-9]+-[0-9a-zA-Z]{24}\b", "Slack Bot Token", "high"),
            (r"\bghp_[a-zA-Z0-9]{36}\b", "GitHub Personal Access Token", "high"),

            # Email addresses in code (could be sensitive)
            (r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b", "Email Address", "low"),

            # IP addresses (private ranges might be sensitive)
            (r"\b(?:10\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?))\b", "Private IP Address", "low"),

            # URLs that might contain sensitive info
            (r"https?://[^\\s]*(?:secret|token|key|password)=[^\\s&]*", "URL with Sensitive Parameter", "medium"),

            # Common secret environment variables
            (r"\$\{?(?:SECRET|PASSWORD|TOKEN|KEY|PRIVATE)", "Environment Variable Secret Reference", "medium"),
        ]

    def _is_false_positive(self, match: str, line: str, file_path: Path) -> bool:
        """Check if a match is likely a false positive."""
        # Skip common false positives
        false_positive_indicators = [
            "example",
            "placeholder",
            "your_",
            "your-",
            "<",
            ">",
            "XXX",
            "000",
            "123",
            "test",
            "demo",
            "sample",
            "dummy",
            "fake",
        ]

        match_lower = match.lower()
        line_lower = line.lower()

        # Check if match contains false positive indicators
        for indicator in false_positive_indicators:
            if indicator in match_lower or indicator in line_lower:
                return True

        # Skip email addresses in documentation files that are clearly examples
        if "@" in match and file_path.suffix == ".md":
            if any(domain in match for domain in ["example.com", "example.org", "test.com", "docs.com"]):
                return True

        # Skip if in comments
        if line.strip().startswith("#") or line.strip().startswith("//"):
            return True

        # Skip if in markdown code blocks
        if "```" in line or "`" in match:
            return True

        return False

    def _map_severity(self, severity_level: str) -> IssueSeverity:
        """Map string severity levels to IssueSeverity enum."""
        severity_map = {
            "high": IssueSeverity.ERROR,
            "medium": IssueSeverity.WARNING,
            "low": IssueSeverity.INFO,
        }
        return severity_map.get(severity_level.lower(), IssueSeverity.WARNING)

    def supports_file(self, file_path: Path) -> bool:
        """Check if this validator supports the given file."""
        # Exclude cache and build directories
        excluded_dirs = {".mypy_cache", "__pycache__", ".ruff_cache", "node_modules", ".git"}

        # Convert to string and check if any excluded directory is in the path
        path_str = str(file_path)
        for excluded in excluded_dirs:
            if excluded in path_str:
                return False

        supported_extensions = {".md", ".py", ".yml", ".yaml", ".json", ".txt", ".sh"}
        return file_path.suffix.lower() in supported_extensions

    def get_check_metadata(self) -> dict[str, Any]:
        """Get metadata about this check for optimization."""
        return {
            "check_type": "io_bound",  # Text processing with regex
            "estimated_files_per_second": 100.0,  # Fast regex matching
            "memory_usage_mb": 5.0,
            "supports_batching": True,
            "requires_context_isolation": False,
        }
