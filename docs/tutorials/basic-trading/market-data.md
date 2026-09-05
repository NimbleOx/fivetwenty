# Read quotes and completed candles

This lesson reads market data without placing orders. Quotes describe current
pricing; candles summarize intervals. Choose the representation that matches your
calculation and keep the observation time with the value.

## Inspect a pricing snapshot

```python
from fivetwenty import AsyncClient


async def show_quote(client: AsyncClient, instrument: str) -> None:
    response = await client.pricing.get_pricing(
        client.account_id, instruments=[instrument]
    )
    for price in response["prices"]:
        if not price.bids or not price.asks:
            print(f"No bid/ask buckets for {price.instrument}")
            continue
        bid = price.bids[0].price
        ask = price.asks[0].price
        print(f"{price.instrument} at {price.time}: bid={bid}, ask={ask}")
        print(f"Quoted spread: {ask - bid}")
```

Bid and ask buckets include liquidity at their quoted levels. The first bucket is
useful for a small-size quote calculation, but it does not guarantee the fill price
for an arbitrary order size. `closeout_bid` and `closeout_ask` are separate closeout
prices; they are not substitutes for entry liquidity buckets.

An empty response or missing buckets needs an explicit application decision. Check
price status and freshness before using a quote for an order calculation.

## Select completed midpoint candles

```python
from decimal import Decimal

from fivetwenty import AsyncClient


async def completed_closes(
    client: AsyncClient, instrument: str, count: int = 50
) -> list[Decimal]:
    response = await client.instruments.get_instrument_candles(
        instrument, granularity="M5", price="M", count=count
    )
    return [
        candle.mid.c
        for candle in response["candles"]
        if candle.complete and candle.mid is not None
    ]
```

The requested count is not a promise that this filtered list has that many values.
The latest candle may be incomplete; a component is present only when returned by
the API. Check the resulting length before calculating an indicator.

A candle's `volume` counts prices created in its interval, not exchange-traded
units. Midpoint candles do not include the bid/ask spread needed for an execution
cost model. See OANDA's [candlestick definition](https://developer.oanda.com/rest-live-v20/instrument-df/#Candlestick).

## Query a time range

Use `from_time` and `to_time` with timezone-aware datetimes for a bounded interval.
Omit `count` when both boundaries are provided. `count` can be combined with one
boundary and is limited by the API to 5,000 candles per request.

When paging forward, use the last returned candle time as the next `from_time`
and `include_first=False` to avoid repeating that boundary candle. Stop if no new
data arrives. Daily and weekly alignment settings affect interval boundaries; do
not assume that a daily candle always begins at midnight UTC.

For ongoing sampled prices, see [streaming data](../streaming-data.md). Next,
[inspect trades and positions](position-management.md).
