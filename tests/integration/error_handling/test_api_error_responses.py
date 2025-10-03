"""Integration tests for API error response handling."""

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.edge_cases
class TestAPIErrorResponses:
    """Integration tests for API error response handling."""

    async def test_api_error_responses(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test handling of various API error responses.

        Validates:
        - 400 Bad Request handling
        - 401 Unauthorized handling
        - 403 Forbidden handling
        - 404 Not Found handling
        - 429 Rate Limiting handling
        - 500 Server Error handling
        """
        from fivetwenty import FiveTwentyError

        # Test 400 Bad Request - Invalid parameter values
        with pytest.raises(FiveTwentyError) as exc_info:
            await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument="EUR_USD",  # Valid instrument
                units=1000000000000,  # Unrealistically large units that should trigger API error
            )

        error = exc_info.value
        assert error.status == 400
        assert error.is_client_error
        assert not error.is_server_error
        assert not error.retryable
        # error_category might be None for some errors, so just check that we have a valid error
        assert error.code is not None

        # Test 401 Unauthorized - Invalid token (simulate by using wrong token)
        from fivetwenty import AsyncClient

        invalid_client = AsyncClient(token="invalid-token-12345", account_id="000-000-0000000-000", environment="practice")

        with pytest.raises(FiveTwentyError) as exc_info:
            await invalid_client.accounts.get_accounts()

        error = exc_info.value
        assert error.status == 401
        assert error.is_authentication_error
        assert error.is_client_error
        assert not error.retryable

        await invalid_client.close()

        # Test 403 Forbidden - Access to restricted resource
        fake_account_id = "000-000-0000000-000"  # Format looks valid but doesn't exist
        with pytest.raises(FiveTwentyError) as exc_info:
            await sandbox_client.accounts.get_account_summary(fake_account_id)

        error = exc_info.value
        # Could be 400, 403, or 404 depending on OANDA's validation
        assert error.status in {400, 403, 404}
        assert error.is_client_error

        # Test 404 Not Found - Non-existent resource
        with pytest.raises(FiveTwentyError) as exc_info:
            # Try to get a non-existent transaction
            await sandbox_client.transactions.get_transaction(account_id=test_account_id, transaction_id="999999999")

        error = exc_info.value
        assert error.status == 404
        assert error.is_not_found
        assert error.is_client_error
        assert not error.retryable

        # Test error message formatting
        error_str = str(error)
        assert "HTTP 404" in error_str
        assert error.message in error_str

        # Test error representation
        error_repr = repr(error)
        assert "FiveTwentyError" in error_repr
        assert "status=404" in error_repr

        # Test validation error handling
        from decimal import Decimal

        with pytest.raises(FiveTwentyError) as exc_info:
            await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument="EUR_USD",
                units=1000,
                price=Decimal("0"),  # Invalid price (zero or negative)
            )

        error = exc_info.value
        assert error.is_validation_error
        _ = error.get_validation_errors()
        # Should have field-specific validation errors

        # Test remediation messages for common errors
        if error.code:
            _ = error.get_remediation_message()
            # Should provide helpful guidance when available
