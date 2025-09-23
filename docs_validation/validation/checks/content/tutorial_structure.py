"""Tutorial structure validation checks."""

from pathlib import Path
from typing import Any

from validation.checks.base import ContentCheck
from validation.core.context import ValidationContext
from validation.core.results import IssueSeverity, ValidationIssue, ValidationResult


class TutorialStructureCheck(ContentCheck):
    """Check that tutorial content follows educational best practices and proper structure."""

    def __init__(self) -> None:
        super().__init__(
            name="tutorial_structure",
            description="Validates tutorial content follows educational best practices and proper structure",
            file_patterns=["docs/tutorials/**/*.md"],
            required_extensions=[".md"],
        )

        # Tutorial structure requirements based on educational best practices
        self.required_sections = {
            "learning_outcomes": ["learning objective", "learning outcome", "you will learn", "by the end", "after completing", "skills you'll gain"],
            "prerequisites": ["prerequisite", "before starting", "requirements", "what you need", "you should know", "familiarity with"],
            "time_estimate": ["time commitment", "duration", "estimated time", "time required", "approximately", "takes about", "expect to spend"],
            "hands_on_exercises": ["hands-on", "exercise", "try this", "practice", "tutorial", "let's build", "follow along"],
            "checkpoints": ["checkpoint", "test your understanding", "verify", "skill check", "recap", "summary", "what we covered"],
        }

        # Progressive difficulty indicators
        self.difficulty_indicators = {"beginner": ["getting started", "first", "basic", "introduction", "simple"], "intermediate": ["advanced", "complex", "comprehensive", "in-depth"], "advanced": ["expert", "production", "sophisticated", "enterprise"]}

        # Educational structure patterns
        self.structure_patterns = {
            "introduction": ["introduction", "overview", "what is", "why use"],
            "motivation": ["why", "benefits", "use case", "real-world"],
            "step_by_step": ["step 1", "step 2", "first", "next", "then", "finally"],
            "explanation": ["how it works", "under the hood", "explanation", "details"],
            "troubleshooting": ["troubleshooting", "common issues", "problems", "errors"],
        }

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check tutorial structure and educational content standards."""
        # Check for required sections
        self._check_required_sections(file_path, content, result)

        # Check tutorial structure
        self._check_tutorial_structure(file_path, content, result)

        # Check heading hierarchy
        self._check_heading_hierarchy(file_path, content, result)

        # Check code-to-text ratio
        self._check_code_text_balance(file_path, content, result)

    def _check_required_sections(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check for required tutorial sections."""
        content_lower = content.lower()
        missing_sections = []

        for section_name, patterns in self.required_sections.items():
            has_section = any(pattern in content_lower for pattern in patterns)
            if not has_section:
                missing_sections.append(section_name)

        # Be less strict for short tutorials
        if len(content) < 500:  # Short tutorial
            # Only require learning outcomes for short tutorials
            if "learning_outcomes" in missing_sections:
                result.add_issue(
                    message="Tutorial lacks clear learning outcomes",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.WARNING,
                    suggestion="Add section explaining what learners will achieve",
                    context={"line": ""},
                )
        else:
            # Longer tutorials should have more structure
            for section in missing_sections:
                if section in ["learning_outcomes", "prerequisites"]:
                    severity = IssueSeverity.WARNING
                else:
                    severity = IssueSeverity.INFO

                result.add_issue(
                    message=f"Tutorial missing recommended section: {section}",
                    file_path=str(file_path),
                    line=1,
                    severity=severity,
                    suggestion=f"Consider adding {section.replace('_', ' ')} section",
                    context={"line": ""},
                )

    def _check_tutorial_structure(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check overall tutorial structure patterns."""
        content_lower = content.lower()

        # Check for step-by-step structure
        has_steps = any(pattern in content_lower for pattern in self.structure_patterns["step_by_step"])

        # Check for motivation/why section
        has_motivation = any(pattern in content_lower for pattern in self.structure_patterns["motivation"])

        # For tutorials longer than 1000 characters, expect clear structure
        if len(content) > 1000:
            if not has_steps:
                result.add_issue(
                    message="Tutorial lacks clear step-by-step structure",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.INFO,
                    suggestion="Consider organizing content with numbered steps or clear progression",
                    context={"line": ""},
                )

            if not has_motivation:
                result.add_issue(
                    message="Tutorial lacks motivation or 'why' section",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.INFO,
                    suggestion="Explain why this tutorial is useful or what problems it solves",
                    context={"line": ""},
                )

    def _check_heading_hierarchy(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check heading hierarchy for logical structure."""
        lines = content.split("\n")
        headings = []

        # Extract headings with their levels and line numbers
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                heading_text = line.lstrip("#").strip()
                headings.append({"level": level, "text": heading_text, "line_number": line_num})

        # Check for skipped heading levels
        if len(headings) > 1:
            for i in range(1, len(headings)):
                current_level = headings[i]["level"]
                previous_level = headings[i - 1]["level"]

                # Skip from h1 to h3+ is problematic
                if current_level - previous_level > 1:
                    result.add_issue(
                        message=f"Heading hierarchy skip: h{previous_level} to h{current_level}",
                        file_path=str(file_path),
                        line=headings[i]["line_number"],
                        severity=IssueSeverity.WARNING,
                        suggestion="Use consecutive heading levels for better structure",
                        context={"line": f"{'#' * current_level} {headings[i]['text']}"},
                    )

        # Check for single h1 rule
        h1_count = sum(1 for h in headings if h["level"] == 1)
        if h1_count > 1:
            result.add_issue(
                ValidationIssue(
                    file_path=file_path,
                    line_number=1,
                    severity=IssueSeverity.WARNING,
                    message=f"Multiple h1 headings found ({h1_count})",
                    suggestion="Use only one h1 heading per tutorial",
                    context_line="",
                )
            )

    def _check_code_text_balance(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check balance between code examples and explanatory text."""
        # Extract code blocks
        code_blocks = self._extract_code_blocks(content)
        total_code_lines = sum(len(block["content"].split("\n")) for block in code_blocks)

        # Calculate text lines (excluding code blocks and empty lines)
        lines = content.split("\n")
        text_lines = 0
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
            elif not in_code_block and line.strip():
                text_lines += 1

        # Check ratio
        if total_code_lines > 0 and text_lines > 0:
            code_ratio = total_code_lines / (total_code_lines + text_lines)

            # Too much code (>70%) might be overwhelming
            if code_ratio > 0.7:
                result.add_issue(
                    message=f"High code-to-text ratio ({code_ratio:.1%})",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.INFO,
                    suggestion="Consider adding more explanatory text between code examples",
                    context={"line": ""},
                )

            # Too little code (<10%) might not be practical enough
            elif code_ratio < 0.1:
                result.add_issue(
                    message=f"Low code-to-text ratio ({code_ratio:.1%})",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.INFO,
                    suggestion="Consider adding more practical code examples",
                    context={"line": ""},
                )

    def _extract_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract all code blocks from content."""
        blocks = []
        lines = content.split("\n")
        in_code_block = False
        current_block_lines = []
        block_start_line = 0
        block_language = ""

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    blocks.append({"content": "\n".join(current_block_lines), "start_line": block_start_line, "end_line": line_num, "language": block_language})
                    in_code_block = False
                    current_block_lines = []
                else:
                    # Start of code block
                    in_code_block = True
                    block_start_line = line_num + 1
                    block_language = line.strip()[3:].strip()
                    current_block_lines = []
            elif in_code_block:
                current_block_lines.append(line)

        return blocks
