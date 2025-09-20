"""Tests for instrument-related models."""

from fivetwenty.models import (
    Instrument,
    InstrumentName,
    InstrumentType,
)


class TestInstrumentModels:
    """Test instrument-related models."""

    def test_instrument(self) -> None:
        """Test Instrument model."""
        instrument = Instrument(
            name=InstrumentName.EUR_USD,
            type=InstrumentType.CURRENCY,
            display_name="EUR/USD",
            pip_location=-4,
            display_precision=5,
            trade_units_precision=0,
            minimum_trade_size="1",
            maximum_trailing_stop_distance="100.0",
            minimum_trailing_stop_distance="0.0001",
            maximum_position_size="100000000",
            maximum_order_units="100000000",
            margin_rate="0.02",
        )
        assert instrument.name == InstrumentName.EUR_USD
        assert instrument.type == InstrumentType.CURRENCY
        assert instrument.display_name == "EUR/USD"
        assert instrument.pip_location == -4
