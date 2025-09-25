#!/usr/bin/env python3
"""Check remaining critical errors after fixes."""

import subprocess
import sys

def main():
    """Run validation and show only errors."""

    try:
        # Run validation from docs_validation directory
        result = subprocess.run([
            sys.executable, "-m", "src.cli", "validate",
            "--project-root", "..", "--verbose"
        ],
        cwd="docs_validation",
        env={"PYTHONPATH": "docs_validation"},
        capture_output=True,
        text=True,
        timeout=60
        )

        output_lines = result.stdout.split('\n')

        # Extract only error lines
        in_issues_section = False
        error_count = 0
        current_file = ""

        for line in output_lines:
            if "📋 Issues Found:" in line:
                in_issues_section = True
                continue

            if in_issues_section:
                # Track current file
                if line.strip().startswith("📄"):
                    current_file = line.strip()[2:].strip()
                    continue

                # Only show errors (❌)
                if "❌" in line:
                    error_count += 1
                    print(f"\n🔴 ERROR #{error_count}")
                    print(f"📁 File: {current_file}")
                    print(f"❌ {line.strip()}")

                    # Show next few lines for context
                    continue

        print(f"\n📊 Total remaining errors found: {error_count}")

    except Exception as e:
        print(f"❌ Error running validation: {e}")

if __name__ == "__main__":
    main()