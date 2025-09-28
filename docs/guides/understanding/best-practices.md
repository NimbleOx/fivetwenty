# FiveTwenty SDK Best Practices

Essential patterns and practices for building robust applications with the FiveTwenty SDK.

## Client Architecture Patterns

### Context Manager Usage

Always use context managers for proper resource cleanup:

<!-- fragment: client usage examples with placeholder values -->
```python
import os

from fivetwenty import AsyncClient, Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# AsyncClient
async def example_async():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Client automatically cleaned up on exit
        return await client.accounts.get_account(account_id)

# Sync Client
def example_sync():
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Background thread and queues automatically cleaned up
        return client.accounts.get_account(account_id)
```

### Connection Reuse

Reuse client instances across multiple operations:

<!-- fragment: connection reuse examples with placeholder values -->
```python
import os

from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# Good: Reuse client for multiple operations
async def good_example():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        account = await client.accounts.get_account(account_id)
        positions = await client.positions.get_positions(account_id)
        orders = await client.orders.get_orders(account_id)
        return account, positions, orders

# Bad: Create new client for each operation
async def get_account():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        return await client.accounts.get_account(account_id)
```

### Concurrent Operations

Use asyncio.gather() for concurrent API calls:

<!-- fragment: Demo concurrent operations with undefined imports and missing type annotations -->
```python
import asyncio
import os

from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def concurrent_example() -> None:
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Efficient: Concurrent requests
        account, positions, orders = await asyncio.gather(
            client.accounts.get_account(account_id),
            client.positions.get_positions(account_id),
            client.orders.get_orders(account_id)
        )

        # Inefficient: Sequential requests
        account = await client.accounts.get_account(account_id)
        positions = await client.positions.get_positions(account_id)
        orders = await client.orders.get_orders(account_id)

        return account, positions, orders
```

## Financial Precision

### Decimal Usage

Always use Decimal for financial calculations:

<!-- fragment: financial calculation examples with placeholder values -->
```python
from decimal import Decimal

# Example account balance (typically from OANDA API)
account_balance = Decimal("10000.00")

# Good: Exact precision
position_size = Decimal(10000)
risk_amount = account_balance * Decimal("0.02")  # 2% risk
stop_distance = Decimal("0.0050")  # 50 pips

# Bad: Floating point errors (commented out)
# position_size = 10000.0
# risk_amount = account_balance * Decimal("0.02")
# stop_distance = 0.0050
```

### Price Calculation Precision

Handle OANDA's price precision requirements:

```python
from decimal import Decimal

# OANDA price precision (5 decimal places for majors)
price = Decimal("1.08456").quantize(Decimal("0.00001"))

# Position sizing with exact arithmetic
def calculate_position_size(
    account_balance: str,  # AccountUnits from OANDA
    risk_percentage: Decimal,
    stop_loss_pips: int,
    pip_value: Decimal,
) -> Decimal:
    """Calculate position size with exact precision."""
    balance = Decimal(account_balance)
    risk_amount = balance * (risk_percentage / 100)
    risk_per_unit = stop_loss_pips * pip_value
    position_size = risk_amount / risk_per_unit
    return position_size.quantize(Decimal(1))  # Round to whole units
```

### Field Type Handling

FiveTwenty automatically converts between Decimal and string fields:

<!-- fragment: Demo order processing with union attribute issues and type mismatches -->
```python
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def example_order() -> tuple[object, object]:
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # SDK handles conversion automatically
        order = await client.orders.post_limit_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=Decimal(10000),  # Converted to string for API
            price=Decimal("1.0850")  # Converted to string for API
        )

        # Response fields are properly typed
        filled_price = Decimal(order.order_fill_transaction.price)  # string -> Decimal
        return order, filled_price
```

## Error Handling Patterns

### Exception Hierarchy

Use specific exception types for targeted handling:

