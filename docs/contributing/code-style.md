# Code Style and Patterns

FiveTwenty follows strict code quality standards to ensure maintainability, security, and performance.

---

## Core Standards

### Type Safety - 100% MyPy Strict

All code must pass `mypy --strict` with zero errors:

```python
# ✓ Good - Full type annotations
async def create_order(
    self,
    account_id: str,
    order: OrderRequest,
    *,
    timeout: float | None = None,
) -> OrderResponse:
    """Create an order with proper typing."""
    ...
```

### Financial Precision - Decimal Only

**Critical**: Always use `Decimal` for money:

```python
from decimal import Decimal

# ✓ Good
def calculate_value(units: int, price: Decimal) -> Decimal:
    return Decimal(str(units)) * price

# ✗ Bad - Float causes precision loss
def bad_calc(units: int, price: Decimal) -> Decimal:
    return units * price  # Precision loss!
```

### Error Handling

Use structured exceptions with proper context:

```python
from typing import Any
import httpx
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import AccountSummary


async def get_account_example(self: Any, account_id: str) -> AccountSummary:
    """Show proper error handling pattern."""
    try:
        response = await self._request("GET", f"/accounts/{account_id}")
        return AccountSummary.model_validate(response.json())
    except httpx.HTTPError as e:
        raise FiveTwentyError(
            status=e.response.status_code if hasattr(e, "response") else 500,
            message=f"Failed to get account {account_id}",
            response=e.response if hasattr(e, "response") else None,
        ) from e
```

---

## Architecture

### Async-First Design

- **AsyncClient** is primary interface
- **Client** is sync wrapper using `asyncio.run()`
- All endpoint methods are async first, wrapped for sync

### Endpoint Organization

Group methods by OANDA API sections:

```python
class OrdersEndpoint:
    """Order management operations."""

    async def list_orders(self, account_id: str) -> list[Order]: ...
    async def create_order(self, account_id: str, order: OrderRequest) -> OrderResponse: ...
    async def get_order(self, account_id: str, order_id: str) -> Order: ...
```

### Model Validation

Use Pydantic models for all API data:

```python
from decimal import Decimal
from pydantic import BaseModel, Field


class Order(BaseModel):
    id: str = Field(alias="id")
    instrument: str = Field(alias="instrument")
    units: int = Field(alias="units")
    price: Decimal | None = Field(alias="price")

    class Config:
        populate_by_name = True
        use_enum_values = True
```

---

## Naming Conventions

### Methods
- Use full words: `get_accounts()`, `post_market_order()`, `stream_pricing()`
- Avoid abbreviations: ~~`get_acct()`~~, ~~`mk_ord()`~~

### Variables
```python
# ✓ Good
account_id: str
instrument_name: str
timeout_seconds: float

# ✗ Bad
acct_id: str
instr: str
timeout: float  # Ambiguous units
```

### Models
- Descriptive names matching OANDA terminology in the v20 API
- `AccountSummary`, `MarketOrderRequest`, `PricingHeartbeat`
- Avoid generic names: ~~`Account`~~, ~~`Request`~~

---

## Documentation

All public methods require comprehensive docstrings:

```python
async def post_limit_order(
    self,
    account_id: str,
    instrument: str,
    units: int,
    price: Decimal,
) -> OrderResponse:
    """Create a limit order for execution at a specific price.

    Args:
        account_id: OANDA account identifier
        instrument: Trading instrument (e.g., "EUR_USD")
        units: Order size (positive=buy, negative=sell)
        price: Limit price for order execution

    Returns:
        OrderResponse with order details and transactions

    Raises:
        FiveTwentyError: If order creation fails
        ValidationError: If parameters are invalid
    """
    ...
```

---

## Testing

### Unit Tests

```python
import pytest
from unittest.mock import patch
from fivetwenty import AsyncClient


@pytest.mark.asyncio
async def test_get_account_success(client: AsyncClient) -> None:
    """Test successful account retrieval."""
    with patch.object(client, "_request") as mock:
        mock.return_value.json.return_value = {"account": {"id": "123"}, "lastTransactionID": "456"}
        result = await client.accounts.get_account("123")
        assert result["account"].id == "123"  # noqa: S101
```

### Integration Tests

```python
from decimal import Decimal
import pytest
from fivetwenty import AsyncClient


@pytest.mark.integration
async def test_real_api(client: AsyncClient, account_id: str) -> None:
    """Test against real OANDA API (practice account)."""
    async with client:
        response = await client.accounts.get_account_summary(account_id)
        assert isinstance(response["account"].balance, Decimal)  # noqa: S101
```

---

## Performance

### Async Patterns

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models import AccountSummary


# ✓ Good - Concurrent operations
async def get_multiple(client: AsyncClient, account_ids: list[str]) -> list[AccountSummary]:
    tasks = [client.accounts.get_account_summary(acc_id) for acc_id in account_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    # Filter out exceptions and extract account summaries
    return [
        result["account"]  # type: ignore[index]
        for result in results
        if not isinstance(result, BaseException)
    ]
```

### Memory Management

```python
from typing import Any
from fivetwenty import AsyncClient


async def process_batch(buffer: list[Any]) -> None:
    """Process a batch of prices."""
    pass  # Implementation here


# ✓ Good - Streaming with buffer limits
async def process_stream(client: AsyncClient, account_id: str, max_buffer: int = 1000) -> None:
    buffer: list[Any] = []
    async for price in client.pricing.get_pricing_stream(account_id, instruments=["EUR_USD"]):
        buffer.append(price)
        if len(buffer) >= max_buffer:
            await process_batch(buffer)
            buffer.clear()
```

---

## Security

### Credential Handling

Always use `SecretStr` for sensitive data:

```python
from pydantic import SecretStr

class AccountConfig(BaseModel):
    token: SecretStr  # Never logged
    account_id: SecretStr

    def summary(self) -> str:
        return f"{self.alias} ({self.environment.value})"

    def __repr__(self) -> str:
        return f"AccountConfig(token=SecretStr('***'), ...)"

# ✓ Good - Safe logging
logger.info(f"Trade executed (account: {config.summary()})")

# ✗ Bad - May expose secrets
logger.info(f"Config: {config}")
```

---

## Conclusion

These standards ensure FiveTwenty remains reliable and maintainable for production trading. Before submitting a pull request:

1. Run `poe quality` - All checks must pass
2. Run `poe test` - 100% test success required
3. Review this guide - Your code should match these patterns

When in doubt, look at existing code in `fivetwenty/` for reference patterns. Consistency matters more than perfection.

**Questions?** Open a [GitHub Discussion](https://github.com/NimbleOx/fivetwenty/discussions) - we're here to help!
