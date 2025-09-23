"""Tests for trade-related models."""

from decimal import Decimal

from fivetwenty.models import (
    CalculatedTradeState,
    InstrumentName,
    Trade,
    TradeState,
    TradeSummary,
)


class TestTradeModels:
    """Test trade-related models."""

    def test_trade(self) -> None:
        """Test Trade model."""
        trade = Trade(
            id="123",
            instrument=InstrumentName.EUR_USD,
            price="1.1000",
            open_time="2024-01-01T12:00:00Z",
            state=TradeState.OPEN,
            initial_units="1000",
            initial_margin_required="50.00",
            current_units="1000",
            realized_pl="0.00",
            unrealized_pl="10.00",
            margin_used="50.00",
        )
        assert trade.id == "123"
        assert trade.instrument == InstrumentName.EUR_USD
        assert trade.price == Decimal("1.1000")
        assert trade.state == TradeState.OPEN
        assert trade.initial_units == Decimal("1000")  # Field is now Decimal
        assert trade.current_units == Decimal("1000")  # Field is now Decimal


    def test_trade_summary(self) -> None:
        """Test TradeSummary model."""
        summary = TradeSummary(
            id="123",
            instrument=InstrumentName.EUR_USD,
            price="1.1000",
            open_time="2024-01-01T12:00:00Z",
            state=TradeState.OPEN,
            initial_units="1000",
            initial_margin_required="50.00",
            current_units="1000",
            realized_pl="0.00",
            unrealized_pl="10.00",
            margin_used="50.00",
            take_profit_order_id="tp_123",
            stop_loss_order_id="sl_123",
        )
        assert summary.id == "123"
        assert summary.take_profit_order_id == "tp_123"
        assert summary.stop_loss_order_id == "sl_123"
        assert summary.guaranteed_stop_loss_order_id is None


    def test_calculated_trade_state(self) -> None:
        """Test CalculatedTradeState model."""
        calc_state = CalculatedTradeState(id="123", unrealized_pl="10.00", margin_used="50.00")
        assert calc_state.id == "123"
        assert calc_state.unrealized_pl == Decimal("10.00")
        assert calc_state.margin_used == Decimal("50.00")

