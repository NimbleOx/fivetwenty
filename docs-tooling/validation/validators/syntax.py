"""
Syntax validation for documentation.

Validates markdown syntax and structure in documentation files.
"""

import sys
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class SyntaxValidator(FileValidator):  # type: ignore[misc]
    """Validates syntax in markdown files."""

    def __init__(self) -> None:
        super().__init__(name="syntax_validator", description="Validates markdown syntax and structure", file_patterns=["docs/**/*.md", "*.md"])
        self.syntax_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate syntax in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)

        for file_path in files:
            self._check_file_syntax(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.syntax_issues) == 0 else "failed",
            issues_found=len(self.syntax_issues),
            total_checked=total_files,
            details={"syntax_issues": self.syntax_issues, "files_checked": total_files},
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _check_file_syntax(self, file_path: Path) -> None:
        """Check syntax in a single file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Check for unmatched code blocks
            if "```" in content:
                code_blocks = content.count("```")
                if code_blocks % 2 != 0:
                    issue = {"file": str(file_path), "type": "unmatched_code_block", "message": "Unmatched code block delimiters"}
                    self.syntax_issues.append(issue)
                    self.add_issue("Unmatched code block delimiters", str(file_path))

            # Additional syntax checks can be added here
            self._check_heading_structure(content, file_path)
            self._check_list_syntax(content, file_path)
            self._check_ascii_diagrams(content, file_path)

        except Exception as e:
            issue = {"file": str(file_path), "type": "read_error", "message": f"Could not read file: {e}"}
            self.syntax_issues.append(issue)
            self.add_issue(f"Error reading file: {e}", str(file_path))

    def _check_heading_structure(self, content: str, file_path: Path) -> None:
        """Check for proper heading structure."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            if line.startswith("#"):
                # Count heading level
                level = len(line) - len(line.lstrip("#"))
                if level > 6:  # Max heading level in markdown
                    issue = {"file": str(file_path), "line": line_num, "type": "invalid_heading_level", "message": f"Invalid heading level {level} (max 6)"}
                    self.syntax_issues.append(issue)
                    self.add_issue(f"Invalid heading level {level} (max 6)", str(file_path), line_num)

                # Check for heading text after #
                heading_text = line[level:].strip()
                if not heading_text:
                    issue = {"file": str(file_path), "line": line_num, "type": "empty_heading", "message": "Empty heading"}
                    self.syntax_issues.append(issue)
                    self.add_issue("Empty heading", str(file_path), line_num)

    def _check_list_syntax(self, content: str, file_path: Path) -> None:
        """Check for proper list syntax."""
        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()

            # Check for malformed bullet lists
            if stripped.startswith(("-", "*", "+")):
                # Skip markdown formatting (bold/italic) - these start with multiple * or _
                if stripped.startswith(("**", "__")):
                    continue

                # Skip horizontal rules (---, ***, +++)
                if stripped in ("---", "***", "+++") or len(set(stripped)) == 1:
                    continue

                # Should have space after bullet
                if len(stripped) > 1 and stripped[1] != " ":
                    issue = {"file": str(file_path), "line": line_num, "type": "malformed_list_item", "message": "List item should have space after bullet"}
                    self.syntax_issues.append(issue)
                    self.add_issue("List item should have space after bullet", str(file_path), line_num)

            # Check for malformed numbered lists - only match patterns like "1.text" or "2.text"
            if stripped and stripped[0].isdigit():
                # Look for dot immediately after number sequence (with possible whitespace)
                import re
                numbered_list_pattern = r"^(\d+)\.(\S)"  # number, dot, non-space character
                match = re.match(numbered_list_pattern, stripped)

                if match:
                    # This looks like a numbered list item without space after dot
                    issue = {"file": str(file_path), "line": line_num, "type": "malformed_numbered_list", "message": "Numbered list item should have space after dot"}
                    self.syntax_issues.append(issue)
                    self.add_issue("Numbered list item should have space after dot", str(file_path), line_num)

    def _check_ascii_diagrams(self, content: str, file_path: Path) -> None:
        """Check ASCII diagrams for consistency and alignment."""
        lines = content.split("\n")

        # Look for ASCII diagram patterns
        diagram_markers = [
            "┌", "┐", "└", "┘", "│", "─", "├", "┤", "┬", "┴", "┼",  # Box drawing
            "╔", "╗", "╚", "╝", "║", "═", "╠", "╣", "╦", "╩", "╬",  # Double box drawing
            "▲", "▼", "◆", "●", "■", "□", "▓", "░",  # Symbols
        ]

        in_diagram = False
        diagram_start_line = 0
        diagram_lines = []

        for line_num, line in enumerate(lines, 1):
            has_diagram_chars = any(marker in line for marker in diagram_markers)

            # Detect start of diagram
            if has_diagram_chars and not in_diagram:
                in_diagram = True
                diagram_start_line = line_num
                diagram_lines = [line]
            elif has_diagram_chars and in_diagram:
                diagram_lines.append(line)
            elif not has_diagram_chars and in_diagram:
                # End of diagram, validate it
                self._validate_ascii_diagram(file_path, diagram_lines, diagram_start_line)
                in_diagram = False
                diagram_lines = []
            elif in_diagram and not line.strip():
                # Empty line in diagram is okay
                diagram_lines.append(line)

        # Check final diagram if file ends with one
        if in_diagram and diagram_lines:
            self._validate_ascii_diagram(file_path, diagram_lines, diagram_start_line)

    def _validate_ascii_diagram(self, file_path: Path, diagram_lines: list[str], start_line: int) -> None:
        """Validate a single ASCII diagram."""
        if len(diagram_lines) < 2:  # Too small to be a meaningful diagram
            return

        # Check for alignment issues in box diagrams
        self._check_box_alignment(file_path, diagram_lines, start_line)

        # Check for consistent border styles
        self._check_border_consistency(file_path, diagram_lines, start_line)

        # Check for orphaned characters
        self._check_orphaned_characters(file_path, diagram_lines, start_line)

    def _check_box_alignment(self, file_path: Path, diagram_lines: list[str], start_line: int) -> None:
        """Check alignment of box drawing characters."""
        # Find vertical lines and check they align
        vertical_positions = {}  # position -> line_numbers

        for i, line in enumerate(diagram_lines):
            for pos, char in enumerate(line):
                if char in "│║":
                    if pos not in vertical_positions:
                        vertical_positions[pos] = []
                    vertical_positions[pos].append(start_line + i)

        # Check for misaligned vertical lines (single occurrences might be errors)
        for pos, line_nums in vertical_positions.items():
            if len(line_nums) == 1:
                issue = {
                    "file": str(file_path),
                    "line": line_nums[0],
                    "type": "misaligned_diagram",
                    "message": f"Orphaned vertical line character at position {pos} might be misaligned"
                }
                self.syntax_issues.append(issue)
                self.add_issue(f"Orphaned vertical line character at position {pos}", str(file_path), line_nums[0])

    def _check_border_consistency(self, file_path: Path, diagram_lines: list[str], start_line: int) -> None:
        """Check for consistent border character styles."""
        single_line_chars = set("┌┐└┘│─├┤┬┴┼")
        double_line_chars = set("╔╗╚╝║═╠╣╦╩╬")

        has_single = any(any(c in line for c in single_line_chars) for line in diagram_lines)
        has_double = any(any(c in line for c in double_line_chars) for line in diagram_lines)

        if has_single and has_double:
            issue = {
                "file": str(file_path),
                "line": start_line,
                "type": "mixed_border_styles",
                "message": "ASCII diagram mixes single and double line border styles"
            }
            self.syntax_issues.append(issue)
            self.add_issue("Mixed border styles in ASCII diagram", str(file_path), start_line)

    def _check_orphaned_characters(self, file_path: Path, diagram_lines: list[str], start_line: int) -> None:
        """Check for orphaned or incomplete diagram characters."""
        # Characters that typically should have neighbors
        corner_chars = "┌┐└┘╔╗╚╝"
        junction_chars = "├┤┬┴┼╠╣╦╩╬"

        for i, line in enumerate(diagram_lines):
            for pos, char in enumerate(line):
                if char in corner_chars or char in junction_chars:
                    # Check if this character has appropriate neighbors
                    neighbors = self._get_diagram_neighbors(diagram_lines, i, pos)

                    # Corner characters should have 2 connecting sides
                    if char in corner_chars:
                        expected_connections = 2
                        if char in "┌╔": expected_connections = self._count_connections(neighbors, ["right", "down"])
                        elif char in "┐╗": expected_connections = self._count_connections(neighbors, ["left", "down"])
                        elif char in "└╚": expected_connections = self._count_connections(neighbors, ["right", "up"])
                        elif char in "┘╝": expected_connections = self._count_connections(neighbors, ["left", "up"])

                        if expected_connections < 1:  # At least one connection expected
                            issue = {
                                "file": str(file_path),
                                "line": start_line + i,
                                "type": "orphaned_corner",
                                "message": f"Corner character '{char}' appears isolated"
                            }
                            self.syntax_issues.append(issue)
                            self.add_issue(f"Isolated corner character '{char}'", str(file_path), start_line + i)

    def _get_diagram_neighbors(self, diagram_lines: list[str], row: int, col: int) -> dict[str, str]:
        """Get neighboring characters in the diagram."""
        neighbors = {"up": " ", "down": " ", "left": " ", "right": " "}

        if row > 0 and col < len(diagram_lines[row - 1]):
            neighbors["up"] = diagram_lines[row - 1][col]
        if row < len(diagram_lines) - 1 and col < len(diagram_lines[row + 1]):
            neighbors["down"] = diagram_lines[row + 1][col]
        if col > 0:
            neighbors["left"] = diagram_lines[row][col - 1]
        if col < len(diagram_lines[row]) - 1:
            neighbors["right"] = diagram_lines[row][col + 1]

        return neighbors

    def _count_connections(self, neighbors: dict[str, str], directions: list[str]) -> int:
        """Count how many of the specified directions have connecting characters."""
        connecting_chars = "│─║═┌┐└┘├┤┬┴┼╔╗╚╝╠╣╦╩╬"
        count = 0

        for direction in directions:
            if neighbors[direction] in connecting_chars:
                count += 1

        return count
