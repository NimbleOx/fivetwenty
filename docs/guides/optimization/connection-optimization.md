# Reuse connections and bound concurrency

A long-lived client lets HTTPX reuse connections. Creating a new client for every
request repeats connection setup and makes resource ownership harder to follow.
Use a context manager around a group of related operations.

## Reuse one client

This helper performs two reads through an already-open client:

```python
from fivetwenty import AsyncClient


async def read_account_state(client: AsyncClient) -> None:
    account = await client.accounts.get_account_summary(client.account_id)
    orders = await client.orders.get_pending_orders(client.account_id)
    print(account["account"].balance, len(orders["orders"]))
```

Create the client outside the helper when calling it repeatedly. Ordinary reads
and streaming use the same configured HTTPX client, with the appropriate host.

## Bound concurrent reads

Concurrency overlaps network waits; it does not combine requests into an atomic
batch. A semaphore limits simultaneous requests, but does not enforce requests per
second. Add pacing separately if your workload needs a rate limit.

```python
import asyncio

from fivetwenty import AsyncClient


async def read_summaries(client: AsyncClient, account_ids: list[str]) -> None:
    semaphore = asyncio.Semaphore(2)

    async def read_one(account_id: str) -> None:
        async with semaphore:
            result = await client.accounts.get_account_summary(account_id)
            print(account_id, result["account"].balance)

    await asyncio.gather(*(read_one(account_id) for account_id in account_ids))
```

The concurrency value is an example, not a recommended rate for all accounts. If
one read fails, define whether the application should stop or retain other results.
Do not transfer this pattern to coordinated orders while assuming all-or-nothing
execution.

## Configure HTTPX only when measurement calls for it

The default client permits up to 100 connections and keeps up to 20 idle keep-alive
connections. These are pool limits, not a request-rate allowance. For different
pooling, TLS or proxy settings, inject a configured `httpx.AsyncClient`; include the
correct base URL. Closing FiveTwenty also closes that injected client.

OANDA [recommends connection reuse](https://developer.oanda.com/rest-live-v20/best-practices/)
and limiting new connections to two per second and requests on an established
connection to 100 per second. Treat those as published recommendations, not targets
your application must reach. Check the current API guidance and any responses
indicating throttling.

See [latency measurement](latency-optimization.md) before changing timeouts.
