"""Tests for order-related models."""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import pytest

from fivetwenty.endpoints.orders import OrderResponse  # noqa: TC001
from fivetwenty.models import (
    ClientExtensions,
    DynamicOrderState,
    FixedPriceOrder,
    FixedPriceOrderReason,
    GuaranteedStopLossOrderReason,
    GuaranteedStopLossOrderRequest,
    InstrumentName,
    LimitOrder,
    LimitOrderReason,
    LimitOrderRequest,
    MarketIfTouchedOrder,
    MarketIfTouchedOrderReason,
    MarketIfTouchedOrderRequest,
    MarketOrder,
    MarketOrderDelayedTradeClose,
    MarketOrderMarginCloseout,
    MarketOrderMarginCloseoutReason,
    MarketOrderPositionCloseout,
    MarketOrderReason,
    MarketOrderRequest,
    MarketOrderTradeClose,
    OrderCancelReason,
    OrderFillReason,
    OrderIdentifier,
    OrderPositionFill,
    OrderState,
    OrderTriggerCondition,
    OrderType,
    StopLossDetails,
    StopLossOrder,
    StopLossOrderReason,
    StopLossOrderRequest,
    StopOrder,
    StopOrderReason,
    StopOrderRequest,
    TakeProfitDetails,
    TakeProfitOrder,
    TakeProfitOrderReason,
    TakeProfitOrderRequest,
    TimeInForce,
    TrailingStopLossDetails,
    TrailingStopLossOrder,
    TrailingStopLossOrderReason,
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
        """Test OrderResponse TypedDict."""
        response: OrderResponse = {"lastTransactionID": "456"}
        assert response["lastTransactionID"] == "456"


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
        """Test GuaranteedStopLossOrderRequest model.

        Note: guaranteed_execution_premium is reported by OANDA on the resulting
        GuaranteedStopLossOrder, not specified by the client on the request.
        """
        order = GuaranteedStopLossOrderRequest(trade_id="456", price="1.0900")
        assert order.type == OrderType.GUARANTEED_STOP_LOSS
        assert order.trade_id == "456"
        assert order.price == Decimal("1.0900")
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


class TestMarketOrderDetailModels:
    """Named coverage for market order detail sub-models."""

    def test_market_order_trade_close(self) -> None:
        """Test MarketOrderTradeClose aliases."""
        payload = {"tradeID": "6", "clientTradeID": "my-trade-6", "units": "ALL"}
        trade_close = MarketOrderTradeClose(**payload)
        assert trade_close.trade_id == payload["tradeID"]
        assert trade_close.client_trade_id == payload["clientTradeID"]
        assert trade_close.units == "ALL"
        assert MarketOrderTradeClose(**trade_close.model_dump(by_alias=True, exclude_none=True)) == trade_close

    def test_market_order_position_closeout(self) -> None:
        """Test MarketOrderPositionCloseout fields."""
        payload = {"instrument": "EUR_USD", "units": "ALL"}
        closeout = MarketOrderPositionCloseout(**payload)
        assert closeout.instrument == InstrumentName.EUR_USD
        assert closeout.units == "ALL"
        assert MarketOrderPositionCloseout(**closeout.model_dump(by_alias=True, exclude_none=True)) == closeout

    def test_market_order_margin_closeout(self) -> None:
        """Test MarketOrderMarginCloseout reason."""
        closeout = MarketOrderMarginCloseout(reason="MARGIN_CHECK_VIOLATION")
        assert closeout.reason == MarketOrderMarginCloseoutReason.MARGIN_CHECK_VIOLATION
        assert MarketOrderMarginCloseout(**closeout.model_dump(by_alias=True, exclude_none=True)) == closeout

    def test_market_order_delayed_trade_close(self) -> None:
        """Test MarketOrderDelayedTradeClose aliases."""
        payload = {"tradeID": "6", "clientTradeID": "my-trade-6", "sourceTransactionID": "5"}
        delayed = MarketOrderDelayedTradeClose(**payload)
        assert delayed.trade_id == payload["tradeID"]
        assert delayed.client_trade_id == payload["clientTradeID"]
        assert delayed.source_transaction_id == payload["sourceTransactionID"]
        assert MarketOrderDelayedTradeClose(**delayed.model_dump(by_alias=True, exclude_none=True)) == delayed

    def test_order_identifier(self) -> None:
        """Test OrderIdentifier aliases."""
        payload = {"orderID": "10", "clientOrderID": "client-10"}
        identifier = OrderIdentifier(**payload)
        assert identifier.order_id == payload["orderID"]
        assert identifier.client_order_id == payload["clientOrderID"]
        assert OrderIdentifier(**identifier.model_dump(by_alias=True, exclude_none=True)) == identifier

    def test_dynamic_order_state(self) -> None:
        """Test DynamicOrderState aliases and Decimal typing."""
        payload = {"id": "10", "trailingStopValue": "1.1000", "triggerDistance": "0.0050", "isTriggerDistanceExact": True}
        state = DynamicOrderState(**payload)
        assert state.id == "10"
        assert state.trailing_stop_value == Decimal("1.1000")
        assert state.trigger_distance == Decimal("0.0050")
        assert isinstance(state.trigger_distance, Decimal)
        assert state.is_trigger_distance_exact is True
        assert DynamicOrderState(**state.model_dump(by_alias=True, exclude_none=True)) == state


class TestOrderStateModels:
    """Named coverage for the complete order state models."""

    def test_market_order(self) -> None:
        """Test MarketOrder with an OANDA-shaped payload."""
        payload = {
            "id": "10",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "FILLED",
            "type": "MARKET",
            "instrument": "EUR_USD",
            "units": "100",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "tradeClose": {"tradeID": "6", "units": "ALL"},
            "fillingTransactionID": "11",
            "filledTime": "2024-01-15T12:00:00.000000000Z",
            "tradeOpenedID": "12",
        }

        order = MarketOrder(**payload)
        assert order.create_time == datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        assert order.state == OrderState.FILLED
        assert order.units == Decimal("100")
        assert isinstance(order.units, Decimal)
        assert order.filling_transaction_id == payload["fillingTransactionID"]
        assert order.trade_opened_id == payload["tradeOpenedID"]
        assert order.trade_close is not None
        assert order.trade_close.trade_id == "6"
        assert MarketOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_limit_order(self) -> None:
        """Test LimitOrder with an OANDA-shaped payload."""
        payload = {
            "id": "20",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "LIMIT",
            "instrument": "EUR_USD",
            "units": "100",
            "price": "1.0900",
            "timeInForce": "GTC",
            "triggerCondition": "DEFAULT",
            "replacesOrderID": "19",
        }

        order = LimitOrder(**payload)
        assert order.price == Decimal("1.0900")
        assert isinstance(order.price, Decimal)
        assert order.state == OrderState.PENDING
        assert order.replaces_order_id == payload["replacesOrderID"]
        assert order.trigger_condition == OrderTriggerCondition.DEFAULT
        assert LimitOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_stop_order(self) -> None:
        """Test StopOrder with an OANDA-shaped payload."""
        payload = {
            "id": "21",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "STOP",
            "instrument": "GBP_USD",
            "units": "-500",
            "price": "1.2400",
            "priceBound": "1.2390",
            "timeInForce": "GTC",
        }

        order = StopOrder(**payload)
        assert order.price == Decimal("1.2400")
        assert order.price_bound == Decimal("1.2390")
        assert isinstance(order.price_bound, Decimal)
        assert order.units == Decimal("-500")
        assert order.instrument == InstrumentName.GBP_USD
        assert StopOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_market_if_touched_order(self) -> None:
        """Test MarketIfTouchedOrder with an OANDA-shaped payload."""
        payload = {
            "id": "22",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "MARKET_IF_TOUCHED",
            "instrument": "USD_JPY",
            "units": "1000",
            "price": "145.500",
            "priceBound": "145.600",
            "initialMarketPrice": "146.100",
        }

        order = MarketIfTouchedOrder(**payload)
        assert order.price == Decimal("145.500")
        assert order.price_bound == Decimal("145.600")
        assert order.initial_market_price == Decimal("146.100")
        assert isinstance(order.initial_market_price, Decimal)
        assert MarketIfTouchedOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_take_profit_order(self) -> None:
        """Test TakeProfitOrder with an OANDA-shaped payload."""
        payload = {
            "id": "23",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "TAKE_PROFIT",
            "tradeID": "18",
            "clientTradeID": "my-trade-18",
            "price": "1.1500",
            "timeInForce": "GTC",
        }

        order = TakeProfitOrder(**payload)
        assert order.trade_id == payload["tradeID"]
        assert order.client_trade_id == payload["clientTradeID"]
        assert order.price == Decimal("1.1500")
        assert isinstance(order.price, Decimal)
        assert TakeProfitOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_stop_loss_order(self) -> None:
        """Test StopLossOrder with an OANDA-shaped payload."""
        payload = {
            "id": "24",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "STOP_LOSS",
            "tradeID": "18",
            "price": "1.0500",
            "guaranteed": False,
            "guaranteedExecutionPremium": "0.00",
        }

        order = StopLossOrder(**payload)
        assert order.trade_id == payload["tradeID"]
        assert order.price == Decimal("1.0500")
        assert order.guaranteed_execution_premium == Decimal("0.00")
        assert isinstance(order.guaranteed_execution_premium, Decimal)
        assert order.guaranteed is False
        assert StopLossOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_trailing_stop_loss_order(self) -> None:
        """Test TrailingStopLossOrder with an OANDA-shaped payload."""
        payload = {
            "id": "25",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "PENDING",
            "type": "TRAILING_STOP_LOSS",
            "tradeID": "18",
            "distance": "0.0050",
            "trailingStopValue": "1.0850",
        }

        order = TrailingStopLossOrder(**payload)
        assert order.trade_id == payload["tradeID"]
        assert order.distance == Decimal("0.0050")
        assert order.trailing_stop_value == Decimal("1.0850")
        assert isinstance(order.trailing_stop_value, Decimal)
        assert TrailingStopLossOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order

    def test_fixed_price_order(self) -> None:
        """Test FixedPriceOrder with an OANDA-shaped payload."""
        payload = {
            "id": "26",
            "createTime": "2024-01-15T12:00:00.000000000Z",
            "state": "FILLED",
            "type": "FIXED_PRICE",
            "instrument": "SPX500_USD",
            "units": "10",
            "price": "5250.0",
            "positionFill": "DEFAULT",
            "tradeState": "OPEN",
            "fillingTransactionID": "27",
        }

        order = FixedPriceOrder(**payload)
        assert order.trade_state == payload["tradeState"]
        assert order.price == Decimal("5250.0")
        assert order.units == Decimal("10")
        assert isinstance(order.price, Decimal)
        assert order.filling_transaction_id == payload["fillingTransactionID"]
        assert order.type == OrderType.FIXED_PRICE
        assert FixedPriceOrder(**order.model_dump(by_alias=True, exclude_none=True)) == order


class TestOrderReasonEnums:
    """Member counts and value round-trips for order reason enums."""

    @pytest.mark.parametrize(
        ("enum_cls", "expected_count", "sample_values"),
        [
            pytest.param(MarketOrderReason, 5, ["CLIENT_ORDER", "TRADE_CLOSE", "MARGIN_CLOSEOUT", "DELAYED_TRADE_CLOSE"], id="market-order-reason"),
            pytest.param(LimitOrderReason, 2, ["CLIENT_ORDER", "REPLACEMENT"], id="limit-order-reason"),
            pytest.param(StopOrderReason, 2, ["CLIENT_ORDER", "REPLACEMENT"], id="stop-order-reason"),
            pytest.param(MarketIfTouchedOrderReason, 2, ["CLIENT_ORDER", "REPLACEMENT"], id="market-if-touched-order-reason"),
            pytest.param(TakeProfitOrderReason, 3, ["CLIENT_ORDER", "REPLACEMENT", "ON_FILL"], id="take-profit-order-reason"),
            pytest.param(StopLossOrderReason, 3, ["CLIENT_ORDER", "REPLACEMENT", "ON_FILL"], id="stop-loss-order-reason"),
            pytest.param(TrailingStopLossOrderReason, 3, ["CLIENT_ORDER", "REPLACEMENT", "ON_FILL"], id="trailing-stop-loss-order-reason"),
            pytest.param(GuaranteedStopLossOrderReason, 3, ["CLIENT_ORDER", "REPLACEMENT", "ON_FILL"], id="guaranteed-stop-loss-order-reason"),
            pytest.param(FixedPriceOrderReason, 3, ["PLATFORM_ACCOUNT_MIGRATION", "TRADE_CLOSE_ADMINISTRATIVE_ACTION"], id="fixed-price-order-reason"),
            pytest.param(MarketOrderMarginCloseoutReason, 3, ["MARGIN_CHECK_VIOLATION", "REGULATORY_MARGIN_CALL_VIOLATION"], id="market-order-margin-closeout-reason"),
            pytest.param(OrderFillReason, 16, ["LIMIT_ORDER", "MARKET_ORDER_TRADE_CLOSE", "FIXED_PRICE_ORDER"], id="order-fill-reason"),
            pytest.param(OrderCancelReason, 65, ["CLIENT_REQUEST", "TIME_IN_FORCE_EXPIRED", "INSUFFICIENT_MARGIN"], id="order-cancel-reason"),
        ],
    )
    def test_reason_enum_members(self, enum_cls: type[Enum], expected_count: int, sample_values: list[str]) -> None:
        """Assert member count, value uniqueness, and value round-trip."""
        values = [member.value for member in enum_cls]
        assert len(values) == expected_count
        assert len(set(values)) == expected_count
        for value in sample_values:
            assert enum_cls(value).value == value
