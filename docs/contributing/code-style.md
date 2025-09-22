# Code Style and Patterns

FiveTwenty follows strict code quality standards to ensure maintainability, security, and performance. This guide outlines our coding conventions and patterns.

---

## Code Quality Standards

### **Type Safety - 100% MyPy Strict Compliance**

All code must pass mypy strict mode with no errors:

```python
# ✅ Good - Full type annotations
async def create_order(
    self,
    account_id: str,
    order: OrderRequest,
    *,
    timeout: Optional[float] = None
) -> OrderResponse:
    """Create an order with proper typing."""
    pass

# ❌ Bad - Missing type annotations
async def create_order(self, account_id, order, timeout=None):
    pass
```

### **Financial Precision - Decimal Only**

**Critical**: Always use `Decimal` for financial calculations:

```python
from decimal import Decimal
from typing import Union

# ✅ Good - Decimal for financial values
def calculate_position_value(
    units: int,
    price: Decimal
) -> Decimal:
    return Decimal(str(units)) * price

# ❌ Bad - Float causes precision errors
def calculate_position_value(units: int, price: float) -> float:
    return units * price  # Precision loss!

# ✅ Good - Accept Decimal or convert from string/int
def parse_price(value: Union[str, int, Decimal]) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))
```

### **Error Handling - Structured Exceptions**

Use FiveTwenty's exception hierarchy:

```python
from fivetwenty.exceptions import FiveTwentyError, StreamStall

# ✅ Good - Specific exception types
async def get_account(self, account_id: str) -> AccountSummary:
    try:
        response = await self._request("GET", f"/accounts/{account_id}")
        return AccountSummary.model_validate(response.json())
    except httpx.HTTPError as e:
        raise FiveTwentyError(
            message=f"Failed to get account {account_id}",
            response=e.response if hasattr(e, 'response') else None
        ) from e

# ❌ Bad - Generic exceptions
async def get_account(self, account_id: str) -> AccountSummary:
    response = await self._request("GET", f"/accounts/{account_id}")
    return AccountSummary.model_validate(response.json())  # May raise various exceptions
```

---

## Architecture Patterns

### **Async-First Design**

async client is the primary interface, Client is a sync wrapper:

```python
# ✅ Good - async client method
class AccountsEndpoint:
    async def get_summary(
        self,
        account_id: str,
        *,
        timeout: Optional[float] = None
    ) -> AccountSummary:
        """Get account summary (async method)."""
        response = await self._client._request(
            "GET",
            f"/accounts/{account_id}",
            timeout=timeout
        )
        return AccountSummary.model_validate(response.json())

# ✅ Good - Sync wrapper delegates to async
class SyncAccountsEndpoint:
    def get_summary(
        self,
        account_id: str,
        *,
        timeout: Optional[float] = None
    ) -> AccountSummary:
        """Get account summary (sync wrapper)."""
        return self._client._run_async(
            self._async_endpoint.get_summary(account_id, timeout=timeout)
        )
```

### **Endpoint Organization**

Group related methods into endpoint classes:

```python
# ✅ Good - Organized by OANDA API endpoints
class OrdersEndpoint:
    """Order management operations."""

    async def list_orders(self, account_id: str) -> list[Order]:
        """List pending orders."""
        pass

    async def create_order(self, account_id: str, order: OrderRequest) -> OrderResponse:
        """Create new order."""
        pass

    async def get_order(self, account_id: str, order_id: str) -> Order:
        """Get specific order."""
        pass

# Attach to client
class AsyncClient:
    def __init__(self):
        self.orders = OrdersEndpoint(self)
        self.accounts = AccountsEndpoint(self)
        self.trades = TradesEndpoint(self)
```

### **Model Validation**

Use Pydantic models for all API data:

```python
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

# ✅ Good - Complete Pydantic model
class Order(BaseModel):
    """Represents an OANDA order."""

    id: str = Field(alias="id", description="Order ID")
    instrument: str = Field(alias="instrument", description="Trading instrument")
    units: int = Field(alias="units", description="Order size")
    price: Optional[Decimal] = Field(alias="price", description="Order price")
    time_in_force: str = Field(alias="timeInForce", description="Time in force")
    create_time: datetime = Field(alias="createTime", description="Creation time")

    class Config:
        # Allow field aliases for OANDA API compatibility
        populate_by_name = True
        # Use enum values in serialization
        use_enum_values = True

# ✅ Good - Model usage with validation
def parse_order_response(data: dict) -> Order:
    return Order.model_validate(data)
```

