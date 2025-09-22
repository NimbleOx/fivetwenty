# Testing Guide

Comprehensive testing is essential for maintaining the reliability and security of FiveTwenty. This guide covers our testing strategies, tools, and best practices.

---

## Testing Philosophy

### **Testing Pyramid**

FiveTwenty follows a balanced testing approach:

```
     /\
    /  \          ← Integration Tests (Live API, VCR recorded)
   /____\
  /      \        ← Unit Tests (Fast, isolated, mocked)
 /________\
/          \      ← Static Analysis (Type checking, linting)
```

### **Test Categories**

- **Unit Tests** - Fast, isolated tests with mocked dependencies
- **Integration Tests** - Tests against real OANDA API (recorded with VCR.py)
- **Static Analysis** - Type checking, linting, and code quality
- **Performance Tests** - Memory usage, streaming performance
- **Security Tests** - Credential handling, data validation

---

## Running Tests

### **Basic Test Commands**

```bash
# All tests (unit + integration)
uv run poe test
uv run pytest

# Unit tests only (fast)
uv run poe test-unit
uv run pytest tests/unit/

# Integration tests only (slower, requires credentials)
uv run poe test-integration
uv run pytest tests/integration/

# With coverage report
uv run poe test-cov
uv run pytest --cov=fivetwenty --cov-report=html
```

### **Test Selection**

```bash
# Run specific test file
uv run pytest tests/unit/test_client.py

# Run specific test method
uv run pytest tests/unit/test_client.py::test_client_initialization

# Run tests matching pattern
uv run pytest -k "test_account"

# Run tests with specific marker
uv run pytest -m unit
uv run pytest -m integration
uv run pytest -m streaming
```

### **Test Output Control**

```bash
# Verbose output
uv run pytest -v

# Show local variables on failure
uv run pytest -l

# Stop on first failure
uv run pytest -x

# Run in parallel (if pytest-xdist installed)
uv run pytest -n auto
```

---

## Test Organization

### **Directory Structure**

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── unit/                       # Fast, isolated tests
│   ├── test_client.py         # Client initialization and configuration
│   ├── test_models.py         # Pydantic model validation
│   ├── test_exceptions.py     # Exception handling
│   └── endpoints/             # Endpoint-specific tests
│       ├── test_accounts.py
│       ├── test_orders.py
│       ├── test_trades.py
│       └── test_streaming.py
├── integration/               # Live API tests (VCR recorded)
│   ├── test_accounts_integration.py
│   ├── test_orders_integration.py
│   ├── test_streaming_integration.py
│   └── fixtures/             # VCR cassettes
│       ├── accounts/
│       ├── orders/
│       └── streaming/
└── performance/              # Performance and load tests
    ├── test_streaming_performance.py
    └── test_memory_usage.py
```

### **Test Markers**

Tests are organized with pytest markers:

```python
# Example test markers:
@pytest.mark.unit          # Fast unit tests (default)
@pytest.mark.integration   # Integration tests (requires API credentials)
@pytest.mark.streaming     # Streaming-related tests
@pytest.mark.trading       # Trading operation tests
@pytest.mark.core          # Core functionality tests
@pytest.mark.edge_cases    # Edge case and error condition tests
@pytest.mark.slow          # Slower running tests
@pytest.mark.compliance    # OANDA API compliance tests
def test_example():
    pass
```

---

## Unit Testing

### **Unit Test Principles**

- **Fast execution** - Should run in milliseconds
- **Isolated** - No external dependencies (API, network, files)
- **Deterministic** - Same input always produces same output
- **Focused** - Test one specific behavior per test

### **Mocking HTTP Responses**

```python
from decimal import Decimal

import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

