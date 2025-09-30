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
        print("\n=== 1. All Positions ===")

        all_positions_response = await client.positions.get_positions(client.account_id)
        all_positions = all_positions_response.get("positions", [])

        print(f"Total positions (all instruments): {len(all_positions)}")
        for position in all_positions[:5]:  # Show first 5
            print(f"\n  {position.instrument}:")
            if position.long.units != "0":
                print(f"    Long: {position.long.units} units @ {position.long.average_price}")
                print(f"    Unrealized P/L: {position.long.unrealized_pl}")
            if position.short.units != "0":
                print(f"    Short: {position.short.units} units @ {position.short.average_price}")
                print(f"    Unrealized P/L: {position.short.unrealized_pl}")

        # Section 2: Get only open positions
        print("\n=== 2. Open Positions Only ===")

        open_positions_response = await client.positions.get_open_positions(client.account_id)
        open_positions = open_positions_response.get("positions", [])

        print(f"Open positions: {len(open_positions)}")
        for position in open_positions:
            print(f"\n  {position.instrument}:")
            if position.long.units != "0":
                print(f"    Long: {position.long.units} units")
                print(f"    P/L: {position.long.unrealized_pl}")
            if position.short.units != "0":
                print(f"    Short: {position.short.units} units")
                print(f"    P/L: {position.short.unrealized_pl}")

        # Section 3: Get position for specific instrument
        print("\n=== 3. Position by Instrument ===")

        position_response = await client.positions.get_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD
        )
        eur_position = position_response["position"]

        print(f"\nEUR/USD Position:")
        print(f"  Instrument: {eur_position.instrument}")

        print(f"\n  Long Side:")
        print(f"    Units: {eur_position.long.units}")
        if eur_position.long.units != "0":
            print(f"    Average Price: {eur_position.long.average_price}")
            print(f"    Unrealized P/L: {eur_position.long.unrealized_pl}")
            print(f"    Trade IDs: {', '.join(eur_position.long.trade_i_ds) if eur_position.long.trade_i_ds else 'None'}")

        print(f"\n  Short Side:")
        print(f"    Units: {eur_position.short.units}")
        if eur_position.short.units != "0":
            print(f"    Average Price: {eur_position.short.average_price}")
            print(f"    Unrealized P/L: {eur_position.short.unrealized_pl}")
            print(f"    Trade IDs: {', '.join(eur_position.short.trade_i_ds) if eur_position.short.trade_i_ds else 'None'}")

        # Section 4: Open a new position
        print("\n=== 4. Open New Position ===")
        print("Opening position: BUY 2000 units EUR/USD")

        order_response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=2000
        )

        if order_response.order_fill_transaction:
            fill = order_response.order_fill_transaction
            print(f"✅ Position opened at {fill.price}")
            print(f"Units: {fill.units}")

        # Verify position
        position_response = await client.positions.get_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD
        )
        updated_position = position_response["position"]
        print(f"Current long units: {updated_position.long.units}")

        # Section 5: Partially close a position
        print("\n=== 5. Partial Position Close ===")

        current_units = int(updated_position.long.units)
        close_50_percent = -(current_units // 2)  # Close 50%

        print(f"Closing 50% of position ({-close_50_percent} units)")

        partial_close = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=close_50_percent
        )

        if partial_close.order_fill_transaction:
            fill = partial_close.order_fill_transaction
            print(f"✅ Partial close at {fill.price}")
            print(f"Realized P/L: {fill.pl}")

            # Check remaining position
            remaining_response = await client.positions.get_position(
                account_id=client.account_id,
                instrument=InstrumentName.EUR_USD
            )
            remaining_position = remaining_response["position"]
            print(f"Remaining long units: {remaining_position.long.units}")

        # Section 6: Close position completely (long side)
        print("\n=== 6. Close Long Position ===")

        # Get current position
        current_response = await client.positions.get_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD
        )
        current_position = current_response["position"]

        if current_position.long.units != "0":
            print(f"Closing all long units: {current_position.long.units}")

            close_response = await client.positions.close_position(
                account_id=client.account_id,
                instrument=InstrumentName.EUR_USD,
                long_units="ALL"
            )

            if close_response.get("longOrderFillTransaction"):
                long_fill = close_response["longOrderFillTransaction"]
                print(f"✅ Long position closed at {long_fill.price}")
                print(f"Realized P/L: {long_fill.pl}")
        else:
            print("No long position to close")

        # Section 7: Close position completely (short side)
        print("\n=== 7. Close Short Position ===")

        # First, open a short position
        print("Opening short position for demonstration...")
        short_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000  # Negative for short
        )

        if short_order.order_fill_transaction:
            print(f"✅ Short position opened at {short_order.order_fill_transaction.price}")

            # Now close it
            print("\nClosing short position...")
            close_short = await client.positions.close_position(
                account_id=client.account_id,
                instrument=InstrumentName.EUR_USD,
                short_units="ALL"
            )

            if close_short.get("shortOrderFillTransaction"):
                short_fill = close_short["shortOrderFillTransaction"]
                print(f"✅ Short position closed at {short_fill.price}")
                print(f"Realized P/L: {short_fill.pl}")

        # Section 8: Close entire position (both sides)
        print("\n=== 8. Close Entire Position ===")

        # Open positions on both sides
        print("Opening positions on both sides for demonstration...")
        await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000  # Long
        )
        await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-500  # Short
        )

        print("Closing entire EUR/USD position (both sides)...")

        close_all = await client.positions.close_position(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD
        )

        total_pl = Decimal("0")
        if close_all.get("longOrderFillTransaction"):
            long_fill = close_all["longOrderFillTransaction"]
            print(f"✅ Long closed: P/L = {long_fill.pl}")
            total_pl += Decimal(long_fill.pl)

        if close_all.get("shortOrderFillTransaction"):
            short_fill = close_all["shortOrderFillTransaction"]
            print(f"✅ Short closed: P/L = {short_fill.pl}")
            total_pl += Decimal(short_fill.pl)

        print(f"Total realized P/L: {total_pl}")

        # Section 9: Position P/L tracking
        print("\n=== 9. Position P/L Tracking ===")

        print("\nKey P/L Concepts:")
        print("  Unrealized P/L: Current profit/loss on open positions")
        print("  Realized P/L: Profit/loss from closed trades")
        print("  Position-level P/L: Aggregates all trades for an instrument")

        # Get account summary for overall P/L
        account_response = await client.accounts.get_account_summary(client.account_id)
        account = account_response["account"]

        print(f"\nAccount-Level P/L:")
        print(f"  Total Unrealized P/L: {account.unrealized_pl}")
        print(f"  Total Realized P/L: {account.pl}")

        # Get current positions
        positions_response = await client.positions.get_open_positions(client.account_id)
        positions = positions_response.get("positions", [])

        if positions:
            print(f"\nPosition-Level P/L:")
            for position in positions:
                long_pl = Decimal(position.long.unrealized_pl) if position.long.units != "0" else Decimal("0")
                short_pl = Decimal(position.short.unrealized_pl) if position.short.units != "0" else Decimal("0")
                total_position_pl = long_pl + short_pl

                print(f"  {position.instrument}: {total_position_pl}")

                if position.long.units != "0":
                    # Calculate ROI for long position
                    units = abs(Decimal(position.long.units))
                    avg_price = Decimal(position.long.average_price)
                    invested = units * avg_price
                    roi_percent = (long_pl / invested * 100) if invested != 0 else Decimal("0")
                    print(f"    Long ROI: {roi_percent:.2f}%")

    print("\n✅ Position management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
