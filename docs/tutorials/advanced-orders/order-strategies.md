# Combine orders and handle partial outcomes

Some relationships are part of an OANDA request, such as a take profit attached on
fill. Other relationships, such as cancelling one independent entry when another
fills, require application coordination. Distinguish these before designing a workflow.

## Include dependent details in an entry request

This constructs a request without submitting it. The values illustrate the model
shape and are not current market levels.

```python
from decimal import Decimal

from fivetwenty.models import (
    MarketOrderRequest,
    StopLossDetails,
    TakeProfitDetails,
)

request = MarketOrderRequest(
    instrument="EUR_USD",
    units=Decimal("1"),
    stopLossOnFill=StopLossDetails(distance=Decimal("0.0020")),
    takeProfitOnFill=TakeProfitDetails(price=Decimal("1.12000")),
)
print(request.model_dump(mode="json", by_alias=True, exclude_unset=True))
```

On-fill details request dependent orders for a trade opened by the fill. Check the
entry's position-fill behavior and resulting trade details: an order that only
reduces existing exposure is different from one that opens a new trade. A successful
response must still be inspected before reporting a filled or protected trade.

## Coordinate independent orders

Two entry requests submitted together remain two requests. One can succeed while
the other fails. Client-side “one cancels the other” logic also has a race: both
orders can fill before either cancellation is accepted.

Track each request's intent, created order ID and subsequent transactions. When an
outcome is unknown, query account state before retrying or compensating. A client
request ID is useful for tracing; it is not a promise of write deduplication.

Use native stop, limit or MIT orders for supported price conditions. More complex
conditions, such as a relationship across instruments, need application logic and
cannot be made atomic by submitting requests with `asyncio.gather()`.

## Reduce or reverse exposure

For partial closure of a known trade, use the trade-close endpoint. Opposite-side
limit orders with `REDUCE_ONLY` can express price-triggered position reductions,
but they act on the instrument position and are not trade-specific exits.

A larger opposite market order can have different effects on hedging and
non-hedging accounts. Do not describe reversal as a universally atomic “close then
open” operation. Choose explicit position-fill behavior, account for possible
partial execution, and inspect the returned trade reductions, closures and openings.

## Measure execution with a defined benchmark

Record the observation timestamp, decision quote, requested size, transaction IDs
and actual fills. Define whether slippage is measured against a bid, ask, midpoint
or another benchmark, and make its sign consistent for buys and sells. The spread
is not automatically an extra slippage charge if the benchmark already uses the
relevant side of the quote.

Keep partial fills and cancellations in the dataset. Aggregate costs in a common
currency with an explicit conversion method. These measurements describe observed
execution; they do not establish future performance.

See [order management](../../guides/practical-solutions/manage-orders-effectively.md)
for create, replace and cancel behavior, and [account management](../account-management.md)
for transaction-based reporting.
