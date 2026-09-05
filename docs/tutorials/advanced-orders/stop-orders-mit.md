# Stop and market-if-touched entry orders

Use a server-side entry order when OANDA's price-trigger behavior matches your
intention. Once accepted, a pending order does not need your process to remain
connected for the server to monitor its trigger. Your application still needs to
track fills, cancellations and expiry.

## Choose the trigger behavior

A stop entry is commonly used to request execution when price reaches a level in
the direction of a move. A market-if-touched (MIT) entry requests execution when its
specified level is touched; trigger direction is established relative to the price
when the order is created. A limit order additionally constrains execution to its
price or better. Triggering an order and filling it are distinct events.

These types can support many strategies; they do not themselves confirm momentum
or predict a reversal. Read OANDA's [order definitions](https://developer.oanda.com/rest-live-v20/order-df/)
for direction, trigger-condition and price-bound behavior.

## Submit a stop request

This helper changes practice account state. The caller supplies a valid instrument,
signed units and trigger price after reading account and instrument constraints.

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopOrderRequest


async def submit_stop(
    client: AsyncClient, instrument: str, units: Decimal, trigger_price: Decimal
) -> str:
    if client.config.environment != Environment.PRACTICE:
        message = "This example requires practice mode"
        raise ValueError(message)
    request = StopOrderRequest(
        instrument=instrument, units=units, price=trigger_price
    )
    response = await client.orders.post_order(client.account_id, request)
    created = response.get("orderCreateTransaction")
    if created is None:
        message = "No creation transaction; inspect the response"
        raise RuntimeError(message)
    return created.id
```

The returned ID identifies the created order; it does not prove the order is still
pending. Inspect the full response for fills or cancellations and query the order
if you need current state. The convenience method `post_stop_order()` offers an
alternative to constructing the request model.

For an MIT request, use `MarketIfTouchedOrderRequest` with the corresponding
instrument, units and price, or `post_market_if_touched_order()`. Check trigger
behavior against the current price before submission.

## Give pending orders a lifecycle

Decide how long the entry should remain valid. With `GTD`, provide a timezone-aware
`gtd_time`; with `GTC`, your application needs an explicit cancellation policy if the
signal becomes stale. An order may fill while a cancellation request is in flight.
Handle that race by examining transactions and current exposure.

When changing the trigger, `put_order()` performs a cancel-and-replace operation.
Track the replacement's ID and both parts of the response. Concurrently submitting
several entries does not make them a single transaction or guarantee a fill sequence.

Continue with [dynamic management](dynamic-management.md) or
[order combinations](order-strategies.md).
