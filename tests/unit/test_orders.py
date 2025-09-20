"""Unit tests for enhanced order management endpoints."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from fivetwenty.endpoints.orders import OrderEndpoints
from fivetwenty.models import OrderResponse


class TestEnhancedOrderEndpoints:
    """Test suite for enhanced order management functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async client."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"orderCreateTransaction": {"id": "12345", "type": "ORDER_CREATE", "instrument": "EUR_USD", "units": "1000"}, "lastTransactionID": "12345"}
        client._request = AsyncMock(return_value=mock_response)
        return client

    @pytest.fixture
    def orders(self, mock_client):
        """Create OrderEndpoints instance with mock client."""
        return OrderEndpoints(mock_client)

    @pytest.mark.asyncio
    async def test_get_orders_basic(self, orders, mock_client):
        """Test basic order listing."""
        mock_client._request.return_value.json.return_value = {"orders": [{"id": "12345", "instrument": "EUR_USD", "state": "PENDING"}, {"id": "12346", "instrument": "GBP_USD", "state": "PENDING"}]}

        result = await orders.get_orders("101-001-123456-001")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders", params={"state": "PENDING", "count": 50})
        assert len(result) == 2
        assert result[0]["id"] == "12345"

    @pytest.mark.asyncio
    async def test_get_orders_with_filters(self, orders, mock_client):
        """Test order listing with filters."""
        mock_client._request.return_value.json.return_value = {"orders": []}

        await orders.get_orders("101-001-123456-001", state="FILLED", instrument="EUR_USD", count=25, before_id="12340")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders", params={"state": "FILLED", "count": 25, "instrument": "EUR_USD", "beforeID": "12340"})

    @pytest.mark.asyncio
    async def test_get_order(self, orders, mock_client):
        """Test getting specific order details."""
        mock_client._request.return_value.json.return_value = {"order": {"id": "12345", "instrument": "EUR_USD", "state": "PENDING", "type": "LIMIT"}, "lastTransactionID": "6789"}

        result = await orders.get_order("101-001-123456-001", "12345")

        mock_client._request.assert_called_once_with("GET", "/accounts/101-001-123456-001/orders/12345")
        assert result["order"]["id"] == "12345"
        assert result["order"]["instrument"] == "EUR_USD"
        assert result["lastTransactionID"] == "6789"

    @pytest.mark.asyncio
    async def test_cancel_order(self, orders, mock_client):
        """Test order cancellation."""
        mock_client._request.return_value.json.return_value = {"orderCancelTransaction": {"id": "12346", "type": "ORDER_CANCEL", "orderID": "12345"}}

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
        mock_client._request.return_value.json.return_value = {"orderCancelTransaction": {"id": "12346", "type": "ORDER_CANCEL", "orderID": "12345"}}

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
        order_request = {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.12000", "timeInForce": "GTC"}

        await orders.put_order("101-001-123456-001", "12345", order_request)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345", json_data={"order": order_request}, headers={})

    @pytest.mark.asyncio
    async def test_replace_order_with_client_id(self, orders, mock_client):
        """Test replacing an order using @clientID format."""
        order_request = {"type": "STOP", "instrument": "GBP_USD", "units": "-500", "price": "1.25000", "timeInForce": "GTC"}

        await orders.put_order("101-001-123456-001", "@my_custom_order_123", order_request)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/@my_custom_order_123", json_data={"order": order_request}, headers={})

    @pytest.mark.asyncio
    async def test_replace_order_with_client_request_id(self, orders, mock_client):
        """Test replacing an order with client request ID."""
        order_request = {"type": "MARKET_IF_TOUCHED", "instrument": "USD_JPY", "units": "2000", "price": "110.500", "timeInForce": "GTC"}

        await orders.put_order("101-001-123456-001", "67890", order_request, client_request_id="replace_request_123")

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/67890", json_data={"order": order_request}, headers={"ClientRequestID": "replace_request_123"})

    @pytest.mark.asyncio
    async def test_update_client_extensions_order_only(self, orders, mock_client):
        """Test updating only order client extensions."""
        client_extensions = {"id": "my_order_id", "tag": "strategy_v1", "comment": "Breakout trade"}

        await orders.put_order_client_extensions("101-001-123456-001", "12345", client_extensions=client_extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/12345/clientExtensions", json_data={"clientExtensions": client_extensions})

    @pytest.mark.asyncio
    async def test_update_client_extensions_trade_only(self, orders, mock_client):
        """Test updating only trade client extensions."""
        trade_extensions = {"id": "trade_tracking_456", "tag": "momentum", "comment": "Following trend"}

        await orders.put_order_client_extensions("101-001-123456-001", "98765", trade_client_extensions=trade_extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/98765/clientExtensions", json_data={"tradeClientExtensions": trade_extensions})

    @pytest.mark.asyncio
    async def test_update_client_extensions_both(self, orders, mock_client):
        """Test updating both order and trade client extensions."""
        order_extensions = {"id": "order_123", "tag": "scalping", "comment": "Quick trade"}
        trade_extensions = {"id": "trade_123", "tag": "scalping_result", "comment": "Filled order"}

        await orders.put_order_client_extensions("101-001-123456-001", "55555", client_extensions=order_extensions, trade_client_extensions=trade_extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/55555/clientExtensions", json_data={"clientExtensions": order_extensions, "tradeClientExtensions": trade_extensions})

    @pytest.mark.asyncio
    async def test_update_client_extensions_with_client_id(self, orders, mock_client):
        """Test updating extensions using @clientID format."""
        extensions = {"id": "updated_id", "tag": "revised"}

        await orders.put_order_client_extensions("101-001-123456-001", "@client_order_789", client_extensions=extensions)

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/@client_order_789/clientExtensions", json_data={"clientExtensions": extensions})

    @pytest.mark.asyncio
    async def test_update_client_extensions_no_extensions_raises_error(self, orders, mock_client):
        """Test that ValueError is raised when no extensions provided."""
        with pytest.raises(ValueError, match="Must provide at least one set of client extensions"):
            await orders.put_order_client_extensions("101-001-123456-001", "12345")

    @pytest.mark.asyncio
    async def test_replace_complex_order_request(self, orders, mock_client):
        """Test replacing order with complex order request including TP/SL."""
        order_request = {
            "type": "LIMIT",
            "instrument": "EUR_USD",
            "units": "10000",
            "price": "1.15000",
            "timeInForce": "GTD",
            "gtdTime": "2024-12-31T23:59:59Z",
            "takeProfitOnFill": {"price": "1.16000", "timeInForce": "GTC"},
            "stopLossOnFill": {"price": "1.14000", "timeInForce": "GTC", "guaranteed": False},
            "trailingStopLossOnFill": {"distance": "0.00100", "timeInForce": "GTC"},
        }

        await orders.put_order("101-001-123456-001", "99999", order_request, client_request_id="complex_replace")

        mock_client._request.assert_called_once_with("PUT", "/accounts/101-001-123456-001/orders/99999", json_data={"order": order_request}, headers={"ClientRequestID": "complex_replace"})

    @pytest.mark.asyncio
    async def test_post_order_core_method(self, orders, mock_client):
        """Test the core post_order method with various order types."""
        from fivetwenty.models import LimitOrderRequest

        mock_client._request.return_value.json.return_value = {"orderCreateTransaction": {"id": "12345"}, "lastTransactionID": "12345"}

        # Test with LimitOrderRequest
        limit_order = LimitOrderRequest(instrument="EUR_USD", units="1000", price="1.10000", timeInForce="GTC")

        result = await orders.post_order(account_id="101-001-123456-001", order_request=limit_order, client_request_id="core-test-001")

        mock_client._request.assert_called_once_with(
            "POST", "/accounts/101-001-123456-001/orders", json_data={"order": {"type": "LIMIT", "instrument": "EUR_USD", "units": "1000", "price": "1.10000", "timeInForce": "GTC", "positionFill": "DEFAULT", "triggerCondition": "DEFAULT"}}, timeout=None, headers={"ClientRequestID": "core-test-001"}
        )
        assert isinstance(result, OrderResponse)

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
        mock_response = MagicMock()
        mock_response.json.return_value = {"orderCreateTransaction": {"id": "12345", "type": "ORDER_CREATE", "instrument": "EUR_USD", "units": "1000"}, "lastTransactionID": "12345"}
        client._request = AsyncMock(return_value=mock_response)
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
        assert isinstance(result, OrderResponse)

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
