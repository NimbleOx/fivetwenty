"""Tests for instrument-related models."""

from decimal import Decimal

from fivetwenty.models import (
    DayOfWeek,
    FinancingDayOfWeek,
    GuaranteedStopLossOrderEntryData,
    GuaranteedStopLossOrderLevelRestriction,
    Instrument,
    InstrumentCommission,
    InstrumentFinancing,
    InstrumentName,
    InstrumentType,
    Tag,
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


class TestInstrumentMetadataModels:
    """Named coverage for instrument metadata sub-models."""

    def test_tag(self) -> None:
        """Test Tag model."""
        tag = Tag(type="ASSET_CLASS", name="CURRENCY")
        assert tag.type == "ASSET_CLASS"
        assert tag.name == "CURRENCY"
        assert Tag(**tag.model_dump(by_alias=True, exclude_none=True)) == tag

    def test_financing_day_of_week(self) -> None:
        """Test FinancingDayOfWeek aliases."""
        payload = {"dayOfWeek": "MONDAY", "daysCharged": 1}
        financing_day = FinancingDayOfWeek(**payload)
        assert financing_day.day_of_week == DayOfWeek.MONDAY
        assert financing_day.days_charged == payload["daysCharged"]
        assert FinancingDayOfWeek(**financing_day.model_dump(by_alias=True, exclude_none=True)) == financing_day

    def test_instrument_financing(self) -> None:
        """Test InstrumentFinancing aliases and Decimal typing."""
        payload = {
            "longRate": "-0.0095",
            "shortRate": "0.0042",
            "financingDaysOfWeek": [
                {"dayOfWeek": "MONDAY", "daysCharged": 1},
                {"dayOfWeek": "WEDNESDAY", "daysCharged": 3},
            ],
        }

        financing = InstrumentFinancing(**payload)
        assert financing.long_rate == Decimal("-0.0095")
        assert financing.short_rate == Decimal("0.0042")
        assert isinstance(financing.long_rate, Decimal)
        assert len(financing.financing_days_of_week) == 2
        assert financing.financing_days_of_week[1].days_charged == 3
        assert InstrumentFinancing(**financing.model_dump(by_alias=True, exclude_none=True)) == financing

    def test_instrument_commission(self) -> None:
        """Test InstrumentCommission aliases and Decimal typing."""
        payload = {"commission": "0.50", "unitsTraded": "100000", "minimumCommission": "1.25"}

        commission = InstrumentCommission(**payload)
        assert commission.commission == Decimal("0.50")
        assert commission.units_traded == Decimal("100000")
        assert commission.minimum_commission == Decimal("1.25")
        assert isinstance(commission.minimum_commission, Decimal)
        assert InstrumentCommission(**commission.model_dump(by_alias=True, exclude_none=True)) == commission

    def test_guaranteed_stop_loss_order_level_restriction(self) -> None:
        """Test GuaranteedStopLossOrderLevelRestriction aliases and Decimal typing."""
        payload = {"volume": "1000000", "priceRange": "0.05"}

        restriction = GuaranteedStopLossOrderLevelRestriction(**payload)
        assert restriction.volume == Decimal("1000000")
        assert restriction.price_range == Decimal("0.05")
        assert isinstance(restriction.price_range, Decimal)
        assert GuaranteedStopLossOrderLevelRestriction(**restriction.model_dump(by_alias=True, exclude_none=True)) == restriction

    def test_guaranteed_stop_loss_order_entry_data(self) -> None:
        """Test GuaranteedStopLossOrderEntryData aliases and nested restriction."""
        payload = {
            "minimumDistance": "0.0010",
            "premium": "0.50",
            "levelRestriction": {"volume": "1000000", "priceRange": "0.05"},
        }

        entry_data = GuaranteedStopLossOrderEntryData(**payload)
        assert entry_data.minimum_distance == Decimal("0.0010")
        assert entry_data.premium == Decimal("0.50")
        assert isinstance(entry_data.premium, Decimal)
        assert entry_data.level_restriction is not None
        assert entry_data.level_restriction.volume == Decimal("1000000")
        assert GuaranteedStopLossOrderEntryData(**entry_data.model_dump(by_alias=True, exclude_none=True)) == entry_data
