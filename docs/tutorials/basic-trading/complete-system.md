# Assemble a decision workflow

This final lesson combines a data read, a calculation and a decision preview. It
runs once and submits no orders. Keeping the first integrated workflow finite makes
its inputs and result easy to inspect before adding scheduling or account changes.

## Run a read-only preview

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        if client.config.environment != Environment.PRACTICE:
            message = "Use a practice account for this tutorial"
            raise ValueError(message)
        response = await client.instruments.get_instrument_candles(
            "EUR_USD", granularity="M5", price="M", count=21
        )
        candles = [
            candle for candle in response["candles"]
            if candle.complete and candle.mid is not None
        ]
        closes = [candle.mid.c for candle in candles if candle.mid is not None]
        if len(closes) < 20:
            print("No decision: fewer than 20 completed midpoint candles")
            return
        short_average = sum(closes[-5:], Decimal("0")) / 5
        long_average = sum(closes[-20:], Decimal("0")) / 20
        trades = await client.trades.get_open_trades(client.account_id)
        orders = await client.orders.get_pending_orders(client.account_id)
        print(f"Final candle: {candles[-1].time}")
        print(f"Short average={short_average}; long average={long_average}")
        print(f"Open trades={len(trades['trades'])}; pending orders={len(orders['orders'])}")
        print("Preview complete; no order submitted")


if __name__ == "__main__":
    asyncio.run(main())
```

The moving-average calculation mirrors the [previous lesson](strategy-building.md).
Its values describe this data window; they do not certify a trade. The account
reads occur at different times and may already be outdated when printed.

## Add execution as a separate stage

Before adding a write, define which orders and trades the application owns, how it
sizes requests using instrument and currency data, and what it does with an
unexpected response. Persist the decision's candle timestamp and enough request and
transaction identifiers to reconcile it after a restart.

A useful state progression is: collect inputs, validate freshness and limits,
record intent, submit once, inspect the response, then reconcile account state.
A timeout during submission produces an unknown outcome; it should not take the
workflow straight back to submission. See [connection failures](../../guides/practical-solutions/handle-connection-failures.md#unknown-write-outcomes).

## Add continuous operation deliberately

Scheduling introduces duplicate inputs, overlapping runs and shutdown behavior.
Streaming introduces disconnects and gaps. Multiple workers introduce shared state
and ordering decisions. Test these transitions before connecting the calculation
to continuous account operations.

This lesson does not include durable storage, an execution simulator or a deployed
service. Use the [practice lifecycle](../getting-started/first-trade.md) to study one
write-and-close sequence, [streaming](../streaming-data.md) for connection lifecycle,
and [account management](../account-management.md) for reconciliation inputs.