class TestAccountsEndpoint:
    """Unit tests for accounts endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return AsyncClient(token="test-token", environment="practice")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_account_summary_success(self, client):
        """Test successful account summary retrieval."""
        # Mock response data
        mock_response_data = {
            "account": {
                "id": "123-456-789",
                "currency": "USD",
                "balance": "10000.0000",
                "marginAvailable": "10000.0000",
                "marginUsed": "0.0000",
                "marginCloseoutPercent": "0.00000"
            }
        }

        # Mock the HTTP request
        with patch.object(client, '_request') as mock_request:
            mock_response = Mock()
            mock_response.json.return_value = mock_response_data
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            # Execute test
            result = await client.accounts.get_account_summary("123-456-789")

            # Verify behavior
            assert result.id == "123-456-789"
            assert result.currency == "USD"
            assert result.balance == Decimal("10000.0000")

            # Verify HTTP call
            mock_request.assert_called_once_with(
                "GET",
                "/accounts/123-456-789",
                timeout=None
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_account_summary_not_found(self, client):
        """Test account not found error handling."""
        with patch.object(client, '_request') as mock_request:
            # Mock HTTP 404 error
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "errorCode": "ACCOUNT_NOT_EXIST",
                "errorMessage": "The account specified does not exist"
            }

            mock_request.side_effect = httpx.HTTPStatusError(
                message="Not Found",
                request=Mock(),
                response=mock_response
            )

            # Test error handling
            with pytest.raises(FiveTwentyError) as exc_info:
                await client.accounts.get_account_summary("invalid-account")

            # Verify exception details
            assert exc_info.value.error_code == "ACCOUNT_NOT_EXIST"
            assert "account specified does not exist" in exc_info.value.message

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_account_summary_timeout(self, client):
        """Test request timeout handling."""
        with patch.object(client, '_request') as mock_request:
            mock_request.side_effect = httpx.TimeoutException(
                message="Request timed out"
            )

            with pytest.raises(FiveTwentyError) as exc_info:
                await client.accounts.get_account_summary(
                    "123-456-789",
                    timeout=1.0
                )

            assert "timed out" in str(exc_info.value).lower()
```

### **Model Testing**

```python
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError
from fivetwenty.models import Order, OrderRequest

class TestOrderModel:
    """Unit tests for Order model."""

    @pytest.mark.unit
    def test_order_model_validation(self):
        """Test Order model with valid data."""
        order_data = {
            "id": "12345",
            "instrument": "EUR_USD",
            "units": "1000",
            "price": "1.2345",
            "timeInForce": "GTC",
            "createTime": "2024-01-15T10:30:00.000000Z",
            "state": "PENDING"
        }

        order = Order.model_validate(order_data)

        assert order.id == "12345"
        assert order.instrument == "EUR_USD"
        assert order.units == 1000
        assert order.price == Decimal("1.2345")
        assert order.time_in_force == "GTC"
        assert isinstance(order.create_time, datetime)

    @pytest.mark.unit
    def test_order_model_invalid_data(self):
        """Test Order model validation with invalid data."""
        invalid_data = {
            "id": "",  # Empty ID
            "instrument": "INVALID",  # Invalid instrument format
            "units": "not-a-number",  # Invalid units
            "price": "invalid-price"  # Invalid price
        }

        with pytest.raises(ValidationError) as exc_info:
            Order.model_validate(invalid_data)

        errors = exc_info.value.errors()
        assert len(errors) >= 3  # Multiple validation errors

    @pytest.mark.unit
    def test_order_serialization_roundtrip(self):
        """Test Order serialization and deserialization."""
        original_data = {
            "id": "67890",
            "instrument": "GBP_USD",
            "units": "-500",
            "price": "1.3456",
            "timeInForce": "FOK",
            "createTime": "2024-01-15T15:45:30.123456Z"
        }

        # Parse from dict
        order = Order.model_validate(original_data)

        # Serialize back to dict
        serialized = order.model_dump(by_alias=True)

        # Verify roundtrip consistency
        assert serialized["id"] == original_data["id"]
        assert serialized["instrument"] == original_data["instrument"]
        assert serialized["timeInForce"] == original_data["timeInForce"]
```

---

## Integration Testing

### **Integration Test Setup**

Integration tests use real OANDA API calls recorded with VCR.py for reproducibility:

```python
from decimal import Decimal

import pytest
import os
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

@pytest.mark.integration
class TestAccountsIntegration:
    """Integration tests for accounts endpoint."""

    @pytest.fixture
    def client(self):
        """Create client with test credentials."""
        return AsyncClient(
            token=os.environ["TEST_OANDA_TOKEN"],
            account_id=os.environ["TEST_OANDA_ACCOUNT"],
            environment=Environment.PRACTICE  # Always use practice for tests
        )

    @pytest.mark.asyncio
    async def test_get_account_summary_real_api(self, client):
        """Test account summary with real OANDA API."""
        account_id = os.environ["TEST_OANDA_ACCOUNT"]

        async with client:
            # This call will be recorded by VCR on first run
            # Subsequent runs will use the recorded response
            summary = await client.accounts.get_account_summary(account_id)

            # Verify response structure and types
            assert summary.id == account_id
            assert isinstance(summary.balance, Decimal)
            assert summary.currency in ["USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "NZD"]
            assert summary.margin_available >= Decimal("0")
            assert summary.margin_used >= Decimal("0")
            assert summary.open_trade_count >= 0

    @pytest.mark.asyncio
    async def test_account_not_found_real_api(self, client):
        """Test account not found error with real API."""
        async with client:
            with pytest.raises(FiveTwentyError) as exc_info:
                await client.accounts.get_account_summary("999-999-999")

            assert exc_info.value.error_code == "ACCOUNT_NOT_EXIST"
            assert exc_info.value.response.status_code == 404
```

### **VCR.py Configuration**

VCR.py records HTTP interactions for reproducible tests:

```python
# conftest.py
import pytest
import vcr
import os

@pytest.fixture(scope="function")
def vcr_config():
    """Configure VCR for integration tests."""
    return {
        "record_mode": "once",  # Record once, then replay
        "match_on": ["uri", "method"],
        "filter_headers": ["authorization"],  # Remove sensitive headers
        "decode_compressed_response": True,
        "cassette_library_dir": "tests/integration/fixtures/",
    }

@pytest.fixture
def vcr(vcr_config):
    """VCR fixture for recording/replaying HTTP interactions."""
    with vcr.VCR(**vcr_config) as cassette:
        yield cassette

# Usage in test
@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_vcr_recording(client, vcr):
    """Test that records HTTP interaction."""
    with vcr.use_cassette("accounts/get_summary.yaml"):
        summary = await client.accounts.get_account_summary("123-456-789")
        assert summary.id == "123-456-789"
```

### **Environment Variables for Testing**

```bash
# Required for integration tests
export TEST_OANDA_TOKEN="your-practice-token"
export TEST_OANDA_ACCOUNT="your-practice-account-id"
export TEST_OANDA_ENVIRONMENT="practice"

# VCR.py recording mode
export VCR_RECORD_MODE="once"  # once, new_episodes, all, none

# Optional: Enable debug logging for tests
export FIVETWENTY_LOG_LEVEL="DEBUG"
```

---

## Streaming Tests

### **Streaming Unit Tests**

```python
from decimal import Decimal

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall

@pytest.mark.streaming
@pytest.mark.unit
class TestPricingStreaming:
    """Unit tests for pricing streams."""

    @pytest.fixture
    def client(self):
        return AsyncClient(token="test-token", environment="practice")

    @pytest.mark.asyncio
    async def test_stream_pricing_success(self, client):
        """Test successful price streaming."""
        # Mock streaming data
        mock_stream_data = [
            '{"type":"PRICE","instrument":"EUR_USD","time":"2024-01-15T10:30:00Z","bids":[{"price":"1.0850","liquidity":10000}],"asks":[{"price":"1.0851","liquidity":10000}]}',
            '{"type":"HEARTBEAT","time":"2024-01-15T10:30:05Z"}',
            '{"type":"PRICE","instrument":"EUR_USD","time":"2024-01-15T10:30:10Z","bids":[{"price":"1.0852","liquidity":10000}],"asks":[{"price":"1.0853","liquidity":10000}]}'
        ]

        async def mock_stream():
            for data in mock_stream_data:
                yield data

        with patch.object(client.pricing, '_stream_lines', return_value=mock_stream()):
            prices = []
            heartbeats = []

            async for item in client.pricing.stream_pricing("123-456-789", ["EUR_USD"]):
                if hasattr(item, 'instrument'):  # Price
                    prices.append(item)
                else:  # Heartbeat
                    heartbeats.append(item)

                if len(prices) >= 2:  # Stop after collecting test data
                    break

            assert len(prices) == 2
            assert len(heartbeats) == 1
            assert prices[0].instrument == "EUR_USD"
            assert prices[0].bids[0].price == Decimal("1.0850")

    @pytest.mark.asyncio
    async def test_stream_stall_detection(self, client):
        """Test stream stall detection."""
        async def slow_stream():
            # Simulate stalled stream (no data for extended period)
            yield '{"type":"PRICE","instrument":"EUR_USD","time":"2024-01-15T10:30:00Z","bids":[{"price":"1.0850","liquidity":10000}],"asks":[{"price":"1.0851","liquidity":10000}]}'
            await asyncio.sleep(10)  # Simulate stall

        with patch.object(client.pricing, '_stream_lines', return_value=slow_stream()):
            with patch('fivetwenty.endpoints.pricing.HEARTBEAT_TIMEOUT', 1):  # 1 second timeout
                with pytest.raises(StreamStall):
                    async for _ in client.pricing.stream_pricing("123-456-789", ["EUR_USD"]):
                        pass
```

### **Streaming Integration Tests**

```python
@pytest.mark.streaming
@pytest.mark.integration
class TestStreamingIntegration:
    """Integration tests for streaming functionality."""

    @pytest.mark.asyncio
    async def test_real_pricing_stream(self, client):
        """Test real pricing stream with timeout."""
        account_id = os.environ["TEST_OANDA_ACCOUNT"]
        instruments = ["EUR_USD", "GBP_USD"]

        async with client:
            stream_count = 0
            async for item in client.pricing.stream_pricing(account_id, instruments):
                stream_count += 1

                # Verify stream item structure
                if hasattr(item, 'instrument'):  # Price
                    assert item.instrument in instruments
                    assert len(item.bids) > 0
                    assert len(item.asks) > 0
                    assert item.bids[0].price < item.asks[0].price  # Bid < Ask

                # Stop after receiving some data
                if stream_count >= 10:
                    break

            assert stream_count >= 10
```

---

## Test Fixtures

### **Common Fixtures**

```python
# conftest.py
import pytest
import os
from decimal import Decimal
from datetime import datetime
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountSummary, Order, Trade

@pytest.fixture
def test_client():
    """Create test client with mock credentials."""
    return AsyncClient(
        token="test-token-12345",
        environment=Environment.PRACTICE
    )

@pytest.fixture
def integration_client():
    """Create client for integration tests."""
    if not os.environ.get("TEST_OANDA_TOKEN"):
        pytest.skip("Integration tests require TEST_OANDA_TOKEN")

    return AsyncClient(
        token=os.environ["TEST_OANDA_TOKEN"],
        environment=Environment.PRACTICE
    )

@pytest.fixture
def sample_account_summary():
    """Sample account summary for testing."""
    return AccountSummary(
        id="123-456-789",
        currency="USD",
        balance=Decimal("10000.0000"),
        margin_available=Decimal("10000.0000"),
        margin_used=Decimal("0.0000"),
        margin_closeout_percent=Decimal("0.00000"),
        open_trade_count=0,
        open_position_count=0,
        pending_order_count=0,
        hedging_enabled=False,
        last_transaction_id="1000"
    )

@pytest.fixture
def sample_order():
    """Sample order for testing."""
    return Order(
        id="12345",
        instrument="EUR_USD",
        units=1000,
        price=Decimal("1.2345"),
        time_in_force="GTC",
        create_time=datetime.now(),
        state="PENDING",
        type="LIMIT"
    )

@pytest.fixture
def mock_responses():
    """Common mock HTTP responses."""
    return {
        "account_summary": {
            "account": {
                "id": "123-456-789",
                "currency": "USD",
                "balance": "10000.0000",
                "marginAvailable": "10000.0000",
                "marginUsed": "0.0000"
            }
        },
        "orders_list": {
            "orders": [
                {
                    "id": "12345",
                    "instrument": "EUR_USD",
                    "units": "1000",
                    "price": "1.2345",
                    "timeInForce": "GTC",
                    "createTime": "2024-01-15T10:30:00.000000Z",
                    "state": "PENDING",
                    "type": "LIMIT"
                }
            ]
        }
    }
```

---

## Performance Testing

### **Memory Usage Tests**

```python
import pytest
import asyncio
import psutil
import os
from fivetwenty import AsyncClient

@pytest.mark.performance
class TestMemoryUsage:
    """Performance tests for memory usage."""

    @pytest.mark.asyncio
    async def test_streaming_memory_usage(self):
        """Test that streaming doesn't leak memory."""
        if not os.environ.get("TEST_OANDA_TOKEN"):
            pytest.skip("Performance tests require API credentials")

        client = AsyncClient(
            token=os.environ["TEST_OANDA_TOKEN"],
            environment="practice"
        )

        process = psutil.Process()
        initial_memory = process.memory_info().rss

        async with client:
            stream_count = 0
            async for item in client.pricing.stream_pricing("123-456-789", ["EUR_USD"]):
                stream_count += 1

                # Check memory every 100 items
                if stream_count % 100 == 0:
                    current_memory = process.memory_info().rss
                    memory_growth = current_memory - initial_memory

                    # Memory growth should be reasonable (< 50MB)
                    assert memory_growth < 50 * 1024 * 1024, f"Memory growth: {memory_growth / 1024 / 1024:.1f}MB"

                if stream_count >= 1000:
                    break

    @pytest.mark.asyncio
    async def test_concurrent_requests_performance(self):
        """Test performance with concurrent requests."""
        if not os.environ.get("TEST_OANDA_TOKEN"):
            pytest.skip("Performance tests require API credentials")

        client = AsyncClient(
            token=os.environ["TEST_OANDA_TOKEN"],
            environment="practice"
        )

        async with client:
            # Test concurrent account summary requests
            tasks = [
                client.accounts.get_account_summary(os.environ["TEST_OANDA_ACCOUNT"])
                for _ in range(10)
            ]

            start_time = asyncio.get_event_loop().time()
            results = await asyncio.gather(*tasks)
            end_time = asyncio.get_event_loop().time()

            # All requests should succeed
            assert len(results) == 10
            assert all(r.id == os.environ["TEST_OANDA_ACCOUNT"] for r in results)

            # Should complete reasonably quickly (adjust threshold as needed)
            elapsed = end_time - start_time
            assert elapsed < 5.0, f"Concurrent requests took {elapsed:.2f}s"
