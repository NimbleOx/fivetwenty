"""
Financial Precision validation for documentation.

Validates that financial examples in documentation follow best practices
for precision, type safety, and forex trading conventions.
"""

import re
import sys
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

# Import after path manipulation
from core.base import FileValidator, ValidationResult  # type: ignore[import-not-found] # noqa: E402


class FinancialPrecisionValidator(FileValidator):  # type: ignore[misc]
    """Validates financial precision in documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="financial_precision_validator",
            description="Validates financial examples follow precision and type safety best practices",
            file_patterns=["docs/**/*.md", "*.md"]
        )
        self.precision_issues: list[dict[str, Any]] = []

    def validate(self) -> ValidationResult:
        """Validate financial precision in all markdown files."""
        files = self.get_files_to_validate()
        total_files = len(files)
        total_examples = 0

        for file_path in files:
            total_examples += self._check_file_financial_examples(file_path)

        return ValidationResult(
            validator_name=self.name,
            status="passed" if len(self.precision_issues) == 0 else "failed",
            issues_found=len(self.precision_issues),
            total_checked=total_examples,
            details={
                "precision_issues": self.precision_issues,
                "files_checked": total_files,
                "financial_examples_checked": total_examples
            },
            timestamp=self.start_time.isoformat() if self.start_time else "",
            duration_seconds=self.get_elapsed_time(),
        )

    def _check_file_financial_examples(self, file_path: Path) -> int:
        """Check financial examples in a single file. Returns number of examples checked."""
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            examples_count = 0

            # Extract code blocks and inline code
            code_blocks = self._extract_code_sections(content)

            for code, line_start, is_block in code_blocks:
                examples_count += 1
                self._validate_financial_code(file_path, code, line_start, is_block)

            # Also check financial values in regular text
            examples_count += self._check_financial_text_examples(file_path, content)

            return examples_count

        except Exception as e:
            self.precision_issues.append({
                "file": str(file_path),
                "type": "file_error",
                "message": f"Could not read file: {e}",
                "severity": "error"
            })
            return 0

    def _extract_code_sections(self, content: str) -> list[tuple[str, int, bool]]:
        """Extract code blocks and inline code. Returns (code, line_start, is_block)."""
        sections = []

        # Extract Python code blocks
        python_block_pattern = r'```python\n(.*?)\n```'
        for match in re.finditer(python_block_pattern, content, re.DOTALL):
            code = match.group(1)
            line_start = content[:match.start()].count('\n') + 2  # +2 for ```python line
            sections.append((code, line_start, True))

        # Extract generic code blocks that might contain financial examples
        generic_block_pattern = r'```(?!python)\w*\n(.*?)\n```'
        for match in re.finditer(generic_block_pattern, content, re.DOTALL):
            code = match.group(1)
            if self._contains_financial_content(code):
                line_start = content[:match.start()].count('\n') + 2
                sections.append((code, line_start, True))

        # Extract inline code with financial content
        inline_pattern = r'`([^`]+)`'
        for match in re.finditer(inline_pattern, content):
            code = match.group(1)
            if self._contains_financial_content(code):
                line_start = content[:match.start()].count('\n') + 1
                sections.append((code, line_start, False))

        return sections

    def _contains_financial_content(self, code: str) -> bool:
        """Check if code contains financial-related content."""
        financial_keywords = [
            'price', 'amount', 'balance', 'spread', 'margin', 'leverage',
            'units', 'profit', 'loss', 'bid', 'ask', 'EUR_USD', 'GBP_USD',
            'order', 'trade', 'position', 'account'
        ]

        # Also look for decimal patterns
        decimal_pattern = r'\d+\.\d+'

        code_lower = code.lower()
        return (any(keyword in code_lower for keyword in financial_keywords) or
                re.search(decimal_pattern, code))

    def _validate_financial_code(self, file_path: Path, code: str, line_start: int, is_block: bool) -> None:
        """Validate financial precision in code."""
        # Check for float usage in financial contexts
        self._check_float_usage(file_path, code, line_start, is_block)

        # Check forex precision
        self._check_forex_precision(file_path, code, line_start, is_block)

        # Check financial type patterns
        self._check_financial_types(file_path, code, line_start, is_block)

        # Check realistic values
        self._check_realistic_values(file_path, code, line_start, is_block)

    def _check_float_usage(self, file_path: Path, code: str, line_start: int, is_block: bool) -> None:
        """Check for inappropriate float usage in financial calculations."""
        # Pattern for explicit float() calls with financial context
        float_patterns = [
            (r'float\(\s*["\']?[\d.]+["\']?\s*\)', "Avoid float() for financial values, use Decimal instead"),
            (r'(\w*(?:price|amount|balance|spread|margin|units|profit|loss)\w*)\s*=\s*\d+\.\d+(?!\d)', "Financial values should use Decimal, not float literals"),
            (r'(\w+)\s*\*\s*\d+\.\d+', "Financial calculations should use Decimal for precision"),
            (r'(\w+)\s*/\s*\d+\.\d+', "Financial calculations should use Decimal for precision"),
        ]

        for pattern, message in float_patterns:
            matches = re.finditer(pattern, code, re.IGNORECASE)
            for match in matches:
                # Skip if already using Decimal
                if 'Decimal' in match.group():
                    continue

                line_offset = code[:match.start()].count('\n')
                self._add_precision_issue(
                    file_path=file_path,
                    issue_type="float_usage",
                    message=f"{message}: {match.group()}",
                    line=line_start + line_offset,
                    severity="critical",
                    code_type="block" if is_block else "inline",
                    suggestion="Use Decimal('...') instead of float literals"
                )

    def _check_forex_precision(self, file_path: Path, code: str, line_start: int, is_block: bool) -> None:
        """Check forex-specific precision requirements."""
        # Forex prices should have 4-5 decimal places
        forex_price_pattern = r'([A-Z]{3}_[A-Z]{3}.*?(\d+\.\d+))'

        for match in re.finditer(forex_price_pattern, code):
            full_match = match.group(1)
            price_value = match.group(2)

            # Count decimal places
            if '.' in price_value:
                decimal_places = len(price_value.split('.')[1])

                # Most forex pairs need 4-5 decimal places, JPY pairs need 2-3
                expected_places = 2 if 'JPY' in full_match else 4

                if decimal_places < expected_places:
                    line_offset = code[:match.start()].count('\n')
                    self._add_precision_issue(
                        file_path=file_path,
                        issue_type="insufficient_precision",
                        message=f"Forex price {price_value} may need more decimal places (expected {expected_places}+)",
                        line=line_start + line_offset,
                        severity="warning",
                        code_type="block" if is_block else "inline"
                    )

    def _check_financial_types(self, file_path: Path, code: str, line_start: int, is_block: bool) -> None:
        """Check for proper financial type usage."""
        # Check for missing Decimal import when using Decimal
        if 'Decimal(' in code and 'from decimal import Decimal' not in code and 'import decimal' not in code:
            self._add_precision_issue(
                file_path=file_path,
                issue_type="missing_decimal_import",
                message="Code uses Decimal but missing 'from decimal import Decimal' import",
                line=line_start,
                severity="error",
                code_type="block" if is_block else "inline",
                suggestion="Add 'from decimal import Decimal' to imports"
            )

        # Check for proper string quoting in Decimal
        decimal_pattern = r'Decimal\((\d+\.\d+)\)'  # Decimal(1.23) without quotes
        for match in re.finditer(decimal_pattern, code):
            line_offset = code[:match.start()].count('\n')
            self._add_precision_issue(
                file_path=file_path,
                issue_type="unquoted_decimal",
                message=f"Decimal should use string argument: Decimal('{match.group(1)}') not Decimal({match.group(1)})",
                line=line_start + line_offset,
                severity="warning",
                code_type="block" if is_block else "inline"
            )

    def _check_realistic_values(self, file_path: Path, code: str, line_start: int, is_block: bool) -> None:
        """Check for realistic financial values in examples."""
        # Check for unrealistic forex prices
        unrealistic_patterns = [
            (r'EUR_USD.*?(\d+\.\d+)', 'EUR_USD', (0.5, 2.0)),  # EUR/USD typically 0.8-1.5
            (r'GBP_USD.*?(\d+\.\d+)', 'GBP_USD', (0.5, 2.5)),  # GBP/USD typically 1.0-2.0
            (r'USD_JPY.*?(\d+\.\d+)', 'USD_JPY', (50, 200)),   # USD/JPY typically 80-150
        ]

        for pattern, pair, (min_val, max_val) in unrealistic_patterns:
            for match in re.finditer(pattern, code, re.IGNORECASE):
                try:
                    value = float(match.group(1))
                    if value < min_val or value > max_val:
                        line_offset = code[:match.start()].count('\n')
                        self._add_precision_issue(
                            file_path=file_path,
                            issue_type="unrealistic_value",
                            message=f"Unrealistic {pair} price: {value} (typical range: {min_val}-{max_val})",
                            line=line_start + line_offset,
                            severity="info",
                            code_type="block" if is_block else "inline"
                        )
                except ValueError:
                    continue

    def _check_financial_text_examples(self, file_path: Path, content: str) -> int:
        """Check financial examples in regular text (not code blocks)."""
        examples_count = 0
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip code blocks
            if line.strip().startswith('```') or line.strip().startswith('    '):
                continue

            # Look for financial values in text
            financial_text_patterns = [
                r'price of (\d+\.\d+)',
                r'spread of (\d+\.\d+)',
                r'balance: \$?(\d+\.\d+)',
                r'profit of \$?(\d+\.\d+)',
            ]

            for pattern in financial_text_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    examples_count += 1
                    value = match.group(1)

                    # Check if it looks like a float that should be a Decimal example
                    if '.' in value and len(value.split('.')[1]) > 0:
                        # This is a text example, so just flag if it seems imprecise
                        if len(value.split('.')[1]) == 1:  # Only 1 decimal place
                            self._add_precision_issue(
                                file_path=file_path,
                                issue_type="imprecise_text_example",
                                message=f"Financial example in text may need more precision: {value}",
                                line=line_num,
                                severity="info",
                                code_type="text"
                            )

        return examples_count

    def _add_precision_issue(self, file_path: Path, issue_type: str, message: str, line: int, severity: str, **kwargs: Any) -> None:
        """Add a precision issue to the results."""
        issue = {
            "file": str(file_path.relative_to(Path.cwd())),
            "line": line,
            "type": issue_type,
            "message": message,
            "severity": severity,
            **kwargs
        }
        self.precision_issues.append(issue)
        self.add_issue(message, str(file_path), line)
