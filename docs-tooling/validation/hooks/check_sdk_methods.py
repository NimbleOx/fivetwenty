#!/usr/bin/env python3
"""
Pre-commit hook for SDK method validation.

This hook validates that documentation uses current SDK method names
and not deprecated patterns.
"""

import sys
from pathlib import Path

# Add the validation directory to the path for imports
validation_root = Path(__file__).parent.parent
sys.path.insert(0, str(validation_root))

from validators.sdk_methods import SDKMethodValidator  # noqa: E402


def main() -> int:
    """Run SDK method validation as a pre-commit hook."""
    validator = SDKMethodValidator()
    result = validator.validate()

    if result.issues_found > 0:
        print("❌ SDK method validation failed!")
        print(f"Found {result.issues_found} deprecated method references.")
        print("\nPlease update deprecated method names:")
        print("  create_market() → post_market_order()")
        print("  create_limit() → post_limit_order()")
        print("  create_stop() → post_stop_order()")
        print("  create_order() → post_order()")
        print("\nRun 'uv run python docs-tooling/validation/cli.py run sdk-methods' for details.")
        return 1

    print("✅ SDK method validation passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
