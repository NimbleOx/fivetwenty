# Consume price and transaction streams

The SDK exposes two data streams: sampled instrument prices and account
transactions. Both can contain heartbeat records. This tutorial demonstrates
bounded consumption and cleanup without submitting orders.

## Read one price and close the stream

```python
import asyncio
from contextlib import aclosing

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import ClientPrice

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        if client.config.environment != Environment.PRACTICE:
            message = "Use practice mode for this tutorial"
            raise ValueError(message)
        stream = client.pricing.get_pricing_stream(
            client.account_id, instruments=["EUR_USD"]
        )
        async with aclosing(stream):
            async for record in stream:
                if isinstance(record, ClientPrice):
                    print(f"{record.instrument} at {record.time}")
                    break


if __name__ == "__main__":
    asyncio.run(asyncio.wait_for(main(), timeout=30))
```

`aclosing` releases the stream when iteration ends early. The outer timeout bounds
the whole demonstration; receiving heartbeats alone does not count as receiving a
price. A timeout is possible when no usable price arrives.

Price streaming is sampled, not a record of every tick. OANDA documents at most
four prices per second per instrument and heartbeat messages every five seconds.
Do not use message count as market trade volume. See the
[pricing stream specification](https://developer.oanda.com/rest-live-v20/pricing-ep/#StreamingPrices).

## Consume account transactions

```python
from contextlib import aclosing

from fivetwenty import AsyncClient
from fivetwenty.models import TransactionHeartbeat


async def show_one_transaction(client: AsyncClient) -> None:
    stream = client.transactions.get_transactions_stream(client.account_id)
    async with aclosing(stream):
        async for record in stream:
            if isinstance(record, TransactionHeartbeat):
                continue
            print(f"Transaction {record.id}: {record.type}")
            return
```

The iterator yields transaction models directly, not a dictionary containing a
`transaction` key. This helper can wait indefinitely if only heartbeats arrive; use
an application deadline when that is undesirable.

## Reconnect and reconcile

The basic stream methods do not reconnect automatically. Pricing also provides
`stream_pricing_with_retries()` with retry configuration and connection state. Reconnection restores
a connection; it does not replay missed prices or reconstruct account history.

For transactions, persist the last record your application has successfully applied.
After a gap, use transaction history and account state to reconcile before processing
new records as a continuous ledger. A heartbeat's latest transaction ID is not proof
that your consumer has applied everything through that ID.

## Keep processing bounded

Move slow storage or analysis work into a bounded processing design. Dropping old
prices can be acceptable for a latest-quote display; dropping transactions is
inappropriate for a complete account ledger. Define the policy explicitly.

The synchronous `pricing.stream_iter()` adapter uses a queue of 1,024 records and
drops the oldest record when full. It is therefore unsuitable as a lossless archive.
Close blocking iterators explicitly when stopping early. See
[streaming concepts](../guides/trading-concepts/streaming.md) and
[stream processing](../guides/optimization/streaming-optimization.md).
