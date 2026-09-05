# FiveTwenty

FiveTwenty is a Python client for OANDA's v20 REST API. Read market data, manage
orders and trades, and follow account activity through async or synchronous code.

The library turns API responses into typed Python models, using `Decimal` for
financial values and `datetime` for timestamps. It also manages HTTP connections,
formats requests and provides structured exceptions when something goes wrong.

## Find what you need

| You want to… | Start here |
|---|---|
| Set up your first connection | [Installation](tutorials/getting-started/installation.md), then [authentication](tutorials/getting-started/authentication.md) |
| Create and close a practice trade | [Your first trade](tutorials/getting-started/first-trade.md) |
| Solve a specific integration problem | [Guides](guides/index.md) |
| Look up a method, parameter or field | [API reference](api-reference/index.md) |
| Run a script or notebook | [Examples](examples.md) |
| Contribute to the library | [Contributing](contributing/index.md) |

## Start with a read-only request

You need Python 3.10 or later and an OANDA v20 practice account. In a uv project,
install FiveTwenty and the optional `python-dotenv` helper:

```bash
uv add fivetwenty python-dotenv
```

With pip, use `python -m pip install fivetwenty python-dotenv` instead.

Create a `.env` file in your project directory. Replace the placeholders with your
practice token and account ID, and add `.env` to `.gitignore`:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

Save the following as `quickstart.py` alongside `.env`. The script uses
`AsyncClient` to read your balance and a price snapshot for EUR/USD. It checks that
the client is configured for practice and does not place an order.

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

Run `uv run quickstart.py`, or `python quickstart.py` if you installed with pip.
The `load_dotenv()` call loads the file into your process environment; FiveTwenty
reads those environment variables to configure the client.

### Understand the response

`response` is a dictionary. Its `"account"` entry contains an `AccountSummary` model,
so `account.balance` gives you a `Decimal` and `account.currency` gives you the
account's currency. The dictionary also retains metadata such as
`response["lastTransactionID"]`, which you can use to track account changes.

The pricing response follows the same pattern: `response_prices["prices"]`
contains a list of price models. See [models and response shapes](api-reference/models/index.md)
for more about working with model attributes and API field names.

For synchronous code, use `Client`. The [async and sync guide](guides/understanding/async-vs-sync.md)
shows both clients and explains how to close connections and streams.

## API scope and compatibility

FiveTwenty covers accounts, instruments, orders, trades, positions, pricing and
transactions. The instruments and order features you can use depend on your OANDA
account. OANDA validates each request against the account's permissions and settings.

The SDK retries eligible read requests after selected failures and sends write
requests once. If a write times out, check account or transaction state before
submitting it again. The [client reference](api-reference/client.md) explains retry
settings, timeouts and datetime formats; the [connection guide](guides/practical-solutions/handle-connection-failures.md)
covers recovery.

While FiveTwenty is below version 1.0, minor releases may include breaking changes.
Read the [changelog](https://github.com/NimbleOx/fivetwenty/blob/main/CHANGELOG.md)
for migration notes before upgrading.
