# FiveTwenty

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://nimbleox.github.io/fivetwenty/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/NimbleOx/fivetwenty/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

FiveTwenty is a typed Python client for OANDA's v20 REST API. It provides an
`AsyncClient` for asyncio applications and a synchronous `Client` for blocking
request code.

## What the SDK handles

- Seven endpoint groups: accounts, instruments, orders, trades, positions, pricing and transactions.
- Pydantic models with Python field names, `Decimal` financial values and native `datetime` attributes.
- Response dictionaries that retain OANDA's envelope keys, such as `account` and `lastTransactionID`.
- Connection reuse, structured API errors and retries for eligible read requests.
- Pricing and transaction streams, plus a pricing helper with configurable reconnection.

The SDK does not automatically retry writes. If an order request times out, its
outcome may be unknown; check account or transaction state before submitting again.
The [API reference](https://nimbleox.github.io/fivetwenty/api-reference/) describes
method signatures, return types and account-specific restrictions.

## Quick start

Install Python 3.10 or later, then install the SDK. `python-dotenv` is optional; this
example uses it to load a local `.env` file.

```bash
pip install fivetwenty python-dotenv
```

With uv, use `uv add fivetwenty python-dotenv` instead.

Create `.env` with credentials for your OANDA v20 practice account, and keep it out
of version control:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

This example reads the configured account and current pricing. It does not place
an order. Printed prices are a snapshot, not a promised execution price.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        if client.config.environment != Environment.PRACTICE:
            message = "Use a practice account for this example"
            raise ValueError(message)
        response = await client.accounts.get_account_summary(client.account_id)
        account = response["account"]
        print(f"Balance: {account.balance} {account.currency}")

        response_prices = await client.pricing.get_pricing(
            client.account_id, instruments=["EUR_USD"]
        )
        for price in response_prices["prices"]:
            print(f"{price.instrument}: {price.closeout_bid} / {price.closeout_ask}")


if __name__ == "__main__":
    asyncio.run(main())
```


The SDK reads process environment variables; it does not load `.env` files itself.
For an order lifecycle, continue with
[Your first trade](https://nimbleox.github.io/fivetwenty/tutorials/getting-started/first-trade/).

## Beta compatibility

The public API may change as this beta library is aligned with OANDA v20. Review
changes before upgrading.

- Collection methods generally return an envelope. For example, read
  `response["orders"]` after `get_orders()` and retain `response["lastTransactionID"]`
  when tracking account state. `get_accounts()` returns its account list directly.
- Omit a dependent-order update argument to leave that order unchanged; pass
  `None` to cancel it. Partial dictionaries use OANDA's camelCase field names.
- `max_retries=3` allows the initial request plus three retries for eligible reads.
  `max_retries=0` still sends the initial request. Writes are sent once.
- `datetime_format` controls the wire format. Parsed model attributes remain Python
  datetimes; Python represents microseconds, not OANDA's full nanosecond precision.

## Requirements and development

The direct runtime dependencies are HTTPX >= 0.26.0 and Pydantic >= 2.7.0.
See the [testing guide](https://nimbleox.github.io/fivetwenty/contributing/testing-guide/)
for supported Python versions, coverage checks and opt-in practice-account tests.

## License

MIT License - see LICENSE file for details.

## Disclaimer

**This library is provided for educational and demonstration purposes only.**

Trading financial instruments involves substantial risk of loss. Test against a practice account before risking real capital; you are solely responsible for your trading decisions, and the authors accept no liability for losses incurred through use of this software. Past performance is not indicative of future results.

**USE AT YOUR OWN RISK.**
