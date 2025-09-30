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
from datetime import datetime, timedelta
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import (
    ClientExtensions,
    InstrumentName,
    OrderPositionFill,
    StopLossDetails,
    TakeProfitDetails,
    TimeInForce,
)


async def main() -> None:
    """Advanced order management operations example."""

    async with AsyncClient() as client:

        # Get current pricing for reference
        pricing_response = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.EUR_USD]
        )
        current_price = pricing_response["prices"][0]
        current_ask = Decimal(current_price.asks[0].price)
        current_bid = Decimal(current_price.bids[0].price)

        print(f"\nCurrent EUR/USD: Bid={current_bid}, Ask={current_ask}")

        # Section 1: Market orders with extensions
        print("\n=== 1. Market Order with Extensions ===")

        # Create client extensions for tracking
        extensions = ClientExtensions(
            id="strategy-A-001",
            tag="momentum-strategy",
            comment="Opening position with auto TP/SL"
        )

        # Define take profit and stop loss on fill
        take_profit = TakeProfitDetails(price=str(current_ask + Decimal("0.0050")))  # 50 pips profit
        stop_loss = StopLossDetails(price=str(current_ask - Decimal("0.0025")))      # 25 pips loss

        print(f"Placing market order with TP={take_profit.price}, SL={stop_loss.price}")

        order_response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            client_extensions=extensions,
            take_profit_on_fill=take_profit,
            stop_loss_on_fill=stop_loss
        )

        if order_response.order_fill_transaction:
            fill = order_response.order_fill_transaction
            print(f"✅ Order filled at {fill.price}")
            print(f"Client ID: {extensions.id}")

            if order_response.order_create_transaction.take_profit_on_fill:
                print(f"Take Profit: {order_response.order_create_transaction.take_profit_on_fill.price}")
            if order_response.order_create_transaction.stop_loss_on_fill:
                print(f"Stop Loss: {order_response.order_create_transaction.stop_loss_on_fill.price}")

        # Section 2: Limit orders
        print("\n=== 2. Limit Orders ===")

        # Buy limit below current market (expecting pullback)
        limit_price = current_bid - Decimal("0.0020")  # 20 pips below

        print(f"Placing GTC limit order at {limit_price}")

        limit_order = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=limit_price,
            time_in_force=TimeInForce.GTC,  # Good-Till-Cancelled
            client_extensions=ClientExtensions(comment="Buy limit - support level")
        )

        limit_order_id = None
        if limit_order.order_create_transaction:
            limit_order_id = limit_order.order_create_transaction.id
            print(f"✅ Limit order created: {limit_order_id}")
            print(f"Price: {limit_order.order_create_transaction.price}")
            print(f"Time in Force: {limit_order.order_create_transaction.time_in_force}")

        # GTD limit order (expires in 1 hour)
        gtd_time = (datetime.utcnow() + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000000000Z")

        print(f"\nPlacing GTD limit order (expires at {gtd_time})")

        gtd_order = await client.orders.post_limit_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=500,
            price=current_bid - Decimal("0.0030"),
            time_in_force=TimeInForce.GTD,
            gtd_time=gtd_time,
            client_extensions=ClientExtensions(comment="1-hour limit order")
        )

        gtd_order_id = None
        if gtd_order.order_create_transaction:
            gtd_order_id = gtd_order.order_create_transaction.id
            print(f"✅ GTD limit order created: {gtd_order_id}")
            print(f"Expires: {gtd_order.order_create_transaction.gtd_time}")

        # Section 3: Stop orders
        print("\n=== 3. Stop Orders ===")

        # Stop-entry order (buy above market for breakout)
        stop_entry_price = current_ask + Decimal("0.0030")  # 30 pips above

        print(f"Placing stop-entry order at {stop_entry_price}")

        stop_order = await client.orders.post_stop_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=stop_entry_price,
            time_in_force=TimeInForce.GTC,
            client_extensions=ClientExtensions(comment="Breakout entry")
        )

        stop_order_id = None
        if stop_order.order_create_transaction:
            stop_order_id = stop_order.order_create_transaction.id
            print(f"✅ Stop order created: {stop_order_id}")
            print(f"Trigger Price: {stop_order.order_create_transaction.price}")

        # Section 4: Market-if-touched (MIT) orders
        print("\n=== 4. Market-If-Touched Orders ===")

        # MIT below market (like limit but guarantees fill)
        mit_price = current_bid - Decimal("0.0015")

        print(f"Placing MIT order at {mit_price}")

        mit_order = await client.orders.post_market_if_touched_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000,
            price=mit_price,
            time_in_force=TimeInForce.GTC,
            take_profit_on_fill=TakeProfitDetails(price=str(mit_price + Decimal("0.0040"))),
            client_extensions=ClientExtensions(comment="MIT with TP")
        )

        mit_order_id = None
        if mit_order.order_create_transaction:
            mit_order_id = mit_order.order_create_transaction.id
            print(f"✅ MIT order created: {mit_order_id}")
            print(f"Trigger Price: {mit_order.order_create_transaction.price}")

        # Section 5: List and filter orders
        print("\n=== 5. List and Filter Orders ===")

        # Get all orders
        all_orders = await client.orders.get_orders(account_id=client.account_id)
        print(f"\nTotal orders: {len(all_orders.get('orders', []))}")

        # Filter by instrument
        eur_orders = await client.orders.get_orders(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD
        )
        print(f"EUR/USD orders: {len(eur_orders.get('orders', []))}")

        # Filter by state
        pending_orders = await client.orders.get_orders(
            account_id=client.account_id,
            state="PENDING"
        )
        print(f"Pending orders: {len(pending_orders.get('orders', []))}")

        # Section 6: Get pending orders
        print("\n=== 6. Pending Orders ===")

        pending = await client.orders.get_pending_orders(account_id=client.account_id)
        pending_list = pending.get("orders", [])

        print(f"\nFound {len(pending_list)} pending order(s):")
        for order in pending_list[:5]:  # Show first 5
            print(f"\n  Order {order.id}:")
            print(f"    Type: {order.type}")
            print(f"    Instrument: {order.instrument}")
            print(f"    Units: {order.units}")
            if hasattr(order, 'price'):
                print(f"    Price: {order.price}")
            print(f"    Time in Force: {order.time_in_force}")

        # Section 7: Get specific order details
        print("\n=== 7. Order Details ===")

        if limit_order_id:
            order_details = await client.orders.get_order(
                account_id=client.account_id,
                order_specifier=limit_order_id
            )
            order = order_details["order"]
            print(f"\nDetails for order {order.id}:")
            print(f"  Type: {order.type}")
            print(f"  State: {order.state}")
            print(f"  Instrument: {order.instrument}")
            print(f"  Units: {order.units}")
            print(f"  Price: {order.price}")
            print(f"  Created: {order.create_time}")

        # Section 8: Modify an existing order
        print("\n=== 8. Modify Order ===")

        if limit_order_id:
            # Change the limit price
            new_price = current_bid - Decimal("0.0025")
            print(f"\nModifying limit order {limit_order_id}")
            print(f"New price: {new_price}")

            modify_response = await client.orders.put_order(
                account_id=client.account_id,
                order_specifier=limit_order_id,
                order_request={
                    "order": {
                        "type": "LIMIT",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "price": str(new_price),
                        "timeInForce": "GTC"
                    }
                }
            )

            if modify_response.get("orderCreateTransaction"):
                print(f"✅ Order modified successfully")
                print(f"New Order ID: {modify_response['orderCreateTransaction'].id}")

        # Section 9: Update order client extensions
        print("\n=== 9. Update Client Extensions ===")

        if gtd_order_id:
            print(f"\nUpdating client extensions for order {gtd_order_id}")

            extension_response = await client.orders.put_order_client_extensions(
                account_id=client.account_id,
                order_specifier=gtd_order_id,
                client_extensions=ClientExtensions(
                    comment="Updated: High priority order",
                    tag="priority-high"
                )
            )

            if extension_response.get("orderClientExtensionsModifyTransaction"):
                print(f"✅ Client extensions updated")

        # Section 10: Cancel orders
        print("\n=== 10. Cancel Orders ===")

        # Cancel all our test orders
        orders_to_cancel = [id for id in [limit_order_id, gtd_order_id, stop_order_id, mit_order_id] if id]

        for order_id in orders_to_cancel:
            print(f"\nCancelling order {order_id}")
            cancel_response = await client.orders.cancel_order(
                account_id=client.account_id,
                order_specifier=order_id
            )

            if cancel_response.get("orderCancelTransaction"):
                print(f"✅ Order {order_id} cancelled")

        # Section 11: Complex order strategies
        print("\n=== 11. Complex Order Strategies ===")

        print("\nBracket Order Strategy:")
        print("  1. Entry: Market order")
        print("  2. Take Profit: Automatically placed on fill")
        print("  3. Stop Loss: Automatically placed on fill")
        print("  ✅ Demonstrated in Section 1")

        print("\nOCO (One-Cancels-Other):")
        print("  - Place a take-profit limit order")
        print("  - Place a stop-loss stop order")
        print("  - When one fills, the other is automatically cancelled")
        print("  ✅ OANDA handles this automatically with TP/SL on trades")

        print("\nTrailing Stop (via Trade Management):")
        print("  - Place order to open position")
        print("  - Use client.trades.put_trade_orders() to add trailing stop")
        print("  - Stop automatically follows price movements")

        # Close our test position
        print("\n\nCleaning up: Closing EUR/USD position...")
        close_response = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000
        )

        if close_response.order_fill_transaction:
            print(f"✅ Position closed")

    print("\n✅ Advanced order management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
