"""Unit tests for transaction endpoints."""

import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.transactions import TransactionEndpoints
from fivetwenty.models import OrderFillTransaction, TransactionFilter, TransactionHeartbeat


class TestTransactionEndpoints:
    """Test suite for transaction history and audit functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()

        # Define side_effect function to return different responses based on endpoint
        def mock_request_side_effect(*args, **kwargs):
            mock_response = MagicMock()

            # Extract the endpoint path
            if len(args) >= 2:
                endpoint = args[1]
            else:
                endpoint = ""

            # Return appropriate mock data based on endpoint
            if "/transactions/" in endpoint and not endpoint.endswith("/transactions"):
                # Single transaction response (get_transaction)
                if "/sinceid" in endpoint:
                    # get_transactions_since_id response
                    mock_response.json.return_value = {
                        "transactions": [
                            {
                                "id": "1001",
                                "type": "ORDER_FILL",
                                "time": "2024-01-01T12:00:00.000000000Z",
                                "userID": 12345,
                                "accountID": "101-001-123456-001",
                                "batchID": "1001",
                                "orderID": "5001",
                                "instrument": "EUR_USD",
                                "units": "1000",
                            }
                        ],
                        "lastTransactionID": "1001",
                    }
                elif "/idrange" in endpoint:
                    # get_transactions_range response
                    mock_response.json.return_value = {
                        "transactions": [
                            {
                                "id": "1500",
                                "type": "MARKET_ORDER",
                                "time": "2024-01-01T13:00:00.000000000Z",
                                "userID": 12345,
                                "accountID": "101-001-123456-001",
                                "batchID": "1500",
                                "instrument": "USD_JPY",
                                "units": "5000",
                                "timeInForce": "FOK",
                                "positionFill": "DEFAULT",
                                "reason": "CLIENT_ORDER",
                            }
                        ],
                        "lastTransactionID": "2000",
                    }
                else:
                    # Single transaction (get_transaction)
                    mock_response.json.return_value = {
                        "transaction": {
                            "id": "12345",
                            "type": "CREATE",
                            "time": "2024-01-01T00:00:00.000000000Z",
                            "userID": 12345,
                            "accountID": "101-001-123456-001",
                            "batchID": "12345",
                            "divisionID": 1,
                            "siteID": 1,
                            "accountUserID": 12345,
                            "accountNumber": 1,
                            "homeCurrency": "USD",
                        },
                        "lastTransactionID": "12345",
                    }
            elif endpoint.endswith("/transactions"):
                # The transactions list endpoint always returns page URLs,
                # never inline transaction data (matches real OANDA behavior).
                params = kwargs.get("params", {})
                mock_response.json.return_value = {
                    "from": "2024-01-01T00:00:00.000000000Z",
                    "to": "2024-01-02T00:00:00.000000000Z",
                    "pageSize": params.get("pageSize", "100"),
                    "count": "150",
                    "pages": [
                        "https://api-fxpractice.oanda.com/v3/accounts/101-001-123456-001/transactions?from=2024-01-01T00:00:00.000000000Z&to=2024-01-02T00:00:00.000000000Z&pageSize=100&page=1",
                        "https://api-fxpractice.oanda.com/v3/accounts/101-001-123456-001/transactions?from=2024-01-01T00:00:00.000000000Z&to=2024-01-02T00:00:00.000000000Z&pageSize=100&page=2",
                    ],
                    "lastTransactionID": "5000",
                }
            else:
                # Default response
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=mock_request_side_effect)
        return client

    @pytest.fixture
    def transactions(self, mock_client):
        """Create TransactionEndpoints instance with mock client."""
        return TransactionEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_list_basic(self, transactions, mock_client):
        """Test basic transaction listing."""
        result = await transactions.get_transactions("101-001-123456-001")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions",
            params={"pageSize": "100"},
        )
        assert result["count"] == "150"
        assert result["lastTransactionID"] == "5000"
        assert result["from_"] == "2024-01-01T00:00:00.000000000Z"

    @pytest.mark.asyncio
    async def test_list_with_time_range(self, transactions, mock_client):
        """Test transaction listing with time range."""
        from_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        to_time = datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

        await transactions.get_transactions("101-001-123456-001", from_time=from_time, to_time=to_time, page_size=200)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions",
            params={
                "pageSize": "200",
                "from": from_time.isoformat(),
                "to": to_time.isoformat(),
            },
        )

    @pytest.mark.asyncio
    async def test_list_uses_unix_datetime_format(self, transactions, mock_client):
        """Test transaction listing honors the client's DateTime format."""
        mock_client._datetime_format = "UNIX"
        from_time = datetime(2024, 1, 1, 12, 0, 0, 123456, tzinfo=timezone.utc)
        to_time = datetime(2024, 1, 1, 12, 5, 0, 654321, tzinfo=timezone.utc)

        await transactions.get_transactions("101-001-123456-001", from_time=from_time, to_time=to_time, page_size=200)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions",
            params={
                "pageSize": "200",
                "from": "1704110400.123456000",
                "to": "1704110700.654321000",
            },
        )

    @pytest.mark.asyncio
    async def test_list_with_transaction_types(self, transactions, mock_client):
        """Test transaction listing with type filtering."""
        transaction_types = ["ORDER_FILL", "MARKET_ORDER", "LIMIT_ORDER"]

        await transactions.get_transactions("101-001-123456-001", transaction_type=transaction_types, page_size=50)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions",
            params={
                "pageSize": "50",
                "type": "ORDER_FILL,MARKET_ORDER,LIMIT_ORDER",
            },
        )

    @pytest.mark.asyncio
    async def test_list_page_size_out_of_range_raises_error(self, transactions, mock_client):
        """Test that page_size outside OANDA's documented range raises ValueError."""
        with pytest.raises(ValueError, match="Page size must be between 1 and 1000"):
            await transactions.get_transactions("101-001-123456-001", page_size=0)

        with pytest.raises(ValueError, match="Page size must be between 1 and 1000"):
            await transactions.get_transactions("101-001-123456-001", page_size=1001)

    @pytest.mark.asyncio
    async def test_get_transaction(self, transactions, mock_client):
        """Test getting a specific transaction."""
        result = await transactions.get_transaction("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions/12345",
        )
        assert result["transaction"].id == "12345"
        assert result["transaction"].type == "CREATE"
        assert result["lastTransactionID"] == "12345"

    @pytest.mark.asyncio
    async def test_get_since_id_basic(self, transactions, mock_client):
        """Test getting transactions since a specific ID."""
        result = await transactions.get_transactions_since_id("101-001-123456-001", "1000")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions/sinceid",
            params={"id": "1000"},
        )
        assert result["transactions"][0].id == "1001"
        assert result["transactions"][0].type == "ORDER_FILL"
        assert result["lastTransactionID"] == "1001"

    @pytest.mark.asyncio
    async def test_get_since_id_with_type_filter(self, transactions, mock_client):
        """Test getting transactions since ID with type filtering."""
        transaction_types = [TransactionFilter.ORDER_FILL, TransactionFilter.TRANSFER_FUNDS]

        await transactions.get_transactions_since_id("101-001-123456-001", "2000", transaction_type=transaction_types)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions/sinceid",
            params={
                "id": "2000",
                "type": "ORDER_FILL,TRANSFER_FUNDS",
            },
        )

    @pytest.mark.asyncio
    async def test_get_range_basic(self, transactions, mock_client):
        """Test getting transactions within an ID range."""
        result = await transactions.get_transactions_range("101-001-123456-001", "1000", "2000")

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions/idrange",
            params={
                "from": "1000",
                "to": "2000",
            },
        )
        assert result["transactions"][0].id == "1500"
        assert result["transactions"][0].type == "MARKET_ORDER"
        assert result["lastTransactionID"] == "2000"

    @pytest.mark.asyncio
    async def test_get_range_with_type_filter(self, transactions, mock_client):
        """Test getting transaction range with type filtering."""
        transaction_types = ["MARKET_ORDER"]

        await transactions.get_transactions_range("101-001-123456-001", "1500", "2500", transaction_type=transaction_types)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions/idrange",
            params={
                "from": "1500",
                "to": "2500",
                "type": "MARKET_ORDER",
            },
        )

    @pytest.mark.asyncio
    async def test_get_range_invalid_id_order_raises_error(self, transactions, mock_client):
        """Test that invalid ID order raises ValueError."""
        with pytest.raises(ValueError, match="from_transaction_id must be <= to_transaction_id"):
            await transactions.get_transactions_range("101-001-123456-001", "2000", "1000")

    @pytest.mark.asyncio
    async def test_get_range_non_numeric_ids_raises_error(self, transactions, mock_client):
        """Test that non-numeric transaction IDs raise ValueError."""
        with pytest.raises(ValueError, match="Transaction IDs must be numeric"):
            await transactions.get_transactions_range("101-001-123456-001", "abc", "def")

    @pytest.mark.asyncio
    async def test_get_recent_basic(self, transactions, mock_client):
        """Recent transactions resolve the last ID, then fetch the trailing ID range."""
        result = await transactions.get_recent_transactions("101-001-123456-001")

        assert mock_client._request.call_args_list == [
            (("GET", "/accounts/101-001-123456-001/transactions"), {"params": {"pageSize": "1"}}),
            (("GET", "/accounts/101-001-123456-001/transactions/idrange"), {"params": {"from": "4951", "to": "5000"}}),
        ]
        assert result["transactions"][0].id == "1500"
        assert result["transactions"][0].type == "MARKET_ORDER"
        assert result["lastTransactionID"] == "2000"

    @pytest.mark.asyncio
    async def test_get_recent_with_count_and_type(self, transactions, mock_client):
        """Custom count and type filter are applied to the ID-range request."""
        transaction_types = ["ORDER_FILL", "STOP_LOSS_ORDER"]

        await transactions.get_recent_transactions("101-001-123456-001", count=100, transaction_type=transaction_types)

        assert mock_client._request.call_args_list[-1] == (
            ("GET", "/accounts/101-001-123456-001/transactions/idrange"),
            {"params": {"from": "4901", "to": "5000", "type": "ORDER_FILL,STOP_LOSS_ORDER"}},
        )

    @pytest.mark.asyncio
    async def test_get_recent_count_clamps_range_start_at_one(self, transactions, mock_client):
        """A count larger than the transaction history starts the range at ID 1."""

        def small_history(*args, **kwargs):
            mock_response = MagicMock()
            if args[1].endswith("/transactions"):
                mock_response.json.return_value = {"pages": [], "lastTransactionID": "3"}
            else:
                mock_response.json.return_value = {"transactions": [], "lastTransactionID": "3"}
            return mock_response

        mock_client._request = AsyncMock(side_effect=small_history)

        await transactions.get_recent_transactions("101-001-123456-001", count=500)

        assert mock_client._request.call_args_list[-1] == (
            ("GET", "/accounts/101-001-123456-001/transactions/idrange"),
            {"params": {"from": "1", "to": "3"}},
        )

    @pytest.mark.asyncio
    async def test_get_recent_count_out_of_bounds_raises_error(self, transactions, mock_client):
        """Counts outside 1-500 raise ValueError."""
        with pytest.raises(ValueError, match="Count must be between 1 and 500"):
            await transactions.get_recent_transactions("101-001-123456-001", count=501)
        with pytest.raises(ValueError, match="Count must be between 1 and 500"):
            await transactions.get_recent_transactions("101-001-123456-001", count=0)

    @pytest.mark.asyncio
    async def test_stream_basic(self, transactions, mock_client):
        """Test basic transaction streaming setup."""

        # Create a proper async generator
        async def mock_stream_generator():
            yield '{"type": "TRANSACTION", "id": "123"}'

        # Mock the _stream method to return our generator
        mock_client._stream = mock_stream_generator

        # Test that we can call the stream method (just verify setup)
        stream_iter = transactions.get_transactions_stream("101-001-123456-001")

        # Verify it's an async iterator
        assert hasattr(stream_iter, "__aiter__")

        # Note: We don't fully test the streaming here as it requires complex mocking
        # The important part is that the method is correctly set up

    @pytest.mark.asyncio
    async def test_stream_with_custom_timeout(self, transactions, mock_client):
        """Test transaction streaming method signature."""
        # Just test that the method can be called with custom timeout
        # without doing full streaming which would require complex async mocking

        # Mock to track calls
        mock_client._stream = AsyncMock()

        # Create the stream iterator (don't consume it)
        stream_iter = transactions.get_transactions_stream("101-001-123456-001", stall_timeout=60.0)

        # Verify it's an async iterator
        assert hasattr(stream_iter, "__aiter__")

        # The actual streaming would happen when we iterate, which we skip for testing

    @pytest.mark.asyncio
    async def test_stream_json_handling(self, transactions, mock_client):
        """Test that streaming method sets up JSON parsing correctly."""
        # Test the JSON parsing logic without full streaming
        # This tests that the method correctly handles JSON parsing setup

        # Mock the logging method
        mock_client._log = MagicMock()
        mock_client._stream = AsyncMock()

        # Create the stream iterator
        stream_iter = transactions.get_transactions_stream("101-001-123456-001")

        # Verify the iterator is created correctly
        assert hasattr(stream_iter, "__aiter__")

        # The actual JSON parsing and error handling is tested in integration tests
        # Here we just verify the method is properly configured

    @pytest.mark.asyncio
    async def test_comprehensive_time_based_query(self, transactions, mock_client):
        """Test comprehensive time-based transaction query with all parameters."""
        from_time = datetime(2024, 6, 1, 9, 0, 0, tzinfo=timezone.utc)
        to_time = datetime(2024, 6, 1, 17, 0, 0, tzinfo=timezone.utc)
        transaction_types = ["ORDER_FILL", "DAILY_FINANCING", "MARKET_ORDER"]

        await transactions.get_transactions("101-001-123456-001", from_time=from_time, to_time=to_time, page_size=250, transaction_type=transaction_types)

        mock_client._request.assert_called_once_with(
            "GET",
            "/accounts/101-001-123456-001/transactions",
            params={
                "pageSize": "250",
                "from": from_time.isoformat(),
                "to": to_time.isoformat(),
                "type": "ORDER_FILL,DAILY_FINANCING,MARKET_ORDER",
            },
        )

    @pytest.mark.asyncio
    async def test_all_transaction_types_filtering(self, transactions, mock_client):
        """Test filtering with comprehensive transaction types."""
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

        await transactions.get_recent_transactions("101-001-123456-001", count=200, transaction_type=transaction_types)

        expected_types = ",".join(transaction_types)
        assert mock_client._request.call_args_list[-1] == (
            ("GET", "/accounts/101-001-123456-001/transactions/idrange"),
            {"params": {"from": "4801", "to": "5000", "type": expected_types}},
        )

    @pytest.mark.asyncio
    async def test_transaction_responses_support_compatibility_access(self, transactions):
        """Test transaction endpoint responses support attribute and nested model access."""
        list_response = await transactions.get_transactions("101-001-123456-001")

        assert list_response.from_ == "2024-01-01T00:00:00.000000000Z"
        assert list_response.last_transaction_id == "5000"

        detail_response = await transactions.get_transaction("101-001-123456-001", "12345")

        assert detail_response.last_transaction_id == "12345"
        assert detail_response.transaction.id == "12345"
        assert detail_response["id"] == "12345"


