# FiveTwenty Documentation Validation v2.0

Fast, reliable documentation validation for the FiveTwenty trading SDK.

## Features

- 🚀 **Fast**: Sub-2-second validation for typical documentation sets
- 🎯 **Financial Safety**: Validates Decimal usage and detects exposed API tokens
- 🔧 **Incremental**: Only validates changed files for quick feedback
- 📊 **Rich Output**: Beautiful terminal output with clear error messages
- ⚙️ **Configurable**: YAML-based configuration with quality gates
- 🔀 **Parallel**: Multi-threaded validation for performance

## Quick Start

```bash
# Install dependencies
uv sync

# Run validation on all documentation
uv run python -m src.cli validate

# Run validation on specific files
uv run python -m src.cli check docs/tutorials/getting-started.md

# List available validators
uv run python -m src.cli list-validators
```

## Validators

### Financial Precision
- Validates use of `Decimal` instead of `float` for financial calculations
- Checks for proper precision in monetary values
- Enforces financial safety requirements

### Security
- Scans for exposed API tokens and secrets
- Detects OANDA v20 tokens, JWT tokens, and generic credentials
- Excludes common placeholder values

### Markdown Syntax
- Validates markdown structure and syntax
- Checks headers, links, code blocks, and lists
- Detects unclosed code blocks

### Python Syntax
- Validates Python code in `.py` files and markdown code blocks
- Uses AST parsing for accurate syntax checking
- Provides line-level error reporting

### Cross References
- Validates internal links and references
- Checks relative file paths and anchor links
- Ensures documentation integrity

## Configuration

Configuration is loaded from `config/validation.yml`:

```yaml
# Enable/disable validators
validators:
  financial_precision:
    enabled: true
    options:
      strict_mode: true

  security:
    enabled: true
    options:
      severity_filter: "high"

# Quality gates
quality_gates:
  max_errors: 5
  max_warnings: 100
  min_success_rate: 90.0
  fail_on_error: true
```

## Performance

- **Target**: < 2 seconds for full validation
- **Incremental**: < 500ms for changed files
- **Memory**: < 100MB for large documentation sets
- **Parallel**: Configurable worker threads

## Architecture

```
src/
├── cli.py              # Command-line interface
├── config.py           # Configuration management
├── engine.py           # Validation engine
├── models.py           # Data models
├── validators.py       # Base validator classes
└── validators/         # Validator implementations
    ├── financial.py
    ├── security.py
    ├── markdown.py
    ├── python.py
    └── cross_references.py
```

## Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
uv run pytest

# Format code
uv run ruff format .

# Type checking
uv run mypy src/
```