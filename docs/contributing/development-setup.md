# Development Environment Setup

Complete guide to setting up your development environment for contributing to FiveTwenty.

---

## Prerequisites

**Required:**
- **Python 3.10+** - Modern type hints support
- **Git** - Version control
- **uv** - Fast Python package manager

**Optional:**
- **VS Code** - Recommended (includes project config)

---

## Quick Setup

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with Homebrew
brew install uv
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty

# Complete setup (installs deps, runs checks)
uv run poe setup
```

The `setup` command runs:

- `uv sync` - Install all dependencies
- Install package in editable mode
- Run type checking
- Run tests to verify

### 3. Verify Installation

```bash
# Fast development checks
uv run poe dev

# Expected: Code formatted, type checking passed, all tests passed
```

---

## Essential Commands

### Development Workflow

```bash
# Fast feedback during development
uv run poe dev              # Format, typecheck, test (~15s)

# Pre-commit checks
uv run poe check-fast            # Format check, lint, typecheck, unit tests (~30s)

# Code quality only (no tests)
uv run poe quality          # Format, lint, typecheck (~10s)
```

### Testing

```bash
uv run pytest               # Unit tests plus skipped live integration tests
uv run poe test             # Unit tests only
uv run poe test-integration # Live integration tests only; requires practice credentials
uv run pytest --cov=fivetwenty --cov-report=html  # Coverage report
```

### Code Quality

```bash
uv run ruff format .        # Format code
uv run ruff check .         # Check linting
uv run ruff check --fix .   # Auto-fix issues
uv run mypy fivetwenty/     # Type checking (strict mode)
```

### Documentation

```bash
uv run mkdocs serve         # Local preview (auto-reload)
uv run mkdocs build --clean # Build static site
uv run poe docs-validate    # Validate documentation
```

---

## Environment Variables

### Development `.env` File

```bash
# OANDA API credentials (PRACTICE ONLY)
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-practice-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_ACCOUNT_ALIAS=dev_account

# Optional
FIVETWENTY_LOG_LEVEL=DEBUG
FIVETWENTY_DEFAULT_TIMEOUT=30
```

### Testing (Optional)

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-practice-account
```

**Security:**
- **Never use live trading accounts** for development
- **Never commit credentials** to git
- **Use practice accounts only**

---

## IDE Setup

### VS Code (Recommended)

Project includes `.vscode/` configuration:

- **Ruff** - Auto-format and lint on save
- **MyPy** - Type checking enabled
- **Pytest** - Debug test integration

**Install extensions:**
- Python (Microsoft)
- Ruff (Astral Software)
- markdownlint (David Anson)

### Other IDEs

**PyCharm:**
- Install Ruff plugin
- Configure MyPy as external tool
- Set pytest as test runner

**Vim/Neovim:**
- Use ruff-lsp for formatting/linting
- Configure pytest runner

---

## Common Development Tasks

### Adding a New Endpoint

1. Create endpoint method in `fivetwenty/endpoints/`
2. Import and attach to AsyncClient/Client in `client.py`
3. Add Pydantic models if needed (check the existing 130+ models first)
4. Write unit and integration tests
5. Add API reference documentation
6. Run `uv run poe check-fast`

### Adding New Models

1. Define Pydantic model in `fivetwenty/models.py`
2. Use `Decimal` for money, proper field aliases
3. Write validation tests
4. Document all fields

### Writing Tests

```python
# Unit test - Mock HTTP responses
@pytest.mark.asyncio
async def test_get_account(client: AsyncClient) -> None:
    with patch.object(client, "_request") as mock:
        mock.return_value.json.return_value = {"account": {...}}
        result = await client.accounts.get_accounts("123")
        assert result.id == "123"

# Integration test - Real API (practice account)
@pytest.mark.integration
async def test_real_api(client: AsyncClient) -> None:
    async with client:
        summary = await client.accounts.get_accounts(account_id)
        assert isinstance(summary.balance, Decimal)
```

---

## Troubleshooting

### uv not found
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

### Type checking failures
```bash
# Check specific file for details
uv run mypy fivetwenty/client.py
```

### Test failures
```bash
# Verbose output
uv run pytest -v

# Specific test
uv run pytest tests/unit/test_client.py::test_name -v
```

### Import errors
```bash
# Reinstall in dev mode
uv sync --dev

# Verify installation
uv run python -c "import fivetwenty; print(fivetwenty.__file__)"
```

---

## Performance Tips

### Fast Development Cycle

```bash
uv run poe dev              # Fastest - Use during active development
uv run poe test             # Unit tests only - Quick iteration
uv run pytest -n auto       # Parallel tests (if pytest-xdist installed)
```

### IDE Configuration

- Configure Ruff to run on save
- Enable real-time type checking
- Use test discovery for quick test execution

---

## Next Steps

Once your environment is ready:

1. **Explore codebase** - `fivetwenty/client.py` and `fivetwenty/models.py`
2. **Run examples** - Try scripts in `examples/`
3. **Review [Code Style Guide](code-style.md)** - Learn patterns and standards
4. **Read [Testing Guide](testing-guide.md)** - Test practices and coverage
5. **Pick an issue** - Look for "good first issue" on GitHub
6. **Join [Discussions](https://github.com/NimbleOx/fivetwenty/discussions)** - Ask questions

**Happy contributing!**
