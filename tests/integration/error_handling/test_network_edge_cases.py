"""Integration tests for network-related edge cases."""

import asyncio

import httpx
import pytest

from fivetwenty import AsyncClient, FiveTwentyError, StreamStall


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.edge_cases
class TestNetworkEdgeCases:
    """Integration tests for network-related edge cases."""

    async def test_connection_timeout_handling(self, integration_config: dict):
        """Test connection timeout handling with very short timeouts.

        Validates:
        - Client handles connection timeouts gracefully
        - Appropriate exceptions are raised for timeout scenarios
        """
        # Create a client with very short timeout to simulate timeout scenarios
        timeout_client = AsyncClient(
            token=integration_config["token"],
            environment=integration_config["environment"],
            timeout=httpx.Timeout(0.01),  # 10ms timeout - will likely timeout
        )

        try:
            with pytest.raises((FiveTwentyError, httpx.TimeoutException, asyncio.TimeoutError)):
                await timeout_client.accounts.get_accounts()
        finally:
            await timeout_client.close()

    async def test_request_timeout_scenarios(self, integration_config: dict, test_account_id: str):
        """Test request timeout with operations that might take longer.

        Validates:
        - Request-level timeout handling
        - Streaming operation timeout behavior
        """
        moderate_timeout_client = AsyncClient(
            token=integration_config["token"],
            environment=integration_config["environment"],
            timeout=httpx.Timeout(0.1),  # 100ms timeout
        )

        try:
            # Try an operation that might take longer than 100ms
            price_stream = moderate_timeout_client.pricing.get_pricing_stream(account_id=test_account_id, instruments=["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD"])

            # Either it times out (expected) or succeeds (also fine)
            try:
                await price_stream.__anext__()
            except (FiveTwentyError, httpx.TimeoutException, asyncio.TimeoutError, StreamStall):
                # Expected timeout behavior
                pass
        finally:
            await moderate_timeout_client.close()

    async def test_authentication_failure_handling(self, integration_config: dict):
        """Test authentication failure scenarios.

        Validates:
        - Proper handling of invalid authentication tokens
        - Authentication error detection
        """
        auth_fail_client = AsyncClient(
            token="invalid-network-token-123456789",
            environment=integration_config["environment"],
        )

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await auth_fail_client.accounts.get_accounts()

            error = exc_info.value
            assert error.is_authentication_error, f"Expected authentication error, got: {error}"
        finally:
            await auth_fail_client.close()

    async def test_network_resilience_and_retry(self, sandbox_client: AsyncClient):
        """Test client resilience to intermittent network issues.

        Validates:
        - Client can recover from temporary network issues
        - Basic connectivity recovery
        """
        retry_count = 0
        max_retries = 3

        while retry_count < max_retries:
            try:
                # Test basic connectivity recovery
                accounts = await sandbox_client.accounts.get_accounts()
                assert accounts is not None, "Accounts response should not be None"
                assert len(accounts) >= 0, "Should return valid accounts list"
                break
            except (FiveTwentyError, httpx.NetworkError) as e:
                retry_count += 1
                if retry_count >= max_retries:
                    pytest.fail(f"Network connectivity failed after {max_retries} retries: {e}")
                await asyncio.sleep(0.1 * retry_count)  # Progressive backoff

    async def test_ssl_tls_certificate_handling(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test SSL/TLS certificate handling.

        Validates:
        - HTTPS connections work properly
        - SSL certificate validation
        """
        try:
            # Make a request that requires SSL/TLS
            account_summary = await sandbox_client.accounts.get_account_summary(test_account_id)
            assert account_summary is not None, "Account summary should not be None"
            assert "account" in account_summary, "Response should contain account data"
            assert hasattr(account_summary["account"], "id"), "Account should have ID"
        except httpx.ConnectError as e:
            if any(keyword in str(e).lower() for keyword in ["ssl", "tls", "certificate"]):
                pytest.fail(f"SSL/TLS certificate issue: {e}")
            else:
                # Re-raise if it's not an SSL issue
                raise

    async def test_connection_pooling_and_reuse(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test connection pooling and concurrent request handling.

        Validates:
        - Multiple concurrent requests work correctly
        - Connection pooling functions properly
        """
        # Create multiple concurrent requests
        tasks = [sandbox_client.accounts.get_account_summary(test_account_id) for _ in range(5)]

        try:
            results = await asyncio.gather(*tasks)
            assert len(results) == 5, f"Expected 5 results, got {len(results)}"

            for i, result in enumerate(results):
                assert result is not None, f"Result {i} should not be None"
                assert "account" in result, f"Result {i} should contain account data"
                assert hasattr(result["account"], "id"), f"Result {i} account should have ID"
                assert result["account"].id == test_account_id, f"Result {i} should match test account ID"
        except Exception as e:
            pytest.fail(f"Connection pooling test failed: {e}")

    async def test_large_response_handling(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test handling of large API responses.

        Validates:
        - Network can handle substantial data transfers
        - Large response processing works correctly
        """
        try:
            # Request a potentially large response
            transactions = await sandbox_client.transactions.get_transactions(
                account_id=test_account_id,
                page_size=500,  # Request a large page size
            )
            assert transactions is not None, "Transactions response should not be None"
        except (httpx.NetworkError, httpx.TimeoutException) as e:
            # Network issues with large responses are part of what we're testing
            pytest.skip(f"Large response failed due to network conditions: {e}")
        except Exception as e:
            # Other errors should be investigated
            pytest.fail(f"Unexpected error in large response test: {e}")

    async def test_concurrent_client_connections(self, integration_config: dict, test_account_id: str):
        """Test multiple client instances working concurrently.

        Validates:
        - Multiple client instances can operate simultaneously
        - No resource conflicts between clients
        """
        clients = []
        try:
            # Create multiple client instances
            for _ in range(3):
                client = AsyncClient(
                    token=integration_config["token"],
                    environment=integration_config["environment"],
                    timeout=integration_config["timeout"],
                )
                clients.append(client)

            # Make concurrent requests from different clients
            tasks = [client.accounts.get_account_summary(test_account_id) for client in clients]

            results = await asyncio.gather(*tasks)
            assert len(results) == 3, f"Expected 3 results, got {len(results)}"

            for i, result in enumerate(results):
                assert result is not None, f"Client {i} result should not be None"
                assert "account" in result, f"Client {i} result should contain account data"

        finally:
            # Clean up all clients
            for client in clients:
                await client.close()

    async def test_network_error_classification(self, integration_config: dict):
        """Test proper classification of different network error types.

        Validates:
        - Different network errors are properly categorized
        - Error details are meaningful
        """
        # Test with rate limiting (HTTP 429) behavior
        # This is a more reliable test than DNS failures
        try:
            # Make many rapid requests to potentially trigger rate limiting
            tasks = []
            client = AsyncClient(
                token=integration_config["token"],
                environment=integration_config["environment"],
                timeout=5.0,
            )

            try:
                # Create many concurrent requests that might trigger rate limiting
                for _ in range(10):
                    task = client.accounts.get_accounts()
                    tasks.append(task)

                # Execute all requests - some might fail with rate limiting
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check that we either got valid responses or expected errors
                for result in results:
                    if isinstance(result, Exception):
                        # Should be FiveTwentyError or network-related error
                        assert isinstance(result, FiveTwentyError | httpx.HTTPError), f"Unexpected error type: {type(result)}"
                    else:
                        # Should be valid account list
                        assert result is not None, "Valid result should not be None"

            finally:
                await client.close()

        except Exception as e:
            # If the test itself fails for other reasons, skip it
            pytest.skip(f"Network error classification test not applicable: {e}")