class TestTransactionTypeDispatch:
    """The type→model dispatch must stay exhaustive over OANDA's TransactionType set."""

    def test_dispatch_map_covers_every_transaction_type(self):
        from fivetwenty.endpoints.transactions import _TRANSACTION_TYPE_MAP
        from fivetwenty.models import TransactionType

        enum_values = {member.value for member in TransactionType}
        assert set(_TRANSACTION_TYPE_MAP) == enum_values

    def test_dispatch_map_matches_union_membership(self):
        import typing

        from fivetwenty.endpoints.transactions import _TRANSACTION_TYPE_MAP, TransactionUnion

        union_members = set(typing.get_args(TransactionUnion))
        assert set(_TRANSACTION_TYPE_MAP.values()) == union_members

    @pytest.mark.asyncio
    async def test_client_extensions_modify_reject_types_parse(self):
        """Regression: these two types previously raised ValueError (unknown type)."""
        from unittest.mock import MagicMock

        from fivetwenty.models import (
            OrderClientExtensionsModifyRejectTransaction,
            TradeClientExtensionsModifyRejectTransaction,
        )

        endpoints = TransactionEndpoints(MagicMock())
        base = {
            "id": "77",
            "time": "2024-01-01T00:00:00.000000000Z",
            "userID": 12345,
            "accountID": "101-001-123456-001",
            "batchID": "77",
            "rejectReason": "CLIENT_EXTENSIONS_DATA_MISSING",
        }
        order_reject = endpoints._parse_transaction({**base, "type": "ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT", "orderID": "5"})
        assert isinstance(order_reject, OrderClientExtensionsModifyRejectTransaction)
        trade_reject = endpoints._parse_transaction({**base, "type": "TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT", "tradeID": "6"})
        assert isinstance(trade_reject, TradeClientExtensionsModifyRejectTransaction)

    def test_delayed_trade_closure_transaction_name_matches_oanda(self):
        """The model is named after OANDA's DelayedTradeClosureTransaction definition."""
        from fivetwenty.models import DelayedTradeClosureTransaction

        assert DelayedTradeClosureTransaction.__name__ == "DelayedTradeClosureTransaction"

    def test_unknown_transaction_type_raises(self):
        from unittest.mock import MagicMock

        endpoints = TransactionEndpoints(MagicMock())
        with pytest.raises(ValueError, match="Unknown transaction type"):
            endpoints._parse_transaction({"type": "NOT_A_REAL_TYPE"})


