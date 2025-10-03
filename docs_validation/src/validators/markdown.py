"""Markdown syntax validator."""

import re
from pathlib import Path
from typing import Any

from ..base import BaseValidator
from ..models import FileInfo, IssueSeverity, ValidationIssue, ValidationResult


class MarkdownSyntaxValidator(BaseValidator):
    """Validates markdown syntax and structure."""

    def __init__(self) -> None:
        super().__init__(name="markdown_syntax", description="Validates markdown syntax and structure")

    def supports_file(self, file_path: Path) -> bool:
        """Support markdown files only."""
        return file_path.suffix.lower() in {".md", ".markdown"}

    def validate_file(self, file_info: FileInfo, content: str, options: dict[str, Any]) -> ValidationResult:
        """Validate markdown syntax in file content."""
        issues: list[ValidationIssue] = []

        lines = content.split("\n")

        # Track code block state to avoid false positives
        in_code_block = False

        for line_num, line in enumerate(lines, 1):
            # Check for malformed code blocks first to update state
            code_block_issues, in_code_block = self._check_code_blocks(line, line_num, file_info.path, lines, line_num - 1, in_code_block)
            issues.extend(code_block_issues)

            # Check for malformed headers (skip if in code block)
            if not in_code_block:
                issues.extend(self._check_headers(line, line_num, file_info.path))

            # Check for malformed links (skip if in code block)
            if not in_code_block:
                issues.extend(self._check_links(line, line_num, file_info.path))

            # Check for malformed lists
            issues.extend(self._check_lists(line, line_num, file_info.path, lines, in_code_block))

        # Check for unclosed code blocks
        issues.extend(self._check_unclosed_code_blocks(lines, file_info.path))

        return ValidationResult(validator_name=self.name, file_path=file_info.path, passed=len(issues) == 0, issues=issues)

    def _check_headers(self, line: str, line_num: int, file_path: Path) -> list[ValidationIssue]:
        """Check for malformed markdown headers."""
        issues: list[ValidationIssue] = []

        # Header pattern: # Title (but not shebang lines like #!/bin/bash)
        if line.strip().startswith("#") and not line.strip().startswith("#!"):
            # Check for space after #
            if not re.match(r"^#+\s+.+", line.strip()):
                issues.append(ValidationIssue(message="Header should have a space after the # symbol", file_path=file_path, line=line_num, severity=IssueSeverity.WARNING, rule_id="markdown_header_space", context=line.strip(), suggestion="Add a space after # (e.g., '# Title' instead of '#Title')"))

            # Check for empty headers
            if re.match(r"^#+\s*$", line.strip()):
                issues.append(ValidationIssue(message="Empty header found", file_path=file_path, line=line_num, severity=IssueSeverity.ERROR, rule_id="markdown_empty_header", context=line.strip(), suggestion="Add header text after the # symbols"))

        return issues

    def _check_links(self, line: str, line_num: int, file_path: Path) -> list[ValidationIssue]:
        """Check for malformed markdown links."""
        issues: list[ValidationIssue] = []

        # Find markdown links: [text](url)
        link_pattern = r"\[([^\]]*)\]\(([^)]*)\)"
        matches = re.finditer(link_pattern, line)

        for match in matches:
            text, url = match.groups()

            # Check for empty link text
            if not text.strip():
                issues.append(ValidationIssue(message="Link has empty text", file_path=file_path, line=line_num, severity=IssueSeverity.WARNING, rule_id="markdown_empty_link_text", context=match.group(0), suggestion="Add descriptive text between the square brackets"))

            # Check for empty URL
            if not url.strip():
                issues.append(ValidationIssue(message="Link has empty URL", file_path=file_path, line=line_num, severity=IssueSeverity.ERROR, rule_id="markdown_empty_link_url", context=match.group(0), suggestion="Add a valid URL between the parentheses"))

        # Check for malformed reference links
        ref_link_pattern = r"\[([^\]]+)\]\[([^\]]*)\]"
        ref_matches = re.finditer(ref_link_pattern, line)

        for match in ref_matches:
            text, _ref = match.groups()
            if not text.strip():
                issues.append(ValidationIssue(message="Reference link has empty text", file_path=file_path, line=line_num, severity=IssueSeverity.WARNING, rule_id="markdown_empty_ref_link", context=match.group(0), suggestion="Add descriptive text for the reference link"))

        return issues

    def _check_code_blocks(self, line: str, line_num: int, file_path: Path, all_lines: list[str], line_index: int, in_code_block: bool) -> tuple[list[ValidationIssue], bool]:
        """Check for malformed code blocks and track state."""
        issues: list[ValidationIssue] = []

        # Check for indented code blocks with inconsistent indentation
        if line.startswith(("    ", "\t")):
            # This might be a code block - check if previous/next lines have consistent indentation
            # This is a simplified check - full implementation would track code block state
            pass

        # Check for fenced code blocks
        if line.strip().startswith("```"):
            if not in_code_block:
                # This is an opening code block
                if len(line.strip()) == 3:  # No language specified
                    # Check if this starts a code block (has content after)
                    if line_index + 1 < len(all_lines):
                        next_line = all_lines[line_index + 1] if line_index + 1 < len(all_lines) else ""
                        # If next line looks like code content, suggest adding language
                        if next_line.strip() and not next_line.strip().startswith("```"):
                            issues.append(ValidationIssue(message="Code block missing language specification", file_path=file_path, line=line_num, severity=IssueSeverity.INFO, rule_id="markdown_code_block_language", context=line.strip(), suggestion="Add language after ``` (e.g., ```python, ```bash, ```yaml)"))
                # Enter code block
                in_code_block = True
            else:
                # This is a closing code block
                in_code_block = False

        return issues, in_code_block

    def _check_lists(self, line: str, line_num: int, file_path: Path, lines: list[str], in_code_block: bool) -> list[ValidationIssue]:
        """Check for malformed lists."""
        issues: list[ValidationIssue] = []

        # Check unordered lists
        if re.match(r"^\s*[-*+]\s*$", line):
            issues.append(ValidationIssue(message="Empty list item", file_path=file_path, line=line_num, severity=IssueSeverity.WARNING, rule_id="markdown_empty_list_item", context=line.strip(), suggestion="Add content to the list item or remove it"))

        # Check ordered lists
        if re.match(r"^\s*\d+\.\s*$", line):
            issues.append(ValidationIssue(message="Empty numbered list item", file_path=file_path, line=line_num, severity=IssueSeverity.WARNING, rule_id="markdown_empty_numbered_item", context=line.strip(), suggestion="Add content to the list item or remove it"))

        # Check for lists that need blank line separation (skip if in code block)
        if not in_code_block and (re.match(r"^\s*[-*+]\s+.+", line) or re.match(r"^\s*\d+\.\s+.+", line)):
            # This is the first item of a list - check if previous line needs a blank line
            if line_num > 1:
                prev_line = lines[line_num - 2]  # line_num is 1-based, lines is 0-based

                # Check if previous line is text that likely introduces a list
                if (
                    prev_line.strip()
                    and not re.match(r"^\s*[-*+]\s", prev_line)  # Not a list item
                    and not re.match(r"^\s*\d+\.\s", prev_line)  # Not a numbered list item
                    and not prev_line.strip().startswith("#")  # Not a header
                    and not prev_line.strip().startswith("```")  # Not code block
                    and not prev_line.strip().startswith(">")  # Not blockquote
                    and not prev_line.strip().startswith("!")  # Not admonition
                    and prev_line.strip().endswith(":")  # Must end with colon
                    and len(prev_line.strip()) > 15  # Must be substantial text (avoid short labels)
                    and not re.search(r"\b(where|through|include[sd]?|such as|benefits?|coefficients?|principles?|analysis|reduction|fields?|values?|types?|inputs?|store|remain|accept|contain|decimal)\b.*:$", prev_line.strip(), re.IGNORECASE)  # Not technical documentation patterns
                ):
                    issues.append(
                        ValidationIssue(
                            message="List should be separated from preceding text with a blank line",
                            file_path=file_path,
                            line=line_num,
                            severity=IssueSeverity.WARNING,
                            rule_id="markdown_list_spacing",
                            context=f"Previous line: '{prev_line.strip()}' → List: '{line.strip()}'",
                            suggestion="Add a blank line before the list to ensure proper Markdown rendering",
                        )
                    )

        return issues

    def _check_unclosed_code_blocks(self, lines: list[str], file_path: Path) -> list[ValidationIssue]:
        """Check for unclosed fenced code blocks."""
        issues: list[ValidationIssue] = []

        fence_stack: list[int] = []
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if fence_stack:
                    # Closing a code block
                    fence_stack.pop()
                else:
                    # Opening a code block
                    fence_stack.append(line_num)

        # Any remaining items in stack are unclosed
        issues.extend([ValidationIssue(message="Unclosed code block", file_path=file_path, line=line_num, severity=IssueSeverity.ERROR, rule_id="markdown_unclosed_code_block", context=f"Code block opened at line {line_num}", suggestion="Add closing ``` to end the code block") for line_num in fence_stack])

        return issues

    def get_file_patterns(self) -> list[str]:
        """Get patterns for files this validator handles."""
        return ["**/*.md", "**/*.markdown"]
