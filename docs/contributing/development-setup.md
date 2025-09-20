# Development Environment Setup

Complete guide to setting up your development environment for contributing to fivetwenty.

---

## Prerequisites

### **System Requirements**

- **Python 3.10+** - Required for modern type hints and syntax
- **Git** - For version control and collaboration
- **uv** - Fast Python package manager (automatically handles virtual environments)

### **Optional Tools**

- **VS Code** - Recommended editor (project includes configuration)
- **Node.js** - For additional documentation tools (if needed)

---

## Quick Setup

### **1. Clone and Setup**

```bash
# Clone the repository
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty

# Complete setup (installs dependencies, runs initial checks)
uv run poe setup
```

The `setup` command will:
- Install all dependencies with `uv sync`
- Install package in development mode with `uv pip install -e .`
- Run type checking to verify setup
- Run tests to ensure everything works

### **2. Verify Installation**

```bash
# Should run without errors
uv run poe dev

# Expected output:
# ✅ Code formatted
# ✅ Type checking passed
# ✅ Tests passed (158 tests)
```

---

## Detailed Setup

### **Installing uv**

If you don't have uv installed:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# With pip
pip install uv

# With homebrew
brew install uv
```

### **Project Dependencies**

The project uses dependency groups defined in `pyproject.toml`:

```toml
[dependency-groups]
dev = [
    "pytest>=7.4.0",           # Testing framework
    "pytest-asyncio>=0.21.0",  # Async test support
    "pytest-mock>=3.12.0",     # Mocking utilities
    "pytest-vcr>=1.0.2",       # HTTP response recording
    "pytest-cov>=4.0.0",       # Coverage reporting
    "mypy>=1.7.0",            # Type checking
    "ruff>=0.1.0",            # Formatting and linting
    "poethepoet>=0.24.0",     # Task runner
    "python-dotenv>=1.0.0",   # Environment variables
    "mkdocs>=1.6.1",          # Documentation
    "mkdocs-material>=9.6.19", # Documentation theme
    # ... and more
]
```

### **Manual Dependency Installation**

If needed, install dependencies manually:

```bash
# Install all dependencies
uv sync

# Install package in development mode
uv pip install -e .

# Install with all development dependencies
uv pip install -e .[dev]
```

---

## Development Tools

### **Code Quality Tools**

#### **Ruff** - Formatting and Linting

Ruff handles both code formatting and linting with extensive rule coverage:

```bash
# Format code (modifies files)
uv run ruff format .

# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .
```

Configuration in `pyproject.toml`:
- Line length: 320 (effectively unlimited)
- 35+ rule categories enabled
- Special handling for tests and examples

#### **MyPy** - Type Checking

Strict type checking is required:

```bash
# Type check the entire codebase
uv run mypy fivetwenty/

# MyPy configuration
strict = true                    # Maximum strictness
disallow_untyped_defs = true    # All functions must have types
warn_return_any = true          # Warn about Any returns
```

#### **pytest** - Testing

Comprehensive testing with async support:

```bash
# All tests
uv run pytest

# With coverage
uv run pytest --cov=fivetwenty --cov-report=html

# Specific test markers
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
```

### **Documentation Tools**

#### **MkDocs** - Documentation Site

```bash
# Serve locally (auto-reloads on changes)
uv run mkdocs serve

# Build static site
uv run mkdocs build --clean

# Deploy to GitHub Pages
uv run mkdocs gh-deploy --force
```

#### **MDFormat** - Markdown Linting

```bash
# Check markdown formatting
uv run poe markdown-check

# Auto-format markdown (careful - may change structure)
uv run poe markdown-format
```

---

## IDE Configuration

### **VS Code Setup**

The project includes `.vscode/` configuration:

**Settings (`.vscode/settings.json`):**
- Ruff formatting and linting enabled
- MyPy type checking configured
- Python interpreter path set correctly
- Markdown preview enhanced

**Recommended Extensions:**
- Python (Microsoft)
- Ruff (Astral Software)
- Python Type Hint (Microsoft)
- markdownlint (David Anson)

**Launch Configuration:**
- Debug pytest tests
- Run specific test files
- Debug with environment variables loaded

### **Other IDEs**

**PyCharm:**
- Install Ruff plugin
- Configure MyPy as external tool
- Set up pytest as test runner
- Enable type checking inspections

**Vim/Neovim:**
- Use coc.nvim or similar for Python support
- Configure ruff-lsp for formatting/linting
- Set up pytest runner

---

## Environment Variables

### **Development Environment**

Create `.env` file for development:

```bash
# OANDA API credentials (practice account only)
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-practice-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_ACCOUNT_ALIAS=dev_account

