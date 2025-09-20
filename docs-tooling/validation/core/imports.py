"""
Import utilities for validation modules.

Provides centralized import path management.
"""

import sys
from pathlib import Path


def setup_validation_imports() -> None:
    """
    Setup import paths for validator modules.

    This ensures that validators can import from the core modules
    regardless of where they are executed from.
    """
    validation_root = Path(__file__).parent.parent
    validation_root_str = str(validation_root)

    # Only add if not already in path to avoid duplicates
    if validation_root_str not in sys.path:
        sys.path.insert(0, validation_root_str)
