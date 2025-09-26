# Best Practices

This guide provides production-ready best practices for using the FiveTwenty in real trading systems.

## Production Architecture

### System Design

```python
"""Comprehensive module for trading operations."""
import asyncio
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from fivetwenty import AsyncClient, Environment


@dataclass
class TradingSystemConfig:
    """Production trading system configuration."""

    # Risk limits
    max_position_size: int = 10000
    max_daily_loss: Decimal = Decimal("1000.0")
    max_open_positions: int = 5

    # Performance
    order_timeout: float = 5.0
    stream_reconnect_delay: float = 5.0

    # Monitoring
    health_check_interval: float = 60.0
    alert_on_disconnect: bool = True

class ProductionTradingSystem:
    """Production-ready trading system."""

    def __init__(self, config: TradingSystemConfig) -> None:
        self.config = config
        self.client: AsyncClient | None = None
        self.positions: dict = {}
        self.daily_pnl = 0.0
        self.is_running = False

    async def start(self) -> Any:
        """Start the trading system."""
        import logging

        # Initialize client
        self.client = AsyncClient(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],
            environment=Environment.LIVE,  # Production!
            timeout=self.config.order_timeout,
            max_retries=5,  # More retries for production
            logger=logging.getLogger(__name__),
        )

        # Start components
        self.is_running = True
        await asyncio.gather(
            self.monitor_health(),
            self.stream_prices(),
            self.manage_risk(),
            return_exceptions=True,
        )

    async def setup_logger(self) -> Any:
        """Set up logging."""
        return None

    async def monitor_health(self) -> Any:
        """Monitor system health."""
        pass

    async def stream_prices(self) -> Any:
        """Stream price data."""
        pass

    async def manage_risk(self) -> Any:
        """Manage risk."""
        pass
```

### Separation of Concerns

```python
"""Comprehensive module for trading operations."""
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient


class DataLayer:
    """Handle all data operations."""

    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.price_cache: dict = {}
        self.account_cache = None

    async def get_price(self, instrument: str) -> Decimal:
        """Get current price with caching."""
        # Implementation
        pass


class TradingLogic:
    """Trading strategy implementation."""

    def __init__(self, data: DataLayer) -> None:
        self.data = data

    async def should_trade(self, instrument: str) -> bool:
        """Determine if we should trade."""
        # Strategy logic
        pass


class RiskManager:
    """Risk management layer."""

    def __init__(self, config: TradingSystemConfig) -> None:
        self.config = config

    def validate_order(self, order: dict) -> bool:
        """Validate order against risk limits."""
        # Risk checks
        pass


class OrderExecutor:
    """Handle order execution."""

    def __init__(self, client: AsyncClient, risk: RiskManager) -> None:
        self.client = client
        self.risk = risk

    async def execute_order(self, order: dict) -> Any:
        """Execute order with risk checks."""
        if not self.risk.validate_order(order):
            raise ValueError("Order failed risk checks")

        return await self.client.orders.post_market_order(**order)
```

## Risk Management

### Position Sizing

```python
"""Comprehensive module for trading operations."""
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient


class PositionSizer:
    """Calculate safe position sizes."""

    def __init__(self, risk_per_trade: float = 0.02) -> None:
        self.risk_per_trade = risk_per_trade  # 2% risk per trade

    async def calculate_position_size(
        self,
        client: AsyncClient,
        account_id: str,
        instrument: str,
        stop_distance: Decimal,
    ) -> int:
        """Calculate position size based on risk."""

        # Get account info
        account = await client.accounts.get_account(account_id)
        balance = Decimal(account.balance)

        # Calculate risk amount
        risk_amount = balance * Decimal(str(self.risk_per_trade))

        # Get instrument info for pip value
        instruments = await client.accounts.get_account_instruments(
            account_id=account_id,
            instruments=[instrument],
        )
        pip_value = self.calculate_pip_value(instruments[0])

        # Calculate position size
        position_size = risk_amount / (stop_distance * pip_value)

        # Round to valid increment
        return self.round_to_increment(position_size, instruments[0])

    def calculate_pip_value(self, instrument: Any) -> Any:
        """Calculate pip value for instrument."""
        # Implementation based on instrument
        pass

    def round_to_increment(self, position_size: Decimal, instrument: Any) -> int:
        """Round position size to valid increment."""
        # Implementation
        return int(position_size)
```

