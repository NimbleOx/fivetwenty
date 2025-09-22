#!/usr/bin/env python3
"""
Simple script to find code validation issues in tutorial files.
"""

import ast
import re
from pathlib import Path
from typing import Any


def extract_python_code_blocks(content: str) -> list[tuple[str, int]]:
    """Extract Python code blocks from markdown content."""
    blocks = []
    lines = content.split('\n')
    in_python_block = False
    current_block: list[str] = []
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

def check_syntax(code: str) -> list[str]:
    """Check Python syntax and return error messages."""
    try:
        ast.parse(code)
        return []
    except SyntaxError as e:
        return [f"Syntax error: {e.msg} at line {e.lineno}"]

def check_imports(code: str) -> list[str]:
    """Check for missing imports."""
    issues = []

    # Common patterns that need imports
    patterns = [
        (r'\bMarketOrderRequest\b', 'from fivetwenty.models import MarketOrderRequest'),
        (r'\bInstrumentName\b', 'from fivetwenty.models import InstrumentName'),
        (r'\bTimeInForce\b', 'from fivetwenty.models import TimeInForce'),
        (r'\bAccountConfig\b', 'from fivetwenty import AccountConfig'),
        (r'\bStopLossOrderRequest\b', 'from fivetwenty.models import StopLossOrderRequest'),
        (r'\bAsyncClient\b', 'from fivetwenty import AsyncClient'),
        (r'\bClient\b', 'from fivetwenty import Client'),
        (r'\bEnvironment\b', 'from fivetwenty import Environment'),
        (r'\bFiveTwentyError\b', 'from fivetwenty.exceptions import FiveTwentyError'),
        (r'\bFiveTwentyErrorCode\b', 'from fivetwenty.exceptions import FiveTwentyErrorCode'),
        (r'\bDecimal\b', 'from decimal import Decimal'),
        (r'\bos\.environ\b', 'import os'),
        (r'\bhttpx\b', 'import httpx'),
    ]

    for pattern, required_import in patterns:
        if re.search(pattern, code) and required_import not in code:
            # Skip if this looks like an import example
            if not any(keyword in code.lower() for keyword in ["# import", "# imports", "import example", "importing"]):
                issues.append(f"Missing import: {required_import}")

    return issues

def check_financial_precision(code: str) -> list[str]:
    """Check for financial precision issues."""
    issues = []

    # Check for float usage in financial contexts
    financial_patterns = [
        r"price\s*=\s*\d+\.\d+",
        r"amount\s*=\s*\d+\.\d+",
        r"spread\s*=\s*\d+\.\d+",
        r"balance\s*=\s*\d+\.\d+",
    ]

    for pattern in financial_patterns:
        matches = re.finditer(pattern, code, re.IGNORECASE)
        issues.extend([
            f"Financial value should use Decimal: {match.group()}"
            for match in matches
            if "Decimal" not in match.group()
        ])

    return issues

def scan_file(file_path: Path) -> dict[str, Any]:
    """Scan a single file for code issues."""
    print(f"\n📁 Scanning: {file_path}")

    try:
        content = file_path.read_text(encoding='utf-8')
        blocks = extract_python_code_blocks(content)

        file_issues = []

        for block_num, (code, line_start) in enumerate(blocks, 1):
            # Skip incomplete examples
            if any(marker in code for marker in ["# ...", "pass  # Implementation", "..."]):
                continue

            if len(code.strip()) < 10:
                continue

            print(f"  📝 Block {block_num} (line {line_start}): {len(code)} chars")

            # Check syntax
            syntax_issues = check_syntax(code)
            file_issues.extend([
                {
                    'block': block_num,
                    'line': line_start,
                    'type': 'syntax_error',
                    'message': issue,
                    'code_snippet': code[:100] + "..." if len(code) > 100 else code
                }
                for issue in syntax_issues
            ])

            # Check imports
            import_issues = check_imports(code)
            file_issues.extend([
                {
                    'block': block_num,
                    'line': line_start,
                    'type': 'missing_import',
                    'message': issue
                }
                for issue in import_issues
            ])

            # Check financial precision
            precision_issues = check_financial_precision(code)
            file_issues.extend([
                {
                    'block': block_num,
                    'line': line_start,
                    'type': 'financial_precision',
                    'message': issue
                }
                for issue in precision_issues
            ])

        return {
            'file': str(file_path),
            'blocks_checked': len(blocks),
            'issues': file_issues
        }

    except Exception as e:
        return {
            'file': str(file_path),
            'blocks_checked': 0,
            'issues': [{'type': 'file_error', 'message': f"Could not read file: {e}"}]
        }

def main() -> None:
    """Main function to scan tutorial files."""
    print("🔍 Scanning tutorial files for code validation issues...")

    tutorial_files = [
        "docs/tutorials/getting-started/first-trade.md",
        "docs/tutorials/decimal-best-practices.md",
        "docs/tutorials/streaming-data.md",
        "docs/tutorials/risk-management.md",
        "docs/tutorials/portfolio-analysis.md",
        "docs/tutorials/getting-started/authentication.md",
        "docs/tutorials/getting-started/environments.md",
        "docs/tutorials/getting-started/installation.md",
        "docs/tutorials/basic-trading.md",
        "docs/tutorials/advanced-orders.md",
    ]

    total_issues = 0

    for file_path_str in tutorial_files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            continue

        result = scan_file(file_path)

        if result['issues']:
            print(f"  🚨 {len(result['issues'])} issues found:")
            for issue in result['issues']:
                print(f"    • {issue['type']}: {issue['message']}")
                if 'line' in issue:
                    print(f"      Line {issue['line']}, Block {issue.get('block', '?')}")
        else:
            print("  ✅ No issues found")

        total_issues += len(result['issues'])

    print(f"\n📊 Total issues found: {total_issues}")

if __name__ == "__main__":
    main()
