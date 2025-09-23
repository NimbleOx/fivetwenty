"""Integration test configuration and fixtures."""

import os
from decimal import Decimal
from pathlib import Path

import pytest
from dotenv import load_dotenv

from fivetwenty import AsyncClient, Client, Environment

# Load .env file from project root if it exists
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


@pytest.fixture(scope="session")
def integration_config():
    """Integration test configuration."""
    return {
        "environment": Environment.PRACTICE,  # Always use practice environment
        "token": os.getenv("FIVETWENTY_OANDA_TOKEN"),
        "account_id": os.getenv("FIVETWENTY_OANDA_ACCOUNT"),
        "timeout": 30.0,
        "max_retries": 3,
    }


@pytest.fixture
async def sandbox_client_no_cleanup(integration_config):
    """Async client configured for sandbox testing WITHOUT automatic cleanup."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")

    async with AsyncClient(token=integration_config["token"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
        yield client


@pytest.fixture
async def sandbox_client(integration_config, test_account_id):
    """Async client with automatic order and trade cleanup enabled by default."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")

    async with AsyncClient(token=integration_config["token"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
        created_order_ids = []
        created_trade_ids = []

        # Store original methods
        original_post_limit_order = client.orders.post_limit_order
        original_post_stop_order = client.orders.post_stop_order
        original_post_market_order = client.orders.post_market_order
        original_post_market_if_touched_order = client.orders.post_market_if_touched_order
        original_post_order = client.orders.post_order

        async def track_order_creation(original_method, *args, **kwargs):
            """Wrapper to track order creation."""
            response = await original_method(*args, **kwargs)
            if response and hasattr(response, 'order_create_transaction') and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                if order_id:
                    created_order_ids.append(order_id)
            # Also track trades created from market orders
            if response and hasattr(response, 'order_fill_transaction') and response.order_fill_transaction:
                fill_tx = response.order_fill_transaction
                if "tradeOpened" in fill_tx and "tradeID" in fill_tx["tradeOpened"]:
                    trade_id = fill_tx["tradeOpened"]["tradeID"]
                    created_trade_ids.append(trade_id)
            return response

        # Patch the order creation methods
        client.orders.post_limit_order = lambda *args, **kwargs: track_order_creation(original_post_limit_order, *args, **kwargs)
        client.orders.post_stop_order = lambda *args, **kwargs: track_order_creation(original_post_stop_order, *args, **kwargs)
        client.orders.post_market_order = lambda *args, **kwargs: track_order_creation(original_post_market_order, *args, **kwargs)
        client.orders.post_market_if_touched_order = lambda *args, **kwargs: track_order_creation(original_post_market_if_touched_order, *args, **kwargs)
        client.orders.post_order = lambda *args, **kwargs: track_order_creation(original_post_order, *args, **kwargs)

        yield client

        # Restore original methods
        client.orders.post_limit_order = original_post_limit_order
        client.orders.post_stop_order = original_post_stop_order
        client.orders.post_market_order = original_post_market_order
        client.orders.post_market_if_touched_order = original_post_market_if_touched_order
        client.orders.post_order = original_post_order

        # Cleanup
        order_cleanup_count = 0
        trade_cleanup_count = 0

        # Clean up orders
        for order_id in created_order_ids:
            try:
                order_response = await client.orders.get_order(test_account_id, order_id)
                if order_response and "order" in order_response:
                    order = order_response["order"]
                    if order.get("state") == "PENDING":
                        await client.orders.cancel_order(test_account_id, order_id)
                        order_cleanup_count += 1
            except Exception:
                pass  # Order may already be cancelled or filled

        # Clean up trades
        for trade_id in created_trade_ids:
            try:
                close_response = await client.trades.close_trade(
                    account_id=test_account_id,
                    trade_specifier=trade_id
                )
                if close_response:
                    trade_cleanup_count += 1
            except Exception:
                pass  # Trade may already be closed

        if order_cleanup_count > 0 or trade_cleanup_count > 0:
            print(f"✓ Auto-cleaned up {order_cleanup_count} orders and {trade_cleanup_count} trades")


# Alias for backward compatibility
sandbox_client_with_auto_cleanup = sandbox_client


@pytest.fixture
def sync_sandbox_client(integration_config):
    """Sync client configured for sandbox testing."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")

    with Client(token=integration_config["token"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
        yield client


@pytest.fixture
def test_account_id(integration_config) -> str:
    """Test account ID for integration tests."""
    if not integration_config["account_id"]:
        pytest.skip("FIVETWENTY_OANDA_ACCOUNT environment variable not set")
    return integration_config["account_id"]


@pytest.fixture
def test_instruments():
    """Common test instruments for integration tests."""
    return {
        "major_pairs": ["EUR_USD", "GBP_USD", "USD_JPY"],
        "minor_pairs": ["EUR_GBP", "GBP_JPY", "AUD_CAD"],
        "metals": ["XAU_USD", "XAG_USD"],
        "indices": ["SPX500_USD", "UK100_GBP"],
    }


@pytest.fixture
def financial_assertions():
    """Helper functions for financial data assertions."""

    class FinancialAssertions:
        """Financial data assertion helpers."""

        @staticmethod
        def assert_decimal_precision(value: str, expected_precision: int):
            """Assert decimal has correct precision."""
            decimal_value = Decimal(value)
            decimal_places = abs(decimal_value.as_tuple().exponent)
            assert decimal_places <= expected_precision, f"Expected max {expected_precision} decimal places, got {decimal_places}"

        @staticmethod
        def assert_price_reasonable(price: str, instrument: str):
            """Assert price is within reasonable ranges."""
            price_val = float(price)

            # Basic sanity checks for major instruments
            if "JPY" in instrument:
                assert 50 < price_val < 200, f"JPY price {price_val} seems unreasonable"
            elif "XAU" in instrument:  # Gold
                assert 1000 < price_val < 3000, f"Gold price {price_val} seems unreasonable"
            else:  # Major pairs
                assert 0.1 < price_val < 10, f"Price {price_val} for {instrument} seems unreasonable"

        @staticmethod
        def assert_spread_reasonable(bid: str, ask: str, instrument: str):
            """Assert bid/ask spread is reasonable."""
            bid_val = float(bid)
            ask_val = float(ask)
            spread = ask_val - bid_val

            assert spread > 0, f"Ask ({ask_val}) should be higher than bid ({bid_val})"

            # Reasonable spread checks
            spread_pct = (spread / bid_val) * 100
            assert spread_pct < 1.0, f"Spread {spread_pct:.4f}% seems too wide for {instrument}"

    return FinancialAssertions()


@pytest.fixture
def vcr_config():
    """VCR configuration for response recording."""
    return {
        "filter_headers": ["authorization"],
        "filter_query_parameters": ["access_token"],
        "decode_compressed_response": True,
        "record_mode": "once",
    }


# Skip markers for different test types
integration_only = pytest.mark.skipif(os.getenv("SKIP_INTEGRATION") == "1", reason="Integration tests skipped (SKIP_INTEGRATION=1)")

requires_token = pytest.mark.skipif(not os.getenv("FIVETWENTY_OANDA_TOKEN"), reason="Requires FIVETWENTY_OANDA_TOKEN environment variable")

requires_account = pytest.mark.skipif(not os.getenv("FIVETWENTY_OANDA_ACCOUNT"), reason="Requires FIVETWENTY_OANDA_ACCOUNT environment variable")


class CleanupTracker:
    """Tracks orders and trades created during tests for automatic cleanup."""

    def __init__(self, client, account_id):
        self.client = client
        self.account_id = account_id
        self.created_orders = []
        self.created_trades = []

    def track_order(self, order_id):
        """Track an order for cleanup."""
        if order_id and order_id not in self.created_orders:
            self.created_orders.append(order_id)

    def track_trade(self, trade_id):
        """Track a trade for cleanup."""
        if trade_id and trade_id not in self.created_trades:
            self.created_trades.append(trade_id)

    async def cleanup_orders(self):
        """Clean up all tracked orders."""
        cleanup_count = 0
        for order_id in self.created_orders[:]:  # Copy list to avoid modification during iteration
            try:
                # Check if order still exists and is cancellable
                order_response = await self.client.orders.get_order(self.account_id, order_id)
                if order_response and "order" in order_response:
                    order = order_response["order"]
                    if order.get("state") == "PENDING":
                        await self.client.orders.cancel_order(self.account_id, order_id)
                        cleanup_count += 1
                self.created_orders.remove(order_id)
            except Exception:
                # Order may already be filled, cancelled, or non-existent - remove from tracking
                self.created_orders.remove(order_id)
        return cleanup_count

    async def cleanup_trades(self):
        """Clean up all tracked trades."""
        cleanup_count = 0
        for trade_id in self.created_trades[:]:  # Copy list to avoid modification during iteration
            try:
                # Try to close the trade
                close_response = await self.client.trades.close_trade(
                    account_id=self.account_id,
                    trade_specifier=trade_id
                )
                if close_response:
                    cleanup_count += 1
                self.created_trades.remove(trade_id)
            except Exception:
                # Trade may already be closed or non-existent - remove from tracking
                self.created_trades.remove(trade_id)
        return cleanup_count

    async def cleanup_all(self):
        """Clean up all tracked orders and trades."""
        orders_cleaned = await self.cleanup_orders()
        trades_cleaned = await self.cleanup_trades()
        return orders_cleaned, trades_cleaned


@pytest.fixture
async def cleanup_tracker(sandbox_client, test_account_id):
    """Fixture that provides automatic cleanup of orders and trades."""
    tracker = CleanupTracker(sandbox_client, test_account_id)

    yield tracker

    # Cleanup after test
    try:
        orders_cleaned, trades_cleaned = await tracker.cleanup_all()
        if orders_cleaned > 0 or trades_cleaned > 0:
            print(f"✓ Cleaned up {orders_cleaned} orders and {trades_cleaned} trades")
    except Exception as e:
        print(f"⚠ Cleanup failed: {type(e).__name__}")


@pytest.fixture
async def auto_cleanup_orders(sandbox_client, test_account_id):
    """Fixture that automatically tracks and cleans up orders created during tests."""
    created_order_ids = []

    # Create a wrapper function to track order creation
    original_post_limit_order = sandbox_client.orders.post_limit_order
    original_post_stop_order = sandbox_client.orders.post_stop_order
    original_post_market_order = sandbox_client.orders.post_market_order
    original_post_market_if_touched_order = sandbox_client.orders.post_market_if_touched_order
    original_post_order = sandbox_client.orders.post_order

    async def track_order_creation(original_method, *args, **kwargs):
        """Wrapper to track order creation."""
        response = await original_method(*args, **kwargs)
        if response and hasattr(response, 'order_create_transaction') and response.order_create_transaction:
            order_id = response.order_create_transaction.get("id")
            if order_id:
                created_order_ids.append(order_id)
        return response

    # Patch the order creation methods
    sandbox_client.orders.post_limit_order = lambda *args, **kwargs: track_order_creation(original_post_limit_order, *args, **kwargs)
    sandbox_client.orders.post_stop_order = lambda *args, **kwargs: track_order_creation(original_post_stop_order, *args, **kwargs)
    sandbox_client.orders.post_market_order = lambda *args, **kwargs: track_order_creation(original_post_market_order, *args, **kwargs)
    sandbox_client.orders.post_market_if_touched_order = lambda *args, **kwargs: track_order_creation(original_post_market_if_touched_order, *args, **kwargs)
    sandbox_client.orders.post_order = lambda *args, **kwargs: track_order_creation(original_post_order, *args, **kwargs)

    yield created_order_ids

    # Restore original methods
    sandbox_client.orders.post_limit_order = original_post_limit_order
    sandbox_client.orders.post_stop_order = original_post_stop_order
    sandbox_client.orders.post_market_order = original_post_market_order
    sandbox_client.orders.post_market_if_touched_order = original_post_market_if_touched_order
    sandbox_client.orders.post_order = original_post_order

    # Cleanup
    cleanup_count = 0
    for order_id in created_order_ids:
        try:
            order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
            if order_response and "order" in order_response:
                order = order_response["order"]
                if order.get("state") == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_id)
                    cleanup_count += 1
        except Exception:
            pass  # Order may already be cancelled or filled

    if cleanup_count > 0:
        print(f"✓ Auto-cleaned up {cleanup_count} orders")
