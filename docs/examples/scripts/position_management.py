#!/usr/bin/env python3
"""
Position Management Example

Demonstrates position operations including:
- Viewing open and all positions
- Position details by instrument
- Closing positions (full and partial)
- Position P/L tracking
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName


async def main() -> None:
    """Position management operations example."""

    async with AsyncClient() as client:
        # Section 1: Get all positions
        # =============================
        # CRITICAL DISTINCTION: Positions vs Trades (see trade_management.py for full explanation)
        #
        # POSITION = Aggregate of all trades for ONE instrument
        # - One position per instrument (EUR/USD, GBP/USD, etc.)
        # - Sums up all open trades for that instrument
        # - Tracks net exposure (long or short)
        # - Has TWO sides: long and short (OANDA uses hedged position model)
        #
        # Why get all positions?
        # - Portfolio overview: See all instruments you're exposed to
        # - Risk management: Understand total exposure across instruments
        # - Rebalancing: Identify over-weighted positions
        # - Dashboard displays: Show complete portfolio status
        #
        # get_positions() returns ALL positions for your account,
        # including those with zero units (closed positions still tracked)
        print("\n=== 1. All Positions ===")

        # Returns dict with "positions" key containing list of Position objects
        # This can be hundreds of positions if you've traded many instruments
        all_positions_response = await client.positions.get_positions(client.account_id)
        all_positions = all_positions_response.get("positions", [])

        print(f"Total positions (all instruments): {len(all_positions)}")

        # Display first 5 positions to avoid overwhelming output
        # In production, you'd filter by instrument or non-zero positions
        for position in all_positions[:5]:  # Show first 5
            print(f"\n  {position.instrument}:")

            # OANDA's hedged position model:
            # You can have BOTH long and short positions on the same instrument simultaneously
            # This is different from many brokers who only allow net positions
            #
            # Example: You could have:
            # - Long: +2000 units (two buy orders)
            # - Short: -1000 units (one sell order)
            # Net exposure: +1000 units long
            #
            # Why? Hedging strategies, complex trading systems, or multiple strategies
            # trading the same instrument independently

            # Check long side (positive units = buying the base currency)
            if position.long.units != "0":
                # Units: Total size of all long trades combined
                # Average Price: Weighted average entry price of all long trades
                # Example: Buy 1000 @ 1.1000, Buy 2000 @ 1.1020
                #          Average = (1000*1.1000 + 2000*1.1020) / 3000 = 1.1013
                print(f"    Long: {position.long.units} units @ {position.long.average_price}")

                # Unrealized P/L: Current profit/loss on all long trades
                # = (Current Price - Average Entry Price) * Units
                # This changes constantly as market moves
                print(f"    Unrealized P/L: {position.long.unrealized_pl}")

            # Check short side (negative units = selling the base currency)
            if position.short.units != "0":
                print(f"    Short: {position.short.units} units @ {position.short.average_price}")
                print(f"    Unrealized P/L: {position.short.unrealized_pl}")

        # Section 2: Get only open positions
        # ===================================
        # get_open_positions() is MORE EFFICIENT than get_positions()
        # It only returns positions with non-zero units (actively open positions)
        #
        # get_positions() vs get_open_positions():
        # - get_positions(): Returns ALL positions (including zero-unit positions)
        #   - Use when: Need complete list, historical tracking, or specific instrument lookup
        #   - Slower: Returns hundreds of positions even if you only have 5 open
        #
        # - get_open_positions(): Returns ONLY active positions
        #   - Use when: Quick status check, dashboard display, risk calculation
        #   - Faster: Only returns what you currently care about
        #   - Recommended for frequent polling
        #
        # Best practice: Use get_open_positions() for 95% of operations
        # Only use get_positions() when you specifically need all instruments
        print("\n=== 2. Open Positions Only ===")

        # Returns dict with "positions" key, but only non-zero positions
        # If you have no open positions, this returns an empty list
        open_positions_response = await client.positions.get_open_positions(client.account_id)
        open_positions = open_positions_response.get("positions", [])

        print(f"Open positions: {len(open_positions)}")

        # Iterate through active positions
        # This is what you'd use for a trading dashboard or risk monitor
        for position in open_positions:
            print(f"\n  {position.instrument}:")

            # Check each side independently
            # A position can have long, short, or both sides open
            if position.long.units != "0":
                print(f"    Long: {position.long.units} units")
                # Unrealized P/L: How much you'd gain/lose if you closed now
                print(f"    P/L: {position.long.unrealized_pl}")

            if position.short.units != "0":
                print(f"    Short: {position.short.units} units")
                print(f"    P/L: {position.short.unrealized_pl}")

        # Section 3: Get position for specific instrument
        # ================================================
        # get_position() fetches position details for ONE specific instrument
        # This is the MOST EFFICIENT way to check a single instrument's status
        #
        # Use cases:
        # - Pre-trade checks: "Do I already have a EUR/USD position?"
        # - Strategy monitors: Check position for your strategy's specific instrument
        # - Position sizing: Calculate how much more you can trade
        # - Risk checks: Verify position before placing orders
        #
        # Key advantage: Direct lookup by instrument name (no iteration needed)
        # Much faster than get_positions() or get_open_positions() if you only need one
        print("\n=== 3. Position by Instrument ===")

        # Query specific instrument position
        # Returns position even if units are zero (closed position)
        position_response = await client.positions.get_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

        # Response has "position" key with Position object
        eur_position = position_response["position"]

        print("\nEUR/USD Position:")
        print(f"  Instrument: {eur_position.instrument}")

        # Long side details
        # Even if no long position, long object still exists with units="0"
        print("\n  Long Side:")
        print(f"    Units: {eur_position.long.units}")

        if eur_position.long.units != "0":
            # Average Price: Weighted average of all long trade entry prices
            # Critical for calculating P/L and understanding your cost basis
            print(f"    Average Price: {eur_position.long.average_price}")

            # Unrealized P/L: Current floating profit/loss
            # This is NOT locked in - it changes with every price tick
            print(f"    Unrealized P/L: {eur_position.long.unrealized_pl}")

            # Trade IDs: List of individual trades that make up this position
            # IMPORTANT: A position can consist of multiple trades
            # Example: You place 3 separate buy orders = 3 trades = 1 long position
            #
            # Why track trade IDs?
            # - Close specific trades individually (FIFO or selective)
            # - Audit trail: Know which orders created which trades
            # - Different trades may have different entry prices/times
            # - Apply different exit strategies per trade
            print(f"    Trade IDs: {', '.join(eur_position.long.trade_ids) if eur_position.long.trade_ids else 'None'}")

        # Short side details
        # Same structure as long side but for short positions
        print("\n  Short Side:")
        print(f"    Units: {eur_position.short.units}")

        if eur_position.short.units != "0":
            print(f"    Average Price: {eur_position.short.average_price}")
            print(f"    Unrealized P/L: {eur_position.short.unrealized_pl}")

            # Trade IDs for short side
            # You can have different trades on long and short sides simultaneously
            print(f"    Trade IDs: {', '.join(eur_position.short.trade_ids) if eur_position.short.trade_ids else 'None'}")

        # Section 4: Open a new position
        # ===============================
        # Opening a position is done by placing a market order
        # There's no separate "open position" endpoint - positions are created automatically
        #
        # When you place an order that fills:
        # - If no position exists for that instrument → creates new position
        # - If position exists → adds to existing position
        # - Position aggregates all trades automatically
        #
        # Example: EUR/USD position lifecycle
        # 1. No position: units=0
        # 2. Buy 1000 units → Long position: units=1000
        # 3. Buy 2000 more → Long position: units=3000 (aggregated)
        # 4. Sell 500 → Long position: units=2500 (reduced)
        print("\n=== 4. Open New Position ===")
        print("Opening position: BUY 2000 units EUR/USD")

        # Place market order to open position
        # Positive units = BUY = LONG position
        # Negative units = SELL = SHORT position
        order_response = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=2000)

        if order_response.order_fill_transaction:
            fill = order_response.order_fill_transaction
            print(f"✅ Position opened at {fill.price}")

            # Units: Actual units filled (usually matches request for market orders)
            # For large orders or illiquid markets, might get partial fill
            print(f"Units: {fill.units}")

        # Verify the position was created/updated
        # Good practice: Always verify critical operations succeeded
        # API operations can fail silently in rare cases (network issues, etc.)
        position_response = await client.positions.get_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
        updated_position = position_response["position"]

        # Should show 2000 units (or more if you already had a position)
        print(f"Current long units: {updated_position.long.units}")

        # Section 5: Partially close a position
        # ======================================
        # Partial closes allow you to lock in profits or cut losses on PART of a position
        # This is done by placing an order in the opposite direction with smaller size
        #
        # Use cases:
        # - Scaling out: Take profits in stages (close 25%, then 50%, then 100%)
        # - Risk management: Reduce exposure when uncertain
        # - Trailing stops: Lock in profits while keeping position open
        # - Position rebalancing: Adjust size to match changing market conditions
        #
        # Example: You have +2000 units long
        # - Sell 500 units → Reduces to +1500 units (partial close)
        # - Sell 1000 more → Reduces to +500 units (another partial close)
        # - Sell 500 more → Closes to 0 units (full close)
        #
        # IMPORTANT: Opposite direction with LESS units = partial close
        # Opposite direction with MORE units = close + reverse position
        print("\n=== 5. Partial Position Close ===")

        # Calculate 50% of current position
        current_units = int(updated_position.long.units)
        close_50_percent = -(current_units // 2)  # Negative to close long

        # Why negative units?
        # - Current position: +2000 (long)
        # - To reduce: Place sell order with negative units
        # - Close 50%: -1000 units
        # - Result: +1000 units remaining (50% closed)
        print(f"Closing 50% of position ({-close_50_percent} units)")

        # Place market order to partially close
        # This is the same as opening a position, just opposite direction with smaller size
        partial_close = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=close_50_percent)

        if partial_close.order_fill_transaction:
            fill = partial_close.order_fill_transaction
            print(f"✅ Partial close at {fill.price}")

            # Realized P/L: Profit/loss locked in from this partial close
            # = (Exit Price - Entry Price) * Units Closed
            # This is NOW part of your account balance (no longer unrealized)
            print(f"Realized P/L: {fill.pl}")

            # Verify remaining position
            # Should be 50% of original (1000 units if started with 2000)
            remaining_response = await client.positions.get_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
            remaining_position = remaining_response["position"]
            print(f"Remaining long units: {remaining_position.long.units}")

        # Section 6: Close position completely (long side)
        # ================================================
        # The close_position() endpoint is a CONVENIENCE METHOD for closing positions
        # It's more explicit than placing orders and prevents mistakes
        #
        # Two ways to close a position:
        # 1. Place opposite market order with exact units (as shown in Section 5)
        #    - More flexible: Can specify exact units, price, dependent orders
        #    - More error-prone: Need to calculate correct opposite units
        #
        # 2. Use close_position() with "ALL" (this section)
        #    - Simpler: Just say "close everything" - no calculations
        #    - Safer: Can't accidentally reverse position by mistake
        #    - Recommended for most use cases
        #
        # close_position() parameters:
        # - long_units="ALL": Close entire long position
        # - short_units="ALL": Close entire short position
        # - (neither): Close BOTH sides
        # - long_units="NONE": Don't touch long side (when closing short only)
        # - short_units="NONE": Don't touch short side (when closing long only)
        print("\n=== 6. Close Long Position ===")

        # Get current position to check if there's anything to close
        # Good practice: Always check before attempting to close
        current_response = await client.positions.get_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
        current_position = current_response["position"]

        if current_position.long.units != "0":
            print(f"Closing all long units: {current_position.long.units}")

            # close_position() with long_units="ALL"
            # This closes the ENTIRE long side, regardless of how many units
            # Behind the scenes: OANDA calculates units and places market order
            close_response = await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD, long_units="ALL")

            # Response contains "longOrderFillTransaction" if long side was closed
            # Note the camelCase key (OANDA API convention)
            if close_response.get("longOrderFillTransaction"):
                long_fill = close_response["longOrderFillTransaction"]
                print(f"✅ Long position closed at {long_fill.price}")

                # Realized P/L: Total profit/loss from closing ALL long trades
                # This is the sum of P/L from all trades that made up the long position
                print(f"Realized P/L: {long_fill.pl}")
        else:
            # No long position to close
            # This is expected if you only have short position or no position at all
            print("No long position to close")

        # Section 7: Close position completely (short side)
        # =================================================
        # Closing short positions works the same as long positions
        # Just use short_units="ALL" parameter instead of long_units="ALL"
        #
        # Short position P/L calculation is INVERSE of long:
        # - Long: Profit when price goes UP (sell higher than you bought)
        # - Short: Profit when price goes DOWN (buy back lower than you sold)
        #
        # Example short position:
        # 1. Sell 1000 units @ 1.1000 (open short)
        # 2. Price drops to 1.0950
        # 3. Buy 1000 units @ 1.0950 (close short)
        # 4. Profit: (1.1000 - 1.0950) * 1000 = 50 units of quote currency
        #
        # Why short? Profit from falling prices, hedging, or arbitrage strategies
        print("\n=== 7. Close Short Position ===")

        # First, open a short position for demonstration
        # Negative units = SELL = SHORT position
        print("Opening short position for demonstration...")
        short_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000,  # Negative for short
        )

        if short_order.order_fill_transaction:
            print(f"✅ Short position opened at {short_order.order_fill_transaction.price}")

            # Now close the short position
            # To close short: Buy back the units you sold
            print("\nClosing short position...")

            # short_units="ALL" closes entire short side
            # Behind the scenes: Places buy order for exact amount of short position
            close_short = await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD, short_units="ALL")

            # Response contains "shortOrderFillTransaction" if short side was closed
            if close_short.get("shortOrderFillTransaction"):
                short_fill = close_short["shortOrderFillTransaction"]
                print(f"✅ Short position closed at {short_fill.price}")

                # Realized P/L: Profit/loss from closing short position
                # Positive = price went down (profit on short)
                # Negative = price went up (loss on short)
                print(f"Realized P/L: {short_fill.pl}")

        # Section 8: Close entire position (both sides)
        # ==============================================
        # Sometimes you have BOTH long and short positions on the same instrument
        # This is common in hedged trading strategies or when running multiple bots
        #
        # Example scenario:
        # - Strategy A: Long 1000 units EUR/USD (trend following)
        # - Strategy B: Short 500 units EUR/USD (mean reversion)
        # - Net exposure: +500 units long
        # - But you have BOTH a long and short position simultaneously
        #
        # To close EVERYTHING at once:
        # Call close_position() with NO parameters (no long_units, no short_units)
        # This closes BOTH sides in a single operation
        #
        # Why close both sides?
        # - Emergency exit: Close all exposure immediately
        # - Strategy shutdown: Flatten everything before stopping
        # - End of trading session: Go to cash before weekend/holidays
        # - Risk events: Major news, volatility spikes, etc.
        print("\n=== 8. Close Entire Position ===")

        # Open positions on both sides for demonstration
        # This creates a hedged position (both long and short simultaneously)
        print("Opening positions on both sides for demonstration...")
        await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,  # Long
        )
        await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-500,  # Short
        )

        print("Closing entire EUR/USD position (both sides)...")

        # close_position() with NO parameters closes EVERYTHING
        # Behind the scenes: Places two market orders (one for long, one for short)
        # Both orders execute simultaneously at current market prices
        close_all = await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

        # Calculate total P/L from both sides
        # Important: Use Decimal for financial calculations (never float)
        total_pl = Decimal("0")

        # Check if long side was closed
        if close_all.get("longOrderFillTransaction"):
            long_fill = close_all["longOrderFillTransaction"]
            print(f"✅ Long closed: P/L = {long_fill.pl}")
            total_pl += Decimal(long_fill.pl)

        # Check if short side was closed
        if close_all.get("shortOrderFillTransaction"):
            short_fill = close_all["shortOrderFillTransaction"]
            print(f"✅ Short closed: P/L = {short_fill.pl}")
            total_pl += Decimal(short_fill.pl)

        # Total P/L: Combined profit/loss from both sides
        # This is the actual impact on your account balance
        print(f"Total realized P/L: {total_pl}")

        # Section 9: Position P/L tracking
        # =================================
        # P/L (Profit/Loss) tracking is CRITICAL for trading performance analysis
        # There are multiple levels of P/L to understand:
        #
        # 1. Trade-level P/L: Individual trade profit/loss
        # 2. Position-level P/L: Aggregated P/L for all trades in an instrument
        # 3. Account-level P/L: Total P/L across all positions
        #
        # UNREALIZED P/L vs REALIZED P/L:
        # - Unrealized: "Paper profits/losses" on open positions
        #   - Changes constantly as market moves
        #   - Not locked in yet
        #   - Doesn't affect balance until closed
        #
        # - Realized: Actual profits/losses from closed positions
        #   - Locked in (can't change)
        #   - Part of your account balance
        #   - Used for performance reporting
        #
        # Example:
        # - Buy 1000 EUR/USD @ 1.1000
        # - Current price: 1.1050
        # - Unrealized P/L: +50 pips (not locked in yet)
        # - Close position @ 1.1050
        # - Realized P/L: +50 pips (locked in, part of balance)
        print("\n=== 9. Position P/L Tracking ===")

        print("\nKey P/L Concepts:")
        print("  Unrealized P/L: Current profit/loss on open positions")
        print("  Realized P/L: Profit/loss from closed trades")
        print("  Position-level P/L: Aggregates all trades for an instrument")

        # Get account summary for overall P/L
        # This is the highest-level view of your trading performance
        account_response = await client.accounts.get_account_summary(client.account_id)
        account = account_response["account"]

        print("\nAccount-Level P/L:")
        # Total Unrealized P/L: Sum of all open positions' P/L
        # If positive: Your open positions are winning overall
        # If negative: Your open positions are losing overall
        print(f"  Total Unrealized P/L: {account.unrealized_pl}")

        # Total Realized P/L: Cumulative P/L from all closed trades
        # This is your actual trading profit/loss (locked in)
        # Part of your account balance
        print(f"  Total Realized P/L: {account.pl}")

        # Get current positions to calculate position-level P/L
        positions_response = await client.positions.get_open_positions(client.account_id)
        positions = positions_response.get("positions", [])

        if positions:
            print("\nPosition-Level P/L:")
            # Analyze each position's P/L contribution
            for position in positions:
                # Calculate P/L for each side
                # Use Decimal for accurate financial calculations
                long_pl = Decimal(position.long.unrealized_pl) if position.long.units != "0" else Decimal("0")
                short_pl = Decimal(position.short.unrealized_pl) if position.short.units != "0" else Decimal("0")

                # Total position P/L: Combined long and short P/L
                # This shows net P/L for this instrument
                total_position_pl = long_pl + short_pl

                print(f"  {position.instrument}: {total_position_pl}")

                if position.long.units != "0":
                    # Calculate ROI (Return on Investment) for long position
                    # ROI = (Profit / Investment) * 100%
                    #
                    # Why ROI matters:
                    # - Compare different position sizes fairly
                    # - Understand capital efficiency
                    # - Benchmark against other strategies
                    #
                    # Example: +$50 P/L on $1000 investment = 5% ROI
                    #         +$50 P/L on $10000 investment = 0.5% ROI
                    units = abs(Decimal(position.long.units))
                    avg_price = Decimal(position.long.average_price) if position.long.average_price else Decimal("0")

                    # Invested capital: Units * Entry Price
                    # This is how much capital you committed to this position
                    invested = units * avg_price

                    # ROI as percentage
                    roi_percent = (long_pl / invested * 100) if invested != 0 else Decimal("0")
                    print(f"    Long ROI: {roi_percent:.2f}%")

    print("\n✅ Position management example completed!")
    print("\n📚 Summary:")
    print("   - get_positions(): All positions (including closed)")
    print("   - get_open_positions(): Only active positions (faster)")
    print("   - get_position(): Single instrument lookup (most efficient)")
    print("   - close_position(): Convenience method for closing positions")
    print("   - Partial closes: Scale in/out of positions")
    print("   - P/L tracking: Monitor performance at trade/position/account levels")
    print("\n   Best practices:")
    print("   - Use get_open_positions() for frequent polling")
    print("   - Use close_position() with 'ALL' for safety")
    print("   - Track both unrealized and realized P/L")
    print("   - Calculate ROI for position comparison")


if __name__ == "__main__":
    asyncio.run(main())
