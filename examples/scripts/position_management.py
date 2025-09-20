"""
FiveTwenty Position Management Example

This example demonstrates comprehensive position management capabilities
including listing, querying, and closing positions.
"""

import asyncio
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID, InstrumentName


async def main() -> None:
    """Demonstrate position management operations."""

    # Get token from environment
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("Please set FIVETWENTY_OANDA_TOKEN environment variable")
        return

    # Use practice environment for safety
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get account ID (use first available account)
        accounts = await client.accounts.get_accounts()
        if not accounts:
            print("No accounts available")
            return

        account_id = AccountID(accounts[0].id)
        print(f"Using account: {account_id}")
        print("=" * 60)

        # 1. List all positions (including historical)
        print("1. Listing all positions (including historical):")
        all_positions = await client.positions.get_positions(account_id)
        positions = all_positions.get("positions", [])

        if not positions:
            print("   No positions found in account history")
        else:
            for position in positions:
                instrument = position["instrument"]
                long_units = position["long"]["units"]
                short_units = position["short"]["units"]
                total_pl = position["pl"]
                unrealized_pl = position["unrealizedPL"]

                print(f"   {instrument}:")
                print(f"     Long units: {long_units}")
                print(f"     Short units: {short_units}")
                print(f"     Total P&L: {total_pl}")
                print(f"     Unrealized P&L: {unrealized_pl}")
                print()

        # 2. List only open positions (active trades)
        print("2. Listing open positions only:")
        open_positions = await client.positions.get_open_positions(account_id)
        open_pos = open_positions.get("positions", [])

        if not open_pos:
            print("   No open positions")
        else:
            for position in open_pos:
                instrument = position["instrument"]
                long_units = position["long"]["units"]
                short_units = position["short"]["units"]
                long_avg = position["long"].get("averagePrice", "N/A")
                short_avg = position["short"].get("averagePrice", "N/A")

                print(f"   {instrument}:")
                print(f"     Long: {long_units} units @ {long_avg}")
                print(f"     Short: {short_units} units @ {short_avg}")
                print()

        # 3. Get position for specific instrument
        print("3. Getting position for specific instrument (EUR_USD):")
        try:
            eur_usd_position = await client.positions.get_position(account_id, InstrumentName.EUR_USD)
            position = eur_usd_position["position"]

            print("   EUR_USD Position:")
            print(f"     Long units: {position['long']['units']}")
            print(f"     Short units: {position['short']['units']}")
            print(f"     Total P&L: {position['pl']}")
            print(f"     Unrealized P&L: {position['unrealizedPL']}")

            # Show trade IDs if any
            long_trades = position["long"].get("tradeIDs", [])
            short_trades = position["short"].get("tradeIDs", [])
            if long_trades:
                print(f"     Long trade IDs: {long_trades}")
            if short_trades:
                print(f"     Short trade IDs: {short_trades}")

        except Exception as e:
            print(f"   No EUR_USD position or error: {e}")
        print()

        # 4. Position closure examples (DEMO ONLY - be careful with real money!)
        print("4. Position closure examples:")
        print("   NOTE: These are demonstration calls - use with caution!")

        # Find an open position to demonstrate closure
        demo_instrument = None
        for position in open_pos:
            long_units = float(position["long"]["units"])
            short_units = float(position["short"]["units"])
            if long_units > 0 or short_units > 0:
                demo_instrument = position["instrument"]
                break

        if demo_instrument:
            print(f"   Found open position in {demo_instrument} for demonstration")

            # Example 1: Close all long position
            print("\n   Example: How to close entire long position:")
            print("   await client.positions.close(")
            print("       account_id,")
            print(f"       '{demo_instrument}',")
            print("       long_units='ALL'")
            print("   )")

            # Example 2: Close partial short position
            print("\n   Example: How to close 500 units of short position:")
            print("   await client.positions.close(")
            print("       account_id,")
            print(f"       '{demo_instrument}',")
            print("       short_units='500'")
            print("   )")

            # Example 3: Close both sides
            print("\n   Example: How to close both long (all) and short (partial):")
            print("   await client.positions.close(")
            print("       account_id,")
            print(f"       '{demo_instrument}',")
            print("       long_units='ALL',")
            print("       short_units='1000'")
            print("   )")

            # Example 4: Using Decimal for precise amounts
            print("\n   Example: How to close using Decimal for precision:")
            print("   from decimal import Decimal")
            print("   ")
            print("   precise_units = Decimal('1250.50')")
            print("   await client.positions.close(")
            print("       account_id,")
            print(f"       '{demo_instrument}',")
            print("       long_units=precise_units")
            print("   )")

        else:
            print("   No open positions available for demonstration")

        # 5. Position aggregation explanation
        print("\n5. Understanding Position Aggregation:")
        print("""
   OANDA positions aggregate all trades for an instrument:

   - Long Side: All buy trades are netted together
     * Units: Total long units held
     * Average Price: Volume-weighted average entry price
     * Trade IDs: List of contributing trade IDs
     * P&L: Realized + Unrealized profit/loss

   - Short Side: All sell trades are netted together
     * Similar structure to long side

   - Position Total:
     * Net P&L from both sides
     * Margin used for the entire position
     * Financing charges/credits
        """)

        # 6. Risk management considerations
        print("6. Risk Management Best Practices:")
        print("""
   - Monitor unrealized P&L regularly
   - Set position size limits based on account balance
   - Use 'NONE' directive to leave one side unchanged
   - Consider partial closures for profit taking
   - Always validate position sizes before closure
   - Monitor margin usage across all positions
        """)

        print("\nPosition management demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
