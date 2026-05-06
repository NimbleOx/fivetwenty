"""Tests for pricing-related models."""

from datetime import datetime, timezone
from decimal import Decimal

from fivetwenty.endpoints.pricing import CandlesResponse  # noqa: TC001
from fivetwenty.models import (
    Candlestick,
    CandlestickData,
    CandlestickGranularity,
    ClientPrice,
    Currency,
    DailyAlignment,
    HomeConversions,
    InstrumentName,
    PriceBucket,
    PricingHeartbeat,
    QuoteHomeConversionFactors,
    UnitsAvailable,
    WeeklyAlignment,
)


class TestPricingModels:
    """Test pricing-related models."""

    def test_client_price(self) -> None:
        """Test ClientPrice model."""
        price = ClientPrice(instrument=InstrumentName.EUR_USD, time="2024-01-01T12:00:00Z", status="tradeable", tradeable=True, closeout_bid="1.1000", closeout_ask="1.1002")
        assert price.instrument == InstrumentName.EUR_USD
        assert price.tradeable is True
        assert price.closeout_bid == Decimal("1.1000")
        assert price.closeout_ask == Decimal("1.1002")

    def test_pricing_heartbeat(self) -> None:
        """Test PricingHeartbeat model."""
        heartbeat = PricingHeartbeat(time="2024-01-01T12:00:00Z")
        assert heartbeat.type == "HEARTBEAT"
        assert heartbeat.time == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


class TestPhase3PricingModels:
    """Test Phase 3 enhanced pricing and market data models."""

    def test_candlestick_granularity_enum(self) -> None:
        """Test CandlestickGranularity enum values."""
        # Second-based intervals
        assert CandlestickGranularity.S5 == "S5"
        assert CandlestickGranularity.S10 == "S10"
        assert CandlestickGranularity.S15 == "S15"
        assert CandlestickGranularity.S30 == "S30"

        # Minute-based intervals
        assert CandlestickGranularity.M1 == "M1"
        assert CandlestickGranularity.M5 == "M5"
        assert CandlestickGranularity.M15 == "M15"
        assert CandlestickGranularity.M30 == "M30"

        # Hour-based intervals
        assert CandlestickGranularity.H1 == "H1"
        assert CandlestickGranularity.H4 == "H4"
        assert CandlestickGranularity.H12 == "H12"

        # Higher timeframes
        assert CandlestickGranularity.D == "D"
        assert CandlestickGranularity.W == "W"
        assert CandlestickGranularity.M == "M"

    def test_weekly_alignment_enum(self) -> None:
        """Test WeeklyAlignment enum values."""
        assert WeeklyAlignment.MONDAY == "Monday"
        assert WeeklyAlignment.TUESDAY == "Tuesday"
        assert WeeklyAlignment.WEDNESDAY == "Wednesday"
        assert WeeklyAlignment.THURSDAY == "Thursday"
        assert WeeklyAlignment.FRIDAY == "Friday"
        assert WeeklyAlignment.SATURDAY == "Saturday"
        assert WeeklyAlignment.SUNDAY == "Sunday"

    def test_daily_alignment_enum(self) -> None:
        """Test DailyAlignment enum values."""
        assert DailyAlignment.MIDNIGHT == 0
        assert DailyAlignment.NOON == 12
        assert DailyAlignment.H23 == 23

    def test_price_bucket(self) -> None:
        """Test PriceBucket model."""
        bucket = PriceBucket(price="1.1234", liquidity="1000000")
        assert bucket.price == Decimal("1.1234")
        assert bucket.liquidity == Decimal("1000000")  # Field is now Decimal

    def test_home_conversions(self) -> None:
        """Test HomeConversions model."""
        conversions = HomeConversions(currency=Currency.USD, account_gain="1.0", account_loss="1.0", position_value="1.0")
        assert conversions.currency == Currency.USD
        assert conversions.account_gain == Decimal("1.0")  # Field is now Decimal
        assert conversions.account_loss == Decimal("1.0")  # Field is now Decimal
        assert conversions.position_value == Decimal("1.0")  # Field is now Decimal

    def test_quote_home_conversion_factors(self) -> None:
        """Test QuoteHomeConversionFactors model."""
        factors = QuoteHomeConversionFactors(positive_units="1.0", negative_units="-1.0")
        assert factors.positive_units == Decimal("1.0")  # Field is now Decimal
        assert factors.negative_units == Decimal("-1.0")  # Field is now Decimal

    def test_units_available(self) -> None:
        """Test UnitsAvailable model."""
        units = UnitsAvailable(default={"long": "100000", "short": "100000"}, reduce_first={"long": "50000", "short": "50000"}, reduce_only={"long": "25000", "short": "25000"}, open_only={"long": "75000", "short": "75000"})
        assert units.default.long == Decimal("100000")
        assert units.reduce_first.long == Decimal("50000")
        assert units.reduce_only.short == Decimal("25000")
        assert units.open_only.short == Decimal("75000")

    def test_candlestick_data(self) -> None:
        """Test CandlestickData model."""
        candle_data = CandlestickData(
            o="1.1000",  # Open
            h="1.1050",  # High
            l="1.0990",  # Low
            c="1.1030",  # Close
        )

        # Test basic fields
        assert candle_data.o == Decimal("1.1000")
        assert candle_data.h == Decimal("1.1050")
        assert candle_data.l == Decimal("1.0990")
        assert candle_data.c == Decimal("1.1030")

    def test_candlestick(self) -> None:
        """Test Candlestick model."""
        bid_data = CandlestickData(o="1.1000", h="1.1050", l="1.0990", c="1.1030")
        ask_data = CandlestickData(o="1.1005", h="1.1055", l="1.0995", c="1.1035")
        mid_data = CandlestickData(o="1.1002", h="1.1052", l="1.0992", c="1.1032")

        candlestick = Candlestick(time="2024-01-01T12:00:00Z", complete=True, volume=1500, bid=bid_data, ask=ask_data, mid=mid_data)

        # Test basic fields
        assert candlestick.time == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert candlestick.complete is True
        assert candlestick.volume == 1500

    def test_candlestick_response(self) -> None:
        """Test CandlesResponse TypedDict."""
        # Create test candlestick
        complete_candle = Candlestick(time=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc), complete=True, volume=1000, mid=CandlestickData(o="1.1000", h="1.1050", l="1.0990", c="1.1030"))

        response: CandlesResponse = {"instrument": InstrumentName.EUR_USD, "granularity": CandlestickGranularity.M1, "candles": [complete_candle]}

        # Test basic fields
        assert response["instrument"] == InstrumentName.EUR_USD
        assert response["granularity"] == CandlestickGranularity.M1
        assert len(response["candles"]) == 1