---

## Naming Conventions

### **Methods and Functions**

```python
# ✅ Good - Clear, descriptive names
async def get_accounts(self, account_id: str) -> AccountSummary:
    pass

async def post_market_order(
    self,
    account_id: str,
    instrument: str,
    units: int
) -> OrderResponse:
    pass

async def stream_pricing(
    self,
    account_id: str,
    instruments: list[str]
) -> AsyncIterator[Price]:
    pass

# ❌ Bad - Unclear abbreviations
async def get_acct(self, id: str) -> AccountSummary:
    pass

async def mk_ord(self, acct: str, instr: str, u: int) -> OrderResponse:
    pass
```

### **Variables and Parameters**

```python
# ✅ Good - Full words, clear purpose
account_id: str
instrument_name: str
order_request: OrderRequest
timeout_seconds: float
client_request_id: Optional[str]

# ❌ Bad - Cryptic abbreviations
acct_id: str
instr: str
req: OrderRequest
timeout: float  # Ambiguous units
req_id: Optional[str]
```

### **Model Classes**

```python
# ✅ Good - Descriptive, matches OANDA terminology
class AccountSummary(BaseModel):
    pass

class MarketOrderRequest(BaseModel):
    pass

class PricingHeartbeat(BaseModel):
    pass

# ❌ Bad - Generic or unclear names
class Account(BaseModel):  # Too generic - summary? details?
    pass

class Request(BaseModel):  # What kind of request?
    pass
```

---

## Documentation Patterns

### **Method Documentation**

All public methods require comprehensive docstrings:

```python
from decimal import Decimal
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def post_limit_order(
    self,
    account_id: str,
    instrument: str,
    units: int,
    price: Decimal,
    *,
    time_in_force: str = "GTC",
    client_request_id: Optional[str] = None,
    timeout: Optional[float] = None,
) -> OrderResponse:
    """Create a limit order for execution at a specific price.

    Args:
        account_id: OANDA account identifier
        instrument: Trading instrument (e.g., "EUR_USD", "GBP_JPY")
        units: Order size (positive for buy, negative for sell)
        price: Limit price for order execution
        time_in_force: Order duration ("GTC", "IOC", "FOK", "GTD")
        client_request_id: Optional client-provided request identifier
        timeout: Request timeout in seconds

    Returns:
        OrderResponse containing order details, fill information, and related transactions

    Raises:
        FiveTwentyError: If order creation fails due to API error
        ValidationError: If parameters are invalid or missing
        TimeoutError: If request exceeds specified timeout

    Example:
        Create a limit buy order for EUR/USD:

        >>> response = await client.orders.post_limit_order(
        ...     account_id="123-456-789",
        ...     instrument="EUR_USD",
        ...     units=1000,
        ...     price=Decimal("1.2500")
        ... )
        >>> print(f"Order ID: {response.order_create_transaction.id}")

    Note:
        - Limit orders may not fill immediately if price is not available
        - Use positive units for buy orders, negative for sell orders
        - Price precision depends on instrument (typically 4-5 decimal places)
    """
```

### **Model Documentation**

```python
class Position(BaseModel):
    """Represents a trading position for a specific instrument.

    A position aggregates all trades for an instrument into long and short sides,
    showing net exposure, unrealized P&L, and margin requirements.

    Attributes:
        instrument: Trading instrument (e.g., "EUR_USD")
        long: Long side position details (aggregated long trades)
        short: Short side position details (aggregated short trades)
        pl: Total realized profit/loss for the position
        unrealized_pl: Current unrealized profit/loss
        margin_used: Margin currently required for this position
    """

    instrument: str = Field(description="Position's trading instrument")
    long: PositionSide = Field(description="Long side aggregation")
    short: PositionSide = Field(description="Short side aggregation")
    pl: Decimal = Field(description="Realized profit/loss")
    unrealized_pl: Decimal = Field(alias="unrealizedPL", description="Unrealized P&L")
    margin_used: Decimal = Field(alias="marginUsed", description="Required margin")
```

---

## Error Handling Patterns

### **Exception Hierarchy Usage**

