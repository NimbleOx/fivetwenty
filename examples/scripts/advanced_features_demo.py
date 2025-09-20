"""
OANDA Advanced Features Demonstration

This example demonstrates advanced order management features including:
- GTD/GFD time-in-force options with timezone handling
- Trigger conditions (BID, ASK, MID, INVERSE)
- Comprehensive error handling and edge cases
- Best practices for robust order management

Features covered:
✅ GTD (Good Till Date) orders with automatic expiration
✅ GFD (Good For Day) orders
✅ Trigger condition testing and validation
✅ Error scenario handling and recovery
✅ Timeout management and resilience
"""

import asyncio
import contextlib
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import AccountID, LimitOrderRequest, MarketIfTouchedOrderRequest, StopOrderRequest


async def demonstrate_gtd_orders(client: AsyncClient, account_id: AccountID, instrument: str) -> list[str]:
    """Demonstrate GTD (Good Till Date) order functionality."""
    print("\n" + "=" * 50)
    print("🕐 GTD (Good Till Date) Orders Demonstration")
    print("=" * 50)

    created_orders = []

    try:
        # Get current pricing
        pricing = await client.pricing.get_pricing(account_id, [instrument])
        current_price = Decimal(str(pricing[0]["closeoutBid"]))
        print(f"📊 Current {instrument} price: {current_price}")

        # 1. GTD order with 2-minute expiration
        print("\n1. Creating GTD order with 2-minute expiration...")
        gtd_time = datetime.now(timezone.utc) + timedelta(minutes=2)
        gtd_time_str = gtd_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        gtd_order = LimitOrderRequest(
            instrument=instrument,
            units=1000,
            price=str(current_price - Decimal("0.0050")),  # 50 pips below market
            timeInForce="GTD",
            gtdTime=gtd_time_str,
        )

        response = await client.orders.post_order(account_id, gtd_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ GTD order created: {order_id}")
            print(f"   Expires at: {gtd_time_str}")
            print(f"   Price: {current_price - Decimal('0.0050')}")

        # 2. GFD (Good For Day) order
        print("\n2. Creating GFD (Good For Day) order...")
        gfd_order = LimitOrderRequest(
            instrument=instrument,
            units=1000,
            price=str(current_price - Decimal("0.0040")),  # 40 pips below market
            timeInForce="GFD",
        )

        response = await client.orders.post_order(account_id, gfd_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ GFD order created: {order_id}")
            print("   Expires: End of trading day")

        # 3. Invalid GTD handling
        print("\n3. Testing invalid GTD datetime handling...")
        try:
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            past_time_str = past_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            invalid_gtd = LimitOrderRequest(instrument=instrument, units=1000, price=str(current_price - Decimal("0.0020")), timeInForce="GTD", gtdTime=past_time_str)

            await client.orders.post_order(account_id, invalid_gtd)
            print("⚠️ Invalid GTD order was unexpectedly accepted")
        except FiveTwentyError as e:
            print(f"✅ Invalid GTD properly rejected: {type(e).__name__}")

    except Exception as e:
        print(f"❌ GTD demonstration error: {e}")

    return created_orders


async def demonstrate_trigger_conditions(client: AsyncClient, account_id: AccountID, instrument: str) -> list[str]:
    """Demonstrate trigger condition functionality."""
    print("\n" + "=" * 50)
    print("🎯 Trigger Conditions Demonstration")
    print("=" * 50)

    created_orders = []

    try:
        # Get current pricing for trigger levels
        pricing = await client.pricing.get_pricing(account_id, [instrument])
        price_data = pricing[0]
        bid_price = Decimal(str(price_data["bid"]))
        ask_price = Decimal(str(price_data["ask"]))
        current_price = (bid_price + ask_price) / 2

        print(f"📊 Current pricing - Bid: {bid_price}, Ask: {ask_price}, Mid: {current_price}")

        # 1. DEFAULT trigger condition
        print("\n1. Creating order with DEFAULT trigger condition...")
        default_order = StopOrderRequest(
            instrument=instrument,
            units=1000,
            price=str(ask_price + Decimal("0.0050")),  # Above current ask
            timeInForce="GTC",
            triggerCondition="DEFAULT",
        )

        response = await client.orders.post_order(account_id, default_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ DEFAULT trigger order: {order_id}")

        # 2. BID trigger condition
        print("\n2. Creating order with BID trigger condition...")
        bid_order = LimitOrderRequest(
            instrument=instrument,
            units=-1000,  # Sell limit
            price=str(bid_price + Decimal("0.0030")),  # Above current bid
            timeInForce="GTC",
            triggerCondition="BID",
        )

        response = await client.orders.post_order(account_id, bid_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ BID trigger order: {order_id}")

        # 3. ASK trigger condition
        print("\n3. Creating order with ASK trigger condition...")
        ask_order = StopOrderRequest(
            instrument=instrument,
            units=-800,  # Sell stop
            price=str(ask_price - Decimal("0.0040")),  # Below current ask
            timeInForce="GTC",
            triggerCondition="ASK",
        )

        response = await client.orders.post_order(account_id, ask_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ ASK trigger order: {order_id}")

        # 4. MID trigger condition
        print("\n4. Creating order with MID trigger condition...")
        mid_order = MarketIfTouchedOrderRequest(
            instrument=instrument,
            units=1200,  # Buy MIT
            price=str(current_price - Decimal("0.0020")),  # Below current mid
            timeInForce="GTC",
            triggerCondition="MID",
        )

        response = await client.orders.post_order(account_id, mid_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ MID trigger order: {order_id}")

        # 5. INVERSE trigger condition
        print("\n5. Creating order with INVERSE trigger condition...")
        inverse_order = StopOrderRequest(
            instrument=instrument,
            units=600,  # Buy stop
            price=str(current_price + Decimal("0.0060")),  # Above current price
            timeInForce="GTC",
            triggerCondition="INVERSE",
        )

        response = await client.orders.post_order(account_id, inverse_order)
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            created_orders.append(order_id)
            print(f"✅ INVERSE trigger order: {order_id}")

        # 6. Invalid trigger condition
        print("\n6. Testing invalid trigger condition...")
        try:
            invalid_trigger = LimitOrderRequest(instrument=instrument, units=100, price=str(current_price - Decimal("0.0050")), timeInForce="GTC", triggerCondition="INVALID_CONDITION")

            await client.orders.post_order(account_id, invalid_trigger)
            print("⚠️ Invalid trigger condition was unexpectedly accepted")
        except Exception as e:
            print(f"✅ Invalid trigger condition properly rejected: {type(e).__name__}")

    except Exception as e:
        print(f"❌ Trigger condition demonstration error: {e}")

    return created_orders


async def demonstrate_error_scenarios(client: AsyncClient, account_id: AccountID, instrument: str):
    """Demonstrate comprehensive error handling."""
    print("\n" + "=" * 50)
    print("⚠️  Error Scenarios & Recovery Demonstration")
    print("=" * 50)

    # Get current pricing for realistic error testing
    try:
        pricing = await client.pricing.get_pricing(account_id, [instrument])
        current_price = Decimal(str(pricing[0]["closeoutBid"]))
        print(f"📊 Using {instrument} price: {current_price}")
    except Exception as e:
        print(f"⚠️ Pricing error: {e}")
        current_price = Decimal("1.1000")  # Fallback

    # 1. Invalid instrument
    print("\n1. Testing invalid instrument handling...")
    try:
        invalid_order = LimitOrderRequest(instrument="INVALID_INSTRUMENT", units=1000, price=str(current_price), timeInForce="GTC")
        await client.orders.post_order(account_id, invalid_order)
        print("⚠️ Invalid instrument unexpectedly accepted")
    except FiveTwentyError as e:
        print(f"✅ Invalid instrument properly rejected: {type(e).__name__}")

    # 2. Invalid account ID
    print("\n2. Testing invalid account ID...")
    try:
        valid_order = LimitOrderRequest(instrument=instrument, units=1000, price=str(current_price - Decimal("0.0050")), timeInForce="GTC")
        await client.orders.post_order("INVALID-ACCOUNT-ID", valid_order)
        print("⚠️ Invalid account ID unexpectedly accepted")
    except FiveTwentyError as e:
        print(f"✅ Invalid account ID properly rejected: {type(e).__name__}")

    # 3. Invalid price formats
    print("\n3. Testing invalid price formats...")
    invalid_prices = ["not_a_number", "-1.0000", "0.0000", "999999.9999"]

    for invalid_price in invalid_prices:
        try:
            invalid_order = LimitOrderRequest(instrument=instrument, units=1000, price=invalid_price, timeInForce="GTC")
            await client.orders.post_order(account_id, invalid_order)
            print(f"⚠️ Invalid price {invalid_price} unexpectedly accepted")
        except Exception as e:
            print(f"✅ Invalid price {invalid_price} rejected: {type(e).__name__}")

    # 4. Invalid order ID operations
    print("\n4. Testing invalid order ID operations...")
    invalid_ids = ["INVALID_ORDER_ID", "99999999", "0", "-1"]

    for invalid_id in invalid_ids:
        try:
            await client.orders.get_order(account_id, invalid_id)
            print(f"⚠️ Invalid ID {invalid_id} get unexpectedly successful")
        except FiveTwentyError as e:
            print(f"✅ Invalid ID {invalid_id} get rejected: {type(e).__name__}")

    # 5. Network timeout simulation
    print("\n5. Testing timeout handling...")
    try:
        timeout_order = LimitOrderRequest(instrument=instrument, units=1000, price=str(current_price - Decimal("0.0050")), timeInForce="GTC")

        # Use extremely short timeout
        response = await client.orders.post_order(
            account_id=account_id,
            order_request=timeout_order,
            timeout=0.001,  # 1 millisecond
        )
        print("⚠️ Order with tiny timeout unexpectedly succeeded")

        # Clean up if somehow succeeded
        if response.order_create_transaction:
            order_id = response.order_create_transaction["id"]
            with contextlib.suppress(Exception):
                await client.orders.cancel_order(account_id, order_id)
    except Exception as e:
        print(f"✅ Timeout properly handled: {type(e).__name__}")


async def cleanup_orders(client: AsyncClient, account_id: AccountID, order_ids: list[str]):
    """Clean up test orders."""
    if not order_ids:
        return

    print(f"\n🧹 Cleaning up {len(order_ids)} test orders...")

    for order_id in order_ids:
        try:
            await client.orders.cancel_order(account_id, order_id)
            print(f"✅ Cancelled order: {order_id}")
        except Exception as e:
            print(f"⚠️ Could not cancel {order_id}: {type(e).__name__}")


async def main():
    """Main demonstration function."""
    # Get token from environment
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("❌ Please set FIVETWENTY_OANDA_TOKEN environment variable")
        print("   export FIVETWENTY_OANDA_TOKEN='your-token-here'")
        return

    print("🚀 OANDA Advanced Features Demonstration")
    print("=" * 60)

    # Use practice environment for safety
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get account ID
        accounts = await client.accounts.get_accounts()
        if not accounts:
            print("❌ No accounts available")
            return

        account_id = AccountID(accounts[0].id)
        instrument = "EUR_USD"  # Use major pair for demonstration

        print(f"📋 Account: {account_id}")
        print(f"💱 Instrument: {instrument}")

        all_created_orders = []

        try:
            # Demonstrate advanced features
            gtd_orders = await demonstrate_gtd_orders(client, account_id, instrument)
            all_created_orders.extend(gtd_orders)

            trigger_orders = await demonstrate_trigger_conditions(client, account_id, instrument)
            all_created_orders.extend(trigger_orders)

            await demonstrate_error_scenarios(client, account_id, instrument)

            # Show summary
            print("\n" + "=" * 60)
            print("📊 DEMONSTRATION SUMMARY")
            print("=" * 60)
            print(f"✅ GTD/GFD Orders: {len(gtd_orders)} created")
            print(f"✅ Trigger Conditions: {len(trigger_orders)} created")
            print("✅ Error Scenarios: Comprehensive testing completed")
            print(f"📝 Total Orders: {len(all_created_orders)} test orders")

            print("\n🎯 KEY LEARNINGS:")
            print("• GTD orders provide precise expiration control")
            print("• Trigger conditions offer sophisticated execution logic")
            print("• Robust error handling ensures application stability")
            print("• Timeout management prevents hanging operations")
            print("• Proper validation catches issues before API calls")

        finally:
            # Always clean up test orders
            await cleanup_orders(client, account_id, all_created_orders)

    print("\n✅ Advanced features demonstration completed!")
    print("💡 Ready to implement advanced order management in your trading application!")


if __name__ == "__main__":
    asyncio.run(main())
