# Configure and verify live access

This guide verifies configuration and account access with a read-only request.
It does not enable an automatic trading loop or choose a position size.

## Supply the intended configuration

Use a distinct alias and secret-store entry for live access. Pass explicit
credentials or an `AccountConfig` with `Environment.LIVE`; do not change private
fields on an existing practice client. Review the
[configuration precedence rules](../understanding/configuration.md#configuration-priority).

```python
import asyncio
import os

from pydantic import SecretStr

from fivetwenty import AccountConfig, AsyncClient, Environment


async def verify_live_access() -> None:
    config = AccountConfig(
        alias="live_monitor",
        token=SecretStr(os.environ["LIVE_FIVETWENTY_OANDA_TOKEN"]),
        account_id=SecretStr(os.environ["LIVE_FIVETWENTY_OANDA_ACCOUNT"]),
        environment=Environment.LIVE,
    )
    async with AsyncClient(config=config, max_retries=0) as client:
        response = await client.accounts.get_account_summary(client.account_id)
        account = response["account"]
        print(config.summary(), account.currency)
        print(f"Open trades: {account.open_trade_count}")


if __name__ == "__main__":
    asyncio.run(verify_live_access())
```

This makes one account-summary request and prints no token. A successful response
establishes access at that time; it does not establish that every instrument or
order type is available, or that the account can accept a proposed order.

## Before the application can submit orders

Give the operator a way to verify the account and environment. Establish ownership
of orders/trades, an audit of submitted actions, and a process for resolving a
write whose response was lost. The SDK does not enforce strategy risk limits or
provide a live-trading confirmation dialog.

Practice testing and backtesting answer different questions. Neither establishes
future live execution or profitability. Use OANDA's current account-specific rules
and instrument metadata for the actual deployment.

## Stop new actions before cleaning up

Stopping a Python process does not cancel server-side orders or close trades.
Pause order submission first, identify the resources owned by the application,
then deliberately cancel pending orders or close exposure and verify each result.
Do not cancel another strategy's resources merely because they share an account.

See [order management](manage-orders-effectively.md), [closing exposure](close-positions.md)
and [unknown write outcomes](handle-connection-failures.md#unknown-write-outcomes).

## Troubleshoot access

For 401/403 responses, confirm the resolved host, token and account access. For
throttling or TLS errors, use the [connection-failure guide](handle-connection-failures.md).
Do not print credentials, disable certificate checks, or increase order size as a
way to diagnose access problems.
