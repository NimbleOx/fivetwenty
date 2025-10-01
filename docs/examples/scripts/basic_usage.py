#!/usr/bin/env python3
"""
Basic FiveTwenty Usage Example

This script demonstrates the fundamental operations with the FiveTwenty SDK.
Covers: Client setup, account info, basic market data, simple orders.
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName


async def main() -> None:
    """Basic usage example demonstrating core functionality."""

    # Section 1: Initialize the client
    # The client automatically reads environment variables:
    # - FIVETWENTY_OANDA_TOKEN
    # - FIVETWENTY_OANDA_ACCOUNT
    # - FIVETWENTY_OANDA_ENVIRONMENT
    print("\n=== 1. Client Initialization ===")

    async with AsyncClient() as client:
        print(f"✅ Connected to OANDA {client._environment.value} environment")
        print(f"📊 Using account: {client.account_id}")

        # Section 2: Get account information
        print("\n=== 2. Account Information ===")

        account_summary = await client.accounts.get_account_summary(client.account_id)
        account = account_summary["account"]

        print(f"Balance: {account.balance} {account.currency}")
        print(f"NAV: {account.nav} {account.currency}")
        print(f"Unrealized P/L: {account.unrealized_pl} {account.currency}")
        print(f"Margin Used: {account.margin_used} {account.currency}")
        print(f"Margin Available: {account.margin_available} {account.currency}")
        print(f"Open Trades: {account.open_trade_count}")
        print(f"Open Positions: {account.open_position_count}")

        # Section 3: Get current market prices
        print("\n=== 3. Current Market Prices ===")

        pricing = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])

        price = pricing["prices"][0]
        bid = price.bids[0].price if price.bids else "N/A"
        ask = price.asks[0].price if price.asks else "N/A"

        if bid != "N/A" and ask != "N/A":
            spread = Decimal(ask) - Decimal(bid)
            print(f"Instrument: {price.instrument}")
            print(f"Bid: {bid}")
            print(f"Ask: {ask}")
            print(f"Spread: {spread:.5f}")
            print(f"Time: {price.time}")
        else:
            print(f"Instrument: {price.instrument}")
            print(f"Status: {price.status}")

        # Section 4: Place a simple market order
        print("\n=== 4. Place Market Order ===")
        print("⚠️  Placing a BUY order for 1000 units of EUR/USD...")

        order_response = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        if order_response.order_fill_transaction:
            fill = order_response.order_fill_transaction
            print("✅ Order filled!")
            print(f"Transaction ID: {fill.get('id')}")
            print(f"Instrument: {fill.get('instrument')}")
            print(f"Units: {fill.get('units')}")
            print(f"Price: {fill.get('price')}")
            print(f"Time: {fill.get('time')}")

            trade_id = None
            if fill.get("tradeOpened"):
                trade_id = fill["tradeOpened"]["tradeID"]
                print(f"Trade Opened: {trade_id}")
        else:
            print("❌ Order was not filled")
            print(f"Order Create Transaction: {order_response.order_create_transaction}")

        # Section 5: Check positions
        print("\n=== 5. Open Positions ===")

        positions_response = await client.positions.get_open_positions(client.account_id)
        positions = positions_response.get("positions", [])

        if positions:
            print(f"Found {len(positions)} open position(s):")
            for position in positions:
                print(f"\n  Instrument: {position.instrument}")

                # Check long side
                if hasattr(position, "long") and position.long.units != "0":
                    print("  Long:")
                    print(f"    Units: {position.long.units}")
                    print(f"    Average Price: {position.long.average_price}")
                    print(f"    Unrealized P/L: {position.long.unrealized_pl}")

                # Check short side
                if hasattr(position, "short") and position.short.units != "0":
                    print("  Short:")
                    print(f"    Units: {position.short.units}")
                    print(f"    Average Price: {position.short.average_price}")
                    print(f"    Unrealized P/L: {position.short.unrealized_pl}")
        else:
            print("No open positions")

        # Section 6: Close the position
        print("\n=== 6. Close Position ===")
        print("⚠️  Closing EUR/USD position...")

        close_response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000,  # Negative to close long position
        )

        if close_response.order_fill_transaction:
            close_fill = close_response.order_fill_transaction
            print("✅ Position closed!")
            print(f"Transaction ID: {close_fill.get('id')}")
            print(f"Close Price: {close_fill.get('price')}")
            print(f"Realized P/L: {close_fill.get('pl')} {account.currency}")
            print(f"Time: {close_fill.get('time')}")

            if close_fill.get("tradeClosed"):
                print(f"Trade Closed: {close_fill['tradeClosed']['tradeID']}")
        else:
            print("❌ Position was not closed")

    print("\n✅ Basic usage example completed!")


if __name__ == "__main__":
    asyncio.run(main())