```python
from fivetwenty.exceptions import FiveTwentyError, StreamStall

# ✅ Good - Appropriate exception types
async def get_pricing(self, account_id: str, instruments: list[str]) -> list[Price]:
    """Get current pricing with proper error handling."""
    try:
        response = await self._request("GET", "/pricing", params={
            "accountID": account_id,
            "instruments": ",".join(instruments)
        })

        pricing_data = response.json()
        return [Price.model_validate(price) for price in pricing_data["prices"]]

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise FiveTwentyError(
                message=f"Account {account_id} not found",
                error_code="ACCOUNT_NOT_EXIST",
                response=e.response
            ) from e
        elif e.response.status_code == 400:
            raise FiveTwentyError(
                message="Invalid instruments specified",
                error_code="INVALID_INSTRUMENTS",
                response=e.response
            ) from e
        else:
            raise FiveTwentyError(
                message=f"Pricing request failed: {e.response.status_code}",
                response=e.response
            ) from e

    except httpx.TimeoutException as e:
        raise FiveTwentyError(
            message="Pricing request timed out",
            error_code="REQUEST_TIMEOUT"
        ) from e

# ✅ Good - Streaming-specific error handling
async def stream_pricing(
    self,
    account_id: str,
    instruments: list[str]
) -> AsyncIterator[Union[Price, PricingHeartbeat]]:
    """Stream pricing with reconnection logic."""
    last_heartbeat = time.monotonic()

    async for line in self._stream_lines(url, headers):
        if not line.strip():
            continue

        # Check for stall condition
        if time.monotonic() - last_heartbeat > HEARTBEAT_TIMEOUT:
            raise StreamStall(
                message="Pricing stream stalled - no heartbeat received",
                last_heartbeat_time=datetime.fromtimestamp(last_heartbeat)
            )

        try:
            data = json.loads(line)
            if data["type"] == "PRICE":
                yield Price.model_validate(data)
            elif data["type"] == "HEARTBEAT":
                last_heartbeat = time.monotonic()
                yield PricingHeartbeat.model_validate(data)

        except (json.JSONDecodeError, KeyError, ValidationError) as e:
            # Log but don't crash stream for individual parsing errors
            logger.warning(f"Failed to parse streaming data: {e}")
            continue
```

### **Validation Patterns**

```python
from pydantic import ValidationError

# ✅ Good - Validate inputs early
def create_order_request(
    instrument: str,
    units: int,
    order_type: str,
    **kwargs
) -> OrderRequest:
    """Create validated order request."""

    # Validate instrument format
    if not re.match(r'^[A-Z]{3}_[A-Z]{3}$', instrument):
        raise ValueError(f"Invalid instrument format: {instrument}")

    # Validate units
    if units == 0:
        raise ValueError("Order units cannot be zero")

    if abs(units) > 100_000_000:
        raise ValueError(f"Order size too large: {abs(units)}")

    # Build request data
    request_data = {
        "instrument": instrument,
        "units": str(units),
        "type": order_type.upper(),
        **kwargs
    }

    try:
        return OrderRequest.model_validate(request_data)
    except ValidationError as e:
        raise ValueError(f"Invalid order parameters: {e}") from e
```

---

## Testing Patterns

### **Unit Test Structure**

```python
from decimal import Decimal

import pytest
from unittest.mock import AsyncMock, Mock, patch
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

class TestAccountsEndpoint:
    """Test suite for accounts endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client with mocked HTTP."""
        return AsyncClient(token="test-token", environment="practice")

    @pytest.mark.asyncio
    async def test_get_accounts_success(self, client):
        """Test successful account summary retrieval."""
        # Arrange
        expected_response = {
            "account": {
                "id": "123-456-789",
                "currency": "USD",
                "balance": "10000.00"
            }
        }

        with patch.object(client, '_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = expected_response
            mock_request.return_value = mock_response

            # Act
            result = await client.accounts.get_accounts("123-456-789")

            # Assert
            assert result.id == "123-456-789"
            assert result.currency == "USD"
            assert result.balance == Decimal("10000.00")
            mock_request.assert_called_once_with("GET", "/accounts/123-456-789")

    @pytest.mark.asyncio
    async def test_get_accounts_not_found(self, client):
        """Test account not found error handling."""
        with patch.object(client, '_request') as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError(
                message="Not Found",
                request=Mock(),
                response=Mock(status_code=404)
            )

            with pytest.raises(FiveTwentyError) as exc_info:
                await client.accounts.get_accounts("invalid-id")

            assert "Account invalid-id not found" in str(exc_info.value)
            assert exc_info.value.error_code == "ACCOUNT_NOT_EXIST"
```

