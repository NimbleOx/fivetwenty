"""Tests for order-related models."""

from datetime import datetime, timezone
from decimal import Decimal

from fivetwenty.models import (
    ClientExtensions,
    GuaranteedStopLossOrderRequest,
    InstrumentName,
    LimitOrderRequest,
    MarketIfTouchedOrderRequest,
    MarketOrderRequest,
    OrderPositionFill,
    OrderResponse,
    OrderTriggerCondition,
    OrderType,
    StopLossDetails,
    StopLossOrderRequest,
    StopOrderRequest,
    TakeProfitDetails,
    TakeProfitOrderRequest,
    TimeInForce,
    TrailingStopLossDetails,
    TrailingStopLossOrderRequest,
)


class TestOrderModels:
    """Test order-related models."""

    def test_market_order_request(self) -> None:
        """Test MarketOrderRequest model."""
        order = MarketOrderRequest(instrument=InstrumentName.EUR_USD, units="1000")
        assert order.type == OrderType.MARKET
        assert order.instrument == InstrumentName.EUR_USD
        assert order.units == Decimal("1000")  # Field is now Decimal
        assert order.time_in_force == TimeInForce.FOK
        assert order.position_fill == OrderPositionFill.DEFAULT

    def test_limit_order_request(self) -> None:
        """Test LimitOrderRequest model."""
        order = LimitOrderRequest(instrument=InstrumentName.EUR_USD, units="1000", price="1.1000")
        assert order.type == OrderType.LIMIT
        assert order.instrument == InstrumentName.EUR_USD
        assert order.units == Decimal("1000")  # Field is now Decimal
        assert order.price == Decimal("1.1000")  # PriceValue is now Decimal
        assert order.time_in_force == TimeInForce.GTC
        assert order.position_fill == OrderPositionFill.DEFAULT
        assert order.trigger_condition == OrderTriggerCondition.DEFAULT

    def test_limit_order_request_with_options(self) -> None:
        """Test LimitOrderRequest with optional fields."""
        from fivetwenty.models import ClientExtensions

        client_ext = ClientExtensions(tag="test")
        order = LimitOrderRequest(instrument=InstrumentName.EUR_USD, units="1000", price="1.1000", time_in_force=TimeInForce.GTD, gtd_time="2024-01-02T12:00:00Z", position_fill=OrderPositionFill.REDUCE_ONLY, trigger_condition=OrderTriggerCondition.BID, client_extensions=client_ext)
        assert order.time_in_force == TimeInForce.GTD
        assert order.gtd_time == datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        assert order.position_fill == OrderPositionFill.REDUCE_ONLY
        assert order.trigger_condition == OrderTriggerCondition.BID
        assert order.client_extensions.tag == "test"

    def test_stop_order_request(self) -> None:
        """Test StopOrderRequest model."""
        order = StopOrderRequest(instrument=InstrumentName.EUR_USD, units="-1000", price="1.0950", price_bound="1.0940")
        assert order.type == OrderType.STOP
        assert order.instrument == InstrumentName.EUR_USD
        assert order.units == Decimal("-1000")  # Field is now Decimal
        assert order.price == Decimal("1.0950")
        assert order.price_bound == Decimal("1.0940")
        assert order.time_in_force == TimeInForce.GTC

    def test_take_profit_order_request(self) -> None:
        """Test TakeProfitOrderRequest model."""
        order = TakeProfitOrderRequest(trade_id="123", price="1.1100")
        assert order.type == OrderType.TAKE_PROFIT
        assert order.trade_id == "123"
        assert order.price == Decimal("1.1100")
        assert order.time_in_force == TimeInForce.GTC
        assert order.trigger_condition == OrderTriggerCondition.DEFAULT

    def test_stop_loss_order_request(self) -> None:
        """Test StopLossOrderRequest model."""
        order = StopLossOrderRequest(trade_id="123", price="1.0900")
        assert order.type == OrderType.STOP_LOSS
        assert order.trade_id == "123"
        assert order.price == Decimal("1.0900")
        assert order.distance is None
        assert order.guaranteed is False

    def test_stop_loss_order_request_with_distance(self) -> None:
        """Test StopLossOrderRequest with distance instead of price."""
        order = StopLossOrderRequest(trade_id="123", distance="0.0100", guaranteed=True)
        assert order.trade_id == "123"
        assert order.price is None
        assert order.distance == Decimal("0.0100")  # Field is now Decimal
        assert order.guaranteed is True

    def test_order_response(self) -> None:
        """Test OrderResponse model."""
        response = OrderResponse(last_transaction_id="456", order_create_transaction={"id": "456", "type": "ORDER_CREATE"}, related_transaction_ids=["456"])
        assert response.last_transaction_id == "456"
        assert response.order_create_transaction == {"id": "456", "type": "ORDER_CREATE"}
        assert response.related_transaction_ids == ["456"]