### Stop Loss Management

```python
"""Comprehensive module for trading operations."""
from decimal import Decimal
from typing import Any

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode


class StopLossManager:
    """Manage stop losses for all positions."""

    def __init__(self, client: AsyncClient) -> None:
        self.client = client

    async def set_stop_loss(self, account_id: str, trade_id: str, stop_price: str) -> Any:
        """Set or update stop loss."""

        try:
            # Update stop loss
            # Create stop loss using post_order with StopLossOrderRequest
            from fivetwenty.models import StopLossOrderRequest

            sl_request = StopLossOrderRequest(
                tradeID=trade_id,
                price=stop_price,
                timeInForce="GTC",
            )
            await self.client.orders.post_order(account_id, sl_request)
            print(f"Stop loss set at {stop_price} for trade {trade_id}")

        except FiveTwentyError as e:
            if e.code == FiveTwentyErrorCode.STOP_LOSS_ORDER_ALREADY_EXISTS:
                # Update existing stop loss
                await self.update_stop_loss(account_id, trade_id, stop_price)
            else:
                raise

    async def trailing_stop(self, account_id: str, trade_id: str, distance: Decimal) -> Any:
        """Implement trailing stop."""

        # Get current trade
        trade = await self.client.trades.get_trade(account_id, trade_id)

        # Calculate new stop based on current price
        if float(trade.current_units) > 0:  # Long position
            new_stop = Decimal(trade.price) - distance
        else:  # Short position
            new_stop = Decimal(trade.price) + distance

        # Update if better than current stop
        if self.is_better_stop(trade, new_stop):
            await self.set_stop_loss(account_id, trade_id, str(new_stop))

    async def update_stop_loss(self, account_id: str, trade_id: str, stop_price: str) -> Any:
        """Update existing stop loss."""
        pass

    def is_better_stop(self, trade: Any, new_stop: Decimal) -> bool:
        """Check if new stop is better."""
        return True
```

### Daily Loss Limits

```python
"""Comprehensive module for trading operations."""
from decimal import Decimal
from typing import Any


class DailyLossLimiter:
    """Enforce daily loss limits."""

    def __init__(self, max_daily_loss: Decimal) -> None:
        self.max_daily_loss = max_daily_loss
        self.daily_pnl = Decimal("0.0")
        self.trading_enabled = True

    async def update_pnl(self, pnl: Decimal) -> Any:
        """Update daily P&L and check limits."""

        self.daily_pnl += pnl

        if self.daily_pnl <= -self.max_daily_loss:
            self.trading_enabled = False
            await self.close_all_positions()
            await self.send_alert("Daily loss limit reached!")

    def can_trade(self) -> bool:
        """Check if trading is allowed."""
        return self.trading_enabled

    def reset_daily(self) -> None:
        """Reset for new trading day."""
        self.daily_pnl = Decimal("0.0")
        self.trading_enabled = True

    async def close_all_positions(self) -> None:
        """Close all open positions."""
        pass

    async def send_alert(self, message: str) -> None:
        """Send alert message."""
        print(message)
```

## Error Recovery

### Resilient Operations

```python
"""Comprehensive module for trading operations."""
import asyncio
import logging
from typing import Any

from fivetwenty import AsyncClient


logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self) -> None:
        self.is_open_flag = False

    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.is_open_flag

    def on_success(self) -> None:
        """Handle successful operation."""
        self.is_open_flag = False

    def on_failure(self) -> None:
        """Handle failed operation."""
        self.is_open_flag = True


class TooManyRequests(Exception):
    """Rate limit exceeded exception."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__()


class InternalServerError(Exception):
    """Internal server error exception."""
    pass


class ResilientClient:
    """Wrapper for resilient operations."""

    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.circuit_breaker = CircuitBreaker()

    async def safe_order(self, **kwargs: Any) -> Any:
        """Place order with full error handling."""

        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                raise Exception("Circuit breaker open")

            # Validate order
            self.validate_order(kwargs)

            # Execute with timeout
            async with asyncio.timeout(5.0):
                result = await self.client.orders.post_market_order(**kwargs)

            # Reset circuit breaker on success
            self.circuit_breaker.on_success()

            return result

        except TooManyRequests as e:
            # Rate limited - wait and retry
            await asyncio.sleep(e.retry_after or 60)
            return await self.safe_order(**kwargs)

        except InternalServerError as e:
            # Server error - circuit breaker
            self.circuit_breaker.on_failure()
            raise

        except Exception as e:
            # Log and re-raise
            logger.error(f"Order failed: {e}")
            raise

    def validate_order(self, kwargs: dict) -> None:
        """Validate order parameters."""
        pass
```

