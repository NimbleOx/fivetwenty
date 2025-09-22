"""Educational progression validation checks."""

import re
from pathlib import Path
from typing import Any

from docs_validation.validation.checks.base import ContentCheck
from docs_validation.validation.core.context import ValidationContext
from docs_validation.validation.core.results import IssueSeverity, ValidationIssue, ValidationResult


class EducationalProgressionCheck(ContentCheck):
    """Check that tutorial content follows progressive learning patterns."""

    def __init__(self) -> None:
        super().__init__(
            name="educational_progression",
            description="Validates progressive learning patterns and complexity building",
            file_patterns=["docs/tutorials/**/*.md"],
            required_extensions=[".md"],
        )

        # Complexity indicators for different skill levels
        self.complexity_patterns = {
            "beginner": {"concepts": ["account", "client", "environment", "basic", "simple", "first", "getting started"], "methods": ["get_accounts", "get_instruments", "get_pricing"], "max_code_lines": 20, "max_imports": 3, "forbidden_concepts": ["strategy", "portfolio", "optimization", "complex", "advanced"]},
            "intermediate": {"concepts": ["order", "position", "streaming", "async", "error handling"], "methods": ["post_order", "stream_pricing", "get_positions"], "max_code_lines": 50, "max_imports": 6, "forbidden_concepts": ["enterprise", "production", "sophisticated"]},
            "advanced": {
                "concepts": ["portfolio", "risk management", "strategy", "optimization"],
                "methods": ["multiple orders", "complex strategies", "custom classes"],
                "max_code_lines": 100,
                "max_imports": 10,
                "forbidden_concepts": [],  # Advanced can use anything
            },
        }

        # Learning pathway progression
        self.expected_progression = ["installation", "authentication", "first", "basic", "account", "instruments", "pricing", "orders", "positions", "streaming", "async", "strategies"]

        # Tutorial quality indicators
        self.quality_patterns = {
            "learning_outcomes": ["you will learn", "by the end", "after completing", "learning objective", "skills you'll gain"],
            "checkpoints": ["checkpoint", "test your understanding", "verify", "skill check", "practice"],
            "progressive_examples": ["building on", "next step", "now that you know", "extending", "advanced version"],
        }

    def check_content(
        self,
        file_path: Path,
        content: str,
        context: ValidationContext,
        result: ValidationResult,
    ) -> None:
        """Check educational progression in tutorial content."""
        # Determine tutorial difficulty level
        difficulty = self._determine_difficulty_level(content, file_path)

        # Check complexity appropriateness
        self._check_complexity_level(file_path, content, difficulty, result)

        # Check for learning structure
        self._check_learning_structure(file_path, content, result)

        # Check for progressive building
        self._check_progressive_building(file_path, content, result)

    def _determine_difficulty_level(self, content: str, file_path: Path) -> str:
        """Determine the intended difficulty level of the tutorial."""
        content_lower = content.lower()
        file_name_lower = str(file_path).lower()

        # Check file path and name for difficulty indicators
        if any(indicator in file_name_lower for indicator in ["beginner", "first", "basic", "getting-started"]):
            return "beginner"
        elif any(indicator in file_name_lower for indicator in ["advanced", "expert", "production"]):
            return "advanced"

        # Check content for difficulty indicators
        beginner_score = sum(1 for concept in self.complexity_patterns["beginner"]["concepts"] if concept in content_lower)
        intermediate_score = sum(1 for concept in self.complexity_patterns["intermediate"]["concepts"] if concept in content_lower)
        advanced_score = sum(1 for concept in self.complexity_patterns["advanced"]["concepts"] if concept in content_lower)

        if advanced_score > intermediate_score and advanced_score > beginner_score:
            return "advanced"
        elif intermediate_score > beginner_score:
            return "intermediate"
        else:
            return "beginner"

    def _check_complexity_level(
        self,
        file_path: Path,
        content: str,
        difficulty: str,
        result: ValidationResult,
    ) -> None:
        """Check if content complexity matches the intended difficulty level."""
        patterns = self.complexity_patterns[difficulty]

        # Check code complexity
        code_blocks = self._extract_python_code_blocks(content)
        for block_info in code_blocks:
            code = block_info["content"]
            line_count = len([line for line in code.split("\n") if line.strip()])
            import_count = len([line for line in code.split("\n") if "import" in line])

            if line_count > patterns["max_code_lines"]:
                result.add_issue(
                    message=f"Code block too complex for {difficulty} level ({line_count} lines > {patterns['max_code_lines']})",
                    file_path=str(file_path),
                    line=block_info["start_line"],
                    severity=IssueSeverity.WARNING,
                    suggestion=f"Break into smaller examples or move to higher difficulty level",
                    context={"line": ""},
                )

            if import_count > patterns["max_imports"]:
                result.add_issue(
                    message=f"Too many imports for {difficulty} level ({import_count} > {patterns['max_imports']})",
                    file_path=str(file_path),
                    line=block_info["start_line"],
                    severity=IssueSeverity.WARNING,
                    suggestion="Simplify the example or move to higher difficulty level",
                    context={"line": ""},
                )

        # Check for forbidden concepts
        content_lower = content.lower()
        for forbidden_concept in patterns["forbidden_concepts"]:
            if forbidden_concept in content_lower:
                result.add_issue(
                    message=f"Concept '{forbidden_concept}' may be too advanced for {difficulty} level",
                    file_path=str(file_path),
                    line=1,
                    severity=IssueSeverity.WARNING,
                    suggestion=f"Consider moving to higher difficulty level or simplifying",
                    context={"line": ""},
                )

    def _check_learning_structure(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check for proper learning structure elements."""
        content_lower = content.lower()

        # Check for learning outcomes
        has_learning_outcomes = any(pattern in content_lower for pattern in self.quality_patterns["learning_outcomes"])

        if not has_learning_outcomes:
            result.add_issue(
                message="Tutorial lacks clear learning outcomes",
                file_path=str(file_path),
                line=1,
                severity=IssueSeverity.WARNING,
                suggestion="Add section explaining what learners will achieve",
                context={"line": ""},
            )

        # Check for checkpoints
        has_checkpoints = any(pattern in content_lower for pattern in self.quality_patterns["checkpoints"])

        if not has_checkpoints and len(content) > 1000:  # Only for longer tutorials
            result.add_issue(
                message="Long tutorial lacks learning checkpoints",
                file_path=str(file_path),
                line=1,
                severity=IssueSeverity.INFO,
                suggestion="Add checkpoints to help learners verify understanding",
                context={"line": ""},
            )

    def _check_progressive_building(
        self,
        file_path: Path,
        content: str,
        result: ValidationResult,
    ) -> None:
        """Check for progressive complexity building."""
        content_lower = content.lower()

        # Check for progressive building language
        has_progressive_building = any(pattern in content_lower for pattern in self.quality_patterns["progressive_examples"])

        # For multi-part tutorials, progressive building is more important
        if ("part" in str(file_path).lower() or "chapter" in content_lower) and not has_progressive_building:
            result.add_issue(
                message="Multi-part tutorial lacks progressive building language",
                file_path=str(file_path),
                line=1,
                severity=IssueSeverity.INFO,
                suggestion="Use phrases like 'building on', 'next step', 'now that you know'",
                context={"line": ""},
            )

        # Check for concept progression
        code_blocks = self._extract_python_code_blocks(content)
        if len(code_blocks) > 1:
            # Simple heuristic: later code blocks should generally be longer or more complex
            first_block_lines = len([line for line in code_blocks[0]["content"].split("\n") if line.strip()])
            last_block_lines = len([line for line in code_blocks[-1]["content"].split("\n") if line.strip()])

            if last_block_lines < first_block_lines and len(code_blocks) > 2:
                result.add_issue(
                    message="Tutorial may not build complexity progressively",
                    file_path=str(file_path),
                    line=code_blocks[-1]["start_line"],
                    severity=IssueSeverity.INFO,
                    suggestion="Consider ordering examples from simple to complex",
                    context={"line": ""},
                )

    def _extract_python_code_blocks(self, content: str) -> list[dict[str, Any]]:
        """Extract Python code blocks with metadata."""
        blocks = []
        lines = content.split("\n")
        in_python_block = False
        current_block_lines = []
        block_start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith("```python"):
                in_python_block = True
                current_block_lines = []
                block_start_line = line_num + 1
            elif line.strip() == "```" and in_python_block:
                if current_block_lines:
                    blocks.append({"content": "\n".join(current_block_lines), "start_line": block_start_line, "end_line": line_num - 1, "lines": current_block_lines})
                in_python_block = False
            elif in_python_block:
                current_block_lines.append(line)

        return blocks
