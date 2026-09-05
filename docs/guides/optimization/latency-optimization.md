# Measure latency before tuning

Separate three quantities: time to obtain an HTTP response, time to process that
response, and time until a trading outcome is known. They are not interchangeable.
A fast rejection is not a fast fill.

## Measure a read request

Use a monotonic clock for elapsed duration. This helper reuses a caller-owned client
and reports a result only after the request succeeds:

```python
from time import perf_counter

from fivetwenty import AsyncClient


async def measure_summary(client: AsyncClient) -> float:
    started = perf_counter()
    result = await client.accounts.get_account_summary(client.account_id)
    elapsed = perf_counter() - started
    print(f"Summary received in {elapsed:.3f}s; transaction {result['lastTransactionID']}")
    return elapsed
```

If retries are enabled, this duration includes their delays. Record that setting
with the measurement. Use multiple samples and report failures and percentiles;
a single fast response does not establish expected latency.

## Set timeouts to bound waiting

A shorter timeout does not make the server execute faster. It changes how long the
client waits. Start with the library defaults, measure your network and workload,
and choose a timeout consistent with the application's failure policy.

For a timed-out write, the server may already have acted. Reducing write timeouts
can increase the number of outcomes that need reconciliation. Do not retry an order
just because it exceeded a latency target.

## Reduce avoidable work

Reuse connections, request only the instruments and candle ranges you need, and
avoid blocking analysis in the event loop. Cache static instrument metadata with a
refresh policy; do not treat rapidly changing margin or pricing as static data.

Validate request shape before submission, but remember that local validation cannot
predict account state at execution time. Concurrent reads are separate requests,
and concurrent writes are not an atomic transaction.

## Observe the full path

Record timestamps for signal creation, request submission, response receipt and
local processing. Use server transaction timestamps to understand server events,
while allowing for local clock differences. Track unknown write outcomes and their
resolution, not just successful response latency.

There is no supported sub-100ms execution guarantee or universal fill-rate target.
See [connection reuse](connection-optimization.md) and
[connection failures](../practical-solutions/handle-connection-failures.md) for the
controls the client actually provides.