### State Persistence

```python
import json
from pathlib import Path
from fivetwenty import AsyncClient
from datetime import datetime




"""Comprehensive module for trading operations."""
class StateManager:
    """Persist and recover system state."""

    def __init__(self, state_file: str = "trading_state.json") -> None:
        self.state_file = Path(state_file)
        self.state = self.load_state()

    def load_state(self) -> dict:
        """Load state from file."""

        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)

        return {
            "positions": {},
            "pending_orders": [],
            "daily_pnl": 0.0,
            "last_update": None,
        }

    def save_state(self) -> Any:
        """Save current state."""

        self.state["last_update"] = datetime.now().isoformat()

        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    async def recover_positions(self, client: AsyncClient, account_id: str) -> Any:
        """Recover positions after restart."""

        # Get current positions
        current = await client.positions.get_open_positions(account_id)

        # Compare with saved state
        for position in current:
            if position.instrument not in self.state["positions"]:
                print(f"New position detected: {position.instrument}")
                # Handle unexpected position
```

## Performance Optimization

### Connection Pooling

```python
from fivetwenty import AsyncClient



"""Comprehensive module for trading operations."""
class ConnectionPool:
    """Manage multiple client connections."""

    def __init__(self, size: int = 5) -> None:
        self.clients = []
        self.current = 0

        # Load secure configuration
        from fivetwenty import AccountConfigLoader
        config = AccountConfigLoader.load_default()
        if not config:
            raise ValueError("No configuration found for connection pool")

        for _ in range(size):
            client = AsyncClient(config=config)
            self.clients.append(client)

    def get_client(self) -> AsyncClient:
        """Get next available client."""

        client = self.clients[self.current]
        self.current = (self.current + 1) % len(self.clients)
        return client

    async def close_all(self) -> Any:
        """Close all clients."""

        for client in self.clients:
            await client.aclose()
```

### Caching Strategy

```python
from datetime import datetime, timedelta
from fivetwenty import AsyncClient




"""Comprehensive module for trading operations."""
class CachedDataProvider:
    """Cache frequently accessed data."""

    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.cache = {}
        self.cache_times = {}

    async def get_instrument_info(self, account_id: str, instrument: str, cache_duration: int = 3600) -> Any:
        """Get instrument info with caching."""

        cache_key = f"{account_id}:{instrument}"

        # Check cache
        if cache_key in self.cache:
            cache_time = self.cache_times[cache_key]
            if datetime.now() - cache_time < timedelta(seconds=cache_duration):
                return self.cache[cache_key]

        # Fetch fresh data
        data = await self.client.accounts.get_account_instruments(
            account_id=account_id,
            instruments=[instrument],
        )

        # Update cache
        self.cache[cache_key] = data[0]
        self.cache_times[cache_key] = datetime.now()

        return data[0]
```

## Monitoring and Alerting

### Health Checks

```python
from fivetwenty import AsyncClient
from datetime import datetime


"""Comprehensive module for trading operations."""
class HealthMonitor:
    """Monitor system health."""

    def __init__(self, client: AsyncClient) -> None:
        self.client = client
        self.metrics = {
            "api_calls": 0,
            "errors": 0,
            "last_heartbeat": None,
            "stream_status": "unknown",
        }

    async def health_check(self) -> dict:
        """Perform health check."""

        health = {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "checks": {},
        }

        # Check API connectivity
        try:
            accounts = await self.client.accounts.get_accounts()
            health["checks"]["api"] = "ok"
        except Exception as e:
            health["checks"]["api"] = f"failed: {e}"
            health["status"] = "unhealthy"

        # Check stream status
        if self.metrics["last_heartbeat"]:
            heartbeat_age = datetime.now() - self.metrics["last_heartbeat"]
            if heartbeat_age.total_seconds() > 60:
                health["checks"]["stream"] = "stale"
                health["status"] = "degraded"
            else:
                health["checks"]["stream"] = "ok"

        # Check error rate
        if self.metrics["api_calls"] > 0:
            error_rate = self.metrics["errors"] / self.metrics["api_calls"]
            if error_rate > 0.05:  # 5% error rate
                health["checks"]["errors"] = f"high: {error_rate:.2%}"
                health["status"] = "degraded"

        return health
```

