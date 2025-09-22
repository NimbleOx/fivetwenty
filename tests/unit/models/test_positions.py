"""Tests for position-related models."""

from decimal import Decimal

from fivetwenty.models import (
    CalculatedPositionState,
    InstrumentName,
    Position,
    PositionSide,
)


class TestPositionModels:
    """Test position-related models."""

    def test_position(self) -> None:
        """Test Position model."""
        long_side = PositionSide(units="1000", pl="8.00", unrealized_pl="2.00", resettable_pl="8.00")
        short_side = PositionSide(units="0", pl="0.00", unrealized_pl="0.00", resettable_pl="0.00")
        position = Position(instrument=InstrumentName.EUR_USD, pl="15.00", unrealized_pl="10.00", margin_used="100.00", resettable_pl="5.00", long=long_side, short=short_side)
        assert position.instrument == InstrumentName.EUR_USD
        assert position.pl == Decimal("15.00")
        assert position.unrealized_pl == Decimal("10.00")
        assert position.margin_used == Decimal("100.00")
        assert position.resettable_pl == Decimal("5.00")

    def test_position_side(self) -> None:
        """Test PositionSide model."""
        position_side = PositionSide(units="1000", average_price="1.1000", pl="10.00", unrealized_pl="5.00", resettable_pl="10.00", trade_ids=["123", "124"])
        assert position_side.units == Decimal("1000")  # Field is now Decimal
        assert position_side.average_price == Decimal("1.1000")
        assert position_side.pl == Decimal("10.00")
        assert position_side.trade_ids == ["123", "124"]

    def test_calculated_position_state(self) -> None:
        """Test CalculatedPositionState model."""
        calc_state = CalculatedPositionState(instrument=InstrumentName.GBP_USD, net_unrealized_pl="15.00", long_unrealized_pl="20.00", short_unrealized_pl="-5.00", margin_used="75.00")
        assert calc_state.instrument == InstrumentName.GBP_USD
        assert calc_state.net_unrealized_pl == Decimal("15.00")
        assert calc_state.long_unrealized_pl == Decimal("20.00")
        assert calc_state.short_unrealized_pl == Decimal("-5.00")
        assert calc_state.margin_used == Decimal("75.00")
