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
    # ================================
    # The AsyncClient is the main entry point for all API operations.
    # It automatically reads configuration from environment variables:
    # - FIVETWENTY_OANDA_TOKEN: Your OANDA API access token
    # - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
    # - FIVETWENTY_OANDA_ENVIRONMENT: Either "practice" or "live"
    #
    # IMPORTANT: Always use 'async with' context manager - this ensures:
    # - Proper connection pooling and resource cleanup
    # - Automatic closing of HTTP connections
    # - Exception-safe cleanup even if errors occur
    print("\n=== 1. Client Initialization ===")

    async with AsyncClient() as client:
        # The client is now connected and ready to use
        # _environment shows whether we're in practice (sandbox) or live (real money) mode
        print(f"✅ Connected to OANDA {client._environment.value} environment")
        print(f"📊 Using account: {client.account_id}")

        # Section 2: Get account information
        # ==================================
        # Account summary provides a snapshot of your account's current state
        # This is typically the first call you make to check your account status
        print("\n=== 2. Account Information ===")

        # get_account_summary returns a dict with account data
        # It's more efficient than get_account (which returns more detailed info)
        account_summary = await client.accounts.get_account_summary(client.account_id)
        account = account_summary["account"]

        # Key account metrics:
        # - balance: Your account's current balance (includes unrealized P/L)
        # - nav: Net Asset Value (balance + unrealized P/L from open positions)
        # - unrealized_pl: Profit/loss on open positions (not yet realized)
        # - margin_used: Capital tied up in open positions
        # - margin_available: Capital still available for new trades
        print(f"Balance: {account.balance} {account.currency}")
        print(f"NAV: {account.nav} {account.currency}")
        print(f"Unrealized P/L: {account.unrealized_pl if account.unrealized_pl is not None else 'N/A'} {account.currency}")
        print(f"Margin Used: {account.margin_used if account.margin_used is not None else 'N/A'} {account.currency}")
        print(f"Margin Available: {account.margin_available} {account.currency}")
        print(f"Open Trades: {account.open_trade_count}")
        print(f"Open Positions: {account.open_position_count}")

        # Section 3: Get current market prices
        # ====================================
        # Pricing data shows current bid/ask prices and spreads
        # This is essential before placing orders to understand current market conditions
        print("\n=== 3. Current Market Prices ===")

        # InstrumentName.EUR_USD is a typed enum - provides autocomplete and type safety
        # You can request prices for multiple instruments at once by passing a list
        pricing = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])

        # Pricing response contains a list of price objects (one per instrument requested)
        price = pricing["prices"][0]

        # Bid = price at which you can SELL
        # Ask = price at which you can BUY
        # Spread = difference between ask and bid (broker's profit + market liquidity)
        bid = price.bids[0].price if price.bids else "N/A"
        ask = price.asks[0].price if price.asks else "N/A"

        if bid != "N/A" and ask != "N/A":
            # Calculate spread - the cost of entering and immediately exiting a trade
            # Lower spreads = lower trading costs
            spread = Decimal(ask) - Decimal(bid)
            print(f"Instrument: {price.instrument}")
            print(f"Bid: {bid}")
            print(f"Ask: {ask}")
            print(f"Spread: {spread:.5f}")  # Typically shown in pips (0.0001 for EUR/USD)
            print(f"Time: {price.time}")
        else:
            # Market might be closed or instrument unavailable
            print(f"Instrument: {price.instrument}")
            print(f"Status: {price.status}")

        # Section 4: Place a simple market order
        # ======================================
        # Market orders execute immediately at the best available price
        # They're the simplest order type - guaranteed to fill (if market is open)
        print("\n=== 4. Place Market Order ===")
        print("⚠️  Placing a BUY order for 1000 units of EUR/USD...")

        # Units: Positive = BUY, Negative = SELL
        # 1000 units = 0.01 lots (a micro lot)
        # For EUR/USD, this means buying €1,000 worth
        order_response = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        # Check if order was filled (it should be - market orders fill immediately)
        if order_response.get("orderFillTransaction"):
            fill = order_response["orderFillTransaction"]
            print("✅ Order filled!")

            # Transaction ID: Unique identifier for this fill (useful for tracking/auditing)
            print(f"Transaction ID: {fill.id}")
            print(f"Instrument: {fill.instrument}")
            print(f"Units: {fill.units}")

            # Price: Actual execution price (might differ slightly from quoted price)
            # This is the "fill price" - what you actually paid
            print(f"Price: {fill.price}")
            print(f"Time: {fill.time}")

            # If this order opened a new trade, we get the trade_id
            # Trades are individual positions that can be closed independently
            trade_id = None
            if fill.trade_opened:
                trade_id = fill.trade_opened.trade_id
                print(f"Trade Opened: {trade_id}")
        else:
            # Rare case - market order didn't fill (market closed, insufficient margin, etc.)
            print("❌ Order was not filled")
            print(f"Order Create Transaction: {order_response.get('orderCreateTransaction')}")

        # Section 5: Check positions
        # ==========================
        # Positions aggregate all trades for an instrument
        # Example: 3 separate EUR/USD buy trades = 1 EUR/USD long position
        print("\n=== 5. Open Positions ===")

        # get_open_positions only returns positions with non-zero units
        positions_response = await client.positions.get_open_positions(client.account_id)
        positions = positions_response.get("positions", [])

        if positions:
            print(f"Found {len(positions)} open position(s):")
            for position in positions:
                print(f"\n  Instrument: {position.instrument}")

                # OANDA tracks long and short positions separately per instrument
                # You can have both a long and short position on the same instrument

                # Check long side (positive units = buying)
                if hasattr(position, "long") and position.long.units != "0":
                    print("  Long:")
                    print(f"    Units: {position.long.units}")

                    # Average price: Weighted average if you have multiple trades
                    print(f"    Average Price: {position.long.average_price}")

                    # Unrealized P/L: Current profit/loss (not yet realized by closing)
                    # This changes constantly as market prices move
                    print(f"    Unrealized P/L: {position.long.unrealized_pl}")

                # Check short side (negative units = selling)
                if hasattr(position, "short") and position.short.units != "0":
                    print("  Short:")
                    print(f"    Units: {position.short.units}")
                    print(f"    Average Price: {position.short.average_price}")
                    print(f"    Unrealized P/L: {position.short.unrealized_pl}")
        else:
            print("No open positions")

        # Section 6: Close the position
        # =============================
        # To close a long position, place a sell order with negative units
        # To close a short position, place a buy order with positive units
        print("\n=== 6. Close Position ===")
        print("⚠️  Closing EUR/USD position...")

        # Negative units (-1000) closes our long position (+1000)
        # This "flattens" the position back to zero
        close_response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000,  # Negative to close long position
        )

        if close_response.get("orderFillTransaction"):
            close_fill = close_response["orderFillTransaction"]
            print("✅ Position closed!")
            print(f"Transaction ID: {close_fill.id}")
            print(f"Close Price: {close_fill.price}")

            # Realized P/L: Actual profit/loss from this closed trade
            # This is locked in - it's now part of your account balance
            # Positive = profit, Negative = loss
            print(f"Realized P/L: {close_fill.pl} {account.currency}")
            print(f"Time: {close_fill.time}")

            # trades_closed lists all trades that were closed by this order
            # Usually just one trade, but could be multiple if you had several open
            if close_fill.trades_closed:
                print(f"Trade Closed: {close_fill.trades_closed[0].trade_id}")
        else:
            print("❌ Position was not closed")

    # When we exit the 'async with' block, the client automatically:
    # - Closes all HTTP connections
    # - Cleans up resources
    # - Ensures no lingering connections
    print("\n✅ Basic usage example completed!")


if __name__ == "__main__":
    # asyncio.run() is the standard way to run async code from a synchronous context
    # It creates an event loop, runs the coroutine, and cleans up
    asyncio.run(main())
