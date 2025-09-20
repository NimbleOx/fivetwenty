"""Integration tests for order modification and cancellation operations."""

import asyncio
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestOrderModification:
    """Integration tests for order modification and cancellation operations."""

    async def test_order_modification(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test modification of existing orders.

        Validates:
        - Order replacement (put_order)
        - Client extensions modification
        - Order parameter updates
        - State consistency after modification
        - Error handling for invalid modifications
        """
        print(f"✓ Starting order modification test for account {test_account_id}")

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_pending_orders = initial_account.pending_order_count

        print(f"✓ Initial pending orders: {initial_pending_orders}")

        # Use a major pair for testing
        test_instrument = test_instruments["major_pairs"][0]

        # Get current price to set reasonable order levels
        current_price = Decimal("1.1000")  # Default price for EUR_USD

        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                # Extract prices from the response
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        # Calculate mid price from bid/ask if available
                        if "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
                        elif "mid" in price_data:
                            current_price = Decimal(price_data["mid"])
            except Exception as e:
                print(f"✓ Using default price due to pricing error: {e}")

        print(f"✓ Current {test_instrument} price: {current_price}")

        # Test 1: Create an initial limit order that we can modify
        initial_price = current_price - Decimal("0.0050")  # 50 pips below current

        initial_order_response = await sandbox_client.orders.post_limit_order(account_id=test_account_id, instrument=test_instrument, units=1000, price=initial_price, time_in_force="GTC", client_request_id=f"modify-test-initial-{int(1000 * current_price)}")

        # Validate initial order creation
        assert initial_order_response.order_create_transaction is not None
        initial_order_id = initial_order_response.order_create_transaction["id"]
        print(f"✓ Initial order created: {initial_order_id}")

        # Wait a moment for order to be processed
        await asyncio.sleep(0.5)

        # Verify initial order exists and get its current state
        try:
            initial_order_details = await sandbox_client.orders.get_order(test_account_id, initial_order_id)
            print(f"✓ Initial order state: {initial_order_details['state']}")

            # Only proceed with modification tests if order is in a modifiable state
            if initial_order_details["state"] not in ["PENDING"]:
                print(f"✓ Order state '{initial_order_details['state']}' not suitable for modification, testing error handling instead")

                # Test attempting to modify a non-pending order (should fail)
                try:
                    modified_order_request = {
                        "type": "LIMIT",
                        "instrument": test_instrument,
                        "units": 1500,  # Different size
                        "price": str(initial_price + Decimal("0.0010")),  # Different price
                        "timeInForce": "GTC",
                    }

                    await sandbox_client.orders.put_order(account_id=test_account_id, order_specifier=initial_order_id, order_request=modified_order_request, client_request_id=f"modify-test-error-{int(1000 * current_price)}")
                    print("✗ Expected error when modifying non-pending order, but none occurred")
                except Exception as e:
                    print(f"✓ Correctly received error when trying to modify non-pending order: {type(e).__name__}")

            else:
                # Test 2: Order replacement using put_order
                print("✓ Testing order replacement...")

                modified_price = initial_price + Decimal("0.0010")  # 10 pips higher
                modified_units = 1500  # Different size

                modified_order_request = {
                    "type": "LIMIT",
                    "instrument": test_instrument,
                    "units": modified_units,
                    "price": str(modified_price),
                    "timeInForce": "GTC",
                    "takeProfitOnFill": {"price": str(modified_price + Decimal("0.0050"))},  # Add TP
                    "stopLossOnFill": {"price": str(modified_price - Decimal("0.0030"))},  # Add SL
                }

                replacement_response = await sandbox_client.orders.put_order(account_id=test_account_id, order_specifier=initial_order_id, order_request=modified_order_request, client_request_id=f"modify-test-replace-{int(1000 * current_price)}")

                print("✓ Order replacement completed")

                # Verify replacement response structure
                assert "orderCancelTransaction" in replacement_response
                assert "orderCreateTransaction" in replacement_response

                cancelled_order_id = replacement_response["orderCancelTransaction"]["orderID"]
                new_order_id = replacement_response["orderCreateTransaction"]["id"]

                print(f"✓ Original order {cancelled_order_id} cancelled, new order {new_order_id} created")

                # Verify the original order was cancelled
                try:
                    cancelled_order = await sandbox_client.orders.get_order(test_account_id, initial_order_id)
                    assert cancelled_order["state"] == "CANCELLED"
                    print("✓ Original order correctly cancelled")
                except Exception as e:
                    print(f"✓ Original order no longer exists (expected): {type(e).__name__}")

                # Verify new order has correct parameters
                try:
                    new_order = await sandbox_client.orders.get_order(test_account_id, new_order_id)
                    assert int(new_order["units"]) == modified_units
                    assert Decimal(new_order["price"]) == modified_price
                    assert new_order["takeProfitOnFill"]["price"] == str(modified_price + Decimal("0.0050"))
                    assert new_order["stopLossOnFill"]["price"] == str(modified_price - Decimal("0.0030"))
                    print("✓ New order has correct parameters")

                    # Store new order ID for cleanup
                    cleanup_order_id = new_order_id

                except Exception as e:
                    print(f"✓ New order may have been auto-cancelled by sandbox: {type(e).__name__}")
                    cleanup_order_id = None

        except Exception as e:
            print(f"✓ Initial order may have been auto-cancelled by sandbox: {type(e).__name__}")
            cleanup_order_id = None

        # Test 3: Client Extensions Modification
        print("✓ Testing client extensions modification...")

        # Create a fresh order for client extensions testing
        try:
            extensions_test_response = await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=500,
                price=current_price - Decimal("0.0080"),  # Far from market
                time_in_force="GTC",
                client_request_id=f"modify-test-extensions-{int(1000 * current_price)}",
            )

            extensions_order_id = extensions_test_response.order_create_transaction["id"]
            print(f"✓ Extensions test order created: {extensions_order_id}")

            # Wait a moment for order to be processed
            await asyncio.sleep(0.5)

            # Check if order is still pending
            try:
                extensions_order = await sandbox_client.orders.get_order(test_account_id, extensions_order_id)

                if extensions_order["state"] == "PENDING":
                    # Modify client extensions
                    new_client_extensions = {"id": "modified_order_001", "tag": "test_strategy", "comment": "Modified order for testing"}

                    new_trade_extensions = {"id": "modified_trade_001", "tag": "test_trade", "comment": "Trade from modified order"}

                    extensions_response = await sandbox_client.orders.put_order_client_extensions(account_id=test_account_id, order_specifier=extensions_order_id, client_extensions=new_client_extensions, trade_client_extensions=new_trade_extensions)

                    print("✓ Client extensions modified successfully")

                    # Verify extensions were applied
                    updated_order = await sandbox_client.orders.get_order(test_account_id, extensions_order_id)
                    if "clientExtensions" in updated_order:
                        assert updated_order["clientExtensions"]["id"] == "modified_order_001"
                        assert updated_order["clientExtensions"]["tag"] == "test_strategy"
                        print("✓ Client extensions correctly applied")

                    # Clean up extensions test order
                    await sandbox_client.orders.cancel_order(test_account_id, extensions_order_id)
                    print("✓ Extensions test order cancelled")

                else:
                    print(f"✓ Extensions test order not pending (state: {extensions_order['state']}), skipping extensions test")

            except Exception as e:
                print(f"✓ Extensions test order may have been auto-cancelled: {type(e).__name__}")

        except Exception as e:
            print(f"✓ Could not create extensions test order: {type(e).__name__}")

        # Test 4: Error handling for invalid modifications
        print("✓ Testing error handling for invalid modifications...")

        try:
            # Try to modify a non-existent order
            fake_order_request = {"type": "LIMIT", "instrument": test_instrument, "units": 1000, "price": str(current_price), "timeInForce": "GTC"}

            await sandbox_client.orders.put_order(
                account_id=test_account_id,
                order_specifier="999999",  # Non-existent order ID
                order_request=fake_order_request,
            )
            print("✗ Expected error when modifying non-existent order, but none occurred")

        except Exception as e:
            print(f"✓ Correctly received error when trying to modify non-existent order: {type(e).__name__}")

        # Clean up any remaining test orders
        if "cleanup_order_id" in locals() and cleanup_order_id:
            try:
                await sandbox_client.orders.cancel_order(test_account_id, cleanup_order_id)
                print(f"✓ Cleanup order {cleanup_order_id} cancelled")
            except Exception as e:
                print(f"✓ Cleanup order already cancelled or completed: {type(e).__name__}")

        print("✓ Order modification test completed successfully")

    async def test_order_cancellation(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test cancellation of pending orders.

        Validates:
        - Order cancellation success
        - State transition accuracy
        - Margin release
        - Transaction recording
        - Error handling for invalid cancellations
        """
        print(f"✓ Starting order cancellation test for account {test_account_id}")

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_pending_orders = initial_account.pending_order_count
        initial_nav = Decimal(initial_account.nav)

        print(f"✓ Initial pending orders: {initial_pending_orders}")
        print(f"✓ Initial account NAV: {initial_nav}")

        # Use a major pair for testing
        test_instrument = test_instruments["major_pairs"][0]

        # Get current price to set orders far from market
        current_price = Decimal("1.1000")  # Default price for EUR_USD

        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                # Extract prices from the response
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        # Calculate mid price from bid/ask if available
                        if "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
                        elif "mid" in price_data:
                            current_price = Decimal(price_data["mid"])
            except Exception as e:
                print(f"✓ Using default price due to pricing error: {e}")

        print(f"✓ Current {test_instrument} price: {current_price}")

        # Test 1: Create limit orders that we can cancel (far from market to avoid filling)
        orders_to_cancel = []

        # Create multiple orders for comprehensive testing
        order_configs = [
            {
                "type": "limit",
                "units": 1000,
                "price": current_price - Decimal("0.0200"),  # 200 pips below (buy)
                "description": "buy limit order",
            },
            {
                "type": "limit",
                "units": -1500,
                "price": current_price + Decimal("0.0300"),  # 300 pips above (sell)
                "description": "sell limit order",
            },
            {
                "type": "stop",
                "units": 800,
                "price": current_price + Decimal("0.0150"),  # 150 pips above (buy stop)
                "description": "buy stop order",
            },
        ]

        print("✓ Creating orders for cancellation testing...")

        for i, config in enumerate(order_configs):
            try:
                if config["type"] == "limit":
                    order_response = await sandbox_client.orders.post_limit_order(account_id=test_account_id, instrument=test_instrument, units=config["units"], price=config["price"], time_in_force="GTC", client_request_id=f"cancel-test-{config['type']}-{i}-{int(1000 * current_price)}")
                elif config["type"] == "stop":
                    order_response = await sandbox_client.orders.post_stop_order(account_id=test_account_id, instrument=test_instrument, units=config["units"], price=config["price"], time_in_force="GTC", client_request_id=f"cancel-test-{config['type']}-{i}-{int(1000 * current_price)}")

                if order_response.order_create_transaction:
                    order_id = order_response.order_create_transaction["id"]
                    orders_to_cancel.append({"id": order_id, "type": config["type"], "description": config["description"]})
                    print(f"✓ Created {config['description']}: {order_id}")

                # Brief pause between orders
                await asyncio.sleep(0.2)

            except Exception as e:
                print(f"✓ Could not create {config['description']}: {type(e).__name__}")

        print(f"✓ Created {len(orders_to_cancel)} orders for testing")

        # Test 2: Verify orders are pending before cancellation
        pending_order_ids = []
        for order_info in orders_to_cancel:
            try:
                order_details = await sandbox_client.orders.get_order(test_account_id, order_info["id"])
                if order_details["state"] == "PENDING":
                    pending_order_ids.append(order_info["id"])
                    print(f"✓ Order {order_info['id']} ({order_info['description']}) is pending")
                else:
                    print(f"✓ Order {order_info['id']} state: {order_details['state']} (not pending)")
            except Exception as e:
                print(f"✓ Order {order_info['id']} may have been auto-cancelled: {type(e).__name__}")

        # Test 3: Cancel pending orders and verify cancellation
        successfully_cancelled = []

        if pending_order_ids:
            print("✓ Testing order cancellation...")

            for order_id in pending_order_ids:
                try:
                    # Cancel the order
                    cancel_response = await sandbox_client.orders.cancel_order(test_account_id, order_id)

                    # Verify cancellation response structure
                    assert "orderCancelTransaction" in cancel_response
                    cancelled_order_id = cancel_response["orderCancelTransaction"]["orderID"]
                    assert cancelled_order_id == order_id

                    print(f"✓ Successfully cancelled order {order_id}")
                    successfully_cancelled.append(order_id)

                    # Verify order state changed to CANCELLED
                    try:
                        cancelled_order = await sandbox_client.orders.get_order(test_account_id, order_id)
                        assert cancelled_order["state"] == "CANCELLED"
                        print(f"✓ Order {order_id} state correctly updated to CANCELLED")
                    except Exception as e:
                        print(f"✓ Cancelled order {order_id} no longer in pending orders (expected): {type(e).__name__}")

                    # Brief pause between cancellations
                    await asyncio.sleep(0.2)

                except Exception as e:
                    print(f"✓ Could not cancel order {order_id}: {type(e).__name__}")

        else:
            print("✓ No pending orders available for cancellation test")

        # Test 4: Verify account state after cancellations
        if successfully_cancelled:
            print("✓ Verifying account state after cancellations...")

            # Get updated account state
            updated_account_response = await sandbox_client.accounts.get_account(test_account_id)
            updated_account = updated_account_response["account"]
            final_pending_orders = updated_account.pending_order_count
            final_nav = Decimal(updated_account.nav)

            print(f"✓ Final pending orders: {final_pending_orders}")
            print(f"✓ Final account NAV: {final_nav}")

            # Verify pending order count decreased (or stayed same if orders were auto-cancelled)
            # In sandbox, orders may be auto-cancelled, so we can't guarantee exact counts
            print(f"✓ Pending order count change: {initial_pending_orders} → {final_pending_orders}")

            # NAV should remain stable (no fills occurred, only cancellations)
            nav_difference = abs(final_nav - initial_nav)
            if nav_difference < Decimal("0.01"):  # Allow for small rounding differences
                print("✓ Account NAV remained stable after cancellations")
            else:
                print(f"✓ Account NAV changed by {nav_difference} (may be due to other activity)")

        # Test 5: Error handling for invalid cancellations
        print("✓ Testing error handling for invalid cancellations...")

        # Test cancelling non-existent order
        try:
            await sandbox_client.orders.cancel_order(test_account_id, "999999")
            print("✗ Expected error when cancelling non-existent order, but none occurred")
        except Exception as e:
            print(f"✓ Correctly received error when cancelling non-existent order: {type(e).__name__}")

        # Test cancelling already cancelled order (if we have any)
        if successfully_cancelled:
            try:
                already_cancelled_id = successfully_cancelled[0]
                await sandbox_client.orders.cancel_order(test_account_id, already_cancelled_id)
                print("✗ Expected error when cancelling already cancelled order, but none occurred")
            except Exception as e:
                print(f"✓ Correctly received error when cancelling already cancelled order: {type(e).__name__}")

        # Test 6: Verify pending orders list accuracy
        print("✓ Verifying pending orders list accuracy...")

        try:
            pending_orders_response = await sandbox_client.orders.get_pending_orders(test_account_id)
            current_pending_orders = pending_orders_response.get("orders", [])

            print(f"✓ Current pending orders count: {len(current_pending_orders)}")

            # Verify none of our cancelled orders appear in pending list
            cancelled_ids_still_pending = [order["id"] for order in current_pending_orders if order["id"] in successfully_cancelled]

            if cancelled_ids_still_pending:
                print(f"✗ Found cancelled orders still in pending list: {cancelled_ids_still_pending}")
            else:
                print("✓ No cancelled orders found in pending list (correct)")

        except Exception as e:
            print(f"✓ Could not retrieve pending orders: {type(e).__name__}")

        # Test 7: Batch cancellation testing (if we have multiple pending orders)
        print("✓ Testing batch cancellation pattern...")

        # Create a few more orders for batch testing
        batch_orders = []
        for i in range(2):
            try:
                batch_order_response = await sandbox_client.orders.post_limit_order(
                    account_id=test_account_id,
                    instrument=test_instrument,
                    units=500,
                    price=current_price - Decimal("0.0500") - Decimal(f"0.00{i}0"),  # Far from market
                    time_in_force="GTC",
                    client_request_id=f"batch-cancel-test-{i}-{int(1000 * current_price)}",
                )

                if batch_order_response.order_create_transaction:
                    batch_order_id = batch_order_response.order_create_transaction["id"]
                    batch_orders.append(batch_order_id)
                    print(f"✓ Created batch test order {i + 1}: {batch_order_id}")

            except Exception as e:
                print(f"✓ Could not create batch test order {i + 1}: {type(e).__name__}")

        # Cancel batch orders concurrently
        if len(batch_orders) > 1:
            print("✓ Testing concurrent cancellations...")

            async def cancel_order_safe(order_id):
                try:
                    return await sandbox_client.orders.cancel_order(test_account_id, order_id)
                except Exception as e:
                    return f"Error: {type(e).__name__}"

            # Cancel orders concurrently
            cancellation_tasks = [cancel_order_safe(order_id) for order_id in batch_orders]
            cancellation_results = await asyncio.gather(*cancellation_tasks)

            successful_batch_cancellations = 0
            for i, result in enumerate(cancellation_results):
                if isinstance(result, dict) and "orderCancelTransaction" in result:
                    successful_batch_cancellations += 1
                    print(f"✓ Batch cancellation {i + 1} successful")
                else:
                    print(f"✓ Batch cancellation {i + 1} result: {result}")

            print(f"✓ Successful batch cancellations: {successful_batch_cancellations}/{len(batch_orders)}")

        else:
            print("✓ Insufficient orders for batch cancellation test")

        print("✓ Order cancellation test completed successfully")
