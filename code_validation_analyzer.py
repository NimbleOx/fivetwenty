#!/usr/bin/env python3
"""
Code Validation Report Generator
Analyzes validation results and creates detailed reports for code blocks in documentation.
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List, Set

@dataclass
class CodeBlock:
    file_path: str
    line_start: int
    line_end: int
    language: str
    content: str
    errors: List[str]
    warnings: List[str]

@dataclass
class ValidationIssue:
    file_path: str
    line: int
    message: str
    severity: str
    rule_id: str
    context: str
    suggestion: str

def parse_validation_output(report_file: Path) -> List[ValidationIssue]:
    """Parse the validation report and extract issues."""
    issues = []

    if not report_file.exists():
        print(f"❌ Report file {report_file} not found")
        return issues

    content = report_file.read_text()

    # Parse issues from the validation output
    current_file = ""

    # Split into sections by file
    sections = re.split(r'📄 \.\.(.*\.md)', content)

    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            file_path = sections[i].strip()
            issue_content = sections[i + 1]

            # Extract individual issues
            issue_pattern = r'(❌|⚠️|ℹ️)\s+(.+?):(\d+)\s*\n\s*Context:\s*(.+?)\n\s*💡\s*(.+?)\n\s*Rule:\s*(.+?)(?=\n|$)'

            for match in re.finditer(issue_pattern, issue_content, re.MULTILINE | re.DOTALL):
                severity_emoji, message, line_str, context, suggestion, rule_id = match.groups()

                severity_map = {"❌": "ERROR", "⚠️": "WARNING", "ℹ️": "INFO"}
                severity = severity_map.get(severity_emoji, "UNKNOWN")

                issues.append(ValidationIssue(
                    file_path=file_path,
                    line=int(line_str),
                    message=message.strip(),
                    severity=severity,
                    rule_id=rule_id.strip(),
                    context=context.strip(),
                    suggestion=suggestion.strip()
                ))

    return issues

def extract_code_blocks_from_file(file_path: Path) -> List[CodeBlock]:
    """Extract all code blocks from a markdown file."""
    if not file_path.exists():
        return []

    content = file_path.read_text()
    lines = content.split('\n')
    code_blocks = []

    in_code_block = False
    code_lines = []
    start_line = 0
    language = ""

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        if stripped.startswith('```'):
            if not in_code_block:
                # Starting code block
                in_code_block = True
                start_line = line_num
                language = stripped[3:].strip() or "text"
                code_lines = []
            else:
                # Ending code block
                in_code_block = False
                if code_lines and language.lower() in ['python', 'py', '']:
                    code_blocks.append(CodeBlock(
                        file_path=str(file_path),
                        line_start=start_line + 1,
                        line_end=line_num - 1,
                        language=language,
                        content='\n'.join(code_lines),
                        errors=[],
                        warnings=[]
                    ))
                code_lines = []
        elif in_code_block:
            code_lines.append(line)

    return code_blocks

def analyze_issues_by_file(issues: List[ValidationIssue]) -> Dict:
    """Organize issues by file and create summary statistics."""
    by_file = defaultdict(lambda: {"errors": [], "warnings": [], "info": []})

    for issue in issues:
        severity_key = issue.severity.lower() + "s"
        if severity_key in by_file[issue.file_path]:
            by_file[issue.file_path][severity_key].append(issue)

    return dict(by_file)

def generate_detailed_report(issues: List[ValidationIssue], output_file: Path):
    """Generate a comprehensive markdown report."""

    # Organize data
    by_file = analyze_issues_by_file(issues)
    by_rule = defaultdict(list)
    for issue in issues:
        by_rule[issue.rule_id].append(issue)

    # Count statistics
    total_files = len(by_file)
    total_errors = sum(len(data["errors"]) for data in by_file.values())
    total_warnings = sum(len(data["warnings"]) for data in by_file.values())

    report = f"""# FiveTwenty Documentation Code Validation Report

Generated: {Path().cwd()}

## Summary

- **Total Files Analyzed**: {total_files}
- **Total Issues**: {len(issues)}
  - **Errors**: {total_errors} ❌
  - **Warnings**: {total_warnings} ⚠️
- **Success Rate**: {((total_files * 100 - len(issues)) / max(total_files * 100, 1)):.1f}%

## Issue Categories

### Most Common Rule Violations

"""

    # Top rule violations
    rule_counts = [(rule, len(issues_list)) for rule, issues_list in by_rule.items()]
    rule_counts.sort(key=lambda x: x[1], reverse=True)

    for rule, count in rule_counts[:10]:
        report += f"- **{rule}**: {count} issues\n"

    report += f"""

## Detailed Analysis by File

