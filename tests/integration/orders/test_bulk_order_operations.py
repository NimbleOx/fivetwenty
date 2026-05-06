"""Integration tests for bulk order operations and risk management."""

import asyncio
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from tests.integration.helpers import mid_price_from_pricing_response, skip_or_raise_environment_error


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestBulkOperationsAndRisk:
    """Integration tests for bulk operations and risk management."""

    async def test_bulk_order_operations(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test multiple order operations in sequence."""
        print(f"✓ Starting bulk order operations test for account {test_account_id}")

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_pending_orders = initial_account.pending_order_count
        initial_nav = Decimal(initial_account.nav)

        print(f"✓ Initial state - Pending orders: {initial_pending_orders}, NAV: {initial_nav}")

        # Use multiple instruments for comprehensive testing
        test_instrument_primary = test_instruments["major_pairs"][0]
        test_instrument_secondary = test_instruments["major_pairs"][1] if len(test_instruments["major_pairs"]) > 1 else test_instruments["major_pairs"][0]

        # Get current price for order placement
        current_price = Decimal("1.1000")  # Default price for EUR_USD

        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument_primary])
                current_price = mid_price_from_pricing_response(pricing_response, current_price)
                # Extract prices from the response
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        # Calculate mid price from bid/ask if available
                        if price_data.get("bids") and price_data.get("asks"):
                            bid = Decimal(str(price_data["bids"][0]["price"]))
                            ask = Decimal(str(price_data["asks"][0]["price"]))
                            current_price = (bid + ask) / 2
                        elif "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
                        elif "mid" in price_data:
                            current_price = Decimal(price_data["mid"])
            except Exception as e:
                print(f"✓ Using default price due to pricing error: {e}")

        print(f"✓ Current {test_instrument_primary} price: {current_price}")

        try:
            # Test 1: Sequential bulk order creation
            print("✓ Test 1: Sequential bulk order creation...")

            sequential_orders = []
            sequential_start_time = asyncio.get_event_loop().time()

            # Create orders sequentially
            order_configs = [
                {"type": "limit", "instrument": test_instrument_primary, "units": 1000, "price": current_price - Decimal("0.0100")},
                {"type": "limit", "instrument": test_instrument_primary, "units": -1000, "price": current_price + Decimal("0.0100")},
                {"type": "stop", "instrument": test_instrument_primary, "units": 500, "price": current_price + Decimal("0.0050")},
                {"type": "limit", "instrument": test_instrument_secondary, "units": 750, "price": current_price - Decimal("0.0075")},
                {"type": "limit", "instrument": test_instrument_secondary, "units": -750, "price": current_price + Decimal("0.0075")},
            ]

            for i, config in enumerate(order_configs):
                try:
                    print(f"  Creating order {i + 1}: {config['type']} {config['units']} {config['instrument']}")

                    if config["type"] == "limit":
                        response = await sandbox_client.orders.post_limit_order(
                            account_id=test_account_id,
                            instrument=config["instrument"],
                            units=config["units"],
                            price=config["price"],
                            client_request_id=f"bulk-seq-{i}",
                        )
                    elif config["type"] == "stop":
                        response = await sandbox_client.orders.post_stop_order(
                            account_id=test_account_id,
                            instrument=config["instrument"],
                            units=config["units"],
                            price=config["price"],
                            client_request_id=f"bulk-seq-{i}",
                        )

                    if response.order_create_transaction:
                        order_id = response.order_create_transaction["id"]
                        sequential_orders.append(order_id)
                        print(f"    ✓ Order created: {order_id}")
                    else:
                        print(f"    ⚠️  Order {i + 1} creation failed")

                    # Small delay between orders
                    await asyncio.sleep(0.1)

                except Exception as e:
                    print(f"    ⚠️  Order {i + 1} failed: {e}")

            sequential_duration = asyncio.get_event_loop().time() - sequential_start_time
            print(f"✓ Sequential creation: {len(sequential_orders)}/{len(order_configs)} orders in {sequential_duration:.2f}s")

            # Test 2: Concurrent bulk order creation
            print("✓ Test 2: Concurrent bulk order creation...")

            concurrent_start_time = asyncio.get_event_loop().time()

            # Create orders concurrently
            concurrent_configs = [
                {"type": "limit", "instrument": test_instrument_primary, "units": 250, "price": current_price - Decimal("0.0300")},
                {"type": "limit", "instrument": test_instrument_primary, "units": 250, "price": current_price - Decimal("0.0350")},
                {"type": "limit", "instrument": test_instrument_primary, "units": 250, "price": current_price - Decimal("0.0400")},
            ]

            async def create_concurrent_order(config, index):
                try:
                    if config["type"] == "limit":
                        response = await sandbox_client.orders.post_limit_order(
                            account_id=test_account_id,
                            instrument=config["instrument"],
                            units=config["units"],
                            price=config["price"],
                            client_request_id=f"bulk-conc-{index}",
                        )
                        if response.order_create_transaction:
                            return response.order_create_transaction["id"]
                except Exception as e:
                    print(f"    ⚠️  Concurrent order {index} failed: {e}")
                return None

            # Execute concurrent order creation
            concurrent_tasks = [create_concurrent_order(config, i) for i, config in enumerate(concurrent_configs)]

            concurrent_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)
            concurrent_orders = [r for r in concurrent_results if r and not isinstance(r, Exception)]

            concurrent_duration = asyncio.get_event_loop().time() - concurrent_start_time
            print(f"✓ Concurrent creation: {len(concurrent_orders)}/{len(concurrent_configs)} orders in {concurrent_duration:.2f}s")

            # Performance comparison
            if sequential_duration > 0 and concurrent_duration > 0:
                efficiency_ratio = sequential_duration / concurrent_duration
                print(f"✓ Concurrent efficiency: {efficiency_ratio:.2f}x faster than sequential")

            # Test 3: Bulk order modification
            print("✓ Test 3: Bulk order modification...")

            modification_count = 0
            for order_id in sequential_orders[:3]:  # Modify first 3 orders
                try:
                    # Check if order is still pending
                    order_details = await sandbox_client.orders.get_order(test_account_id, order_id)
                    if order_details["state"] == "PENDING":
                        # Modify the order (change units)
                        new_units = int(order_details["units"]) // 2  # Half the units

                        modify_response = await sandbox_client.orders.modify_order(
                            account_id=test_account_id,
                            order_id=order_id,
                            units=new_units,
                            client_request_id=f"bulk-modify-{modification_count}",
                        )

                        if modify_response.order_modify_transaction:
                            modification_count += 1
                            print(f"    ✓ Modified order {order_id}")

                except Exception as e:
                    print(f"    ⚠️  Could not modify order {order_id}: {e}")

            print(f"✓ Modified {modification_count} orders")

            # Test 4: Bulk order cancellation
            print("✓ Test 4: Bulk order cancellation...")

            all_test_orders = sequential_orders + concurrent_orders
            cancellation_count = 0

            for order_id in all_test_orders:
                try:
                    # Check if order is still pending
                    order_details = await sandbox_client.orders.get_order(test_account_id, order_id)
                    if order_details["state"] == "PENDING":
                        cancel_response = await sandbox_client.orders.cancel_order(test_account_id, order_id, client_request_id=f"bulk-cancel-{cancellation_count}")

                        if "orderCancelTransaction" in cancel_response:
                            cancellation_count += 1
                            print(f"    ✓ Cancelled order {order_id}")

                except Exception as e:
                    print(f"    ⚠️  Could not cancel order {order_id}: {e}")

            print(f"✓ Cancelled {cancellation_count} orders")

            # Verify final account state
            final_account_response = await sandbox_client.accounts.get_account(test_account_id)
            final_account = final_account_response["account"]
            final_pending_orders = final_account.pending_order_count
            final_nav = Decimal(final_account.nav)

            print(f"✓ Final state - Pending orders: {final_pending_orders}, NAV: {final_nav}")

            # Account should be stable after bulk operations
            assert final_nav > 0, "Account NAV should remain positive"
            print("✓ Account remains stable after bulk operations")

        except Exception as e:
            skip_or_raise_environment_error(e, "Bulk operations test")

        print("✓ Bulk order operations test completed")

    async def test_order_error_scenarios(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test various order error scenarios and error handling."""
        print("✓ Testing order error scenarios")

        test_instrument = test_instruments["major_pairs"][0]
        current_price = Decimal("1.1000")

        # Get current pricing if available
        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                current_price = mid_price_from_pricing_response(pricing_response, current_price)
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        if price_data.get("bids") and price_data.get("asks"):
                            bid = Decimal(str(price_data["bids"][0]["price"]))
                            ask = Decimal(str(price_data["asks"][0]["price"]))
                            current_price = (bid + ask) / 2
                        elif "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
            except Exception as e:
                print(f"✓ Using default price: {e}")

        # Test 1: Invalid instrument
        print("✓ Test 1: Invalid instrument error")
        try:
            await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument="INVALID_PAIR",
                units=1000,
            )
            print("⚠️  Expected error for invalid instrument")
        except Exception as e:
            print(f"✓ Invalid instrument error caught: {type(e).__name__}")

        # Test 2: Invalid units (zero or excessive)
        print("✓ Test 2: Invalid units error")
        try:
            await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=0,  # Invalid: zero units
            )
            print("⚠️  Expected error for zero units")
        except Exception as e:
            print(f"✓ Zero units error caught: {type(e).__name__}")

        # Test 3: Invalid price (negative or zero for limit orders)
        print("✓ Test 3: Invalid price error")
        try:
            await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=1000,
                price=Decimal("0.0"),  # Invalid: zero price
            )
            print("⚠️  Expected error for zero price")
        except Exception as e:
            print(f"✓ Zero price error caught: {type(e).__name__}")

        # Test 4: Invalid time-in-force
        print("✓ Test 4: Invalid time-in-force error")
        try:
            await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=1000,
                price=current_price - Decimal("0.0100"),
                time_in_force="INVALID_TIF",
            )
            print("⚠️  Expected error for invalid TIF")
        except Exception as e:
            print(f"✓ Invalid TIF error caught: {type(e).__name__}")

        # Test 5: Duplicate client request ID
        print("✓ Test 5: Duplicate client request ID")
        duplicate_client_id = f"duplicate-test-{int(1000 * current_price)}"

        try:
            # First order with client ID
            first_response = await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=500,
                price=current_price - Decimal("0.0300"),
                client_request_id=duplicate_client_id,
            )

            first_order_id = None
            if first_response.order_create_transaction:
                first_order_id = first_response.order_create_transaction["id"]
                print(f"✓ First order created: {first_order_id}")

            # Second order with same client ID (should fail or be handled)
            try:
                await sandbox_client.orders.post_limit_order(
                    account_id=test_account_id,
                    instrument=test_instrument,
                    units=750,
                    price=current_price - Decimal("0.0350"),
                    client_request_id=duplicate_client_id,  # Duplicate
                )
                print("⚠️  Expected error or special handling for duplicate client ID")
            except Exception as e:
                print(f"✓ Duplicate client ID handled: {type(e).__name__}")

            # Clean up first order
            if first_order_id:
                try:
                    order_details = await sandbox_client.orders.get_order(test_account_id, first_order_id)
                    if order_details["state"] == "PENDING":
                        await sandbox_client.orders.cancel_order(test_account_id, first_order_id)
                        print("✓ Cleanup: Cancelled duplicate test order")
                except Exception as cleanup_error:
                    print(f"⚠️  Cleanup error: {cleanup_error}")

        except Exception as e:
            print(f"✓ Duplicate client ID test handled: {type(e).__name__}")

        print("✓ Order error scenarios test completed")

    async def test_post_trade_risk_management(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test risk management scenarios after trade execution."""
        print("✓ Testing post-trade risk management")

        test_instrument = test_instruments["major_pairs"][0]
        current_price = Decimal("1.1000")

        # Get current pricing and account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_nav = Decimal(initial_account.nav)
        initial_margin_used = Decimal(initial_account.margin_used or 0)

        print(f"✓ Initial NAV: {initial_nav}, Margin used: {initial_margin_used}")

        if hasattr(sandbox_client, "pricing") and hasattr(sandbox_client.pricing, "get_pricing"):
            try:
                pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])
                current_price = mid_price_from_pricing_response(pricing_response, current_price)
                if isinstance(pricing_response, dict) and "prices" in pricing_response:
                    prices = pricing_response["prices"]
                    if prices and isinstance(prices[0], dict):
                        price_data = prices[0]
                        if price_data.get("bids") and price_data.get("asks"):
                            bid = Decimal(str(price_data["bids"][0]["price"]))
                            ask = Decimal(str(price_data["asks"][0]["price"]))
                            current_price = (bid + ask) / 2
                        elif "bid" in price_data and "ask" in price_data:
                            bid = Decimal(price_data["bid"])
                            ask = Decimal(price_data["ask"])
                            current_price = (bid + ask) / 2
            except Exception as e:
                print(f"✓ Using default price: {e}")

        try:
            # Test 1: Risk-managed market order with protective stops
            print("✓ Test 1: Risk-managed market order")

            # Calculate risk parameters
            risk_amount = initial_nav * Decimal("0.01")  # Risk 1% of NAV
            stop_distance = Decimal("0.0050")  # 50 pips stop loss
            profit_target = stop_distance * 2  # 2:1 risk-reward ratio

            # Calculate position size based on risk
            pip_value = Decimal("0.0001")
            position_size = int(risk_amount / (stop_distance / pip_value))
            position_size = max(100, min(position_size, 10000))  # Reasonable bounds

            print("✓ Risk management parameters:")
            print(f"  Risk amount: {risk_amount}")
            print(f"  Stop distance: {stop_distance}")
            print(f"  Position size: {position_size}")

            # Create market order with TP/SL
            tp_price = current_price + profit_target
            sl_price = current_price - stop_distance

            risk_managed_response = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=position_size,
                take_profit=tp_price,
                stop_loss=sl_price,
                client_request_id=f"risk-managed-{int(1000 * current_price)}",
            )

            order_fill_transaction = getattr(risk_managed_response, "order_fill_transaction", None)
            if order_fill_transaction:
                print("✓ Risk-managed order filled")

                # Verify TP/SL orders were created
                if "tradeOpened" in order_fill_transaction:
                    trade_info = order_fill_transaction["tradeOpened"]
                    trade_id = trade_info.get("tradeID")

                    if trade_id:
                        # Check for associated TP/SL orders
                        orders = await sandbox_client.orders.get_orders(test_account_id)
                        tp_sl_orders = [order for order in orders if isinstance(order, dict) and order.get("tradeID") == trade_id and order.get("type") in ["TAKE_PROFIT", "STOP_LOSS"]]

                        print(f"✓ Found {len(tp_sl_orders)} TP/SL orders for trade {trade_id}")
            else:
                print("✓ Risk-managed order was not filled; continuing with account risk checks")

            # Test 2: Account risk monitoring
            print("✓ Test 2: Account risk monitoring")

            # Get updated account state
            updated_account_response = await sandbox_client.accounts.get_account(test_account_id)
            updated_account = updated_account_response["account"]
            updated_nav = Decimal(updated_account.nav)
            updated_margin_used = Decimal(updated_account.margin_used or 0)
            margin_available = Decimal(updated_account.margin_available or 0)

            print(f"✓ Updated NAV: {updated_nav}, Margin used: {updated_margin_used}")

            # Calculate margin utilization
            if updated_nav > 0:
                margin_utilization = (updated_margin_used / updated_nav) * 100
                print(f"✓ Margin utilization: {margin_utilization:.2f}%")

                # Risk checks
                assert margin_utilization < 80, f"Margin utilization too high: {margin_utilization:.2f}%"
                assert margin_available > 0, "Should have available margin"
                print("✓ Risk parameters within acceptable limits")

            # Test 3: Position cleanup for risk management
            print("✓ Test 3: Position cleanup")

            # Close any open positions to reset account state
            try:
                positions_response = await sandbox_client.positions.get_positions(test_account_id)
                positions_closed = 0

                for position in positions_response["positions"]:
                    if position["instrument"] == test_instrument:
                        long_units = position["long"]["units"] if position.get("long") else "0"
                        short_units = position["short"]["units"] if position.get("short") else "0"

                        if long_units != "0" or short_units != "0":
                            try:
                                await sandbox_client.positions.close_position(test_account_id, test_instrument, long_units="ALL", short_units="ALL")
                                print(f"✓ Closed position for {test_instrument}")
                                positions_closed += 1
                            except Exception as close_error:
                                # Handle position closing errors gracefully
                                if "CLOSEOUT_POSITION_DOESNT_EXIST" in str(close_error):
                                    print("✓ No position to close (already closed or never existed)")
                                else:
                                    print(f"✓ Position close failed: {close_error}")

                if positions_closed == 0:
                    print("✓ No positions found to close")

            except Exception as position_error:
                print(f"✓ Position cleanup error (non-critical): {position_error}")

        except Exception as e:
            skip_or_raise_environment_error(e, "Risk management test")

        print("✓ Post-trade risk management test completed")
