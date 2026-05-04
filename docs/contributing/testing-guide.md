# Testing Guide

Comprehensive testing ensures FiveTwenty's reliability for production trading.

---

## Running Tests

```bash
# Default local run (unit tests plus skipped live integration tests)
uv run pytest

# Unit tests (fast)
uv run poe test

# Live integration tests (requires OANDA practice credentials)
uv run poe test-integration

# With coverage
uv run pytest --cov=fivetwenty --cov-report=html

# Specific test
uv run pytest tests/unit/test_client.py::test_name

# By marker
uv run pytest -m unit
uv run pytest -m integration --run-integration-live
```

---

## Test Structure

```text
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Fast, mocked
│   ├── test_client.py
│   └── endpoints/
└── integration/          # Real API
    └── test_accounts_integration.py
```

---

## Unit Testing

Fast, isolated tests with mocked HTTP:

```python
from decimal import Decimal
from unittest.mock import patch
import pytest
from fivetwenty import AsyncClient, Environment


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_account() -> None:
    client = AsyncClient(token="test", account_id="123", environment=Environment.PRACTICE)

    with patch.object(client, '_request') as mock_request:
        mock_request.return_value.json.return_value = {
            "account": {"id": "123", "balance": "10000.0000"},
            "lastTransactionID": "456"
        }

        result = await client.accounts.get_account("123")

        assert result["account"].id == "123"  # noqa: S101
        assert result["account"].balance == Decimal("10000.0000")  # noqa: S101
```

---

## Integration Testing

Tests against real OANDA API (practice only):

```bash
# Setup .env
export FIVETWENTY_OANDA_TOKEN="your-practice-token"
export FIVETWENTY_OANDA_ACCOUNT="your-practice-account"

# Run explicitly; live integration tests are skipped without this opt-in flag.
uv run pytest tests/integration/ --run-integration-live
```

```python
import os
from decimal import Decimal
import pytest
from fivetwenty import AsyncClient, Environment


@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api() -> None:
    client = AsyncClient(
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],
        account_id=os.environ["FIVETWENTY_OANDA_ACCOUNT"],
        environment=Environment.PRACTICE
    )

    async with client:
        response = await client.accounts.get_account_summary(
            os.environ["FIVETWENTY_OANDA_ACCOUNT"]
        )
        assert isinstance(response["account"].balance, Decimal)  # noqa: S101
```

**Always use practice accounts**, never live trading accounts. Set `SKIP_INTEGRATION=1` to force integration tests to skip even when a live integration command is used.

---

## Common Fixtures

```python
# conftest.py
import pytest
from fivetwenty import AsyncClient, Environment


@pytest.fixture
def test_client() -> AsyncClient:
    return AsyncClient(
        token="test-token",
        account_id="123",
        environment=Environment.PRACTICE
    )
```

---

## Best Practices

**Unit Tests:**
- Mock all HTTP calls
- Test success and error paths
- Use `Decimal` for financial assertions

**Integration Tests:**
- Practice accounts only
- Test real error conditions

**General:**
- One focus per test
- Descriptive test names
- Keep tests independent

---

## Coverage

```bash
# Generate report
uv run pytest --cov=fivetwenty --cov-report=html
open htmlcov/index.html

# Goals
# Overall: 80%+
# Core modules: 90%+
# Critical paths (orders/trades): 100%
```

---

## Before Committing

```bash
uv run poe test              # All tests pass
uv run poe check             # Quality checks pass
```
