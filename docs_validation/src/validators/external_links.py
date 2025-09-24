"""External link validator for HTTP/HTTPS URLs."""

import asyncio
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class ExternalLinkValidator(BaseValidator):
    """Validates external HTTP/HTTPS links in documentation."""

    def __init__(self) -> None:
        super().__init__(name="external_links", description="Validates external HTTP/HTTPS links (slow - network requests)")
        self.timeout = 10.0  # seconds
        self.max_concurrent = 5  # concurrent requests

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate external links in file content."""
        issues: list[ValidationIssue] = []

        # Extract all external links first
        external_links = self._extract_external_links(content, file_info)

        if not external_links:
            return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=True, issues=[])

        # Filter out excluded URLs
        excluded_urls = options.get("exclude_urls", [])
        filtered_links = self._filter_excluded_links(external_links, excluded_urls)

        if not filtered_links:
            return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=True, issues=[])

        # Validate links asynchronously
        link_results = asyncio.run(self._validate_links_async(filtered_links))

        # Convert results to issues
        for link_data, status, error in link_results:
            if status != "ok":
                severity = IssueSeverity.WARNING if status == "timeout" else IssueSeverity.ERROR

                # Create a more descriptive message
                link_text = link_data["text"]
                url = link_data["url"]

                # Format status with HTTP code if available
                status_display = f"{status} ({error})" if error and status == "http_error" else status

                if link_text == "bare URL":
                    message = f"Bare URL link failed ({status_display}): {url}"
                    context = f"URL: {url}"
                else:
                    message = f"Link '{link_text}' failed ({status_display}): {url}"
                    context = f"Link text: '{link_text}' → URL: {url}"

                issues.append(ValidationIssue(message=message, file_path=file_info.path, line=link_data["line_num"], severity=severity, rule_id=f"external_link_{status}", context=context, suggestion=f"Check if URL is accessible. Error: {error}" if error else "Check if URL is accessible"))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _extract_external_links(self, content: str, file_info: FileInfo) -> list[dict[str, Any]]:
        """Extract all external HTTP/HTTPS links from content."""
        external_links = []
        lines = content.split("\n")
        in_code_block = False

        for line_num, line in enumerate(lines, 1):
            # Update code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            # Skip link checking if we're inside a code block
            if in_code_block:
                continue

            # Find markdown links: [text](url)
            link_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
            matches = re.finditer(link_pattern, line)

            for match in matches:
                text, url = match.groups()

                # Only process external HTTP/HTTPS URLs
                if url.startswith(("http://", "https://")):
                    # Clean URL by removing trailing punctuation that's not part of the URL
                    clean_url = self._clean_url(url)
                    external_links.append({"url": clean_url, "text": text, "line_num": line_num, "context": match.group(0), "file_path": file_info.path})

            # Also check for bare URLs in text (not in links)
            url_pattern = r"https?://[^\s<>\"']+"
            url_matches = re.finditer(url_pattern, line)

            for match in url_matches:
                url = match.group(0)
                # Skip if it's already part of a markdown link
                if f"]({url})" not in line and f"]({url[:-1]})" not in line:  # Handle trailing punctuation
                    clean_url = self._clean_url(url)
                    external_links.append({"url": clean_url, "text": "bare URL", "line_num": line_num, "context": match.group(0), "file_path": file_info.path})

        return external_links

    def _filter_excluded_links(self, external_links: list[dict[str, Any]], excluded_urls: list[str]) -> list[dict[str, Any]]:
        """Filter out excluded URLs from the list of external links."""
        if not excluded_urls:
            return external_links

        filtered_links = []
        for link in external_links:
            url = link["url"]
            # Check if URL matches any of the excluded patterns
            should_exclude = False
            for excluded_url in excluded_urls:
                # Normalize both URLs by removing trailing slashes
                normalized_excluded = excluded_url.rstrip("/")
                # Check if the URL starts with the excluded pattern
                if url.startswith(normalized_excluded):
                    should_exclude = True
                    break

            if not should_exclude:
                filtered_links.append(link)

        return filtered_links

    def _clean_url(self, url: str) -> str:
        """Clean URL by removing trailing punctuation that's not part of the URL."""
        # Remove trailing punctuation that commonly gets captured by regex but isn't part of the URL
        # Common trailing characters: ), )*, )**, ,, ., ;, etc.
        while url and url[-1] in ")]*,;.!\"'":
            url = url[:-1]

        return url

    async def _validate_links_async(self, external_links: list[dict[str, Any]]) -> list[tuple[dict[str, Any], str, str]]:
        """Validate external links asynchronously."""
        # Remove duplicates while preserving first occurrence info
        seen_urls = {}
        unique_links = []
        for link in external_links:
            url = link["url"]
            if url not in seen_urls:
                seen_urls[url] = link
                unique_links.append(link)

        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Validate all unique links
        tasks = [self._validate_single_link(semaphore, link) for link in unique_links]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results back to all original links (including duplicates)
        final_results = []
        for link in external_links:
            url = link["url"]
            # Find the result for this URL
            for unique_link, result in zip(unique_links, results, strict=False):
                if unique_link["url"] == url:
                    if isinstance(result, Exception):
                        final_results.append((link, "error", str(result)))
                    elif isinstance(result, tuple) and len(result) == 2:
                        status, error = result
                        final_results.append((link, status, error))
                    else:
                        final_results.append((link, "error", "Unexpected result type"))
                    break

        return final_results

    async def _validate_single_link(self, semaphore: asyncio.Semaphore, link_data: dict[str, Any]) -> tuple[str, str]:
        """Validate a single external link."""
        async with semaphore:
            url = link_data["url"]

            # Parse URL to validate format
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return "invalid_url", f"Invalid URL format: {url}"

            try:
                # Make HTTP request with timeout
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": "FiveTwenty-Docs-Validator/1.0"}) as client:
                    response = await client.head(url)  # Use HEAD to avoid downloading content

                    # Try GET if HEAD fails with Method Not Allowed
                    if response.status_code == 405:
                        response = await client.get(url)

                    # Check final response status
                    return ("ok", "") if response.status_code < 400 else ("http_error", f"HTTP {response.status_code}")

            except asyncio.TimeoutError:
                return "timeout", f"Request timeout after {self.timeout}s"
            except httpx.HTTPStatusError as e:
                # This is a proper HTTP response with 4xx/5xx status
                return "http_error", f"HTTP {e.response.status_code}"
            except (httpx.RequestError, Exception) as e:
                # Consolidate request errors and unexpected exceptions
                error_type = "request_error" if isinstance(e, httpx.RequestError) else "error"
                error_prefix = "Request failed" if isinstance(e, httpx.RequestError) else "Unexpected error"
                return error_type, f"{error_prefix}: {type(e).__name__}: {e}"

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
