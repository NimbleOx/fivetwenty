# Installation

## Requirements

- Python 3.10 or higher
- An OANDA account (practice or live)
- API access token from OANDA
- **uv** - Modern Python package manager ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))

## Environment Setup

### Using uv (Recommended)

For optimal package management with automatic virtual environment handling:

```bash
# Create project with virtual environment
uv venv

# Add FiveTwenty to your project
uv add fivetwenty
```

## Install from PyPI

The recommended way to install FiveTwenty is via uv:

```bash
uv add fivetwenty
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
uv sync --dev
```

## Verify Installation

Test your installation:

<!-- fragment: Demo version check with comprehensive installation validation -->
```python
# Step 1: Import FiveTwenty SDK to verify successful installation
# This confirms the package was installed correctly and is accessible
import fivetwenty

# Step 2: Display installed version for verification and troubleshooting
# Version information helps confirm you have the expected release installed
print(f"FiveTwenty SDK version: {fivetwenty.__version__}")

# Step 3: Optional - Verify core dependencies are available
# This additional check ensures all required components are properly installed
try:
    import httpx
    import pydantic
    print("Success Core dependencies verified: httpx and pydantic available")
    print("Starting FiveTwenty SDK installation complete and ready for use")
except ImportError as e:
    print(f"⚠️ Dependency issue detected: {e}")
    print("   Run 'uv add fivetwenty' to reinstall with dependencies")
```

Expected output:
```text
0.1.1 # or current version number
```

## Dependencies

The SDK automatically installs these minimal core dependencies:

- **httpx** - Modern async HTTP client with connection pooling
- **pydantic** - Data validation and serialization (v2+)

## Next Steps

Now that you have the SDK installed:

1. [Set up authentication](authentication.md) with your OANDA API token
2. [Make your first trade](first-trade.md)

For a complete understanding of practice vs live trading, see the [Environment Management Guide](../../guides/understanding/environments.md).

!!! tip "Development Setup"
    If you're contributing to the SDK, see the project's GitHub repository for development setup instructions.
