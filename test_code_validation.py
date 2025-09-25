#!/usr/bin/env python3
"""Direct test of the code executability validator."""

import sys
from pathlib import Path

# Add the validation system to path
sys.path.insert(0, str(Path(__file__).parent / "docs_validation" / "src"))

from validators.code_executability import CodeExecutabilityValidator
from models import FileInfo

def test_validator():
    """Test the code validator on a specific file."""
    validator = CodeExecutabilityValidator()

    # Test on docs/index.md
    test_file = Path("docs/index.md")
    if not test_file.exists():
        print(f"❌ Test file {test_file} not found")
        return

    print(f"🔍 Testing validator on {test_file}")

    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()

    file_info = FileInfo(path=test_file, relative_path=test_file, size=len(content))
    result = validator.validate_file(file_info, content, {})

    print(f"✅ Validation {'PASSED' if result.passed else 'FAILED'}")
    print(f"📊 Found {len(result.issues)} issues")

    for issue in result.issues:
        severity_emoji = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}.get(issue.severity.value, "•")
        print(f"{severity_emoji} Line {issue.line}: {issue.message}")
        if issue.context:
            print(f"   Context: {issue.context}")
        if issue.suggestion:
            print(f"   💡 Suggestion: {issue.suggestion}")
        print()

if __name__ == "__main__":
    test_validator()