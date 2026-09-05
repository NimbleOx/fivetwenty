# Create, inspect and replace orders

An order is a request for an action; a trade is exposure created by a fill.
Keep their IDs separate and inspect returned transactions before updating your
application's state.

## Choose an entry interface

Convenience methods cover market, limit, stop and market-if-touched orders. For
fields not exposed by a convenience method, build the corresponding request model
and call `post_order()`. For example, `post_market_order()` has no `time_in_force`
argument; use `MarketOrderRequest` for IOC or other supported model fields.

This helper creates a practice limit order using caller-selected units and price:

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import LimitOrderRequest


async def create_limit(client: AsyncClient, units: Decimal, price: Decimal) -> str:
    if client.config.environment != Environment.PRACTICE:
        message = "Use a practice account for this example"
        raise ValueError(message)
    request = LimitOrderRequest(instrument="EUR_USD", units=units, price=price)
    response = await client.orders.post_order(client.account_id, request)
    created = response.get("orderCreateTransaction")
    if created is None:
        message = "No creation transaction returned"
        raise RuntimeError(message)
    return created.id
```

A valid model is not assurance of server acceptance. Check instrument metadata and
account restrictions. A marketable limit order can fill immediately, so creation
does not mean it is still pending.

## Inspect the lifecycle

Use `get_order(account_id, order_id)` for a known order and `get_pending_orders()`
for currently pending orders. `get_orders()` returns an envelope and applies its
filters and count; it is not an unbounded account-history dump.

```python
from fivetwenty import AsyncClient


async def inspect_order(client: AsyncClient, order_id: str) -> None:
    response = await client.orders.get_order(client.account_id, order_id)
    order = response["order"]
    print(order.id, order.type, order.state)
    print(response["lastTransactionID"])
```

Use transaction history to explain creation, fills, cancellation and rejection.
`REJECTED` is not an `OrderState` value in this SDK; rejection is represented through
error responses and transaction types.

## Replace or cancel a pending order

`put_order()` replaces an order through a cancel-and-create operation. Supply a
complete replacement request and capture the new creation ID; do not keep treating
the old ID as the active order. The response may contain cancellation, creation,
fill or reissue details.

`cancel_order()` requests cancellation of a pending order. It does not close a
trade that was already opened by a fill. Read the final order state when a
cancellation races with execution.

## Attach and update dependent orders

Use request-model `*_on_fill` fields to describe dependent orders for a newly opened
trade. For an existing trade, use `put_trade_orders()`. Omitting an argument leaves
that dependent order unchanged; `None` cancels it. The helper accepts model objects
or partial dictionaries with OANDA field names.

See [stop-loss management](implement-stop-loss-strategies.md) for exact examples.
Placing related independent orders concurrently does not make them a server-side
bracket or an atomic group.

## Track outcomes, not just HTTP success

Persist identifiers and relevant response transactions. `lastTransactionID` is an
account transaction cursor, not necessarily the order ID. `RequestID` identifies
an HTTP request, and client extension IDs have their own meaning.

If the response is lost, resolve the [unknown write outcome](handle-connection-failures.md#unknown-write-outcomes)
before resubmitting. The SDK deliberately avoids automatic write retries.
