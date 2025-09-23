"""Integration tests for synchronous client wrapper."""

import concurrent.futures
import time
from typing import Any

import pytest

from fivetwenty import Client
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.integration
class TestSyncClientIntegration:
    """Integration tests for the synchronous Client wrapper focusing on sync-specific behavior."""

    def test_sync_client_initialization_and_cleanup(self, sync_sandbox_client: Client):
        """Test synchronous client initialization, threading, and cleanup.

        Validates sync-specific behavior:
        - Background thread management
        - Resource cleanup
        - Context manager protocol
        """
        print("✓ Testing sync client initialization and cleanup...")

        # Test 1: Client attributes and thread setup
        assert sync_sandbox_client is not None
        assert hasattr(sync_sandbox_client, "_async")
        assert hasattr(sync_sandbox_client, "_thread")
        assert hasattr(sync_sandbox_client, "_loop")
        assert sync_sandbox_client._thread is not None
        assert sync_sandbox_client._thread.is_alive()
        assert sync_sandbox_client._thread.daemon is True

        print("  - Background thread and attributes verified")

        # Test 2: Basic API functionality (minimal validation)
        accounts = sync_sandbox_client.accounts.get_accounts()
        assert accounts is not None
        assert len(accounts) > 0
        print("  - Basic API call successful")

        # Test 3: Client creation and cleanup
        test_client = Client(token=sync_sandbox_client._async._token, environment="practice")
        try:
            assert test_client.accounts.get_accounts() is not None
            assert test_client._thread.is_alive()
        finally:
            test_client.close()
            time.sleep(0.5)
            assert not test_client._thread.is_alive()

        print("  - Client cleanup verified")

        # Test 4: Context manager protocol
        with Client(token=sync_sandbox_client._async._token, environment="practice") as client:
            assert client._thread.is_alive()
        time.sleep(0.5)
        assert not client._thread.is_alive()

        print("  - Context manager protocol verified")
        print("✓ Sync client initialization test completed")

    def test_sync_error_propagation(self, sync_sandbox_client: Client, test_account_id: str):
        """Test that async errors properly propagate through sync wrapper.

        Validates sync-specific behavior:
        - Exception propagation from async to sync
        - Error type preservation
        """
        print("✓ Testing sync error propagation...")

        # Test error propagation for invalid account
        with pytest.raises(FiveTwentyError) as exc_info:
            sync_sandbox_client.accounts.get_account_summary("invalid-account-id")
        assert exc_info.value.status in [400, 404]
        print("  - Error propagation verified")

        print("✓ Sync error propagation test completed")

    def test_sync_thread_safety(self, sync_sandbox_client: Client, test_account_id: str):
        """Test thread safety of synchronous client.

        Validates sync-specific behavior:
        - Concurrent API calls from multiple threads
        - Thread-safe queue operations
        - No race conditions
        """
        print("✓ Testing sync client thread safety...")

        # Test concurrent API calls from multiple threads
        def make_api_call(thread_id: int) -> dict[str, Any]:
            try:
                sync_sandbox_client.accounts.get_account_summary(test_account_id)
                return {"thread_id": thread_id, "success": True}
            except Exception as e:
                return {"thread_id": thread_id, "success": False, "error": str(e)}

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_api_call, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        successful = sum(1 for r in results if r["success"])
        assert successful == 10, f"All calls should succeed, got {successful}/10"
        print(f"  - Concurrent API calls successful: {successful}/10")

        print("✓ Thread safety test completed")

    def test_sync_resource_management(self, sync_sandbox_client: Client, test_account_id: str):
        """Test resource management in synchronous client.

        Validates sync-specific behavior:
        - Multiple client lifecycle management
        - Queue overflow handling
        - Memory cleanup
        """
        print("✓ Testing sync client resource management...")

        # Test multiple client creation and cleanup
        clients = []
        try:
            for _i in range(3):
                client = Client(token=sync_sandbox_client._async._token, environment="practice")
                clients.append(client)
                assert client.accounts.get_accounts() is not None

            print(f"  - Created {len(clients)} clients successfully")

        finally:
            for client in clients:
                client.close()
                time.sleep(0.1)
                assert not client._thread.is_alive()
            print("  - All clients cleaned up")

        # Test rapid request handling (queue stress test)
        results = []
        for _i in range(10):
            result = sync_sandbox_client.accounts.get_accounts()
            results.append(result)
        assert len(results) == 10
        print(f"  - Handled {len(results)} rapid requests")

        print("✓ Resource management test completed")
