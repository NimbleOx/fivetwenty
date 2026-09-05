# Update dependent orders on a trade

Dynamic management changes an existing trade's protection as application conditions
change. OANDA can maintain a native trailing stop on the server; a custom policy
that recalculates distances or prices runs in your application.

## Attach a native trailing stop

This helper updates a known practice trade. The distance is in price units, not
pips; validate it against the instrument's trailing-stop constraints.

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import TrailingStopLossDetails


async def set_trailing_stop(
    client: AsyncClient, trade_id: str, distance: Decimal
) -> None:
    if client.config.environment != Environment.PRACTICE:
        message = "This example requires practice mode"
        raise ValueError(message)
    if distance <= 0:
        message = "Trailing distance must be positive"
        raise ValueError(message)
    response = await client.trades.put_trade_orders(
        client.account_id,
        trade_id,
        trailing_stop_loss=TrailingStopLossDetails(distance=distance),
    )
    print(f"Update response transaction: {response['lastTransactionID']}")
```

The server adjusts a native trailing stop as the price moves favorably. Your
process does not implement each adjustment. That does not guarantee an execution
price or make the trade risk-free. Confirm the resulting dependent order on the
trade before reporting that the requested protection is present.

## Replace a fixed stop

Pass `StopLossDetails(price=...)` to `put_trade_orders(stop_loss=...)` for an absolute
stop price. Omitting other dependent-order arguments leaves them unchanged; passing
`None` explicitly requests cancellation. See the
[update semantics guide](../../guides/practical-solutions/implement-stop-loss-strategies.md).

Moving a stop to an entry price does not eliminate spread, financing, commissions
or slippage. Widening a distance can increase potential loss. A volatility-based
calculation is an application policy, not a property guaranteed by the SDK.

## Avoid repeated or conflicting updates

Read the trade and its current dependent orders, calculate a proposed change, and
compare it with the current value after applying instrument precision. Do not
submit an identical replacement for every price update. Record the response and
reconcile before the next change if an update times out.

A trade can close while your update is being prepared. Treat that as a state change
to resolve, not an instruction to open a replacement trade. If multiple workers can
manage the same trade, define ownership or coordination so their updates do not
continually replace each other.

## Scale exposure explicitly

Adding units changes total exposure; partial closure changes remaining units. Neither
operation has a guaranteed advantage over a single entry or exit. For trade-specific
partial closure, use `close_trade(..., units="...")` with a positive quantity.
Instrument-level reducing orders need a separate design: `REDUCE_ONLY` constrains
the position effect but does not target a particular trade ID.

Continue with [order combinations](order-strategies.md).
