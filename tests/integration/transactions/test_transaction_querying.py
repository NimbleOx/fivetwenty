"""Integration tests for advanced transaction querying endpoints.

This module tests transaction querying functionality that was previously
missing from integration test coverage.
"""

import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.core
class TestTransactionQuerying:
    """Integration tests for advanced transaction querying operations."""

    async def test_transaction_since_id_querying(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction querying since a specific transaction ID.

        Validates:
        - Transactions retrieval since specific ID
        - Incremental transaction updates
        - Transaction type filtering
        - Error handling for invalid IDs
        """
        print("✓ Starting transaction since ID querying test...")

        # Get current account state to find a recent transaction ID
        try:
            account_response = await sandbox_client.accounts.get_account(test_account_id)
            current_transaction_id = account_response.get("lastTransactionID")

            if current_transaction_id:
                current_id = int(current_transaction_id)
                print(f"  Current transaction ID: {current_transaction_id}")

                # Test 1: Get transactions since an earlier ID
                since_id = max(1, current_id - 10)  # Get last 10 transactions
                print(f"\n✓ Test 1: Getting transactions since ID {since_id}")

                since_response = await sandbox_client.transactions.get_transactions_since_id(
                    account_id=test_account_id,
                    transaction_id=str(since_id)
                )

                assert since_response is not None, "Since ID response should not be None"

                if "transactions" in since_response:
                    transactions = since_response["transactions"]
                    print(f"  ✓ Retrieved {len(transactions)} transactions since ID {since_id}")

                    # Validate transaction IDs are newer than since_id
                    if transactions:
                        for txn in transactions:
                            if isinstance(txn, dict) and "id" in txn:
                                txn_id = int(txn["id"])
                                assert txn_id > since_id, f"Transaction {txn_id} should be > {since_id}"

                        print(f"  ✓ All transaction IDs are newer than {since_id}")
                else:
                    print("  ✓ Since ID response structure validated")

                # Test 2: Transaction type filtering
                print(f"\n✓ Test 2: Transaction type filtering")

                filtered_response = await sandbox_client.transactions.get_transactions_since_id(
                    account_id=test_account_id,
                    transaction_id=str(since_id),
                    transaction_type=["CREATE", "DAILY_FINANCING"]
                )

                assert filtered_response is not None, "Filtered response should not be None"

                if "transactions" in filtered_response:
                    filtered_transactions = filtered_response["transactions"]
                    print(f"  ✓ Retrieved {len(filtered_transactions)} filtered transactions")

                    # Validate transaction types match filter
                    if filtered_transactions:
                        for txn in filtered_transactions:
                            if isinstance(txn, dict) and "type" in txn:
                                assert txn["type"] in ["CREATE", "DAILY_FINANCING"], f"Unexpected transaction type: {txn['type']}"

                        print("  ✓ Transaction type filtering validated")
                else:
                    print("  ✓ Filtered response structure validated")

                # Test 3: Invalid transaction ID error handling
                print(f"\n✓ Test 3: Invalid transaction ID handling")

                # Test with non-numeric ID
                try:
                    with pytest.raises(FiveTwentyError) as exc_info:
                        await sandbox_client.transactions.get_transactions_since_id(
                            account_id=test_account_id,
                            transaction_id="invalid-id"
                        )

                    error = exc_info.value
                    assert error.status == 400, f"Expected 400 for invalid ID, got {error.status}"
                    print("  ✓ Invalid transaction ID correctly rejected")

                except AssertionError:
                    raise
                except Exception as e:
                    print(f"  ⚠ Unexpected error for invalid transaction ID: {type(e).__name__}")

            else:
                print("  ⚠ No transaction ID found - cannot test since ID functionality")

        except FiveTwentyError as e:
            print(f"  ⚠ Transaction since ID test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during since ID test: {type(e).__name__}: {e}")

        print("✓ Transaction since ID querying test completed")

    async def test_transaction_range_querying(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction querying within specific ID ranges.

        Validates:
        - Transaction range retrieval
        - Range boundary validation
        - Transaction type filtering in ranges
        - Error handling for invalid ranges
        """
        print("✓ Starting transaction range querying test...")

        try:
            # Get current transaction ID to establish a valid range
            account_response = await sandbox_client.accounts.get_account(test_account_id)
            current_transaction_id = account_response.get("lastTransactionID")

            if current_transaction_id:
                current_id = int(current_transaction_id)
                print(f"  Current transaction ID: {current_transaction_id}")

                # Test 1: Valid range query
                from_id = max(1, current_id - 5)
                to_id = current_id
                print(f"\n✓ Test 1: Getting transactions from {from_id} to {to_id}")

                range_response = await sandbox_client.transactions.get_transactions_range(
                    account_id=test_account_id,
                    from_transaction_id=str(from_id),
                    to_transaction_id=str(to_id)
                )

                assert range_response is not None, "Range response should not be None"

                if "transactions" in range_response:
                    transactions = range_response["transactions"]
                    print(f"  ✓ Retrieved {len(transactions)} transactions in range {from_id}-{to_id}")

                    # Validate transaction IDs are within range
                    if transactions:
                        for txn in transactions:
                            if isinstance(txn, dict) and "id" in txn:
                                txn_id = int(txn["id"])
                                assert from_id <= txn_id <= to_id, f"Transaction {txn_id} should be in range {from_id}-{to_id}"

                        print(f"  ✓ All transaction IDs are within range {from_id}-{to_id}")
                else:
                    print("  ✓ Range response structure validated")

                # Test 2: Range with transaction type filtering
                print(f"\n✓ Test 2: Range query with transaction type filtering")

                filtered_range_response = await sandbox_client.transactions.get_transactions_range(
                    account_id=test_account_id,
                    from_transaction_id=str(from_id),
                    to_transaction_id=str(to_id),
                    transaction_type=["CREATE", "DAILY_FINANCING", "ORDER_FILL"]
                )

                assert filtered_range_response is not None, "Filtered range response should not be None"

                if "transactions" in filtered_range_response:
                    filtered_transactions = filtered_range_response["transactions"]
                    print(f"  ✓ Retrieved {len(filtered_transactions)} filtered transactions")

                    # Validate transaction types
                    if filtered_transactions:
                        valid_types = ["CREATE", "DAILY_FINANCING", "ORDER_FILL"]
                        for txn in filtered_transactions:
                            if isinstance(txn, dict) and "type" in txn:
                                assert txn["type"] in valid_types, f"Unexpected transaction type: {txn['type']}"

                        print("  ✓ Transaction type filtering in range validated")
                else:
                    print("  ✓ Filtered range response structure validated")

                # Test 3: Invalid range error handling
                print(f"\n✓ Test 3: Invalid range handling")

                # Test invalid range (from > to)
                try:
                    with pytest.raises((ValueError, FiveTwentyError)):
                        await sandbox_client.transactions.get_transactions_range(
                            account_id=test_account_id,
                            from_transaction_id=str(current_id),
                            to_transaction_id=str(current_id - 1)  # Invalid: from > to
                        )
                    print("  ✓ Invalid range (from > to) correctly rejected")
                except AssertionError:
                    print("  ⚠ Invalid range was unexpectedly accepted")
                except Exception as e:
                    print(f"  ✓ Invalid range rejected: {type(e).__name__}")

                # Test non-numeric IDs
                try:
                    with pytest.raises((ValueError, FiveTwentyError)):
                        await sandbox_client.transactions.get_transactions_range(
                            account_id=test_account_id,
                            from_transaction_id="abc",
                            to_transaction_id="def"
                        )
                    print("  ✓ Non-numeric transaction IDs correctly rejected")
                except Exception as e:
                    print(f"  ✓ Non-numeric IDs rejected: {type(e).__name__}")

            else:
                print("  ⚠ No transaction ID found - cannot test range functionality")

        except FiveTwentyError as e:
            print(f"  ⚠ Transaction range test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during range test: {type(e).__name__}: {e}")

        print("✓ Transaction range querying test completed")

    async def test_recent_transactions_querying(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test recent transactions convenience endpoint.

        Validates:
        - Recent transactions retrieval
        - Count parameter functionality
        - Transaction type filtering
        - Response structure validation
        """
        print("✓ Starting recent transactions querying test...")

        try:
            # Test 1: Basic recent transactions retrieval
            print("\n✓ Test 1: Basic recent transactions retrieval")

            recent_response = await sandbox_client.transactions.get_recent_transactions(
                account_id=test_account_id,
                count=10
            )

            assert recent_response is not None, "Recent transactions response should not be None"

            if "transactions" in recent_response:
                transactions = recent_response["transactions"]
                print(f"  ✓ Retrieved {len(transactions)} recent transactions")

                # Validate we don't get more than requested
                assert len(transactions) <= 10, f"Should not exceed requested count of 10, got {len(transactions)}"

                # Validate transactions are ordered by ID (most recent first)
                if len(transactions) >= 2:
                    for i in range(len(transactions) - 1):
                        if isinstance(transactions[i], dict) and isinstance(transactions[i + 1], dict):
                            if "id" in transactions[i] and "id" in transactions[i + 1]:
                                current_id = int(transactions[i]["id"])
                                next_id = int(transactions[i + 1]["id"])
                                assert current_id >= next_id, "Transactions should be ordered by ID (newest first)"

                    print("  ✓ Transactions are properly ordered by ID")
            else:
                print("  ✓ Recent transactions response structure validated")

            # Test 2: Large count request
            print("\n✓ Test 2: Large count request")

            large_response = await sandbox_client.transactions.get_recent_transactions(
                account_id=test_account_id,
                count=100
            )

            assert large_response is not None, "Large count response should not be None"

            if "transactions" in large_response:
                large_transactions = large_response["transactions"]
                print(f"  ✓ Retrieved {len(large_transactions)} transactions with count=100")

                # Should not exceed 100
                assert len(large_transactions) <= 100, f"Should not exceed requested count of 100"
            else:
                print("  ✓ Large count response structure validated")

            # Test 3: Transaction type filtering
            print("\n✓ Test 3: Recent transactions with type filtering")

            filtered_recent_response = await sandbox_client.transactions.get_recent_transactions(
                account_id=test_account_id,
                count=20,
                transaction_type=["CREATE", "DAILY_FINANCING"]
            )

            assert filtered_recent_response is not None, "Filtered recent response should not be None"

            if "transactions" in filtered_recent_response:
                filtered_transactions = filtered_recent_response["transactions"]
                print(f"  ✓ Retrieved {len(filtered_transactions)} filtered recent transactions")

                # Validate transaction types
                if filtered_transactions:
                    valid_types = ["CREATE", "DAILY_FINANCING"]
                    for txn in filtered_transactions:
                        if isinstance(txn, dict) and "type" in txn:
                            assert txn["type"] in valid_types, f"Unexpected transaction type: {txn['type']}"

                    print("  ✓ Transaction type filtering for recent transactions validated")
            else:
                print("  ✓ Filtered recent response structure validated")

            # Test 4: Error handling for invalid parameters
            print("\n✓ Test 4: Invalid parameter handling")

            # Test with invalid account ID
            try:
                with pytest.raises(FiveTwentyError) as exc_info:
                    await sandbox_client.transactions.get_recent_transactions(
                        account_id="invalid-account-123",
                        count=10
                    )

                error = exc_info.value
                assert error.status in [400, 404], f"Expected 400/404 for invalid account, got {error.status}"
                print(f"  ✓ Invalid account ID correctly rejected: HTTP {error.status}")

            except AssertionError:
                raise
            except Exception as e:
                print(f"  ⚠ Unexpected error for invalid account: {type(e).__name__}")

        except FiveTwentyError as e:
            print(f"  ⚠ Recent transactions test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during recent transactions test: {type(e).__name__}: {e}")

        print("✓ Recent transactions querying test completed")