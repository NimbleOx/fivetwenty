"""
Cross-Reference validation for documentation.

Validates internal documentation links and cross-references to ensure
they point to existing files and sections.
"""

import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class CrossReferenceValidator(FileValidator):  # type: ignore[misc]
    """Validates cross-references in documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="cross_reference_validator",
            description="Validates internal documentation links and cross-references",
            file_patterns=["docs/**/*.md", "*.md"]
        )
        self.reference_issues: list[dict[str, Any]] = []
        self.doc_sections: dict[str, set[str]] = {}  # file -> set of section anchors

    def validate(self) -> ValidationResult:
        """Validate cross-references in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)

        # First pass: collect all section anchors from all files
        for file_path in files:
            self._collect_sections(file_path)

        # Second pass: validate references
        total_references = 0
        for file_path in files:
            total_references += self._check_file_references(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.reference_issues) == 0 else "failed",
            issues_found=len(self.reference_issues),
            total_checked=total_references,
            details={
                "reference_issues": self.reference_issues,
                "files_checked": total_files,
                "references_checked": total_references,
                "sections_found": {str(k): list(v) for k, v in self.doc_sections.items()}
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _collect_sections(self, file_path: Path) -> None:
        """Collect section anchors from a markdown file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            sections = set()

            # Find all headings and create anchor names
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            for match in re.finditer(heading_pattern, content, re.MULTILINE):
                heading_text = match.group(2).strip()
                # Convert heading to anchor format (GitHub style)
                anchor = self._heading_to_anchor(heading_text)
                sections.add(anchor)

            # Store relative path as key for cross-referencing
            try:
                relative_path = file_path.relative_to(Path.cwd())
            except ValueError:
                # If file is not in a subpath of cwd, just use the filename
                relative_path = file_path.name
            self.doc_sections[str(relative_path)] = sections

        except Exception as e:
            self.reference_issues.append({
                "file": str(file_path),
                "type": "section_collection_error",
                "message": f"Could not collect sections: {e}",
                "severity": "warning"
            })

    def _heading_to_anchor(self, heading_text: str) -> str:
        """Convert heading text to GitHub-style anchor."""
        # Remove markdown formatting
        heading_text = re.sub(r'[*_`]', '', heading_text)
        # Convert to lowercase and replace spaces/special chars with hyphens
        anchor = re.sub(r'[^\w\s-]', '', heading_text.lower())
        anchor = re.sub(r'[\s_]+', '-', anchor)
        # Remove leading/trailing hyphens
        return anchor.strip('-')

    def _check_file_references(self, file_path: Path) -> int:
        """Check cross-references in a single file. Returns number of references checked."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            reference_count = 0

            # Find markdown links [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            for match in re.finditer(link_pattern, content):
                link_text = match.group(1)
                link_url = match.group(2)
                line_num = content[:match.start()].count('\n') + 1

                # Only check internal references (not external URLs)
                if self._is_internal_reference(link_url):
                    reference_count += 1
                    self._validate_internal_link(file_path, link_text, link_url, line_num)

            # Find reference-style links [text][ref] and [ref]: url
            ref_link_pattern = r'\[([^\]]+)\]\[([^\]]+)\]'
            ref_def_pattern = r'^\[([^\]]+)\]:\s*(.+)$'

            # Collect reference definitions
            ref_definitions = {}
            for match in re.finditer(ref_def_pattern, content, re.MULTILINE):
                ref_id = match.group(1).lower()
                ref_url = match.group(2).strip()
                ref_definitions[ref_id] = ref_url

            # Check reference-style links
            for match in re.finditer(ref_link_pattern, content):
                link_text = match.group(1)
                ref_id = match.group(2).lower()
                line_num = content[:match.start()].count('\n') + 1

                if ref_id in ref_definitions:
                    link_url = ref_definitions[ref_id]
                    if self._is_internal_reference(link_url):
                        reference_count += 1
                        self._validate_internal_link(file_path, link_text, link_url, line_num)
                else:
                    self._add_reference_issue(
                        file_path=file_path,
                        issue_type="undefined_reference",
                        message=f"Undefined reference '{ref_id}' in link '{link_text}'",
                        line=line_num,
                        severity="error"
                    )

            return reference_count

        except Exception as e:
            self.reference_issues.append({
                "file": str(file_path),
                "type": "file_error",
                "message": f"Could not read file: {e}",
                "severity": "error"
            })
            return 0

    def _is_internal_reference(self, url: str) -> bool:
        """Check if URL is an internal reference."""
        url = url.strip()

        # Skip external URLs
        if url.startswith(('http://', 'https://', 'ftp://', 'mailto:')):
            return False

        # Skip anchors to current document
        if url.startswith('#'):
            return True

        # Check for relative paths
        return bool(url.startswith(('./', '../')) or not url.startswith('/'))

    def _validate_internal_link(self, file_path: Path, link_text: str, link_url: str, line_num: int) -> None:
        """Validate an internal link."""
        # Parse URL into file path and anchor
        url_parts = link_url.split('#', 1)
        target_file = url_parts[0] if url_parts[0] else str(file_path.relative_to(Path.cwd()))
        target_anchor = url_parts[1] if len(url_parts) > 1 else None

        # Handle relative paths
        if target_file and not target_file.startswith('/'):
            # Resolve relative to current file's directory
            current_dir = file_path.parent
            if target_file.startswith('./'):
                target_file = target_file[2:]
            elif target_file.startswith('../'):
                # Handle ../ paths
                parts = target_file.split('/')
                resolved_dir = current_dir
                for part in parts:
                    if part == '..':
                        resolved_dir = resolved_dir.parent
                    elif part and part != '.':
                        resolved_dir = resolved_dir / part
                        break
                # Reconstruct the path for the last part
                if parts[-1] != '..':
                    target_file = str(resolved_dir.relative_to(Path.cwd()))
                else:
                    target_file = str(resolved_dir.relative_to(Path.cwd()))
            else:
                # Relative to current directory
                target_path = current_dir / target_file
                try:
                    target_file = str(target_path.relative_to(Path.cwd()))
                except ValueError:
                    # Path goes outside project
                    self._add_reference_issue(
                        file_path=file_path,
                        issue_type="external_path",
                        message=f"Link points outside project: {link_url}",
                        line=line_num,
                        severity="warning",
                        link_text=link_text
                    )
                    return

        # Check if target file exists
        if target_file and target_file != str(file_path.relative_to(Path.cwd())):
            target_path = Path.cwd() / target_file
            if not target_path.exists():
                self._add_reference_issue(
                    file_path=file_path,
                    issue_type="missing_file",
                    message=f"Link target file does not exist: {target_file}",
                    line=line_num,
                    severity="error",
                    link_text=link_text,
                    target_file=target_file
                )
                return

        # Check if target anchor exists (if specified)
        if target_anchor:
            target_anchor = unquote(target_anchor)  # Decode URL encoding

            # Get sections for target file
            target_sections = self.doc_sections.get(target_file, set())

            if target_anchor not in target_sections:
                self._add_reference_issue(
                    file_path=file_path,
                    issue_type="missing_anchor",
                    message=f"Link target anchor does not exist: #{target_anchor} in {target_file or 'current file'}",
                    line=line_num,
                    severity="error",
                    link_text=link_text,
                    target_file=target_file,
                    target_anchor=target_anchor,
                    available_anchors=list(target_sections)[:10]  # Show first 10 for debugging
                )

    def _add_reference_issue(self, file_path: Path, issue_type: str, message: str, line: int, severity: str, **kwargs: Any) -> None:
        """Add a reference issue to the results."""
        # Try to make path relative to current working directory, fall back to just the filename
        try:
            display_path = str(file_path.relative_to(Path.cwd()))
        except ValueError:
            # If file is not in a subpath of cwd, just use the filename
            display_path = file_path.name

        issue = {
            "file": display_path,
            "line": line,
            "type": issue_type,
            "message": message,
            "severity": severity,
            **kwargs
        }
        self.reference_issues.append(issue)
        self.add_issue(message, str(file_path), line)
