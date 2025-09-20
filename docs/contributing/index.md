# Contributing to FiveTwenty

Thank you for considering contributing to FiveTwenty! This guide will help you get started with contributing to our modern OANDA v20 API Python SDK.

---

## Quick Start for Contributors

### 1. **Set Up Development Environment**

```bash
# Clone the repository
git clone https://github.com/NimbleOx/fivetwenty.git
cd fivetwenty

# Set up development environment (requires Python 3.10+)
uv run poe setup
```

### 2. **Run Development Workflow**

```bash
# Fast development checks (recommended during development)
uv run poe dev

# Full quality checks (recommended before committing)
uv run poe check

# Run tests
uv run poe test
```

### 3. **Make Your Changes**

- Follow existing code patterns and conventions
- Add tests for new functionality
- Update documentation as needed
- Run quality checks frequently

### 4. **Submit Your Contribution**

```bash
# Run final checks
uv run poe check

# Commit your changes
git add .
git commit -m "Your descriptive commit message"

# Push and create pull request
git push origin your-feature-branch
```

---

## Contribution Areas

### **Core SDK Development**
- **Endpoints** - Add new OANDA API endpoints or improve existing ones
- **Models** - Enhance Pydantic models for API responses
- **Client** - Improve AsyncClient and Client functionality
- **Streaming** - Enhance real-time data streaming capabilities

### **Quality & Testing**
- **Unit tests** - Test individual components and functions
- **Integration tests** - Test against live OANDA API (requires credentials)
- **Error handling** - Improve exception handling and recovery
- **Performance** - Optimize for speed and memory usage

### **Documentation**
- **API reference** - Complete method and model documentation
- **Tutorials** - Step-by-step learning guides
- **How-to guides** - Practical problem-solving guides
- **Examples** - Real-world usage examples and notebooks

### **Developer Experience**
- **Type safety** - Improve type hints and mypy compliance
- **Error messages** - Make error messages more helpful
- **Configuration** - Simplify setup and configuration
- **Tooling** - Improve development and testing tools

---

## Development Workflow

### **Project Commands**

FiveTwenty uses **poethepoet (poe)** for development workflows:

```bash
# Quality checks (recommended workflow)
uv run poe dev      # Fast development checks (format, typecheck, test)
uv run poe check    # Full checks (format, lint-core, typecheck, test)
uv run poe quality  # Code quality only (format, lint, typecheck)

# Testing
uv run poe test           # Run all tests
uv run poe test-unit      # Unit tests only
uv run poe test-integration  # Integration tests only
uv run poe test-cov       # Tests with coverage report

# Code quality
uv run poe format     # Format code with ruff
uv run poe lint       # Lint with ruff
uv run poe typecheck  # Type check with mypy

# Documentation
uv run poe docs-serve   # Serve documentation locally
uv run poe docs-build   # Build documentation
uv run poe markdown-check  # Check markdown formatting

# Setup and maintenance
uv run poe setup      # Initial setup for new contributors
uv run poe clean      # Clean build artifacts and caches
```

### **Code Standards**

- **Type Safety**: 100% mypy strict compliance required
- **Code Quality**: ruff formatting and linting (automatically fixed)
- **Testing**: Comprehensive unit and integration test coverage
- **Documentation**: All public APIs must be documented

### **Financial Precision**

**Critical**: Always use `Decimal` for financial calculations, never `float`:

```python
# ✅ Correct
from decimal import Decimal
price = Decimal("1.25435")
units = Decimal("1000")
value = price * units

# ❌ Wrong - will cause precision errors
price=Decimal("1.25435")  # float
value = price * 1000  # precision loss
```

---

## Testing Guidelines

### **Unit Tests**

Unit tests mock HTTP responses and test component logic:

```bash
# Run unit tests
uv run poe test-unit

# Run specific test file
uv run pytest tests/unit/test_client.py

# Run specific test
uv run pytest tests/unit/test_client.py::test_client_init
```

### **Integration Tests**

