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
        # ============================================
        # This is one of the MOST IMPORTANT concepts in OANDA trading!
        # Many beginners confuse trades and positions.
        #
        # TRADE = Individual fill from a single order execution
        # - Each order you place creates one trade (when filled)
        # - Has its own unique ID
        # - Tracks its own entry price, P/L, financing
        # - Can be closed independently
        #
        # POSITION = Aggregate of ALL trades for an instrument
        # - One position per instrument (EUR/USD, GBP/USD, etc.)
        # - Sums up all open trades for that instrument
        # - Tracks net exposure (long or short)
        # - Closing a position closes ALL its trades
        #
        # Example:
        # - Place 3 separate EUR/USD buy orders of 1000 units each
        # - Creates 3 separate trades (trade_1, trade_2, trade_3)
        # - Shows as 1 EUR/USD position with 3000 units total
        # - Each trade can have different entry prices
        # - Average position price = weighted average of all trade prices
        print("\n=== 1. Trades vs Positions ===")

        print("\nKey Differences:")
        print("  Position: Aggregated view of all trades for an instrument")
        print("    - One position per instrument")
        print("    - Shows net exposure (long/short/flat)")
        print("    - Position size = sum of all trade sizes")

        print("\n  Trade: Individual fill from a single order execution")
        print("    - Multiple trades can exist for same instrument")
        print("    - Each has its own entry price and P/L")
        print("    - Can be closed individually (FIFO or specific)")

        print("\n  Example:")
        print("    - Place 3 separate buy orders for EUR/USD")
        print("      → Creates 3 individual trades (1000 units each)")
        print("    - Shows as 1 position (aggregated)")
        print("      → EUR/USD Long: 3000 units total")
        print("    - Close 1 trade:")
        print("      → 2 trades remain, position now 2000 units")

        print("\n  Positions track net exposure, trades track individual entries")
        print("  💡 Use trades for granular control, positions for overall view")

        # Section 2: List all trades
        # ==========================
        # get_trades() retrieves trades based on filters
        # By default, it returns OPEN trades, but you can filter by:
        # - Instrument (specific currency pair)
        # - State (OPEN, CLOSED, CLOSE_WHEN_TRADEABLE)
        # - Trade IDs (specific trades)
        # - Count (pagination)
        print("\n=== 2. List All Trades ===")

        # Get all trades (defaults to OPEN state)
        all_trades_response = await client.trades.get_trades(account_id=client.account_id)
        all_trades = all_trades_response.get("trades", [])

        print(f"\nTotal trades: {len(all_trades)}")

        # Filter by instrument - useful when you only care about specific pairs
        # Only returns EUR/USD trades
        eur_trades = await client.trades.get_trades(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
        print(f"EUR/USD trades: {len(eur_trades.get('trades', []))}")

        # Filter by state - control which lifecycle state you want
        # TradeStateFilter.OPEN = currently active trades
        # TradeStateFilter.CLOSED = historical closed trades
        # TradeStateFilter.ALL = both open and closed
        open_trades = await client.trades.get_trades(account_id=client.account_id, state=TradeStateFilter.OPEN)
        print(f"Open trades: {len(open_trades.get('trades', []))}")

        # Show first few trades to demonstrate structure
        if all_trades:
            print("\nFirst 3 trades:")
            for trade in all_trades[:3]:
                print(f"\n  Trade {trade.id}:")
                print(f"    Instrument: {trade.instrument}")

                # current_units: May differ from initial_units if partially closed
                print(f"    Units: {trade.current_units}")

                # state: OPEN, CLOSED, or CLOSE_WHEN_TRADEABLE
                print(f"    State: {trade.state}")

                # open_time: When this trade was opened (ISO 8601 format)
                print(f"    Open Time: {trade.open_time}")

        # Section 3: List open trades only
        # ================================
        # get_open_trades() is a convenience method
        # Equivalent to get_trades(state=TradeStateFilter.OPEN)
        # More efficient than filtering closed trades yourself
        print("\n=== 3. Open Trades Only ===")

        open_only = await client.trades.get_open_trades(account_id=client.account_id)
        open_trade_list = open_only.get("trades", [])

        print(f"\nFound {len(open_trade_list)} open trade(s):")
        for trade in open_trade_list[:5]:
            print(f"\n  Trade {trade.id}:")
            print(f"    Instrument: {trade.instrument}")
            print(f"    Units: {trade.current_units}")

            # Entry Price: The price at which this trade was opened
            # This doesn't change (unlike current market price)
            print(f"    Entry Price: {trade.price}")

            # Unrealized P/L: Current profit/loss for this trade
            # = (Current Price - Entry Price) * Units
            # Changes constantly as market moves
            print(f"    Unrealized P/L: {trade.unrealized_pl}")

            # Financing: Rollover/swap charges for holding overnight
            # Positive or negative depending on interest rate differential
            # Accumulates daily at 5pm ET
            print(f"    Financing: {trade.financing}")

        # Section 4: Get specific trade details
        # =====================================
        # get_trade() returns complete details for a single trade
        # More information than what's in the list view
        print("\n=== 4. Trade Details ===")

        # Open a trade first so we have something to examine
        order_response = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        trade_id = None
        if order_response.get("orderFillTransaction") and order_response["orderFillTransaction"].trade_opened:
            # Get the trade ID from the order fill transaction
            trade_id = order_response["orderFillTransaction"].trade_opened.trade_id
            print(f"\nOpened trade: {trade_id}")

            # Fetch full trade details
            # This gives us more fields than the list view
            trade_details = await client.trades.get_trade(account_id=client.account_id, trade_specifier=trade_id)
            trade = trade_details["trade"]

            print("\nTrade Details:")
            print(f"  ID: {trade.id}")
            print(f"  Instrument: {trade.instrument}")
            print(f"  State: {trade.state}")

            # initial_units: Original size when trade was opened
            # Never changes (even after partial closes)
            print(f"  Initial Units: {trade.initial_units}")

            # current_units: Current size (may be less if partially closed)
            # This is what matters for calculating current P/L and margin
            print(f"  Current Units: {trade.current_units}")

            # price: Entry price (weighted average if trade was opened in parts)
            print(f"  Price: {trade.price}")

            # open_time: Timestamp when trade was opened
            print(f"  Open Time: {trade.open_time}")

            # unrealized_pl: Current profit/loss
            print(f"  Unrealized P/L: {trade.unrealized_pl}")

            # margin_used: Capital required for this trade
            # = Units * Price * Margin Rate
            print(f"  Margin Used: {trade.margin_used}")

            # financing: Cumulative rollover charges for this trade
            print(f"  Financing: {trade.financing}")

            # client_extensions: Custom metadata you attached to the trade
            if hasattr(trade, "client_extensions") and trade.client_extensions:
                print(f"  Client Extensions: {trade.client_extensions}")

        # Section 5: Open new trades
        # ==========================
        # Demonstrates opening multiple trades on the same instrument
        # This creates separate trade entries that form one position
        print("\n=== 5. Open New Trades ===")

        print("\nOpening 3 separate trades...")
        print("(Each is an independent trade with its own ID)")
        trade_ids = []

        for i in range(3):
            # Use MarketOrderRequest to attach client extensions
            # Client extensions let you tag trades with metadata
            # Useful for: strategy names, batch IDs, notes, etc.
            order_request = MarketOrderRequest(
                instrument=InstrumentName.EUR_USD,
                units=Decimal("500"),
                clientExtensions=ClientExtensions(
                    id=f"trade-batch-{i + 1}",  # Unique identifier
                    comment=f"Trade {i + 1} of 3",  # Human-readable note
                ),
            )

            order = await client.orders.post_order(account_id=client.account_id, order_request=order_request)

            if order.get("orderFillTransaction") and order["orderFillTransaction"].trade_opened:
                tid = order["orderFillTransaction"].trade_opened.trade_id
                trade_ids.append(tid)
                print(f"  ✅ Trade {tid} opened at {order['orderFillTransaction'].price}")

        print(f"\nCreated {len(trade_ids)} separate trades")
        print("Note: These form a single EUR/USD position but are tracked individually")
        print("      Position size = 500 + 500 + 500 = 1500 units")
        print("      But you can close each trade independently!")

        # Section 6: Close a specific trade
        # =================================
        # close_trade() closes a specific trade by ID
        # This is different from closing a position (which closes ALL trades)
        # Useful for:
        # - Partial position exits
        # - Closing winning trades while keeping losers (or vice versa)
        # - FIFO compliance (close oldest first)
        print("\n=== 6. Close Specific Trade ===")

        if trade_ids:
            close_trade_id = trade_ids[0]
            print(f"\nClosing trade {close_trade_id}...")
            print("(The other 2 trades remain open)")

            # Close this specific trade
            # All units for this trade will be closed
            close_response = await client.trades.close_trade(account_id=client.account_id, trade_specifier=close_trade_id)

            if close_response.get("orderFillTransaction"):
                fill = close_response["orderFillTransaction"]
                print(f"✅ Trade closed at {fill.price}")

                # Realized P/L: The actual profit/loss from this closed trade
                # This is now locked in - added to your account balance
                print(f"Realized P/L: {fill.pl}")

                # Remove from our tracking list
                trade_ids.remove(close_trade_id)

                print(f"\nRemaining trades: {len(trade_ids)}")
                print(f"Position size now: {len(trade_ids) * 500} units")

        # Section 7: Partially close a trade
        # ==================================
        # You can close just PART of a trade's units
        # The trade stays open with reduced size
        # Useful for: scaling out, taking partial profits, risk reduction
        print("\n=== 7. Partial Trade Close ===")

        if trade_ids:
            partial_trade_id = trade_ids[0]
            print(f"\nPartially closing trade {partial_trade_id} (250 of 500 units)...")
            print("(Trade stays open with 250 units remaining)")

            # Specify units parameter to close only part of the trade
            # units as string: "250" means close 250 units
            # Omit units to close entire trade
            partial_close = await client.trades.close_trade(account_id=client.account_id, trade_specifier=partial_trade_id, units="250")

            if partial_close.get("orderFillTransaction"):
                fill = partial_close["orderFillTransaction"]
                print(f"✅ Partial close at {fill.price}")

                # Realized P/L only for the 250 units closed
                print(f"Realized P/L: {fill.pl}")

                # Check remaining units - trade should still be open
                trade_check = await client.trades.get_trade(account_id=client.account_id, trade_specifier=partial_trade_id)
                remaining_units = trade_check["trade"].current_units
                print(f"Remaining units in trade: {remaining_units}")
                print(f"  (initial_units: 500, current_units: {remaining_units})")

        # Section 8: Update trade client extensions
        # =========================================
        # Client extensions are metadata attached to trades
        # You can update them after trade is opened
        # Useful for: adding notes, changing tags, tracking strategy changes
        print("\n=== 8. Update Trade Client Extensions ===")

        if trade_ids:
            update_trade_id = trade_ids[0] if len(trade_ids) > 0 else None
            if update_trade_id:
                print(f"\nUpdating client extensions for trade {update_trade_id}...")

                # Update the metadata without affecting the trade itself
                # Trade size, price, P/L all stay the same
                # Only the custom metadata changes
                extension_response = await client.trades.put_trade_client_extensions(
                    account_id=client.account_id,
                    trade_specifier=update_trade_id,
                    client_extensions={
                        "comment": "Updated: Important trade",  # New comment
                        "tag": "high-priority",  # New tag
                    },
                )

                if extension_response.get("tradeClientExtensionsModifyTransaction"):
                    print("✅ Client extensions updated")
                    print("   (Trade itself unchanged - only metadata updated)")

        # Section 9: Add dependent orders to trade
        # ========================================
        # Dependent orders = Take Profit (TP) and Stop Loss (SL) orders
        # Attached to a specific trade, not the whole position
        # When trade closes (or is closed), dependent orders are cancelled
        # Essential for risk management!
        print("\n=== 9. Add Dependent Orders ===")

        # Open a fresh trade for this example
        new_order = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        if new_order.get("orderFillTransaction") and new_order["orderFillTransaction"].trade_opened:
            new_trade_id = new_order["orderFillTransaction"].trade_opened.trade_id
            entry_price = Decimal(str(new_order["orderFillTransaction"].price))

            print(f"\nAdding TP/SL to trade {new_trade_id}...")
            print(f"Entry price: {entry_price}")

            # Add take profit and stop loss to the trade
            # These orders are "attached" to this specific trade
            dependent_orders = await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=new_trade_id,
                # Take Profit: Automatically close at profit target
                # +50 pips above entry (0.0050 for EUR/USD)
                take_profit=TakeProfitDetails(price=entry_price + Decimal("0.0050")),
                # Stop Loss: Automatically close to limit losses
                # -25 pips below entry (0.0025 for EUR/USD)
                # 2:1 risk/reward ratio (50 pips profit / 25 pips loss)
                stop_loss=StopLossDetails(price=entry_price - Decimal("0.0025")),
            )

            if dependent_orders.get("takeProfitOrderTransaction"):
                tp_txn = dependent_orders["takeProfitOrderTransaction"]
                print(f"✅ Take Profit added: {tp_txn.price}")
                print(f"   (Will close when price reaches {tp_txn.price})")

            if dependent_orders.get("stopLossOrderTransaction"):
                sl_txn = dependent_orders["stopLossOrderTransaction"]
                print(f"✅ Stop Loss added: {sl_txn.price}")
                print(f"   (Will close if price falls to {sl_txn.price})")

            print("\n💡 Risk/Reward:")
            print(f"   Potential profit: 50 pips × {entry_price}")
            print(f"   Potential loss: 25 pips × {entry_price}")
            print("   Ratio: 2:1 (risking 1 to make 2)")

        # Section 10: Modify dependent orders
        # ===================================
        # You can update TP/SL levels after setting them
        # Useful for: trailing stops, adjusting to market conditions
        # Simply call put_trade_orders again with new prices
        print("\n=== 10. Modify Dependent Orders ===")

        if new_trade_id:
            print(f"\nModifying TP/SL for trade {new_trade_id}...")
            print("(Widening targets to give trade more room)")

            # Update to wider targets
            # Old: +50 pips TP, -25 pips SL
            # New: +100 pips TP, -50 pips SL
            # Still 2:1 ratio, but wider targets
            modify_response = await client.trades.put_trade_orders(
                account_id=client.account_id,
                trade_specifier=new_trade_id,
                take_profit=TakeProfitDetails(price=entry_price + Decimal("0.0100")),  # 100 pips
                stop_loss=StopLossDetails(price=entry_price - Decimal("0.0050")),  # 50 pips
            )

            if modify_response.get("takeProfitOrderTransaction"):
                print(f"✅ Take Profit updated to {modify_response['takeProfitOrderTransaction'].price}")

            if modify_response.get("stopLossOrderTransaction"):
                print(f"✅ Stop Loss updated to {modify_response['stopLossOrderTransaction'].price}")

            print("\n💡 Common TP/SL adjustments:")
            print("   - Tighten SL after trade moves in your favor (protect profits)")
            print("   - Widen SL if volatility increases (avoid premature stop out)")
            print("   - Trail SL as price moves (lock in profits)")
            print("   - Adjust TP based on support/resistance levels")

        # Section 11: Track trade lifecycle
        # =================================
        # Trades go through different states during their lifecycle
        # Understanding these states helps with trade management
        print("\n=== 11. Trade Lifecycle Tracking ===")

        print("\nTrade Lifecycle States:")
        print("  1. OPEN - Trade is active")
        print("     - Earning/losing money as market moves")
        print("     - Can be closed or modified")
        print("     - Accruing financing charges overnight")

        print("\n  2. CLOSED - Trade has been fully closed")
        print("     - P/L realized and added to balance")
        print("     - No longer using margin")
        print("     - Historical record only")

        print("\n  3. CLOSE_WHEN_TRADEABLE - Will close when market opens")
        print("     - You requested close while market was closed")
        print("     - Will execute at next market open")
        print("     - Rare state - most markets are 24/5")

        print("\nTracking Metrics:")
        print("  - initial_units: Original size (never changes)")
        print("  - current_units: Remaining size (changes with partial closes)")
        print("  - unrealized_pl: Current profit/loss (changes with price)")
        print("  - financing: Rollover/swap charges (accumulates daily)")
        print("  - margin_used: Capital tied up (scales with current_units)")

        # Get current open trades to show lifecycle
        current_trades = await client.trades.get_open_trades(account_id=client.account_id)
        open_list = current_trades.get("trades", [])

        if open_list:
            print("\nCurrent Open Trades Summary:")
            for trade in open_list[:5]:
                print(f"  Trade {trade.id}: {trade.current_units} units, P/L: {trade.unrealized_pl}")

        # Clean up - close all our test trades
        print("\n\nCleaning up: Closing all EUR/USD trades...")
        print("(Using position close - this closes ALL trades for EUR/USD)")

        # close_position closes ALL trades for an instrument at once
        # More efficient than closing trades one by one
        # This is what most traders use for "flatten everything"
        close_position_response = await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

        if close_position_response.get("longOrderFillTransaction"):
            print("✅ All trades closed")
            print("   (Position is now flat - 0 units)")

    print("\n✅ Trade management example completed!")
    print("\n📚 Key Takeaways:")
    print("   • Trades = individual entries, Positions = aggregated view")
    print("   • You can close trades individually or as a position")
    print("   • Partial closes reduce trade size without fully closing")
    print("   • Client extensions help organize and track trades")
    print("   • Dependent orders (TP/SL) are attached to specific trades")
    print("   • Always use TP/SL for risk management!")


if __name__ == "__main__":
    asyncio.run(main())
