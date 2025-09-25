#!/usr/bin/env python3
"""Fix critical errors in documentation code blocks."""

import json
import re
from pathlib import Path
from typing import List, Dict

def load_validation_results():
    """Load validation results from JSON file."""
    results_file = Path("code_validation_results.json")
    if not results_file.exists():
        print("❌ Validation results file not found")
        return None

    with open(results_file) as f:
        return json.load(f)

def get_critical_errors(results):
    """Extract critical errors from validation results."""
    critical_rules = {
        "code_async_outside_function",
        "code_missing_account_id"
    }

    critical_issues = [
        issue for issue in results["issues"]
        if issue["severity"] == "ERROR" and issue["rule_id"] in critical_rules
    ]

    return critical_issues

def fix_async_function_wrappers(file_path: str, line_num: int, context: str) -> bool:
    """Fix async function wrapper issues in a file."""
    file_path_obj = Path(file_path.lstrip('/'))

    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path_obj}")
        return False

    content = file_path_obj.read_text()
    lines = content.split('\n')

    # Find code blocks around the error line
    in_code_block = False
    code_block_start = -1
    code_block_end = -1
    language = ""

    for i, line in enumerate(lines):
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_start = i
                language = line.strip()[3:].strip()
            else:
                in_code_block = False
                code_block_end = i

                # Check if our error line is in this code block
                if code_block_start < line_num - 1 < code_block_end:
                    return fix_code_block_async(file_path_obj, lines, code_block_start, code_block_end, language)

    return False

def fix_code_block_async(file_path: Path, lines: List[str], start_idx: int, end_idx: int, language: str) -> bool:
    """Fix a specific code block to add proper async wrapper."""
    if language.lower() not in ['python', 'py', '']:
        return False

    # Extract code block content
    code_lines = lines[start_idx + 1:end_idx]

    # Check if already has async def main pattern
    code_content = '\n'.join(code_lines)
    if 'async def main():' in code_content and 'asyncio.run(main())' in code_content:
        return False  # Already fixed

    # Check if this has async with or await
    has_async_with = any('async with' in line for line in code_lines)
    has_await = any('await ' in line for line in code_lines)

    if not (has_async_with or has_await):
        return False  # No async code to fix

    # Create the wrapped version
    new_code_lines = []

    # Add imports if not present
    has_asyncio_import = any('import asyncio' in line for line in code_lines)
    if not has_asyncio_import and (has_async_with or has_await):
        new_code_lines.append('import asyncio')
        new_code_lines.append('')

    # Add async def main():
    new_code_lines.append('async def main():')

    # Indent all existing code
    for line in code_lines:
        if line.strip():  # Don't indent empty lines
            new_code_lines.append('    ' + line)
        else:
            new_code_lines.append('')

    # Add asyncio.run call
    new_code_lines.append('')
    new_code_lines.append('asyncio.run(main())')

    # Replace the code block in the original file
    new_lines = lines.copy()
    new_lines[start_idx + 1:end_idx] = new_code_lines

    # Write back to file
    file_path.write_text('\n'.join(new_lines))
    print(f"✅ Fixed async wrapper in {file_path} (lines {start_idx}-{end_idx})")
    return True

def fix_missing_account_id(file_path: str, line_num: int, context: str) -> bool:
    """Fix missing account_id parameter in AsyncClient calls."""
    file_path_obj = Path(file_path.lstrip('/'))

    if not file_path_obj.exists():
        print(f"❌ File not found: {file_path_obj}")
        return False

    content = file_path_obj.read_text()
    lines = content.split('\n')

    # Find the problematic line
    if line_num > len(lines):
        return False

    problem_line = lines[line_num - 1]

    # Check if it's an AsyncClient call with token but no account_id
    if 'AsyncClient(' in problem_line and 'token=' in problem_line:
        # Add account_id parameter
        if 'account_id=' not in problem_line:
            # Insert account_id after token parameter
            # Look for token="..." pattern and add account_id after it
            updated_line = re.sub(
                r'token=([^,)]+)',
                r'token=\1, account_id="your-account-id"',
                problem_line
            )

            if updated_line != problem_line:
                lines[line_num - 1] = updated_line
                file_path_obj.write_text('\n'.join(lines))
                print(f"✅ Added account_id to AsyncClient in {file_path}:{line_num}")
                return True

    return False

def main():
    """Main function to fix critical errors."""
    print("🔧 Loading validation results...")
    results = load_validation_results()

    if not results:
        return

    critical_errors = get_critical_errors(results)
    print(f"🎯 Found {len(critical_errors)} critical errors to fix")

    # Group by rule type
    by_rule = {}
    for error in critical_errors:
        rule = error["rule_id"]
        if rule not in by_rule:
            by_rule[rule] = []
        by_rule[rule].append(error)

    fixed_count = 0

    # Fix async function wrapper errors
    if "code_async_outside_function" in by_rule:
        async_errors = by_rule["code_async_outside_function"]
        print(f"\n🔄 Fixing {len(async_errors)} async function wrapper errors...")

        for error in async_errors:
            if fix_async_function_wrappers(error["file_path"], error["line"], error["context"]):
                fixed_count += 1

    # Fix missing account_id errors
    if "code_missing_account_id" in by_rule:
        account_errors = by_rule["code_missing_account_id"]
        print(f"\n🔄 Fixing {len(account_errors)} missing account_id errors...")

        for error in account_errors:
            if fix_missing_account_id(error["file_path"], error["line"], error["context"]):
                fixed_count += 1

    print(f"\n✅ Fixed {fixed_count} critical errors!")
    print("\n🔍 Run validation again to confirm fixes:")
    print("cd docs_validation && env PYTHONPATH=. uv run python -m src.cli validate --project-root .. --verbose")

if __name__ == "__main__":
    main()