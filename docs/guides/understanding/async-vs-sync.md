# Async and sync clients

Choose the client that fits your application's execution model. Both use the same
HTTP and model code for ordinary requests; async does not make an individual
OANDA request execute faster.

| Requirement | Interface |
|---|---|
| Existing asyncio application or concurrent requests | `AsyncClient` |
| Sequential script with blocking calls | `Client` |
| Pricing or transaction async streams | `AsyncClient` |
| Blocking pricing iterator | `Client.pricing.stream_iter()` |

## Async requests

Use `async with` to close the HTTP client even when a request fails. Independent
reads can overlap with `asyncio.gather`; their results are separate snapshots, not
one atomic view of the account.

```python
import asyncio

from fivetwenty import AsyncClient


async def inspect_account(client: AsyncClient) -> None:
    summary, positions = await asyncio.gather(
        client.accounts.get_account_summary(client.account_id),
        client.positions.get_open_positions(client.account_id),
    )
    print(summary["account"].balance)
    print(positions["positions"])
```

Call this helper from an existing `async with AsyncClient()` block after loading
your configuration. In a notebook with an active event loop, use `await`; do not
start a second loop with `asyncio.run()`.

## Synchronous requests

`Client` owns a background event-loop thread. The calling thread waits for each
request and receives its result or exception.

```python
from fivetwenty import Client

with Client() as client:
    response = client.accounts.get_account_summary(client.account_id)
    print(response["account"].balance)
```

Keep creation, use and closure under one owner. Prefer `AsyncClient` for concurrent
work instead of coordinating multiple threads around one synchronous client's
lifecycle. A blocking call in an async function blocks that function's event loop.

## Streaming and early exit

Async streams need explicit closure when you stop before the server does:

```python
from contextlib import aclosing

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


async def show_one_price(client: AsyncClient) -> None:
    stream = client.pricing.get_pricing_stream(client.account_id, ["EUR_USD"])
    async with aclosing(stream):
        async for record in stream:
            if isinstance(record, ClientPrice):
                print(record.closeout_bid)
                break
```

For blocking pricing, use the dedicated iterator and `contextlib.closing`:

```python
from contextlib import closing

from fivetwenty import Client
from fivetwenty.models import ClientPrice

with Client() as client:
    with closing(client.pricing.stream_iter(client.account_id, ["EUR_USD"])) as stream:
        for record in stream:
            if isinstance(record, ClientPrice):
                print(record.closeout_bid)
                break
```

The sync pricing queue retains at most 1,024 records and drops the oldest when a
consumer falls behind. Other async streaming methods do not acquire a synchronous
iterator interface merely by being accessed through `Client`.

## Performance and failures

Measure throughput, queue age and latency in the application you are building.
There is no fixed per-request latency difference or memory budget guaranteed by the
SDK. Network conditions, OANDA processing and your consumer determine the result.

Both clients surface API errors as `FiveTwentyError`. Transport errors and model
validation failures can also propagate. See
[connection failures](../practical-solutions/handle-connection-failures.md) and
[streaming](../trading-concepts/streaming.md) for recovery behavior.
