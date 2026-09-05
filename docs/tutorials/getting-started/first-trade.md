# Create and close a practice trade

This tutorial submits one market order, identifies the trade it opened, and closes
that trade explicitly. Use a dedicated practice account with no existing orders or
trades and no other process trading on it.

Complete [installation](installation.md) and [authentication](authentication.md)
first. Unlike the account-access check, running this script changes account state.

## Understand the sequence

1. Verify practice mode and an empty account.
2. Read instrument metadata and use its minimum trade size.
3. Submit a market request with `OPEN_ONLY` position-fill behavior.
4. Inspect the fill and capture the opened trade ID.
5. Close that ID and verify the final trade state.

A market request can be rejected or cancelled. The script checks for a fill instead
of assuming execution. It does not close the position by placing an opposite order,
which could open another trade on a hedging account.

## Run the lifecycle

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment
from fivetwenty.models import MarketOrderRequest, OrderPositionFill

load_dotenv()


async def main() -> None:
    async with AsyncClient(max_retries=0) as client:
        if client.config.environment != Environment.PRACTICE:
            message = "This tutorial requires a practice account"
            raise ValueError(message)
        account_id = client.account_id
        pending = await client.orders.get_pending_orders(account_id)
        opened = await client.trades.get_open_trades(account_id)
        if pending["orders"] or opened["trades"]:
            message = "Use an empty, dedicated practice account"
            raise ValueError(message)

        instruments = await client.accounts.get_account_instruments(
            account_id, instruments=["EUR_USD"]
        )
        if not instruments["instruments"]:
            message = "EUR_USD is unavailable for this account"
            raise ValueError(message)
        instrument = instruments["instruments"][0]
        request = MarketOrderRequest(
            instrument=instrument.name,
            units=instrument.minimum_trade_size,
            positionFill=OrderPositionFill.OPEN_ONLY,
        )
        response = await client.orders.post_order(account_id, request)
        fill = response.get("orderFillTransaction")
        if fill is None or fill.trade_opened is None:
            message = "No opened trade returned; inspect the response and account"
            raise RuntimeError(message)
        trade_id = fill.trade_opened.trade_id
        try:
            print(f"Opened trade {trade_id} at {fill.price}")
            trade_response = await client.trades.get_trade(account_id, trade_id)
            print(f"Current units: {trade_response['trade'].current_units}")
        finally:
            close_response = await client.trades.close_trade(account_id, trade_id)
            print(f"Close response transaction: {close_response['lastTransactionID']}")

        final = await client.trades.get_trade(account_id, trade_id)
        if final["trade"].state != "CLOSED":
            message = "Trade is not closed; inspect its current state"
            raise RuntimeError(message)
        print(f"Confirmed trade {trade_id} is closed")


if __name__ == "__main__":
    asyncio.run(main())
```

The `finally` block requests closure once the trade ID is known. It cannot guarantee
closure during a network failure, nor recover an ID from a creation response that
was never received. If any write times out, inspect account and transaction state
before running the script again. See [unknown write outcomes](../../guides/practical-solutions/handle-connection-failures.md#unknown-write-outcomes).

Accounts with additional order restrictions may reject this minimal request. Read
the returned code and account configuration rather than weakening the example's
checks or increasing its size.

## What to inspect

`orderCreateTransaction.id`, the opened trade ID and `lastTransactionID` have
different meanings. A fill can contain trade-opening, reduction or closure details;
`OPEN_ONLY` makes the intended position effect explicit here.

The example uses minimum units to demonstrate the API, not to recommend an
investment size. The bid/ask spread, execution price and any applicable costs can
change the practice balance even over a short lifecycle.

Continue with [model and numeric basics](../basic-trading/foundation.md), then
[market data](../basic-trading/market-data.md).
