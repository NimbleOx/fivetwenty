#!/usr/bin/env python3
"""
Advanced Order Management Example

Demonstrates all order types and order management operations:
- Market, Limit, Stop, and Market-If-Touched orders
- Order modification and cancellation
- Client extensions and order dependencies
- Pending orders management
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import (
    ClientExtensions,
    InstrumentName,
    LimitOrderRequest,
    MarketIfTouchedOrderRequest,
    MarketOrderRequest,
    StopLossDetails,
    StopOrderRequest,
    TakeProfitDetails,
    TimeInForce,
)


async def main() -> None:
    """Advanced order management operations example."""

    async with AsyncClient() as client:
        # Get current pricing for reference
        # CRITICAL: Always check current market price before placing orders
        # This prevents placing orders at stale/incorrect prices
        #
        # Bid vs Ask:
        # - BID: Price at which you SELL (market buys from you)
        # - ASK: Price at which you BUY (you buy from market)
        # - Spread: Ask - Bid (your transaction cost)
        pricing_response = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])
        current_price = pricing_response["prices"][0]

        # Use Decimal for financial calculations (never float)
        current_ask = Decimal(current_price.asks[0].price)
        current_bid = Decimal(current_price.bids[0].price)

        print(f"\nCurrent EUR/USD: Bid={current_bid}, Ask={current_ask}")

        # Section 1: Market orders with extensions
        # ========================================
        # CLIENT EXTENSIONS provide metadata for orders/trades
        # Essential for:
        # - Multi-strategy systems: Track which strategy placed order
        # - Order tracking: Link orders to external IDs
        # - Debugging: Add comments explaining order rationale
        # - Analytics: Tag orders for post-trade analysis
        #
        # ClientExtensions fields:
        # - id: Unique identifier (your own system's ID)
        # - tag: Category/group label
        # - comment: Human-readable description
        #
        # TAKE PROFIT / STOP LOSS ON FILL:
        # Automatically attach TP/SL when order fills
        # This creates a "bracket order" - entry with predefined exits
        # Benefits:
        # - Risk management: Losses limited before you even enter
        # - Discipline: No emotional exit decisions
        # - Automation: Set and forget
        print("\n=== 1. Market Order with Extensions ===")

        # Create client extensions for tracking
        # These persist throughout order→trade lifecycle
        extensions = ClientExtensions(id="strategy-A-001", tag="momentum-strategy", comment="Opening position with auto TP/SL")

        # Define take profit and stop loss on fill
        # RISK:REWARD = 2:1 (50 pips profit vs 25 pips loss)
        # Good traders aim for 2:1 or better ratios
        take_profit = TakeProfitDetails(price=current_ask + Decimal("0.0050"))  # 50 pips profit
        stop_loss = StopLossDetails(price=current_ask - Decimal("0.0025"))  # 25 pips loss

        print(f"Placing market order with TP={take_profit.price}, SL={stop_loss.price}")

        # Market order with automatic TP/SL attachment
        # When this fills, TP and SL orders are automatically created
        order_request = MarketOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("1000"), clientExtensions=extensions, takeProfitOnFill=take_profit, stopLossOnFill=stop_loss)
        order_response = await client.orders.post_order(account_id=client.account_id, order_request=order_request)

        if order_response.get("orderFillTransaction"):
            fill = order_response["orderFillTransaction"]
            print(f"✅ Order filled at {fill.price}")
            print(f"Client ID: {extensions.id}")

            # Check if TP/SL were automatically created
            create_txn = order_response.get("orderCreateTransaction")
            if create_txn and hasattr(create_txn, "take_profit_on_fill") and create_txn.take_profit_on_fill and hasattr(create_txn.take_profit_on_fill, "price"):
                print(f"Take Profit: {create_txn.take_profit_on_fill.price}")
            if create_txn and hasattr(create_txn, "stop_loss_on_fill") and create_txn.stop_loss_on_fill and hasattr(create_txn.stop_loss_on_fill, "price"):
                print(f"Stop Loss: {create_txn.stop_loss_on_fill.price}")

        # Section 2: Limit orders
        # =======================
        # LIMIT ORDER: "Buy/sell at this price or better"
        # - BUY LIMIT: Below current market (buy on pullback/dip)
        # - SELL LIMIT: Above current market (sell on rally/resistance)
        #
        # When to use:
        # - You expect price to retrace before continuing
        # - You want to enter at specific support/resistance level
        # - You're patient and want better price than market
        #
        # Limit vs Market:
        # - Market: Guaranteed fill, uncertain price
        # - Limit: Guaranteed price (or better), uncertain fill
        #
        # TIME IN FORCE options:
        # - GTC (Good-Til-Cancelled): Stays active until filled or cancelled
        # - GTD (Good-Til-Date): Expires at specific datetime
        # - FOK (Fill-Or-Kill): Fill entire order immediately or cancel
        # - IOC (Immediate-Or-Cancel): Fill what you can immediately, cancel rest
        print("\n=== 2. Limit Orders ===")

        # Buy limit below current market (expecting pullback)
        # Example: EUR/USD at 1.1000, place buy limit at 1.0980
        # If price drops to 1.0980, order fills
        # If price stays above, order stays pending
        limit_price = current_bid - Decimal("0.0020")  # 20 pips below

        print(f"Placing GTC limit order at {limit_price}")

        # GTC = Good-Til-Cancelled
        # Order stays active until filled or manually cancelled
        # Use for: Long-term setups, key support/resistance levels
        limit_request = LimitOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("1000"), price=limit_price, timeInForce=TimeInForce.GTC, clientExtensions=ClientExtensions(comment="Buy limit - support level"))
        limit_order = await client.orders.post_order(account_id=client.account_id, order_request=limit_request)

        limit_order_id = None
        if limit_order.get("orderCreateTransaction"):
            create_txn = limit_order["orderCreateTransaction"]
            limit_order_id = create_txn.id
            print(f"✅ Limit order created: {limit_order_id}")
            if hasattr(create_txn, "price"):
                print(f"Price: {create_txn.price}")
            if hasattr(create_txn, "time_in_force"):
                print(f"Time in Force: {create_txn.time_in_force}")

        # GTD = Good-Til-Date
        # Order automatically expires at specified time
        # Use for: Intraday setups, time-sensitive opportunities
        gtd_time = datetime.now(timezone.utc) + timedelta(hours=1)

        print(f"\nPlacing GTD limit order (expires at {gtd_time})")

        # GTD requires gtdTime parameter (must be future datetime)
        # After expiry, order is automatically cancelled
        gtd_request = LimitOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("500"), price=current_bid - Decimal("0.0030"), timeInForce=TimeInForce.GTD, gtdTime=gtd_time, clientExtensions=ClientExtensions(comment="1-hour limit order"))
        gtd_order = await client.orders.post_order(account_id=client.account_id, order_request=gtd_request)

        gtd_order_id = None
        if gtd_order.get("orderCreateTransaction"):
            create_txn = gtd_order["orderCreateTransaction"]
            gtd_order_id = create_txn.id
            print(f"✅ GTD limit order created: {gtd_order_id}")
            if hasattr(create_txn, "gtd_time"):
                print(f"Expires: {create_txn.gtd_time}")

        # Section 3: Stop orders
        # ======================
        # STOP ORDER: "Buy/sell when price reaches trigger level"
        # - BUY STOP: Above current market (buy on breakout)
        # - SELL STOP: Below current market (sell on breakdown)
        #
        # Stop vs Limit (CRITICAL DISTINCTION):
        # LIMIT ORDER:
        # - Buy BELOW market (pullback)
        # - Sell ABOVE market (rally)
        # - "I want a better price"
        #
        # STOP ORDER:
        # - Buy ABOVE market (breakout)
        # - Sell BELOW market (breakdown)
        # - "I want to follow momentum"
        #
        # When to use Stop orders:
        # - Breakout trading: Enter when price breaks resistance
        # - Trend following: Enter when price confirms direction
        # - Stop-loss protection: Exit when price hits loss level
        print("\n=== 3. Stop Orders ===")

        # Stop-entry order (buy above market for breakout)
        # Example: EUR/USD at 1.1000, place buy stop at 1.1030
        # If price rises to 1.1030 (breakout), order triggers
        # If price stays below, order stays pending
        stop_entry_price = current_ask + Decimal("0.0030")  # 30 pips above

        print(f"Placing stop-entry order at {stop_entry_price}")

        # Stop order becomes market order when trigger price reached
        # WARNING: No price guarantee - might fill at worse price (slippage)
        stop_request = StopOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("1000"), price=stop_entry_price, timeInForce=TimeInForce.GTC, clientExtensions=ClientExtensions(comment="Breakout entry"))
        stop_order = await client.orders.post_order(account_id=client.account_id, order_request=stop_request)

        stop_order_id = None
        if stop_order.get("orderCreateTransaction"):
            create_txn = stop_order["orderCreateTransaction"]
            stop_order_id = create_txn.id
            print(f"✅ Stop order created: {stop_order_id}")
            if hasattr(create_txn, "price"):
                print(f"Trigger Price: {create_txn.price}")

        # Section 4: Market-if-touched (MIT) orders
        # ==========================================
        # MIT (Market-If-Touched): Hybrid between Limit and Stop
        # "Limit order that becomes market order when touched"
        #
        # MIT vs LIMIT (key differences):
        # LIMIT ORDER:
        # - Fills at limit price or better
        # - NOT guaranteed to fill (might skip your price)
        # - Example: Bid 1.1000, Limit 1.0990
        #   If price jumps 1.1000 → 1.0985, limit NOT filled
        #
        # MIT ORDER:
        # - Becomes market order when price touches trigger
        # - GUARANTEED to fill (once triggered)
        # - Example: Bid 1.1000, MIT 1.0990
        #   If price touches 1.0990, becomes market order → fills
        #
        # When to use MIT:
        # - You want entry at specific level (like limit)
        # - You MUST get filled (can't miss the move)
        # - Volatility/gaps are concern (price might skip limit)
        # - Examples: News trading, overnight gaps, illiquid markets
        print("\n=== 4. Market-If-Touched Orders ===")

        # MIT below market (like limit but guarantees fill)
        # When price touches this level, order becomes market order
        mit_price = current_bid - Decimal("0.0015")

        print(f"Placing MIT order at {mit_price}")

        # MIT with Take Profit on fill
        # Demonstrates combining MIT entry with automatic TP exit
        mit_request = MarketIfTouchedOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units=Decimal("1000"),
            price=mit_price,
            timeInForce=TimeInForce.GTC,
            takeProfitOnFill=TakeProfitDetails(price=mit_price + Decimal("0.0040")),
            clientExtensions=ClientExtensions(comment="MIT with TP"),
        )
        mit_order = await client.orders.post_order(account_id=client.account_id, order_request=mit_request)

        mit_order_id = None
        if mit_order.get("orderCreateTransaction"):
            create_txn = mit_order["orderCreateTransaction"]
            mit_order_id = create_txn.id
            print(f"✅ MIT order created: {mit_order_id}")
            if hasattr(create_txn, "price"):
                print(f"Trigger Price: {create_txn.price}")

        # Section 5: List and filter orders
        # ==================================
        # Order listing and filtering is essential for:
        # - Portfolio monitoring: See all active orders
        # - Risk management: Track total exposure
        # - Strategy verification: Confirm orders placed correctly
        # - Debugging: Investigate order issues
        #
        # Filtering options:
        # - By instrument: Only EUR/USD orders
        # - By state: PENDING, FILLED, CANCELLED, TRIGGERED
        # - By count/IDs: Specific orders
        print("\n=== 5. List and Filter Orders ===")

        # Get ALL orders (pending, filled, cancelled)
        # This can be many orders if you trade frequently
        # get_orders() returns OANDA's response envelope with orders plus lastTransactionID
        all_orders_response = await client.orders.get_orders(account_id=client.account_id)
        all_orders = all_orders_response["orders"]
        print(f"\nTotal orders: {len(all_orders)}")

        # Filter by instrument: Only show EUR/USD orders
        # Useful for instrument-specific monitoring
        eur_orders_response = await client.orders.get_orders(account_id=client.account_id, instrument=InstrumentName.EUR_USD)
        eur_orders = eur_orders_response["orders"]
        print(f"EUR/USD orders: {len(eur_orders)}")

        # Filter by state: Only show PENDING (active) orders
        # Most useful filter - shows what's currently working
        pending_orders_response = await client.orders.get_orders(account_id=client.account_id, state="PENDING")
        pending_orders = pending_orders_response["orders"]
        print(f"Pending orders: {len(pending_orders)}")

        # Section 6: Get pending orders
        # =============================
        # get_pending_orders() is shortcut for get_orders(state="PENDING")
        # Returns only active orders waiting to fill
        # Most frequently used endpoint for order monitoring
        print("\n=== 6. Pending Orders ===")

        pending = await client.orders.get_pending_orders(account_id=client.account_id)
        pending_list = pending.get("orders", [])

        print(f"\nFound {len(pending_list)} pending order(s):")
        for order in pending_list[:5]:  # Show first 5
            print(f"\n  Order {order.id}:")
            print(f"    Type: {order.type}")
            if hasattr(order, "instrument"):
                print(f"    Instrument: {order.instrument}")
            if hasattr(order, "units"):
                print(f"    Units: {order.units}")
            if hasattr(order, "price"):
                print(f"    Price: {order.price}")
            if hasattr(order, "time_in_force"):
                print(f"    Time in Force: {order.time_in_force}")

        # Section 7: Get specific order details
        # ======================================
        # get_order() fetches full details for single order
        # Use when you need complete information about specific order
        print("\n=== 7. Order Details ===")

        if limit_order_id:
            order_details = await client.orders.get_order(account_id=client.account_id, order_specifier=limit_order_id)
            order = order_details["order"]
            print(f"\nDetails for order {order.id}:")
            print(f"  Type: {order.type}")
            print(f"  State: {order.state}")  # PENDING, FILLED, CANCELLED, etc.
            if hasattr(order, "instrument"):
                print(f"  Instrument: {order.instrument}")
            if hasattr(order, "units"):
                print(f"  Units: {order.units}")
            if hasattr(order, "price"):
                print(f"  Price: {order.price}")
            print(f"  Created: {order.create_time}")

        # Section 8: Modify an existing order
        # ====================================
        # Order modification: Change pending order parameters
        # Only works for PENDING orders (not filled/cancelled)
        # IMPORTANT: Modifying creates NEW order, cancels old one
        # New order gets new ID - original ID becomes invalid
        #
        # Common modifications:
        # - Change price: Adjust limit/stop trigger level
        # - Change units: Increase/decrease order size
        # - Change TIF: Extend/shorten expiry
        print("\n=== 8. Modify Order ===")

        if limit_order_id:
            # Change the limit price (adjust entry level)
            new_price = current_bid - Decimal("0.0025")
            print(f"\nModifying limit order {limit_order_id}")
            print(f"New price: {new_price}")

            # Modification replaces entire order
            # Must provide all order parameters (not just changed fields)
            modify_response = await client.orders.put_order(account_id=client.account_id, order_specifier=limit_order_id, order_request=LimitOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("1000"), price=new_price))

            if modify_response.get("orderCreateTransaction"):
                print("✅ Order modified successfully")
                # NOTE: New order ID - old ID no longer valid
                print(f"New Order ID: {modify_response['orderCreateTransaction'].id}")

        # Section 9: Update order client extensions
        # ==========================================
        # Separate endpoint for updating ONLY client extensions
        # Preserves order, just changes metadata
        # Use for: Updating comments, tags without modifying order itself
        print("\n=== 9. Update Client Extensions ===")

        if gtd_order_id:
            print(f"\nUpdating client extensions for order {gtd_order_id}")

            # Update metadata without changing order
            extensions_update = ClientExtensions(comment="Updated: High priority order", tag="priority-high")
            extension_response = await client.orders.put_order_client_extensions(account_id=client.account_id, order_specifier=gtd_order_id, client_extensions=extensions_update)

            if extension_response.get("orderClientExtensionsModifyTransaction"):
                print("✅ Client extensions updated")

        # Section 10: Cancel orders
        # =========================
        # Cancelling removes pending orders
        # Use when: Setup invalidated, changed mind, risk management
        # Cannot cancel filled/cancelled orders
        print("\n=== 10. Cancel Orders ===")

        # Cancel all our test orders
        orders_to_cancel = [order_id for order_id in [limit_order_id, gtd_order_id, stop_order_id, mit_order_id] if order_id]

        for order_id in orders_to_cancel:
            print(f"\nCancelling order {order_id}")
            cancel_response = await client.orders.cancel_order(account_id=client.account_id, order_specifier=order_id)

            if cancel_response.get("orderCancelTransaction"):
                print(f"✅ Order {order_id} cancelled")

        # Section 11: Complex order strategies
        # =====================================
        # These strategies combine multiple order types
        # Essential for professional trading systems
        print("\n=== 11. Complex Order Strategies ===")

        print("\nBRACKET ORDER:")
        print("  Entry + Take Profit + Stop Loss in one operation")
        print("  - Automatically sets exits when entry fills")
        print("  - Ensures risk is defined before entry")
        print("  - No manual intervention needed")
        print("  ✅ Demonstrated in Section 1 (takeProfitOnFill/stopLossOnFill)")

        print("\nOCO (One-Cancels-Other):")
        print("  Two orders: when one fills, other cancels")
        print("  - Example: TP limit + SL stop on same trade")
        print("  - OANDA implements this automatically")
        print("  - When TP hits, SL cancels (and vice versa)")
        print("  ✅ Built into OANDA's TP/SL system")

        print("\nTRAILING STOP:")
        print("  Stop loss that follows favorable price movement")
        print("  - Locks in profits as trade goes in your favor")
        print("  - Doesn't move against you (only improves)")
        print("  - Implemented via trade management API")
        print("  → See trade_management.py for examples")

        # Close only the trade opened by the first market order.
        # An opposite market order can open a hedge; closing the whole instrument
        # could also affect trades that existed before this example ran.
        opening_fill = order_response.get("orderFillTransaction")
        if opening_fill and opening_fill.trade_opened:
            trade_id = opening_fill.trade_opened.trade_id
            print(f"\n\nCleaning up: Closing test trade {trade_id}...")
            close_response = await client.trades.close_trade(account_id=client.account_id, trade_specifier=trade_id, units="ALL")
            if close_response.get("orderFillTransaction"):
                print("✅ Test trade closed")

    print("\n✅ Advanced order management example completed!")
    print("\n📚 Summary:")
    print("   Order Types:")
    print("   - Market: Immediate execution at best price")
    print("   - Limit: Execution at specific price or better")
    print("   - Stop: Trigger at price, then market order")
    print("   - MIT: Like limit but guaranteed fill when touched")
    print("\n   Time in Force:")
    print("   - GTC: Good-til-cancelled")
    print("   - GTD: Good-til-date (expires)")
    print("   - FOK: Fill-or-kill (all or nothing)")
    print("   - IOC: Immediate-or-cancel (partial OK)")
    print("\n   Key concepts:")
    print("   - Client Extensions: Metadata for tracking")
    print("   - Bracket Orders: Entry + TP + SL together")
    print("   - Order modification: Creates new order with new ID")
    print("   - Pending orders: Active orders waiting to fill")


if __name__ == "__main__":
    asyncio.run(main())
