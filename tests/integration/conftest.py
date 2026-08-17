"""Integration test configuration and fixtures."""

import asyncio
import hashlib
import os
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from dotenv import load_dotenv

from fivetwenty import AsyncClient, Client, Environment
from tests.integration.helpers import cleanup_error_message, is_tolerated_cleanup_error

CLIENT_REQUEST_ID_PREFIX = "fivetwenty-itest"
SAFETY_SWEEP_ATTEMPTS = 3

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


def _resource_id(resource: Any) -> str | None:
    """Extract an OANDA resource id from a dict or model."""
    if isinstance(resource, dict):
        value = resource.get("id")
    else:
        value = getattr(resource, "id", None)
    return str(value) if value is not None else None


async def _pending_order_ids(client: AsyncClient, account_id: str) -> set[str]:
    """Return currently pending order ids for safety checks."""
    response = await client.orders.get_pending_orders(account_id)
    orders = response.get("orders", []) if isinstance(response, dict) else []
    return {order_id for order in orders if (order_id := _resource_id(order))}


async def _open_trade_ids(client: AsyncClient, account_id: str) -> set[str]:
    """Return currently open trade ids for safety checks."""
    response = await client.trades.get_open_trades(account_id)
    trades = response.get("trades", []) if isinstance(response, dict) else []
    return {trade_id for trade in trades if (trade_id := _resource_id(trade))}


async def _read_account_ids(label: str, read_ids) -> set[str] | None:
    """Read account resource ids with short retries for transient live API failures."""
    last_error: Exception | None = None
    for attempt in range(SAFETY_SWEEP_ATTEMPTS):
        try:
            return await read_ids()
        except Exception as exc:
            last_error = exc
            if attempt < SAFETY_SWEEP_ATTEMPTS - 1:
                await asyncio.sleep(0.5 * (attempt + 1))

    print(f"⚠ Could not read {label} for integration safety sweep: {type(last_error).__name__}: {last_error}")
    return None


async def _safe_pending_order_ids(client: AsyncClient, account_id: str) -> set[str] | None:
    """Return pending order ids, or None when live API state cannot be read."""
    return await _read_account_ids("pending orders", lambda: _pending_order_ids(client, account_id))


async def _safe_open_trade_ids(client: AsyncClient, account_id: str) -> set[str] | None:
    """Return open trade ids, or None when live API state cannot be read."""
    return await _read_account_ids("open trades", lambda: _open_trade_ids(client, account_id))


async def _cleanup_pending_orders(client: AsyncClient, account_id: str, order_ids: set[str]) -> tuple[int, list[str]]:
    """Cancel pending orders and return cleanup count plus non-tolerated errors."""
    cleanup_count = 0
    cleanup_errors: list[str] = []
    for order_id in sorted(order_ids):
        try:
            order_response = await client.orders.get_order(account_id, order_id)
            if order_response and "order" in order_response and order_response["order"].get("state") == "PENDING":
                await client.orders.cancel_order(account_id, order_id)
                cleanup_count += 1
        except Exception as exc:
            if not is_tolerated_cleanup_error(exc):
                cleanup_errors.append(cleanup_error_message("order", order_id, exc))
    return cleanup_count, cleanup_errors


async def _cleanup_open_trades(client: AsyncClient, account_id: str, trade_ids: set[str]) -> tuple[int, list[str]]:
    """Close open trades and return cleanup count plus non-tolerated errors."""
    cleanup_count = 0
    cleanup_errors: list[str] = []
    for trade_id in sorted(trade_ids):
        try:
            close_response = await client.trades.close_trade(account_id=account_id, trade_specifier=trade_id)
            if close_response:
                cleanup_count += 1
        except Exception as exc:
            if not is_tolerated_cleanup_error(exc):
                cleanup_errors.append(cleanup_error_message("trade", trade_id, exc))
    return cleanup_count, cleanup_errors


async def _cleanup_new_account_state(client: AsyncClient, account_id: str, preflight_pending_orders: set[str], preflight_open_trades: set[str]) -> tuple[int, int, list[str], bool]:
    """Clean up account state created after preflight.

    Returns order count, trade count, cleanup errors, and whether the postflight
    sweep could be read. A failed sweep is treated as inconclusive instead of a
    teardown failure because the live API can drop connections after long tests.
    """
    postflight_pending_orders = await _safe_pending_order_ids(client, account_id)
    postflight_open_trades = await _safe_open_trade_ids(client, account_id)
    if postflight_pending_orders is None or postflight_open_trades is None:
        return 0, 0, [], False

    leaked_orders = postflight_pending_orders - preflight_pending_orders
    leaked_trades = postflight_open_trades - preflight_open_trades
    order_cleanup_count, order_cleanup_errors = await _cleanup_pending_orders(client, account_id, leaked_orders)
    trade_cleanup_count, trade_cleanup_errors = await _cleanup_open_trades(client, account_id, leaked_trades)
    cleanup_errors = [*order_cleanup_errors, *trade_cleanup_errors]

    return order_cleanup_count, trade_cleanup_count, cleanup_errors, True