### Alerting System

```python

from typing import Any
import smtplib
from email.mime.text import MIMEText




"""Module docstring."""
"""Module docstring."""

"""Comprehensive module for trading operations."""
class AlertManager:
    """Class docstring."""
    """Send alerts for critical events."""

    def __init__(self, email_config: dict) -> None:
        self.email_config = email_config

    async def send_alert(self, subject: str, message: str, severity: str = "INFO") -> Any:
        """Send alert via email."""

        if severity not in ["INFO", "WARNING", "CRITICAL"]:
            severity = "INFO"

        # Only send email for WARNING and CRITICAL
        if severity in ["WARNING", "CRITICAL"]:
            await self.send_email(subject, message)

        # Always log
        logger.log(
            getattr(logging, severity),
            f"Alert: {subject} - {message}",
        )

    async def send_email(self, subject: str, body: str) -> Any:
        """Send email alert."""

        msg = MIMEText(body)
        msg["Subject"] = f"[Trading Alert] {subject}"
        msg["From"] = self.email_config["from"]
        msg["To"] = self.email_config["to"]

        with smtplib.SMTP(self.email_config["smtp_server"]) as server:
            server.send_message(msg)
```

## Testing Strategies

### Test Environment Setup

```bash
# Set up dedicated test environment
export TEST_OANDA_TOKEN="your-practice-token"
export TEST_OANDA_ACCOUNT="your-practice-account"
export TEST_OANDA_ENVIRONMENT="practice"

# Install test dependencies
uv sync --extra dev

# Run specific test types
poe test-unit           # Fast unit tests only
poe test-integration    # Real API integration tests
poe test-cov           # Tests with coverage report
```

### Unit Testing with Mocks

```python
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode
from fivetwenty.models import Account


@pytest.fixture
def mock_client():
    """Create a mocked AsyncClient for testing."""
    return AsyncMock(spec=AsyncClient)

async def test_account_balance_check(mock_client):
    """Test account balance validation."""

    # Setup mock response
    mock_account = Account(
        id="test-account",
        balance=Decimal("10000.00"),
        currency="USD",
        margin_used=Decimal("2000.00"),
        margin_available=Decimal("8000.00"),
    )
    mock_client.accounts.get.return_value = mock_account

    # Test the function
    account = await mock_client.accounts.get_account("test-account")

    assert account.balance == Decimal("10000.00")
    assert account.margin_available == Decimal("8000.00")
    mock_client.accounts.get.assert_called_once_with("test-account")

async def test_order_error_handling(mock_client):
    """Test error handling in order placement."""

    # Setup mock to raise error
    mock_client.orders.post_market_order.side_effect = FiveTwentyError(
        status_code=400,
        code=FiveTwentyErrorCode.INSUFFICIENT_FUNDS,
        message="Insufficient margin",
    )

    # Test error handling
    with pytest.raises(FiveTwentyError) as exc_info:
        await mock_client.orders.post_market_order(
            account_id="test-account",
            instrument="EUR_USD",
            units=1000000,  # Too large
        )

    assert exc_info.value.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS
```

### Integration Testing with VCR

Integration tests use VCR.py to record real API interactions:

```python
import pytest
import vcr

from fivetwenty import AsyncClient, Environment

# Configure VCR for sensitive data
my_vcr = vcr.VCR(
    serializer="yaml",
    cassette_library_dir="tests/fixtures/vcr_cassettes",
    record_mode="once",
    filter_headers=["authorization"],  # Remove sensitive headers
    filter_query_parameters=["access_token"],
)

@pytest.mark.integration
@my_vcr.use_cassette("account_retrieval.yaml")
async def test_account_retrieval():
    """Test real account retrieval with recorded response."""

    async with AsyncClient(
        token=os.environ["TEST_OANDA_TOKEN"],
        environment=Environment.PRACTICE,
    ) as client:
        accounts = await client.accounts.get_accounts()

        assert len(accounts) > 0
        assert accounts[0].currency in ["USD", "EUR", "GBP"]

@pytest.mark.integration
@my_vcr.use_cassette("full_trade_lifecycle.yaml")
async def test_full_trade_lifecycle():
    """Test complete trade lifecycle."""

    async with AsyncClient(
        token=os.environ["TEST_OANDA_TOKEN"],
        environment=Environment.PRACTICE,
    ) as client:
        account_id = os.environ["TEST_OANDA_ACCOUNT"]

        # Place order
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000,
        )

        assert order.order_fill_transaction
        trade_id = order.order_fill_transaction.trade_opened_id

        # Verify trade created
        trades = await client.trades.get_open_trades(account_id)
        trade_ids = [t.id for t in trades]
        assert trade_id in trade_ids

        # Close trade
        await client.trades.close_trade(account_id, trade_id)

        # Verify trade closed
        trades = await client.trades.get_open_trades(account_id)
        trade_ids = [t.id for t in trades]
        assert trade_id not in trade_ids
```

### Property-Based Testing

Use Hypothesis for robust testing with random data:

```python
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st


@given(
    units=st.integers(min_value=1, max_value=100000),
    price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("10.00"), places=5),
)
async def test_position_size_calculation(mock_client, units, price):
    """Test position size calculations with various inputs."""

    position_value = Decimal(str(units)) * price

    # Test that calculations are always precise
    assert isinstance(position_value, Decimal)
    assert position_value >= Decimal("0.01")

@given(
    instruments=st.lists(
        st.sampled_from(["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD"]),
        min_size=1,
        max_size=10,
        unique=True,
    ),
)
async def test_pricing_request(mock_client, instruments):
    """Test pricing requests with various instrument combinations."""

    # Mock successful response
    mock_client.pricing.get.return_value = [
        # Mock price objects for each instrument
    ]

    prices = await mock_client.pricing.get_pricing("account-id", instruments)
    assert len(prices) == len(instruments)
```

### Load Testing

```python
import asyncio
import time
from statistics import mean, median


async def test_concurrent_requests():
    """Test SDK performance under concurrent load."""

    async def make_request(client, account_id):
        start = time.time()
        await client.accounts.get_account(account_id)
        return time.time() - start

    async with AsyncClient(
        token=os.environ["TEST_OANDA_TOKEN"],
        environment=Environment.PRACTICE,
    ) as client:
        account_id = os.environ["TEST_OANDA_ACCOUNT"]

        # Run 20 concurrent requests
        tasks = [make_request(client, account_id) for _ in range(20)]
        durations = await asyncio.gather(*tasks)

        # Performance assertions
        assert mean(durations) < 2.0  # Average under 2 seconds
        assert median(durations) < 1.5  # Median under 1.5 seconds
        assert max(durations) < 5.0  # No request over 5 seconds

### Error Scenario Testing
```python

"""Comprehensive module for trading operations."""
@pytest.mark.parametrize("error_code,expected_behavior", [
    (FiveTwentyErrorCode.INSUFFICIENT_FUNDS, "reduce_position_size"),
    (FiveTwentyErrorCode.MARKET_HALTED, "wait_for_market"),
    (FiveTwentyErrorCode.INVALID_INSTRUMENT, "validation_error"),
])
async def test_error_handling_scenarios(mock_client: Any, error_code: Any, expected_behavior: Any) -> Any:
    """Test various error scenarios and expected responses."""

    mock_client.orders.post_market_order.side_effect = FiveTwentyError(
        status_code=400,
        code=error_code,
        message=f"Test error: {error_code}"
    )

    with pytest.raises(FiveTwentyError) as exc_info:
        await mock_client.orders.post_market_order(
            account_id="test",
            instrument="EUR_USD",
            units=1000
        )

    assert exc_info.value.code == error_code

## Debugging and Troubleshooting

### HTTP Request/Response Debugging

