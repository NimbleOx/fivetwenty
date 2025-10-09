# FiveTwenty

A comprehensive, production-ready Python client for the OANDA v20 REST API.

## Features

- **Async-first** with sync wrapper
- **Type-safe** with mypy strict compliance and comprehensive TypedDict responses
- **Minimal dependencies** (only httpx + pydantic)
- **Robust client** with retries, rate limiting, and comprehensive error handling
- **Complete API coverage** with 100% endpoint implementation (all 7 endpoint groups)

## Quick Start

### Installation

```bash
pip install fivetwenty python-dotenv
```

Or with uv:
```bash
uv add fivetwenty python-dotenv
```

### Configuration

Create a `.env` file with your OANDA credentials:

```bash
FIVETWENTY_OANDA_TOKEN=your-api-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

### Usage

```python
import asyncio
import time
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, InstrumentName

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    # Zero-config client - automatically reads from environment variables
    async with AsyncClient() as client:
        # Get accounts
        accounts = await client.accounts.get_accounts()
        account_id = accounts[0].id

        # Create market order (use Decimal for financial values)
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            stop_loss=Decimal("1.0900"),
            take_profit=Decimal("1.1100"),
        )
        print(f"Order created: {order['lastTransactionID']}")

        # Stream real-time prices for 30 seconds
        end_time = time.time() + 30

        async for price in client.pricing.get_pricing_stream(
            account_id, [InstrumentName.EUR_USD]
        ):
            if isinstance(price, ClientPrice):  # Filter out heartbeats
                spread = price.closeout_ask - price.closeout_bid
                print(f"{price.instrument}: {price.closeout_bid}/{price.closeout_ask} (spread: {spread})")

            if time.time() > end_time:
                break


if __name__ == "__main__":
    asyncio.run(main())
```

## Requirements

- Python 3.10+
- httpx >= 0.25.0
- pydantic >= 2.5.0

## API Coverage

### OANDA v20 API Implementation

- **Account Management**: Complete account operations, configuration updates, and change polling
- **Order Operations**: Full order lifecycle - create, list, get, cancel, replace, and client extensions
- **Trade Management**: Complete trade operations - list, get, close, modify, and dependent orders
- **Position Management**: Full position operations - list, get, close by instrument
- **Pricing & Streaming**: Real-time pricing, reliable streaming, and historical candles
- **Transaction History**: Complete audit trail, streaming, and incremental updates

## License

MIT License - see LICENSE file for details.

## Disclaimer

**This library is provided for educational and demonstration purposes only.**

Trading financial instruments involves substantial risk of loss. The examples and code provided in this library are for demonstration purposes only and should not be used for actual trading without thorough testing and understanding of the risks involved.

- Past performance is not indicative of future results
- You are solely responsible for any trading decisions and their consequences
- The authors and contributors accept no liability for any financial losses incurred through use of this software
- Always test thoroughly with paper trading accounts before risking real capital
- Consult with qualified financial advisors before making investment decisions

**USE AT YOUR OWN RISK.**
