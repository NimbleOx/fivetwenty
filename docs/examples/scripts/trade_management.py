#!/usr/bin/env python3
"""
Trade Management Example

Demonstrates trade operations including:
- Listing all and open trades
- Trade details and lifecycle
- Closing trades
- Trade client extensions and dependent orders
- Trade vs Position differences
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import ClientExtensions, InstrumentName, MarketOrderRequest, StopLossDetails, TakeProfitDetails, TradeStateFilter


async def main() -> None:
    """Trade management operations example."""

    async with AsyncClient() as client:
        # Section 1: Understanding trades vs positions
        print("\n=== 1. Trades vs Positions ===")

        print("\nKey Differences:")
        print("  Position: Aggregated view of all trades for an instrument")
        print("  Trade: Individual fill from a single order execution")
        print("\n  Example:")
        print("    - Place 3 separate buy orders for EUR/USD")
        print("    - Creates 3 individual trades")
        print("    - Shows as 1 position (aggregated)")
        print("\n  Positions track net exposure, trades track individual entries")

        # Section 2: List all trades
        print("\n=== 2. List All Trades ===")

        all_trades_response = await client.trades.get_trades(account_id=client.account_id)
        all_trades = all_trades_response.get("trades", [])

        print(f"\nTotal trades: {len(all_trades)}")

        # Filter by instrument
        eur_trades = await client.trades.get_trades(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
        print(f"EUR/USD trades: {len(eur_trades.get('trades', []))}")

        # Filter by state
        open_trades = await client.trades.get_trades(account_id=client.account_id, state=TradeStateFilter.OPEN)
        print(f"Open trades: {len(open_trades.get('trades', []))}")

        # Show first few trades
        if all_trades:
            print("\nFirst 3 trades:")
            for trade in all_trades[:3]:
                print(f"\n  Trade {trade.id}:")
                print(f"    Instrument: {trade.instrument}")
                print(f"    Units: {trade.current_units}")
                print(f"    State: {trade.state}")
                print(f"    Open Time: {trade.open_time}")

        # Section 3: List open trades only
        print("\n=== 3. Open Trades Only ===")

        open_only = await client.trades.get_open_trades(account_id=client.account_id)
        open_trade_list = open_only.get("trades", [])

        print(f"\nFound {len(open_trade_list)} open trade(s):")
        for trade in open_trade_list[:5]:
            print(f"\n  Trade {trade.id}:")
            print(f"    Instrument: {trade.instrument}")
            print(f"    Units: {trade.current_units}")
            print(f"    Entry Price: {trade.price}")
            print(f"    Unrealized P/L: {trade.unrealized_pl}")
            print(f"    Financing: {trade.financing}")

        # Section 4: Get specific trade details
        print("\n=== 4. Trade Details ===")

        # Open a trade first
        order_response = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        trade_id = None
        if order_response.order_fill_transaction and order_response.order_fill_transaction.trade_opened:
            trade_id = order_response.order_fill_transaction.trade_opened.trade_id
            print(f"\nOpened trade: {trade_id}")

            # Get full trade details
            trade_details = await client.trades.get_trade(account_id=client.account_id, trade_specifier=trade_id)
            trade = trade_details["trade"]

            print("\nTrade Details:")
            print(f"  ID: {trade.id}")
            print(f"  Instrument: {trade.instrument}")
            print(f"  State: {trade.state}")
            print(f"  Initial Units: {trade.initial_units}")
            print(f"  Current Units: {trade.current_units}")
            print(f"  Price: {trade.price}")
            print(f"  Open Time: {trade.open_time}")
            print(f"  Unrealized P/L: {trade.unrealized_pl}")
            print(f"  Margin Used: {trade.margin_used}")
            print(f"  Financing: {trade.financing}")
            if hasattr(trade, "client_extensions") and trade.client_extensions:
                print(f"  Client Extensions: {trade.client_extensions}")

        # Section 5: Open new trades
        print("\n=== 5. Open New Trades ===")

        print("\nOpening 3 separate trades...")
        trade_ids = []

        for i in range(3):
            order_request = MarketOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("500"), clientExtensions=ClientExtensions(id=f"trade-batch-{i + 1}", comment=f"Trade {i + 1} of 3"))
            order = await client.orders.post_order(account_id=client.account_id, order_request=order_request)
            if order.order_fill_transaction and order.order_fill_transaction.trade_opened:
                tid = order.order_fill_transaction.trade_opened.trade_id
                trade_ids.append(tid)
                print(f"  ✅ Trade {tid} opened at {order.order_fill_transaction.price}")

        print(f"\nCreated {len(trade_ids)} separate trades")
        print("Note: These form a single EUR/USD position but are tracked individually")

        # Section 6: Close a specific trade
        print("\n=== 6. Close Specific Trade ===")

        if trade_ids:
            close_trade_id = trade_ids[0]
            print(f"\nClosing trade {close_trade_id}...")

            close_response = await client.trades.close_trade(account_id=client.account_id, trade_specifier=close_trade_id)

            if close_response.get("orderFillTransaction"):
                fill = close_response["orderFillTransaction"]
                print(f"✅ Trade closed at {fill.price}")
                print(f"Realized P/L: {fill.pl}")
                trade_ids.remove(close_trade_id)

        # Section 7: Partially close a trade
        print("\n=== 7. Partial Trade Close ===")

        if trade_ids:
            partial_trade_id = trade_ids[0]
            print(f"\nPartially closing trade {partial_trade_id} (250 of 500 units)...")

            partial_close = await client.trades.close_trade(account_id=client.account_id, trade_specifier=partial_trade_id, units="250")

            if partial_close.get("orderFillTransaction"):
                fill = partial_close["orderFillTransaction"]
                print(f"✅ Partial close at {fill.price}")
                print(f"Realized P/L: {fill.pl}")

                # Check remaining units
                trade_check = await client.trades.get_trade(account_id=client.account_id, trade_specifier=partial_trade_id)
                remaining_units = trade_check["trade"].current_units
                print(f"Remaining units in trade: {remaining_units}")

        # Section 8: Update trade client extensions
        print("\n=== 8. Update Trade Client Extensions ===")

        if trade_ids:
            update_trade_id = trade_ids[0] if len(trade_ids) > 0 else None
            if update_trade_id:
                print(f"\nUpdating client extensions for trade {update_trade_id}...")

                extension_response = await client.trades.put_trade_client_extensions(account_id=client.account_id, trade_specifier=update_trade_id, client_extensions={"comment": "Updated: Important trade", "tag": "high-priority"})

                if extension_response.get("tradeClientExtensionsModifyTransaction"):
                    print("✅ Client extensions updated")

        # Section 9: Add dependent orders to trade
        print("\n=== 9. Add Dependent Orders ===")

        # Open a fresh trade for this example
        new_order = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        if new_order.order_fill_transaction and new_order.order_fill_transaction.trade_opened:
            new_trade_id = new_order.order_fill_transaction.trade_opened.trade_id
            entry_price = Decimal(str(new_order.order_fill_transaction.price))

            print(f"\nAdding TP/SL to trade {new_trade_id}...")

            # Add take profit and stop loss
            dependent_orders = await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=new_trade_id,
                take_profit=TakeProfitDetails(price=entry_price + Decimal("0.0050")),  # 50 pips profit
                stop_loss=StopLossDetails(price=entry_price - Decimal("0.0025")),  # 25 pips loss
            )

            if dependent_orders.get("takeProfitOrderTransaction"):
                tp_txn = dependent_orders["takeProfitOrderTransaction"]
                print(f"✅ Take Profit added: {tp_txn.price}")

            if dependent_orders.get("stopLossOrderTransaction"):
                sl_txn = dependent_orders["stopLossOrderTransaction"]
                print(f"✅ Stop Loss added: {sl_txn.price}")

        # Section 10: Modify dependent orders
        print("\n=== 10. Modify Dependent Orders ===")

        if new_trade_id:
            print(f"\nModifying TP/SL for trade {new_trade_id}...")

            # Update to wider targets
            modify_response = await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=new_trade_id,
                take_profit=TakeProfitDetails(price=entry_price + Decimal("0.0100")),  # 100 pips profit
                stop_loss=StopLossDetails(price=entry_price - Decimal("0.0050")),  # 50 pips loss
            )

            if modify_response.get("takeProfitOrderTransaction"):
                print(f"✅ Take Profit updated to {modify_response['takeProfitOrderTransaction'].price}")

            if modify_response.get("stopLossOrderTransaction"):
                print(f"✅ Stop Loss updated to {modify_response['stopLossOrderTransaction'].price}")

        # Section 11: Track trade lifecycle
        print("\n=== 11. Trade Lifecycle Tracking ===")

        print("\nTrade Lifecycle States:")
        print("  1. OPEN - Trade is active")
        print("  2. CLOSED - Trade has been fully closed")
        print("  3. CLOSE_WHEN_TRADEABLE - Will close when market opens")

        print("\nTracking Metrics:")
        print("  - initial_units: Original size")
        print("  - current_units: Remaining size (after partial closes)")
        print("  - unrealized_pl: Current profit/loss")
        print("  - financing: Rollover/swap charges")
        print("  - margin_used: Capital tied up")

        # Get current open trades to show lifecycle
        current_trades = await client.trades.get_open_trades(account_id=client.account_id)
        open_list = current_trades.get("trades", [])

        if open_list:
            print("\nCurrent Open Trades Summary:")
            for trade in open_list[:5]:
                print(f"  Trade {trade.id}: {trade.current_units} units, P/L: {trade.unrealized_pl}")

        # Clean up - close all our test trades
        print("\n\nCleaning up: Closing all EUR/USD trades...")
        close_position_response = await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

        if close_position_response.get("longOrderFillTransaction"):
            print("✅ All trades closed")

    print("\n✅ Trade management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