### **Integration Test Patterns**

```python
from decimal import Decimal

import pytest
import os
from fivetwenty import AsyncClient, Environment

@pytest.mark.integration
class TestAccountsIntegration:
    """Integration tests for accounts endpoint."""

    @pytest.fixture
    def client(self):
        """Create client with real credentials."""
        return AsyncClient(
            token=os.environ["TEST_OANDA_TOKEN"],
            environment=Environment.PRACTICE  # Always practice for tests
        )

    @pytest.mark.asyncio
    async def test_get_accounts_real_api(self, client, vcr):
        """Test against real OANDA API (recorded with VCR)."""
        account_id = os.environ["TEST_OANDA_ACCOUNT"]

        async with client:
            summary = await client.accounts.get_accounts(account_id)

            # Verify response structure
            assert summary.id == account_id
            assert isinstance(summary.balance, Decimal)
            assert summary.currency in ["USD", "EUR", "GBP", "JPY"]
            assert summary.margin_available >= Decimal("0")
```

---

## Performance Patterns

### **Async Best Practices**

```python
from fivetwenty import AsyncClient, Environment

import asyncio
from contextlib import asynccontextmanager

# ✅ Good - Proper async context management
@asynccontextmanager
async def trading_session(config: AccountConfig):
    """Managed trading session with proper cleanup."""
    client = AsyncClient(config=config)
    try:
        await client.__aenter__()
        yield client
    finally:
        await client.__aexit__(None, None, None)

# ✅ Good - Concurrent operations
async def get_multiple_accounts(
    client: AsyncClient,
    account_ids: list[str]
) -> list[AccountSummary]:
    """Fetch multiple accounts concurrently."""

    tasks = [
        client.accounts.get_accounts(account_id)
        for account_id in account_ids
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    summaries = []
    for result in results:
        if isinstance(result, Exception):
            logger.warning(f"Failed to get account: {result}")
        else:
            summaries.append(result)

    return summaries
```

### **Memory Management**

```python
# ✅ Good - Streaming with backpressure
async def process_price_stream(
    client: AsyncClient,
    account_id: str,
    instruments: list[str],
    max_buffer_size: int = 1000
) -> None:
    """Process price stream with memory management."""

    buffer: list[Price] = []

    async for price in client.pricing.stream_pricing(account_id, instruments):
        if isinstance(price, PricingHeartbeat):
            continue  # Skip heartbeats

        buffer.append(price)

        # Process buffer when full
        if len(buffer) >= max_buffer_size:
            await process_price_batch(buffer)
            buffer.clear()  # Clear to prevent memory growth

    # Process remaining prices
    if buffer:
        await process_price_batch(buffer)

async def process_price_batch(prices: list[Price]) -> None:
    """Process batch of prices efficiently."""
    # Batch processing logic here
    pass
```

---

## Security Patterns

### **Credential Handling**

```python
from pydantic import SecretStr

# ✅ Good - Secure credential handling
class AccountConfig(BaseModel):
    """Secure account configuration."""

    token: SecretStr  # Never logged or printed
    account_id: SecretStr
    environment: Environment
    alias: str

    def summary(self) -> str:
        """Safe representation for logging."""
        return f"{self.alias} ({self.environment.value})"

    def __str__(self) -> str:
        """Never expose secrets in string representation."""
        return self.summary()

    def __repr__(self) -> str:
        """Never expose secrets in repr."""
        return (
            f"AccountConfig("
            f"alias={self.alias!r}, "
            f"environment={self.environment.value}, "
            f"token=SecretStr('***'), "
            f"account_id=SecretStr('***')"
            f")"
        )

# ✅ Good - Safe logging practices
def log_trade_result(trade: Trade, config: AccountConfig) -> None:
    """Log trade result safely."""
    logger.info(
        f"Trade executed: {trade.instrument} "
        f"{trade.units} units at {trade.price} "
        f"(account: {config.summary()})"  # Safe summary only
    )

# ❌ Bad - Exposes credentials
def bad_logging(trade: Trade, config: AccountConfig) -> None:
    logger.info(f"Trade: {trade} Config: {config}")  # May expose secrets!
```

---

This comprehensive code style guide ensures consistency, security, and maintainability across the FiveTwenty codebase. Follow these patterns when contributing to maintain the project's high quality standards.