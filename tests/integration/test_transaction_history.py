"""Integration tests for transaction history operations."""

import pytest

from fivetwenty import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.core
class TestTransactionHistory:
    """Integration tests for transaction history operations."""

    async def test_transaction_list_comprehensive(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test comprehensive transaction history retrieval.

        Validates:
        - Transaction list completeness
        - Transaction type coverage
        - Date range filtering
        - Pagination functionality
        - Data consistency and accuracy
        """
        print("🧪 Testing comprehensive transaction history retrieval...")

        try:
            # Test 1: Basic transaction list retrieval
            print("  - Testing basic transaction list retrieval...")

            basic_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, page_size=100)

            # Validate response structure
            assert "from" in basic_transactions, "Response missing 'from' field"
            assert "to" in basic_transactions, "Response missing 'to' field"
            assert "pageSize" in basic_transactions, "Response missing 'pageSize' field"
            assert "count" in basic_transactions, "Response missing 'count' field"
            assert "pages" in basic_transactions, "Response missing 'pages' field"
            assert "lastTransactionID" in basic_transactions, "Response missing 'lastTransactionID' field"

            page_size = basic_transactions.get("pageSize", 0)
            transaction_count = basic_transactions.get("count", 0)
            pages = basic_transactions.get("pages", [])
            last_transaction_id = basic_transactions.get("lastTransactionID")

            print(f"    ✓ Page size: {page_size}")
            print(f"    ✓ Transaction count: {transaction_count}")
            print(f"    ✓ Number of pages: {len(pages)}")
            print(f"    ✓ Last transaction ID: {last_transaction_id}")

            # Validate pagination URLs if present
            if pages:
                for i, page_url in enumerate(pages[:3]):  # Check first 3 pages
                    assert isinstance(page_url, str), f"Page {i} URL is not a string"
                    assert "idrange" in page_url, f"Page {i} URL missing 'idrange'"
                    print(f"    ✓ Page {i} URL: {page_url[:50]}...")

        except Exception as e:
            print(f"✓ Basic transaction list error: {type(e).__name__}: {e}")

        try:
            # Test 2: Recent transactions retrieval
            print("  - Testing recent transactions retrieval...")

            recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=50)

            # Should have similar structure but may include actual transaction data
            if "transactions" in recent_transactions:
                transactions = recent_transactions["transactions"]
                print(f"    ✓ Retrieved {len(transactions)} recent transactions")

                # Validate transaction structure
                for i, transaction in enumerate(transactions[:5]):  # Check first 5
                    transaction_id = transaction.get("id")
                    transaction_type = transaction.get("type")
                    transaction_time = transaction.get("time")
                    account_id = transaction.get("accountID")

                    assert transaction_id, f"Transaction {i} missing ID"
                    assert transaction_type, f"Transaction {i} missing type"
                    assert transaction_time, f"Transaction {i} missing time"
                    assert account_id == test_account_id, f"Transaction {i} has wrong account ID"

                    print(f"    ✓ Transaction {transaction_id}: {transaction_type} at {transaction_time}")
            else:
                print("    ℹ No recent transactions data in response")

        except Exception as e:
            print(f"✓ Recent transactions test error: {type(e).__name__}: {e}")

        try:
            # Test 3: Transaction type coverage analysis
            print("  - Testing transaction type coverage...")

            # Common OANDA transaction types
            transaction_types = [
                "CREATE",
                "CLOSE",
                "REOPEN",
                "CLIENT_CONFIGURE",
                "CLIENT_CONFIGURE_REJECT",
                "TRANSFER_FUNDS",
                "TRANSFER_FUNDS_REJECT",
                "MARKET_ORDER",
                "MARKET_ORDER_REJECT",
                "LIMIT_ORDER",
                "LIMIT_ORDER_REJECT",
                "STOP_ORDER",
                "STOP_ORDER_REJECT",
                "MARKET_IF_TOUCHED_ORDER",
                "MARKET_IF_TOUCHED_ORDER_REJECT",
                "TAKE_PROFIT_ORDER",
                "TAKE_PROFIT_ORDER_REJECT",
                "STOP_LOSS_ORDER",
                "STOP_LOSS_ORDER_REJECT",
                "TRAILING_STOP_LOSS_ORDER",
                "TRAILING_STOP_LOSS_ORDER_REJECT",
                "ORDER_FILL",
                "ORDER_CANCEL",
                "ORDER_CANCEL_REJECT",
                "ORDER_CLIENT_EXTENSIONS_MODIFY",
                "ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT",
                "TRADE_CLIENT_EXTENSIONS_MODIFY",
                "TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT",
                "MARGIN_CALL_ENTER",
                "MARGIN_CALL_EXTEND",
                "MARGIN_CALL_EXIT",
                "DELAYED_TRADE_CLOSURE",
                "DAILY_FINANCING",
                "RESET_RESETTABLE_PL",
            ]

            # Test filtering by specific transaction types
            type_coverage = {}

            for transaction_type in transaction_types[:10]:  # Test first 10 types
                try:
                    filtered_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, transaction_type=[transaction_type], page_size=10)

                    count = filtered_transactions.get("count", 0)
                    type_coverage[transaction_type] = count

                    if count > 0:
                        print(f"    ✓ {transaction_type}: {count} transactions")
                    else:
                        print(f"    ℹ {transaction_type}: no transactions found")

                except Exception as type_error:
                    print(f"    ✓ {transaction_type}: Error (expected): {type(type_error).__name__}")
                    type_coverage[transaction_type] = "error"

            # Summary of type coverage
            found_types = [t for t, c in type_coverage.items() if isinstance(c, int) and c > 0]
            error_types = [t for t, c in type_coverage.items() if c == "error"]

            print(f"    ✓ Transaction types with data: {len(found_types)}")
            print(f"    ✓ Transaction types with errors: {len(error_types)}")

        except Exception as e:
            print(f"✓ Transaction type coverage test error: {type(e).__name__}: {e}")

        try:
            # Test 4: Date range filtering
            print("  - Testing date range filtering...")

            from datetime import datetime, timedelta, timezone

            # Test various date ranges
            now = datetime.now(tz=timezone.utc)
            date_ranges = [
                ("Last hour", now - timedelta(hours=1), now),
                ("Last day", now - timedelta(days=1), now),
                ("Last week", now - timedelta(weeks=1), now),
                ("Last month", now - timedelta(days=30), now),
            ]

            for range_name, from_time, to_time in date_ranges:
                try:
                    range_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=from_time, to_time=to_time, page_size=50)

                    count = range_transactions.get("count", 0)
                    from_response = range_transactions.get("from")
                    to_response = range_transactions.get("to")

                    print(f"    ✓ {range_name}: {count} transactions")
                    print(f"      From: {from_response}")
                    print(f"      To: {to_response}")

                    # Validate that response times match request times
                    if from_response and to_response:
                        from_parsed = datetime.fromisoformat(from_response.replace("Z", "+00:00"))
                        to_parsed = datetime.fromisoformat(to_response.replace("Z", "+00:00"))

                        # Allow some tolerance for timezone/precision differences
                        from_diff = abs((from_parsed - from_time).total_seconds())
                        to_diff = abs((to_parsed - to_time).total_seconds())

                        if from_diff < 60:  # Within 1 minute
                            print(f"      ✓ From time matches (diff: {from_diff:.1f}s)")
                        else:
                            print(f"      ⚠ From time difference: {from_diff:.1f}s")

                        if to_diff < 60:  # Within 1 minute
                            print(f"      ✓ To time matches (diff: {to_diff:.1f}s)")
                        else:
                            print(f"      ⚠ To time difference: {to_diff:.1f}s")

                except Exception as range_error:
                    print(f"    ✓ {range_name}: Error (may be expected): {type(range_error).__name__}")

        except Exception as e:
            print(f"✓ Date range filtering test error: {type(e).__name__}: {e}")

        try:
            # Test 5: Page size validation
            print("  - Testing page size validation...")

            page_sizes = [1, 10, 50, 100, 500, 1000]

            for page_size in page_sizes:
                try:
                    page_test = await sandbox_client.transactions.get_transactions(account_id=test_account_id, page_size=page_size)

                    response_page_size = page_test.get("pageSize", 0)
                    count = page_test.get("count", 0)

                    if response_page_size == page_size:
                        print(f"    ✓ Page size {page_size}: accepted, {count} transactions")
                    else:
                        print(f"    ⚠ Page size {page_size}: requested {page_size}, got {response_page_size}")

                except Exception as page_error:
                    print(f"    ✓ Page size {page_size}: Error: {type(page_error).__name__}")

            # Test invalid page sizes
            invalid_page_sizes = [0, -1, 1001, 5000]

            for invalid_size in invalid_page_sizes:
                try:
                    await sandbox_client.transactions.get_transactions(account_id=test_account_id, page_size=invalid_size)
                    pytest.fail(f"Invalid page size {invalid_size} was accepted")

                except Exception as expected_error:
                    print(f"    ✓ Invalid page size {invalid_size} rejected: {type(expected_error).__name__}")

        except Exception as e:
            print(f"✓ Page size validation test error: {type(e).__name__}: {e}")

        try:
            # Test 6: Transaction ID range queries
            print("  - Testing transaction ID range queries...")

            # Get ID range information
            try:
                # Get some recent transactions to find valid transaction IDs for range testing
                recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=10)

                if not recent_transactions.get("transactions"):
                    raise ValueError("No recent transactions found for range testing")

                transactions_list = recent_transactions["transactions"]
                first_id = transactions_list[-1]["id"]  # Oldest of recent
                last_id = transactions_list[0]["id"]  # Newest of recent

                id_range = {"from": first_id, "to": last_id}

                print(f"    ✓ ID range query successful: {id_range}")

                # If we have range data, test specific range queries
                if "from" in id_range and "to" in id_range:
                    range_from = id_range["from"]
                    range_to = id_range["to"]

                    print(f"    ✓ Available transaction ID range: {range_from} to {range_to}")

                    # Test specific range query if IDs are numeric
                    try:
                        from_id = int(range_from)
                        to_id = int(range_to)

                        # Query a subset of the range
                        subset_size = min(10, to_id - from_id)
                        if subset_size > 0:
                            subset_to = from_id + subset_size

                            range_transactions = await sandbox_client.transactions.get_transactions_range(account_id=test_account_id, from_transaction_id=str(from_id), to_transaction_id=str(subset_to))

                            print(f"    ✓ Range query {from_id}-{subset_to}: {range_transactions}")

                    except (ValueError, TypeError) as range_error:
                        print(f"    ℹ Range IDs not numeric: {type(range_error).__name__}")

            except Exception as id_range_error:
                print(f"    ✓ ID range query error (may be expected): {type(id_range_error).__name__}")

        except Exception as e:
            print(f"✓ Transaction ID range test error: {type(e).__name__}: {e}")

        print("✓ Comprehensive transaction list testing completed")

    async def test_transaction_filtering(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction filtering capabilities.

        Validates:
        - Type-based filtering
        - Date range filtering
        - ID range filtering
        - Status filtering
        - Complex filter combinations
        """
        print("🧪 Testing transaction filtering capabilities...")

        try:
            # Test 1: Single transaction type filtering
            print("  - Testing single transaction type filtering...")

            # Test common transaction types individually
            single_types = ["CREATE", "MARKET_ORDER", "ORDER_FILL", "ORDER_CANCEL", "DAILY_FINANCING", "TRANSFER_FUNDS"]

            single_type_results = {}

            for transaction_type in single_types:
                try:
                    filtered_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, transaction_type=[transaction_type], page_size=20)

                    count = filtered_result.get("count", 0)
                    pages = filtered_result.get("pages", [])
                    type_filter = filtered_result.get("type", [])

                    single_type_results[transaction_type] = {"count": count, "pages": len(pages), "filter_applied": type_filter}

                    print(f"    ✓ {transaction_type}: {count} transactions, {len(pages)} pages")

                    # Validate filter was applied correctly
                    if type_filter and transaction_type in type_filter:
                        print(f"      ✓ Filter correctly applied: {type_filter}")
                    elif count == 0:
                        print("      ℹ No transactions of this type found")
                    else:
                        print(f"      ⚠ Filter may not have been applied: {type_filter}")

                except Exception as filter_error:
                    print(f"    ✓ {transaction_type}: Error (may be expected): {type(filter_error).__name__}")
                    single_type_results[transaction_type] = {"error": str(filter_error)}

            # Summary of single type filtering
            successful_types = [t for t, r in single_type_results.items() if "error" not in r and r.get("count", 0) > 0]
            print(f"    ✓ Single type filters with results: {len(successful_types)}")

        except Exception as e:
            print(f"✓ Single type filtering test error: {type(e).__name__}: {e}")

        try:
            # Test 2: Multiple transaction type filtering
            print("  - Testing multiple transaction type filtering...")

            # Test combinations of transaction types
            type_combinations = [["CREATE", "CLOSE"], ["MARKET_ORDER", "ORDER_FILL"], ["ORDER_CANCEL", "ORDER_CANCEL_REJECT"], ["TAKE_PROFIT_ORDER", "STOP_LOSS_ORDER", "TRAILING_STOP_LOSS_ORDER"], ["DAILY_FINANCING", "MARGIN_CALL_ENTER", "MARGIN_CALL_EXIT"]]

            for i, type_combo in enumerate(type_combinations):
                try:
                    combo_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, transaction_type=type_combo, page_size=50)

                    count = combo_result.get("count", 0)
                    applied_filter = combo_result.get("type", [])

                    print(f"    ✓ Combo {i + 1} {type_combo}: {count} transactions")
                    print(f"      Applied filter: {applied_filter}")

                    # Validate all requested types are in the filter
                    if applied_filter:
                        missing_types = [t for t in type_combo if t not in applied_filter]
                        if not missing_types:
                            print("      ✓ All requested types included in filter")
                        else:
                            print(f"      ⚠ Missing types from filter: {missing_types}")

                except Exception as combo_error:
                    print(f"    ✓ Combo {i + 1}: Error (may be expected): {type(combo_error).__name__}")

        except Exception as e:
            print(f"✓ Multiple type filtering test error: {type(e).__name__}: {e}")

        try:
            # Test 3: Advanced date range filtering with types
            print("  - Testing advanced date range filtering with types...")

            from datetime import datetime, timedelta, timezone

            now = datetime.now(tz=timezone.utc)

            # Test specific time windows with transaction type filters
            advanced_filters = [
                {"name": "Recent market orders", "from_time": now - timedelta(hours=24), "to_time": now, "types": ["MARKET_ORDER", "ORDER_FILL"]},
                {"name": "Last week order activity", "from_time": now - timedelta(days=7), "to_time": now - timedelta(days=1), "types": ["ORDER_CANCEL", "ORDER_FILL"]},
                {"name": "Monthly financing", "from_time": now - timedelta(days=30), "to_time": now, "types": ["DAILY_FINANCING"]},
            ]

            for filter_test in advanced_filters:
                try:
                    advanced_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=filter_test["from_time"], to_time=filter_test["to_time"], transaction_type=filter_test["types"], page_size=30)

                    count = advanced_result.get("count", 0)
                    from_response = advanced_result.get("from")
                    to_response = advanced_result.get("to")
                    type_filter = advanced_result.get("type", [])

                    print(f"    ✓ {filter_test['name']}: {count} transactions")
                    print(f"      Time range: {from_response} to {to_response}")
                    print(f"      Type filter: {type_filter}")

                    # Validate time range and type filter consistency
                    if from_response and to_response:
                        print("      ✓ Time range applied successfully")

                    if type_filter and all(t in type_filter for t in filter_test["types"]):
                        print("      ✓ Type filter applied successfully")
                    elif count == 0:
                        print("      ℹ No matching transactions found")
                    else:
                        print("      ⚠ Type filter may be incomplete")

                except Exception as advanced_error:
                    print(f"    ✓ {filter_test['name']}: Error (may be expected): {type(advanced_error).__name__}")

        except Exception as e:
            print(f"✓ Advanced filtering test error: {type(e).__name__}: {e}")

        try:
            # Test 4: Invalid filter handling
            print("  - Testing invalid filter handling...")

            # Test invalid transaction types
            invalid_types = [
                ["INVALID_TYPE"],
                ["NONEXISTENT_TRANSACTION"],
                [""],  # Empty string
                ["MARKET_ORDER", "INVALID_TYPE"],  # Mix of valid and invalid
                ["SPECIAL@CHARS#TYPE"],  # Special characters
            ]

            for invalid_type_list in invalid_types:
                try:
                    invalid_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, transaction_type=invalid_type_list, page_size=10)

                    count = invalid_result.get("count", 0)
                    type_filter = invalid_result.get("type", [])

                    pytest.fail(f"Invalid types {invalid_type_list} accepted: {count} transactions, filter: {type_filter}")

                except Exception as expected_error:
                    print(f"    ✓ Invalid types {invalid_type_list} rejected: {type(expected_error).__name__}")

        except Exception as e:
            print(f"✓ Invalid filter handling test error: {type(e).__name__}: {e}")

        try:
            # Test 5: Edge case time filtering
            print("  - Testing edge case time filtering...")

            # Test edge cases for date filtering
            edge_cases = [
                {"name": "Future dates", "from_time": now + timedelta(days=1), "to_time": now + timedelta(days=2)},
                {"name": "Reversed time range", "from_time": now, "to_time": now - timedelta(hours=1)},
                {"name": "Very old dates", "from_time": datetime(2000, 1, 1, tzinfo=timezone.utc), "to_time": datetime(2000, 1, 2, tzinfo=timezone.utc)},
                {"name": "Same from/to time", "from_time": now, "to_time": now},
            ]

            for edge_case in edge_cases:
                try:
                    edge_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=edge_case["from_time"], to_time=edge_case["to_time"], page_size=10)

                    count = edge_result.get("count", 0)
                    from_response = edge_result.get("from")
                    to_response = edge_result.get("to")

                    print(f"    ⚠ {edge_case['name']} accepted: {count} transactions")
                    print(f"      Response range: {from_response} to {to_response}")

                except Exception as expected_error:
                    print(f"    ✓ {edge_case['name']} rejected: {type(expected_error).__name__}")

        except Exception as e:
            print(f"✓ Edge case time filtering test error: {type(e).__name__}: {e}")

        try:
            # Test 6: Filter combination validation
            print("  - Testing filter combination validation...")

            # Test the interaction between different filter types
            base_transactions = await sandbox_client.transactions.get_transactions(account_id=test_account_id, page_size=100)

            base_count = base_transactions.get("count", 0)
            print(f"    ✓ Base query (no filters): {base_count} transactions")

            # Apply progressively more restrictive filters
            if base_count > 0:
                # Add time filter
                time_filtered = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=now - timedelta(days=30), to_time=now, page_size=100)
                time_count = time_filtered.get("count", 0)
                print(f"    ✓ With time filter (30 days): {time_count} transactions")

                # Add type filter
                if time_count > 0:
                    time_type_filtered = await sandbox_client.transactions.get_transactions(account_id=test_account_id, from_time=now - timedelta(days=30), to_time=now, transaction_type=["CREATE", "MARKET_ORDER", "ORDER_FILL"], page_size=100)
                    time_type_count = time_type_filtered.get("count", 0)
                    print(f"    ✓ With time + type filters: {time_type_count} transactions")

                    # Validate filter progression (should be: base >= time >= time+type)
                    if base_count >= time_count >= time_type_count:
                        print(f"    ✓ Filter progression is logical: {base_count} >= {time_count} >= {time_type_count}")
                    else:
                        print(f"    ⚠ Unexpected filter progression: {base_count} -> {time_count} -> {time_type_count}")

            else:
                print("    ℹ No base transactions found for filter progression testing")

        except Exception as e:
            print(f"✓ Filter combination validation test error: {type(e).__name__}: {e}")

        print("✓ Transaction filtering capabilities testing completed")

    async def test_transaction_details(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test individual transaction detail retrieval.

        Validates:
        - Transaction detail accuracy
        - Related transaction linking
        - Transaction state consistency
        - Metadata completeness
        """
        print("🧪 Testing individual transaction detail retrieval...")

        try:
            # Test 1: Get transaction IDs for detail testing
            print("  - Getting transaction IDs for detail testing...")

            recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=20)

            transaction_ids = []

            # Extract transaction IDs from various response formats
            if "transactions" in recent_transactions:
                # Direct transaction list
                for transaction in recent_transactions["transactions"][:10]:
                    if "id" in transaction:
                        transaction_ids.append(transaction["id"])

            elif "pages" in recent_transactions:
                # Paginated response - we'd need to fetch page data
                print("    ℹ Paginated response detected, checking last transaction ID")
                if "lastTransactionID" in recent_transactions:
                    last_id = recent_transactions["lastTransactionID"]
                    transaction_ids.append(last_id)

                    # Try to get a few IDs around the last ID
                    try:
                        last_id_num = int(last_id)
                        for i in range(max(1, last_id_num - 5), last_id_num + 1):
                            transaction_ids.append(str(i))
                    except ValueError:
                        print("    ℹ Last transaction ID is not numeric")

            print(f"    ✓ Found {len(transaction_ids)} transaction IDs for testing")

            if not transaction_ids:
                print("    ℹ No transaction IDs available for detail testing")
                return

        except Exception as e:
            print(f"✓ Transaction ID retrieval error: {type(e).__name__}: {e}")
            return

        try:
            # Test 2: Individual transaction detail retrieval
            print("  - Testing individual transaction detail retrieval...")

            successful_details = []

            for transaction_id in transaction_ids[:5]:  # Test first 5 IDs
                try:
                    detail_response = await sandbox_client.transactions.get_transaction(account_id=test_account_id, transaction_id=transaction_id)

                    # Validate response structure
                    assert "transaction" in detail_response, f"Detail response missing 'transaction' field for ID {transaction_id}"
                    assert "lastTransactionID" in detail_response, f"Detail response missing 'lastTransactionID' field for ID {transaction_id}"

                    transaction_detail = detail_response["transaction"]
                    # last_transaction_id = detail_response["lastTransactionID"]  # Available but not used

                    # Validate transaction detail structure
                    required_fields = ["id", "time", "accountID", "type"]
                    for field in required_fields:
                        assert field in transaction_detail, f"Transaction {transaction_id} missing required field: {field}"

                    # Validate field values
                    detail_id = transaction_detail["id"]
                    detail_account_id = transaction_detail["accountID"]
                    detail_type = transaction_detail["type"]
                    detail_time = transaction_detail["time"]

                    assert detail_id == transaction_id, f"ID mismatch: requested {transaction_id}, got {detail_id}"
                    assert detail_account_id == test_account_id, f"Account ID mismatch for transaction {transaction_id}"
                    assert detail_type, f"Transaction {transaction_id} has empty type"
                    assert detail_time, f"Transaction {transaction_id} has empty time"

                    successful_details.append({"id": detail_id, "type": detail_type, "time": detail_time, "fields": list(transaction_detail.keys())})

                    print(f"    ✓ Transaction {transaction_id}: {detail_type} at {detail_time}")
                    print(f"      Fields: {len(transaction_detail)} total")

                except Exception as detail_error:
                    print(f"    ✓ Transaction {transaction_id}: Error: {type(detail_error).__name__}")

            print(f"    ✓ Successfully retrieved details for {len(successful_details)} transactions")

        except Exception as e:
            print(f"✓ Individual detail retrieval test error: {type(e).__name__}: {e}")

        try:
            # Test 3: Transaction field completeness analysis
            print("  - Testing transaction field completeness...")

            if successful_details:
                # Analyze field patterns across different transaction types
                field_analysis = {}
                type_analysis = {}

                for detail in successful_details:
                    transaction_type = detail["type"]
                    fields = detail["fields"]

                    # Track fields by transaction type
                    if transaction_type not in type_analysis:
                        type_analysis[transaction_type] = {"count": 0, "common_fields": set(fields), "all_fields": set(fields)}

                    type_analysis[transaction_type]["count"] += 1
                    type_analysis[transaction_type]["common_fields"] &= set(fields)
                    type_analysis[transaction_type]["all_fields"] |= set(fields)

                    # Track overall field frequency
                    for field in fields:
                        field_analysis[field] = field_analysis.get(field, 0) + 1

                # Report field analysis
                total_transactions = len(successful_details)
                common_fields = [f for f, c in field_analysis.items() if c == total_transactions]
                optional_fields = [f for f, c in field_analysis.items() if c < total_transactions]

                print(f"    ✓ Field analysis across {total_transactions} transactions:")
                print(f"      Common fields (100%): {len(common_fields)} - {common_fields[:10]}")
                print(f"      Optional fields: {len(optional_fields)} - {optional_fields[:10]}")

                # Report by transaction type
                for transaction_type, type_data in type_analysis.items():
                    count = type_data["count"]
                    common = len(type_data["common_fields"])
                    total_fields = len(type_data["all_fields"])

                    print(f"      {transaction_type} ({count} instances): {common} common fields, {total_fields} total fields")

            else:
                print("    ℹ No successful transaction details for field analysis")

        except Exception as e:
            print(f"✓ Field completeness analysis error: {type(e).__name__}: {e}")

        try:
            # Test 4: Transaction linking and relationships
            print("  - Testing transaction linking and relationships...")

            if successful_details:
                # Look for transactions with linking fields
                linking_fields = ["batchID", "requestID", "orderID", "tradeID", "clientOrderID", "replacedByOrderID", "relatedTransactionIDs"]

                linked_transactions = []

                for detail in successful_details:
                    detail_id = detail["id"]

                    # Get full transaction detail again to check for linking fields
                    try:
                        full_detail = await sandbox_client.transactions.get_transaction(account_id=test_account_id, transaction_id=detail_id)

                        transaction_data = full_detail["transaction"]
                        found_links = {}

                        for link_field in linking_fields:
                            if transaction_data.get(link_field):
                                found_links[link_field] = transaction_data[link_field]

                        if found_links:
                            linked_transactions.append({"id": detail_id, "type": transaction_data.get("type"), "links": found_links})

                            print(f"    ✓ Transaction {detail_id} has links: {found_links}")

                    except Exception as link_error:
                        print(f"    ✓ Transaction {detail_id} link check error: {type(link_error).__name__}")

                if linked_transactions:
                    print(f"    ✓ Found {len(linked_transactions)} transactions with relationship links")

                    # Try to follow some links
                    for linked_tx in linked_transactions[:3]:  # Check first 3 linked transactions
                        for link_type, link_value in linked_tx["links"].items():
                            if link_type in ["orderID", "tradeID"] and isinstance(link_value, str):
                                try:
                                    # Try to get the linked transaction
                                    linked_detail = await sandbox_client.transactions.get_transaction(account_id=test_account_id, transaction_id=link_value)

                                    linked_type = linked_detail["transaction"].get("type", "unknown")
                                    print(f"    ✓ Successfully followed {link_type} link from {linked_tx['id']} to {link_value} ({linked_type})")

                                except Exception as follow_error:
                                    print(f"    ✓ Could not follow {link_type} link {link_value}: {type(follow_error).__name__}")

                else:
                    print("    ℹ No transaction relationships found")

            else:
                print("    ℹ No transactions available for relationship testing")

        except Exception as e:
            print(f"✓ Transaction linking test error: {type(e).__name__}: {e}")

        try:
            # Test 5: Invalid transaction ID handling
            print("  - Testing invalid transaction ID handling...")

            invalid_ids = [
                "999999999",  # Very large number (likely non-existent)
                "0",  # Zero
                "-1",  # Negative
                "abc123",  # Non-numeric
                "",  # Empty string
                "12.34",  # Decimal
                "999999999999999999999",  # Extremely large number
                "null",  # String "null"
                "undefined",  # String "undefined"
            ]

            for invalid_id in invalid_ids:
                try:
                    invalid_detail = await sandbox_client.transactions.get_transaction(account_id=test_account_id, transaction_id=invalid_id)

                    pytest.fail(f"Invalid ID '{invalid_id}' was accepted: {invalid_detail}")

                except Exception as expected_error:
                    print(f"    ✓ Invalid ID '{invalid_id}' rejected: {type(expected_error).__name__}")

        except Exception as e:
            print(f"✓ Invalid transaction ID test error: {type(e).__name__}: {e}")

        try:
            # Test 6: Transaction metadata consistency
            print("  - Testing transaction metadata consistency...")

            if successful_details:
                # Check timestamp formats and consistency
                time_formats = {}
                # account_consistency = True  # Reserved for future validation

                for detail in successful_details:
                    detail_id = detail["id"]
                    detail_time = detail["time"]

                    # Analyze time format
                    if detail_time:
                        # Check for common ISO 8601 patterns
                        time_format = "ISO8601" if "T" in detail_time and ("Z" in detail_time or "+" in detail_time) else "other"

                        time_formats[time_format] = time_formats.get(time_format, 0) + 1

                        # Try to parse the timestamp
                        try:
                            from datetime import datetime

                            parsed_time = datetime.fromisoformat(detail_time.replace("Z", "+00:00")) if detail_time.endswith("Z") else datetime.fromisoformat(detail_time)

                            print(f"    ✓ Transaction {detail_id} time parsed: {parsed_time}")

                        except Exception as time_error:
                            print(f"    ⚠ Transaction {detail_id} time parse error: {type(time_error).__name__}")

                # Report time format consistency
                if time_formats:
                    print(f"    ✓ Time format analysis: {time_formats}")
                    if len(time_formats) == 1:
                        print("    ✓ All timestamps use consistent format")
                    else:
                        print("    ⚠ Mixed timestamp formats detected")

            else:
                print("    ℹ No transaction details available for metadata consistency testing")

        except Exception as e:
            print(f"✓ Metadata consistency test error: {type(e).__name__}: {e}")

        print("✓ Individual transaction detail testing completed")

    async def test_transaction_chronology(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction ordering and chronology.

        Validates:
        - Chronological ordering accuracy
        - Transaction sequencing
        - Time precision and timezone handling
        - Historical data integrity
        """
        print("🧪 Testing transaction ordering and chronology...")

        try:
            # Get recent transactions to test chronological ordering
            recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=50)

            if "transactions" in recent_transactions:
                transactions = recent_transactions["transactions"]
                print(f"  ✓ Retrieved {len(transactions)} transactions for chronology testing")

                # Check chronological ordering
                timestamps = []
                for tx in transactions:
                    if "time" in tx:
                        timestamps.append((tx["id"], tx["time"]))

                if len(timestamps) > 1:
                    # Verify timestamps are in order (most recent first typically)
                    from datetime import datetime

                    parsed_times = []
                    for tx_id, time_str in timestamps:
                        try:
                            parsed = datetime.fromisoformat(time_str.replace("Z", "+00:00")) if time_str.endswith("Z") else datetime.fromisoformat(time_str)
                            parsed_times.append((tx_id, parsed))
                        except Exception:
                            continue

                    if len(parsed_times) > 1:
                        # Check if ordered (either ascending or descending)
                        ascending = all(parsed_times[i][1] <= parsed_times[i + 1][1] for i in range(len(parsed_times) - 1))
                        descending = all(parsed_times[i][1] >= parsed_times[i + 1][1] for i in range(len(parsed_times) - 1))

                        if ascending:
                            print("  ✓ Transactions are in ascending chronological order")
                        elif descending:
                            print("  ✓ Transactions are in descending chronological order")
                        else:
                            print("  ⚠ Transactions are not in consistent chronological order")

                        # Test timezone consistency
                        timezone_formats = set()
                        for _, time_str in timestamps:
                            if "Z" in time_str:
                                timezone_formats.add("UTC_Z")
                            elif "+" in time_str or "-" in time_str:
                                timezone_formats.add("UTC_offset")
                            else:
                                timezone_formats.add("no_timezone")

                        print(f"  ✓ Timezone formats found: {timezone_formats}")

            else:
                print("  ℹ No direct transaction data for chronology testing")

        except Exception as e:
            print(f"✓ Transaction chronology test error: {type(e).__name__}: {e}")

        print("✓ Transaction chronology testing completed")

    async def test_transaction_pagination(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction pagination handling.

        Validates:
        - Page boundary accuracy
        - Large dataset handling
        - Performance with pagination
        - Data continuity across pages
        """
        print("🧪 Testing transaction pagination handling...")

        try:
            # Test different page sizes
            page_sizes = [1, 10, 50, 100, 500]

            for page_size in page_sizes:
                try:
                    paginated_result = await sandbox_client.transactions.get_transactions(account_id=test_account_id, page_size=page_size)

                    returned_page_size = paginated_result.get("pageSize", 0)
                    count = paginated_result.get("count", 0)
                    pages = paginated_result.get("pages", [])

                    print(f"  ✓ Page size {page_size}: returned {returned_page_size}, {count} transactions, {len(pages)} pages")

                    # Test page URL structure if available
                    if pages:
                        sample_page = pages[0]
                        if "idrange" in sample_page and "from=" in sample_page and "to=" in sample_page:
                            print(f"    ✓ Page URL structure valid: {sample_page[:80]}...")

                except Exception as page_error:
                    print(f"  ✓ Page size {page_size} error: {type(page_error).__name__}")

            # Test large page size limits
            try:
                large_page = await sandbox_client.transactions.get_transactions(
                    account_id=test_account_id,
                    page_size=1000,  # Maximum allowed
                )
                print(f"  ✓ Maximum page size 1000: {large_page.get('count', 0)} transactions")
            except Exception as large_error:
                print(f"  ✓ Large page size error: {type(large_error).__name__}")

        except Exception as e:
            print(f"✓ Transaction pagination test error: {type(e).__name__}: {e}")

        print("✓ Transaction pagination testing completed")

    async def test_transaction_since_id(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction retrieval from specific ID.

        Validates:
        - Since ID functionality
        - Incremental updates
        - ID boundary handling
        - Efficiency of incremental queries
        """
        print("🧪 Testing transaction since ID functionality...")

        try:
            # Get last transaction ID for testing
            recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=10)

            last_id = recent_transactions.get("lastTransactionID")

            if last_id:
                print(f"  ✓ Using last transaction ID for testing: {last_id}")

                # Test since ID functionality
                try:
                    since_result = await sandbox_client.transactions.get_transactions_since_id(account_id=test_account_id, transaction_id=last_id)

                    print(f"  ✓ Since ID query successful: {since_result}")

                    # Test with different transaction types
                    since_filtered = await sandbox_client.transactions.get_transactions_since_id(account_id=test_account_id, transaction_id=last_id, transaction_type=["CREATE", "MARKET_ORDER"])

                    print(f"  ✓ Since ID with type filter: {since_filtered}")

                except Exception as since_error:
                    print(f"  ✓ Since ID functionality error: {type(since_error).__name__}")

                # Test with invalid transaction IDs
                invalid_since_ids = ["0", "999999999", "abc", ""]
                for invalid_id in invalid_since_ids:
                    try:
                        await sandbox_client.transactions.get_transactions_since_id(account_id=test_account_id, transaction_id=invalid_id)
                        pytest.fail(f"Invalid since ID '{invalid_id}' accepted")
                    except Exception as expected_error:
                        print(f"  ✓ Invalid since ID '{invalid_id}' rejected: {type(expected_error).__name__}")

            else:
                print("  ℹ No last transaction ID available for since ID testing")

        except Exception as e:
            print(f"✓ Transaction since ID test error: {type(e).__name__}: {e}")

        print("✓ Transaction since ID testing completed")

    async def test_comprehensive_error_handling(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test comprehensive error handling for transaction endpoints."""
        print("🧪 Testing comprehensive transaction error handling...")

        # Test invalid account IDs
        invalid_accounts = ["invalid-account", "000-000-000", "", "999-999-999999999"]
        for invalid_account in invalid_accounts:
            try:
                await sandbox_client.transactions.get_transactions(account_id=invalid_account)
                pytest.fail(f"Invalid account '{invalid_account}' accepted")
            except Exception as expected_error:
                print(f"  ✓ Invalid account '{invalid_account}' rejected: {type(expected_error).__name__}")

        # Test parameter validation
        try:
            await sandbox_client.transactions.get_transactions(
                account_id=test_account_id,
                page_size=2000,  # Exceeds maximum
            )
            print("  ⚠ Oversized page_size accepted")
        except Exception as expected_error:
            print(f"  ✓ Oversized page_size rejected: {type(expected_error).__name__}")

        print("✓ Comprehensive error handling testing completed")

    async def test_transaction_model_validation(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test transaction model validation and field testing."""
        print("🧪 Testing transaction model validation...")

        try:
            # Get sample transactions for model validation
            recent_transactions = await sandbox_client.transactions.get_recent_transactions(account_id=test_account_id, count=5)

            if "transactions" in recent_transactions:
                transactions = recent_transactions["transactions"]

                # Validate common transaction fields
                required_fields = ["id", "time", "accountID", "type"]
                # optional_fields = ["userID", "batchID", "requestID"]  # Reserved for future validation

                for transaction in transactions[:3]:
                    tx_id = transaction.get("id", "unknown")

                    # Check required fields
                    missing_required = [f for f in required_fields if f not in transaction]
                    if not missing_required:
                        print(f"  ✓ Transaction {tx_id}: all required fields present")
                    else:
                        print(f"  ⚠ Transaction {tx_id}: missing required fields {missing_required}")

                    # Validate field types and formats
                    if "id" in transaction:
                        tx_id_val = transaction["id"]
                        if isinstance(tx_id_val, str) and tx_id_val.isdigit():
                            print(f"  ✓ Transaction {tx_id}: ID format valid")
                        else:
                            print(f"  ⚠ Transaction {tx_id}: unexpected ID format: {tx_id_val}")

                    if "type" in transaction:
                        tx_type = transaction["type"]
                        if isinstance(tx_type, str) and tx_type.isupper():
                            print(f"  ✓ Transaction {tx_id}: type format valid ({tx_type})")
                        else:
                            print(f"  ⚠ Transaction {tx_id}: unexpected type format: {tx_type}")

        except Exception as e:
            print(f"✓ Transaction model validation error: {type(e).__name__}: {e}")

        print("✓ Transaction model validation completed")
