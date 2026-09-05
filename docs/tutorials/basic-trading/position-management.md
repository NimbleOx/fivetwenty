# Inspect and manage exposure

An order requests an action, a trade records an individual opened exposure, and a
position aggregates an instrument's exposure. Choose the resource that matches
what your application owns and intends to change.

## Read open trades and positions

```python
from fivetwenty import AsyncClient


async def show_exposure(client: AsyncClient) -> None:
    trades = await client.trades.get_open_trades(client.account_id)
    for trade in trades["trades"]:
        print(f"Trade {trade.id}: {trade.instrument}, units={trade.current_units}")

    positions = await client.positions.get_open_positions(client.account_id)
    for position in positions["positions"]:
        print(
            f"{position.instrument}: long={position.long.units}, "
            f"short={position.short.units}"
        )
```

These are separate reads, so account state can change between them. Do not assume
an atomic snapshot. `get_trades()` is a filtered, paginated history endpoint;
`get_open_trades()` explicitly asks for currently open trades.

On a hedging account, both position sides can contain units. Adding long and short
units gives net exposure; zero net units can still leave two open sides. Keep both
sides when deciding what to close or report.

## Close only the resource you intend

To close one trade, pass its ID to `client.trades.close_trade()`. Omitting `units`
requests full closure; a positive units string requests partial closure. Inspect
the returned transactions and then re-read state if your workflow requires closure
confirmation. See [close positions](../../guides/practical-solutions/close-positions.md)
for helpers and the distinction between trade and position closure.

Placing an opposite market order is not a universal close operation: its effect
depends on the account and `position_fill`. Cancelling a pending order does not
close a trade that has already filled, and closing trades does not remove unrelated
pending entries.

## Manage dependent orders

Use `client.trades.put_trade_orders()` to change a known trade's stop loss, take
profit or trailing stop. Omit a parameter to leave it unchanged, provide details
to create or replace it, and pass `None` to cancel it. Check the response for the
transactions that actually occurred.

A stop order can reduce some exposure to adverse moves, but an ordinary stop does
not establish a guaranteed loss cap. See [dependent order behavior](../../guides/practical-solutions/implement-stop-loss-strategies.md).

Next, [build a signal calculation](strategy-building.md) that can be tested
independently of these account operations.
