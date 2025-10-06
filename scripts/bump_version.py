#!/usr/bin/env python3
"""Interactive version bumping script."""

import re
import sys
from pathlib import Path


def main() -> None:
    """Bump version interactively."""
    pyproject = Path("pyproject.toml")

    # Read current version
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)

    if not match:
        print("Error: Could not find version in pyproject.toml")
        sys.exit(1)

    current = match.group(1)
    major, minor, patch = map(int, current.split("."))

    print(f"Current version: {current}")
    print("\nBump type:")
    print("  1) Major (breaking changes)")
    print("  2) Minor (new features)")
    print("  3) Patch (bug fixes)")
    print("  4) Custom version")

    choice = input("\nSelect (1-4): ").strip()

    if choice == "1":
        new_version = f"{major + 1}.0.0"
    elif choice == "2":
        new_version = f"{major}.{minor + 1}.0"
    elif choice == "3":
        new_version = f"{major}.{minor}.{patch + 1}"
    elif choice == "4":
        new_version = input("Enter version (e.g., 1.2.3): ").strip()
    else:
        print("Invalid choice")
        sys.exit(1)

    # Confirm
    confirm = input(f"\nBump {current} → {new_version}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Cancelled")
        sys.exit(1)

    # Update pyproject.toml
    new_content = re.sub(r'^version = "[^"]+"', f'version = "{new_version}"', content, flags=re.MULTILINE)

    pyproject.write_text(new_content)
    print(f"✓ Version bumped to {new_version}")


if __name__ == "__main__":
    main()
