"""Cross-reference validator for internal links and references."""

import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class CrossReferenceValidator(BaseValidator):
    """Validates internal cross-references and links within documentation."""

    def __init__(self) -> None:
        super().__init__(name="cross_references", description="Validates internal cross-references and relative links")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate cross-references in file content."""
        issues: list[ValidationIssue] = []

        lines = content.split("\n")

        # Track code block state to avoid false positives
        in_code_block = False

        for line_num, line in enumerate(lines, 1):
            # Update code block state
            if line.strip().startswith("```"):
                in_code_block = not in_code_block

            # Skip link checking if we're inside a code block
            if not in_code_block:
                # Check relative links
                issues.extend(self._check_relative_links(line, line_num, file_info))

                # Check anchor links
                issues.extend(self._check_anchor_links(line, line_num, file_info))

                # Check reference-style links
                issues.extend(self._check_reference_links(line, line_num, file_info))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _check_relative_links(self, line: str, line_num: int, file_info: FileInfo) -> list[ValidationIssue]:
        """Check relative file links."""
        issues: list[ValidationIssue] = []

        # Find markdown links that are relative paths
        link_pattern = r"\[([^\]]*)\]\(([^)]+)\)"
        matches = re.finditer(link_pattern, line)

        for match in matches:
            _text, url = match.groups()

            # Skip external URLs
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue

            # Skip empty URLs
            if not url.strip():
                continue

            # Resolve relative path
            try:
                if url.startswith("/"):
                    # Absolute path from project root
                    # Find project root (assuming docs/ is under project root)
                    project_root = self._find_project_root(file_info.path)
                    target_path = project_root / url[1:]  # Remove leading /
                else:
                    # Relative to current file
                    target_path = file_info.path.parent / url

                # Remove URL fragments and query parameters
                clean_url = url.split("#")[0].split("?")[0]
                if clean_url != url:
                    target_path = file_info.path.parent / clean_url if not clean_url.startswith("/") else self._find_project_root(file_info.path) / clean_url[1:]

                # Check if target file exists
                if not target_path.exists():
                    issues.append(ValidationIssue(message=f"Relative link target not found: {url}", file_path=file_info.path, line=line_num, severity=IssueSeverity.ERROR, rule_id="cross_ref_broken_link", context=match.group(0), suggestion=f"Check if the file exists at {target_path}"))

            except Exception as e:
                # Invalid path
                issues.append(ValidationIssue(message=f"Invalid relative link path: {url} ({e})", file_path=file_info.path, line=line_num, severity=IssueSeverity.WARNING, rule_id="cross_ref_invalid_path", context=match.group(0), suggestion="Check the link path syntax"))

        return issues

    def _check_anchor_links(self, line: str, line_num: int, file_info: FileInfo) -> list[ValidationIssue]:
        """Check anchor links within the same file."""
        issues: list[ValidationIssue] = []

        # Find anchor links (starting with #)
        anchor_pattern = r"\[([^\]]*)\]\(#([^)]+)\)"
        matches = re.finditer(anchor_pattern, line)

        for match in matches:
            _text, anchor = match.groups()

            # Read the current file to check if anchor exists
            # This is a simplified check - full implementation would parse all headers
            try:
                with file_info.path.open("r", encoding="utf-8") as f:
                    file_content = f.read()

                # Look for matching header
                # Convert anchor to expected header format
                _expected_header = anchor.replace("-", " ").lower()

                # Find headers in file
                header_pattern = r"^#+\s+(.+)$"
                found_anchor = False

                for file_line in file_content.split("\n"):
                    header_match = re.match(header_pattern, file_line.strip())
                    if header_match:
                        header_text = header_match.group(1).lower()
                        # Simple header-to-anchor conversion
                        header_anchor = re.sub(r"[^\w\s-]", "", header_text).replace(" ", "-")
                        if header_anchor == anchor.lower():
                            found_anchor = True
                            break

                if not found_anchor:
                    issues.append(ValidationIssue(message=f"Anchor link target not found: #{anchor}", file_path=file_info.path, line=line_num, severity=IssueSeverity.WARNING, rule_id="cross_ref_broken_anchor", context=match.group(0), suggestion=f"Check if a header exists that would generate the anchor #{anchor}"))

            except Exception as e:
                # Couldn't read file or other error
                issues.append(ValidationIssue(message=f"Could not validate anchor link #{anchor}: {e}", file_path=file_info.path, line=line_num, severity=IssueSeverity.INFO, rule_id="cross_ref_anchor_check_failed", context=match.group(0), suggestion="Manually verify the anchor link"))

        return issues

    def _check_reference_links(self, line: str, line_num: int, file_info: FileInfo) -> list[ValidationIssue]:
        """Check reference-style links."""
        issues: list[ValidationIssue] = []

        # Find reference-style links [text][ref]
        ref_pattern = r"\[([^\]]+)\]\[([^\]]*)\]"
        matches = re.finditer(ref_pattern, line)

        for match in matches:
            text, ref = match.groups()

            # If ref is empty, it should use text as reference
            ref_to_check = ref if ref else text

            # This is a simplified check - full implementation would track all reference definitions
            # For now, just warn about potential issues
            if not ref_to_check.strip():
                issues.append(ValidationIssue(message="Reference link has empty reference", file_path=file_info.path, line=line_num, severity=IssueSeverity.WARNING, rule_id="cross_ref_empty_reference", context=match.group(0), suggestion="Add a reference name or define the reference elsewhere"))

        return issues

    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root directory."""
        # Look for common project root indicators
        current = file_path.parent

        while current != current.parent:
            # Check for common root indicators
            if any((current / indicator).exists() for indicator in ["pyproject.toml", "setup.py", ".git", "package.json", "Cargo.toml"]):
                return current
            current = current.parent

        # Fallback to current working directory
        return Path.cwd()

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
