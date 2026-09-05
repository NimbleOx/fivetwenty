# Configure authentication

Load your practice-account credentials, then read an account summary to verify
access. This tutorial makes a read-only request.

## Obtain a token and account ID

Use an OANDA account with v20 API access. In the account portal, open **Manage API
Access** and follow OANDA's instructions to generate or manage a personal access
token. Copy the account ID from the account you intend to use.

OANDA's [authentication documentation](https://developer.oanda.com/rest-live-v20/authentication/)
describes token access and revocation. A token can authorize access to multiple
accounts; verify access to each account you plan to use.

## Store local configuration

Install the optional loader if needed: `uv add python-dotenv`. Create `.env` in the
application directory and add it to `.gitignore`:

```bash
FIVETWENTY_OANDA_TOKEN=your-practice-token
FIVETWENTY_OANDA_ACCOUNT=your-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice
```

Replace the placeholders with your practice credentials. Keep real tokens out of
source code, issues and shared notebooks. FiveTwenty reads environment variables;
the `load_dotenv()` call below loads your `.env` file into that environment.

## Verify account access

Save this as `verify_access.py` in the same directory as `.env`:

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

Run `uv run verify_access.py`, or `python verify_access.py` in an activated virtual
environment. A successful run prints a configuration summary, the account currency
and the last transaction ID. That confirms the token can read this account's summary.

The practice check uses the client's resolved configuration. By default,
`load_dotenv()` keeps environment variables that are already set. If the client
uses different values from your `.env` file, check your shell or process settings.

## Other configuration sources

You can also pass credentials directly to the client constructor or use
`AccountConfig` for a named, reusable configuration. The [configuration guide](../../guides/understanding/configuration.md)
explains which source takes priority and how to use custom environment-variable
prefixes and configuration aliases.

Tokens use Pydantic's `SecretStr` to mask them when you display configuration, and
SDK request logs redact Authorization headers. Keep the `.env` file private and
avoid extracting or printing the token in your own logs.

## If the check fails

- If client creation fails, check for missing or malformed configuration values.
- For a 401 or 403 response, check the token, resolved environment and account access.
- For a transport error, check the network, proxy, TLS settings and request timeout.

The [authentication troubleshooting guide](../../guides/practical-solutions/handle-connection-failures.md#authentication-troubleshooting)
walks through these checks without exposing credentials in logs.

Next, [create and close a practice trade](first-trade.md).
