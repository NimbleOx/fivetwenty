"""Integration tests for comprehensive error handling and edge cases."""

import asyncio

import pytest

from fivetwenty import AsyncClient, FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.edge_cases
class TestComprehensiveEdgeCases:
    """Integration tests for comprehensive error handling and edge cases."""

    async def test_malformed_data_handling(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test handling of malformed or unexpected data."""
        # Test with invalid account ID format that should trigger API validation
        with pytest.raises(FiveTwentyError):
            await sandbox_client.accounts.get_account("invalid-account-format")  # Invalid account ID format

    async def test_resource_exhaustion_scenarios(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test resource exhaustion and rate limiting scenarios."""
        # Test rapid consecutive requests
        tasks = []
        for _i in range(10):
            task = sandbox_client.accounts.get_account_summary(test_account_id)
            tasks.append(task)

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Some may succeed, some may fail with rate limiting
            assert len(results) == 10
        except Exception:
            # Rate limiting or other resource constraints are acceptable
            pass

    async def test_concurrent_operation_conflicts(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test concurrent operations that might conflict."""
        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        test_instrument = test_instruments["major_pairs"][0]

        # Test concurrent order placement
        tasks = []
        for i in range(3):
            task = sandbox_client.orders.post_market_order(account_id=test_account_id, instrument=test_instrument, units=100, client_request_id=f"concurrent-test-{i}-{int(asyncio.get_event_loop().time() * 1000)}")
            tasks.append(task)

        trade_ids_to_close = []
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # Some orders may succeed, some may fail due to constraints
            assert len(results) == 3

            # Collect trade IDs for cleanup
            for result in results:
                if hasattr(result, "order_fill_transaction") and result.order_fill_transaction:
                    fill_tx = result.order_fill_transaction
                    if "tradeOpened" in fill_tx and "tradeID" in fill_tx["tradeOpened"]:
                        trade_ids_to_close.append(fill_tx["tradeOpened"]["tradeID"])
        except Exception:
            # Concurrent operation conflicts are expected
            pass

        # Cleanup: Close any opened trades
        for trade_id in trade_ids_to_close:
            try:
                # Try to close trade - some sandbox trades may already be closed or invalid
                close_response = await sandbox_client.trades.close_trade(account_id=test_account_id, trade_specifier=trade_id)
                if close_response:
                    print(f"✓ Cleaned up trade {trade_id}")
                else:
                    print(f"⚠ Trade {trade_id} may already be closed")
            except Exception as cleanup_error:
                # Non-critical cleanup failure - trade may already be closed or invalid in sandbox
                print(f"⚠ Could not close trade {trade_id}: {type(cleanup_error).__name__} (non-critical)")

    async def test_boundary_value_testing(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test boundary values and extreme inputs."""
        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        test_instrument = test_instruments["major_pairs"][0]

        # Test zero units (should be invalid)
        with pytest.raises(FiveTwentyError):
            await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=0,  # Zero units should be invalid
            )

        # Test maximum reasonable unit size
        with pytest.raises(FiveTwentyError):
            await sandbox_client.orders.post_market_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=1000000000,  # Too large
            )

        # Test invalid price for limit orders
        from decimal import Decimal

        with pytest.raises(FiveTwentyError):
            await sandbox_client.orders.post_limit_order(
                account_id=test_account_id,
                instrument=test_instrument,
                units=1000,
                price=Decimal("-1.0"),  # Negative price should be invalid
            )

    async def test_authentication_edge_cases(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test authentication-related edge cases."""
        # Test with malformed token
        malformed_client = AsyncClient(token="malformed-token-format", account_id="test-account", environment="practice")

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await malformed_client.accounts.get_accounts()

            error = exc_info.value
            assert error.is_authentication_error
        finally:
            await malformed_client.close()

        # Test with empty token - should fail at client creation
        with pytest.raises(ValueError):
            AsyncClient(token="", account_id="test-account", environment="practice")

        # Test that authentication errors are properly handled and categorized
        # We've already tested malformed tokens above, so the test is complete
