"""Practice-account fixtures with explicit trading isolation and verified cleanup."""

import asyncio
import os
from typing import Any

import pytest

from fivetwenty import AsyncClient, Environment
from tests.integration.helpers import cleanup_error_message, is_tolerated_cleanup_error

SAFETY_SWEEP_ATTEMPTS = 3


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
    orders = response["orders"]
    return {order_id for order in orders if (order_id := _resource_id(order))}


async def _open_trade_ids(client: AsyncClient, account_id: str) -> set[str]:
    """Return currently open trade ids for safety checks."""
    response = await client.trades.get_open_trades(account_id)
    trades = response["trades"]
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
    sweep could be read. The fixture fails teardown if the sweep is inconclusive.
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


@pytest.fixture(scope="session")
def integration_config():
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    account = os.getenv("FIVETWENTY_OANDA_ACCOUNT")
    if not token or not account:
        pytest.skip("Set practice FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT")
    return {"token": token, "account_id": account, "environment": Environment.PRACTICE, "max_retries": 0}


@pytest.fixture
def test_account_id(integration_config):
    return integration_config["account_id"]


@pytest.fixture
async def sandbox_client(integration_config):
    async with AsyncClient(**integration_config) as client:
        yield client


@pytest.fixture
async def trading_client(sandbox_client, test_account_id):
    """Use an empty, dedicated practice account and verify cleanup even on failure."""
    pending = await _pending_order_ids(sandbox_client, test_account_id)
    trades = await _open_trade_ids(sandbox_client, test_account_id)
    if pending or trades:
        pytest.skip("Trading tests require a dedicated practice account with no pending orders or open trades")
    try:
        yield sandbox_client
    finally:
        _, _, errors, completed = await _cleanup_new_account_state(sandbox_client, test_account_id, pending, trades)
        if not completed:
            pytest.fail("Could not verify practice-account state during cleanup", pytrace=False)
        remaining_orders = await _pending_order_ids(sandbox_client, test_account_id)
        remaining_trades = await _open_trade_ids(sandbox_client, test_account_id)
        if errors or remaining_orders or remaining_trades:
            pytest.fail(f"Practice cleanup failed: {errors}; pending={sorted(remaining_orders)}; trades={sorted(remaining_trades)}", pytrace=False)