Integration tests use VCR.py for recorded API interactions:

```bash
# Run integration tests (requires OANDA credentials)
uv run poe test-integration

# Set up test credentials in .env
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-practice-account
FIVETWENTY_OANDA_ENVIRONMENT=practice
FIVETWENTY_OANDA_ACCOUNT_ALIAS=test_account
```

**Important**: Integration tests should only use **practice** accounts, never live trading accounts.

### **Test Organization**

```
tests/
├── unit/                 # Fast, isolated tests
│   ├── test_client.py
│   ├── test_models.py
│   └── endpoints/
├── integration/          # Tests against OANDA API
│   ├── test_accounts.py
│   ├── test_orders.py
│   └── fixtures/         # VCR cassettes
└── conftest.py          # Shared test configuration
```

---

## Documentation Standards

### **API Documentation**

All public methods require comprehensive documentation:

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def post_market_order(
    self,
    account_id: str,
    instrument: InstrumentName,
    units: int,
    *,
    client_request_id: Optional[str] = None,
    timeout: Optional[float] = None,
) -> OrderResponse:
    """Create a market order for immediate execution.

    Args:
        account_id: OANDA account identifier
        instrument: Trading instrument (e.g., "EUR_USD")
        units: Order size (positive=buy, negative=sell)
        client_request_id: Optional request tracking ID
        timeout: Request timeout in seconds

    Returns:
        OrderResponse containing order details and transaction info

    Raises:
        FiveTwentyError: If order creation fails
        ValidationError: If parameters are invalid

    Example:
        >>> response = await client.orders.post_market_order(
        ...     account_id="123-456-789",
        ...     instrument="EUR_USD",
        ...     units=1000
        ... )
        >>> print(f"Order ID: {response.order.id}")
    """
```

### **Documentation Types**

Following the [Diátaxis framework](https://diataxis.fr/):

- **Tutorials** - Learning-oriented, step-by-step guides
- **How-to Guides** - Problem-oriented, practical solutions
- **API Reference** - Information-oriented, comprehensive specifications
- **Explanations** - Understanding-oriented, background knowledge

---

## Code Review Process

### **Pull Request Guidelines**

1. **Clear description** - Explain what changes and why
2. **Test coverage** - Include tests for new functionality
3. **Documentation updates** - Update relevant docs
4. **Quality checks pass** - Ensure `uv run poe check` succeeds

### **Review Criteria**

- **Correctness** - Does the code work as intended?
- **Test coverage** - Are changes adequately tested?
- **Documentation** - Are public APIs documented?
- **Performance** - Are there performance implications?
- **Security** - Does code handle secrets safely?
- **Consistency** - Does code follow existing patterns?

### **Feedback Process**

- Reviewers focus on code quality and design
- Contributors are encouraged to ask questions
- Multiple small PRs preferred over large ones
- Automated checks must pass before manual review

---

## Release Process

### **Version Strategy**

FiveTwenty follows semantic versioning (semver):

- **Major** (20.x.0) - Breaking API changes
- **Minor** (20.1.x) - New features, backward compatible
- **Patch** (20.1.0) - Bug fixes, backward compatible

### **Release Checklist**

1. All tests passing on main branch
2. Documentation updated and building
3. CHANGELOG.md updated with changes
4. Version bumped in pyproject.toml
5. Git tag created for release
6. PyPI package published
7. GitHub release with notes created

---

## Getting Help

### **Community Channels**

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and community support
- **Documentation** - Comprehensive guides and API reference

### **Development Questions**

- Check existing issues and discussions first
- Provide minimal reproducible examples
- Include environment details (Python version, OS)
- For API-related questions, include OANDA account type (practice/live)

### **Security Issues**

Report security vulnerabilities privately via GitHub Security Advisories or email.

---

## Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md** - All contributors listed
- **Release notes** - Major contributions highlighted
- **GitHub** - Contributor badges and statistics

Thank you for helping make FiveTwenty better! 🎉