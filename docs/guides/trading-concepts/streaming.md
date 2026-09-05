# Pricing and transaction streams

A stream is a long-lived HTTP response containing newline-separated JSON records.
FiveTwenty parses those records and yields models. Pricing and transaction streams
serve different purposes, so their recovery policies should differ too.

## What each stream contains

| Stream | Record types | Purpose |
|---|---|---|
| Pricing | `ClientPrice`, `PricingHeartbeat` | Current account pricing for selected instruments |
| Transactions | Concrete transaction models, `TransactionHeartbeat` | Account events and a last-transaction cursor in heartbeats |

OANDA's pricing stream sends at most four prices per second per instrument and can
omit intermediate prices within each sampling window. Heartbeats are sent every
five seconds. It is not a complete tick feed or a promise that different
connections observe identical updates. See [OANDA's pricing stream specification](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing).

## Basic consumption

Use a type check to distinguish prices from heartbeats, and close the stream when
leaving before its natural end:

```python
from contextlib import aclosing

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


async def read_one_price(client: AsyncClient) -> None:
    stream = client.pricing.get_pricing_stream(client.account_id, ["EUR_USD"])
    async with aclosing(stream):
        async for record in stream:
            if isinstance(record, ClientPrice):
                print(record.instrument, record.time, record.closeout_bid)
                break
```

A heartbeat indicates connection activity, not a new price. The basic methods log
and skip malformed records, so applications that require a complete event history
must still reconcile with the REST API.

## Reconnection is an explicit choice

`get_pricing_stream()` and `get_transactions_stream()` do not automatically reconnect.
`stream_pricing_with_retries()` adds a pricing reconnection policy and yields
`(record, state)` pairs. The first record yielded after connection or reconnection
carries that transition state, even if earlier heartbeats, malformed JSON or
unknown record types were filtered out. Subsequent records carry `CONNECTED`.

`ReconnectionPolicy.max_attempts` counts reconnections after the initial connection.
It is separate from REST `max_retries`. There is no built-in circuit-breaker state
or durable transaction replay service.

## Recover account events

Persist the last transaction ID you have actually processed. After a disconnect,
use history or account changes to recover state. Define how to deduplicate records
and bridge the period between history retrieval and stream resumption. A heartbeat
cursor is useful evidence of server progress, but it does not prove your application
has processed all earlier transactions.

The transaction stream emits bare transaction objects, not an invented
`{"type": "TRANSACTION", "transaction": ...}` envelope. See the
[transaction reference](../../api-reference/endpoints/transactions.md).

## Processing and resource limits

Async iteration integrates with your event loop, but slow work can delay reads and
other tasks. Network buffering still exists. The sync pricing iterator adds a
1,024-record queue and drops the oldest records when full.

Choose a bounded retention policy and measure queue age, failures and discarded
records. See [stream processing](../optimization/streaming-optimization.md) and the
[streaming tutorial](../../tutorials/streaming-data.md).
