# Installation

## Requirements

- Python 3.10 or higher
- An OANDA account (practice or live)
- API access token from OANDA

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

```python
import fivetwenty

print(fivetwenty.__version__)
# Output: 0.1.1
```

## Dependencies

from fivetwenty import Environment

The SDK automatically installs these minimal core dependencies:

- **httpx** - Modern async HTTP client with connection pooling
- **pydantic** - Data validation and serialization (v2+)

## Environment Setup

### Using uv (Recommended)

For faster package management with automatic virtual environment handling:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
uv venv
uv add fivetwenty
```

## Next Steps

Now that you have the SDK installed:

1. [Set up authentication](authentication.md) with your OANDA API token
2. [Learn about environments](environments.md) (practice vs live)
3. [Make your first trade](first-trade.md)

!!! tip "Development Setup"
    If you're contributing to the SDK, see the project's GitHub repository for development setup instructions.
