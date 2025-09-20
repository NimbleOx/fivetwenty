"""
Trade Management Example

This example demonstrates comprehensive trade management using the OANDA Python SDK.
It shows how to:
- List and filter trades
- Get detailed trade information
- Manage trade positions (close, partial close)
- Update client extensions for tracking
- Modify take profit and stop loss orders
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient, Environment, FiveTwentyError
from fivetwenty.models import InstrumentName, TradeStateFilter


async def main() -> None:
    """Demonstrate comprehensive trade management functionality."""

    # Replace with your OANDA API token
    token = "your-api-token-here"

    # Use practice environment for testing
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            # Get account information
            accounts = await client.accounts.get_accounts()
            if not accounts:
                print("No accounts found!")
                return

            account_id = accounts[0].id
            print(f"Using account: {account_id}")

            # === 1. List all open trades ===
            print("\n=== Open Trades ===")
            open_trades = await client.trades.get_open_trades(account_id)

            if open_trades["trades"]:
                for trade in open_trades["trades"]:
                    print(f"Trade {trade['id']}: {trade['instrument']}")
                    print(f"  Units: {trade['currentUnits']}")
                    print(f"  Unrealized P&L: {trade['unrealizedPL']}")

                # === 2. Get detailed information for first trade ===
                first_trade_id = open_trades["trades"][0]["id"]
                print(f"\n=== Trade Details for {first_trade_id} ===")

                trade_details = await client.trades.get_trade(account_id, first_trade_id)
                trade = trade_details["trade"]
                print(f"Instrument: {trade['instrument']}")
                print(f"Open Price: {trade['price']}")
                print(f"Open Time: {trade['openTime']}")
                print(f"Current Units: {trade['currentUnits']}")
                print(f"Realized P&L: {trade['realizedPL']}")
                print(f"Unrealized P&L: {trade['unrealizedPL']}")

                # === 3. Update client extensions for trade tracking ===
                print("\n=== Updating Client Extensions ===")
                extensions = {"id": f"managed_trade_{first_trade_id}", "tag": "example_trade", "comment": f"Trade management example for {trade['instrument']}"}

                result = await client.trades.put_trade_client_extensions(account_id, first_trade_id, client_extensions=extensions, idempotency_key=f"ext-{first_trade_id}")
                print(f"Extensions updated: Transaction {result['lastTransactionID']}")

                # === 4. Add/Update Take Profit and Stop Loss ===
                print("\n=== Managing Dependent Orders ===")
                current_price = float(trade["price"])

                # Calculate reasonable TP/SL levels (example logic)
                if float(trade["currentUnits"]) > 0:  # Long position
                    take_profit_price = f"{current_price + 0.0050:.5f}"  # 50 pips profit
                    stop_loss_price = f"{current_price - 0.0025:.5f}"  # 25 pips loss
                else:  # Short position
                    take_profit_price = f"{current_price - 0.0050:.5f}"  # 50 pips profit
                    stop_loss_price = f"{current_price + 0.0025:.5f}"  # 25 pips loss

                # Update orders
                orders_result = await client.trades.put_trade_orders(account_id, first_trade_id, take_profit={"price": take_profit_price, "timeInForce": "GTC"}, stop_loss={"price": stop_loss_price, "timeInForce": "GTC"}, idempotency_key=f"orders-{first_trade_id}")
                print(f"Orders updated: Transaction {orders_result['lastTransactionID']}")
                print(f"Take Profit: {take_profit_price}")
                print(f"Stop Loss: {stop_loss_price}")

                # === 5. Demonstrate partial close (if trade has enough units) ===
                current_units = int(trade["currentUnits"])
                if abs(current_units) >= 500:  # Only if trade is large enough
                    print("\n=== Partial Trade Closure ===")
                    close_units = str(abs(current_units) // 2)  # Close half

                    close_result = await client.trades.close_trade(account_id, first_trade_id, units=close_units, idempotency_key=f"close-{first_trade_id}-partial")
                    print(f"Partially closed {close_units} units")
                    print(f"Close Transaction: {close_result['lastTransactionID']}")

                    if "orderFillTransaction" in close_result:
                        fill = close_result["orderFillTransaction"]
                        print(f"Fill Price: {fill.get('price', 'N/A')}")
                        print(f"P&L: {fill.get('pl', 'N/A')}")

                # === 6. List all trades with filters ===
                print("\n=== Filtered Trade Listing ===")

                # Get trades for specific instrument
                eur_usd_trades = await client.trades.get_trades(account_id, instrument=InstrumentName("EUR_USD"), count=10)
                print(f"EUR_USD trades: {len(eur_usd_trades['trades'])}")

                # Get all closed trades
                closed_trades = await client.trades.get_trades(account_id, state=TradeStateFilter.CLOSED, count=5)
                print(f"Recent closed trades: {len(closed_trades['trades'])}")

            else:
                print("No open trades found.")
                print("\nTo test trade management:")
                print("1. First create a trade using basic_usage.py")
                print("2. Then run this example to manage the trade")

        except FiveTwentyError as e:
            print(f"OANDA API Error: {e}")
            print(f"Error Code: {e.code}")
            print(f"HTTP Status: {e.status}")
            if e.retryable:
                print("This error is retryable")

        except Exception as e:
            print(f"Unexpected error: {e}")


async def demonstrate_trade_lifecycle() -> None:
    """
    Complete trade lifecycle example: create -> manage -> close.

    This function shows the full lifecycle of a trade from creation to closure.
    """
    token = "your-api-token-here"

    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            accounts = await client.accounts.get_accounts()
            account_id = accounts[0].id

            print("=== Complete Trade Lifecycle Example ===")

            # 1. Create a trade
            print("\n1. Creating trade...")
            order = await client.orders.post_order(
                account_id=account_id,
                instrument=InstrumentName("EUR_USD"),
                units=1000,
                take_profit=Decimal("1.1100"),
                stop_loss=Decimal("1.0900"),
            )
            print(f"Trade created: Order ID {order.last_transaction_id}")

            # Wait a moment for trade to appear
            await asyncio.sleep(1)

            # 2. Find our new trade
            print("\n2. Finding new trade...")
            open_trades = await client.trades.get_open_trades(account_id)
            new_trade = None

            for trade in open_trades["trades"]:
                if trade["instrument"] == "EUR_USD":
                    new_trade = trade
                    break

            if not new_trade:
                print("Could not find the new trade")
                return

            trade_id = new_trade["id"]
            print(f"Found trade: {trade_id}")

            # 3. Update client extensions
            print("\n3. Adding tracking information...")
            await client.trades.put_trade_client_extensions(account_id, trade_id, client_extensions={"id": "lifecycle_example", "tag": "demo", "comment": "Complete lifecycle example trade"})
            print("Client extensions added")

            # 4. Modify the stop loss (tighten it)
            print("\n4. Tightening stop loss...")
            current_price = float(new_trade["price"])
            new_stop_loss = f"{current_price - 0.0015:.5f}"  # Tighter stop

            await client.trades.put_trade_orders(account_id, trade_id, stop_loss={"price": new_stop_loss, "timeInForce": "GTC"})
            print(f"Stop loss updated to: {new_stop_loss}")

            # 5. Close the trade completely
            print("\n5. Closing trade...")
            close_result = await client.trades.close_trade(account_id, trade_id, idempotency_key=f"close-lifecycle-{trade_id}")
            print(f"Trade closed: Transaction {close_result['lastTransactionID']}")

            if "orderFillTransaction" in close_result:
                fill = close_result["orderFillTransaction"]
                print(f"Close price: {fill.get('price', 'N/A')}")
                print(f"Final P&L: {fill.get('pl', 'N/A')}")

            print("\n=== Trade Lifecycle Complete ===")

        except FiveTwentyError as e:
            print(f"Error during lifecycle: {e}")


if __name__ == "__main__":
    print("OANDA Trade Management Example")
    print("=" * 50)
    print()
    print("Make sure to:")
    print("1. Replace 'your-api-token-here' with your actual OANDA API token")
    print("2. Have some existing trades in your practice account")
    print()

    # Run the main trade management example
    asyncio.run(main())

    print("\n" + "=" * 50)
    print("Would you like to see the complete lifecycle example? (y/n)")
    response = input().strip().lower()

    if response == "y":
        print("\nRunning complete lifecycle example...")
        asyncio.run(demonstrate_trade_lifecycle())
