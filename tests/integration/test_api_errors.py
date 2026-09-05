"""Deterministic read-only server errors; transport failures are tested offline."""

import pytest

from fivetwenty import AsyncClient, FiveTwentyError

pytestmark = pytest.mark.integration


async def test_invalid_credentials_produce_an_authentication_error(test_account_id):
    async with AsyncClient(token="offline-invalid-token", account_id=test_account_id, max_retries=0) as client:
        with pytest.raises(FiveTwentyError) as caught:
            await client.accounts.get_accounts()
    assert caught.value.status == 401
    assert caught.value.is_authentication_error
    assert not caught.value.retryable


async def test_missing_transaction_produces_a_not_found_error(sandbox_client, test_account_id):
    account = await sandbox_client.accounts.get_account_summary(test_account_id)
    absent_id = str(int(account["lastTransactionID"]) + 1000000)
    with pytest.raises(FiveTwentyError) as caught:
        await sandbox_client.transactions.get_transaction(test_account_id, absent_id)
    assert caught.value.status == 404
    assert caught.value.is_not_found
    assert caught.value.message
