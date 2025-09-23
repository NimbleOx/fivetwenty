"""Markdown syntax validation."""

import re
from pathlib import Path

from validation.checks.base import ContentCheck
from validation.core.context import ValidationContext
from validation.core.results import IssueSeverity, ValidationResult


class MarkdownSyntaxCheck(ContentCheck):
    """Check markdown syntax and structure."""

    def __init__(self) -> None:
        super().__init__(
            name="markdown_syntax",
            description="Validates markdown syntax and structure",
            file_patterns=["**/*.md"],
            required_extensions=[".md"],
        )

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check markdown content for syntax issues."""
        lines = content.split("\n")

        # Check for common markdown issues
        self._check_headers(file_path, lines, result)
        self._check_links(file_path, lines, result)
        self._check_code_blocks(file_path, lines, result)
        self._check_tables(file_path, lines, result)
        self._check_line_endings(file_path, content, result)

    def _check_headers(self, file_path: Path, lines: list[str], result: ValidationResult) -> None:
        """Check header structure."""
        header_levels = []

        for line_num, line in enumerate(lines, 1):
            if line.startswith("#"):
                # Count header level
                level = len(line) - len(line.lstrip("#"))
                if level > 6:
                    result.add_issue(
                        message="Header level too deep (max 6)",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                        rule="header_depth",
                    )
                    continue

                # Check for space after #
                if level > 0 and len(line) > level and line[level] != " ":
                    result.add_issue(
                        message="Header should have space after #",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.WARNING,
                        rule="header_spacing",
                        suggestion=f"Change to: {'#' * level} {line[level:]}",
                    )

                header_levels.append((level, line_num))

        # Check header sequence
        self._check_header_sequence(file_path, header_levels, result)

    def _check_header_sequence(
        self,
        file_path: Path,
        header_levels: list[tuple[int, int]],
        result: ValidationResult,
    ) -> None:
        """Check if headers follow logical sequence."""
        if len(header_levels) < 2:
            return

        for i in range(1, len(header_levels)):
            current_level, current_line = header_levels[i]
            prev_level, _ = header_levels[i - 1]

            # Check for skipped levels
            if current_level > prev_level + 1:
                result.add_issue(
                    message=f"Header level jumps from {prev_level} to {current_level}",
                    file_path=str(file_path),
                    line=current_line,
                    severity=IssueSeverity.WARNING,
                    rule="header_sequence",
                    suggestion=f"Consider using level {prev_level + 1} instead",
                )

    def _check_links(self, file_path: Path, lines: list[str], result: ValidationResult) -> None:
        """Check link syntax."""
        link_pattern = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
        reference_pattern = re.compile(r"\[([^\]]*)\]\[([^\]]*)\]")

        for line_num, line in enumerate(lines, 1):
            # Check inline links
            for match in link_pattern.finditer(line):
                link_text, link_url = match.groups()

                if not link_text.strip():
                    result.add_issue(
                        message="Link has empty text",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.WARNING,
                        rule="link_text",
                    )

                if not link_url.strip():
                    result.add_issue(
                        message="Link has empty URL",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.ERROR,
                        rule="link_url",
                    )

            # Check reference links
            for match in reference_pattern.finditer(line):
                link_text, _reference = match.groups()

                if not link_text.strip():
                    result.add_issue(
                        message="Reference link has empty text",
                        file_path=str(file_path),
                        line=line_num,
                        severity=IssueSeverity.WARNING,
                        rule="reference_link_text",
                    )

    def _check_code_blocks(self, file_path: Path, lines: list[str], result: ValidationResult) -> None:
        """Check code block syntax."""
        in_code_block = False
        code_block_start = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_block_start = line_num

                    # Check for language specification
                    if line.strip() == "```":
                        result.add_issue(
                            message="Code block missing language specification",
                            file_path=str(file_path),
                            line=line_num,
                            severity=IssueSeverity.INFO,
                            rule="code_block_language",
                            suggestion="Add language after ``` (e.g., ```python)",
                        )

        # Check for unclosed code blocks
        if in_code_block:
            result.add_issue(
                message="Unclosed code block",
                file_path=str(file_path),
                line=code_block_start,
                severity=IssueSeverity.ERROR,
                rule="unclosed_code_block",
            )

    def _check_tables(self, file_path: Path, lines: list[str], result: ValidationResult) -> None:
        """Check table syntax."""
        in_table = False
        header_columns = 0

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            if "|" in stripped and stripped.startswith("|") and stripped.endswith("|"):
                if not in_table:
                    # Start of table
                    in_table = True
                    header_columns = stripped.count("|") - 1

                    if header_columns == 0:
                        result.add_issue(
                            message="Table header has no columns",
                            file_path=str(file_path),
                            line=line_num,
                            severity=IssueSeverity.ERROR,
                            rule="table_columns",
                        )

                else:
                    # Table row
                    row_columns = stripped.count("|") - 1

                    # Check for separator row
                    if re.match(r"^\|[\s\-:]+\|$", stripped):
                        continue

                    # Check column count consistency
                    if row_columns != header_columns:
                        result.add_issue(
                            message=f"Table row has {row_columns} columns, header has {header_columns}",
                            file_path=str(file_path),
                            line=line_num,
                            severity=IssueSeverity.WARNING,
                            rule="table_column_mismatch",
                        )

            elif in_table and stripped:
                # End of table (non-empty line without |)
                in_table = False

    def _check_line_endings(self, file_path: Path, content: str, result: ValidationResult) -> None:
        """Check for consistent line endings."""
        if "\r\n" in content and "\n" in content.replace("\r\n", ""):
            result.add_issue(
                message="Mixed line endings detected",
                file_path=str(file_path),
                severity=IssueSeverity.WARNING,
                rule="line_endings",
                suggestion="Use consistent line endings (preferably LF)",
            )
