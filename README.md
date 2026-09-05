# FiveTwenty

[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue)](https://nimbleox.github.io/fivetwenty/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/NimbleOx/fivetwenty/blob/main/LICENSE)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

FiveTwenty is a Python client for OANDA's v20 REST API. Use it to read market data,
manage orders and trades, and follow account activity. Choose `AsyncClient` for
asyncio applications or `Client` for synchronous code.

## Features

- Access accounts, instruments, orders, trades, positions, pricing and transactions.
- Work with typed Pydantic models, `Decimal` financial values and Python `datetime` objects.
- Reuse HTTP connections and handle failures with structured exceptions and retries for eligible read requests.
- Stream prices and transactions, with an optional reconnection helper for pricing.

The [documentation](https://nimbleox.github.io/fivetwenty/) includes tutorials,
integration guides and a full API reference.

## Quick start

You need Python 3.10 or later and an OANDA v20 practice account. Install FiveTwenty
and `python-dotenv`, the optional helper used here to load credentials from a file:

```bash
pip install fivetwenty python-dotenv
```

With uv, use `uv add fivetwenty python-dotenv` instead.

Create a `.env` file in your project directory and replace the placeholders with
your [practice token and account ID](https://nimbleox.github.io/fivetwenty/tutorials/getting-started/authentication/).
Add `.env` to `.gitignore` to keep credentials out of version control:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

Save the following as `quickstart.py` in the same directory. It reads your account
balance and a price snapshot for EUR/USD without placing an order. The
`load_dotenv()` call loads `.env`; FiveTwenty then reads the environment variables.

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

Run it with `python quickstart.py`, or `uv run quickstart.py` in a uv project.

Responses combine dictionaries and typed models: `response["account"]` selects the
account model, and `account.balance` reads its `Decimal` balance. Other dictionary
keys, such as `lastTransactionID`, preserve OANDA's response metadata. See
[models and response shapes](https://nimbleox.github.io/fivetwenty/api-reference/models/)
for details.

## Next steps

- [Create and close a practice trade](https://nimbleox.github.io/fivetwenty/tutorials/getting-started/first-trade/).
- [Choose between async and sync clients](https://nimbleox.github.io/fivetwenty/guides/understanding/async-vs-sync/).
- [Browse runnable scripts and notebooks](https://nimbleox.github.io/fivetwenty/examples/).
- [Look up methods, parameters and return types](https://nimbleox.github.io/fivetwenty/api-reference/).

Before submitting orders, read the [error-handling guide](https://nimbleox.github.io/fivetwenty/api-reference/error-handling/).
The SDK sends write requests once. If a request times out, check account or
transaction state before submitting it again: OANDA may already have processed it.

<a id="beta-compatibility"></a>

## Compatibility and upgrades

While FiveTwenty is below version 1.0, minor releases may include breaking changes.
Read the [changelog](https://github.com/NimbleOx/fivetwenty/blob/main/CHANGELOG.md)
before upgrading. It includes migration examples for changes to response types and
dependent-order cancellation.

## Requirements and development

FiveTwenty requires HTTPX >= 0.26.0 and Pydantic >= 2.7.0; the installer supplies both.
See the [testing guide](https://nimbleox.github.io/fivetwenty/contributing/testing-guide/)
for supported Python versions, coverage checks and opt-in practice-account tests.

## License

FiveTwenty is released under the [MIT License](https://github.com/NimbleOx/fivetwenty/blob/main/LICENSE).

## Disclaimer

**This library is provided for educational and demonstration purposes only.**

Trading financial instruments involves substantial risk of loss. Test against a practice account before risking real capital; you are solely responsible for your trading decisions, and the authors accept no liability for losses incurred through use of this software. Past performance is not indicative of future results.

**USE AT YOUR OWN RISK.**