<!-- fragment: Demo error handling with undefined exception imports and type issues -->
```python
import asyncio
import os
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def example_error_handling() -> None:
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except BadRequest as e:
            if "INSUFFICIENT_MARGIN" in str(e):
                # Reduce position size
                await handle_margin_error(e)
            elif "INVALID_INSTRUMENT" in str(e):
                # Skip this instrument
                return None
        except TooManyRequests as e:
            # Respect rate limits
            await asyncio.sleep(e.retry_after or 60)
        except InternalServerError:
            # OANDA server error - retry with backoff
            await retry_with_backoff()
        return order

async def handle_margin_error(error) -> None:
    """Handle margin errors."""
    pass

async def retry_with_backoff() -> None:
    """Retry with backoff."""
    pass
```

### Retry Patterns

Implement exponential backoff for retryable errors:

<!-- fragment: retry pattern implementation example -->
```python
import asyncio
import secrets
from collections.abc import Callable
from typing import Any

from fivetwenty.exceptions import InternalServerError, TooManyRequests

async def retry_with_backoff(
    operation: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0
) -> Any:
    """Retry operation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await operation()
        except (InternalServerError, TooManyRequests):
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt)
            # Use secrets module for cryptographically secure random
            jitter = secrets.randbelow(int(0.3 * delay * 1000)) / 1000
            await asyncio.sleep(delay + jitter)
    return None  # Explicit return for all code paths
```

## Streaming Best Practices

### Stream Resource Management

Properly handle streaming connections:

```python
import asyncio
from collections.abc import AsyncIterator
from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall

async def robust_price_stream(
    client: AsyncClient,
    account_id: str,
    instruments: list[str]
) -> AsyncIterator:
    """Streaming with proper error handling."""
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            async for price in client.pricing.get_pricing_stream(
                account_id=account_id,
                instruments=instruments
            ):
                # Reset retry count on successful data
                retry_count = 0
                yield price

        except StreamStall:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            await asyncio.sleep(2 ** retry_count)  # Exponential backoff
```

### Backpressure Management

Handle fast-moving data appropriately:

```python
import os
from fivetwenty import AsyncClient, Client, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def async_stream_example() -> None:
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # AsyncClient: Direct processing (no buffering)
        async for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Process immediately - don't block the stream
            await process_price_async(price)

def sync_stream_example() -> None:
    with Client(token=token, environment=Environment.PRACTICE) as client:
        # Sync Client: Bounded queues prevent memory issues
        for price in client.pricing.get_pricing_stream(
            account_id=account_id,
            instruments=["EUR_USD"]
        ):
            # Queue automatically manages backpressure
            process_price_sync(price)

async def process_price_async(price: object) -> None:
    """Process price data asynchronously."""
    pass

def process_price_sync(price: object) -> None:
    """Process price data synchronously."""
    pass
```

## Environment Management

### Environment-Specific Configuration

Use different settings for practice vs live:

```python
import os

from fivetwenty import AsyncClient, Environment

def get_token(is_live: bool) -> str:
    """Get appropriate token for environment."""
    if is_live:
        return os.environ["OANDA_LIVE_TOKEN"]
    return os.environ["OANDA_PRACTICE_TOKEN"]

def create_client(is_live: bool = False) -> AsyncClient:
    """Create client with environment-appropriate settings."""
    env = Environment.LIVE if is_live else Environment.PRACTICE
    timeout = 30.0 if is_live else 10.0  # Longer timeout for live

    return AsyncClient(
        token=get_token(is_live),
        environment=env,
        timeout=timeout
    )
```

### Token Security

Never hardcode tokens or log sensitive data:

```python
import os
import logging

logger = logging.getLogger(__name__)

# Good: Environment variables
token = os.environ["OANDA_TOKEN"]

# Good: Masked logging
logger.info(f"Using token: {token[:8]}...")

# Bad: Hardcoded token
token = "your-actual-token-here"

# Bad: Token in logs
logger.info(f"Token: {token}")
```

## Performance Optimization

### Instrument Selection

Only stream instruments you actively use:

```python
# Good: Specific instruments only
instruments = ["EUR_USD", "GBP_USD"]  # Only what you need

# Bad: Too many instruments - undefined variables example
# This would cause undefined variable errors:
# bases = ["EUR", "GBP", "USD", "JPY", "CHF", "CAD", "AUD", "NZD"]
# quotes = ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
# instruments = [f"{base}_{quote}" for base in bases for quote in quotes]
```

### Request Batching

Batch related operations when possible:

```python
import os
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

async def batch_pricing_example() -> tuple[object, object, object, object]:
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Good: Single request for multiple instruments
        prices = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=["EUR_USD", "GBP_USD", "USD_JPY"]
        )

        # Less efficient: Multiple requests
        eur_usd = await client.pricing.get_pricing(account_id, ["EUR_USD"])
        gbp_usd = await client.pricing.get_pricing(account_id, ["GBP_USD"])
        usd_jpy = await client.pricing.get_pricing(account_id, ["USD_JPY"])

        return prices, eur_usd, gbp_usd, usd_jpy
```

## Common Anti-Patterns

### Avoid These Patterns

<!-- fragment: bad examples - intentionally wrong patterns -->
```python
import os
import time
from fivetwenty import AsyncClient, Environment

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# ❌ Creating clients in loops
async def bad_pattern_example():
    symbols = ["EUR_USD", "GBP_USD"]
    for symbol in symbols:
        async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:  # Expensive!
            _price = await client.pricing.get_pricing(account_id, [symbol])

# ❌ Blocking operations in async context
async def bad_async():
    time.sleep(1)  # Blocks entire event loop

# ❌ Float arithmetic for money
profit_loss = 1234.56 + 0.1  # Precision errors!

# ❌ Ignoring error details
async def bad_error_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            _order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except Exception:
            pass  # Lost important error information

# ❌ Not handling rate limits
async def bad_rate_limit_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        while True:
            await client.accounts.get_account(account_id)  # Will hit rate limits
```

### Correct Alternatives

<!-- fragment: Demo best practices with logging and exception handling patterns -->
```python
import asyncio
import logging
import os
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import VeeTwentyError, TooManyRequests

logger = logging.getLogger(__name__)

# Setup
token = os.getenv("OANDA_TOKEN")
account_id = "101-001-0000000-001"

# ✅ Reuse client across operations
async def good_pattern_example():
    symbols = ["EUR_USD", "GBP_USD"]
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        for symbol in symbols:
            _price = await client.pricing.get_pricing(account_id, [symbol])

# ✅ Async operations in async context
async def good_async():
    await asyncio.sleep(1)  # Non-blocking

# ✅ Decimal arithmetic for money
profit_loss = Decimal("1234.56") + Decimal("0.1")

# ✅ Specific error handling
async def good_error_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            _order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
        except VeeTwentyError as e:
            logger.error(f"Order failed: {e.message}")

# ✅ Respect rate limits
async def good_rate_limit_handling():
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            await client.accounts.get_account(account_id)
        except TooManyRequests as e:
            await asyncio.sleep(e.retry_after or 60)
```

## Order Validation Framework

### Pre-Order Validation System

Implement comprehensive validation to prevent costly trading errors:

<!-- fragment: Demo validation framework with complex class hierarchies and attribute access -->
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from fivetwenty import AsyncClient


class ValidationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    is_valid: bool
    severity: ValidationSeverity
    rule_name: str
    message: str
    details: dict[str, Any] | None = None


class OrderValidator(ABC):
    """Base class for order validation rules."""

    def __init__(self, name: str, severity: ValidationSeverity = ValidationSeverity.ERROR) -> None:
        self.name = name
        self.severity = severity
        self.enabled = True

    @abstractmethod
    async def validate(self, order_params: dict[str, Any], context: dict[str, Any]) -> ValidationResult:
        """Validate order parameters and return result."""
        pass


