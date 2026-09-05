"""Create and explicitly close one trade in an empty, dedicated practice account.

Matches the first-trade tutorial. A lost write response requires reconciliation
before rerunning; the finally block cannot guarantee closure through a network failure.
"""

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

        instruments = await client.accounts.get_account_instruments(account_id, instruments=["EUR_USD"])
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