class TestTransactionStreamParsing:
    """Test the get_transactions_stream line-parsing loop."""

    @staticmethod
    def _stream_client(lines):
        """Create a mock client whose _stream yields the given raw lines."""
        client = MagicMock()

        async def fake_stream(path, *, params, stall_timeout):
            assert path == "/accounts/101-001-123456-001/transactions/stream"
            assert params == {}
            for line in lines:
                yield line

        client._stream = fake_stream
        client._log = MagicMock()
        return client

    @pytest.mark.asyncio
    async def test_stream_yields_heartbeats_and_transactions(self):
        """Test that heartbeat and transaction lines are parsed into models."""
        heartbeat_line = json.dumps({"type": "HEARTBEAT", "time": "2024-01-01T12:00:05.000000000Z", "lastTransactionID": "1001"})
        order_fill_line = json.dumps(
            {
                "id": "1002",
                "type": "ORDER_FILL",
                "time": "2024-01-01T12:00:06.000000000Z",
                "userID": 12345,
                "accountID": "101-001-123456-001",
                "batchID": "1002",
                "orderID": "5001",
                "instrument": "EUR_USD",
                "units": "1000",
            }
        )
        client = self._stream_client([heartbeat_line, order_fill_line])
        transactions = TransactionEndpoints(client)

        results = [item async for item in transactions.get_transactions_stream("101-001-123456-001")]

        assert len(results) == 2
        assert isinstance(results[0], TransactionHeartbeat)
        assert str(results[0].last_transaction_id) == "1001"
        assert isinstance(results[1], OrderFillTransaction)
        assert results[1].order_id == "5001"
        client._log.assert_not_called()

    @pytest.mark.asyncio
    async def test_stream_skips_and_logs_malformed_lines(self):
        """Test that malformed JSON and unknown types are logged and skipped."""
        heartbeat_line = json.dumps({"type": "HEARTBEAT", "time": "2024-01-01T12:00:05.000000000Z", "lastTransactionID": "1001"})
        malformed_line = "{not valid json"
        unknown_type_line = json.dumps({"id": "1003", "type": "NOT_A_REAL_TYPE"})
        client = self._stream_client([malformed_line, heartbeat_line, unknown_type_line])
        transactions = TransactionEndpoints(client)

        results = [item async for item in transactions.get_transactions_stream("101-001-123456-001")]

        # Only the heartbeat survives; both bad lines are logged and skipped
        assert len(results) == 1
        assert isinstance(results[0], TransactionHeartbeat)
        assert client._log.call_count == 2
        for call in client._log.call_args_list:
            assert call.args[0] == "warning"
            assert "Malformed transaction stream data" in call.args[1]


class TestRecentTransactionsEmptyAccount:
    """Test get_recent_transactions on an account with no transactions."""

    @pytest.mark.asyncio
    async def test_get_recent_returns_empty_when_no_transactions(self):
        """Test the early return when lastTransactionID is below 1."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"lastTransactionID": "0"}
        client._request = AsyncMock(return_value=mock_response)
        transactions = TransactionEndpoints(client)

        result = await transactions.get_recent_transactions("101-001-123456-001")

        assert result["transactions"] == []
        assert result["lastTransactionID"] == "0"
        client._request.assert_called_once()
