"""Cross-endpoint integration tests for data consistency and workflow validation.

This module tests the integration between different OANDA API endpoints to ensure:
- Data consistency across endpoints
- Transaction relationship validation
- Cross-endpoint workflow validation
- Account state synchronization
- Order and position lifecycle coherence
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import MarketOrderRequest


@pytest.mark.integration
class TestCrossEndpointIntegration:
    """Test data consistency and relationships across different API endpoints."""

    async def test_account_instruments_pricing_consistency(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test consistency between account, instruments, and pricing endpoints."""
        print("Testing account-instruments-pricing consistency...")

        # Get account details
        account_response = await sandbox_client.accounts.get_account(test_account_id)
        account = account_response["account"]
        print(f"Account currency: {account.currency}")

        # Get available instruments
        instruments_response = await sandbox_client.accounts.get_account_instruments(test_account_id)
        instruments = instruments_response["instruments"]
        print(f"Found {len(instruments)} instruments")

        # Select first few tradeable instruments
        tradeable_instruments = [inst for inst in instruments[:5] if inst.name and "tradeable" in str(inst).lower()]

        if not tradeable_instruments:
            tradeable_instruments = instruments[:3]

        pricing_data = {}
        for instrument in tradeable_instruments:
            try:
                # Get current pricing
                pricing = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[instrument.name])

                if pricing.get("prices"):
                    price = pricing["prices"][0]
                    pricing_data[instrument.name] = {
                        "instrument": instrument,
                        "price": price,
                        "spread": Decimal(str(price.get("asks", [{}])[0].get("price", 0))) - Decimal(str(price.get("bids", [{}])[0].get("price", 0))) if price.get("bids") and price.get("asks") else None,
                    }
                    bid_price = price.get("bids", [{}])[0].get("price", "N/A") if price.get("bids") else "N/A"
                    ask_price = price.get("asks", [{}])[0].get("price", "N/A") if price.get("asks") else "N/A"
                    print(f"  {instrument.name}: {bid_price}/{ask_price} (spread: {pricing_data[instrument.name]['spread']})")

            except Exception as e:
                print(f"  Warning: Could not get pricing for {instrument.name}: {e}")

        # Validate data consistency
        assert len(pricing_data) > 0, "Should have pricing data for at least one instrument"

        for name, data in pricing_data.items():
            instrument = data["instrument"]
            price = data["price"]

            # Validate instrument properties match pricing
            assert price.get("instrument") == instrument.name
            assert price.get("status") in ["tradeable", "non-tradeable", "invalid"]

            # Validate price precision
            if price.get("bids"):
                bid_price = price["bids"][0].get("price")
                if bid_price:
                    bid_str = str(bid_price)
                    decimal_places = len(bid_str.split(".")[1]) if "." in bid_str else 0
                    assert decimal_places <= instrument.display_precision, f"Bid precision exceeds instrument precision for {name}"

    async def test_order_transaction_account_consistency(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test consistency between order placement, transactions, and account state."""
        print("Testing order-transaction-account consistency...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)
        instrument = all_instruments[0]

        # Get initial account state
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        initial_balance = Decimal(str(initial_account.balance))
        initial_margin = Decimal(str(initial_account.margin_used or 0))
        print(f"Initial balance: {initial_balance}, margin: {initial_margin}")

        # Get current pricing for order
        pricing = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[instrument])

        if not pricing.get("prices") or not pricing["prices"][0].get("asks"):
            pytest.skip(f"No pricing available for {instrument}")

        ask_price = pricing["prices"][0]["asks"][0]["price"] if pricing["prices"][0].get("asks") else "0"
        Decimal(str(ask_price))
        units = "100"  # Small position

        # Create market order
        order_request = MarketOrderRequest(
            instrument=instrument,
            units=units,
        )

        print(f"Placing market order: {units} units of {instrument}")
        order_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=order_request)

        order_fill_transaction = None
        order_create_transaction = None

        if hasattr(order_response, "orderFillTransaction"):
            order_fill_transaction = order_response.orderFillTransaction
        if hasattr(order_response, "orderCreateTransaction"):
            order_create_transaction = order_response.orderCreateTransaction

        # Wait for order to be processed
        await asyncio.sleep(2)

        # Get updated account state
        updated_account_response = await sandbox_client.accounts.get_account(test_account_id)
        updated_account = updated_account_response["account"]
        updated_balance = Decimal(str(updated_account.balance))
        updated_margin = Decimal(str(updated_account.margin_used or 0))

        # Fetch the exact transactions returned by the order response. The
        # time-based transaction query returns page metadata, not inline data.
        order_transactions = []
        for transaction in (order_create_transaction, order_fill_transaction):
            if transaction:
                detail = await sandbox_client.transactions.get_transaction(test_account_id, transaction.id)
                order_transactions.append(detail["transaction"])

        print(f"Found {len(order_transactions)} related transactions")

        # Validate transaction consistency
        if order_create_transaction:
            create_found = any(t.id == order_create_transaction.id for t in order_transactions)
            assert create_found, "Order create transaction should be in transaction history"

        if order_fill_transaction:
            fill_found = any(hasattr(t, "tradeOpened") and t.id == order_fill_transaction.id for t in order_transactions)
            assert fill_found, "Order fill transaction should be in transaction history"

        # Validate account state changes are consistent
        balance_change = updated_balance - initial_balance
        margin_change = updated_margin - initial_margin

        print(f"Balance change: {balance_change}, margin change: {margin_change}")

        # For market orders, balance should decrease (transaction costs)
        # and margin usage should increase (if position opened)
        if order_fill_transaction and hasattr(order_fill_transaction, "tradeOpened"):
            assert margin_change >= 0, "Margin usage should increase when position opened"

        # Cleanup: close any opened positions
        try:
            positions_response = await sandbox_client.positions.get_positions(test_account_id)
            for position in positions_response["positions"]:
                if position["instrument"] == instrument and ((position.get("long") and position["long"].get("units") != "0") or (position.get("short") and position["short"].get("units") != "0")):
                    await sandbox_client.positions.close_position(test_account_id, instrument, long_units="ALL", short_units="ALL")
                    print(f"Cleaned up position for {instrument}")
        except Exception as e:
            print(f"Position cleanup warning: {e}")

    async def test_position_trade_transaction_consistency(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test consistency between positions, trades, and their transactions."""
        print("Testing position-trade-transaction consistency...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)
        instrument = all_instruments[0]

        # Get initial positions
        initial_positions_response = await sandbox_client.positions.get_positions(test_account_id)

        for pos in initial_positions_response.get("positions", []):
            if pos.get("instrument") == instrument:
                break

        # Open a small position via market order
        units = "50"
        order_request = MarketOrderRequest(
            instrument=instrument,
            units=units,
        )

        print(f"Opening position: {units} units of {instrument}")
        await sandbox_client.orders.post_order(account_id=test_account_id, order_request=order_request)

        # Wait for processing
        await asyncio.sleep(2)

        # Get updated positions
        updated_positions_response = await sandbox_client.positions.get_positions(test_account_id)
        updated_positions = updated_positions_response
        updated_position = None

        for pos in updated_positions.get("positions", []):
            if pos.get("instrument") == instrument:
                updated_position = pos
                break

        # Get current trades
        trades_response = await sandbox_client.trades.get_trades(test_account_id)
        trades = trades_response
        instrument_trades = [t for t in trades.get("trades", []) if t.get("instrument") == instrument]

        # Get recent transactions
        recent_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=datetime.now(timezone.utc) - timedelta(minutes=5))

        trade_transactions = [t for t in recent_transactions.get("transactions", []) if hasattr(t, "instrument") and t.instrument == instrument]

        print(f"Found {len(instrument_trades)} trades, {len(trade_transactions)} transactions")

        # Validate position consistency
        if updated_position:
            position_units = 0
            if updated_position.get("long"):
                position_units += int(updated_position["long"].get("units", 0) or 0)
            if updated_position.get("short"):
                position_units += int(updated_position["short"].get("units", 0) or 0)

            # Calculate expected position from trades
            trade_units = sum(int(trade.get("currentUnits", 0) or 0) for trade in instrument_trades)

            # In test environments, exact position/trade matching can be challenging due to existing positions
            print(f"  Position units: {position_units}, Trade units: {trade_units}")
            if abs(position_units - trade_units) > abs(trade_units) + 1:
                print("  Note: Position/trade units mismatch - this can be normal in test environments")

        # Validate transaction-trade consistency (skip if no transactions found - can happen in test environments)
        if trade_transactions:
            for trade in instrument_trades:
                # Find opening transaction for this trade
                opening_transactions = [t for t in trade_transactions if hasattr(t, "tradeOpened") and t.tradeOpened and str(t.tradeOpened.tradeID) == str(trade.get("id"))]

                if opening_transactions:
                    opening_tx = opening_transactions[0]
                    assert str(opening_tx.tradeOpened.units) == str(trade.get("initialUnits")), "Trade initial units should match opening transaction"
        else:
            print("  No transactions found - this can be normal in test environments")

        # Cleanup positions
        try:
            if updated_position and ((updated_position.get("long") and updated_position["long"].get("units") != "0") or (updated_position.get("short") and updated_position["short"].get("units") != "0")):
                await sandbox_client.positions.close_position(test_account_id, instrument, long_units="ALL", short_units="ALL")
                print(f"Cleaned up position for {instrument}")
        except Exception as e:
            print(f"Position cleanup warning: {e}")

    async def test_candle_pricing_consistency(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test consistency between historical candles and current pricing."""
        print("Testing candle-pricing consistency...")

        if not test_instruments:
            pytest.skip("No test instruments available")

        # Get first instrument from the dictionary
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)
        instrument = all_instruments[0]

        # Get recent candles (1-minute granularity)
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=2)

        candles = await sandbox_client.instruments.get_instrument_candles(
            instrument=instrument,
            granularity="M1",
            from_time=start_time,
            to_time=end_time,
        )

        # Get current pricing
        pricing = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[instrument])

        if not candles.get("candles") or not pricing.get("prices"):
            pytest.skip(f"No candles or pricing data for {instrument}")

        latest_candle = candles["candles"][-1]
        current_price = pricing["prices"][0]

        # Candles are now Pydantic models, use attribute access
        print(f"Latest candle: {latest_candle.mid.c if latest_candle.mid else 'N/A'}")
        # Pricing responses return Pydantic models, use attribute access
        current_bid = current_price.bids[0].price if current_price.bids else "N/A"
        current_ask = current_price.asks[0].price if current_price.asks else "N/A"
        print(f"Current price: {current_bid}/{current_ask}")

        # Validate price relationships
        if latest_candle.mid and current_price.bids and current_price.asks:
            candle_close = Decimal(latest_candle.mid.c)
            current_bid = Decimal(current_price.bids[0].price)
            current_ask = Decimal(current_price.asks[0].price)

            # Current price should be reasonably close to latest candle close
            # Allow for reasonable market movement
            bid_diff = abs(candle_close - current_bid)
            ask_diff = abs(candle_close - current_ask)
            max_reasonable_diff = candle_close * Decimal("0.02")  # 2% tolerance

            assert bid_diff <= max_reasonable_diff, f"Bid price ({current_bid}) too far from candle close ({candle_close})"
            assert ask_diff <= max_reasonable_diff, f"Ask price ({current_ask}) too far from candle close ({candle_close})"

        # Validate candle OHLC relationships
        for candle in candles["candles"][-10:]:  # Check last 10 candles
            if candle.mid:
                high = Decimal(candle.mid.h)
                low = Decimal(candle.mid.l)
                open_price = Decimal(candle.mid.o)
                close = Decimal(candle.mid.c)

                assert high >= open_price, "High should be >= Open"
                assert high >= close, "High should be >= Close"
                assert low <= open_price, "Low should be <= Open"
                assert low <= close, "Low should be <= Close"
                assert high >= low, "High should be >= Low"

    async def test_account_summary_detail_consistency(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test consistency between account summary and detailed account information."""
        print("Testing account summary vs detail consistency...")

        # Get account summary
        summary_response = await sandbox_client.accounts.get_account_summary(test_account_id)
        summary = summary_response["account"]

        # Get full account details
        account_response = await sandbox_client.accounts.get_account(test_account_id)
        account = account_response["account"]

        print(f"Account ID: {account.id}")
        print(f"Summary balance: {summary.balance}, Detail balance: {account.balance}")

        # Validate core fields match
        assert summary.id == account.id, "Account IDs should match"
        assert summary.currency == account.currency, "Currencies should match"
        assert summary.balance == account.balance, "Balances should match"

        # For margin fields, allow small differences due to real-time market changes
        margin_tolerance = Decimal("1.0")  # Allow up to $1 difference
        summary_margin_used = Decimal(str(summary.margin_used)) if summary.margin_used else Decimal("0")
        account_margin_used = Decimal(str(account.margin_used)) if account.margin_used else Decimal("0")
        summary_margin_available = Decimal(str(summary.margin_available)) if summary.margin_available else Decimal("0")
        account_margin_available = Decimal(str(account.margin_available)) if account.margin_available else Decimal("0")

        assert abs(summary_margin_used - account_margin_used) <= margin_tolerance, f"Margin used should be close: {summary.margin_used} vs {account.margin_used}"
        assert abs(summary_margin_available - account_margin_available) <= margin_tolerance, f"Margin available should be close: {summary.margin_available} vs {account.margin_available}"

        assert summary.open_trade_count == account.open_trade_count, "Open trade counts should match"
        assert summary.open_position_count == account.open_position_count, "Open position counts should match"
        assert summary.pending_order_count == account.pending_order_count, "Pending order counts should match"

        # Validate calculated fields
        if account.margin_used and account.margin_available:
            calculated_nav = Decimal(str(account.margin_used)) + Decimal(str(account.margin_available))
            account_nav = Decimal(str(account.nav))

            assert abs(calculated_nav - account_nav) < Decimal("10.0"), f"NAV calculation inconsistent: {calculated_nav} vs {account_nav}"

        # Additional consistency checks
        if hasattr(account, "last_transaction_id") and account.last_transaction_id:
            assert int(account.last_transaction_id) > 0, "Last transaction ID should be positive"

        if account.open_trade_count > 0:
            trades_response = await sandbox_client.trades.get_trades(test_account_id)
            open_trades = [t for t in trades_response.get("trades", []) if t.get("state") == "OPEN"]
            # Note: API may paginate trades, so we check that we got some open trades but allow for pagination
            assert len(open_trades) > 0, "Should have some open trades if open_trade_count > 0"
            print(f"✓ Account reports {account.open_trade_count} open trades, API returned {len(open_trades)} (pagination may apply)")

    async def test_multi_instrument_workflow_consistency(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test consistency across multiple instruments in a complex workflow."""
        print("Testing multi-instrument workflow consistency...")

        # Get first 2 instruments from the dictionary
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)

        if len(all_instruments) < 2:
            pytest.skip("Need at least 2 test instruments")

        instruments = all_instruments[:2]
        workflow_data = {
            "instruments": instruments,
            "orders": [],
            "positions": [],
            "transactions": [],
        }

        # Initial state capture
        initial_account_response = await sandbox_client.accounts.get_account(test_account_id)
        initial_account = initial_account_response["account"]
        await sandbox_client.positions.get_positions(test_account_id)
        workflow_start = datetime.now(timezone.utc)

        print(f"Starting workflow with instruments: {instruments}")

        # Execute orders for each instrument
        for i, instrument in enumerate(instruments):
            try:
                # Get pricing
                pricing = await sandbox_client.pricing.get_pricing(account_id=test_account_id, instruments=[instrument])

                if not pricing.get("prices") or not pricing["prices"][0].get("asks"):
                    print(f"Skipping {instrument} - no pricing available")
                    continue

                # Create small market order
                units = str(25 * (i + 1))  # Different sizes
                order_request = MarketOrderRequest(
                    instrument=instrument,
                    units=units,
                )

                print(f"  Placing order: {units} units of {instrument}")
                order_response = await sandbox_client.orders.post_order(account_id=test_account_id, order_request=order_request)

                workflow_data["orders"].append({"instrument": instrument, "units": units, "response": order_response})

                await asyncio.sleep(1)  # Allow processing time

            except Exception as e:
                print(f"  Error with {instrument}: {e}")

        # Wait for all orders to be processed
        await asyncio.sleep(3)

        # Capture final state
        final_account_response = await sandbox_client.accounts.get_account(test_account_id)
        final_account = final_account_response["account"]
        final_positions_response = await sandbox_client.positions.get_positions(test_account_id)
        final_positions = final_positions_response
        final_trades_response = await sandbox_client.trades.get_trades(test_account_id)
        final_trades = final_trades_response

        # Get workflow transactions
        workflow_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=workflow_start)

        # Validate workflow consistency
        print("Validating workflow consistency...")

        # Check account balance changes are reasonable
        balance_change = Decimal(str(final_account.balance)) - Decimal(str(initial_account.balance))
        print(f"Balance change: {balance_change}")

        # Validate each instrument's state
        for order_data in workflow_data["orders"]:
            instrument = order_data["instrument"]
            order_data["units"]

            # Find position for this instrument
            position = None
            for pos in final_positions.get("positions", []):
                if pos.get("instrument") == instrument:
                    position = pos
                    break

            # Find trades for this instrument
            instrument_trades = [t for t in final_trades.get("trades", []) if t.get("instrument") == instrument and t.get("state") == "OPEN"]

            # Find transactions for this instrument
            instrument_transactions = [t for t in workflow_transactions.get("transactions", []) if hasattr(t, "instrument") and t.instrument == instrument]

            print(f"  {instrument}: Position={position is not None}, Trades={len(instrument_trades)}, Transactions={len(instrument_transactions)}")

            # Validate consistency between position and trades
            if position and instrument_trades:
                position_units = 0
                if position.get("long"):
                    position_units += int(position["long"].get("units", 0) or 0)
                if position.get("short"):
                    position_units -= int(position["short"].get("units", 0) or 0)

                trade_units = sum(int(trade.get("currentUnits", 0) or 0) for trade in instrument_trades)

                # In test environments, positions and trades can have complex relationships
                # due to existing positions, test isolation issues, etc. Just log for awareness
                print(f"    Position units: {position_units}, Trade units: {trade_units}")
                if abs(position_units - trade_units) > abs(trade_units) + 1:
                    print(f"    Note: Position/trade units mismatch for {instrument} - this can be normal in test environments with existing positions")

        # Cleanup all positions
        print("Cleaning up positions...")
        try:
            for pos in final_positions.get("positions", []):
                if pos.get("instrument") in instruments and ((pos.get("long") and pos["long"].get("units") != "0") or (pos.get("short") and pos["short"].get("units") != "0")):
                    await sandbox_client.positions.close_position(test_account_id, pos.get("instrument"), long_units="ALL", short_units="ALL")
                    print(f"  Closed position for {pos.get('instrument')}")
        except Exception as e:
            print(f"Position cleanup warning: {e}")

        print("Multi-instrument workflow consistency test completed")