class OrderValidationFramework:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.validators: list[OrderValidator] = []
        self.validation_history: list[object] = []

    def add_validator(self, validator: OrderValidator) -> None:
        """Add a validator to the framework."""
        self.validators.append(validator)

    async def validate_order(
        self,
        order_params: dict[str, Any],
        strict_mode: bool = True,
    ) -> dict[str, Any]:
        """Validate order against all registered validators."""
        validation_session = {
            "timestamp": datetime.utcnow(),
            "order_params": order_params,
            "results": [],
            "passed": True,
            "errors": [],
            "warnings": [],
        }

        # Build context for validators
        context = await self._build_validation_context()

        # Run all validators
        for validator in self.validators:
            if not validator.enabled:
                continue

            try:
                result = await validator.validate(order_params, context)
                validation_session["results"].append(result)

                if not result.is_valid:
                    if result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]:
                        validation_session["errors"].append(result)
                        validation_session["passed"] = False
                    elif result.severity == ValidationSeverity.WARNING:
                        validation_session["warnings"].append(result)
                        if strict_mode:
                            validation_session["passed"] = False

            except Exception as e:
                error_result = ValidationResult(
                    is_valid=False,
                    severity=ValidationSeverity.CRITICAL,
                    rule_name=validator.name,
                    message=f"Validator failed: {e}",
                    details={"exception": str(e)},
                )
                validation_session["results"].append(error_result)
                validation_session["errors"].append(error_result)
                validation_session["passed"] = False

        # Store validation history
        self.validation_history.append(validation_session)
        return validation_session

    async def _build_validation_context(self) -> dict[str, Any]:
        """Build context information for validators."""
        try:
            # Get account information
            account = await self.client.accounts.get_account(account_id=self.account_id)
            positions = await self.client.positions.get_positions(account_id=self.account_id)
            orders = await self.client.orders.get_orders(account_id=self.account_id)

            return {
                "account": account,
                "positions": positions.positions,
                "pending_orders": orders.orders,
                "current_time": datetime.utcnow(),
                "account_balance": Decimal(account.balance),
                "margin_available": Decimal(account.margin_available),
                "margin_used": Decimal(account.margin_used),
            }

        except Exception as e:
            return {"error": str(e)}
```

### Risk-Based Validators

<!-- fragment: validator class example with missing imports -->
```python
class MaxPositionSizeValidator(OrderValidator):
    """Validate order doesn't exceed maximum position size limits."""

    def __init__(self, max_units_per_instrument: int, max_total_exposure: Decimal) -> None:
        super().__init__("MaxPositionSize", ValidationSeverity.ERROR)
        self.max_units_per_instrument = max_units_per_instrument
        self.max_total_exposure = max_total_exposure

    async def validate(self, order_params: dict[str, Any], context: dict[str, Any]) -> ValidationResult:
        """Validate position size limits."""
        instrument = order_params.get("instrument")
        units = int(order_params.get("units", 0))

        # Check individual instrument limit
        current_position_size = 0
        for position in context.get("positions", []):
            if position.instrument == instrument:
                if position.long.units != "0":
                    current_position_size += int(position.long.units)
                if position.short.units != "0":
                    current_position_size += abs(int(position.short.units))

        new_position_size = current_position_size + abs(units)

        if new_position_size > self.max_units_per_instrument:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Position size {new_position_size} exceeds limit {self.max_units_per_instrument}",
                details={
                    "current_size": current_position_size,
                    "order_size": abs(units),
                    "new_size": new_position_size,
                    "limit": self.max_units_per_instrument
                }
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message="Position size validation passed"
        )