# Optional: Enable debug logging
FIVETWENTY_LOG_LEVEL=DEBUG

# Optional: Custom API timeouts
FIVETWENTY_DEFAULT_TIMEOUT=30
```

### **Testing Environment**

For integration tests (optional):

```bash
# Test-specific credentials
TEST_OANDA_TOKEN=your-practice-token
TEST_OANDA_ACCOUNT=your-practice-account
TEST_OANDA_ENVIRONMENT=practice

# VCR.py configuration
VCR_RECORD_MODE=once  # once, new_episodes, all, none
```

### **Security Notes**

- **Never use live trading accounts** for development/testing
- **Never commit credentials** to version control
- **Use practice accounts only** for all development work
- **Rotate tokens regularly** as a security practice

---

## Common Development Tasks

### **Adding a New Endpoint**

1. **Create endpoint method** in appropriate `fivetwenty/endpoints/` file
2. **Add to client** by importing and attaching to AsyncClient/Client
3. **Create models** if new response types needed
4. **Write tests** - both unit and integration
5. **Add documentation** - API reference and examples
6. **Run quality checks** - `uv run poe check`

### **Adding New Models**

1. **Define Pydantic model** in `fivetwenty/models.py`
2. **Use proper types** - Decimal for money, datetime for times
3. **Add field aliases** for OANDA API compatibility
4. **Write validation tests** - ensure roundtrip serialization works
5. **Document all fields** with clear descriptions

### **Writing Tests**

1. **Unit tests** - Mock HTTP responses, test logic
2. **Integration tests** - Use VCR.py for real API interactions
3. **Mark tests appropriately** - `@pytest.mark.unit` or `@pytest.mark.integration`
4. **Test edge cases** - Error conditions, boundary values
5. **Maintain coverage** - Aim for high coverage on new code

### **Updating Documentation**

1. **API Reference** - Update method signatures and examples
2. **Tutorials** - Add new learning content if appropriate
3. **How-to Guides** - Add practical solutions for common problems
4. **Examples** - Update code examples and notebooks

---

## Troubleshooting

### **Common Issues**

#### **uv not found**
```bash
# Install uv first
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or ~/.zshrc
```

#### **Type checking failures**
```bash
# Check mypy version
uv run mypy --version

# Run on specific file for detailed errors
uv run mypy fivetwenty/client.py
```

#### **Test failures**
```bash
# Run with verbose output
uv run pytest -v

# Run specific failing test
uv run pytest tests/unit/test_client.py::test_specific -v
```

#### **Import errors during development**
```bash
# Reinstall in development mode
uv pip install -e .

# Check Python path
uv run python -c "import fivetwenty; print(fivetwenty.__file__)"
```

### **Getting Help**

1. **Check existing issues** on GitHub
2. **Run diagnostics** - `uv run poe setup` to verify environment
3. **Share error output** when asking for help
4. **Include environment details** - Python version, OS, uv version

---

## Performance Tips

### **Fast Development Workflow**

```bash
# Use 'dev' for fastest feedback during development
uv run poe dev      # ~15 seconds (format, typecheck, test)

# Use 'check' before committing
uv run poe check    # ~30 seconds (format, lint-core, typecheck, test)

# Use 'quality' for code quality only (no tests)
uv run poe quality  # ~10 seconds
```

### **Incremental Testing**

```bash
# Run only fast unit tests during development
uv run poe test-unit

# Run integration tests less frequently
uv run poe test-integration

# Use pytest-xdist for parallel tests (if needed)
uv run pytest -n auto
```

### **IDE Performance**

- **Configure file watchers** to run ruff on save
- **Enable type checking** in real-time for immediate feedback
- **Use test discovery** to run tests from IDE
- **Configure memory settings** for large codebases

---

## Next Steps

Once your environment is set up:

1. **Explore the codebase** - Start with `fivetwenty/client.py` and `fivetwenty/models.py`
2. **Run the examples** - Try `examples/scripts/basic_usage.py`
3. **Read the architecture** - Check `docs/explanation/sdk-architecture.md`
4. **Pick an issue** - Look for "good first issue" labels on GitHub
5. **Join discussions** - Participate in GitHub Discussions

Happy contributing! 🚀