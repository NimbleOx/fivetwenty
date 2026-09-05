"""Tests for base model functionality and aliases."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any

import pytest

from fivetwenty.models import (
    CalculatedTradeState,
    InstrumentName,
    LimitOrderRequest,
    MarketOrderRequest,
    OrderPositionFill,
    OrderTriggerCondition,
    TakeProfitOrderRequest,
    TimeInForce,
    Trade,
)
from fivetwenty.models.base import ApiModel


class TestApiModel:
    """Test base ApiModel functionality."""

    def test_model_configuration(self) -> None:
        """Test ApiModel configuration settings."""
        # Test that models use proper configuration
        order = MarketOrderRequest(instrument=InstrumentName.EUR_USD, units="1000", time_in_force=TimeInForce.GTC)

        # Test populate_by_name allows both field name and alias
        assert order.instrument == InstrumentName.EUR_USD
        assert order.units == Decimal("1000")  # Field is now Decimal
        assert order.time_in_force == TimeInForce.GTC

        # Test use_enum_values in serialization
        data = order.model_dump()
        assert data["time_in_force"] == "GTC"  # String value, not enum object

        # Test validate_assignment
        order.units = "2000"  # Should work due to validate_assignment=True
        assert order.units == Decimal("2000")  # Field is now Decimal

    def test_camel_case_aliases(self) -> None:
        """Test that camelCase input and output work correctly."""
        # Test camelCase input (as from OANDA API responses)
        from fivetwenty.models import ClientExtensions

        order = MarketOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units="1000",
            timeInForce=TimeInForce.GTC,  # camelCase input
            positionFill=OrderPositionFill.REDUCE_ONLY,  # camelCase input
            clientExtensions=ClientExtensions(tag="test"),  # camelCase input
        )
        assert order.time_in_force == TimeInForce.GTC
        assert order.position_fill == OrderPositionFill.REDUCE_ONLY
        assert order.client_extensions.tag == "test"

        # Test camelCase output (for OANDA API requests)
        api_data = order.model_dump(by_alias=True, exclude_none=True)
        assert "timeInForce" in api_data
        assert "positionFill" in api_data
        assert "clientExtensions" in api_data
        assert api_data["timeInForce"] == "GTC"
        assert api_data["positionFill"] == "REDUCE_ONLY"

        # Test that snake_case field names still work
        order2 = MarketOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units="1000",
            time_in_force=TimeInForce.GTC,  # snake_case input
            position_fill=OrderPositionFill.REDUCE_ONLY,  # snake_case input
        )
        assert order2.time_in_force == TimeInForce.GTC
        assert order2.position_fill == OrderPositionFill.REDUCE_ONLY

    def test_limit_order_aliases(self) -> None:
        """Test LimitOrderRequest camelCase aliases."""
        # Test camelCase input
        order = LimitOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units="1000",
            price="1.1000",
            timeInForce=TimeInForce.GTD,  # camelCase
            gtdTime="2024-01-02T12:00:00Z",  # camelCase
            triggerCondition=OrderTriggerCondition.BID,  # camelCase
        )
        assert order.time_in_force == TimeInForce.GTD
        assert isinstance(order.gtd_time, datetime)
        assert order.gtd_time.year == 2024
        assert order.gtd_time.month == 1
        assert order.gtd_time.day == 2
        assert order.trigger_condition == OrderTriggerCondition.BID

        # Test camelCase output
        api_data = order.model_dump(by_alias=True, exclude_none=True)
        assert api_data["timeInForce"] == "GTD"
        assert api_data["gtdTime"] == "2024-01-02T12:00:00Z"
        assert api_data["triggerCondition"] == "BID"

    def test_trade_aliases(self) -> None:
        """Test Trade model camelCase aliases."""
        # Test camelCase input (simulating API response)
        trade_data = {
            "id": "123",
            "instrument": "EUR_USD",
            "price": "1.1000",
            "openTime": "2024-01-01T12:00:00Z",  # camelCase
            "state": "OPEN",
            "initialUnits": "1000",  # camelCase
            "initialMarginRequired": "50.00",  # camelCase
            "currentUnits": "1000",  # camelCase
            "realizedPL": "5.00",  # camelCase
            "unrealizedPL": "10.00",  # camelCase
            "marginUsed": "50.00",  # camelCase
        }

        trade = Trade(**trade_data)
        assert isinstance(trade.open_time, datetime)
        assert trade.open_time.year == 2024
        assert trade.open_time.month == 1
        assert trade.open_time.day == 1
        assert trade.open_time.hour == 12
        assert trade.initial_units == Decimal("1000")  # Field is now Decimal
        assert trade.realized_pl == Decimal("5.00")
        assert trade.unrealized_pl == Decimal("10.00")
        assert trade.margin_used == Decimal("50.00")

        # Test camelCase output (for API requests)
        api_data = trade.model_dump(by_alias=True, exclude_none=True)
        assert api_data["openTime"] == "2024-01-01T12:00:00Z"
        assert api_data["initialUnits"] == "1000"
        assert api_data["realizedPL"] == "5.00"
        assert api_data["unrealizedPL"] == "10.00"
        assert api_data["marginUsed"] == "50.00"

    def test_attribute_access_resolves_aliases(self) -> None:
        """Test ApiModel attribute compatibility for OANDA aliases."""
        trade = Trade(
            id="123",
            instrument="EUR_USD",
            price="1.1000",
            openTime="2024-01-01T12:00:00Z",
            state="OPEN",
            initialUnits="1000",
            initialMarginRequired="50.00",
            currentUnits="1000",
            realizedPL="5.00",
            marginUsed="50.00",
        )

        assert trade.openTime == trade.open_time
        assert trade.realizedPL == Decimal("5.00")
        assert trade.marginUsed == Decimal("50.00")

    def test_dict_like_access_resolves_fields_and_aliases(self) -> None:
        """Test ApiModel dict-like access for Python names and OANDA aliases."""
        trade = Trade(
            id="123",
            instrument="EUR_USD",
            price="1.1000",
            openTime="2024-01-01T12:00:00Z",
            state="OPEN",
            initialUnits="1000",
            initialMarginRequired="50.00",
            currentUnits="1000",
            realizedPL="5.00",
            marginUsed="50.00",
        )

        assert trade["open_time"] == "2024-01-01T12:00:00Z"
        assert trade["openTime"] == "2024-01-01T12:00:00Z"
        assert trade.get("realizedPL") == "5.00"
        assert trade.get("realized_pl") == "5.00"
        assert "marginUsed" in trade
        assert "margin_used" in trade
        assert "unrealizedPL" not in trade
        assert trade.get("missing", "default") == "default"

        with pytest.raises(KeyError):
            trade["missing"]

    def test_take_profit_order_aliases(self) -> None:
        """Test TakeProfitOrderRequest camelCase aliases."""
        # Test camelCase input
        order = TakeProfitOrderRequest(
            tradeID="123",  # camelCase
            price="1.1100",
            timeInForce=TimeInForce.GTD,  # camelCase
            gtdTime="2024-01-02T12:00:00Z",  # camelCase
        )
        assert order.trade_id == "123"
        assert order.time_in_force == TimeInForce.GTD
        assert order.gtd_time == datetime(2024, 1, 2, 12, 0, 0, tzinfo=timezone.utc)

        # Test camelCase output
        api_data = order.model_dump(by_alias=True, exclude_none=True)
        assert api_data["tradeID"] == "123"
        assert api_data["timeInForce"] == "GTD"
        assert api_data["gtdTime"] == "2024-01-02T12:00:00Z"

    def test_calculated_trade_state_aliases(self) -> None:
        """Test CalculatedTradeState camelCase aliases."""
        # Test camelCase input (from API)
        calc_data = {
            "id": "123",
            "unrealizedPL": "15.00",  # camelCase
            "marginUsed": "75.00",  # camelCase
        }

        calc_state = CalculatedTradeState(**calc_data)
        assert calc_state.unrealized_pl == Decimal("15.00")
        assert calc_state.margin_used == Decimal("75.00")

        # Test camelCase output
        api_data = calc_state.model_dump(by_alias=True)
        assert api_data["unrealizedPL"] == "15.00"
        assert api_data["marginUsed"] == "75.00"

    def test_alias_roundtrip(self) -> None:
        """Test that models can round-trip through camelCase JSON (API simulation)."""
        # Simulate receiving data from OANDA API (camelCase) and sending it back

        # 1. Receive MarketOrderRequest from API (camelCase)
        api_order = {
            "type": "MARKET",
            "instrument": "EUR_USD",
            "units": "1000",
            "timeInForce": "GTC",  # camelCase
            "positionFill": "DEFAULT",  # camelCase
            "clientExtensions": {"tag": "test"},  # camelCase
        }
        order = MarketOrderRequest(**api_order)

        # 2. Send it back to API (camelCase)
        back_to_api = order.model_dump(by_alias=True, exclude_none=True)
        assert back_to_api["timeInForce"] == "GTC"
        assert back_to_api["positionFill"] == "DEFAULT"
        assert back_to_api["clientExtensions"] == {"tag": "test"}

        # 3. Receive Trade from API (camelCase)
        api_trade = {
            "id": "456",
            "instrument": "GBP_USD",
            "price": "1.2500",
            "openTime": "2024-01-01T15:30:00Z",
            "state": "OPEN",
            "initialUnits": "500",
            "initialMarginRequired": "25.00",
            "currentUnits": "500",
            "realizedPL": "0.00",
            "unrealizedPL": "2.50",
            "marginUsed": "25.00",
        }
        trade = Trade(**api_trade)

        # 4. Send it back to API (camelCase)
        trade_to_api = trade.model_dump(by_alias=True, exclude_none=True)
        assert trade_to_api["openTime"] == "2024-01-01T15:30:00Z"
        assert trade_to_api["initialUnits"] == "500"
        assert trade_to_api["realizedPL"] == "0.00"
        assert trade_to_api["unrealizedPL"] == "2.50"

        # Verify we can round-trip perfectly
        trade_roundtrip = Trade(**trade_to_api)
        assert trade_roundtrip.open_time == trade.open_time
        assert trade_roundtrip.initial_units == trade.initial_units
        assert trade_roundtrip.realized_pl == trade.realized_pl


class _ContainerModel(ApiModel):
    """Test-only model exercising nested serialization of dicts and lists."""

    data: dict[str, Any] | None = None
    items: list[Any] | None = None
    when: datetime | None = None


class TestApiModelSerializationAndDictCompat:
    """Test ApiModel serializer recursion and dict-compat edge cases."""

    def _trade(self) -> Trade:
        return Trade(
            id="123",
            instrument="EUR_USD",
            price="1.1000",
            openTime="2024-01-01T12:00:00Z",
            state="OPEN",
            initialUnits="1000",
            initialMarginRequired="50.00",
            currentUnits="1000",
            realizedPL="5.00",
            marginUsed="50.00",
        )

    def test_contains_non_string_key_is_false(self) -> None:
        """Test that __contains__ rejects non-string keys."""
        trade = self._trade()
        assert 123 not in trade
        assert None not in trade
        assert ("openTime",) not in trade

    def test_getitem_unknown_key_raises_keyerror(self) -> None:
        """Test that unknown keys raise KeyError from __getitem__."""
        trade = self._trade()
        with pytest.raises(KeyError):
            trade["definitelyNotAField"]

    def test_get_returns_default_for_none_unset_field(self) -> None:
        """Test that get() falls back to the default for unset None fields."""
        trade = self._trade()
        assert trade.get("unrealizedPL") is None
        assert trade.get("unrealizedPL", "fallback") == "fallback"
        assert "unrealizedPL" not in trade

    def test_serializer_recurses_into_dicts_and_lists(self) -> None:
        """Test that Decimals and datetimes nested in containers are stringified."""
        model = _ContainerModel(
            data={"price": Decimal("1.25"), "nested": {"pl": Decimal("-0.50")}, "stamp": datetime(2024, 1, 1, 12, 0, tzinfo=timezone.utc)},
            items=[Decimal("2.50"), [Decimal("3.00")], {"d": Decimal("4.00")}],
        )

        dumped = model.model_dump()
        assert dumped["data"]["price"] == "1.25"
        assert dumped["data"]["nested"]["pl"] == "-0.50"
        assert dumped["data"]["stamp"] == "2024-01-01T12:00:00Z"
        assert dumped["items"][0] == "2.50"
        assert dumped["items"][1] == ["3.00"]
        assert dumped["items"][2] == {"d": "4.00"}

    def test_serializer_non_utc_datetime_keeps_offset(self) -> None:
        """Test that non-UTC datetimes serialize with an explicit offset."""
        tz = timezone(timedelta(hours=-5))
        model = _ContainerModel(when=datetime(2024, 6, 1, 9, 30, tzinfo=tz))

        dumped = model.model_dump()
        assert dumped["when"] == "2024-06-01T09:30:00-05:00"
