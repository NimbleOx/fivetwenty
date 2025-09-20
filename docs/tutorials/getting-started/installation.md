# Installation

## Requirements

- Python 3.9 or higher
- An OANDA account (practice or live)
- API access token from OANDA

## Install from PyPI

The recommended way to install FiveTwenty is via pip:

```bash
pip install fivetwenty
```

Or if you're using uv (recommended for faster installs):

```bash
uv pip install fivetwenty
```

## Install from Source

For the latest development version:

```bash
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty
pip install -e .
```

## Verify Installation

Test your installation:

```python
import fivetwenty
print(fivetwenty.__version__)
# Output: 20.1.0
```

## Dependencies

The SDK automatically installs these core dependencies:

- **httpx** - Modern async HTTP client
- **pydantic** - Data validation and settings management
- **python-dateutil** - Date/time handling
- **typing-extensions** - Enhanced type hints

## Optional Dependencies

For development and testing:

```bash
pip install fivetwenty[dev]
```

This includes:
- pytest & pytest-asyncio for testing
- ruff for linting
- mypy for type checking
- mkdocs-material for documentation

## Environment Setup

### Virtual Environment (Recommended)

Always use a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install SDK
pip install fivetwenty
```

### Using uv

For faster package management with uv:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uv venv
uv pip install fivetwenty
```

## Troubleshooting

### SSL Certificate Errors

If you encounter SSL errors, update your certificates:

```bash
pip install --upgrade certifi
```

### Import Errors

Ensure you're using Python 3.9+:

```bash
python --version
```

### Permission Errors

On macOS/Linux, you might need to use sudo or --user:

```bash
pip install --user fivetwenty
```

## Next Steps

Now that you have the SDK installed:

1. [Set up authentication](authentication.md) with your OANDA API token
2. [Learn about environments](environments.md) (practice vs live)
3. [Make your first trade](first-trade.md)

!!! tip "Development Setup"
    If you're contributing to the SDK, see the project's GitHub repository for development setup instructions.
