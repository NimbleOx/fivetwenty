"""
Code Linting validator for documentation.

Validates Python code blocks using ruff for comprehensive linting, based on lessons
learned from manual linting exercise. Catches issues that AST parsing alone misses.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class CodeLintingValidator(FileValidator):  # type: ignore[misc]
    """Validates Python code blocks using ruff linting."""

    def __init__(self) -> None:
        super().__init__(
            name="code_linting_validator",
            description="Validates Python code blocks with ruff linting for style and correctness",
            file_patterns=["docs/**/*.md", "*.md"]
        )
        self.linting_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate code linting in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)
        total_code_blocks = 0

        for file_path in files:
            total_code_blocks += self._check_file_linting(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.linting_issues) == 0 else "failed",
            issues_found=len(self.linting_issues),
            total_checked=total_code_blocks,
            details={
                "linting_issues": self.linting_issues,
                "files_checked": total_files,
                "code_blocks_checked": total_code_blocks
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _check_file_linting(self, file_path: Path) -> int:
        """Check linting issues in a single file. Returns number of code blocks checked."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Extract Python code blocks
            python_blocks = self._extract_python_code_blocks(content)

            for block_num, (code, line_start) in enumerate(python_blocks, 1):
                self._validate_code_block_linting(file_path, code, line_start, block_num)

            return len(python_blocks)

        except Exception as e:
            self.linting_issues.append({
                "file": str(file_path),
                "type": "file_error",
                "message": f"Could not read file: {e}",
                "severity": "error"
            })
            return 0

    def _extract_python_code_blocks(self, content: str) -> list[tuple[str, int]]:
        """Extract Python code blocks from markdown content."""
        blocks = []
        lines = content.split('\n')
        in_python_block = False
        current_block = []
        block_start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('```python'):
                in_python_block = True
                current_block = []
                block_start_line = line_num + 1
            elif line.strip() == '```' and in_python_block:
                if current_block:
                    blocks.append(('\n'.join(current_block), block_start_line))
                in_python_block = False
            elif in_python_block:
                current_block.append(line)

        return blocks

    def _validate_code_block_linting(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Validate a single Python code block with comprehensive linting."""
        # Skip validation for specific patterns we learned during the exercise
        if self._should_skip_linting(code):
            return

        # Check for mixed shell/Python code (lesson learned #1)
        self._check_mixed_shell_python(file_path, code, line_start, block_num)

        # Check for invalid method signatures (lesson learned #2)
        self._check_method_signatures(file_path, code, line_start, block_num)

        # Check for async context issues (lesson learned #3)
        self._check_async_context_issues(file_path, code, line_start, block_num)

        # Run ruff linting on the code block
        self._run_ruff_linting(file_path, code, line_start, block_num)

    def _should_skip_linting(self, code: str) -> bool:
        """Check if this code block should be skipped for linting."""
        skip_markers = [
            "# Example output:",
            "# Output:",
            "# Result:",
            "# This will output:",
            "# Returns:",
            "...",  # Ellipsis indicating incomplete code
            "# ... rest of code",
            "# ... implementation",
            "# TODO:",
            "# FIXME:",
        ]

        # Skip very short code snippets
        if len(code.strip()) < 5:
            return True

        # Skip code that's primarily comments explaining signatures
        if code.strip().startswith('#') and '->' in code and '(' in code:
            return True

        return any(marker in code for marker in skip_markers)

    def _check_mixed_shell_python(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for mixed shell and Python commands (lesson learned from index.md)."""
        shell_commands = ['export ', 'cd ', 'mkdir ', 'ls ', 'git ', 'pip ', 'npm ', 'uv ']

        has_python = any(keyword in code for keyword in ['import ', 'from ', 'def ', 'class ', 'async ', 'await'])
        has_shell = any(cmd in code for cmd in shell_commands)

        if has_python and has_shell:
            self._add_linting_issue(
                file_path=file_path,
                issue_type="mixed_shell_python",
                message=f"Code block {block_num} mixes shell commands with Python code. Consider separating into bash and python blocks.",
                line=line_start,
                severity="warning",
                suggestion="Separate shell commands (export, cd, etc.) into ```bash blocks and Python code into ```python blocks"
            )

    def _check_method_signatures(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for invalid method signature syntax (lesson learned from API docs)."""
        # Pattern for method signatures like "method_name(...) -> return_type"
        method_sig_pattern = r'^[a-zA-Z_][a-zA-Z0-9_.]*\([^)]*\)\s*->'

        lines = code.strip().split('\n')
        for line_offset, line in enumerate(lines):
            stripped = line.strip()
            if re.match(method_sig_pattern, stripped) and not stripped.startswith('#'):
                self._add_linting_issue(
                    file_path=file_path,
                    issue_type="invalid_method_signature",
                    message=f"Code block {block_num} contains method signature syntax that is not valid Python",
                    line=line_start + line_offset,
                    severity="error",
                    suggestion="Convert method signatures to comments (prefix with #) or wrap in a function definition"
                )

    def _check_async_context_issues(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Check for async context manager usage outside async functions."""
        if 'async with' in code and 'async def' not in code and 'asyncio.run(' not in code:
            # Check if it's not already wrapped properly
            if not any(pattern in code for pattern in ['def main():', 'async def main():', 'asyncio.run(']):
                self._add_linting_issue(
                    file_path=file_path,
                    issue_type="async_context_outside_function",
                    message=f"Code block {block_num} uses 'async with' outside of an async function",
                    line=line_start,
                    severity="error",
                    suggestion="Wrap async code in 'async def main():' and call with 'asyncio.run(main())'"
                )

    def _run_ruff_linting(self, file_path: Path, code: str, line_start: int, block_num: int) -> None:
        """Run ruff linting on the code block."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name

            # Run ruff check
            result = subprocess.run(
                ['ruff', 'check', temp_path, '--output-format', 'json'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0 and result.stdout:
                try:
                    import json
                    issues = json.loads(result.stdout)
                    for issue in issues:
                        self._add_linting_issue(
                            file_path=file_path,
                            issue_type="ruff_lint",
                            message=f"Code block {block_num}: {issue.get('message', 'Linting issue')}",
                            line=line_start + issue.get('location', {}).get('row', 1) - 1,
                            severity="warning",
                            code=issue.get('code', ''),
                            suggestion=issue.get('fix', {}).get('message', '') if issue.get('fix') else ''
                        )
                except (json.JSONDecodeError, KeyError):
                    # Fallback to text output if JSON parsing fails
                    if result.stdout and 'error' in result.stdout.lower():
                        self._add_linting_issue(
                            file_path=file_path,
                            issue_type="ruff_lint",
                            message=f"Code block {block_num}: Linting issues found",
                            line=line_start,
                            severity="warning",
                            suggestion="Review code formatting and style"
                        )

        except Exception as e:
            # Don't fail validation if ruff isn't available
            pass
        finally:
            # Clean up temporary file
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass

    def _add_linting_issue(self, file_path: Path, issue_type: str, message: str,
                          line: int, severity: str, suggestion: str = "", code: str = "") -> None:
        """Add a linting issue to the results."""
        issue = {
            "file": str(file_path),
            "type": issue_type,
            "message": message,
            "line": line,
            "severity": severity
        }

        if suggestion:
            issue["suggestion"] = suggestion
        if code:
            issue["code"] = code

        self.linting_issues.append(issue)


# Export the validator
def get_validator() -> CodeLintingValidator:
    """Get the code linting validator instance."""
    return CodeLintingValidator()