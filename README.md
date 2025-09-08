# OANDA Python SDK

A simple, elegant Python client for OANDA's REST API v20.

## Features

- **Async-first** with sync wrapper
- **Type-safe** with full mypy support  
- **Minimal dependencies** (only httpx + pydantic)
- **Production ready** with retries, rate limiting, and error handling
- **Real-time streaming** with automatic reconnection
- **Decimal precision** for financial calculations

## Quick Start

### Installation

```bash
pip install oanda
```

### Async Usage (Recommended)

```python
import asyncio
from decimal import Decimal
from oanda import AsyncClient, Environment

async def main():
    async with AsyncClient(
        token="your-token-here",
        environment=Environment.PRACTICE
    ) as client:
        
        # Get accounts
        accounts = await client.accounts.list()
        account_id = accounts[0].id
        
        # Create a market order
        order = await client.orders.create_market(
            account_id=account_id,
            instrument="EUR_USD",
            units=1000,
            stop_loss=Decimal("1.0900"),
            take_profit=Decimal("1.1100"),
        )
        print(f"Order created: {order.last_transaction_id}")
        
        # Stream prices for 30 seconds
        import time
        end_time = time.time() + 30
        
        async for price in client.pricing.stream(account_id, ["EUR_USD"]):
            if hasattr(price, 'instrument'):  # It's a price update
                spread = price.spread
                print(f"{price.instrument}: {price.closeout_bid}/{price.closeout_ask} (spread: {spread})")
            
            if time.time() > end_time:
                break

if __name__ == "__main__":
    asyncio.run(main())
```

### Sync Usage

```python
from decimal import Decimal
from oanda import Client, Environment

with Client(token="your-token-here", environment=Environment.PRACTICE) as client:
    # Get accounts
    accounts = client.accounts.list()
    account_id = accounts[0].id
    
    # Create a market order  
    order = client.orders.create_market(
        account_id=account_id,
        instrument="EUR_USD", 
        units=1000,
        stop_loss=Decimal("1.0900")
    )
    
    # Stream prices (blocking iterator)
    count = 0
    for price in client.pricing.stream_iter(account_id, ["EUR_USD"]):
        if hasattr(price, 'instrument'):
            print(f"{price.instrument}: {price.closeout_bid}/{price.closeout_ask}")
        
        count += 1
        if count > 10:
            break  # Stop after 10 updates
```

## Configuration

### Environment Variables

- `OANDA_TOKEN`: Your API token
- `OANDA_SDK_USER_AGENT_EXTRA`: Additional user agent info

### Advanced Configuration

```python
from oanda import AsyncClient, Environment
import httpx

client = AsyncClient(
    token="your-token",
    environment=Environment.LIVE,  # Use live trading
    timeout=60.0,  # 60 second timeout
    max_retries=5,  # Retry failed requests
    
    # Custom HTTP client with proxy
    transport=httpx.AsyncClient(
        proxies="http://proxy.example.com:8080",
        verify="/path/to/ca-bundle.crt"
    ),
    
    # Custom logging
    logger=your_logger,
)
```

## Error Handling

```python
from oanda import OandaError, StreamStall

try:
    order = await client.orders.create_market(...)
except OandaError as e:
    print(f"API Error: {e}")
    print(f"Status: {e.status}")
    print(f"Code: {e.code}")  
    print(f"Request ID: {e.request_id}")
    
    if e.retryable:
        # Can retry this operation
        pass

try:
    async for price in client.pricing.stream(...):
        process(price)
except StreamStall:
    # Reconnect and try again
    pass
```

## Requirements

- Python 3.10+
- httpx >= 0.25.0
- pydantic >= 2.5.0

## License

MIT License - see LICENSE file for details.