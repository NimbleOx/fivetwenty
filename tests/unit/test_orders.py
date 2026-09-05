"""Unit tests for enhanced order management endpoints."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.orders import OrderEndpoints
from fivetwenty.models import (
    ClientExtensions,
    FixedPriceOrder,
    GuaranteedStopLossOrder,
    GuaranteedStopLossOrderRejectTransaction,
    GuaranteedStopLossOrderTransaction,
    LimitOrder,
    LimitOrderRejectTransaction,
    LimitOrderRequest,
    LimitOrderTransaction,
    MarketIfTouchedOrder,
    MarketIfTouchedOrderRejectTransaction,
    MarketIfTouchedOrderRequest,
    MarketIfTouchedOrderTransaction,
    MarketOrder,
    MarketOrderRejectTransaction,
    MarketOrderTransaction,
    OrderCancelTransaction,
    OrderFillTransaction,
    StopLossOrder,
    StopLossOrderRejectTransaction,
    StopLossOrderTransaction,
    StopOrder,
    StopOrderRejectTransaction,
    StopOrderRequest,
    StopOrderTransaction,
    TakeProfitOrder,
    TakeProfitOrderRejectTransaction,
    TakeProfitOrderTransaction,
    TrailingStopLossOrder,
    TrailingStopLossOrderRejectTransaction,
    TrailingStopLossOrderTransaction,
)


class TestEnhancedOrderEndpoints:
    """Test suite for enhanced order management functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()

        # Create a side effect function that returns appropriate responses based on the request
        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()

            # For POST /accounts/{id}/orders - order creation
            if method == "POST" and "/orders" in path and "/cancel" not in path and "/clientExtensions" not in path:
                mock_response.json.return_value = {
                    "orderCreateTransaction": {
                        "id": "12345",
                        "type": "MARKET_ORDER",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12345",
                        "requestID": "12345",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "timeInForce": "FOK",
                        "positionFill": "DEFAULT",
                        "reason": "CLIENT_ORDER",
                    },
                    "orderFillTransaction": {
                        "id": "12346",
                        "type": "ORDER_FILL",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12345",
                        "requestID": "12345",
                        "orderID": "12345",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "price": "1.10000",
                        "pl": "0.0000",
                        "financing": "0.0000",
                        "commission": "0.0000",
                        "accountBalance": "100000.0000",
                        "reason": "MARKET_ORDER",
                    },
                    "relatedTransactionIDs": ["12345", "12346"],
                    "lastTransactionID": "12346",
                }
            # For GET /accounts/{id}/orders/{order_id} - get specific order
            elif method == "GET" and "/orders/" in path and not path.endswith("/orders"):
                order_id = path.split("/")[-1]
                mock_response.json.return_value = {
                    "order": {
                        "id": order_id,
                        "createTime": "2024-01-01T00:00:00.000000000Z",
                        "state": "PENDING",
                        "type": "LIMIT",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "price": "1.10000",
                        "timeInForce": "GTC",
                        "positionFill": "DEFAULT",
                        "triggerCondition": "DEFAULT",
                    },
                    "lastTransactionID": "6789",
                }
            # For GET /accounts/{id}/orders - list orders
            elif method == "GET" and path.endswith("/orders"):
                mock_response.json.return_value = {
                    "orders": [
                        {
                            "id": "12345",
                            "createTime": "2024-01-01T00:00:00.000000000Z",
                            "state": "PENDING",
                            "type": "LIMIT",
                            "instrument": "EUR_USD",
                            "units": "1000",
                            "price": "1.10000",
                            "timeInForce": "GTC",
                            "positionFill": "DEFAULT",
                            "triggerCondition": "DEFAULT",
                        },
                        {
                            "id": "12346",
                            "createTime": "2024-01-01T00:00:00.000000000Z",
                            "state": "PENDING",
                            "type": "LIMIT",
                            "instrument": "GBP_USD",
                            "units": "500",
                            "price": "1.25000",
                            "timeInForce": "GTC",
                            "positionFill": "DEFAULT",
                            "triggerCondition": "DEFAULT",
                        },
                    ],
                    "lastTransactionID": "12346",
                }
            # For GET /accounts/{id}/pendingOrders
            elif method == "GET" and "/pendingOrders" in path:
                mock_response.json.return_value = {
                    "orders": [],
                    "lastTransactionID": "12345",
                }
            # For PUT /accounts/{id}/orders/{id}/cancel
            elif method == "PUT" and "/cancel" in path:
                mock_response.json.return_value = {
                    "orderCancelTransaction": {
                        "id": "12346",
                        "type": "ORDER_CANCEL",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12346",
                        "requestID": "12346",
                        "orderID": "12345",
                        "reason": "CLIENT_REQUEST",
                    },
                    "relatedTransactionIDs": ["12346"],
                    "lastTransactionID": "12346",
                }
            # For PUT /accounts/{id}/orders/{id}/clientExtensions
            elif method == "PUT" and "/clientExtensions" in path:
                mock_response.json.return_value = {
                    "orderClientExtensionsModifyTransaction": {
                        "id": "12347",
                        "type": "ORDER_CLIENT_EXTENSIONS_MODIFY",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12347",
                        "requestID": "12347",
                        "orderID": "12345",
                        "clientExtensionsModify": {
                            "id": "my_order_id",
                            "tag": "strategy_v1",
                            "comment": "Breakout trade",
                        },
                    },
                    "relatedTransactionIDs": ["12347"],
                    "lastTransactionID": "12347",
                }
            # For PUT /accounts/{id}/orders/{id} - replace order
            elif method == "PUT" and "/orders/" in path and "/cancel" not in path and "/clientExtensions" not in path:
                mock_response.json.return_value = {
                    "orderCancelTransaction": {
                        "id": "12346",
                        "type": "ORDER_CANCEL",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12346",
                        "requestID": "12346",
                        "orderID": "12345",
                        "reason": "CLIENT_REQUEST_REPLACED",
                    },
                    "orderCreateTransaction": {
                        "id": "12347",
                        "type": "LIMIT_ORDER",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12346",
                        "requestID": "12346",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "price": "1.12000",
                        "timeInForce": "GTC",
                        "positionFill": "DEFAULT",
                        "triggerCondition": "DEFAULT",
                        "reason": "REPLACEMENT",
                    },
                    "relatedTransactionIDs": ["12346", "12347"],
                    "lastTransactionID": "12347",
                }
            else:
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
        return client

    @pytest.fixture
    def orders(self, mock_client):
        """Create OrderEndpoints instance with mock client."""
        return OrderEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_orders_basic(self, orders, mock_client):
        """Test basic order listing."""
        result = await orders.get_orders("101-001-123456-001")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders", params={"state": "PENDING", "count": 50})
        assert len(result["orders"]) == 2
        assert result["orders"][0].id == "12345"
        assert result["lastTransactionID"] == "12346"

    @pytest.mark.asyncio
    async def test_get_orders_with_filters(self, orders, mock_client):
        """Test order listing with filters."""
        await orders.get_orders("101-001-123456-001", state="FILLED", instrument="EUR_USD", count=25, before_id="12340")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders", params={"state": "FILLED", "count": 25, "instrument": "EUR_USD", "beforeID": "12340"})

    @pytest.mark.asyncio
    async def test_get_order(self, orders, mock_client):
        """Test getting specific order details."""
        result = await orders.get_order("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders/12345")
        assert result["order"].id == "12345"
        assert result["order"].instrument == "EUR_USD"
        assert result["lastTransactionID"] == "6789"

    @pytest.mark.asyncio
    async def test_cancel_order(self, orders, mock_client):
        """Test order cancellation."""
        result = await orders.cancel_order("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345/cancel", timeout=None, headers={})
        assert "orderCancelTransaction" in result

    @pytest.mark.asyncio
    async def test_cancel_order_with_timeout(self, orders, mock_client):
        """Test order cancellation with timeout."""
        await orders.cancel_order("101-001-123456-001", "12345", timeout=30.0)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345/cancel", timeout=30.0, headers={})

    @pytest.mark.asyncio
    async def test_cancel_order_with_client_request_id(self, orders, mock_client):
        """Test order cancellation with client request ID."""
        result = await orders.cancel_order("101-001-123456-001", "12345", client_request_id="cancel-req-123")

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345/cancel", timeout=None, headers={"ClientRequestID": "cancel-req-123"})
        assert "orderCancelTransaction" in result

    @pytest.mark.asyncio
    async def test_list_pending_orders(self, orders, mock_client):
        """Test listing all pending orders."""
        await orders.get_pending_orders("101-001-123456-001")
        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/pendingOrders")

    @pytest.mark.asyncio
    async def test_replace_order(self, orders, mock_client):
        """Test replacing an existing order."""
        order_request = LimitOrderRequest(instrument="EUR_USD", units=Decimal("1000"), price=Decimal("1.12000"))

        await orders.put_order("101-001-123456-001", "12345", order_request)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/orders/12345",
            json_data={
                "order": {
                    "type": "LIMIT",
                    "instrument": "EUR_USD",
                    "units": "1000",
                    "price": "1.12000",
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                }
            },
            headers={},
        )

    @pytest.mark.asyncio
    async def test_replace_order_with_client_id(self, orders, mock_client):
        """Test replacing an order using @clientID format."""
        order_request = StopOrderRequest(instrument="GBP_USD", units=Decimal("-500"), price=Decimal("1.25000"))

        await orders.put_order("101-001-123456-001", "@my_custom_order_123", order_request)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/orders/@my_custom_order_123",
            json_data={
                "order": {
                    "type": "STOP",
                    "instrument": "GBP_USD",
                    "units": "-500",
                    "price": "1.25000",
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                }
            },
            headers={},
        )

    @pytest.mark.asyncio
    async def test_replace_order_with_client_request_id(self, orders, mock_client):
        """Test replacing an order with client request ID."""
        order_request = MarketIfTouchedOrderRequest(instrument="USD_JPY", units=Decimal("2000"), price=Decimal("110.500"))

        await orders.put_order("101-001-123456-001", "67890", order_request, client_request_id="replace_request_123")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/orders/67890",
            json_data={
                "order": {
                    "type": "MARKET_IF_TOUCHED",
                    "instrument": "USD_JPY",
                    "units": "2000",
                    "price": "110.500",
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                }
            },
            headers={"ClientRequestID": "replace_request_123"},
        )

    @pytest.mark.asyncio
    async def test_update_client_extensions_order_only(self, orders, mock_client):
        """Test updating only order client extensions."""
        client_extensions = ClientExtensions(id="my_order_id", tag="strategy_v1", comment="Breakout trade")

        await orders.put_order_client_extensions("101-001-123456-001", "12345", client_extensions=client_extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345/clientExtensions", json_data={"clientExtensions": {"id": "my_order_id", "tag": "strategy_v1", "comment": "Breakout trade"}})

    @pytest.mark.asyncio
    async def test_update_client_extensions_trade_only(self, orders, mock_client):
        """Test updating only trade client extensions."""
        trade_extensions = ClientExtensions(id="trade_tracking_456", tag="momentum", comment="Following trend")

        await orders.put_order_client_extensions("101-001-123456-001", "98765", trade_client_extensions=trade_extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/98765/clientExtensions", json_data={"tradeClientExtensions": {"id": "trade_tracking_456", "tag": "momentum", "comment": "Following trend"}})

    @pytest.mark.asyncio
    async def test_update_client_extensions_both(self, orders, mock_client):
        """Test updating both order and trade client extensions."""
        order_extensions = ClientExtensions(id="order_123", tag="scalping", comment="Quick trade")
        trade_extensions = ClientExtensions(id="trade_123", tag="scalping_result", comment="Filled order")

        await orders.put_order_client_extensions("101-001-123456-001", "55555", client_extensions=order_extensions, trade_client_extensions=trade_extensions)

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/orders/55555/clientExtensions",
            json_data={
                "clientExtensions": {"id": "order_123", "tag": "scalping", "comment": "Quick trade"},
                "tradeClientExtensions": {"id": "trade_123", "tag": "scalping_result", "comment": "Filled order"},
            },
        )

    @pytest.mark.asyncio
    async def test_update_client_extensions_with_client_id(self, orders, mock_client):
        """Test updating extensions using @clientID format."""
        extensions = ClientExtensions(id="updated_id", tag="revised")

        await orders.put_order_client_extensions("101-001-123456-001", "@client_order_789", client_extensions=extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/@client_order_789/clientExtensions", json_data={"clientExtensions": {"id": "updated_id", "tag": "revised"}})

    @pytest.mark.asyncio
    async def test_update_client_extensions_no_extensions_raises_error(self, orders, mock_client):
        """Test that ValueError is raised when no extensions provided."""
        with pytest.raises(ValueError, match="Must provide at least one set of client extensions"):
            await orders.put_order_client_extensions("101-001-123456-001", "12345")

    @pytest.mark.asyncio
    async def test_replace_complex_order_request(self, orders, mock_client):
        """Test replacing order with complex order request including TP/SL."""
        from datetime import datetime

        from fivetwenty.models import StopLossDetails, TakeProfitDetails, TimeInForce, TrailingStopLossDetails

        order_request = LimitOrderRequest(
            instrument="EUR_USD",
            units=Decimal("10000"),
            price=Decimal("1.15000"),
            time_in_force=TimeInForce.GTD,
            gtd_time=datetime.fromisoformat("2024-12-31T23:59:59"),
            take_profit_on_fill=TakeProfitDetails(price=Decimal("1.16000")),
            stop_loss_on_fill=StopLossDetails(price=Decimal("1.14000"), guaranteed=False),
            trailing_stop_loss_on_fill=TrailingStopLossDetails(distance=Decimal("0.00100")),
        )

        await orders.put_order("101-001-123456-001", "99999", order_request, client_request_id="complex_replace")

        mock_client._request.assert_called_once_with(
            "PUT",
            "/accounts/101-001-123456-001/orders/99999",
            json_data={
                "order": {
                    "type": "LIMIT",
                    "instrument": "EUR_USD",
                    "units": "10000",
                    "price": "1.15000",
                    "timeInForce": "GTD",
                    "gtdTime": "2024-12-31T23:59:59",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                    "takeProfitOnFill": {"price": "1.16000", "timeInForce": "GTC"},
                    "stopLossOnFill": {"price": "1.14000", "timeInForce": "GTC", "guaranteed": False},
                    "trailingStopLossOnFill": {"distance": "0.00100", "timeInForce": "GTC"},
                }
            },
            headers={"ClientRequestID": "complex_replace"},
        )

    @pytest.mark.asyncio
    async def test_post_order_core_method(self, orders, mock_client):
        """Test the core post_order method with various order types."""
        from fivetwenty.models import LimitOrderRequest

        # Test with LimitOrderRequest
        limit_order = LimitOrderRequest(instrument="EUR_USD", units="1000", price="1.10000", timeInForce="GTC")

        result = await orders.post_order(account_id="101-001-123456-001", order_request=limit_order, client_request_id="core-test-001")

        mock_client._request.assert_called_once_with(
            "POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "timeInForce": "GTC", "positionFill": "DEFAULT", "triggerCondition": "DEFAULT"}}, timeout=None, headers={"ClientRequestID": "core-test-001"}
        )
        assert "orderCreateTransaction" in result
        assert result["lastTransactionID"] == "12346"

    @pytest.mark.asyncio
    async def test_post_order_without_client_request_id(self, orders, mock_client):
        """Test post_order without client request ID."""
        from fivetwenty.models import MarketOrderRequest

        market_order = MarketOrderRequest(instrument="EUR_USD", units="500")

        await orders.post_order(account_id="101-001-123456-001", order_request=market_order)

        mock_client._request.assert_called_once_with("POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "MARKET", "instrument": "EUR_USD", "units": "500", "timeInForce": "FOK", "positionFill": "DEFAULT"}}, timeout=None, headers={})

    @pytest.mark.asyncio
    async def test_precision_cache_functionality(self, orders, mock_client):
        """Test the internal precision caching mechanism."""
        # Mock the accounts endpoint for instrument lookup
        mock_instruments = [MagicMock()]
        mock_instruments[0].display_precision = 5
        mock_client.accounts.get_account_instruments = AsyncMock(return_value={"instruments": mock_instruments})

        # First call should fetch from API
        precision1 = await orders._get_precision("101-001-123456-001", "EUR_USD")
        assert precision1 == 5

        # Second call should use cache (accounts endpoint shouldn't be called again)
        mock_client.accounts.get_account_instruments.reset_mock()
        precision2 = await orders._get_precision("101-001-123456-001", "EUR_USD")
        assert precision2 == 5

        # Verify cache was used (no second API call)
        mock_client.accounts.get_account_instruments.assert_not_called()

    @pytest.mark.asyncio
    async def test_precision_cache_instrument_not_found(self, orders, mock_client):
        """Test precision cache when instrument is not found."""
        # Mock empty response
        mock_client.accounts.get_account_instruments = AsyncMock(return_value={"instruments": []})

        with pytest.raises(ValueError, match="Instrument TEST_INVALID not found"):
            await orders._get_precision("101-001-123456-001", "TEST_INVALID")

    @pytest.mark.asyncio
    async def test_convenience_method_uses_precision_cache(self, orders, mock_client):
        """Test that convenience methods properly use the precision cache."""
        # Pre-populate cache to avoid API call (use valid instrument)
        orders._precision_cache["EUR_USD"] = 4

        await orders.post_limit_order(
            account_id="101-001-123456-001",
            instrument="EUR_USD",
            units=1000,
            price=Decimal("1.23456789"),  # Should be quantized to 4 decimal places
        )

        # Verify the price was properly quantized
        mock_client._request.assert_called_once()
        call_args = mock_client._request.call_args
        order_data = call_args[1]["json_data"]["order"]
        assert order_data["price"] == "1.2346"  # Quantized to 4 decimal places


class TestOrderConvenienceMethods:
    """Test suite for order convenience methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()

        # Create a side effect function that returns appropriate responses based on the request
        async def mock_request(method, path, **kwargs):
            mock_response = MagicMock()

            # For POST /accounts/{id}/orders - order creation
            if method == "POST" and "/orders" in path:
                mock_response.json.return_value = {
                    "orderCreateTransaction": {
                        "id": "12345",
                        "type": "MARKET_ORDER",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12345",
                        "requestID": "12345",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "timeInForce": "FOK",
                        "positionFill": "DEFAULT",
                        "reason": "CLIENT_ORDER",
                    },
                    "orderFillTransaction": {
                        "id": "12346",
                        "type": "ORDER_FILL",
                        "time": "2024-01-01T00:00:00.000000000Z",
                        "userID": 1,
                        "accountID": "101-001-123456-001",
                        "batchID": "12345",
                        "requestID": "12345",
                        "orderID": "12345",
                        "instrument": "EUR_USD",
                        "units": "1000",
                        "price": "1.10000",
                        "pl": "0.0000",
                        "financing": "0.0000",
                        "commission": "0.0000",
                        "accountBalance": "100000.0000",
                        "reason": "MARKET_ORDER",
                    },
                    "relatedTransactionIDs": ["12345", "12346"],
                    "lastTransactionID": "12346",
                }
            else:
                mock_response.json.return_value = {"mock": "data"}

            return mock_response

        client._request = AsyncMock(side_effect=mock_request)
        return client

    @pytest.fixture
    def orders(self, mock_client):
        """Create OrderEndpoints instance with mock client."""
        orders_endpoint = OrderEndpoints(mock_client)
        # Mock the precision cache to avoid instrument lookup
        orders_endpoint._precision_cache = {"EUR_USD": 5, "GBP_USD": 5, "USD_JPY": 3}
        return orders_endpoint

    @pytest.mark.asyncio
    async def test_post_market_order_basic(self, orders, mock_client):
        """Test basic market order creation."""
        result = await orders.post_market_order(account_id="101-001-123456-001", instrument="EUR_USD", units=1000)

        # Verify the request was made correctly
        mock_client._request.assert_called_once_with("POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "MARKET", "instrument": "EUR_USD", "units": "1000", "timeInForce": "FOK", "positionFill": "DEFAULT"}}, timeout=None, headers={})

        # Verify response is properly parsed
        assert "orderCreateTransaction" in result
        assert result["lastTransactionID"] == "12346"

    @pytest.mark.asyncio
    async def test_post_market_order_with_tp_sl(self, orders, mock_client):
        """Test market order with take profit and stop loss."""
        await orders.post_market_order(account_id="101-001-123456-001", instrument="EUR_USD", units=1000, take_profit=Decimal("1.1100"), stop_loss=Decimal("1.0900"), client_request_id="market-order-001")

        # Verify the request includes TP/SL and client request ID
        mock_client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={"order": {"type": "MARKET", "instrument": "EUR_USD", "units": "1000", "timeInForce": "FOK", "positionFill": "DEFAULT", "takeProfitOnFill": {"price": "1.11000", "timeInForce": "GTC"}, "stopLossOnFill": {"price": "1.09000", "timeInForce": "GTC", "guaranteed": False}}},
            timeout=None,
            headers={"ClientRequestID": "market-order-001"},
        )

    @pytest.mark.asyncio
    async def test_post_limit_order_basic(self, orders, mock_client):
        """Test basic limit order creation."""
        await orders.post_limit_order(account_id="101-001-123456-001", instrument="EUR_USD", units=1000, price=Decimal("1.1000"))

        mock_client._request.assert_called_once_with("POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "timeInForce": "GTC", "positionFill": "DEFAULT", "triggerCondition": "DEFAULT"}}, timeout=None, headers={})

    @pytest.mark.asyncio
    async def test_post_limit_order_with_tp_sl(self, orders, mock_client):
        """Test limit order with take profit and stop loss."""
        await orders.post_limit_order(account_id="101-001-123456-001", instrument="GBP_USD", units=500, price=Decimal("1.2500"), time_in_force="IOC", take_profit=Decimal("1.2600"), stop_loss=Decimal("1.2400"), client_request_id="limit-order-001")

        mock_client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={
                "order": {
                    "type": "LIMIT",
                    "instrument": "GBP_USD",
                    "units": "500",
                    "price": "1.25000",
                    "timeInForce": "IOC",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                    "takeProfitOnFill": {"price": "1.26000", "timeInForce": "GTC"},
                    "stopLossOnFill": {"price": "1.24000", "timeInForce": "GTC", "guaranteed": False},
                }
            },
            timeout=None,
            headers={"ClientRequestID": "limit-order-001"},
        )

    @pytest.mark.asyncio
    async def test_post_stop_order_basic(self, orders, mock_client):
        """Test basic stop order creation."""
        await orders.post_stop_order(account_id="101-001-123456-001", instrument="EUR_USD", units=1000, price=Decimal("1.1100"))

        mock_client._request.assert_called_once_with("POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "STOP", "instrument": "EUR_USD", "units": "1000", "price": "1.11000", "timeInForce": "GTC", "positionFill": "DEFAULT", "triggerCondition": "DEFAULT"}}, timeout=None, headers={})

    @pytest.mark.asyncio
    async def test_post_stop_order_with_price_bound_and_tp_sl(self, orders, mock_client):
        """Test stop order with price bound, take profit and stop loss."""
        await orders.post_stop_order(account_id="101-001-123456-001", instrument="EUR_USD", units=1000, price=Decimal("1.1100"), price_bound=Decimal("1.1110"), time_in_force="GFD", take_profit=Decimal("1.1150"), stop_loss=Decimal("1.1050"), client_request_id="stop-order-001")

        mock_client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={
                "order": {
                    "type": "STOP",
                    "instrument": "EUR_USD",
                    "units": "1000",
                    "price": "1.11000",
                    "priceBound": "1.11100",
                    "timeInForce": "GFD",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                    "takeProfitOnFill": {"price": "1.11500", "timeInForce": "GTC"},
                    "stopLossOnFill": {"price": "1.10500", "timeInForce": "GTC", "guaranteed": False},
                }
            },
            timeout=None,
            headers={"ClientRequestID": "stop-order-001"},
        )

    @pytest.mark.asyncio
    async def test_post_market_if_touched_order_basic(self, orders, mock_client):
        """Test basic market-if-touched order creation."""
        await orders.post_market_if_touched_order(account_id="101-001-123456-001", instrument="GBP_USD", units=750, price=Decimal("1.2400"))

        mock_client._request.assert_called_once_with("POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "MARKET_IF_TOUCHED", "instrument": "GBP_USD", "units": "750", "price": "1.24000", "timeInForce": "GTC", "positionFill": "DEFAULT", "triggerCondition": "DEFAULT"}}, timeout=None, headers={})

    @pytest.mark.asyncio
    async def test_post_market_if_touched_order_with_price_bound_and_tp_sl(self, orders, mock_client):
        """Test MIT order with price bound, take profit and stop loss."""
        await orders.post_market_if_touched_order(account_id="101-001-123456-001", instrument="GBP_USD", units=750, price=Decimal("1.2400"), price_bound=Decimal("1.2390"), time_in_force="GTD", take_profit=Decimal("1.2500"), stop_loss=Decimal("1.2350"), client_request_id="mit-order-001")

        mock_client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={
                "order": {
                    "type": "MARKET_IF_TOUCHED",
                    "instrument": "GBP_USD",
                    "units": "750",
                    "price": "1.24000",
                    "priceBound": "1.23900",
                    "timeInForce": "GTD",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                    "takeProfitOnFill": {"price": "1.25000", "timeInForce": "GTC"},
                    "stopLossOnFill": {"price": "1.23500", "timeInForce": "GTC", "guaranteed": False},
                }
            },
            timeout=None,
            headers={"ClientRequestID": "mit-order-001"},
        )

    @pytest.mark.asyncio
    async def test_convenience_method_price_quantization(self, orders, mock_client):
        """Test that convenience methods properly quantize prices based on instrument precision."""
        # Test with USD_JPY which has 3 decimal places
        await orders.post_limit_order(
            account_id="101-001-123456-001",
            instrument="USD_JPY",
            units=1000,
            price=Decimal("110.12345"),  # Should be quantized to 110.123
        )

        mock_client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={
                "order": {
                    "type": "LIMIT",
                    "instrument": "USD_JPY",
                    "units": "1000",
                    "price": "110.123",  # Quantized to 3 decimal places
                    "timeInForce": "GTC",
                    "positionFill": "DEFAULT",
                    "triggerCondition": "DEFAULT",
                }
            },
            timeout=None,
            headers={},
        )


def _response_client(payload):
    """Create a mock client whose _request returns the given JSON payload."""
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = payload
    client._request = AsyncMock(return_value=mock_response)
    return client


_BASE_ORDER = {"id": "42", "createTime": "2024-01-01T00:00:00.000000000Z", "state": "PENDING"}
_BASE_TXN = {"id": "77", "time": "2024-01-01T00:00:00.000000000Z", "userID": 1, "accountID": "101-001-123456-001", "batchID": "77", "requestID": "77"}

_ORDER_PAYLOADS = [
    ({**_BASE_ORDER, "type": "MARKET", "instrument": "EUR_USD", "units": "1000", "timeInForce": "FOK", "positionFill": "DEFAULT"}, MarketOrder),
    ({**_BASE_ORDER, "type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "timeInForce": "GTC"}, LimitOrder),
    ({**_BASE_ORDER, "type": "STOP", "instrument": "EUR_USD", "units": "-500", "price": "1.09000", "timeInForce": "GTC"}, StopOrder),
    ({**_BASE_ORDER, "type": "MARKET_IF_TOUCHED", "instrument": "GBP_USD", "units": "750", "price": "1.24000", "timeInForce": "GTC"}, MarketIfTouchedOrder),
    ({**_BASE_ORDER, "type": "TAKE_PROFIT", "tradeID": "10", "price": "1.12000", "timeInForce": "GTC"}, TakeProfitOrder),
    ({**_BASE_ORDER, "type": "STOP_LOSS", "tradeID": "10", "price": "1.08000", "timeInForce": "GTC"}, StopLossOrder),
    ({**_BASE_ORDER, "type": "GUARANTEED_STOP_LOSS", "tradeID": "10", "price": "1.07000", "timeInForce": "GTC"}, GuaranteedStopLossOrder),
    ({**_BASE_ORDER, "type": "TRAILING_STOP_LOSS", "tradeID": "10", "distance": "0.00100", "timeInForce": "GTC"}, TrailingStopLossOrder),
    ({**_BASE_ORDER, "type": "FIXED_PRICE", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "tradeState": "OPEN"}, FixedPriceOrder),
]

_ORDER_TXN_PAYLOADS = [
    ({**_BASE_TXN, "type": "MARKET_ORDER", "instrument": "EUR_USD", "units": "1000", "timeInForce": "FOK", "positionFill": "DEFAULT"}, MarketOrderTransaction),
    ({**_BASE_TXN, "type": "LIMIT_ORDER", "instrument": "EUR_USD", "units": "1000", "price": "1.10000"}, LimitOrderTransaction),
    ({**_BASE_TXN, "type": "STOP_ORDER", "instrument": "EUR_USD", "units": "-500", "price": "1.09000"}, StopOrderTransaction),
    ({**_BASE_TXN, "type": "MARKET_IF_TOUCHED_ORDER", "instrument": "GBP_USD", "units": "750", "price": "1.24000"}, MarketIfTouchedOrderTransaction),
    ({**_BASE_TXN, "type": "TAKE_PROFIT_ORDER", "tradeID": "10", "price": "1.12000"}, TakeProfitOrderTransaction),
    ({**_BASE_TXN, "type": "STOP_LOSS_ORDER", "tradeID": "10", "price": "1.08000"}, StopLossOrderTransaction),
    ({**_BASE_TXN, "type": "GUARANTEED_STOP_LOSS_ORDER", "tradeID": "10", "price": "1.07000", "guaranteedExecutionPremium": "0.50"}, GuaranteedStopLossOrderTransaction),
    ({**_BASE_TXN, "type": "TRAILING_STOP_LOSS_ORDER", "tradeID": "10", "distance": "0.00100"}, TrailingStopLossOrderTransaction),
]

_ORDER_REJECT_TXN_PAYLOADS = [
    ({**_BASE_TXN, "type": "MARKET_ORDER_REJECT", "instrument": "EUR_USD", "units": "1000", "rejectReason": "INSUFFICIENT_MARGIN"}, MarketOrderRejectTransaction),
    ({**_BASE_TXN, "type": "LIMIT_ORDER_REJECT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "rejectReason": "INSUFFICIENT_MARGIN"}, LimitOrderRejectTransaction),
    ({**_BASE_TXN, "type": "STOP_ORDER_REJECT", "instrument": "EUR_USD", "units": "-500", "price": "1.09000", "rejectReason": "INSUFFICIENT_MARGIN"}, StopOrderRejectTransaction),
    ({**_BASE_TXN, "type": "MARKET_IF_TOUCHED_ORDER_REJECT", "instrument": "GBP_USD", "units": "750", "price": "1.24000", "rejectReason": "INSUFFICIENT_MARGIN"}, MarketIfTouchedOrderRejectTransaction),
    ({**_BASE_TXN, "type": "TAKE_PROFIT_ORDER_REJECT", "tradeID": "10", "price": "1.12000", "rejectReason": "TRADE_DOESNT_EXIST"}, TakeProfitOrderRejectTransaction),
    ({**_BASE_TXN, "type": "STOP_LOSS_ORDER_REJECT", "tradeID": "10", "price": "1.08000", "rejectReason": "TRADE_DOESNT_EXIST"}, StopLossOrderRejectTransaction),
    ({**_BASE_TXN, "type": "GUARANTEED_STOP_LOSS_ORDER_REJECT", "tradeID": "10", "price": "1.07000", "rejectReason": "TRADE_DOESNT_EXIST"}, GuaranteedStopLossOrderRejectTransaction),
    ({**_BASE_TXN, "type": "TRAILING_STOP_LOSS_ORDER_REJECT", "tradeID": "10", "distance": "0.00100", "rejectReason": "TRADE_DOESNT_EXIST"}, TrailingStopLossOrderRejectTransaction),
]


class TestOrderParsers:
    """Test the private discriminator-based parsers."""

    @pytest.fixture
    def orders(self):
        """Create OrderEndpoints with an inert client (parsers are pure)."""
        return OrderEndpoints(MagicMock())

    @pytest.mark.parametrize(("payload", "expected_cls"), _ORDER_PAYLOADS, ids=[p[0]["type"] for p in _ORDER_PAYLOADS])
    def test_parse_order_types(self, orders, payload, expected_cls):
        """Test that _parse_order dispatches to the correct Order model."""
        result = orders._parse_order(payload)
        assert isinstance(result, expected_cls)
        assert result.id == "42"

    def test_parse_order_unknown_type_raises(self, orders):
        """Test that an unknown order type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown order type: MYSTERY"):
            orders._parse_order({**_BASE_ORDER, "type": "MYSTERY"})

    def test_parse_order_missing_type_raises(self, orders):
        """Test that a payload without a type discriminator raises ValueError."""
        with pytest.raises(ValueError, match="Unknown order type: None"):
            orders._parse_order(dict(_BASE_ORDER))

    @pytest.mark.parametrize(("payload", "expected_cls"), _ORDER_TXN_PAYLOADS, ids=[p[0]["type"] for p in _ORDER_TXN_PAYLOADS])
    def test_parse_order_transaction_types(self, orders, payload, expected_cls):
        """Test that _parse_order_transaction dispatches to the correct model."""
        result = orders._parse_order_transaction(payload)
        assert isinstance(result, expected_cls)
        assert result.id == "77"

    def test_parse_order_transaction_unknown_type_raises(self, orders):
        """Test that an unknown transaction type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown order transaction type: ORDER_FILL"):
            orders._parse_order_transaction({**_BASE_TXN, "type": "ORDER_FILL"})

    @pytest.mark.parametrize(("payload", "expected_cls"), _ORDER_REJECT_TXN_PAYLOADS, ids=[p[0]["type"] for p in _ORDER_REJECT_TXN_PAYLOADS])
    def test_parse_order_reject_transaction_types(self, orders, payload, expected_cls):
        """Test that _parse_order_reject_transaction dispatches to the correct model."""
        result = orders._parse_order_reject_transaction(payload)
        assert isinstance(result, expected_cls)
        assert result.reject_reason is not None

    def test_parse_order_reject_transaction_unknown_type_raises(self, orders):
        """Test that an unknown reject transaction type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown order reject transaction type: LIMIT_ORDER"):
            orders._parse_order_reject_transaction({**_BASE_TXN, "type": "LIMIT_ORDER"})


class TestOrderResponseBranches:
    """Test optional response-transaction parsing branches."""

    @pytest.mark.asyncio
    async def test_post_order_parses_cancel_and_reissue_transactions(self):
        """Test post_order handling of cancel, reissue, and reissue-reject payloads."""
        payload = {
            "orderCreateTransaction": _ORDER_TXN_PAYLOADS[1][0],  # LIMIT_ORDER
            "orderCancelTransaction": {**_BASE_TXN, "type": "ORDER_CANCEL", "orderID": "42", "reason": "CLIENT_REQUEST"},
            "orderReissueTransaction": _ORDER_TXN_PAYLOADS[0][0],  # MARKET_ORDER
            "orderReissueRejectTransaction": _ORDER_REJECT_TXN_PAYLOADS[0][0],  # MARKET_ORDER_REJECT
            "lastTransactionID": "80",
        }
        client = _response_client(payload)
        orders = OrderEndpoints(client)

        # Pass a raw dict to exercise the dict passthrough branch
        result = await orders.post_order("101-001-123456-001", {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000"})

        client._request.assert_called_once_with(
            "POST",
            "/accounts/101-001-123456-001/orders",
            json_data={"order": {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000"}},
            timeout=None,
            headers={},
        )
        assert isinstance(result["orderCreateTransaction"], LimitOrderTransaction)
        assert isinstance(result["orderCancelTransaction"], OrderCancelTransaction)
        assert isinstance(result["orderReissueTransaction"], MarketOrderTransaction)
        assert isinstance(result["orderReissueRejectTransaction"], MarketOrderRejectTransaction)
        assert "relatedTransactionIDs" not in result
        assert result["lastTransactionID"] == "80"

    @pytest.mark.asyncio
    async def test_put_order_parses_fill_reissue_and_replacing_cancel(self):
        """Test put_order handling of fill, reissue, reject, and replacing-cancel payloads."""
        fill_txn = {**_BASE_TXN, "type": "ORDER_FILL", "orderID": "42", "instrument": "EUR_USD", "units": "1000", "price": "1.10000"}
        payload = {
            "orderFillTransaction": fill_txn,
            "orderReissueTransaction": _ORDER_TXN_PAYLOADS[2][0],  # STOP_ORDER
            "orderReissueRejectTransaction": _ORDER_REJECT_TXN_PAYLOADS[1][0],  # LIMIT_ORDER_REJECT
            "replacingOrderCancelTransaction": {**_BASE_TXN, "type": "ORDER_CANCEL", "orderID": "42", "reason": "CLIENT_REQUEST_REPLACED"},
            "relatedTransactionIDs": ["77", "78"],
            "lastTransactionID": "78",
        }
        client = _response_client(payload)
        orders = OrderEndpoints(client)

        result = await orders.put_order("101-001-123456-001", "42", {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.11000"})

        assert isinstance(result["orderFillTransaction"], OrderFillTransaction)
        assert isinstance(result["orderReissueTransaction"], StopOrderTransaction)
        assert isinstance(result["orderReissueRejectTransaction"], LimitOrderRejectTransaction)
        assert isinstance(result["replacingOrderCancelTransaction"], OrderCancelTransaction)
        assert result["relatedTransactionIDs"] == ["77", "78"]
        assert "orderCreateTransaction" not in result

    @pytest.mark.asyncio
    async def test_cancel_order_minimal_response(self):
        """Test cancel_order when the response has only lastTransactionID."""
        client = _response_client({"lastTransactionID": "90"})
        orders = OrderEndpoints(client)

        result = await orders.cancel_order("101-001-123456-001", "42")

        assert result["lastTransactionID"] == "90"
        assert "orderCancelTransaction" not in result
        assert "relatedTransactionIDs" not in result

    @pytest.mark.asyncio
    async def test_put_order_client_extensions_minimal_response(self):
        """Test put_order_client_extensions when the response has only lastTransactionID."""
        client = _response_client({"lastTransactionID": "91"})
        orders = OrderEndpoints(client)

        result = await orders.put_order_client_extensions("101-001-123456-001", "42", client_extensions=ClientExtensions(id="x"))

        assert result["lastTransactionID"] == "91"
        assert "orderClientExtensionsModifyTransaction" not in result

    @pytest.mark.asyncio
    async def test_get_orders_with_ids_filter(self):
        """Test get_orders joins explicit order IDs into the ids param."""
        client = _response_client({"orders": [], "lastTransactionID": "92"})
        orders = OrderEndpoints(client)

        result = await orders.get_orders("101-001-123456-001", ids=["12345", "12346"])

        client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders", params={"state": "PENDING", "count": 50, "ids": "12345,12346"})
        assert result["orders"] == []
        assert result["lastTransactionID"] == "92"

    @pytest.mark.asyncio
    async def test_get_orders_count_outside_oanda_range_raises(self):
        """Test get_orders enforces OANDA's count range."""
        client = _response_client({"orders": [], "lastTransactionID": "92"})
        orders = OrderEndpoints(client)

        with pytest.raises(ValueError, match="Count must be between 1 and 500"):
            await orders.get_orders("101-001-123456-001", count=501)

        client._request.assert_not_called()

    @pytest.mark.asyncio
    async def test_post_order_minimal_response(self):
        """Test post_order when the response has only lastTransactionID."""
        client = _response_client({"lastTransactionID": "93"})
        orders = OrderEndpoints(client)

        result = await orders.post_order("101-001-123456-001", {"type": "MARKET", "instrument": "EUR_USD", "units": "1"})

        assert result["lastTransactionID"] == "93"
        assert "orderCreateTransaction" not in result

    @pytest.mark.asyncio
    async def test_put_order_minimal_response(self):
        """Test put_order when the response has only lastTransactionID."""
        client = _response_client({"lastTransactionID": "94"})
        orders = OrderEndpoints(client)

        result = await orders.put_order("101-001-123456-001", "42", {"type": "MARKET", "instrument": "EUR_USD", "units": "1"})

        assert result["lastTransactionID"] == "94"
        assert "relatedTransactionIDs" not in result
