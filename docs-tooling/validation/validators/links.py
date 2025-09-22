"""
Link validation for documentation.

Validates internal and external links in markdown files.
"""

import re
import sys
from pathlib import Path
from typing import Any

import requests

# Setup imports - must be done before importing core modules
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.imports import setup_validation_imports

setup_validation_imports()

# Import after path setup
from core.base import FileValidator, ValidationResult  # noqa: E402
from core.cache import EXTERNAL_LINK_CACHE  # noqa: E402


class LinkValidator(FileValidator):
    """Validates links in markdown files."""

    # Pre-compile regex patterns for better performance
    LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    def __init__(self) -> None:
        super().__init__(name="link_validator", description="Validates internal and external links in documentation", file_patterns=["docs/**/*.md", "*.md"])
        self.broken_links: list[dict[str, Any]] = []
        self.checked_external_links: set[str] = set()

    def validate(self) -> ValidationResult:
        """Validate all links in markdown files."""
        files = self.get_files_to_validate()
        total_links = 0

        for file_path in files:
            file_links = self._check_file_links(file_path)
            total_links += len(file_links)

        return ValidationResult(
            validator_name=self.name, status="passed" if len(self.broken_links) == 0 else "failed", issues_found=len(self.broken_links), total_checked=total_links, details={"broken_links": self.broken_links, "files_checked": len(files)}, timestamp=self.start_time.isoformat() if self.start_time else "", duration_seconds=self.get_elapsed_time()
        )

    def _check_file_links(self, file_path: Path) -> list[dict[str, Any]]:
        """Check all links in a single file."""
        links = []

        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Extract markdown links using pre-compiled pattern
            matches = self.LINK_PATTERN.finditer(content)

            for match in matches:
                link_text = match.group(1)
                link_url = match.group(2)
                line_number = content[: match.start()].count("\n") + 1

                link_info = {"text": link_text, "url": link_url, "file": str(file_path), "line": line_number}

                links.append(link_info)

                # Validate the link
                if self._is_broken_link(link_url, file_path):
                    self.broken_links.append(link_info)
                    self.add_issue(f"Broken link: {link_url}", str(file_path), line_number)

        except Exception as e:
            self.add_issue(f"Error reading file: {e}", str(file_path))

        return links

    def _is_broken_link(self, url: str, file_path: Path) -> bool:
        """Check if a link is broken."""
        # Skip anchor links within the same file
        if url.startswith("#"):
            return False

        # Check internal file links
        if not url.startswith(("http://", "https://", "mailto:")):
            return self._is_broken_internal_link(url, file_path)

        # Check external links
        return self._is_broken_external_link(url)

    def _is_broken_internal_link(self, url: str, file_path: Path) -> bool:
        """Check if an internal link is broken."""
        # Remove anchor part
        url_path = url.split("#")[0]
        if not url_path:
            return False

        # Resolve relative path
        target_path = Path(url_path[1:]) if url_path.startswith("/") else file_path.parent / url_path

        # Check if target exists
        return not target_path.exists()

    def _is_broken_external_link(self, url: str) -> bool:
        """Check if an external link is broken using caching."""
        # Check cache first
        cached_result = EXTERNAL_LINK_CACHE.get(url)
        if cached_result is not None:
            return bool(cached_result)

        # Skip if already checked in this session
        if url in self.checked_external_links:
            return False

        self.checked_external_links.add(url)

        try:
            response = requests.head(url, timeout=10, allow_redirects=True)
            is_broken = response.status_code >= 400
        except Exception:
            is_broken = True

        # Cache the result
        EXTERNAL_LINK_CACHE.set(url, is_broken)
        return is_broken
