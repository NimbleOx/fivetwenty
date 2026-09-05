"""Tests for live integration safety helpers."""

from unittest.mock import AsyncMock, Mock

import pytest

from fivetwenty import FiveTwentyError
from tests.integration import conftest as fixtures
from tests.integration.helpers import cleanup_error_message, is_tolerated_cleanup_error


class _MissingResourceError(Exception):
    status = 404


async def test_cleanup_preserves_preexisting_resources_and_removes_only_new_state():
    client = Mock()
    client.orders.get_pending_orders = AsyncMock(return_value={"orders": [{"id": "old-order"}, {"id": "new-order"}]})
    client.trades.get_open_trades = AsyncMock(return_value={"trades": [{"id": "old-trade"}, {"id": "new-trade"}]})
    client.orders.get_order = AsyncMock(return_value={"order": {"id": "new-order", "state": "PENDING"}})
    client.orders.cancel_order = AsyncMock()
    client.trades.close_trade = AsyncMock(return_value={"lastTransactionID": "42"})
    result = await fixtures._cleanup_new_account_state(client, "offline", {"old-order"}, {"old-trade"})
    assert result == (1, 1, [], True)
    client.orders.cancel_order.assert_awaited_once_with("offline", "new-order")
    client.trades.close_trade.assert_awaited_once_with(account_id="offline", trade_specifier="new-trade")


async def test_cleanup_failure_is_reported_and_other_resources_are_still_attempted():
    client = Mock()
    client.trades.close_trade = AsyncMock(side_effect=[FiveTwentyError(status=500, message="unavailable"), {"lastTransactionID": "42"}])
    count, errors = await fixtures._cleanup_open_trades(client, "offline", {"a", "b"})
    assert count == 1
    assert len(errors) == 1
    assert "trade a" in errors[0]
    assert client.trades.close_trade.await_count == 2


async def test_trading_fixture_refuses_preexisting_exposure():
    client = Mock()
    client.orders.get_pending_orders = AsyncMock(return_value={"orders": []})
    client.trades.get_open_trades = AsyncMock(return_value={"trades": [{"id": "existing"}]})
    fixture = fixtures.trading_client.__wrapped__(client, "offline")
    with pytest.raises(pytest.skip.Exception, match="dedicated practice account"):
        await anext(fixture)


async def test_trading_fixture_fails_when_postflight_state_cannot_be_verified(monkeypatch):
    client = Mock()
    client.orders.get_pending_orders = AsyncMock(return_value={"orders": []})
    client.trades.get_open_trades = AsyncMock(return_value={"trades": []})
    monkeypatch.setattr(fixtures, "_cleanup_new_account_state", AsyncMock(return_value=(0, 0, [], False)))
    fixture = fixtures.trading_client.__wrapped__(client, "offline")
    assert await anext(fixture) is client
    with pytest.raises(pytest.fail.Exception, match="Could not verify"):
        await anext(fixture)


def test_cleanup_error_classification_and_message() -> None:
    exc = _MissingResourceError("missing")

    assert is_tolerated_cleanup_error(exc)
    assert cleanup_error_message("order", "123", exc) == "order 123: _MissingResourceError: missing"
