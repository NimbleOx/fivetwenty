"""
OANDA Advanced Order Management Example

This example demonstrates advanced order management capabilities including
pending orders, order replacement, and client extensions.
"""

import asyncio
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID


async def main() -> None:
    """Demonstrate advanced order management operations."""

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

        # 1. List all pending orders
        print("1. Listing all pending orders:")
        pending = await client.orders.get_pending_orders(account_id)
        pending_orders = pending.get("orders", [])

        if not pending_orders:
            print("   No pending orders")
        else:
            for order in pending_orders:
                order_type = order.get("type", "UNKNOWN")
                instrument = order.get("instrument", "N/A")
                units = order.get("units", "0")
                order_id = order.get("id", "N/A")

                print(f"   Order {order_id}:")
                print(f"     Type: {order_type}")
                print(f"     Instrument: {instrument}")
                print(f"     Units: {units}")

                # Show price for limit/stop orders
                if order_type in ["LIMIT", "STOP", "MARKET_IF_TOUCHED"]:
                    price = order.get("price", "N/A")
                    print(f"     Price: {price}")

                # Show time in force
                tif = order.get("timeInForce", "N/A")
                print(f"     Time in Force: {tif}")
                print()

        # 2. Order replacement example
        print("2. Order replacement example:")
        print("   NOTE: This demonstrates the replacement pattern")

        if pending_orders:
            # Use first pending order for demonstration
            original_order = pending_orders[0]
            order_id = original_order["id"]
            original_type = original_order.get("type", "UNKNOWN")
            original_instrument = original_order.get("instrument", "EUR_USD")
            original_units = original_order.get("units", "1000")

            print(f"   Original order {order_id}:")
            print(f"     Type: {original_type}")
            print(f"     Instrument: {original_instrument}")
            print(f"     Units: {original_units}")

            # Example: How to replace with a different price/type
            print("\n   Example replacement (DEMO - not executed):")
            print("""
   # Replace a LIMIT order with updated price
   replacement_order = {
       "type": "LIMIT",
       "instrument": original_instrument,
       "units": original_units,
       "price": "1.12500",  # New price
       "timeInForce": "GTC"
   }

   result = await client.orders.replace(
       account_id,
       order_id,
       replacement_order,
       client_request_id="my_replace_123"
   )
            """)

            # Example: Replace with take profit and stop loss
            print("\n   Example: Replace with TP/SL (DEMO):")
            print("""
   # Add protective orders to existing order
   replacement_with_protection = {
       "type": "LIMIT",
       "instrument": "EUR_USD",
       "units": "1000",
       "price": "1.12000",
       "timeInForce": "GTC",
       "takeProfitOnFill": {
           "price": "1.13000",
           "timeInForce": "GTC"
       },
       "stopLossOnFill": {
           "price": "1.11000",
           "timeInForce": "GTC"
       }
   }

   result = await client.orders.replace(
       account_id,
       order_id,
       replacement_with_protection
   )
            """)
        else:
            print("   No pending orders available for replacement demo")

        # 3. Client extensions example
        print("\n3. Client extensions example:")
        print("   Client extensions allow custom metadata on orders/trades")

        if pending_orders:
            order_id = pending_orders[0]["id"]
            print(f"\n   Updating extensions for order {order_id}:")

            print("""
   # Example: Add tracking metadata (DEMO - not executed)
   order_extensions = {
       "id": "strategy_123",
       "tag": "breakout_v2",
       "comment": "EUR momentum play"
   }

   trade_extensions = {
       "id": "trade_tracking_456",
       "tag": "breakout_result",
       "comment": "Filled from breakout strategy"
   }

   await client.orders.update_client_extensions(
       account_id,
       order_id,
       client_extensions=order_extensions,
       trade_client_extensions=trade_extensions
   )
            """)
        else:
            print("   No orders available for client extensions demo")

        # 4. Using client order IDs
        print("\n4. Using client-provided order IDs:")
        print("""
   OANDA supports client-provided order identifiers using @clientID format:

   # Create order with client ID
   order_request = {
       "type": "LIMIT",
       "instrument": "EUR_USD",
       "units": "1000",
       "price": "1.12000",
       "clientExtensions": {
           "id": "my_custom_order_001",
           "tag": "strategy_xyz"
       }
   }

   # Later, reference by client ID
   await client.orders.get(account_id, "@my_custom_order_001")
   await client.orders.cancel(account_id, "@my_custom_order_001")
   await client.orders.replace(account_id, "@my_custom_order_001", new_order)
        """)

        # 5. Order filtering strategies
        print("\n5. Order filtering and management patterns:")

        # Get regular pending orders (already shown above)
        all_orders = await client.orders.get_orders(account_id, state="ALL", count=100)
        all_order_list = all_orders if isinstance(all_orders, list) else []

        # Count by state
        pending_count = len([o for o in all_order_list if o.get("state") == "PENDING"])
        filled_count = len([o for o in all_order_list if o.get("state") == "FILLED"])
        cancelled_count = len([o for o in all_order_list if o.get("state") == "CANCELLED"])

        print("   Order statistics:")
        print(f"     Pending: {pending_count}")
        print(f"     Filled: {filled_count}")
        print(f"     Cancelled: {cancelled_count}")

        # 6. Advanced replacement patterns
        print("\n6. Advanced order replacement patterns:")
        print("""
   Common replacement scenarios:

   1. Update price on pending limit order:
      - Replace with same type but new price

   2. Convert order type:
      - Replace LIMIT with STOP order
      - Convert to MARKET_IF_TOUCHED

   3. Add protection:
      - Add take profit to existing order
      - Add stop loss or trailing stop

   4. Change size:
      - Increase/decrease units
      - Split into multiple orders

   5. Update expiry:
      - Change from GTC to GTD
      - Update GTD time
        """)

        # 7. Best practices
        print("\n7. Best practices for order management:")
        print("""
   - Use client extensions for tracking and reporting
   - Implement idempotency with client request IDs
   - Always handle 404 errors when replacing/updating orders
   - Monitor pending order count to avoid limits
   - Use atomic replacement instead of cancel + create
   - Cache order IDs for efficient management
   - Implement order state machine for complex strategies
        """)

        print("\nAdvanced order management demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
