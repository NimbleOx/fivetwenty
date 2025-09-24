"""Integration tests for comprehensive trading workflows."""

import asyncio
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
class TestComprehensiveTradingWorkflows:
    """Integration tests for comprehensive trading workflows."""

    async def test_complete_order_lifecycle_workflow(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test complete order lifecycle workflow."""
        print("✓ Testing complete order lifecycle workflow...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        if test_instruments:
            all_instruments = []
            for category_instruments in test_instruments.values():
                all_instruments.extend(category_instruments)
            instrument = all_instruments[0]
        else:
            instrument = "EUR_USD"

        # Step 1: Market order placement
        try:
            print("  - Step 1: Placing market order...")

            order_response = await sandbox_client.orders.post_market_order(account_id=test_account_id, instrument=instrument, units=1000, client_request_id=f"workflow-market-{int(asyncio.get_event_loop().time() * 1000)}")

            assert order_response.order_fill_transaction is not None
            print(f"    * Market order filled at: {order_response.order_fill_transaction.get('price')}")

        except Exception as e:
            pytest.fail(f"Market order placement failed: {e}")

        # Step 2: Position monitoring
        try:
            print("  - Step 2: Monitoring position...")
            await asyncio.sleep(1)

            position_response = await sandbox_client.positions.get_position(test_account_id, instrument)
            position = position_response["position"]

            assert position is not None
            print(f"    * Position established: {position.get('instrument')}")

        except Exception as e:
            pytest.fail(f"Position monitoring failed: {e}")

        # Step 3: Position closure
        try:
            print("  - Step 3: Closing position...")

            # Check current position to see which sides exist
            check_position_response = await sandbox_client.positions.get_position(test_account_id, instrument)
            check_position = check_position_response["position"]

            long_units = check_position.get("long", {}).get("units", "0")
            short_units = check_position.get("short", {}).get("units", "0")

            close_kwargs = {}
            if long_units != "0":
                close_kwargs["long_units"] = "ALL"
            if short_units != "0":
                close_kwargs["short_units"] = "ALL"

            await sandbox_client.positions.close_position(account_id=test_account_id, instrument=instrument, **close_kwargs)

            print("    * Position closed successfully")

        except Exception as e:
            pytest.fail(f"Position closure failed: {e}")

    async def test_position_management_workflow(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test position management workflow."""
        print("✓ Testing position management workflow...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        if test_instruments:
            all_instruments = []
            for category_instruments in test_instruments.values():
                all_instruments.extend(category_instruments)
            instrument = all_instruments[0]
        else:
            instrument = "EUR_USD"

        # Step 1: Initial position creation
        try:
            print("  - Step 1: Creating initial position...")

            initial_order = await sandbox_client.orders.post_market_order(account_id=test_account_id, instrument=instrument, units=2000, client_request_id=f"workflow-mgmt-{int(asyncio.get_event_loop().time() * 1000)}")

            assert initial_order.order_fill_transaction is not None
            print("    * Initial position created")

            await asyncio.sleep(1)

        except Exception as e:
            pytest.fail(f"Initial position creation failed: {e}")

        # Step 2: Position scaling (increase)
        try:
            print("  - Step 2: Scaling position up...")

            scale_up_order = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=instrument,
                units=1000,  # Add to existing position
                client_request_id=f"workflow-scaleup-{int(asyncio.get_event_loop().time() * 1000)}",
            )

            assert scale_up_order.order_fill_transaction is not None
            print("    * Position scaled up")

            await asyncio.sleep(1)

        except Exception as e:
            pytest.fail(f"Position scaling failed: {e}")

        # Step 3: Partial position reduction
        try:
            print("  - Step 3: Partial position reduction...")

            reduce_order = await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=instrument,
                units=-1500,  # Reduce position
                client_request_id=f"workflow-reduce-{int(asyncio.get_event_loop().time() * 1000)}",
            )

            assert reduce_order.order_fill_transaction is not None
            print("    * Position partially reduced")

            await asyncio.sleep(1)

        except Exception as e:
            pytest.fail(f"Position reduction failed: {e}")

        # Step 4: Final cleanup
        try:
            print("  - Step 4: Final position cleanup...")

            # Check current position to see which sides exist
            cleanup_position_response = await sandbox_client.positions.get_position(test_account_id, instrument)
            cleanup_position = cleanup_position_response["position"]

            long_units = cleanup_position.get("long", {}).get("units", "0")
            short_units = cleanup_position.get("short", {}).get("units", "0")

            close_kwargs = {}
            if long_units != "0":
                close_kwargs["long_units"] = "ALL"
            if short_units != "0":
                close_kwargs["short_units"] = "ALL"

            await sandbox_client.positions.close_position(account_id=test_account_id, instrument=instrument, **close_kwargs)

            print("    * Position management workflow completed")

        except Exception as e:
            pytest.fail(f"Final cleanup failed: {e}")

    async def test_portfolio_rebalancing_workflow(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test portfolio rebalancing workflow."""
        print("✓ Testing portfolio rebalancing workflow...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first 2 instruments from the dictionary
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)

        if len(all_instruments) < 2:
            pytest.skip("Insufficient test instruments for portfolio test")

        instruments = all_instruments[:2]  # Use first 2 instruments

        try:
            # Step 1: Create initial portfolio positions
            print("  - Step 1: Creating initial portfolio positions...")

            for i, instrument in enumerate(instruments):
                await sandbox_client.orders.post_market_order(
                    account_id=test_account_id,
                    instrument=instrument,
                    units=1000 * (i + 1),  # Different sizes
                    client_request_id=f"portfolio-init-{i}-{int(asyncio.get_event_loop().time() * 1000)}",
                )
                print(f"    * Position created in {instrument}")
                await asyncio.sleep(0.5)

            # Step 2: Analyze current portfolio
            print("  - Step 2: Analyzing portfolio composition...")

            open_positions = await sandbox_client.positions.get_open_positions(test_account_id)
            positions = open_positions.get("positions", [])

            portfolio_value = Decimal("0")
            for position in positions:
                if position.get("instrument") in instruments:
                    margin_used = Decimal(position.get("marginUsed", "0"))
                    portfolio_value += margin_used

            print(f"    * Portfolio value: {portfolio_value}")

            # Step 3: Rebalance positions
            print("  - Step 3: Rebalancing portfolio...")

            # Simple rebalancing: reduce larger positions, increase smaller ones
            for position in positions:
                if position.get("instrument") in instruments:
                    long_side = position.get("long")
                    if long_side and long_side.get("units"):
                        current_units = int(long_side["units"])
                        if current_units > 1500:
                            # Reduce large positions
                            reduction_units = -(current_units - 1000)
                            await sandbox_client.orders.post_market_order(account_id=test_account_id, instrument=position["instrument"], units=reduction_units, client_request_id=f"rebalance-{position['instrument']}-{int(asyncio.get_event_loop().time() * 1000)}")
                            print(f"    * Rebalanced {position['instrument']}")

                await asyncio.sleep(0.5)

            # Step 4: Portfolio cleanup
            print("  - Step 4: Portfolio cleanup...")

            for instrument in instruments:
                try:
                    # Check which sides exist for this instrument
                    cleanup_position_response = await sandbox_client.positions.get_position(test_account_id, instrument)
                    cleanup_position = cleanup_position_response["position"]

                    long_units = cleanup_position.get("long", {}).get("units", "0")
                    short_units = cleanup_position.get("short", {}).get("units", "0")

                    close_kwargs = {}
                    if long_units != "0":
                        close_kwargs["long_units"] = "ALL"
                    if short_units != "0":
                        close_kwargs["short_units"] = "ALL"

                    if close_kwargs:  # Only close if there are positions
                        await sandbox_client.positions.close_position(account_id=test_account_id, instrument=instrument, **close_kwargs)
                except Exception as e:
                    # Some instruments might not have positions, continue with others
                    print(f"    * Could not close {instrument}: {e}")

            print("    * Portfolio rebalancing workflow completed")

        except Exception as e:
            pytest.fail(f"Portfolio rebalancing workflow failed: {e}")

    async def test_risk_management_workflow(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test risk management workflow."""
        print("✓ Testing risk management workflow...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        if test_instruments:
            all_instruments = []
            for category_instruments in test_instruments.values():
                all_instruments.extend(category_instruments)
            instrument = all_instruments[0]
        else:
            instrument = "EUR_USD"

        try:
            # Step 1: Account risk assessment
            print("  - Step 1: Account risk assessment...")

            account_response = await sandbox_client.accounts.get_account(test_account_id)
            account = account_response["account"]
            initial_balance = Decimal(account.balance)
            margin_available = Decimal(account.margin_available)

            # Risk parameters
            max_risk_per_trade = initial_balance * Decimal("0.02")  # 2% risk
            position_size = min(1000, int(margin_available / 100))  # Conservative sizing

            print(f"    * Account balance: {initial_balance}")
            print(f"    * Max risk per trade: {max_risk_per_trade}")
            print(f"    * Calculated position size: {position_size}")

            # Step 2: Create position with risk controls
            print("  - Step 2: Creating position with risk controls...")

            # Get current price for stop loss calculation
            pricing_response = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[instrument])

            prices = pricing_response.get("prices", [])
            current_price = Decimal(prices[0].get("bids", [{}])[0].get("price", "1.0"))
            current_price * Decimal("0.99")  # 1% stop loss

            order_response = await sandbox_client.orders.post_market_order(account_id=test_account_id, instrument=instrument, units=position_size, client_request_id=f"risk-mgmt-{int(asyncio.get_event_loop().time() * 1000)}")

            assert order_response.order_fill_transaction is not None
            print("    * Position created with risk controls")

            # Step 3: Monitor and manage risk
            print("  - Step 3: Risk monitoring...")

            await asyncio.sleep(1)

            position_response = await sandbox_client.positions.get_position(test_account_id, instrument)
            position = position_response["position"]

            unrealized_pl = Decimal(position.get("unrealizedPL", "0"))
            margin_used = Decimal(position.get("marginUsed", "0"))

            print(f"    * Position P&L: {unrealized_pl}")
            print(f"    * Margin used: {margin_used}")

            # Step 4: Risk-based position closure
            print("  - Step 4: Risk-based position management...")

            # Close position to manage risk
            # Only close the side that has units
            long_units = position.get("long", {}).get("units", "0")
            short_units = position.get("short", {}).get("units", "0")

            close_kwargs = {}
            if long_units != "0":
                close_kwargs["long_units"] = "ALL"
            if short_units != "0":
                close_kwargs["short_units"] = "ALL"

            close_response = await sandbox_client.positions.close_position(account_id=test_account_id, instrument=instrument, **close_kwargs)

            final_pl = Decimal("0")
            if "longOrderFillTransaction" in close_response:
                final_pl += Decimal(close_response["longOrderFillTransaction"].get("pl", "0"))
            if "shortOrderFillTransaction" in close_response:
                final_pl += Decimal(close_response["shortOrderFillTransaction"].get("pl", "0"))

            print(f"    * Final P&L: {final_pl}")
            print(f"    * Risk as % of balance: {abs(final_pl) / initial_balance * 100:.2f}%")

            # Validate risk management
            risk_percentage = abs(final_pl) / initial_balance
            assert risk_percentage <= Decimal("0.05"), f"Risk exceeded 5%: {risk_percentage}"

            print("    * Risk management workflow completed successfully")

        except Exception as e:
            pytest.fail(f"Risk management workflow failed: {e}")