class RiskPerTradeValidator(OrderValidator):
    """Validate risk per trade doesn't exceed limits."""

    def __init__(self, max_risk_per_trade: Decimal) -> None:
        super().__init__("RiskPerTrade", ValidationSeverity.WARNING)
        self.max_risk_per_trade = max_risk_per_trade

    async def validate(self, order_params: dict[str, Any], context: dict[str, Any]) -> ValidationResult:
        """Validate risk per trade."""
        units = order_params.get("units", 0)
        entry_price = order_params.get("price")
        stop_price = order_params.get("stop_loss_price")

        if not entry_price or not stop_price:
            return ValidationResult(
                is_valid=True,
                severity=ValidationSeverity.INFO,
                rule_name=self.name,
                message="No stop loss specified - cannot validate risk"
            )

        # Calculate risk amount
        stop_distance = abs(Decimal(str(entry_price)) - Decimal(str(stop_price)))
        risk_amount = abs(units) * stop_distance
        account_balance = context.get("account_balance", Decimal("0"))
        risk_percentage = risk_amount / account_balance if account_balance > 0 else Decimal("1")

        if risk_percentage > self.max_risk_per_trade:
            return ValidationResult(
                is_valid=False,
                severity=self.severity,
                rule_name=self.name,
                message=f"Risk {risk_percentage:.2%} exceeds limit {self.max_risk_per_trade:.2%}",
                details={
                    "risk_amount": risk_amount,
                    "risk_percentage": risk_percentage,
                    "limit": self.max_risk_per_trade,
                    "account_balance": account_balance
                }
            )

        return ValidationResult(
            is_valid=True,
            severity=ValidationSeverity.INFO,
            rule_name=self.name,
            message=f"Risk validation passed: {risk_percentage:.2%}"
        )
```

### Production Error Recovery

Implement comprehensive error recovery for production systems:

```python
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import traceback
import asyncio

from fivetwenty.exceptions import VeeTwentyError


class ErrorCategory(Enum):
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    MARKET_DATA = "market_data"
    ORDER_EXECUTION = "order_execution"
    INSUFFICIENT_FUNDS = "insufficient_funds"
    RATE_LIMITING = "rate_limiting"
    SYSTEM = "system"


