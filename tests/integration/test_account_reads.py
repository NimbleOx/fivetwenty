"""Read-only checks of actual account envelopes and public model values."""

import asyncio
from datetime import datetime
from decimal import Decimal

import pytest

from fivetwenty import Client
from fivetwenty.models import AccountChangesState

pytestmark = pytest.mark.integration


async def test_account_discovery_and_details(sandbox_client, test_account_id):
    accounts = await sandbox_client.accounts.get_accounts()
    assert test_account_id in {account.id for account in accounts}
    response = await sandbox_client.accounts.get_account(test_account_id)
    account = response["account"]
    assert account.id == test_account_id
    assert isinstance(account.balance, Decimal)
    assert isinstance(account.created_time, datetime)
    assert int(response["lastTransactionID"]) > 0


async def test_concurrent_summaries_preserve_account_identity(sandbox_client, test_account_id):
    results = await asyncio.gather(*(sandbox_client.accounts.get_account_summary(test_account_id) for _ in range(3)))
    assert len(results) == 3
    assert all(result["account"].id == test_account_id for result in results)
    assert all(isinstance(result["account"].nav, Decimal) for result in results)


async def test_instrument_filter_returns_requested_instrument(sandbox_client, test_account_id):
    result = await sandbox_client.accounts.get_account_instruments(test_account_id, instruments=["EUR_USD"])
    assert [instrument.name for instrument in result["instruments"]] == ["EUR_USD"]
    assert result["instruments"][0].minimum_trade_size > 0


@pytest.mark.parametrize(("endpoint", "method", "key"), [("orders", "get_orders", "orders"), ("orders", "get_pending_orders", "orders"), ("trades", "get_trades", "trades"), ("trades", "get_open_trades", "trades"), ("positions", "get_positions", "positions"), ("positions", "get_open_positions", "positions")])
async def test_collection_envelopes(sandbox_client, test_account_id, endpoint, method, key):
    result = await getattr(getattr(sandbox_client, endpoint), method)(test_account_id)
    assert isinstance(result[key], list)
    assert int(result["lastTransactionID"]) > 0
    if method == "get_pending_orders":
        assert all(order.state == "PENDING" for order in result[key])
    if method == "get_open_trades":
        assert all(trade.state == "OPEN" for trade in result[key])


async def test_incremental_account_changes(sandbox_client, test_account_id):
    before = await sandbox_client.accounts.get_account_summary(test_account_id)
    result = await sandbox_client.accounts.get_account_changes(test_account_id, since_transaction_id=before["lastTransactionID"])
    assert int(result["lastTransactionID"]) >= int(before["lastTransactionID"])
    assert result["changes"] is not None
    assert isinstance(result["state"], AccountChangesState)


def test_sync_client_returns_the_same_account_contract(integration_config, test_account_id):
    with Client(**integration_config) as client:
        result = client.accounts.get_account_summary(test_account_id)
        assert result["account"].id == test_account_id
        assert isinstance(result["account"].balance, Decimal)