Enable detailed logging to see all API interactions:
```python
import logging
import os
import sys

from fivetwenty import AsyncClient, Environment

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)

# Enable httpx debug logging
logging.getLogger("httpx").setLevel(logging.DEBUG)

async def debug_api_calls():
    """Debug API calls with full request/response logging."""

    async with AsyncClient(
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],
        environment=Environment.PRACTICE,
    ) as client:
        # This will log all HTTP details
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} accounts")
```

### Model Validation Debugging

When Pydantic models fail validation:

```python
from pydantic import ValidationError

from fivetwenty.models import Account


def debug_model_validation(raw_data: dict):
    """Debug model validation issues."""

    try:
        account = Account.model_validate(raw_data)
        print("✅ Validation successful")
        return account
    except ValidationError as e:
        print("❌ Validation failed:")

        for error in e.errors():
            field_path = " -> ".join(str(x) for x in error["loc"])
            print(f"  Field: {field_path}")
            print(f"  Error: {error['msg']}")
            print(f"  Input: {error['input']}")
            print(f"  Type: {error['type']}")
            print("---")

        # Show the full error for debugging
        print(f"Full error: {e}")
        raise

# Example usage
raw_account_data = {
    "id": "123-456-789",
    "balance": "invalid_number",  # This will cause validation error
    "currency": "USD",
}

try:
    account = debug_model_validation(raw_account_data)
except ValidationError:
    print("Fix the data and try again")
```

### Connection and Network Debugging

```python
import asyncio

import aiohttp

from fivetwenty import AsyncClient


async def debug_connection_issues():
    """Debug connection and timeout issues."""

    # Custom timeout configuration for debugging
    timeout = aiohttp.ClientTimeout(
        total=30,      # Total request timeout
        connect=10,    # Connection timeout
        sock_read=10,   # Socket read timeout
    )

    try:
        async with AsyncClient(
            token=os.environ["FIVETWENTY_OANDA_TOKEN"],
            environment=Environment.PRACTICE,
            timeout=timeout,
        ) as client:

            start_time = asyncio.get_event_loop().time()
            accounts = await client.accounts.get_accounts()
            end_time = asyncio.get_event_loop().time()

            print(f"✅ Request successful in {end_time - start_time:.2f} seconds")

    except asyncio.TimeoutError:
        print("❌ Request timed out - check your internet connection")
    except Exception as e:
        print(f"❌ Connection error: {type(e).__name__}: {e}")

### Performance Profiling
```python
import cProfile
import asyncio
from fivetwenty import AsyncClient, Environment


"""Comprehensive module for trading operations."""
def profile_async_function(func: Any) -> Any:
    """Profile an async function."""

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        pr = cProfile.Profile()
        pr.enable()

        # Run the async function
        result = asyncio.run(func(*args, **kwargs))

        pr.disable()
        pr.print_stats(sort='cumulative')

        return result

    return wrapper

