# Order types and position effects

Choose an order type for its execution condition, then specify how a fill may
change exposure. An order type alone does not determine whether an existing trade
will be reduced, closed or accompanied by a new trade.

## Entry order types

| Type | Execution condition | SDK convenience method |
|---|---|---|
| Market | Requests immediate execution, subject to time-in-force, liquidity and other constraints | `post_market_order()` |
| Limit | Requests the specified price or better | `post_limit_order()` |
| Stop | Triggers execution when its price condition is reached; the final price can differ | `post_stop_order()` |
| Market-if-touched | Triggers market execution when its touch condition is met; it is not a limit-price guarantee | `post_market_if_touched_order()` |

For precise trigger behavior, price bounds and allowed combinations, use the
[order reference](../../api-reference/endpoints/orders.md) and
[OANDA's order definitions](https://developer.oanda.com/rest-live-v20/order-df/).
A market order can be rejected or cancelled; it does not guarantee a fill.

## Time in force

- `FOK`: fill the requested quantity immediately or cancel.
- `IOC`: execute the available quantity immediately and cancel the remainder.
- `GTC`: remain active until filled or cancelled.
- `GTD`: remain active until the specified expiry, unless filled or cancelled first.
- `GFD`: an OANDA enum value whose support depends on the specific order schema.

Not every order type supports every enum value. In particular, market order
requests use FOK or IOC. For a GTD request, supply an aware `gtd_time`. The enum
reference lists wire values; it does not override an individual model's validation.

## Position-fill behavior

`OrderPositionFill` controls whether fills may open or reduce trades. Its values
are `OPEN_ONLY`, `REDUCE_ONLY`, `REDUCE_FIRST` and `DEFAULT`. The effect of `DEFAULT`
depends on the account's hedging configuration. Use an explicit close endpoint when
your intent is to close a known trade or position side.

The model interface exposes fields that some convenience methods omit:

```python
from decimal import Decimal

from fivetwenty.models import MarketOrderRequest, OrderPositionFill, TimeInForce

request = MarketOrderRequest(
    instrument="EUR_USD",
    units=Decimal("1"),
    timeInForce=TimeInForce.IOC,
    positionFill=OrderPositionFill.OPEN_ONLY,
)
print(request.model_dump(mode="json", by_alias=True, exclude_none=True))
```

This constructs a request without sending it. To submit a request model, call
`client.orders.post_order(account_id, request)` from the configured application.

## Dependent orders

Take-profit, stop-loss, trailing-stop-loss and guaranteed-stop-loss orders attach
to a trade. Request-model `*_on_fill` fields specify them for a newly opened trade;
`put_trade_orders()` manages them on an existing trade. An entry stop order and a
dependent stop-loss order are different schemas and operations.

Guaranteed stops have account-specific availability and restrictions. Ordinary
stop-loss placement does not promise that realized loss will equal a chosen price
distance. See [stop-loss management](../practical-solutions/implement-stop-loss-strategies.md).

## Order state and transactions

The SDK's `OrderState` values are `PENDING`, `FILLED`, `TRIGGERED` and `CANCELLED`.
They are states, not a mandatory sequence every order follows. Rejections are
reported through errors and transaction types rather than an `OrderState.REJECTED`.

A creation response may already include a fill or cancellation. Replacing a pending
order creates a new order ID. Store transaction relationships and re-read the target
when cancellation or replacement races with execution.

See [order management](../practical-solutions/manage-orders-effectively.md) for a
workflow and [advanced-order tutorials](../../tutorials/advanced-orders/index.md) for
focused exercises.
