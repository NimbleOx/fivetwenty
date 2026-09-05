# Close a trade or position

Use a trade ID when closing one known trade. Use the position endpoint when closing
a specified side of an instrument's aggregate exposure. An opposite market order
can change exposure differently on a hedging account; it is not a reliable
replacement for an explicit close operation.

## Close a known trade

The helper below changes the supplied practice trade and returns the transaction
ID associated with the response. Call it only with an ID your application owns.

```python
from fivetwenty import AsyncClient, Environment


async def close_owned_trade(client: AsyncClient, trade_id: str) -> str:
    if client.config.environment != Environment.PRACTICE:
        message = "Use a practice account for this example"
        raise ValueError(message)
    response = await client.trades.close_trade(client.account_id, trade_id)
    fill = response.get("orderFillTransaction")
    if fill is None:
        message = "No close fill returned; inspect cancellation and account state"
        raise RuntimeError(message)
    return response["lastTransactionID"]
```

Omitting `units` requests a full trade close. For a partial close, pass a positive
numeric string such as `units="10"`, after checking the trade's current size and the
instrument's unit precision. See the [trade reference](../../api-reference/endpoints/trades.md).

## Close an instrument side

Specify the side explicitly. `"ALL"` closes that side, `"NONE"` leaves it alone,
and a positive number requests that many units to close. Short-side close amounts
are positive quantities, even though the open short position has negative units.

```python
from fivetwenty import AsyncClient, Environment


async def close_long_side(client: AsyncClient, instrument: str) -> None:
    if client.config.environment != Environment.PRACTICE:
        message = "Use a practice account for this example"
        raise ValueError(message)
    response = await client.positions.close_position(
        client.account_id, instrument, long_units="ALL", short_units="NONE"
    )
    print(response["lastTransactionID"])
    print(response.get("longOrderFillTransaction"))
```

This action can affect several trades. Inspect the side-specific fill or
cancellation transactions and re-read the position. The accepted parameters follow
[OANDA's position-close endpoint](https://developer.oanda.com/rest-live-v20/position-ep/).

## Verify the result

Check the trade's `state` and `current_units`, or both sides of the position, after
the close. A concurrent process or pending entry order can change exposure again.
Closing exposure does not automatically cancel every unrelated pending entry order.

For multiple instruments, take a snapshot of the intended targets, record each
outcome and verify each remaining position. These are separate requests; there is
no atomic close-all API in the SDK. Stop the strategy from creating new orders
before attempting a controlled shutdown.

## Handle races and failures

A trade may already have closed through a dependent order. Re-read the target when
a close fails instead of assuming the failure left it open. After a timeout,
reconcile state before resubmitting: the first close may already have succeeded.
See [connection failures](handle-connection-failures.md#unknown-write-outcomes).
