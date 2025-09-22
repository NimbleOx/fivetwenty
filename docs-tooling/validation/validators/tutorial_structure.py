#!/usr/bin/env python3
"""
Tutorial Structure Validator

Validates that tutorial content follows educational best practices and proper structure
for progressive learning. Based on lessons learned from comprehensive tutorial validation.
"""

import re
from pathlib import Path
from typing import List, Dict, Any

from core.base import BaseValidator, ValidationResult


class TutorialStructureValidator(BaseValidator):
    """Validate tutorial structure and educational content standards."""

    def __init__(self):
        super().__init__("tutorial_structure", "Validates tutorial content follows educational best practices and proper structure")
        self.validator_name = "tutorial_structure"
        self.file_patterns = ["docs/tutorials/**/*.md"]
        self.tutorial_issues: list[dict[str, Any]] = []

        # Tutorial structure requirements based on our analysis
        self.required_sections = {
            "learning_outcomes": [
                "learning objective", "learning outcome", "you will learn",
                "by the end", "after completing", "skills you'll gain"
            ],
            "prerequisites": [
                "prerequisite", "before starting", "requirements", "what you need"
            ],
            "time_estimate": [
                "time commitment", "duration", "estimated time", "time required"
            ],
            "hands_on_exercises": [
                "hands-on", "exercise", "try this", "practice", "tutorial"
            ],
            "checkpoints": [
                "checkpoint", "test your understanding", "verify", "skill check"
            ]
        }

        # Progressive difficulty indicators
        self.difficulty_indicators = {
            "beginner": ["getting started", "first", "basic", "introduction", "simple"],
            "intermediate": ["advanced", "complex", "comprehensive", "in-depth"],
            "advanced": ["expert", "production", "sophisticated", "enterprise"]
        }

    def validate(self) -> ValidationResult:
        """Run tutorial structure validation."""
        tutorial_files = self._find_tutorial_files()
        total_checked = len(tutorial_files)

        for file_path in tutorial_files:
            file_issues = self._validate_tutorial_file(file_path)
            self.tutorial_issues.extend(file_issues)

        status = "passed" if len(self.tutorial_issues) == 0 else "failed"

        return ValidationResult(
            validator_name=self.validator_name,
            status=status,
            issues_found=len(self.tutorial_issues),
            total_checked=total_checked,
            details={
                "files_checked": total_checked,
                "tutorial_issues": self.tutorial_issues,
                "validation_focus": "Educational content structure and learning progression"
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _find_tutorial_files(self) -> List[Path]:
        """Find all tutorial files to validate."""
        tutorial_files = []

        for pattern in self.file_patterns:
            tutorial_files.extend(Path(".").glob(pattern))

        return [f for f in tutorial_files if f.is_file()]

    def _validate_tutorial_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Validate structure of a single tutorial file."""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8')

            # Skip index files - they have different requirements
            if file_path.name == "index.md":
                return []

            # Check for required educational structure
            issues.extend(self._check_educational_structure(content, file_path))

            # Check learning progression indicators
            issues.extend(self._check_learning_progression(content, file_path))

            # Check for proper tutorial formatting
            issues.extend(self._check_tutorial_formatting(content, file_path))

            # Check code example progression
            issues.extend(self._check_code_progression(content, file_path))

        except Exception as e:
            issues.append({
                "type": "file_error",
                "severity": "error",
                "message": f"Could not validate tutorial structure: {e}",
                "file": str(file_path)
            })

        return issues

    def _check_educational_structure(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for required educational content structure."""
        issues = []
        content_lower = content.lower()

        # Check for learning outcomes (critical for tutorials)
        if not any(pattern in content_lower for pattern in self.required_sections["learning_outcomes"]):
            issues.append({
                "type": "missing_learning_outcomes",
                "severity": "warning",
                "message": "Tutorial should include clear learning outcomes or objectives",
                "suggestion": "Add a section like 'Learning Objectives' or 'What You'll Learn'",
                "file": str(file_path)
            })

        # Check for prerequisites
        if not any(pattern in content_lower for pattern in self.required_sections["prerequisites"]):
            issues.append({
                "type": "missing_prerequisites",
                "severity": "info",
                "message": "Consider adding a prerequisites section for learner guidance",
                "suggestion": "Add prerequisites to help learners understand required background",
                "file": str(file_path)
            })

        # Check for hands-on exercises (essential for tutorials)
        if not any(pattern in content_lower for pattern in self.required_sections["hands_on_exercises"]):
            issues.append({
                "type": "missing_hands_on_content",
                "severity": "warning",
                "message": "Tutorial should include hands-on exercises or practical examples",
                "suggestion": "Add practical exercises that let learners apply the concepts",
                "file": str(file_path)
            })

        return issues

    def _check_learning_progression(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for proper learning progression indicators."""
        issues = []

        # Look for step-by-step progression
        step_patterns = [
            r"step \d+", r"\d+\.", r"level \d+", r"stage \d+",
            r"first", r"next", r"then", r"finally"
        ]

        has_progression = any(re.search(pattern, content, re.IGNORECASE) for pattern in step_patterns)

        if not has_progression:
            issues.append({
                "type": "unclear_progression",
                "severity": "info",
                "message": "Tutorial could benefit from clearer step-by-step progression",
                "suggestion": "Use numbered steps, levels, or clear progression indicators",
                "file": str(file_path)
            })

        # Check for skill checkpoints
        checkpoint_patterns = self.required_sections["checkpoints"]
        has_checkpoints = any(pattern in content.lower() for pattern in checkpoint_patterns)

        if not has_checkpoints and len(content) > 2000:  # Only for longer tutorials
            issues.append({
                "type": "missing_skill_checkpoints",
                "severity": "info",
                "message": "Longer tutorials should include skill checkpoints or progress verification",
                "suggestion": "Add checkpoints to help learners verify their understanding",
                "file": str(file_path)
            })

        return issues

    def _check_tutorial_formatting(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for proper tutorial-specific formatting."""
        issues = []

        # Check for tutorial identification
        tutorial_indicators = ["tutorial", "learning", "guide", "walkthrough"]
        has_tutorial_indicator = any(indicator in content.lower()[:500] for indicator in tutorial_indicators)

        if not has_tutorial_indicator:
            issues.append({
                "type": "unclear_tutorial_purpose",
                "severity": "info",
                "message": "Content should clearly indicate it's a tutorial for learning",
                "suggestion": "Add tutorial identification in title or introduction",
                "file": str(file_path)
            })

        # Check for success criteria
        success_patterns = [
            "success", "complete", "achievement", "accomplished",
            "mastery", "finished", "done"
        ]

        has_success_criteria = any(pattern in content.lower() for pattern in success_patterns)

        if not has_success_criteria:
            issues.append({
                "type": "missing_success_criteria",
                "severity": "info",
                "message": "Tutorial should include clear success criteria or completion indicators",
                "suggestion": "Add completion criteria so learners know when they've succeeded",
                "file": str(file_path)
            })

        return issues

    def _check_code_progression(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Check for proper code example progression in tutorials."""
        issues = []

        # Extract code blocks
        code_blocks = re.findall(r'```python\n(.*?)\n```', content, re.DOTALL)

        if len(code_blocks) > 3:  # Only check tutorials with multiple code examples
            # Check if examples build on each other
            first_block = code_blocks[0] if code_blocks else ""
            last_block = code_blocks[-1] if code_blocks else ""

            # Simple heuristic: later examples should be more complex
            if len(last_block) <= len(first_block) * 1.5:
                issues.append({
                    "type": "lack_of_code_progression",
                    "severity": "info",
                    "message": "Code examples should show progression from simple to complex",
                    "suggestion": "Structure examples to build complexity gradually",
                    "file": str(file_path)
                })

            # Check for imports progression (should stabilize, not keep adding)
            import_counts = []
            for block in code_blocks:
                import_count = len(re.findall(r'^(from|import)\s+', block, re.MULTILINE))
                import_counts.append(import_count)

            # After first few examples, imports should stabilize
            if len(import_counts) > 3:
                later_imports = import_counts[3:]
                if max(later_imports) > min(later_imports) * 2:
                    issues.append({
                        "type": "inconsistent_imports",
                        "severity": "info",
                        "message": "Code examples show inconsistent import patterns - consider consolidating",
                        "suggestion": "Ensure consistent imports after initial examples",
                        "file": str(file_path)
                    })

        return issues

    def _log_issues(self, file_path: Path, issues: List[Dict[str, Any]]):
        """Log issues found in a file."""
        if not issues:
            return

        print(f"\n📚 Tutorial Structure Issues in {file_path}:")
        for issue in issues:
            severity = issue.get('severity', 'unknown')
            message = issue.get('message', 'No message')
            suggestion = issue.get('suggestion', '')

            severity_icon = {"error": "❌", "warning": "⚠️", "info": "💡"}.get(severity, "•")
            print(f"  {severity_icon} {issue.get('type', 'unknown')}: {message}")
            if suggestion:
                print(f"      💡 {suggestion}")