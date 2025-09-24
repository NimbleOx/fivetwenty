# Installation

## Requirements

- Python 3.10 or higher
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
# Output: 0.1.1
```

## Dependencies

The SDK automatically installs these minimal core dependencies:

- **httpx** - Modern async HTTP client with connection pooling
- **pydantic** - Data validation and serialization (v2+)

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

## Next Steps

Now that you have the SDK installed:

1. [Set up authentication](authentication.md) with your OANDA API token
2. [Learn about environments](environments.md) (practice vs live)
3. [Make your first trade](first-trade.md)

!!! tip "Development Setup"
    If you're contributing to the SDK, see the project's GitHub repository for development setup instructions.
