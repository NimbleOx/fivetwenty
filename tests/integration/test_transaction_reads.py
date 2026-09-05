"""Transaction pagination and filtering with assertions on parsed model objects."""

from datetime import datetime, timedelta, timezone

import pytest

from fivetwenty.models import Transaction

pytestmark = pytest.mark.integration


async def test_transaction_pages_describe_a_bounded_time_range(sandbox_client, test_account_id):
    end = datetime.now(timezone.utc)
    result = await sandbox_client.transactions.get_transactions(test_account_id, from_time=end - timedelta(days=1), to_time=end, page_size=10)
    assert result["pageSize"] == 10
    assert isinstance(result["count"], int)
    assert result["count"] >= 0
    assert isinstance(result["pages"], list)
    assert all("/transactions/idrange?" in page for page in result["pages"])
    assert int(result["lastTransactionID"]) > 0


async def test_transaction_range_matches_direct_lookup(sandbox_client, test_account_id):
    account = await sandbox_client.accounts.get_account_summary(test_account_id)
    latest = account["lastTransactionID"]
    direct = await sandbox_client.transactions.get_transaction(test_account_id, latest)
    ranged = await sandbox_client.transactions.get_transactions_range(test_account_id, from_transaction_id=latest, to_transaction_id=latest)
    assert isinstance(direct["transaction"], Transaction)
    assert direct["transaction"].id == latest
    assert ranged["transactions"] == [direct["transaction"]]
    assert isinstance(direct["transaction"].time, datetime)


@pytest.mark.parametrize("filters", [None, ["ORDER_FILL"]])
async def test_since_id_respects_cursor_and_filter(sandbox_client, test_account_id, filters):
    account = await sandbox_client.accounts.get_account_summary(test_account_id)
    cursor = max(1, int(account["lastTransactionID"]) - 10)
    result = await sandbox_client.transactions.get_transactions_since_id(test_account_id, str(cursor), transaction_type=filters)
    ids = [int(transaction.id) for transaction in result["transactions"]]
    assert ids == sorted(ids)
    assert all(value > cursor for value in ids)
    assert int(result["lastTransactionID"]) >= cursor
    if filters:
        assert all(transaction.type == "ORDER_FILL" for transaction in result["transactions"])


async def test_recent_transactions_have_unique_ordered_ids(sandbox_client, test_account_id):
    result = await sandbox_client.transactions.get_recent_transactions(test_account_id, count=10)
    ids = [int(transaction.id) for transaction in result["transactions"]]
    assert ids, "An existing account has at least its creation transaction"
    assert ids == sorted(set(ids))
    assert ids[-1] <= int(result["lastTransactionID"])
