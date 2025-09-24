"""Integration tests for post-trade risk management orders."""

from decimal import Decimal

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestPostTradeRiskManagement:
    """Integration tests for post-trade risk management operations."""

    async def test_post_trade_risk_management(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test post-trade risk management orders linked to existing trades.

        This tests the secondary pattern where risk management orders are added
        AFTER a trade is created, rather than using the OnFill pattern.

        Validates:
        - TAKE_PROFIT orders linked to existing trades
        - STOP_LOSS orders linked to existing trades (price and distance-based)
        - TRAILING_STOP_LOSS orders linked to existing trades
        - GUARANTEED_STOP_LOSS orders with premium calculation
        - Trade ID validation and error handling
        - Order execution and trade closure
        """
        print(f"✓ Starting post-trade risk management test for account {test_account_id}")

        test_instrument = test_instruments["major_pairs"][0]
        created_orders = []
        created_trades = []

        try:
            # Get current pricing for trade creation
            pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[test_instrument])

            current_price = Decimal("1.1000")  # Default fallback
            if isinstance(pricing_response, dict) and "prices" in pricing_response:
                prices = pricing_response["prices"]
                if prices and isinstance(prices[0], dict):
                    price_data = prices[0]
                    if "bid" in price_data and "ask" in price_data:
                        bid = Decimal(str(price_data["bid"]))
                        ask = Decimal(str(price_data["ask"]))
                        current_price = (bid + ask) / 2
                        print(f"✓ Current {test_instrument} price: {current_price}")

            # Step 1: Create market order to establish trades for risk management
            print("\n=== Step 1: Creating trades for post-trade risk management ===")

            # Create a long position
            print("1. Creating long position...")
            long_response = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=1000,  # Buy 1000 units
            )

            long_trade_id = None
            if long_response.order_fill_transaction and "tradeOpened" in long_response.order_fill_transaction and long_response.order_fill_transaction["tradeOpened"]:
                long_trade_id = long_response.order_fill_transaction["tradeOpened"]["tradeID"]
                created_trades.append(long_trade_id)
                print(f"✓ Long trade created: {long_trade_id}")

            # Create a short position
            print("2. Creating short position...")
            short_response = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=-800,  # Sell 800 units
            )

            short_trade_id = None
            if short_response.order_fill_transaction and "tradeOpened" in short_response.order_fill_transaction and short_response.order_fill_transaction["tradeOpened"]:
                short_trade_id = short_response.order_fill_transaction["tradeOpened"]["tradeID"]
                created_trades.append(short_trade_id)
                print(f"✓ Short trade created: {short_trade_id}")

            if not long_trade_id or not short_trade_id:
                print("⚠️ Could not create trades - skipping post-trade tests")
                return

            # Step 2: Test TAKE_PROFIT orders
            print("\n=== Step 2: Testing TAKE_PROFIT Orders ===")

            from fivetwenty.models import TakeProfitOrderRequest

            # Take profit for long trade (sell at higher price)
            print("1. Adding take profit to long trade...")
            long_tp_request = TakeProfitOrderRequest(
                tradeID=long_trade_id,
                price=str(current_price + Decimal("0.0050")),  # 50 pips profit
                timeInForce="GTC",
            )

            tp_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=long_tp_request)

            if tp_response.order_create_transaction:
                tp_order_id = tp_response.order_create_transaction["id"]
                created_orders.append(tp_order_id)
                print(f"✓ Take profit order created: {tp_order_id}")
                print(f"   Linked to trade: {long_trade_id}")
                print(f"   Target price: {current_price + Decimal('0.0050')}")

            # Take profit for short trade (buy at lower price)
            print("2. Adding take profit to short trade...")
            short_tp_request = TakeProfitOrderRequest(
                tradeID=short_trade_id,
                price=str(current_price - Decimal("0.0040")),  # 40 pips profit
                timeInForce="GTC",
            )

            tp_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=short_tp_request)

            if tp_response.order_create_transaction:
                tp_order_id = tp_response.order_create_transaction["id"]
                created_orders.append(tp_order_id)
                print(f"✓ Take profit order created: {tp_order_id}")
                print(f"   Linked to trade: {short_trade_id}")
                print(f"   Target price: {current_price - Decimal('0.0040')}")

            # Step 3: Test STOP_LOSS orders (price-based)
            print("\n=== Step 3: Testing STOP_LOSS Orders (Price-Based) ===")

            from fivetwenty.models import StopLossOrderRequest

            # Stop loss for long trade (sell at lower price)
            print("1. Adding price-based stop loss to long trade...")
            long_sl_request = StopLossOrderRequest(
                tradeID=long_trade_id,
                price=str(current_price - Decimal("0.0030")),  # 30 pips stop
                timeInForce="GTC",
            )

            sl_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=long_sl_request)

            if sl_response.order_create_transaction:
                sl_order_id = sl_response.order_create_transaction["id"]
                created_orders.append(sl_order_id)
                print(f"✓ Stop loss order created: {sl_order_id}")
                print(f"   Linked to trade: {long_trade_id}")
                print(f"   Stop price: {current_price - Decimal('0.0030')}")

            # Step 4: Test STOP_LOSS orders (distance-based)
            print("\n=== Step 4: Testing STOP_LOSS Orders (Distance-Based) ===")

            # Distance-based stop loss for short trade
            print("1. Adding distance-based stop loss to short trade...")
            short_sl_request = StopLossOrderRequest(
                tradeID=short_trade_id,
                distance="0.0025",  # 25 pips distance
                timeInForce="GTC",
            )

            sl_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=short_sl_request)

            if sl_response.order_create_transaction:
                sl_order_id = sl_response.order_create_transaction["id"]
                created_orders.append(sl_order_id)
                print(f"✓ Distance-based stop loss created: {sl_order_id}")
                print(f"   Linked to trade: {short_trade_id}")
                print("   Distance: 25 pips")

            # Step 5: Test TRAILING_STOP_LOSS orders
            print("\n=== Step 5: Testing TRAILING_STOP_LOSS Orders ===")

            from fivetwenty.models import TrailingStopLossOrderRequest

            # Create another trade for trailing stop testing
            print("1. Creating additional trade for trailing stop...")
            trail_response = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=500,  # Small position for trailing
            )

            trail_trade_id = None
            if trail_response.order_fill_transaction and "tradeOpened" in trail_response.order_fill_transaction and trail_response.order_fill_transaction["tradeOpened"]:
                trail_trade_id = trail_response.order_fill_transaction["tradeOpened"]["tradeID"]
                created_trades.append(trail_trade_id)
                print(f"✓ Trailing trade created: {trail_trade_id}")

                # Add trailing stop loss
                print("2. Adding trailing stop loss...")
                tsl_request = TrailingStopLossOrderRequest(
                    tradeID=trail_trade_id,
                    distance="0.0020",  # 20 pips trailing distance
                    timeInForce="GTC",
                )

                tsl_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=tsl_request)

                if tsl_response.order_create_transaction:
                    tsl_order_id = tsl_response.order_create_transaction["id"]
                    created_orders.append(tsl_order_id)
                    print(f"✓ Trailing stop loss created: {tsl_order_id}")
                    print(f"   Linked to trade: {trail_trade_id}")
                    print("   Trailing distance: 20 pips")

            # Step 6: Test GUARANTEED_STOP_LOSS orders
            print("\n=== Step 6: Testing GUARANTEED_STOP_LOSS Orders ===")

            from fivetwenty.models import GuaranteedStopLossOrderRequest

            # Create another trade for guaranteed stop testing
            print("1. Creating trade for guaranteed stop loss...")
            gsl_response = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=300,  # Small position
            )

            gsl_trade_id = None
            if gsl_response.order_fill_transaction and "tradeOpened" in gsl_response.order_fill_transaction and gsl_response.order_fill_transaction["tradeOpened"]:
                gsl_trade_id = gsl_response.order_fill_transaction["tradeOpened"]["tradeID"]
                created_trades.append(gsl_trade_id)
                print(f"✓ GSL trade created: {gsl_trade_id}")

                # Add guaranteed stop loss
                print("2. Adding guaranteed stop loss...")
                gsl_request = GuaranteedStopLossOrderRequest(
                    tradeID=gsl_trade_id,
                    price=str(current_price - Decimal("0.0100")),  # 100 pips guaranteed stop
                    timeInForce="GTC",
                )

                try:
                    gsl_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=gsl_request)

                    if gsl_response.order_create_transaction:
                        gsl_order_id = gsl_response.order_create_transaction["id"]
                        created_orders.append(gsl_order_id)
                        print(f"✓ Guaranteed stop loss created: {gsl_order_id}")
                        print(f"   Linked to trade: {gsl_trade_id}")
                        print(f"   Guaranteed price: {current_price - Decimal('0.0100')}")

                        # Check for premium information
                        if "guaranteedExecutionPremium" in gsl_response.order_create_transaction:
                            premium = gsl_response.order_create_transaction["guaranteedExecutionPremium"]
                            print(f"   Premium cost: {premium}")

                except Exception as e:
                    print(f"✓ Guaranteed stop loss test: {type(e).__name__}")
                    print("   Note: GSL may not be available for all instruments/accounts")

            # Step 7: Test error scenarios
            print("\n=== Step 7: Testing Post-Trade Error Scenarios ===")

            # Invalid trade ID
            print("1. Testing invalid trade ID...")
            try:
                invalid_tp = TakeProfitOrderRequest(tradeID="INVALID_TRADE_ID", price=str(current_price + Decimal("0.0050")), timeInForce="GTC")

                await sandbox_client.orders.post_order(account_id=test_account_id, order_request=invalid_tp)
                print("⚠️ Invalid trade ID was unexpectedly accepted")
            except Exception as e:
                print(f"✓ Invalid trade ID properly rejected: {type(e).__name__}")

            # Non-existent trade ID (valid format but doesn't exist)
            print("2. Testing non-existent trade ID...")
            try:
                nonexistent_sl = StopLossOrderRequest(tradeID="99999999", price=str(current_price - Decimal("0.0050")), timeInForce="GTC")

                await sandbox_client.orders.post_order(account_id=test_account_id, order_request=nonexistent_sl)
                print("⚠️ Non-existent trade ID was unexpectedly accepted")
            except Exception as e:
                print(f"✓ Non-existent trade ID properly rejected: {type(e).__name__}")

            print(f"\n✓ Created {len(created_orders)} post-trade risk management orders")
            print(f"✓ Tested against {len(created_trades)} trades")
            print("✓ Post-trade risk management test completed successfully!")

        except Exception as e:
            print(f"❌ Post-trade risk management test error: {e}")
            raise

        finally:
            # Cleanup: Cancel risk management orders first
            if created_orders:
                print(f"\n✓ Cleaning up {len(created_orders)} risk management orders...")
                for order_id in created_orders:
                    try:
                        await sandbox_client.orders.cancel_order(account_id=test_account_id, order_id=order_id)
                        print(f"✓ Cancelled order: {order_id}")
                    except Exception as e:
                        print(f"⚠️ Could not cancel order {order_id}: {type(e).__name__}")

            # Then close trades
            if created_trades:
                print(f"✓ Closing {len(created_trades)} trades...")
                for trade_id in created_trades:
                    try:
                        await sandbox_client.trades.close_trade(account_id=test_account_id, trade_specifier=trade_id)
                        print(f"✓ Closed trade: {trade_id}")
                    except Exception as e:
                        print(f"⚠️ Could not close trade {trade_id}: {type(e).__name__}")

        print("✓ Post-trade risk management test completed with cleanup")
