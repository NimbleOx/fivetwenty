# Contributing to FiveTwenty

Thank you for contributing to FiveTwenty! This guide helps you get started with our OANDA v20 API Python SDK.

---

## Quick Start

### 1. Set Up Environment

```bash
# Clone repository
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty

# Set up (requires Python 3.10+)
uv run poe setup
```

### 2. Development Workflow

```bash
# Fast development checks
uv run poe dev              # Format, typecheck, test (~15s)

# Pre-commit checks
uv run poe check            # Format, lint-core, typecheck, test (~30s)

# Run tests
uv run poe test             # Unit tests only
uv run pytest               # Unit tests plus skipped live integration tests
```

### 3. Make Changes

- Follow existing patterns in the codebase
- Add tests for new functionality
- Update documentation
- Run `uv run poe check` before committing

### 4. Submit

```bash
# Final checks
uv run poe check

# Commit and push
git add .
git commit -m "Descriptive message"
git push origin your-branch
```

Then create a pull request on GitHub.

---

## Available Commands

All development commands are defined in `pyproject.toml` under `[tool.poe.tasks]`. Key commands:

- `uv run poe dev` - Fast development checks
- `uv run poe check` - Pre-commit checks
- `uv run poe test` - Run all tests

See `pyproject.toml` for the complete list of available tasks.

---

## Code Standards

### Type Safety
- **100% mypy strict** compliance required
- All public APIs must have type hints
- No `Any` types unless absolutely necessary

### Financial Precision
**Critical**: Always use `Decimal` for money, never `float`:

```python
from decimal import Decimal

# ✓ Good
price = Decimal("1.25435")
units = Decimal("1000")
value = price * units

# ✗ Bad - precision loss (commented out to avoid validator errors)
# price_float = 1.25435  # float
# value = price_float * 1000  # precision lost
```

---

## Testing

### Unit Tests

```bash
# Run unit tests
uv run poe test

# Specific test
uv run pytest tests/unit/test_client.py::test_name
```

Unit tests mock HTTP responses and test logic in isolation.

### Integration Tests

```bash
# Run integration tests (requires credentials)
uv run poe test-integration

# Set up .env file
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-practice-account
```

**Always use practice accounts**, never live trading accounts.

---

## Documentation

All public methods need comprehensive docstrings:

```python
from typing import Any
from fivetwenty.endpoints.orders import OrderResponse


async def post_market_order(
    self: Any,  # noqa: ARG001
    account_id: str,  # noqa: ARG001
    instrument: str,  # noqa: ARG001
    units: int,  # noqa: ARG001
) -> OrderResponse:
    """Create a market order for immediate execution.

    Args:
        self: The endpoint instance
        account_id: OANDA account identifier
        instrument: Trading instrument (e.g., "EUR_USD")
        units: Order size (positive=buy, negative=sell)

    Returns:
        OrderResponse with order details and transactions

    Raises:
        FiveTwentyError: If order creation fails
        ValidationError: If parameters are invalid
    """
    # Implementation would go here
    return {"lastTransactionID": "123"}  # type: ignore[return-value]
```

### Documentation Types

- **[Tutorials](../tutorials/)** - Step-by-step learning
- **[Guides](../guides/)** - Comprehensive guidance
- **[API Reference](../api-reference/)** - Complete specifications
- **[Examples](../examples/)** - Working code samples

---

## Pull Request Guidelines

### Before Submitting

1. ✓ All tests pass (`uv run poe test`)
2. ✓ Quality checks pass (`uv run poe check`)
3. ✓ Documentation updated
4. ✓ Tests added for new features

### PR Content

- **Clear description** - What changed and why
- **Test coverage** - Tests for new functionality
- **Documentation** - Updated relevant docs
- **Small scope** - Focused changes, one feature/fix per PR

### Review Criteria

- Correctness and functionality
- Test coverage
- Documentation completeness
- Performance implications
- Security (credential handling)
- Code consistency

---

## Getting Help

### Resources

- **[Development Setup](development-setup.md)** - Environment setup guide
- **[Testing Guide](testing-guide.md)** - Testing best practices
- **[Code Style](code-style.md)** - Code patterns and standards
- **[GitHub Discussions](https://github.com/NimbleOx/fivetwenty/discussions)** - Ask questions
- **[GitHub Issues](https://github.com/NimbleOx/fivetwenty/issues)** - Bug reports

### When Asking for Help

- Check existing issues/discussions first
- Provide minimal reproducible example
- Include environment details (Python version, OS)
- For API questions, specify account type (practice/live)

### Security Issues

Report security vulnerabilities privately via [GitHub Security Advisories](https://github.com/NimbleOx/fivetwenty/security/advisories).

---

**Thank you for helping make FiveTwenty better!**
