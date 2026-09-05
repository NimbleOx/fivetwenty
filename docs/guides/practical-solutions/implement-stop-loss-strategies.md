# Manage stop-loss orders

A dependent stop-loss order belongs to a trade. Its parameters express an intended
exit condition, not a universal maximum-loss guarantee. Price gaps, execution
conditions, costs and account rules matter; guaranteed stop losses are a distinct
feature with their own restrictions.

## Choose when to attach the order

For a newly opened trade, put `stop_loss_on_fill=StopLossDetails(...)` in its entry
request model. This sends the dependent-order instruction with the entry request.
For an existing trade, call `put_trade_orders()` using that trade's ID.

The convenience `post_market_order(stop_loss=...)` accepts an absolute price. For a
distance, trailing stop or other supported settings, use a request model. Check the
[order-model reference](../../api-reference/models/order-models.md) for those fields.

## Update an existing trade

The following helper submits the caller's chosen absolute stop price. It makes no
assumption about which price is appropriate for the strategy:

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StopLossDetails


async def set_stop(client: AsyncClient, trade_id: str, price: Decimal) -> None:
    if client.config.environment != Environment.PRACTICE:
        message = "Use a practice account for this example"
        raise ValueError(message)
    response = await client.trades.put_trade_orders(
        client.account_id, trade_id, stop_loss=StopLossDetails(price=price)
    )
    print(response["lastTransactionID"])
```

Re-read the trade to verify the resulting dependent order. Modifying a local
`StopLossDetails` object does not change the server order.

## Omission, partial updates and cancellation

OANDA distinguishes an omitted field from JSON `null`. FiveTwenty preserves that
distinction in `put_trade_orders()`:

| Argument | Effect |
|---|---|
| No `stop_loss` argument | Leave the existing stop-loss unchanged |
| `stop_loss=StopLossDetails(price=...)` | Create or update from the supplied model |
| `stop_loss={"price": "1.05"}` | Send a partial update using OANDA field names |
| `stop_loss=None` | Cancel the dependent stop-loss |

The example price is illustrative. Partial dictionaries use camelCase names such
as `timeInForce` and `gtdTime`; the endpoint validates the result. Cancelling one
dependent order does not request changes to other omitted dependent-order types.
These semantics follow [OANDA's dependent-order endpoint](https://developer.oanda.com/rest-live-v20/trade-ep/#SetDependentOrders).

## Distances and instrument precision

A pip is `10 ** instrument.pip_location` price units. Do not hardcode `0.0001` for
all instruments. Use instrument metadata to check price precision, minimum distance
and trailing/guaranteed-stop restrictions. Price precision and unit precision are
separate constraints.

A trailing stop takes a distance and adjusts its trigger as the market moves in the
favorable direction. An ATR or percentage rule is application logic: it calculates
a proposed distance, then submits an ordinary API request. The SDK does not compute
or validate a trading strategy's risk budget.

## Failure and recovery

A dependent-order update may be rejected, cancelled or filled according to current
state. Inspect response transactions and re-read the trade. After a timeout, verify
the actual dependent order before retrying. A move to entry price can still leave
costs or slippage; avoid describing it as a risk-free trade.
