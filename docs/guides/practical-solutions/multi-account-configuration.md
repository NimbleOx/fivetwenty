# Configure multiple accounts

Use one configuration and client per account context. Distinct aliases make
application logs and stored state easier to associate with the right account;
they do not change OANDA permissions or account rules.

## Configure prefixes

The loader prepends the prefix exactly as supplied. With `"RESEARCH_"`, set:

```bash
RESEARCH_FIVETWENTY_OANDA_TOKEN=your-practice-token
RESEARCH_FIVETWENTY_OANDA_ACCOUNT=your-research-account-id
RESEARCH_FIVETWENTY_OANDA_ENVIRONMENT=practice

MONITOR_FIVETWENTY_OANDA_TOKEN=your-practice-token
MONITOR_FIVETWENTY_OANDA_ACCOUNT=your-monitor-account-id
MONITOR_FIVETWENTY_OANDA_ENVIRONMENT=practice
```

The generated aliases are `research` and `monitor`. There is no separate environment
variable for the alias. Keep these values in the process environment or load them
from a protected `.env` file before running the example.

## Read both accounts

This script loads each required configuration, verifies practice mode and closes
all created clients even if a read fails:

```python
import asyncio
from contextlib import AsyncExitStack

from dotenv import load_dotenv
from fivetwenty import AccountConfigLoader, AsyncClient, Environment

load_dotenv()


async def main() -> None:
    async with AsyncExitStack() as stack:
        clients: list[AsyncClient] = []
        for prefix in ("RESEARCH_", "MONITOR_"):
            config = AccountConfigLoader.from_env_prefix(prefix)
            if config is None:
                message = f"Missing credentials for {prefix}"
                raise ValueError(message)
            if config.environment != Environment.PRACTICE:
                message = "Use practice accounts for this example"
                raise ValueError(message)
            clients.append(await stack.enter_async_context(AsyncClient(config=config)))
        for client in clients:
            result = await client.accounts.get_account_summary(client.account_id)
            account = result["account"]
            print(client.config.alias, account.balance, account.currency)


if __name__ == "__main__":
    asyncio.run(main())
```

Missing credentials are an error here, rather than permission to fall back to the
default account. A malformed environment or alias can raise local validation errors
instead of returning `None`.

## Keep state separate

Store order IDs, trade IDs and transaction cursors with their account ID. Do not
assume IDs from two accounts identify the same resource. Aggregate balances only
after checking account currencies and choosing an explicit conversion policy.

Separate accounts can organize strategy state, but do not establish compliance
with trading restrictions or eliminate correlated exposure. Use each account's
reported configuration and permissions.

For direct `AccountConfig` construction and JSON files, see
[configuration](../understanding/configuration.md). Closing a client also closes its
injected HTTPX transport; avoid sharing one transport between independently closed
clients.
