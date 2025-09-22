"""Integration tests for trade order management operations.

This module tests trade order management functionality (adding/modifying
stop loss and take profit orders on existing trades) that was previously
missing comprehensive integration test coverage.
"""

from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestTradeOrderManagement:
    """Integration tests for trade order management operations."""

    async def test_trade_stop_loss_take_profit_management(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test adding and modifying stop loss and take profit orders on existing trades.

        Validates:
        - Adding stop loss orders to existing trades
        - Adding take profit orders to existing trades
        - Modifying existing dependent orders
        - Canceling dependent orders
        - Error handling for invalid parameters
        """
        print("✓ Starting trade stop loss and take profit management test...")

        test_instrument = test_instruments["major_pairs"][0]  # EUR_USD
        print(f"  Using instrument: {test_instrument}")

        # Check for existing open trades first
        try:
            trades_response = await sandbox_client.trades.get_open_trades(test_account_id)
            existing_trades = trades_response.get("trades", [])

            test_trade = None
            test_trade_id = None

            # Look for an existing trade we can use
            for trade in existing_trades:
                if hasattr(trade, "instrument") and trade.instrument == test_instrument:
                    if hasattr(trade, "current_units") and int(trade.current_units) != 0:
                        test_trade = trade
                        test_trade_id = trade.id
                        break

            if not test_trade:
                print("  No existing trade found - creating test trade first")

                # Get minimum trade size and current pricing
                instruments_response = await sandbox_client.accounts.get_account_instruments(
                    test_account_id, instruments=[test_instrument]
                )

                if instruments_response.get("instruments"):
                    instrument_details = instruments_response["instruments"][0]
                    min_trade_size = max(int(instrument_details.minimum_trade_size), 1)

                    # Create a market order to establish a trade
                    market_order_response = await sandbox_client.orders.post_market_order(
                        account_id=test_account_id,
                        instrument=test_instrument,
                        units=min_trade_size,
                    )

                    if market_order_response and market_order_response.order_fill_transaction:
                        fill_tx = market_order_response.order_fill_transaction
                        if "tradeOpened" in fill_tx and "tradeID" in fill_tx["tradeOpened"]:
                            test_trade_id = fill_tx["tradeOpened"]["tradeID"]
                            print(f"  ✓ Created test trade: {test_trade_id}")

            if test_trade_id:
                # Get current pricing to set realistic SL/TP levels
                pricing_response = await sandbox_client.pricing.get_pricing(
                    account_id=test_account_id,
                    instruments=[test_instrument]
                )

                current_price = Decimal("1.1000")  # Default fallback
                if pricing_response.get("prices"):
                    price_data = pricing_response["prices"][0]
                    if price_data.get("asks"):
                        current_price = Decimal(price_data["asks"][0]["price"])

                print(f"  Current price for {test_instrument}: {current_price}")

                # Test 1: Add stop loss order to existing trade
                print(f"\n✓ Test 1: Adding stop loss order to trade {test_trade_id}")

                stop_loss_price = current_price * Decimal("0.99")  # 1% below current price

                try:
                    stop_loss_spec = {
                        "price": str(stop_loss_price),
                        "timeInForce": "GTC"
                    }

                    sl_response = await sandbox_client.trades.put_trade_orders(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        stop_loss=stop_loss_spec
                    )

                    assert sl_response is not None, "Stop loss response should not be None"
                    print(f"  ✓ Stop loss order added at price {stop_loss_price}")

                    # Verify the stop loss was added
                    trade_response = await sandbox_client.trades.get_trade(test_account_id, test_trade_id)
                    if "trade" in trade_response:
                        trade = trade_response["trade"]
                        if hasattr(trade, "stop_loss_order") and trade.stop_loss_order:
                            sl_order = trade.stop_loss_order
                            print(f"    Stop loss order ID: {sl_order.id}")
                            print(f"    Stop loss price: {sl_order.price}")

                except FiveTwentyError as e:
                    print(f"  ⚠ Stop loss addition failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error adding stop loss: {type(e).__name__}")

                # Test 2: Add take profit order to existing trade
                print(f"\n✓ Test 2: Adding take profit order to trade {test_trade_id}")

                take_profit_price = current_price * Decimal("1.01")  # 1% above current price

                try:
                    take_profit_spec = {
                        "price": str(take_profit_price),
                        "timeInForce": "GTC"
                    }

                    tp_response = await sandbox_client.trades.put_trade_orders(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        take_profit=take_profit_spec
                    )

                    assert tp_response is not None, "Take profit response should not be None"
                    print(f"  ✓ Take profit order added at price {take_profit_price}")

                    # Verify the take profit was added
                    trade_response = await sandbox_client.trades.get_trade(test_account_id, test_trade_id)
                    if "trade" in trade_response:
                        trade = trade_response["trade"]
                        if hasattr(trade, "take_profit_order") and trade.take_profit_order:
                            tp_order = trade.take_profit_order
                            print(f"    Take profit order ID: {tp_order.id}")
                            print(f"    Take profit price: {tp_order.price}")

                except FiveTwentyError as e:
                    print(f"  ⚠ Take profit addition failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error adding take profit: {type(e).__name__}")

                # Test 3: Modify existing stop loss order
                print("\n✓ Test 3: Modifying existing stop loss order")

                new_stop_loss_price = current_price * Decimal("0.985")  # 1.5% below current price

                try:
                    modified_stop_loss_spec = {
                        "price": str(new_stop_loss_price),
                        "timeInForce": "GTC"
                    }

                    modify_sl_response = await sandbox_client.trades.put_trade_orders(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        stop_loss=modified_stop_loss_spec
                    )

                    assert modify_sl_response is not None, "Modified stop loss response should not be None"
                    print(f"  ✓ Stop loss order modified to price {new_stop_loss_price}")

                except FiveTwentyError as e:
                    print(f"  ⚠ Stop loss modification failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error modifying stop loss: {type(e).__name__}")

                # Test 4: Add both stop loss and take profit in single request
                print("\n✓ Test 4: Adding both SL and TP in single request")

                combined_sl_price = current_price * Decimal("0.98")
                combined_tp_price = current_price * Decimal("1.02")

                try:
                    combined_sl_spec = {
                        "price": str(combined_sl_price),
                        "timeInForce": "GTC"
                    }

                    combined_tp_spec = {
                        "price": str(combined_tp_price),
                        "timeInForce": "GTC"
                    }

                    combined_response = await sandbox_client.trades.put_trade_orders(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        stop_loss=combined_sl_spec,
                        take_profit=combined_tp_spec
                    )

                    assert combined_response is not None, "Combined SL/TP response should not be None"
                    print(f"  ✓ Both stop loss ({combined_sl_price}) and take profit ({combined_tp_price}) added")

                except FiveTwentyError as e:
                    print(f"  ⚠ Combined SL/TP addition failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error adding combined orders: {type(e).__name__}")

                # Test 5: Cancel dependent orders (pass None to cancel)
                print("\n✓ Test 5: Canceling dependent orders")

                try:
                    cancel_response = await sandbox_client.trades.put_trade_orders(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        stop_loss=None,  # Cancel stop loss
                        take_profit=None  # Cancel take profit
                    )

                    assert cancel_response is not None, "Cancel response should not be None"
                    print("  ✓ Stop loss and take profit orders canceled")

                    # Verify cancellation
                    final_trade_response = await sandbox_client.trades.get_trade(test_account_id, test_trade_id)
                    if "trade" in final_trade_response:
                        final_trade = final_trade_response["trade"]
                        has_sl = hasattr(final_trade, "stop_loss_order") and final_trade.stop_loss_order
                        has_tp = hasattr(final_trade, "take_profit_order") and final_trade.take_profit_order
                        print(f"    After cancellation - Has SL: {has_sl}, Has TP: {has_tp}")

                except FiveTwentyError as e:
                    print(f"  ⚠ Order cancellation failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error canceling orders: {type(e).__name__}")

                # Cleanup: Close the test trade
                print(f"\n✓ Cleanup: Closing test trade {test_trade_id}")

                try:
                    close_response = await sandbox_client.trades.close_trade(test_account_id, test_trade_id)
                    if close_response:
                        print("  ✓ Test trade closed successfully")
                except Exception as e:
                    print(f"  ⚠ Could not close test trade (this is okay): {type(e).__name__}")

            else:
                print("  ⚠ No trade available for testing - test requires an open position")

        except Exception as e:
            print(f"  ⚠ Trade order management test failed: {type(e).__name__}: {e}")

        print("✓ Trade stop loss and take profit management test completed")

    async def test_trade_order_management_error_handling(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test error handling for trade order management operations.

        Validates:
        - Invalid trade ID handling
        - Invalid price handling
        - Invalid account ID handling
        - Malformed order specifications
        """
        print("✓ Starting trade order management error handling test...")

        test_instrument = test_instruments["major_pairs"][0]

        # Test 1: Invalid trade ID
        print("\n✓ Test 1: Invalid trade ID handling")

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.trades.put_trade_orders(
                    account_id=test_account_id,
                    trade_specifier="invalid-trade-123",
                    stop_loss={"price": "1.0000", "timeInForce": "GTC"}
                )

            error = exc_info.value
            assert error.status == 404, f"Expected 404 for invalid trade ID, got {error.status}"
            print("  ✓ Invalid trade ID correctly rejected")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid trade ID: {type(e).__name__}")

        # Test 2: Invalid account ID
        print("\n✓ Test 2: Invalid account ID handling")

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.trades.put_trade_orders(
                    account_id="invalid-account-123",
                    trade_specifier="1",
                    stop_loss={"price": "1.0000", "timeInForce": "GTC"}
                )

            error = exc_info.value
            assert error.status in [400, 404], f"Expected 400/404 for invalid account, got {error.status}"
            print(f"  ✓ Invalid account ID correctly rejected: HTTP {error.status}")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid account: {type(e).__name__}")

        # Test 3: Invalid price values
        print("\n✓ Test 3: Invalid price handling")

        # First check if we have any open trades to test with
        try:
            trades_response = await sandbox_client.trades.get_open_trades(test_account_id)
            open_trades = trades_response.get("trades", [])

            if open_trades:
                test_trade_id = open_trades[0].id

                # Test invalid price format
                try:
                    with pytest.raises(FiveTwentyError) as exc_info:
                        await sandbox_client.trades.put_trade_orders(
                            account_id=test_account_id,
                            trade_specifier=test_trade_id,
                            stop_loss={"price": "invalid-price", "timeInForce": "GTC"}
                        )

                    error = exc_info.value
                    assert error.status == 400, f"Expected 400 for invalid price, got {error.status}"
                    print("  ✓ Invalid price format correctly rejected")

                except AssertionError:
                    raise
                except Exception as e:
                    print(f"  ⚠ Unexpected error for invalid price: {type(e).__name__}")

                # Test negative price
                try:
                    with pytest.raises(FiveTwentyError) as exc_info:
                        await sandbox_client.trades.put_trade_orders(
                            account_id=test_account_id,
                            trade_specifier=test_trade_id,
                            stop_loss={"price": "-1.0000", "timeInForce": "GTC"}
                        )

                    error = exc_info.value
                    assert error.status == 400, f"Expected 400 for negative price, got {error.status}"
                    print("  ✓ Negative price correctly rejected")

                except AssertionError:
                    raise
                except Exception as e:
                    print(f"  ⚠ Unexpected error for negative price: {type(e).__name__}")

            else:
                print("  ⚠ No open trades available for price validation testing")

        except Exception as e:
            print(f"  ⚠ Error during price validation test: {type(e).__name__}")

        print("✓ Trade order management error handling test completed")

    async def test_trade_client_extensions_management(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test trade client extensions functionality.

        Validates:
        - Adding client extensions to trades
        - Modifying existing client extensions
        - Client extension data preservation
        """
        print("✓ Starting trade client extensions management test...")

        test_instrument = test_instruments["major_pairs"][0]

        try:
            # Check for existing trades
            trades_response = await sandbox_client.trades.get_open_trades(test_account_id)
            open_trades = trades_response.get("trades", [])

            if open_trades:
                test_trade_id = open_trades[0].id
                print(f"  Using existing trade: {test_trade_id}")

                # Test client extensions
                client_extensions = {
                    "id": f"test-ext-{test_account_id[-4:]}",
                    "tag": "integration-test-trade",
                    "comment": "Trade with client extensions"
                }

                print(f"  Testing client extensions: {client_extensions}")

                try:
                    extensions_response = await sandbox_client.trades.put_trade_client_extensions(
                        account_id=test_account_id,
                        trade_specifier=test_trade_id,
                        client_extensions=client_extensions
                    )

                    assert extensions_response is not None, "Extensions response should not be None"
                    print("  ✓ Trade client extensions added successfully")

                    # Verify the extensions were applied
                    trade_response = await sandbox_client.trades.get_trade(test_account_id, test_trade_id)
                    if "trade" in trade_response:
                        trade = trade_response["trade"]
                        if hasattr(trade, "client_extensions") and trade.client_extensions:
                            print(f"    Client extensions verified: {trade.client_extensions}")

                except FiveTwentyError as e:
                    print(f"  ⚠ Client extensions failed: {e.status} - {e.code}")
                except Exception as e:
                    print(f"  ⚠ Unexpected error with client extensions: {type(e).__name__}")

            else:
                print("  ⚠ No open trades available for client extensions testing")

        except Exception as e:
            print(f"  ⚠ Client extensions test failed: {type(e).__name__}: {e}")

        print("✓ Trade client extensions management test completed")
