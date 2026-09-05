# Keep stream processing bounded

A price consumer that falls behind acts on old information. Measure queue age and
processing time before changing buffer sizes or adding worker tasks.

## Choose a retention policy

| Data | Useful policy |
|---|---|
| Current prices for a dashboard | Keep the latest record per instrument |
| A rolling indicator window | Keep a bounded history with an explicit sampling rule |
| Transactions used to reconstruct account state | Persist IDs and reconcile gaps through history |

Increasing a buffer may delay the point at which it fills while making its oldest
records less useful. OANDA's pricing stream is sampled; see
[streaming semantics](../trading-concepts/streaming.md) before treating it as a tick archive.

## Retain a bounded price history

The following helper collects a finite number of price records. It filters
heartbeats, retains at most 100 prices, and closes the stream on early exit:

```python
from collections import deque
from contextlib import aclosing

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


async def collect_prices(client: AsyncClient, count: int = 10) -> list[ClientPrice]:
    if count < 1:
        message = "count must be positive"
        raise ValueError(message)
    history: deque[ClientPrice] = deque(maxlen=100)
    stream = client.pricing.get_pricing_stream(client.account_id, ["EUR_USD"])
    received = 0
    async with aclosing(stream):
        async for record in stream:
            if isinstance(record, ClientPrice):
                history.append(record)
                received += 1
                if received >= count:
                    break
    return list(history)
```

A record limit is not a wall-clock deadline: a quiet or closed market may produce
heartbeats without prices. Wrap the helper with `asyncio.wait_for` when the task also
needs a time limit.

## Keep slow work off the read path

Avoid blocking file writes, synchronous HTTP calls and expensive calculations in
the stream loop. Use a bounded work queue and a fixed number of consumers. Decide
whether a full queue blocks, replaces an older price or stops processing; do not
silently drop transaction records.

The synchronous pricing iterator already drops the oldest queued records when its
1,024-record queue fills. Its behavior suits current-price consumers, not lossless
capture. The async interfaces give your application control over processing but do
not eliminate network buffers or prevent data loss during a disconnect.

## Measure what matters

Track receipt-to-processing delay, queue length, discarded records, stream restarts
and time since the last record. Distinguish missing prices from missing heartbeats.
A low average callback duration can hide occasional long stalls, so record tail
latencies as well.
