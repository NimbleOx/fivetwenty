#!/usr/bin/env python3
"""
FiveTwenty Documentation Auto-Fix Script

Automatically fixes common validation issues based on patterns discovered
during explanation and how-to-guides validation.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

# Add the validation directory to the path for imports
validation_dir = Path(__file__).parent.parent
sys.path.insert(0, str(validation_dir))


class DocumentationAutoFixer:
    """Automatically fix common documentation validation issues."""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.fixes_applied = []
        self.backup_suffix = ".bak"

    def fix_directory(self, target_dir: str, patterns: list[str] | None = None) -> dict[str, Any]:
        """Fix all markdown files in a directory."""
        target_path = Path(target_dir)
        if not target_path.exists():
            raise ValueError(f"Directory does not exist: {target_dir}")

        patterns_to_fix = patterns or ["financial-precision", "missing-imports", "deprecated-patterns"]

        results = {
            "directory": target_dir,
            "files_processed": 0,
            "files_modified": 0,
            "total_fixes": 0,
            "fixes_by_pattern": {},
            "errors": []
        }

        print(f"🔧 {'DRY RUN: ' if self.dry_run else ''}Auto-fixing documentation in {target_dir}")
        print(f"📋 Patterns to fix: {', '.join(patterns_to_fix)}")

        for md_file in target_path.glob("**/*.md"):
            try:
                file_fixes = self._fix_file(md_file, patterns_to_fix)
                results["files_processed"] += 1

                if file_fixes["total_fixes"] > 0:
                    results["files_modified"] += 1
                    results["total_fixes"] += file_fixes["total_fixes"]

                    for pattern, count in file_fixes["fixes_by_pattern"].items():
                        results["fixes_by_pattern"][pattern] = results["fixes_by_pattern"].get(pattern, 0) + count

                    print(f"  📄 {md_file.relative_to(target_path)}: {file_fixes['total_fixes']} fixes")

            except Exception as e:
                error_msg = f"Error processing {md_file}: {e}"
                results["errors"].append(error_msg)
                print(f"  ❌ {error_msg}")

        return results

    def _fix_file(self, file_path: Path, patterns: list[str]) -> dict[str, Any]:
        """Fix issues in a single markdown file."""
        with file_path.open(encoding='utf-8') as f:
            original_content = f.read()

        content = original_content
        fixes_applied = []

        # Apply each pattern fix
        for pattern in patterns:
            if pattern == "financial-precision":
                content, pattern_fixes = self._fix_financial_precision(content)
                fixes_applied.extend(pattern_fixes)
            elif pattern == "missing-imports":
                content, pattern_fixes = self._fix_missing_imports(content)
                fixes_applied.extend(pattern_fixes)
            elif pattern == "deprecated-patterns":
                content, pattern_fixes = self._fix_deprecated_patterns(content)
                fixes_applied.extend(pattern_fixes)

        # Count fixes by pattern
        fixes_by_pattern = {}
        for fix in fixes_applied:
            pattern = fix["pattern"]
            fixes_by_pattern[pattern] = fixes_by_pattern.get(pattern, 0) + 1

        # Save file if changes were made
        if content != original_content:
            if not self.dry_run:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + self.backup_suffix)
                backup_path.write_text(original_content, encoding='utf-8')

                # Write fixed content
                file_path.write_text(content, encoding='utf-8')

            self.fixes_applied.extend(fixes_applied)

        return {
            "file": str(file_path),
            "total_fixes": len(fixes_applied),
            "fixes_by_pattern": fixes_by_pattern,
            "fixes_applied": fixes_applied
        }

    def _fix_financial_precision(self, content: str) -> tuple[str, list[dict[str, Any]]]:
        """Fix financial precision issues."""
        fixes = []

        # Pattern 1: Float literals in financial contexts
        financial_float_pattern = r'(price|amount|balance|stop_loss|take_profit|daily_loss_limit|spread|margin|units)\s*=\s*(\d+\.\d+)(?!["\'])'

        def replace_financial_float(match):
            var_name = match.group(1)
            value = match.group(2)
            fixes.append({
                "pattern": "financial-precision",
                "type": "float_to_decimal",
                "original": match.group(0),
                "fixed": f'{var_name}=Decimal("{value}")',
                "description": f"Converted float literal {value} to Decimal for financial precision"
            })
            return f'{var_name}=Decimal("{value}")'

        content = re.sub(financial_float_pattern, replace_financial_float, content)

        # Pattern 2: Float arithmetic in financial calculations
        float_arithmetic_pattern = r'(\w+)\s*\*\s*(\d+\.\d+)(?!["\'])'

        def replace_float_arithmetic(match):
            var_name = match.group(1)
            value = match.group(2)
            fixes.append({
                "pattern": "financial-precision",
                "type": "float_arithmetic_to_decimal",
                "original": match.group(0),
                "fixed": f'{var_name} * Decimal("{value}")',
                "description": "Converted float arithmetic to use Decimal for precision"
            })
            return f'{var_name} * Decimal("{value}")'

        content = re.sub(float_arithmetic_pattern, replace_float_arithmetic, content)

        return content, fixes

    def _fix_missing_imports(self, content: str) -> tuple[str, list[dict[str, Any]]]:
        """Fix missing import statements in code blocks."""
        fixes = []

        # Extract all Python code blocks
        python_blocks = self._extract_python_code_blocks(content)

        for _block_start, _block_end, code in python_blocks:
            # Check what imports are needed
            needed_imports = []

            if "Decimal(" in code and "from decimal import Decimal" not in code:
                needed_imports.append("from decimal import Decimal")

            if ("AsyncClient(" in code or "AsyncClient(" in code) and "from fivetwenty import AsyncClient" not in code:
                needed_imports.append("from fivetwenty import AsyncClient, Environment")

            if "FiveTwentyError" in code and "from fivetwenty.exceptions import FiveTwentyError" not in code:
                needed_imports.append("from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode")

            if "os.getenv(" in code and "import os" not in code:
                needed_imports.append("import os")

            # Add missing imports
            if needed_imports:
                # Find the start of the code block (after ```python)
                code.split('\n')

                # Insert imports at the beginning
                imports_to_add = []
                for import_stmt in needed_imports:
                    if import_stmt not in code:
                        imports_to_add.append(import_stmt)

                if imports_to_add:
                    # Add imports at the beginning of the code block
                    new_code = '\n'.join(imports_to_add) + '\n\n' + code

                    # Replace in the original content
                    content = content.replace(
                        f"```python\n{code}\n```",
                        f"```python\n{new_code}\n```"
                    )

                    fixes.append({
                        "pattern": "missing-imports",
                        "type": "add_imports",
                        "imports_added": imports_to_add,
                        "description": f"Added missing imports: {', '.join(imports_to_add)}"
                    })

        return content, fixes

    def _fix_deprecated_patterns(self, content: str) -> tuple[str, list[dict[str, Any]]]:
        """Fix deprecated SDK patterns."""
        fixes = []

        # Pattern 1: ErrorCode vs FiveTwentyErrorCode
        error_code_pattern = r'\bErrorCode\b(?!\.)'
        if re.search(error_code_pattern, content):
            content = re.sub(error_code_pattern, 'FiveTwentyErrorCode', content)
            fixes.append({
                "pattern": "deprecated-patterns",
                "type": "error_code_fix",
                "description": "Replaced 'ErrorCode' with 'FiveTwentyErrorCode'"
            })

        # Pattern 2: Placeholder functions
        placeholder_patterns = [
            (r'refresh_token\(\)', '# Implementation needed: token refresh logic'),
            (r'notify_operations_team\([^)]*\)', '# Implementation needed: notification logic'),
            (r'undefined_function\([^)]*\)', '# Implementation needed')
        ]

        for pattern, replacement in placeholder_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                fixes.append({
                    "pattern": "deprecated-patterns",
                    "type": "placeholder_function",
                    "description": "Replaced placeholder function with implementation note"
                })

        return content, fixes

    def _extract_python_code_blocks(self, content: str) -> list[tuple[int, int, str]]:
        """Extract Python code blocks with their positions."""
        blocks = []
        lines = content.split('\n')
        in_python_block = False
        current_block = []
        block_start = 0

        for line_num, line in enumerate(lines):
            if line.strip().startswith('```python'):
                in_python_block = True
                current_block = []
                block_start = line_num
            elif line.strip() == '```' and in_python_block:
                if current_block:
                    block_code = '\n'.join(current_block)
                    blocks.append((block_start, line_num, block_code))
                in_python_block = False
            elif in_python_block:
                current_block.append(line)

        return blocks

    def generate_fix_report(self, results: dict[str, Any]) -> str:
        """Generate a summary report of fixes applied."""
        report = []

        report.append("# Auto-Fix Report")
        report.append(f"**Directory:** {results['directory']}")
        report.append(f"**Mode:** {'DRY RUN' if self.dry_run else 'APPLIED'}")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"- **Files Processed:** {results['files_processed']}")
        report.append(f"- **Files Modified:** {results['files_modified']}")
        report.append(f"- **Total Fixes:** {results['total_fixes']}")
        report.append("")

        # Fixes by pattern
        if results["fixes_by_pattern"]:
            report.append("## Fixes by Pattern")
            for pattern, count in results["fixes_by_pattern"].items():
                report.append(f"- **{pattern}:** {count} fixes")
            report.append("")

        # Errors
        if results["errors"]:
            report.append("## Errors")
            for error in results["errors"]:
                report.append(f"- {error}")
            report.append("")

        # Recommendations
        report.append("## Recommendations")
        if results["total_fixes"] == 0:
            report.append("- ✅ No issues found! Documentation meets validation standards.")
        elif self.dry_run:
            report.append("- 🔧 Run again with `--apply` to apply the fixes")
        else:
            report.append("- ✅ Fixes have been applied successfully")
            report.append("- 📋 Run validation again to verify all issues are resolved")
            report.append("- 🗃️ Backup files created with .bak extension")

        return '\n'.join(report)


def main():
    """Main entry point for the auto-fix script."""
    parser = argparse.ArgumentParser(description="Auto-fix common documentation validation issues")
    parser.add_argument("directory", help="Directory to process")
    parser.add_argument("--apply", action="store_true", help="Apply fixes (default is dry-run)")
    parser.add_argument("--patterns", nargs="+",
                       choices=["financial-precision", "missing-imports", "deprecated-patterns"],
                       default=["financial-precision", "missing-imports", "deprecated-patterns"],
                       help="Specific patterns to fix")
    parser.add_argument("--report", type=str, help="Save report to file")

    args = parser.parse_args()

    # Validate directory
    if not Path(args.directory).exists():
        print(f"❌ Directory does not exist: {args.directory}")
        return 1

    # Create auto-fixer
    fixer = DocumentationAutoFixer(dry_run=not args.apply)

    try:
        # Run auto-fix
        results = fixer.fix_directory(args.directory, args.patterns)

        # Generate and display report
        report = fixer.generate_fix_report(results)
        print("\n" + "="*60)
        print(report)

        # Save report if requested
        if args.report:
            with Path(args.report).open('w') as f:
                f.write(report)
            print(f"\n📄 Report saved to: {args.report}")

        # Return appropriate exit code
        if results["errors"]:
            return 1
        if results["total_fixes"] > 0 and not args.apply:
            print(f"\n💡 Found {results['total_fixes']} fixable issues. Run with --apply to fix them.")
            return 0
        return 0

    except Exception as e:
        print(f"❌ Error running auto-fix: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