@profile_async_function
async def performance_test() -> Any:
    """Profile SDK performance."""

    async with AsyncClient(
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:

        # Multiple concurrent operations
        results = await asyncio.gather(
            client.accounts.get_accounts(),
            client.accounts.get_account("your-account-id"),
            client.pricing.get_pricing("your-account-id", ["EUR_USD", "GBP_USD"]),
            return_exceptions=True
        )

        return results

# Run performance test
# performance_test()
```

### Memory Usage Debugging
```python
import tracemalloc
import asyncio
from fivetwenty import AsyncClient, Environment


"""Comprehensive module for trading operations."""
async def memory_usage_test() -> Any:
    """Monitor memory usage during SDK operations."""

    # Start memory tracing
    tracemalloc.start()

    async with AsyncClient(
        token=os.environ["FIVETWENTY_OANDA_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:

        # Take snapshot before
        snapshot1 = tracemalloc.take_snapshot()

        # Perform operations
        for i in range(100):
            await client.accounts.get_accounts()

        # Take snapshot after
        snapshot2 = tracemalloc.take_snapshot()

        # Compare snapshots
        top_stats = snapshot2.compare_to(snapshot1, 'lineno')

        print("Top 10 memory allocations:")
        for stat in top_stats[:10]:
            print(stat)

### Common Issues and Solutions

#### Issue: "RuntimeError: This event loop is already running"
```python
from fivetwenty import AsyncClient, Environment

# Solution 1: Use nest_asyncio (for Jupyter)
import nest_asyncio
nest_asyncio.apply()

# Solution 2: Use asyncio.create_task() instead of asyncio.run()
async def main():
    async with AsyncClient(...) as client:
        result = await client.accounts.get_accounts()
    return result

# In Jupyter or existing event loop:
task = asyncio.create_task(main())
result = await task
```

#### Issue: SSL Certificate Errors

```python
import asyncio


async def main():
    # For development/testing only - never in production
    import ssl

    import aiohttp

    from fivetwenty import AsyncClient, Environment

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with AsyncClient(
        token=token,
        environment=Environment.PRACTICE,
        connector=connector,  # Custom connector
    ) as client:
        # This will bypass SSL verification (DANGEROUS)
        pass

asyncio.run(main())
```

#### Issue: Rate Limiting

```python
from fivetwenty.exceptions import TooManyRequests
import asyncio

async def rate_limited_operation(client, operations):
    """Handle rate limiting gracefully."""

    results = []

    for operation in operations:
        try:
            result = await operation(client)
            results.append(result)

        except TooManyRequests as e:
            # Respect the retry-after header
            retry_after = getattr(e, 'retry_after', 60)
            print(f"Rate limited, waiting {retry_after} seconds...")
            await asyncio.sleep(retry_after)

            # Retry the operation
            result = await operation(client)
            results.append(result)

    return results
```

### Mock Testing for Development

Mock testing allows rapid development without API calls:

```python
from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def trading_system_mocks():
    """Comprehensive mocks for trading system testing."""

    with patch("fivetwenty.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Setup realistic mock responses
        mock_client.accounts.list.return_value = [
            # Mock account objects
        ]

        mock_client.orders.post_market_order.return_value = {
            "order_fill_transaction": {"id": "123", "trade_opened_id": "456"},
        }

        yield mock_client

async def test_trading_strategy(trading_system_mocks):
    """Test trading strategy with full mocks."""

    # Your trading strategy can now be tested
    # without any real API calls
    pass
```

## Security Best Practices

### Credential Management

```python
import keyring
from cryptography.fernet import Fernet


class SecureCredentials:
    """Secure credential storage."""

    def __init__(self, service_name: str = "oanda_trading"):
        self.service = service_name

    def store_token(self, token: str, username: str = "default"):
        """Store token securely."""

        # Use system keyring
        keyring.set_password(self.service, username, token)

    def get_token(self, username: str = "default") -> str:
        """Retrieve token securely."""

        token = keyring.get_password(self.service, username)
        if not token:
            raise ValueError("Token not found")

        return token

    def encrypt_config(self, config: dict) -> bytes:
        """Encrypt configuration."""

        key = Fernet.generate_key()
        cipher = Fernet(key)

        config_bytes = json.dumps(config).encode()
        encrypted = cipher.encrypt(config_bytes)

        return encrypted, key
```

## Documentation Standards

### Code Documentation

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_order_with_risk_management(
    client: AsyncClient,
    account_id: str,
    instrument: str,
    units: int,
    stop_loss: Optional[str] = None,
    take_profit: Optional[str] = None
) -> OrderResponse:
    """
    Place an order with comprehensive risk management.

    This function validates the order against risk limits, sets appropriate
    stop losses, and logs all actions for audit purposes.

    Args:
        client: OANDA API client instance
        account_id: Account to place order on
        instrument: Trading instrument (e.g., "EUR_USD")
        units: Position size (positive for buy, negative for sell)
        stop_loss: Optional stop loss price
        take_profit: Optional take profit price

    Returns:
        OrderResponse containing fill transaction details

    Raises:
        ValueError: If order fails risk validation
        FiveTwentyError: If API request fails

    Example:
        >>> order = await place_order_with_risk_management(
        ...     client=client,
        ...     account_id="101-001-1234567-001",
        ...     instrument="EUR_USD",
        ...     units=1000,
        ...     stop_loss="1.0900"
        ... )
        >>> print(f"Order filled at {order.order_fill_transaction.price}")
    """
    # Implementation
    pass
```

## Deployment Checklist


"""Comprehensive module for trading operations."""
Before deploying to production:

- [ ] ✅ All tests passing
- [ ] ✅ Risk limits configured
- [ ] ✅ Stop losses on every trade
- [ ] ✅ Daily loss limits set
- [ ] ✅ Monitoring configured
- [ ] ✅ Alerting enabled
- [ ] ✅ Logging to files
- [ ] ✅ Error recovery tested
- [ ] ✅ Credentials secured
- [ ] ✅ Backup systems ready
- [ ] ✅ Documentation complete
- [ ] ✅ Performance tested
- [ ] ✅ Circuit breakers configured
- [ ] ✅ State persistence enabled
- [ ] ✅ Health checks running

## Documentation Quality Assurance

### Validation Framework

The FiveTwenty project includes a comprehensive documentation validation framework to ensure accuracy and completeness. This framework achieves:

- **100% Model Documentation Accuracy** (66/66 models)
- **100% Endpoint Documentation Accuracy** (39/39 endpoints)

#### Using the Validation Framework
```bash
# Navigate to the docs-tooling directory
cd docs-tooling

# Run all validators with quality gates and reporting
uv run python validation/cli.py run --parallel --gates --report

# Run specific accuracy audits
uv run python validation/cli.py run endpoint-accuracy model-accuracy

# Run common validators during development
uv run python validation/cli.py run links syntax security
```

#### Key Validation Areas


"""Comprehensive module for trading operations."""
**Accuracy Validators:**
- **Endpoint Documentation**: Validates that all documented endpoints match the actual SDK implementation
- **Model Documentation**: Ensures all model fields are correctly documented with proper types and requirements
- **SDK Method Names**: Checks for deprecated method patterns and ensures current SDK methods are used

**Quality Validators:**
- **Link Validation**: Verifies all internal and external links work correctly
- **Syntax Validation**: Ensures markdown syntax is correct and consistent
- **Security Scanning**: Detects potential security issues in documentation
- **Prose Quality**: Style validation using Vale for professional documentation

#### Integration with Development Workflow
```bash
# Quick validation checks during development
uv run python validation/cli.py run links syntax

# Accuracy audits before commits
uv run python validation/cli.py run endpoint-accuracy model-accuracy

# Full validation suite before major releases
uv run python validation/cli.py run --parallel --gates --report
```

**Pre-commit Hook Example:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: docs-validation
        name: Documentation Validation
        entry: uv run python docs-tooling/validation/cli.py run links syntax security
        language: system
        pass_filenames: false
```

#### Benefits for Production Systems

- **Prevents Documentation Debt**: Automatic detection of outdated documentation
- **Ensures API Accuracy**: Documentation always matches actual implementation
- **Maintains Quality Standards**: Consistent formatting and style across all docs
- **Reduces Support Load**: Accurate documentation means fewer user issues

The validation framework is particularly important for trading systems where accurate documentation can prevent costly implementation mistakes.

## Summary

Following these best practices will help you build robust, production-ready trading systems with FiveTwenty. Remember:

1. **Always prioritize risk management**
2. **Test thoroughly in practice first**
3. **Monitor everything in production**
4. **Have recovery plans ready**
5. **Keep your code maintainable**

## Next Steps

After implementing these best practices:

- **Deploy to production**: Follow [How-to Deploy SDK to Production](../how-to-guides/production-deployment/index.md)
- **Monitor your system**: Set up comprehensive logging and alerting
- **Scale your operations**: Consider horizontal scaling patterns
- **Continuous improvement**: Regular performance and risk reviews

## Related Resources

**Understanding-Oriented:**
- **[SDK Architecture](sdk-architecture.md)**: Core design principles and patterns
- **[Error Handling](error-handling.md)**: Comprehensive error management strategies
- **[Forex Trading Concepts](forex-trading-concepts.md)**: Domain knowledge for trading systems

**Task-Oriented:**
- **[How-to Guides](../how-to-guides/index.md)**: Specific implementation solutions
- **[Tutorials](../tutorials/index.md)**: Complete learning projects

**Reference:**
- **[API Documentation](../api-reference/index.md)**: Complete method specifications
- **[Configuration Reference](configuration.md)**: All configuration options