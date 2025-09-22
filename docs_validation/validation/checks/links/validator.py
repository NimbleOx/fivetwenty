"""Link validation checks."""

import re
from pathlib import Path
from urllib.parse import urlparse

import requests

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationResult


class LinkValidationCheck(ContentCheck):
    """Validate links in markdown content."""

    def __init__(self) -> None:
        super().__init__(
            name="link_validation",
            description="Validates internal and external links",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

        # Link patterns
        self.inline_link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
        self.reference_link_pattern = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")
        self.reference_def_pattern = re.compile(r"^\s*\[([^\]]+)\]:\s*(.+)$", re.MULTILINE)

        # Cache for external link checks
        self.external_cache: dict[str, bool] = {}

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check all links in the content."""
        # Extract all links
        inline_links = self._extract_inline_links(content)
        reference_links, reference_definitions = self._extract_reference_links(content)

        # Check inline links
        for link_text, url, line_num in inline_links:
            self._validate_link(file_path, url, link_text, line_num, result, context)

        # Check reference links
        self._validate_reference_links(
            file_path, reference_links, reference_definitions, result, context,
        )

    def _extract_inline_links(self, content: str) -> list[tuple[str, str, int]]:
        """Extract inline links with line numbers."""
        links = []
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            for match in self.inline_link_pattern.finditer(line):
                link_text, url = match.groups()
                links.append((link_text, url, line_num))

        return links

    def _extract_reference_links(self, content: str) -> tuple[list[tuple[str, str, int]], dict[str, str]]:
        """Extract reference links and their definitions."""
        reference_links = []
        reference_definitions = {}

        lines = content.split("\n")

        # Extract reference link usages
        for line_num, line in enumerate(lines, 1):
            for match in self.reference_link_pattern.finditer(line):
                link_text, reference = match.groups()
                if not reference:  # [text][] format uses text as reference
                    reference = link_text
                reference_links.append((link_text, reference, line_num))

        # Extract reference definitions
        for match in self.reference_def_pattern.finditer(content):
            reference, url = match.groups()
            reference_definitions[reference.strip()] = url.strip()

        return reference_links, reference_definitions

    def _validate_reference_links(
        self,
        file_path: Path,
        reference_links: list[tuple[str, str, int]],
        reference_definitions: dict[str, str],
        result: ValidationResult,
        context: ValidationContext,
    ) -> None:
        """Validate reference links."""
        for link_text, reference, line_num in reference_links:
            if reference not in reference_definitions:
                result.add_issue(
                    message=f"Reference link '{reference}' not defined",
                    file_path=str(file_path),
                    line=line_num,
                    severity=IssueSeverity.ERROR,
                    rule="reference_link_undefined",
                    suggestion=f"Add definition: [{reference}]: <URL>",
                    context={"reference": reference, "link_text": link_text},
                )
            else:
                url = reference_definitions[reference]
                self._validate_link(file_path, url, link_text, line_num, result, context)

    def _validate_link(
        self,
        file_path: Path,
        url: str,
        link_text: str,
        line_num: int,
        result: ValidationResult,
        context: ValidationContext,
    ) -> None:
        """Validate a single link."""
        # Skip empty links
        if not url.strip():
            result.add_issue(
                message="Empty link URL",
                file_path=str(file_path),
                line=line_num,
                severity=IssueSeverity.ERROR,
                rule="empty_link",
            )
            return

        # Parse URL
        parsed = urlparse(url)

        if parsed.scheme in ["http", "https"]:
            # External link
            self._validate_external_link(file_path, url, link_text, line_num, result, context)
        elif parsed.scheme == "mailto":
            # Email link - basic validation
            self._validate_email_link(file_path, url, line_num, result)
        elif not parsed.scheme:
            # Internal link (relative path)
            self._validate_internal_link(file_path, url, line_num, result, context)
        else:
            result.add_issue(
                message=f"Unknown URL scheme: {parsed.scheme}",
                file_path=str(file_path),
                line=line_num,
                severity=IssueSeverity.WARNING,
                rule="unknown_scheme",
                context={"url": url, "scheme": parsed.scheme},
            )

    def _validate_internal_link(
        self,
        file_path: Path,
        url: str,
        line_num: int,
        result: ValidationResult,
        context: ValidationContext,
    ) -> None:
        """Validate internal (relative) links."""
        # Remove anchor/fragment
        path_part = url.split("#")[0]

        if not path_part:
            # Pure anchor link (#section)
            return

        # Resolve relative to current file
        current_dir = file_path.parent
        target_path = current_dir / path_part

        # Try to resolve the path
        try:
            resolved_path = target_path.resolve()
            if not resolved_path.exists():
                result.add_issue(
                    message=f"Internal link target not found: {path_part}",
                    file_path=str(file_path),
                    line=line_num,
                    severity=IssueSeverity.ERROR,
                    rule="broken_internal_link",
                    suggestion=f"Check if file exists: {resolved_path}",
                    context={"target_path": str(resolved_path), "url": url},
                )
        except (OSError, ValueError) as e:
            result.add_issue(
                message=f"Invalid internal link path: {path_part} ({e})",
                file_path=str(file_path),
                line=line_num,
                severity=IssueSeverity.ERROR,
                rule="invalid_internal_link",
                context={"url": url, "error": str(e)},
            )

    def _validate_external_link(
        self,
        file_path: Path,
        url: str,
        link_text: str,
        line_num: int,
        result: ValidationResult,
        context: ValidationContext,
    ) -> None:
        """Validate external links."""
        # Check cache first
        cache_key = f"external_link_{url}"
        cached_result = context.get_cached_metadata(file_path, cache_key)

        if cached_result is not None:
            if not cached_result:
                result.add_issue(
                    message=f"External link unreachable: {url}",
                    file_path=str(file_path),
                    line=line_num,
                    severity=IssueSeverity.WARNING,
                    rule="broken_external_link",
                    context={"url": url, "cached": True},
                )
            return

        # Check if external link checking is enabled
        if not context.config.tools.vale_enabled:  # Reuse vale_enabled as external check flag
            return

        # Perform HTTP check (with timeout and error handling)
        try:
            response = requests.head(
                url,
                timeout=10,
                allow_redirects=True,
                headers={"User-Agent": "FiveTwenty-Docs-Validator/2.0"},
            )

            is_accessible = response.status_code < 400

            # Cache the result
            context.cache_file_metadata(file_path, cache_key, is_accessible)

            if not is_accessible:
                result.add_issue(
                    message=f"External link returned {response.status_code}: {url}",
                    file_path=str(file_path),
                    line=line_num,
                    severity=IssueSeverity.WARNING,
                    rule="broken_external_link",
                    context={"url": url, "status_code": response.status_code},
                )

        except requests.RequestException as e:
            # Cache as inaccessible
            context.cache_file_metadata(file_path, cache_key, False)

            result.add_issue(
                message=f"External link check failed: {url} ({type(e).__name__})",
                file_path=str(file_path),
                line=line_num,
                severity=IssueSeverity.INFO,
                rule="external_link_check_failed",
                context={"url": url, "error": str(e)},
            )

    def _validate_email_link(
        self,
        file_path: Path,
        url: str,
        line_num: int,
        result: ValidationResult,
    ) -> None:
        """Validate email links."""
        email = url.replace("mailto:", "")

        # Basic email validation
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not email_pattern.match(email):
            result.add_issue(
                message=f"Invalid email format: {email}",
                file_path=str(file_path),
                line=line_num,
                severity=IssueSeverity.WARNING,
                rule="invalid_email",
                context={"email": email},
            )