class TradingErrorHandler:
    def __init__(self, client: AsyncClient, account_id: str) -> None:
        self.client = client
        self.account_id = account_id
        self.error_handlers = {}
        self.error_history = []
        self.circuit_breaker_states = {}

    def register_error_handler(
        self,
        error_category: ErrorCategory,
        handler: Callable,
        max_retries: int = 3,
        retry_delay: int = 1
    ) -> None:
        """Register error handler for specific error category."""
        self.error_handlers[error_category] = {
            "handler": handler,
            "max_retries": max_retries,
            "retry_delay": retry_delay
        }

    async def handle_error(
        self,
        error: Exception,
        operation_context: dict[str, Any],
        error_category: Optional[ErrorCategory] = None
    ) -> dict[str, Any]:
        """Handle error with appropriate recovery strategy."""
        if not error_category:
            error_category = self._categorize_error(error)

        # Record error
        error_record = {
            "timestamp": datetime.utcnow(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_category": error_category,
            "operation_context": operation_context,
            "stack_trace": traceback.format_exc(),
            "recovery_attempted": False,
            "recovery_successful": False
        }

        self.error_history.append(error_record)

        # Check circuit breaker
        if self._should_circuit_break(error_category):
            error_record["circuit_breaker_triggered"] = True
            return error_record

        # Attempt recovery
        if error_category in self.error_handlers:
            handler_config = self.error_handlers[error_category]

            for attempt in range(handler_config["max_retries"]):
                try:
                    error_record["recovery_attempted"] = True
                    recovery_result = await handler_config["handler"](
                        error, operation_context, attempt
                    )

                    if recovery_result.get("success", False):
                        error_record["recovery_successful"] = True
                        error_record["recovery_result"] = recovery_result
                        break

                    await asyncio.sleep(handler_config["retry_delay"] * (2 ** attempt))

                except Exception as recovery_error:
                    error_record["recovery_error"] = str(recovery_error)

        return error_record

    def _categorize_error(self, error: Exception) -> ErrorCategory:
        """Categorize error based on type and message."""
        error_message = str(error).lower()

        if "network" in error_message or "connection" in error_message:
            return ErrorCategory.NETWORK
        if "authentication" in error_message or "unauthorized" in error_message:
            return ErrorCategory.AUTHENTICATION
        if "insufficient" in error_message and "margin" in error_message:
            return ErrorCategory.INSUFFICIENT_FUNDS
        if "rate limit" in error_message or "too many requests" in error_message:
            return ErrorCategory.RATE_LIMITING
        if "validation" in error_message or "invalid" in error_message:
            return ErrorCategory.VALIDATION
        if isinstance(error, VeeTwentyError):
            return ErrorCategory.ORDER_EXECUTION

        return ErrorCategory.SYSTEM

    def _should_circuit_break(self, error_category: ErrorCategory) -> bool:
        """Determine if circuit breaker should trigger."""
        recent_errors = [
            err for err in self.error_history[-10:]  # Last 10 errors
            if err["error_category"] == error_category
            and (datetime.utcnow() - err["timestamp"]).seconds < 300  # Last 5 minutes
        ]
        return len(recent_errors) >= 5
```

## Testing Considerations

### Mock Testing

Use proper mocking for unit tests:

<!-- fragment: test mocking examples with mock data -->
```python
from unittest.mock import AsyncMock
import pytest

# Mock response object
mock_response = AsyncMock()

# Example trading function to test
async def trading_function(client, account_id: str, instrument: str, units: int):
    return await client.orders.post_market_order(
        account_id=account_id,
        instrument=instrument,
        units=units
    )

@pytest.mark.asyncio
async def test_trading_logic():
    # Mock the client
    mock_client = AsyncMock()
    mock_client.orders.post_market_order.return_value = mock_response

    # Test your logic
    result = await trading_function(mock_client, "101-001-0000000-001", "EUR_USD", 1000)

    # Verify calls
    mock_client.orders.post_market_order.assert_called_once_with(
        account_id="101-001-0000000-001",
        instrument="EUR_USD",
        units=1000
    )
```

### Integration Testing

Test against practice environment:

<!-- fragment: Demo integration testing with ValueError string literals -->
```python
import os
import pytest
from fivetwenty import AsyncClient, Environment

@pytest.mark.integration
async def test_live_api():
    """Test against OANDA practice environment."""
    async with AsyncClient(
        token=os.environ["OANDA_PRACTICE_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:
        # Test real API calls
        accounts = await client.accounts.get_accounts()
        if len(accounts) == 0:
            raise ValueError("Expected at least one account")
```

### Validation Testing

Test your validation rules thoroughly:

<!-- fragment: test example with undefined imports and mock objects -->
```python
@pytest.mark.asyncio
async def test_position_size_validator():
    # Create validator
    validator = MaxPositionSizeValidator(
        max_units_per_instrument=100000,
        max_total_exposure=Decimal("500000")
    )

    # Mock context with existing position
    context = {
        "positions": [
            MockPosition(instrument="EUR_USD", long_units="50000", short_units="0")
        ]
    }

    # Test order that would exceed limit
    order_params = {"instrument": "EUR_USD", "units": 60000}
    result = await validator.validate(order_params, context)

    if result.is_valid:
        raise ValueError("Expected validation to fail")
    if result.severity != ValidationSeverity.ERROR:
        raise ValueError(f"Expected severity ERROR, got '{result.severity}'")
```

## Summary

Key principles for FiveTwenty SDK usage:

1. **Use context managers** for automatic resource cleanup
2. **Always use Decimal** for financial calculations
3. **Handle specific exceptions** rather than generic Exception
4. **Reuse client instances** for better performance
5. **Implement proper retry logic** with exponential backoff
6. **Secure token management** - never hardcode or log tokens
7. **Test thoroughly** in practice environment before live trading
8. **Implement comprehensive validation** - prevent costly errors before they occur
9. **Build robust error recovery** - handle failures gracefully with circuit breakers
10. **Monitor and categorize errors** - track patterns for system improvement

Following these patterns ensures robust, maintainable, and secure trading applications with comprehensive risk management and validation frameworks.