Files sorted by issue count (highest first):

"""

    # Sort files by total issue count
    file_issues = [(file_path, len(data["errors"]) + len(data["warnings"]))
                   for file_path, data in by_file.items()]
    file_issues.sort(key=lambda x: x[1], reverse=True)

    for file_path, issue_count in file_issues[:20]:  # Top 20 files
        data = by_file[file_path]
        error_count = len(data["errors"])
        warning_count = len(data["warnings"])

        report += f"""
### 📄 {file_path}

**Issues**: {issue_count} total ({error_count} errors, {warning_count} warnings)

"""

        # Show errors first
        if data["errors"]:
            report += "#### Errors ❌\n\n"
            for issue in data["errors"][:5]:  # Limit to 5 per file
                report += f"""- **Line {issue.line}**: {issue.message}
  - Context: `{issue.context}`
  - Rule: `{issue.rule_id}`
  - 💡 {issue.suggestion}

"""

        # Show warnings
        if data["warnings"] and len(data["warnings"]) <= 10:  # Only show warnings for files with few warnings
            report += "#### Warnings ⚠️\n\n"
            for issue in data["warnings"][:3]:  # Limit to 3 warnings per file
                report += f"""- **Line {issue.line}**: {issue.message}
  - Context: `{issue.context}`
  - Rule: `{issue.rule_id}`

"""

    report += f"""

## Recommendations

### High Priority Fixes (Errors)

1. **Async Function Wrappers**: {len([i for i in issues if i.rule_id == "code_async_outside_function"])} files need proper async function wrappers
   - Add `async def main():` wrapper around async code
   - Add `asyncio.run(main())` to execute async functions
   - Most affected: API reference documentation

2. **Missing Account ID**: {len([i for i in issues if i.rule_id == "code_missing_account_id"])} instances need account_id parameter
   - Add `account_id` parameter when providing token directly to AsyncClient

### Medium Priority Fixes (Warnings)

1. **Missing Imports**: {len([i for i in issues if i.rule_id == "code_undefined_variable"])} undefined variables
   - Add proper import statements at the top of code examples
   - Most common missing imports: AsyncClient, Environment, Decimal, InstrumentName

2. **Import Organization**: Standardize import statements across all code examples

### Suggested Action Plan

1. **Phase 1**: Fix all async function wrapper errors ({len([i for i in issues if i.rule_id == "code_async_outside_function"])} issues)
2. **Phase 2**: Add missing imports to reduce warning noise
3. **Phase 3**: Create code example templates for consistency

## Files Requiring Immediate Attention

These files have the most critical errors:

"""

    # Files with most errors
    error_files = [(file_path, len(data["errors"])) for file_path, data in by_file.items()
                   if data["errors"]]
    error_files.sort(key=lambda x: x[1], reverse=True)

    for file_path, error_count in error_files[:10]:
        report += f"- **{file_path}**: {error_count} errors\n"

    report += """

## Validation Configuration

The validation is currently configured to check:

- ✅ Python syntax in code blocks
- ✅ Async/await usage patterns
- ✅ FiveTwenty-specific API usage
- ✅ Import availability
- ✅ Variable definition checking

Consider adjusting validation rules based on this report to focus on the most impactful issues.
"""

    # Write report
    output_file.write_text(report)
    print(f"✅ Detailed report written to {output_file}")

def main():
    """Main function to generate the report."""
    report_file = Path("docs_validation/validation_report_updated.txt")
    output_file = Path("code_validation_detailed_report.md")

    print("🔍 Parsing validation results...")
    issues = parse_validation_output(report_file)

    if not issues:
        print("❌ No issues found in validation report. Check if validation ran successfully.")
        return

    print(f"📊 Found {len(issues)} issues across {len(set(i.file_path for i in issues))} files")

    print("📝 Generating detailed report...")
    generate_detailed_report(issues, output_file)

    # Also create a JSON export for programmatic use
    json_file = Path("code_validation_results.json")
    json_data = {
        "summary": {
            "total_issues": len(issues),
            "total_files": len(set(i.file_path for i in issues)),
            "errors": len([i for i in issues if i.severity == "ERROR"]),
            "warnings": len([i for i in issues if i.severity == "WARNING"])
        },
        "issues": [
            {
                "file_path": issue.file_path,
                "line": issue.line,
                "message": issue.message,
                "severity": issue.severity,
                "rule_id": issue.rule_id,
                "context": issue.context,
                "suggestion": issue.suggestion
            }
            for issue in issues
        ]
    }

    json_file.write_text(json.dumps(json_data, indent=2))
    print(f"📁 JSON data exported to {json_file}")

if __name__ == "__main__":
    main()