```

---

## Test Configuration

### **pytest.ini**

```ini
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: mark test as a unit test",
    "integration: mark test as an integration test (requires API credentials)",
    "core: mark test as a core functionality test",
    "streaming: mark test as a streaming-related test",
    "trading: mark test as a trading operation test",
    "edge_cases: mark test as an edge case test",
    "slow: mark test as slow running",
    "compliance: mark test as a compliance test",
    "performance: mark test as a performance test"
]
```

### **Coverage Configuration**

```toml
# pyproject.toml
[tool.coverage.run]
source = ["fivetwenty"]
omit = [
    "*/tests/*",
    "*/examples/*",
    "*/__pycache__/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:"
]
```

---

## Continuous Integration

### **GitHub Actions Test Workflow**

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.10, 3.11, 3.12]

    steps:
    - uses: actions/checkout@v4

    - name: Install uv
      uses: astral-sh/setup-uv@v1
      with:
        version: "latest"

    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}

    - name: Install dependencies
      run: uv sync --dev

    - name: Run unit tests
      run: uv run pytest tests/unit/ -v

    - name: Run integration tests
      run: uv run pytest tests/integration/ -v
      env:
        TEST_OANDA_TOKEN: ${{ secrets.TEST_OANDA_TOKEN }}
        TEST_OANDA_ACCOUNT: ${{ secrets.TEST_OANDA_ACCOUNT }}
        VCR_RECORD_MODE: "none"  # Only use recorded cassettes in CI

    - name: Generate coverage report
      run: uv run pytest --cov=fivetwenty --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

---

This comprehensive testing guide ensures that FiveTwenty maintains high quality, reliability, and security standards through thorough automated testing.