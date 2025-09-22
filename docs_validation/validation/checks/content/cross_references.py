"""Cross-reference validation for documentation."""

import re
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from validation.checks.base import FileCheck
from validation.core.context import ValidationContext
from validation.core.results import IssueSeverity, ValidationResult, ValidationStatus


class CrossReferenceCheck(FileCheck):
    """Validates internal documentation links and cross-references."""

    def __init__(self):
        super().__init__(
            name="cross_references",
            description="Validates internal documentation links and cross-references",
            file_patterns=["**/*.md"],
        )
        self.doc_sections: dict[str, set[str]] = {}  # file -> set of section anchors

    def run(self, context: ValidationContext) -> ValidationResult:
        """Run cross-reference validation with two-pass algorithm."""
        from datetime import datetime

        start_time = datetime.now()
        result = self.create_result(context)

        try:
            # Get files to check
            files_to_check = self.get_files_to_check(context)
            result.files_checked = len(files_to_check)

            if not files_to_check:
                result.status = ValidationStatus.SKIPPED
                result.metadata["reason"] = "No files found matching patterns"
                return result

            # First pass: collect all section anchors from all files
            for file_path in files_to_check:
                self._collect_sections(file_path, context)

            # Second pass: validate references
            for file_path in files_to_check:
                try:
                    self._check_file_references(file_path, context, result)
                    context.mark_file_checked(file_path)
                except Exception as e:
                    result.add_issue(
                        message=f"Error checking file: {e}",
                        file_path=str(file_path),
                        severity=IssueSeverity.ERROR,
                    )

            # Determine final status
            if result.issues:
                error_count = len([i for i in result.issues if i.severity == IssueSeverity.ERROR])
                result.status = ValidationStatus.FAILED if error_count > 0 else ValidationStatus.WARNING
            else:
                result.status = ValidationStatus.PASSED

        except Exception as e:
            result.status = ValidationStatus.ERROR
            result.add_issue(
                message=f"Check execution failed: {e}",
                file_path="<check>",
                severity=IssueSeverity.ERROR,
            )

        finally:
            result.duration_seconds = (datetime.now() - start_time).total_seconds()

        return result

    def check_file(
        self,
        file_path: Path,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check individual file - not used since we override run() method."""
        # This method is required by FileCheck but not used since we override run()

    def _collect_sections(self, file_path: Path, context: ValidationContext) -> None:
        """Collect all section headers from a markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = str(file_path.relative_to(context.config.project_root))

            sections = set()

            # Find markdown headers
            header_pattern = r"^#{1,6}\s+(.+?)(?:\s*\{#([^}]+)\})?$"
            for match in re.finditer(header_pattern, content, re.MULTILINE):
                header_text = match.group(1).strip()
                custom_anchor = match.group(2)

                if custom_anchor:
                    # Use custom anchor if provided
                    sections.add(custom_anchor)
                else:
                    # Generate GitHub-style anchor
                    anchor = self._generate_anchor(header_text)
                    sections.add(anchor)

            self.doc_sections[relative_path] = sections

        except Exception:
            # If we can't read the file, skip it
            pass

    def _generate_anchor(self, header_text: str) -> str:
        """Generate GitHub-style anchor from header text."""
        # Convert to lowercase
        anchor = header_text.lower()

        # Replace spaces and special characters with hyphens
        anchor = re.sub(r"[^a-z0-9\s-]", "", anchor)
        anchor = re.sub(r"\s+", "-", anchor)

        # Remove leading/trailing hyphens
        anchor = anchor.strip("-")

        return anchor

    def _check_file_references(
        self,
        file_path: Path,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check all references in a markdown file."""
        try:
            content = file_path.read_text(encoding="utf-8")
            relative_path = str(file_path.relative_to(context.config.project_root))

            # Find markdown links: [text](url) and [text][ref]
            link_patterns = [
                r"\[([^\]]+)\]\(([^)]+)\)",  # [text](url)
                r"\[([^\]]+)\]\[([^\]]+)\]",  # [text][ref]
            ]

            lines = content.split("\n")
            in_code_block = False

            for line_number, line in enumerate(lines, 1):
                # Track code block boundaries
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue

                # Skip lines inside code blocks
                if in_code_block:
                    continue

                for pattern in link_patterns:
                    for match in re.finditer(pattern, line):
                        link_text = match.group(1)
                        link_url = match.group(2)

                        # Skip external links
                        if self._is_external_link(link_url):
                            continue

                        # Check internal reference
                        self._validate_internal_link(
                            link_url,
                            relative_path,
                            line_number,
                            context,
                            result,
                        )

        except Exception as e:
            result.add_issue(
                message=f"Error reading file for cross-reference validation: {e}",
                file_path=str(file_path),
                severity=IssueSeverity.ERROR,
            )

    def _is_external_link(self, url: str) -> bool:
        """Check if a URL is an external link."""
        external_indicators = [
            "http://",
            "https://",
            "ftp://",
            "mailto:",
            "tel:",
            "//",  # Protocol-relative URLs
        ]

        return any(url.startswith(indicator) for indicator in external_indicators)

    def _validate_internal_link(
        self,
        link_url: str,
        current_file: str,
        line_number: int,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Validate an internal link."""
        # URL decode the link
        link_url = unquote(link_url)

        # Split URL and anchor
        if "#" in link_url:
            file_part, anchor_part = link_url.split("#", 1)
        else:
            file_part, anchor_part = link_url, ""

        # If no file part, it's a reference to current file
        if not file_part:
            target_file = current_file
        else:
            # Resolve relative path
            current_dir = Path(current_file).parent
            target_path = current_dir / file_part

            # Normalize the path
            target_file = str(target_path).replace("\\", "/")

            # Remove leading './' if present
            if target_file.startswith("./"):
                target_file = target_file[2:]

        # Check if target file exists
        target_file_path = context.config.project_root / target_file
        if not target_file_path.exists():
            result.add_issue(
                message=f"Broken internal link: file '{target_file}' not found",
                file_path=str(context.config.project_root / current_file),
                line=line_number,
                severity=IssueSeverity.ERROR,
                context=f"Link: {link_url}",
                suggestion=f"Check if file path '{target_file}' is correct",
            )
            return

        # Check anchor if specified
        if anchor_part:
            sections = self.doc_sections.get(target_file, set())
            if anchor_part not in sections:
                result.add_issue(
                    message=f"Broken anchor link: section '#{anchor_part}' not found in '{target_file}'",
                    file_path=str(context.config.project_root / current_file),
                    line=line_number,
                    severity=IssueSeverity.WARNING,
                    context=f"Link: {link_url}",
                    suggestion=f"Check if section anchor '#{anchor_part}' exists in '{target_file}'",
                )

    def supports_file(self, file_path: Path) -> bool:
        """Check if this validator supports the given file."""
        return file_path.suffix.lower() == ".md"

    def get_check_metadata(self) -> dict[str, Any]:
        """Get metadata about this check for optimization."""
        return {
            "check_type": "io_bound",  # File reading and path resolution
            "estimated_files_per_second": 50.0,  # Moderate speed due to cross-file analysis
            "memory_usage_mb": 15.0,  # Stores section mappings in memory
            "supports_batching": False,  # Requires two-pass analysis
            "requires_context_isolation": False,
        }
