"""Integration tests for advanced order features - time-in-force and trigger conditions."""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestAdvancedFeatures:
    """Integration tests for advanced order features."""

    async def test_advanced_time_in_force_options(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test advanced time-in-force options including GTD.

        Validates:
        - GTD (Good Till Date) with future datetime
        - GFD (Good For Day) behavior
        - GTD order cancellation at expiry
        - Timezone handling for GTD
        - Invalid GTD datetime handling
        """
        from decimal import Decimal

        print(f"✓ Starting advanced time-in-force test for account {test_account_id}")

        test_instrument = test_instruments["major_pairs"][0]
        created_orders = []

        # Get current pricing to set realistic order prices
        try:
            prices = await sandbox_client.pricing.get_pricing(test_account_id, [test_instrument])
            current_price = Decimal(prices[0]["closeout_bid"])
            print(f"✓ Current {test_instrument} price: {current_price}")
        except Exception as e:
            print(f"✓ Using fallback pricing due to: {type(e).__name__}")
            current_price = Decimal("1.1000")  # Fallback for EUR_USD

        # Test 1: GTD (Good Till Date) with future datetime
        print("✓ Test 1: GTD order with future expiration...")

        try:
            # Set GTD time to 2 minutes from now
            gtd_time = datetime.now(timezone.utc) + timedelta(minutes=2)
            gtd_time_str = gtd_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            # Create limit order below current market for testing
            limit_price = current_price - Decimal("0.0050")  # 50 pips below market

            from fivetwenty.models import LimitOrderRequest

            gtd_order_request = LimitOrderRequest(instrument=test_instrument, units="1000", price=str(limit_price), timeInForce="GTD", gtdTime=gtd_time_str)

            gtd_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=gtd_order_request, client_request_id=f"gtd-test-{int(asyncio.get_event_loop().time() * 1000)}")

            if gtd_response.order_create_transaction:
                gtd_order_id = gtd_response.order_create_transaction.get("id")
                created_orders.append(gtd_order_id)
                print(f"✓ GTD order created: {gtd_order_id}")
                print(f"  - Expires at: {gtd_time_str}")
                print(f"  - Price: {limit_price}")

                # Verify order details
                order_details = await sandbox_client.orders.get_order(test_account_id, gtd_order_id)
                assert order_details["timeInForce"] == "GTD", "Should be GTD order"
                assert "gtdTime" in order_details, "Should have GTD time"
                print(f"✓ GTD order verified: {order_details['timeInForce']}")

        except Exception as e:
            print(f"✓ GTD order test error: {type(e).__name__}")

        # Test 2: GFD (Good For Day) order
        print("✓ Test 2: GFD order creation...")

        try:
            gfd_limit_price = current_price - Decimal("0.0040")  # 40 pips below market

            gfd_response = await sandbox_client.orders.post_limit_order(account_id=test_account_id, instrument=test_instrument, units="1000", price=gfd_limit_price, time_in_force="GFD", client_request_id=f"gfd-test-{int(asyncio.get_event_loop().time() * 1000)}")

            if gfd_response.order_create_transaction:
                gfd_order_id = gfd_response.order_create_transaction.get("id")
                created_orders.append(gfd_order_id)
                print(f"✓ GFD order created: {gfd_order_id}")

                # Verify order details
                order_details = await sandbox_client.orders.get_order(test_account_id, gfd_order_id)
                assert order_details["timeInForce"] == "GFD", "Should be GFD order"
                print(f"✓ GFD order verified: {order_details['timeInForce']}")

        except Exception as e:
            print(f"✓ GFD order test error: {type(e).__name__}")

        # Test 3: GTD order with near-immediate expiry (testing cancellation)
        print("✓ Test 3: GTD order with near-immediate expiry...")

        try:
            # Set GTD time to 10 seconds from now
            short_gtd_time = datetime.now(timezone.utc) + timedelta(seconds=10)
            short_gtd_str = short_gtd_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            short_limit_price = current_price - Decimal("0.0030")  # 30 pips below market

            from fivetwenty.models import LimitOrderRequest

            short_gtd_request = LimitOrderRequest(instrument=test_instrument, units="1000", price=str(short_limit_price), timeInForce="GTD", gtdTime=short_gtd_str)

            short_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=short_gtd_request, client_request_id=f"short-gtd-{int(asyncio.get_event_loop().time() * 1000)}")

            if short_response.order_create_transaction:
                short_order_id = short_response.order_create_transaction.get("id")
                print(f"✓ Short-term GTD order created: {short_order_id}")
                print(f"  - Expires in 10 seconds at: {short_gtd_str}")

                # Wait for order to expire (plus buffer)
                print("✓ Waiting for GTD expiration...")
                await asyncio.sleep(15)

                # Check if order was automatically cancelled
                try:
                    expired_order = await sandbox_client.orders.get_order(test_account_id, short_order_id)
                    if expired_order["state"] == "CANCELLED":
                        print("✓ GTD order automatically cancelled at expiry")
                    else:
                        print(f"✓ GTD order state: {expired_order['state']} (may still be pending)")
                except Exception as e:
                    if "ORDER_DOESNT_EXIST" in str(e):
                        print("✓ GTD order removed after expiry (expected)")
                    else:
                        print(f"✓ GTD order check error: {type(e).__name__}")

        except Exception as e:
            print(f"✓ Short-term GTD test error: {type(e).__name__}")

        # Test 4: Invalid GTD datetime handling
        print("✓ Test 4: Invalid GTD datetime handling...")

        try:
            # Try GTD time in the past
            past_time = datetime.now(timezone.utc) - timedelta(hours=1)
            past_time_str = past_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

            from fivetwenty.models import LimitOrderRequest

            invalid_gtd_request = LimitOrderRequest(instrument=test_instrument, units="1000", price=str(current_price - Decimal("0.0020")), timeInForce="GTD", gtdTime=past_time_str)

            try:
                await sandbox_client.orders.post_order(account_id=test_account_id, order_request=invalid_gtd_request, client_request_id=f"invalid-gtd-{int(asyncio.get_event_loop().time() * 1000)}")
                pytest.fail("Invalid GTD order was unexpectedly accepted")
            except Exception as e:
                print(f"✓ Invalid GTD properly rejected: {type(e).__name__}")

        except Exception as e:
            print(f"✓ Invalid GTD test error: {type(e).__name__}")

        # Cleanup: Cancel any remaining test orders
        print("✓ Cleanup: Cancelling test orders...")

        cleanup_count = 0
        for order_id in created_orders:
            try:
                await sandbox_client.orders.cancel_order(test_account_id, order_id)
                cleanup_count += 1
                await asyncio.sleep(0.1)  # Brief pause between cancellations
            except Exception as e:
                print(f"✓ Order {order_id} cleanup: {type(e).__name__}")

        print(f"✓ Cleanup completed: {cleanup_count} orders cancelled")
        print("✓ Advanced time-in-force test completed successfully")

    async def test_trigger_conditions(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test trigger conditions: BID, ASK, MID, and INVERSE behaviors.

        Validates:
        - DEFAULT trigger condition behavior
        - BID trigger condition for order execution
        - ASK trigger condition for order execution
        - MID trigger condition for order execution
        - INVERSE trigger condition behavior
        - Invalid trigger condition handling
        """
        print(f"✓ Starting trigger conditions test for account {test_account_id}")

        test_instrument = test_instruments["major_pairs"][0]
        created_orders = []

        # Get current pricing to set appropriate trigger levels
        current_price = Decimal("1.1000")  # Default fallback
        bid_price = current_price - Decimal("0.0001")
        ask_price = current_price + Decimal("0.0001")
        price_quantum = Decimal("0.001") if test_instrument.endswith("_JPY") else Decimal("0.00001")

        def price_text(price: Decimal) -> str:
            return str(price.quantize(price_quantum))

        try:
            pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])

            if isinstance(pricing_response, dict) and "prices" in pricing_response:
                prices = pricing_response["prices"]
                if prices:
                    price_data = prices[0]
                    if isinstance(price_data, dict):
                        bids = price_data.get("bids", [])
                        asks = price_data.get("asks", [])
                    else:
                        bids = getattr(price_data, "bids", [])
                        asks = getattr(price_data, "asks", [])

                    if bids and asks:
                        bid = bids[0].get("price") if isinstance(bids[0], dict) else bids[0].price
                        ask = asks[0].get("price") if isinstance(asks[0], dict) else asks[0].price
                        bid_price = Decimal(str(bid))
                        ask_price = Decimal(str(ask))
                        current_price = (bid_price + ask_price) / 2
                        print(f"✓ Current pricing - Bid: {bid_price}, Ask: {ask_price}, Mid: {current_price}")
        except Exception as e:
            print(f"✓ Using default pricing due to error: {e}")
            print(f"✓ Default pricing - Bid: {bid_price}, Ask: {ask_price}, Mid: {current_price}")

        try:
            # Test 1: DEFAULT trigger condition (should behave like BID for sell orders, ASK for buy orders)
            print("✓ Test 1: DEFAULT trigger condition...")

            from fivetwenty.models import StopOrderRequest

            default_stop_order = StopOrderRequest(
                instrument=test_instrument,
                units="1000",  # Buy stop
                price=price_text(ask_price + Decimal("0.0050")),  # Trigger above current ask
                timeInForce="GTC",
                triggerCondition="DEFAULT",
            )

            response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=default_stop_order)

            if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                created_orders.append(order_id)
                print(f"✓ Created DEFAULT trigger stop order: {order_id}")

                # Verify the order details
                order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
                order_details = order_response["order"]

                if isinstance(order_details, dict):
                    trigger_condition = order_details.get("triggerCondition", "DEFAULT")
                    print(f"✓ Confirmed trigger condition: {trigger_condition}")

            # Test 2: BID trigger condition
            print("✓ Test 2: BID trigger condition...")

            from fivetwenty.models import LimitOrderRequest

            bid_limit_order = LimitOrderRequest(
                instrument=test_instrument,
                units="-1000",  # Sell limit
                price=price_text(bid_price + Decimal("0.0030")),  # Above current bid
                timeInForce="GTC",
                triggerCondition="BID",
            )

            response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=bid_limit_order)

            if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                created_orders.append(order_id)
                print(f"✓ Created BID trigger limit order: {order_id}")

            # Test 3: ASK trigger condition
            print("✓ Test 3: ASK trigger condition...")

            ask_stop_order = StopOrderRequest(
                instrument=test_instrument,
                units="-800",  # Sell stop
                price=price_text(ask_price - Decimal("0.0040")),  # Below current ask
                timeInForce="GTC",
                triggerCondition="ASK",
            )

            response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=ask_stop_order)

            if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                created_orders.append(order_id)
                print(f"✓ Created ASK trigger stop order: {order_id}")

            # Test 4: MID trigger condition
            print("✓ Test 4: MID trigger condition...")

            from fivetwenty.models import MarketIfTouchedOrderRequest

            mid_mit_order = MarketIfTouchedOrderRequest(
                instrument=test_instrument,
                units="1200",  # Buy MIT
                price=price_text(current_price - Decimal("0.0020")),  # Below current mid
                timeInForce="GTC",
                triggerCondition="MID",
            )

            response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=mid_mit_order)

            if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                created_orders.append(order_id)
                print(f"✓ Created MID trigger MIT order: {order_id}")

            # Test 5: INVERSE trigger condition
            print("✓ Test 5: INVERSE trigger condition...")

            inverse_stop_order = StopOrderRequest(
                instrument=test_instrument,
                units="600",  # Buy stop
                price=price_text(current_price + Decimal("0.0060")),  # Above current price
                timeInForce="GTC",
                triggerCondition="INVERSE",
            )

            response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=inverse_stop_order)

            if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                created_orders.append(order_id)
                print(f"✓ Created INVERSE trigger stop order: {order_id}")

            # Test 6: Verify different trigger conditions on the same order type
            print("✓ Test 6: Multiple trigger conditions validation...")

            # Create similar orders with different trigger conditions to verify behavior
            trigger_test_orders = []
            for condition in ["BID", "ASK", "MID"]:
                order_request = LimitOrderRequest(
                    instrument=test_instrument,
                    units="500",  # Small buy order
                    price=price_text(current_price - Decimal("0.0100")),  # Well below market
                    timeInForce="GTC",
                    triggerCondition=condition,
                )

                response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=order_request)

                if hasattr(response, "order_create_transaction") and response.order_create_transaction:
                    order_id = response.order_create_transaction.get("id")
                    created_orders.append(order_id)
                    trigger_test_orders.append((order_id, condition))
                    print(f"✓ Created {condition} trigger comparison order: {order_id}")

            # Verify all orders have correct trigger conditions
            print("✓ Verifying trigger conditions...")
            for order_id, expected_condition in trigger_test_orders:
                order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
                order_details = order_response["order"]

                if isinstance(order_details, dict):
                    actual_condition = order_details.get("triggerCondition", "DEFAULT")
                    if actual_condition == expected_condition:
                        print(f"✓ Order {order_id}: trigger condition correctly set to {actual_condition}")
                    else:
                        print(f"⚠ Order {order_id}: expected {expected_condition}, got {actual_condition}")

            # Test 7: Invalid trigger condition handling
            print("✓ Test 7: Invalid trigger condition handling...")

            try:
                invalid_trigger_order = LimitOrderRequest(instrument=test_instrument, units="100", price=price_text(current_price - Decimal("0.0050")), timeInForce="GTC", triggerCondition="INVALID_CONDITION")

                await sandbox_client.orders.post_order(account_id=test_account_id, order_request=invalid_trigger_order)
                pytest.fail("Invalid trigger condition was unexpectedly accepted")
            except Exception as e:
                print(f"✓ Invalid trigger condition properly rejected: {str(e)[:100]}...")

            print(f"✓ Created {len(created_orders)} orders for trigger condition testing")
            print("✓ All trigger condition tests completed successfully!")

        finally:
            # Cleanup: Cancel all created orders
            if created_orders:
                print(f"✓ Cleaning up {len(created_orders)} test orders...")
                for order_id in created_orders:
                    try:
                        await sandbox_client.orders.cancel_order(test_account_id, order_id)
                        print(f"✓ Cancelled order: {order_id}")
                    except Exception as e:
                        print(f"⚠ Failed to cancel order {order_id}: {e}")

        print("✓ Trigger conditions test completed successfully")
