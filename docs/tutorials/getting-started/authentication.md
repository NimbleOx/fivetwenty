# Configure authentication

By the end of this tutorial, you will have loaded practice-account credentials and
verified that the token can access the configured account. No orders are submitted.

## Obtain a token and account ID

Use an OANDA account with v20 API access. In the account portal, open **Manage API
Access** and follow OANDA's instructions to generate or manage a personal access
token. Copy the account ID from the account you intend to use.

OANDA's [authentication documentation](https://developer.oanda.com/rest-live-v20/authentication/)
describes token access and revocation. A token can authorize access to multiple
accounts; access to one account does not prove access to another.

## Store local configuration

Install the optional loader if needed: `uv add python-dotenv`. Create `.env` in the
application directory and add it to `.gitignore`:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

These are placeholders. Do not paste a real token into source code, an issue or a
shared notebook. FiveTwenty reads process variables; `load_dotenv()` loads the file
into that environment for this example.

## Verify account access

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        if client.config.environment != Environment.PRACTICE:
            message = "This tutorial requires a practice account"
            raise ValueError(message)
        response = await client.accounts.get_account_summary(client.account_id)
        account = response["account"]
        print(client.config.summary())
        print(f"Account currency: {account.currency}")
        print(f"Last transaction: {response['lastTransactionID']}")


if __name__ == "__main__":
    asyncio.run(main())
```

A successful response establishes access at the time of the request. It does not
place a trade or verify every account-specific feature. The environment check uses
the resolved configuration, which may differ from the `.env` file if the process
already had variables set.

## Other configuration sources

Pass direct credentials when you want explicit constructor arguments. Use
`AccountConfig` for a named, reusable configuration. The [configuration guide](../../guides/understanding/configuration.md)
explains source precedence, required aliases and custom prefixes.

`SecretStr` masks configuration display and SDK request logs redact Authorization
headers. Those features do not encrypt `.env` files or protect a token you extract
and print yourself.

## If the check fails

- A construction error usually means required values are missing or malformed.
- A 401/403 response requires checking the token, resolved environment and account access.
- A transport error points to the network, proxy, TLS settings or request timeout.

Do not infer authentication from token length alone. See
[authentication troubleshooting](../../guides/practical-solutions/handle-connection-failures.md#authentication-troubleshooting)
for a diagnostic sequence that keeps credentials out of logs.

Next, [create and close a practice trade](first-trade.md).