class TestPhase3AliasTests:
    """Test camelCase aliases for Phase 3 models."""

    def test_home_conversions_aliases(self) -> None:
        """Test HomeConversions model camelCase aliases."""
        # Test camelCase input (from API)
        api_data = {
            "currency": "USD",
            "accountGain": "1.0",  # camelCase
            "accountLoss": "0.98",  # camelCase
            "positionValue": "1.02",  # camelCase
        }

        conversions = HomeConversions(**api_data)
        assert conversions.account_gain == Decimal("1.0")  # Decimal fields
        assert conversions.account_loss == Decimal("0.98")  # Decimal fields
        assert conversions.position_value == Decimal("1.02")  # Decimal fields

        # Test camelCase output (for API)
        api_output = conversions.model_dump(by_alias=True, exclude_none=True)
        assert api_output["accountGain"] == "1.0"
        assert api_output["accountLoss"] == "0.98"
        assert api_output["positionValue"] == "1.02"

    def test_quote_home_conversion_factors_aliases(self) -> None:
        """Test QuoteHomeConversionFactors model camelCase aliases."""
        # Test camelCase input
        api_data = {
            "positiveUnits": "1.0",  # camelCase
            "negativeUnits": "-1.0",  # camelCase
        }

        factors = QuoteHomeConversionFactors(**api_data)
        assert factors.positive_units == Decimal("1.0")  # Decimal fields
        assert factors.negative_units == Decimal("-1.0")  # Decimal fields

        # Test camelCase output
        api_output = factors.model_dump(by_alias=True, exclude_none=True)
        assert api_output["positiveUnits"] == "1.0"
        assert api_output["negativeUnits"] == "-1.0"

    def test_units_available_aliases(self) -> None:
        """Test UnitsAvailable model camelCase aliases."""
        # Test camelCase input
        api_data = {
            "default": {"long": "100000", "short": "100000"},
            "reduceFirst": {"long": "50000", "short": "50000"},  # camelCase
            "reduceOnly": {"long": "25000", "short": "25000"},  # camelCase
            "openOnly": {"long": "75000", "short": "75000"},  # camelCase
        }

        units = UnitsAvailable(**api_data)
        assert units.reduce_first.long == Decimal("50000")
        assert units.reduce_only.short == Decimal("25000")
        assert units.open_only.short == Decimal("75000")

        # Test camelCase output
        api_output = units.model_dump(by_alias=True, exclude_none=True)
        assert api_output["reduceFirst"]["long"] == "50000"
        assert api_output["reduceOnly"]["short"] == "25000"
        assert api_output["openOnly"]["short"] == "75000"

    def test_phase3_roundtrip_compatibility(self) -> None:
        """Test Phase 3 models can round-trip through camelCase JSON."""
        # Test HomeConversions round-trip
        conversions_api = {"currency": "EUR", "accountGain": "0.95", "accountLoss": "0.93", "positionValue": "1.05"}

        conversions = HomeConversions(**conversions_api)
        conversions_back_to_api = conversions.model_dump(by_alias=True, exclude_none=True)
        assert conversions_back_to_api["accountGain"] == "0.95"
        assert conversions_back_to_api["accountLoss"] == "0.93"
        assert conversions_back_to_api["positionValue"] == "1.05"

        # Perfect round-trip
        conversions_roundtrip = HomeConversions(**conversions_back_to_api)
        assert conversions_roundtrip.account_gain == conversions.account_gain
        assert conversions_roundtrip.account_loss == conversions.account_loss
        assert conversions_roundtrip.position_value == conversions.position_value

        # Test UnitsAvailable round-trip
        units_api = {
            "default": {"long": "100000", "short": "100000"},
            "reduceFirst": {"long": "50000", "short": "50000"},
            "reduceOnly": {"long": "25000", "short": "25000"},
            "openOnly": {"long": "75000", "short": "75000"},
        }

        units = UnitsAvailable(**units_api)
        units_back_to_api = units.model_dump(by_alias=True, exclude_none=True)
        assert units_back_to_api["reduceFirst"]["short"] == "50000"
        assert units_back_to_api["reduceOnly"]["long"] == "25000"
        assert units_back_to_api["openOnly"]["short"] == "75000"

        # Perfect round-trip
        units_roundtrip = UnitsAvailable(**units_back_to_api)
        assert units_roundtrip.reduce_first == units.reduce_first
        assert units_roundtrip.reduce_only == units.reduce_only
        assert units_roundtrip.open_only == units.open_only