class TestAdvancedOrderModels:
    """Test advanced order-related models."""

    def test_market_if_touched_order_request(self) -> None:
        """Test MarketIfTouchedOrderRequest model."""
        order = MarketIfTouchedOrderRequest(instrument=InstrumentName.EUR_USD, units="1000", price="1.1100", price_bound="1.1110")
        assert order.type == OrderType.MARKET_IF_TOUCHED
        assert order.instrument == InstrumentName.EUR_USD
        assert order.units == Decimal("1000")  # Field is now Decimal
        assert order.price == Decimal("1.1100")
        assert order.price_bound == Decimal("1.1110")
        assert order.time_in_force == TimeInForce.GTC

    def test_trailing_stop_loss_order_request(self) -> None:
        """Test TrailingStopLossOrderRequest model."""
        order = TrailingStopLossOrderRequest(trade_id="123", distance="0.0050")
        assert order.type == OrderType.TRAILING_STOP_LOSS
        assert order.trade_id == "123"
        assert order.distance == Decimal("0.0050")  # Field is now Decimal
        assert order.time_in_force == TimeInForce.GTC
        assert order.trigger_condition == OrderTriggerCondition.DEFAULT

    def test_guaranteed_stop_loss_order_request(self) -> None:
        """Test GuaranteedStopLossOrderRequest model."""
        order = GuaranteedStopLossOrderRequest(trade_id="456", price="1.0900", guaranteed_execution_premium="2.50")
        assert order.type == OrderType.GUARANTEED_STOP_LOSS
        assert order.trade_id == "456"
        assert order.price == Decimal("1.0900")
        assert order.guaranteed_execution_premium == Decimal("2.50")
        assert order.distance is None

    def test_guaranteed_stop_loss_with_distance(self) -> None:
        """Test GuaranteedStopLossOrderRequest with distance."""
        order = GuaranteedStopLossOrderRequest(trade_id="789", distance="0.0100")
        assert order.trade_id == "789"
        assert order.price is None
        assert order.distance == Decimal("0.0100")  # Field is now Decimal


class TestOrderDetailsModels:
    """Test order details and extensions models."""

    def test_client_extensions(self) -> None:
        """Test ClientExtensions model."""
        extensions = ClientExtensions(id="order_123", tag="demo_trade", comment="Test order for demo account")
        assert extensions.id == "order_123"
        assert extensions.tag == "demo_trade"
        assert extensions.comment == "Test order for demo account"

    def test_client_extensions_optional(self) -> None:
        """Test ClientExtensions with optional fields."""
        extensions = ClientExtensions(tag="important")
        assert extensions.id is None
        assert extensions.tag == "important"
        assert extensions.comment is None

    def test_take_profit_details(self) -> None:
        """Test TakeProfitDetails model."""
        tp_details = TakeProfitDetails(price="1.1200", time_in_force=TimeInForce.GTD, gtd_time="2024-01-02T12:00:00Z")
        assert tp_details.price == Decimal("1.1200")
        assert tp_details.time_in_force == TimeInForce.GTD
        assert tp_details.gtd_time == datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        assert tp_details.client_extensions is None

    def test_stop_loss_details(self) -> None:
        """Test StopLossDetails model."""
        sl_details = StopLossDetails(price="1.0900", guaranteed=True)
        assert sl_details.price == Decimal("1.0900")
        assert sl_details.distance is None
        assert sl_details.guaranteed is True
        assert sl_details.time_in_force == TimeInForce.GTC

    def test_stop_loss_details_with_distance(self) -> None:
        """Test StopLossDetails with distance instead of price."""
        sl_details = StopLossDetails(distance="0.0100", guaranteed=False)
        assert sl_details.price is None
        assert sl_details.distance == Decimal("0.0100")  # Field is now Decimal
        assert sl_details.guaranteed is False

    def test_trailing_stop_loss_details(self) -> None:
        """Test TrailingStopLossDetails model."""
        tsl_details = TrailingStopLossDetails(distance="0.0050", time_in_force=TimeInForce.GTD, gtd_time="2024-01-03T12:00:00Z")
        assert tsl_details.distance == Decimal("0.0050")  # Field is now Decimal
        assert tsl_details.time_in_force == TimeInForce.GTD
        assert tsl_details.gtd_time == datetime(2024, 1, 3, 12, 0, 0, tzinfo=timezone.utc)
