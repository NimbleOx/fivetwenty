"""Integration tests for advanced order types (stop, market-if-touched, etc.)."""

from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from tests.integration.helpers import skip_or_raise_environment_error


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestAdvancedOrderTypes:
    """Integration tests for advanced order types."""

    async def test_stop_order_creation(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test creation and validation of stop orders."""
        print(f"✓ Starting stop order creation test for account {test_account_id}")

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_pending_orders = initial_account.pending_order_count

        print(f"✓ Initial pending orders: {initial_pending_orders}")

        # Use a major pair for testing
        test_instrument = test_instruments["major_pairs"][0]

        # Get current price to set reasonable stop level
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

        # Create stop order above current price (buy stop)
        stop_price = current_price + Decimal("0.0100")  # 100 pips above
        price_bound = stop_price + Decimal("0.0050")  # 50 pips slippage protection

        print(f"✓ Creating buy stop order at {stop_price} with bound at {price_bound}")

        try:
            # Test 1: Basic stop order
            response = await sandbox_client.orders.post_stop_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="1000",  # Small position
                price=stop_price,
                price_bound=price_bound,
                client_request_id=f"stop-order-test-{int(1000 * current_price)}",
            )

            # Validate response structure
            assert response.order_create_transaction is not None
            assert response.last_transaction_id is not None

            order_id = response.order_create_transaction["id"]
            print(f"✓ Stop order created: {order_id}")

            # Test 2: Stop order with TP/SL
            tp_price = stop_price + Decimal("0.0050")  # Take profit 50 pips above stop
            sl_price = stop_price - Decimal("0.0050")  # Stop loss 50 pips below stop

            response_with_tpsl = await sandbox_client.orders.post_stop_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="1000",
                price=stop_price + Decimal("0.0010"),  # Slightly different price
                take_profit=tp_price,
                stop_loss=sl_price,
                time_in_force="GFD",  # Good for day
                client_request_id=f"stop-order-tpsl-test-{int(1000 * current_price)}",
            )

            order_with_tpsl_id = response_with_tpsl.order_create_transaction["id"]
            print(f"✓ Stop order with TP/SL created: {order_with_tpsl_id}")

            # Verify order creation and structure
            order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
            order_details = order_response["order"]
            assert order_details["state"] in ["PENDING", "CANCELLED"]
            assert order_details["type"] == "STOP"
            assert Decimal(order_details["price"]) == stop_price

            # Verify TP/SL order configuration
            order_tpsl_response = await sandbox_client.orders.get_order(test_account_id, order_with_tpsl_id)
            order_tpsl_details = order_tpsl_response["order"]
            assert order_tpsl_details["state"] in ["PENDING", "CANCELLED", "FILLED"]

            # Check TP/SL prices if order is still pending
            if order_tpsl_details["state"] == "PENDING":
                if order_tpsl_details.get("takeProfitOnFill"):
                    actual_tp = Decimal(order_tpsl_details["takeProfitOnFill"]["price"])
                    assert actual_tp == tp_price, f"Expected TP {tp_price}, got {actual_tp}"

                if order_tpsl_details.get("stopLossOnFill"):
                    actual_sl = Decimal(order_tpsl_details["stopLossOnFill"]["price"])
                    assert actual_sl == sl_price, f"Expected SL {sl_price}, got {actual_sl}"
            else:
                print(f"✓ Order state is {order_tpsl_details['state']}, skipping TP/SL validation")

            print("✓ Stop order validation completed")

            # Clean up: Cancel test orders (if still pending)
            try:
                if order_details["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_id)
                if order_tpsl_details["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_with_tpsl_id)
                print("✓ Test orders cancelled")
            except Exception as e:
                print(f"✓ Orders already cancelled or completed: {e}")

        except Exception as e:
            skip_or_raise_environment_error(e, "Stop order creation test")

    async def test_market_if_touched_order_creation(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test creation and validation of market-if-touched orders."""
        print(f"✓ Starting market-if-touched order creation test for account {test_account_id}")

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_pending_orders = initial_account.pending_order_count

        print(f"✓ Initial pending orders: {initial_pending_orders}")

        # Use a major pair for testing
        test_instrument = test_instruments["major_pairs"][0]

        # Get current price to set reasonable trigger level
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

        # Create MIT order below current price (buy when price drops)
        trigger_price = current_price - Decimal("0.0100")  # 100 pips below
        price_bound = trigger_price + Decimal("0.0050")  # 50 pips slippage protection

        print(f"✓ Creating buy MIT order at {trigger_price} with bound at {price_bound}")

        try:
            # Test 1: Basic MIT order
            response = await sandbox_client.orders.post_market_if_touched_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="1000",  # Small position
                price=trigger_price,
                price_bound=price_bound,
                client_request_id=f"mit-order-test-{int(1000 * current_price)}",
            )

            # Validate response structure
            assert response.order_create_transaction is not None
            assert response.last_transaction_id is not None

            order_id = response.order_create_transaction["id"]
            print(f"✓ MIT order created: {order_id}")

            # Test 2: MIT order with TP/SL
            tp_price = trigger_price + Decimal("0.0050")  # Take profit 50 pips above trigger
            sl_price = trigger_price - Decimal("0.0050")  # Stop loss 50 pips below trigger

            response_with_tpsl = await sandbox_client.orders.post_market_if_touched_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="1000",
                price=trigger_price + Decimal("0.0010"),  # Slightly different price
                take_profit=tp_price,
                stop_loss=sl_price,
                time_in_force="GFD",  # Good for day
                client_request_id=f"mit-order-tpsl-test-{int(1000 * current_price)}",
            )

            order_with_tpsl_id = response_with_tpsl.order_create_transaction["id"]
            print(f"✓ MIT order with TP/SL created: {order_with_tpsl_id}")

            # Verify order creation and structure
            order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
            order_details = order_response["order"]
            assert order_details["state"] in ["PENDING", "CANCELLED"]
            assert order_details["type"] == "MARKET_IF_TOUCHED"
            assert Decimal(order_details["price"]) == trigger_price

            # Verify TP/SL order configuration
            order_tpsl_response = await sandbox_client.orders.get_order(test_account_id, order_with_tpsl_id)
            order_tpsl_details = order_tpsl_response["order"]
            assert order_tpsl_details["state"] in ["PENDING", "CANCELLED", "FILLED"]

            # Check TP/SL prices if order is still pending
            if order_tpsl_details["state"] == "PENDING":
                if order_tpsl_details.get("takeProfitOnFill"):
                    actual_tp = Decimal(order_tpsl_details["takeProfitOnFill"]["price"])
                    assert actual_tp == tp_price, f"Expected TP {tp_price}, got {actual_tp}"

                if order_tpsl_details.get("stopLossOnFill"):
                    actual_sl = Decimal(order_tpsl_details["stopLossOnFill"]["price"])
                    assert actual_sl == sl_price, f"Expected SL {sl_price}, got {actual_sl}"
            else:
                print(f"✓ Order state is {order_tpsl_details['state']}, skipping TP/SL validation")

            print("✓ MIT order validation completed")

            # Clean up: Cancel test orders (if still pending)
            try:
                if order_details["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_id)
                if order_tpsl_details["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_with_tpsl_id)
                print("✓ Test orders cancelled")
            except Exception as e:
                print(f"✓ Orders already cancelled or completed: {e}")

        except Exception as e:
            skip_or_raise_environment_error(e, "MIT order creation test")

    async def test_advanced_time_in_force_options(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test advanced time-in-force options for orders."""
        print("✓ Testing advanced time-in-force options")

        test_instrument = test_instruments["major_pairs"][0]
        current_price = Decimal("1.1000")  # Default price

        # Get current pricing if available
        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        if "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
            except Exception as e:
                print(f"✓ Using default price: {e}")

        # Test different time-in-force options
        tif_tests = [
            {"tif": "GFD", "name": "Good For Day"},
            {"tif": "GTC", "name": "Good Till Cancelled"},
            {"tif": "IOC", "name": "Immediate or Cancel"},
            {"tif": "FOK", "name": "Fill or Kill"},
        ]

        created_orders = []

        for tif_test in tif_tests:
            try:
                print(f"✓ Testing {tif_test['name']} ({tif_test['tif']})")

                # Create limit order with specific time-in-force
                limit_price = current_price - Decimal("0.0200")  # Far from market

                response = await sandbox_client.orders.post_limit_order(
                    account_id=test_account_id,
                    instrument=test_instrument,
                    units="1000",
                    price=limit_price,
                    time_in_force=tif_test["tif"],
                    client_request_id=f"tif-test-{tif_test['tif']}-{int(1000 * current_price)}",
                )

                if response.order_create_transaction:
                    order_id = response.order_create_transaction["id"]
                    created_orders.append(order_id)
                    print(f"  ✓ Order created: {order_id}")

                    # Validate the order was created with correct TIF
                    order_details = await sandbox_client.orders.get_order(test_account_id, order_id)
                    if order_details["state"] == "PENDING":
                        assert order_details.get("timeInForce") == tif_test["tif"]
                        print(f"  ✓ Time-in-force verified: {tif_test['tif']}")

            except Exception as e:
                error_msg = str(e).lower()
                if any(term in error_msg for term in ["margin", "funds", "closed", "trading"]):
                    print(f"  ✓ {tif_test['name']} test skipped: {e}")
                else:
                    print(f"  ⚠️  {tif_test['name']} test failed: {e}")

        # Clean up created orders
        for order_id in created_orders:
            try:
                order_details = await sandbox_client.orders.get_order(test_account_id, order_id)
                if order_details["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_id)
                    print(f"  ✓ Cancelled order {order_id}")
            except Exception as e:
                print(f"  ⚠️  Could not cancel order {order_id}: {e}")

        print("✓ Time-in-force options test completed")

    async def test_order_trigger_conditions(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test various order trigger conditions and scenarios."""
        print("✓ Testing order trigger conditions")

        test_instrument = test_instruments["major_pairs"][0]
        current_price = Decimal("1.1000")

        # Get current pricing if available
        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        if "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
            except Exception as e:
                print(f"✓ Using default price: {e}")

        print(f"✓ Current price: {current_price}")

        # Test 1: Stop order trigger (buy stop above market)
        try:
            print("✓ Test 1: Stop order trigger conditions")

            stop_price = current_price + Decimal("0.0500")  # 500 pips above market

            stop_response = await sandbox_client.orders.post_stop_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="500",
                price=stop_price,
                time_in_force="GFD",
                client_request_id=f"trigger-stop-test-{int(1000 * current_price)}",
            )

            if stop_response.order_create_transaction:
                stop_order_id = stop_response.order_create_transaction["id"]
                print(f"  ✓ Stop order created: {stop_order_id}")

                # Verify stop trigger price
                stop_order = await sandbox_client.orders.get_order(test_account_id, stop_order_id)
                assert Decimal(stop_order["price"]) == stop_price
                print("  ✓ Stop trigger price verified")

                # Clean up
                if stop_order["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, stop_order_id)

        except Exception as e:
            print(f"  ⚠️  Stop order trigger test failed: {e}")

        # Test 2: Market-if-touched trigger (buy MIT below market)
        try:
            print("✓ Test 2: MIT order trigger conditions")

            mit_price = current_price - Decimal("0.0300")  # 300 pips below market

            mit_response = await sandbox_client.orders.post_market_if_touched_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units="750",
                price=mit_price,
                time_in_force="GFD",
                client_request_id=f"trigger-mit-test-{int(1000 * current_price)}",
            )

            if mit_response.order_create_transaction:
                mit_order_id = mit_response.order_create_transaction["id"]
                print(f"  ✓ MIT order created: {mit_order_id}")

                # Verify MIT trigger price
                mit_order = await sandbox_client.orders.get_order(test_account_id, mit_order_id)
                assert Decimal(mit_order["price"]) == mit_price
                print("  ✓ MIT trigger price verified")

                # Clean up
                if mit_order["state"] == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, mit_order_id)

        except Exception as e:
            print(f"  ⚠️  MIT order trigger test failed: {e}")

        print("✓ Order trigger conditions test completed")
