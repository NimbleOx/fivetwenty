# FiveTwenty

FiveTwenty wraps OANDA's v20 REST API for Python. Use `AsyncClient` in an asyncio
application or `Client` for synchronous requests. Financial model attributes use
`Decimal`; timestamps use Python `datetime` objects.

The SDK handles request serialization, response parsing, HTTP connections and
structured API errors. Your application decides when to trade, how to reconcile
uncertain outcomes and how to manage account state.

## Start with a read-only request

Install the SDK and the optional `.env` loader:

```bash
uv add fivetwenty python-dotenv
```

Create a `.env` file with practice-account credentials:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

Keep the file out of version control. Run the following script to read an account
summary and price snapshot:

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


`response["account"]` is an `AccountSummary` model. Its `balance` attribute is a
`Decimal`, while the enclosing response retains OANDA's dictionary keys. See
[models and response shapes](api-reference/models/index.md) for this distinction.

## Choose your next step

| You want to… | Start here |
|---|---|
| Connect and learn the basic workflow | [Installation](tutorials/getting-started/installation.md), then [authentication](tutorials/getting-started/authentication.md) |
| Create and close a practice trade | [Your first trade](tutorials/getting-started/first-trade.md) |
| Solve a specific integration problem | [Guides](guides/index.md) |
| Look up a method, parameter or field | [API reference](api-reference/index.md) |
| Run a script or notebook | [Examples](examples.md) |
| Change the library | [Contributing](contributing/index.md) |

## API scope and compatibility

The library exposes accounts, instruments, orders, trades, positions, pricing and
transactions. Availability of instruments and order features depends on the OANDA
account. A model accepting a request does not establish that OANDA will accept it.

Read requests can retry after selected failures. Writes are not automatically
resubmitted. Basic streams end on failure; the pricing reconnection helper is a
separate method. See [client behavior](api-reference/client.md) and
[connection failures](guides/practical-solutions/handle-connection-failures.md).

This is beta software. The repository's tests and cached specification comparisons
help detect regressions; they do not prove complete equivalence with every live API
behavior. Check the [compatibility notes](https://github.com/NimbleOx/fivetwenty#beta-compatibility)
before upgrading.
