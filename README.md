# FiveTwenty

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://nimbleox.github.io/fivetwenty/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/NimbleOx/fivetwenty/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

A Python client for the OANDA v20 REST API. Async-first with a synchronous wrapper, every monetary value in `Decimal`, and all seven v20 endpoint groups implemented.

## Features

- Async-first `AsyncClient`, plus a thread-backed sync `Client` with the same surface
- mypy strict throughout, with typed models and TypedDict responses
- Two runtime dependencies: httpx and pydantic
- Retries with backoff for safe requests only; writes are never re-sent, so a timed-out order can't be double-submitted
- Price and transaction streaming with stall detection and configurable reconnection
- 130+ Pydantic models and 41 enums, checked against OANDA's published spec by an automated parity pipeline

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

## API coverage

All seven OANDA v20 endpoint groups:

- **Accounts**: account details, summary, instruments, configuration, change polling
- **Instruments**: candles, order book and position book snapshots
- **Orders**: create (market, limit, stop, market-if-touched), list, get, cancel, replace, client extensions
- **Trades**: list, get, close, client extensions, dependent take-profit/stop-loss orders
- **Positions**: list, get, close by instrument
- **Pricing**: current prices, streaming, account-scoped candles, latest candles
- **Transactions**: history by time or ID range, single lookup, streaming

## License

MIT License - see LICENSE file for details.

## Disclaimer

**This library is provided for educational and demonstration purposes only.**

Trading financial instruments involves substantial risk of loss. Test against a practice account before risking real capital; you are solely responsible for your trading decisions, and the authors accept no liability for losses incurred through use of this software. Past performance is not indicative of future results.

**USE AT YOUR OWN RISK.**
