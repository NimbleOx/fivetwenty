#!/usr/bin/env python3
"""
Debug script to find the remaining 6 code example validation issues in tutorials.
"""

import sys
from pathlib import Path

# Add the validation directory to the path for imports
validation_dir = Path(__file__).parent.parent
sys.path.insert(0, str(validation_dir))

from validators.code_examples import CodeExampleValidator


def main():
    """Run code examples validator and show detailed issues in tutorials."""
    print("🔍 Running code examples validator on tutorials directory...")

    # Create validator instance
    validator = CodeExampleValidator()

    # Manually override the file patterns to only look at tutorials
    validator.file_patterns = ["docs/tutorials/**/*.md"]

    # Run validation
    result = validator.validate()

    print("\n📊 Validation Results:")
    print(f"   Status: {result.status}")
    print(f"   Issues Found: {result.issues_found}")
    print(f"   Total Code Blocks Checked: {result.total_checked}")
    print(f"   Files Processed: {result.details.get('files_checked', 0)}")

    if result.issues_found > 0:
        print(f"\n🚨 Issues Found ({len(validator.code_issues)}):")
        print("=" * 80)

        # Group issues by file for better organization
        issues_by_file = {}
        for issue in validator.code_issues:
            file_path = issue['file']
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)

        for file_path, file_issues in sorted(issues_by_file.items()):
            print(f"\n📁 {file_path}")
            print("-" * 60)

            for i, issue in enumerate(file_issues, 1):
                line_num = issue.get('line', 'unknown')
                issue_type = issue.get('type', 'unknown')
                severity = issue.get('severity', 'unknown')
                message = issue.get('message', 'No message')

                print(f"  {i}. Line {line_num}: {issue_type} ({severity})")
                print(f"     {message}")
                if 'suggestion' in issue:
                    print(f"     💡 Suggestion: {issue['suggestion']}")
                if 'code_snippet' in issue:
                    snippet = issue['code_snippet']
                    if len(snippet) > 100:
                        snippet = snippet[:100] + "..."
                    print(f"     📝 Code: {snippet}")
                print()
    else:
        print("\n✅ No issues found!")

if __name__ == "__main__":
    main()
