#!/usr/bin/env python3
"""
Educational Progression Validator

Validates that tutorial content follows progressive learning patterns and
builds complexity appropriately for educational effectiveness.
Based on lessons learned from comprehensive tutorial validation.
"""

import re
from pathlib import Path
from typing import Any

from core.base import BaseValidator, ValidationResult


class EducationalProgressionValidator(BaseValidator):
    """Validate educational progression and complexity building in tutorials."""

    def __init__(self):
        super().__init__("educational_progression", "Validates progressive learning patterns and complexity building")
        self.validator_name = "educational_progression"
        self.file_patterns = ["docs/tutorials/**/*.md"]
        self.progression_issues: list[dict[str, Any]] = []

        # Complexity indicators for different skill levels
        self.complexity_patterns = {
            "beginner": {
                "concepts": ["account", "client", "environment", "basic", "simple"],
                "methods": ["get_accounts", "get_instruments", "get_pricing"],
                "max_code_lines": 20,
                "max_imports": 3
            },
            "intermediate": {
                "concepts": ["order", "position", "streaming", "async", "error handling"],
                "methods": ["post_order", "stream_pricing", "get_positions"],
                "max_code_lines": 50,
                "max_imports": 6
            },
            "advanced": {
                "concepts": ["portfolio", "risk management", "strategy", "optimization"],
                "methods": ["multiple orders", "complex strategies", "custom classes"],
                "max_code_lines": 100,
                "max_imports": 10
            }
        }

        # Learning pathway progression
        self.expected_progression = [
            "installation", "authentication", "first", "basic",
            "advanced", "risk", "portfolio", "streaming"
        ]

    def validate(self) -> ValidationResult:
        """Run educational progression validation."""
        tutorial_files = self._find_tutorial_files()
        total_checked = len(tutorial_files)

        for file_path in tutorial_files:
            file_issues = self._validate_tutorial_progression(file_path)
            self.progression_issues.extend(file_issues)

        status = "passed" if len(self.progression_issues) == 0 else "failed"

        return ValidationResult(
            validator_name=self.validator_name,
            status=status,
            issues_found=len(self.progression_issues),
            total_checked=total_checked,
            details={
                "files_checked": total_checked,
                "progression_issues": self.progression_issues,
                "validation_focus": "Educational progression and complexity building"
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _find_tutorial_files(self) -> list[Path]:
        """Find all tutorial files to validate."""
        tutorial_files = []

        for pattern in self.file_patterns:
            tutorial_files.extend(Path().glob(pattern))

        return [f for f in tutorial_files if f.is_file()]

    def _validate_tutorial_progression(self, file_path: Path) -> list[dict[str, Any]]:
        """Validate progression of a single tutorial file."""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8')

            # Skip index files
            if file_path.name == "index.md":
                return []

            # Determine intended skill level from path and content
            skill_level = self._determine_skill_level(file_path, content)

            # Check complexity appropriateness
            issues.extend(self._check_complexity_appropriateness(content, file_path, skill_level))

            # Check code example progression within the tutorial
            issues.extend(self._check_internal_progression(content, file_path))

            # Check prerequisite alignment
            issues.extend(self._check_prerequisite_alignment(content, file_path, skill_level))

            # Check learning scaffolding
            issues.extend(self._check_learning_scaffolding(content, file_path))

        except Exception as e:
            issues.append({
                "type": "file_error",
                "severity": "error",
                "message": f"Could not validate educational progression: {e}",
                "file": str(file_path)
            })

        return issues

    def _determine_skill_level(self, file_path: Path, content: str) -> str:
        """Determine the intended skill level of a tutorial."""
        path_str = str(file_path).lower()
        content.lower()

        # Check path indicators
        if "getting-started" in path_str or "first" in path_str or "installation" in path_str:
            return "beginner"
        if "advanced" in path_str or "risk" in path_str or "portfolio" in path_str:
            return "advanced"
        return "intermediate"

    def _check_complexity_appropriateness(self, content: str, file_path: Path, skill_level: str) -> list[dict[str, Any]]:
        """Check if complexity matches intended skill level."""
        issues = []
        complexity_config = self.complexity_patterns[skill_level]

        # Extract code blocks for analysis
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

        if code_blocks:
            for i, block in enumerate(code_blocks):
                lines = len(block.split('\n'))
                imports = len(re.findall(r'^(from|import)\s+', block, re.MULTILINE))

                # Check if complexity exceeds level expectations
                if lines > complexity_config["max_code_lines"]:
                    issues.append({
                        "type": "excessive_complexity",
                        "severity": "warning",
                        "message": f"Code block {i+1} has {lines} lines, exceeding {skill_level} level expectation of {complexity_config['max_code_lines']}",
                        "suggestion": f"Consider breaking complex examples into smaller steps for {skill_level} learners",
                        "file": str(file_path)
                    })

                if imports > complexity_config["max_imports"]:
                    issues.append({
                        "type": "excessive_imports",
                        "severity": "info",
                        "message": f"Code block {i+1} has {imports} imports, which may overwhelm {skill_level} learners",
                        "suggestion": "Consider introducing imports gradually or explaining their purpose",
                        "file": str(file_path)
                    })

        return issues

    def _check_internal_progression(self, content: str, file_path: Path) -> list[dict[str, Any]]:
        """Check progression within a single tutorial."""
        issues = []
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

        if len(code_blocks) > 2:
            # Check that examples build on each other
            first_block = code_blocks[0]
            last_block = code_blocks[-1]

            # Simple heuristic: later examples should introduce new concepts
            first_functions = set(re.findall(r'(\w+)\(', first_block))
            last_functions = set(re.findall(r'(\w+)\(', last_block))

            if len(last_functions) <= len(first_functions):
                issues.append({
                    "type": "lack_of_progression",
                    "severity": "info",
                    "message": "Code examples don't show clear progression in complexity or functionality",
                    "suggestion": "Each example should introduce new concepts or build on previous ones",
                    "file": str(file_path)
                })

            # Check for abrupt complexity jumps
            block_complexities = []
            for block in code_blocks:
                complexity = len(block.split('\n')) + len(re.findall(r'(\w+)\(', block))
                block_complexities.append(complexity)

            for i in range(1, len(block_complexities)):
                if block_complexities[i] > block_complexities[i-1] * 2:
                    issues.append({
                        "type": "complexity_jump",
                        "severity": "warning",
                        "message": f"Abrupt complexity increase between code examples {i} and {i+1}",
                        "suggestion": "Add intermediate examples to bridge complexity gaps",
                        "file": str(file_path)
                    })

        return issues

    def _check_prerequisite_alignment(self, content: str, file_path: Path, skill_level: str) -> list[dict[str, Any]]:
        """Check if prerequisites match skill level."""
        issues = []
        content_lower = content.lower()

        # Advanced concepts that shouldn't appear in beginner tutorials
        advanced_concepts = [
            "async", "await", "concurrent", "thread", "pool", "optimization",
            "portfolio", "risk management", "complex strategy"
        ]

        if skill_level == "beginner":
            for concept in advanced_concepts:
                if concept in content_lower and "prerequisite" not in content_lower:
                    issues.append({
                        "type": "inappropriate_concept",
                        "severity": "warning",
                        "message": f"Advanced concept '{concept}' used in beginner tutorial without prerequisite note",
                        "suggestion": "Either add prerequisite requirements or move to intermediate/advanced tutorial",
                        "file": str(file_path)
                    })

        return issues

    def _check_learning_scaffolding(self, content: str, file_path: Path) -> list[dict[str, Any]]:
        """Check for proper learning scaffolding techniques."""
        issues = []

        # Check for explanation before examples
        sections = re.split(r'\n#+\s+', content)

        for i, section in enumerate(sections):
            # Look for code blocks
            code_blocks = re.findall(r'```python\n(.*?)\n```', section, re.DOTALL)

            if code_blocks:
                # Check if there's explanatory text before the first code block
                text_before_code = section.split('```')[0]
                explanation_words = len(text_before_code.split())

                if explanation_words < 20:  # Less than ~20 words of explanation
                    issues.append({
                        "type": "insufficient_context",
                        "severity": "info",
                        "message": f"Section {i+1} has code examples with minimal explanatory context",
                        "suggestion": "Add more explanation before showing code examples",
                        "file": str(file_path)
                    })

        # Check for learning reinforcement patterns
        reinforcement_patterns = [
            "try this", "practice", "exercise", "check your understanding",
            "verify", "test", "experiment"
        ]

        has_reinforcement = any(pattern in content.lower() for pattern in reinforcement_patterns)

        if len(content) > 1500 and not has_reinforcement:  # Only for longer tutorials
            issues.append({
                "type": "missing_reinforcement",
                "severity": "info",
                "message": "Tutorial lacks learning reinforcement activities",
                "suggestion": "Add practice exercises or comprehension checks",
                "file": str(file_path)
            })

        return issues

    def _log_issues(self, file_path: Path, issues: list[dict[str, Any]]):
        """Log issues found in a file."""
        if not issues:
            return

        print(f"\n🎓 Educational Progression Issues in {file_path}:")
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            message = issue.get('message', 'No message')
            suggestion = issue.get('suggestion', '')

            severity_icon = {"error": "❌", "warning": "⚠️", "info": "💡"}.get(severity, "•")
            print(f"  {severity_icon} {issue.get('type', 'unknown')}: {message}")
            if suggestion:
                print(f"      💡 {suggestion}")