def _client_request_id_factory(nodeid: str):
    """Create deterministic, short ClientRequestID values for a pytest node."""
    node_hash = hashlib.sha1(nodeid.encode("utf-8")).hexdigest()[:10]
    counter = 0

    def make_client_request_id(existing: str | None = None) -> str:
        nonlocal counter
        counter += 1
        suffix = re.sub(r"[^A-Za-z0-9_-]+", "-", existing or "request").strip("-")[:48]
        return f"{CLIENT_REQUEST_ID_PREFIX}-{node_hash}-{counter}-{suffix}"[:128]

    return make_client_request_id


@pytest.fixture
async def sandbox_client_no_cleanup(integration_config, test_account_id):
    """Async client configured for sandbox testing WITHOUT automatic cleanup."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")
    if not integration_config["account_id"]:
        pytest.skip("FIVETWENTY_OANDA_ACCOUNT environment variable not set")

    async with AsyncClient(token=integration_config["token"], account_id=integration_config["account_id"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
        preflight_pending_orders = await _safe_pending_order_ids(client, test_account_id)
        preflight_open_trades = await _safe_open_trade_ids(client, test_account_id)
        if preflight_pending_orders is None or preflight_open_trades is None:
            pytest.skip("Could not capture live account preflight state")
        yield client

        postflight_pending_orders = await _safe_pending_order_ids(client, test_account_id)
        postflight_open_trades = await _safe_open_trade_ids(client, test_account_id)
        if postflight_pending_orders is None or postflight_open_trades is None:
            print("⚠ Could not verify postflight live account state")
            return
        new_orders = postflight_pending_orders - preflight_pending_orders
        new_trades = postflight_open_trades - preflight_open_trades
        if new_orders or new_trades:
            pytest.fail(
                f"Live integration test left account state behind: pending_orders={sorted(new_orders)}, open_trades={sorted(new_trades)}",
                pytrace=False,
            )


@pytest.fixture
async def sandbox_client(integration_config, test_account_id, request: pytest.FixtureRequest):
    """Async client with automatic order and trade cleanup enabled by default."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")
    if not integration_config["account_id"]:
        pytest.skip("FIVETWENTY_OANDA_ACCOUNT environment variable not set")

    async with AsyncClient(token=integration_config["token"], account_id=integration_config["account_id"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
        created_order_ids: list[str] = []
        created_trade_ids: list[str] = []
        make_client_request_id = _client_request_id_factory(request.node.nodeid)
        preflight_pending_orders = await _safe_pending_order_ids(client, test_account_id)
        preflight_open_trades = await _safe_open_trade_ids(client, test_account_id)
        if preflight_pending_orders is None or preflight_open_trades is None:
            pytest.skip("Could not capture live account preflight state")

        # Store original methods
        original_post_limit_order = client.orders.post_limit_order
        original_post_stop_order = client.orders.post_stop_order
        original_post_market_order = client.orders.post_market_order
        original_post_market_if_touched_order = client.orders.post_market_if_touched_order
        original_post_order = client.orders.post_order

        async def track_order_creation(original_method, *args, **kwargs):
            """Wrapper to track order creation."""
            kwargs["client_request_id"] = make_client_request_id(kwargs.get("client_request_id"))
            response = await original_method(*args, **kwargs)
            if response and hasattr(response, "order_create_transaction") and response.order_create_transaction:
                order_id = response.order_create_transaction.get("id")
                if order_id:
                    created_order_ids.append(order_id)
            # Also track trades created from market orders
            if response and hasattr(response, "order_fill_transaction") and response.order_fill_transaction:
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
        cleanup_errors: list[str] = []

        tracked_order_cleanup_count, tracked_order_errors = await _cleanup_pending_orders(client, test_account_id, set(created_order_ids))
        tracked_trade_cleanup_count, tracked_trade_errors = await _cleanup_open_trades(client, test_account_id, set(created_trade_ids))
        order_cleanup_count += tracked_order_cleanup_count
        trade_cleanup_count += tracked_trade_cleanup_count
        cleanup_errors.extend(tracked_order_errors)
        cleanup_errors.extend(tracked_trade_errors)

        sweep_order_count, sweep_trade_count, sweep_errors, sweep_completed = await _cleanup_new_account_state(client, test_account_id, preflight_pending_orders, preflight_open_trades)
        order_cleanup_count += sweep_order_count
        trade_cleanup_count += sweep_trade_count
        cleanup_errors.extend(sweep_errors)

        if order_cleanup_count > 0 or trade_cleanup_count > 0:
            print(f"✓ Auto-cleaned up {order_cleanup_count} orders and {trade_cleanup_count} trades")

        if cleanup_errors:
            pytest.fail("Automatic integration cleanup failed:\n" + "\n".join(cleanup_errors), pytrace=False)

        if not sweep_completed:
            print("⚠ Could not verify postflight live account state after cleanup")
            return

        final_pending_orders = await _safe_pending_order_ids(client, test_account_id)
        final_open_trades = await _safe_open_trade_ids(client, test_account_id)
        if final_pending_orders is None or final_open_trades is None:
            print("⚠ Could not verify final live account state after cleanup")
            return
        leaked_orders = final_pending_orders - preflight_pending_orders
        leaked_trades = final_open_trades - preflight_open_trades
        if leaked_orders or leaked_trades:
            pytest.fail(
                f"Live integration test left account state behind after cleanup: pending_orders={sorted(leaked_orders)}, open_trades={sorted(leaked_trades)}",
                pytrace=False,
            )


# Alias for backward compatibility
sandbox_client_with_auto_cleanup = sandbox_client


@pytest.fixture
def sync_sandbox_client(integration_config):
    """Sync client configured for sandbox testing."""
    if not integration_config["token"]:
        pytest.skip("FIVETWENTY_OANDA_TOKEN environment variable not set")
    if not integration_config["account_id"]:
        pytest.skip("FIVETWENTY_OANDA_ACCOUNT environment variable not set")

    with Client(token=integration_config["token"], account_id=integration_config["account_id"], environment=integration_config["environment"], timeout=integration_config["timeout"], max_retries=integration_config["max_retries"]) as client:
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
        self.cleanup_errors: list[str] = []

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
            except Exception as exc:
                if not is_tolerated_cleanup_error(exc):
                    self.cleanup_errors.append(cleanup_error_message("order", order_id, exc))
                self.created_orders.remove(order_id)
        return cleanup_count

    async def cleanup_trades(self):
        """Clean up all tracked trades."""
        cleanup_count = 0
        for trade_id in self.created_trades[:]:  # Copy list to avoid modification during iteration
            try:
                # Try to close the trade
                close_response = await self.client.trades.close_trade(account_id=self.account_id, trade_specifier=trade_id)
                if close_response:
                    cleanup_count += 1
                self.created_trades.remove(trade_id)
            except Exception as exc:
                if not is_tolerated_cleanup_error(exc):
                    self.cleanup_errors.append(cleanup_error_message("trade", trade_id, exc))
                self.created_trades.remove(trade_id)
        return cleanup_count

    async def cleanup_all(self):
        """Clean up all tracked orders and trades."""
        orders_cleaned = await self.cleanup_orders()
        trades_cleaned = await self.cleanup_trades()
        return orders_cleaned, trades_cleaned, self.cleanup_errors


@pytest.fixture
async def cleanup_tracker(sandbox_client, test_account_id):
    """Fixture that provides automatic cleanup of orders and trades."""
    tracker = CleanupTracker(sandbox_client, test_account_id)

    yield tracker

    # Cleanup after test
    orders_cleaned, trades_cleaned, cleanup_errors = await tracker.cleanup_all()
    if orders_cleaned > 0 or trades_cleaned > 0:
        print(f"✓ Cleaned up {orders_cleaned} orders and {trades_cleaned} trades")
    if cleanup_errors:
        pytest.fail("Tracked integration cleanup failed:\n" + "\n".join(cleanup_errors), pytrace=False)


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
        if response and hasattr(response, "order_create_transaction") and response.order_create_transaction:
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
    cleanup_errors: list[str] = []
    for order_id in created_order_ids:
        try:
            order_response = await sandbox_client.orders.get_order(test_account_id, order_id)
            if order_response and "order" in order_response:
                order = order_response["order"]
                if order.get("state") == "PENDING":
                    await sandbox_client.orders.cancel_order(test_account_id, order_id)
                    cleanup_count += 1
        except Exception as exc:
            if not is_tolerated_cleanup_error(exc):
                cleanup_errors.append(cleanup_error_message("order", order_id, exc))

    if cleanup_count > 0:
        print(f"✓ Auto-cleaned up {cleanup_count} orders")
    if cleanup_errors:
        pytest.fail("Automatic order cleanup failed:\n" + "\n".join(cleanup_errors), pytrace=False)
