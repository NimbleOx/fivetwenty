"""Tests for comprehensive enum validation."""

from decimal import Decimal

import pytest

from fivetwenty.models.enums import (
    AccountFinancingMode,
    # Type aliases
    AccountID,
    AccountUnits,
    CancellableOrderType,
    # Time related
    CandlestickGranularity,
    # Core enums
    Currency,
    DailyAlignment,
    DayOfWeek,
    # Trade related
    Direction,
    FundingReason,
    # Account related
    GuaranteedStopLossOrderMode,
    GuaranteedStopLossOrderModeForInstrument,
    GuaranteedStopLossOrderMutability,
    InstrumentName,
    InstrumentType,
    OrderID,
    OrderPositionFill,
    OrderState,
    OrderStateFilter,
    OrderTriggerCondition,
    # Order related
    OrderType,
    PositionAggregationMode,
    # Price related
    PriceStatus,
    PriceValue,
    RequestID,
    TimeInForce,
    TradeID,
    TradePL,
    TradeState,
    TradeStateFilter,
    TransactionID,
    TransactionRejectReason,
    # Transaction related
    TransactionType,
    WeeklyAlignment,
)


class TestCurrencyEnum:
    """Test Currency enum functionality."""

    def test_currency_values(self):
        """Test Currency enum has expected values."""
        expected_currencies = {"AUD", "CAD", "CHF", "CNH", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "JPY", "MXN", "NOK", "NZD", "PLN", "SEK", "SGD", "THB", "TRY", "USD", "ZAR"}

        actual_currencies = {currency.value for currency in Currency}
        assert actual_currencies == expected_currencies

    def test_currency_string_inheritance(self):
        """Test Currency inherits from str."""
        assert issubclass(Currency, str)
        assert isinstance(Currency.USD, str)
        assert Currency.USD == "USD"

    def test_major_currencies_present(self):
        """Test major currencies are present."""
        major_currencies = [Currency.USD, Currency.EUR, Currency.GBP, Currency.JPY]
        assert all(currency in Currency for currency in major_currencies)

    def test_currency_enum_completeness(self):
        """Test all expected currencies are present."""
        # Test a few specific currencies
        assert Currency.USD.value == "USD"
        assert Currency.EUR.value == "EUR"
        assert Currency.JPY.value == "JPY"
        assert Currency.GBP.value == "GBP"


class TestInstrumentNameEnum:
    """Test InstrumentName enum functionality."""

    def test_instrument_name_format(self):
        """Test InstrumentName values follow expected format."""
        for instrument in InstrumentName:
            # All instruments should be in BASE_QUOTE format
            assert "_" in instrument.value
            parts = instrument.value.split("_")
            assert len(parts) == 2
            assert len(parts[0]) == 3  # Base currency code
            assert len(parts[1]) == 3  # Quote currency code

    def test_major_pairs_present(self):
        """Test major currency pairs are present."""
        major_pairs = [
            InstrumentName.EUR_USD,
            InstrumentName.GBP_USD,
            InstrumentName.USD_JPY,
            InstrumentName.USD_CHF,
            InstrumentName.AUD_USD,
            InstrumentName.USD_CAD,
            InstrumentName.NZD_USD,
        ]

        for pair in major_pairs:
            assert pair in InstrumentName

    def test_instrument_name_string_inheritance(self):
        """Test InstrumentName inherits from str."""
        assert issubclass(InstrumentName, str)
        assert isinstance(InstrumentName.EUR_USD, str)
        assert InstrumentName.EUR_USD == "EUR_USD"

    def test_instrument_name_uniqueness(self):
        """Test all instrument names are unique."""
        values = [instrument.value for instrument in InstrumentName]
        assert len(values) == len(set(values))


class TestOrderEnums:
    """Test order-related enums."""

    def test_order_type_completeness(self):
        """Test OrderType has all expected values."""
        expected_types = {"MARKET", "LIMIT", "STOP", "MARKET_IF_TOUCHED", "TAKE_PROFIT", "STOP_LOSS", "GUARANTEED_STOP_LOSS", "TRAILING_STOP_LOSS"}

        actual_types = {order_type.value for order_type in OrderType}
        assert actual_types == expected_types

    def test_order_state_values(self):
        """Test OrderState has correct values."""
        expected_states = {"PENDING", "FILLED", "TRIGGERED", "CANCELLED"}
        actual_states = {state.value for state in OrderState}
        assert actual_states == expected_states

    def test_order_position_fill_values(self):
        """Test OrderPositionFill values."""
        expected_fills = {"OPEN_ONLY", "REDUCE_FIRST", "REDUCE_ONLY", "DEFAULT"}
        actual_fills = {fill.value for fill in OrderPositionFill}
        assert actual_fills == expected_fills

    def test_time_in_force_values(self):
        """Test TimeInForce values."""
        expected_tifs = {"GTC", "GTD", "GFD", "FOK", "IOC"}
        actual_tifs = {tif.value for tif in TimeInForce}
        assert actual_tifs == expected_tifs


class TestTradeEnums:
    """Test trade-related enums."""

    def test_direction_values(self):
        """Test Direction enum values."""
        assert Direction.LONG.value == "LONG"
        assert Direction.SHORT.value == "SHORT"
        assert len(Direction) == 2

    def test_trade_state_values(self):
        """Test TradeState values."""
        expected_states = {"OPEN", "CLOSED", "CLOSE_WHEN_TRADEABLE"}
        actual_states = {state.value for state in TradeState}
        assert actual_states == expected_states

    def test_trade_state_filter_values(self):
        """Test TradeStateFilter values."""
        expected_filters = {"OPEN", "CLOSED", "CLOSE_WHEN_TRADEABLE", "ALL"}
        actual_filters = {filter_val.value for filter_val in TradeStateFilter}
        assert actual_filters == expected_filters

    def test_trade_pl_values(self):
        """Test TradePL values."""
        expected_pl = {"POSITIVE", "NEGATIVE", "ZERO"}
        actual_pl = {pl.value for pl in TradePL}
        assert actual_pl == expected_pl


class TestCandlestickGranularity:
    """Test CandlestickGranularity enum."""

    def test_second_based_granularities(self):
        """Test second-based granularities."""
        second_granularities = [
            CandlestickGranularity.S5,
            CandlestickGranularity.S10,
            CandlestickGranularity.S15,
            CandlestickGranularity.S30,
        ]

        for granularity in second_granularities:
            assert granularity.value.startswith("S")

    def test_minute_based_granularities(self):
        """Test minute-based granularities."""
        minute_granularities = [
            CandlestickGranularity.M1,
            CandlestickGranularity.M2,
            CandlestickGranularity.M4,
            CandlestickGranularity.M5,
            CandlestickGranularity.M10,
            CandlestickGranularity.M15,
            CandlestickGranularity.M30,
        ]

        for granularity in minute_granularities:
            assert granularity.value.startswith("M")
            assert granularity.value != "M"

    def test_hour_based_granularities(self):
        """Test hour-based granularities."""
        hour_granularities = [
            CandlestickGranularity.H1,
            CandlestickGranularity.H2,
            CandlestickGranularity.H3,
            CandlestickGranularity.H4,
            CandlestickGranularity.H6,
            CandlestickGranularity.H8,
            CandlestickGranularity.H12,
        ]

        for granularity in hour_granularities:
            assert granularity.value.startswith("H")

    def test_period_based_granularities(self):
        """Test day/week/month granularities."""
        assert CandlestickGranularity.D.value == "D"
        assert CandlestickGranularity.W.value == "W"
        assert CandlestickGranularity.M.value == "M"


class TestTimeAlignmentEnums:
    """Test time alignment enums."""

    def test_weekly_alignment_days(self):
        """Test WeeklyAlignment has all days."""
        expected_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}

        actual_days = {day.value for day in WeeklyAlignment}
        assert actual_days == expected_days

    def test_daily_alignment_hours(self):
        """Test DailyAlignment has all hours."""
        # Should have hours 0-23
        expected_hours = set(range(24))
        actual_hours = {hour.value for hour in DailyAlignment}
        assert actual_hours == expected_hours

    def test_daily_alignment_special_values(self):
        """Test DailyAlignment special values."""
        assert DailyAlignment.MIDNIGHT.value == 0
        assert DailyAlignment.NOON.value == 12

    def test_day_of_week_values(self):
        """Test DayOfWeek enum values."""
        expected_days = {"SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"}

        actual_days = {day.value for day in DayOfWeek}
        assert actual_days == expected_days


class TestTransactionEnums:
    """Test transaction-related enums."""

    def test_transaction_type_categories(self):
        """Test TransactionType has expected categories."""
        # Test a few key transaction types
        assert TransactionType.CREATE.value == "CREATE"
        assert TransactionType.MARKET_ORDER.value == "MARKET_ORDER"
        assert TransactionType.ORDER_FILL.value == "ORDER_FILL"
        assert TransactionType.DAILY_FINANCING.value == "DAILY_FINANCING"

    def test_transaction_reject_reasons(self):
        """Test TransactionRejectReason values."""
        # Test a few key reject reasons
        assert TransactionRejectReason.INSUFFICIENT_MARGIN.value == "INSUFFICIENT_MARGIN"
        assert TransactionRejectReason.INSTRUMENT_NOT_TRADEABLE.value == "INSTRUMENT_NOT_TRADEABLE"
        assert TransactionRejectReason.ACCOUNT_NOT_ACTIVE.value == "ACCOUNT_NOT_ACTIVE"

    def test_funding_reason_values(self):
        """Test FundingReason values."""
        expected_reasons = {"CLIENT_FUNDING", "ACCOUNT_TRANSFER", "DIVISION_MIGRATION", "SITE_MIGRATION", "ADJUSTMENT"}

        actual_reasons = {reason.value for reason in FundingReason}
        assert actual_reasons == expected_reasons


class TestAccountEnums:
    """Test account-related enums."""

    def test_guaranteed_stop_loss_mode(self):
        """Test GuaranteedStopLossOrderMode values."""
        expected_modes = {"DISABLED", "ALLOWED", "REQUIRED"}
        actual_modes = {mode.value for mode in GuaranteedStopLossOrderMode}
        assert actual_modes == expected_modes

    def test_guaranteed_stop_loss_mutability(self):
        """Test GuaranteedStopLossOrderMutability values."""
        expected_mutabilities = {"FIXED", "REPLACEABLE", "CANCELABLE", "PRICE_WIDEN_ONLY"}
        actual_mutabilities = {mut.value for mut in GuaranteedStopLossOrderMutability}
        assert actual_mutabilities == expected_mutabilities

    def test_account_financing_mode(self):
        """Test AccountFinancingMode values."""
        expected_modes = {"NO_FINANCING", "SECOND_BY_SECOND", "DAILY"}
        actual_modes = {mode.value for mode in AccountFinancingMode}
        assert actual_modes == expected_modes

    def test_position_aggregation_mode(self):
        """Test PositionAggregationMode values."""
        expected_modes = {"ABSOLUTE_SUM", "MAXIMAL_SIDE", "NET_SUM"}
        actual_modes = {mode.value for mode in PositionAggregationMode}
        assert actual_modes == expected_modes


class TestMiscellaneousEnums:
    """Test miscellaneous enums."""

    def test_instrument_type_values(self):
        """Test InstrumentType values."""
        expected_types = {"CURRENCY", "CFD", "METAL"}
        actual_types = {inst_type.value for inst_type in InstrumentType}
        assert actual_types == expected_types

    def test_price_status_values(self):
        """Test PriceStatus values."""
        assert PriceStatus.tradeable.value == "tradeable"
        assert PriceStatus.non_tradeable.value == "non-tradeable"
        assert PriceStatus.invalid.value == "invalid"

    def test_cancellable_order_type_values(self):
        """Test CancellableOrderType values."""
        expected_types = {"LIMIT", "STOP", "MARKET_IF_TOUCHED", "TAKE_PROFIT", "STOP_LOSS", "GUARANTEED_STOP_LOSS", "TRAILING_STOP_LOSS"}

        actual_types = {order_type.value for order_type in CancellableOrderType}
        assert actual_types == expected_types


class TestTypeAliases:
    """Test type aliases."""

    def test_type_aliases_are_correct_types(self):
        """Test that type aliases are correct types."""
        # These are type aliases, not classes, so we just test they exist
        assert AccountID is str
        assert TradeID is str
        assert OrderID is str
        assert TransactionID is str
        assert RequestID is str
        assert PriceValue is Decimal
        assert AccountUnits is Decimal


class TestEnumStringInheritance:
    """Test that all string enums properly inherit from str."""

    def test_all_enums_inherit_from_str(self):
        """Test that all enums inherit from str where expected."""
        string_enums = [
            Currency,
            InstrumentName,
            InstrumentType,
            OrderType,
            OrderState,
            Direction,
            TradeState,
            TimeInForce,
            OrderPositionFill,
            OrderTriggerCondition,
            CandlestickGranularity,
            WeeklyAlignment,
            TransactionType,
            TransactionRejectReason,
            FundingReason,
            GuaranteedStopLossOrderMode,
            GuaranteedStopLossOrderMutability,
            AccountFinancingMode,
            PositionAggregationMode,
            DayOfWeek,
            GuaranteedStopLossOrderModeForInstrument,
            TradeStateFilter,
            TradePL,
            OrderStateFilter,
            CancellableOrderType,
            PriceStatus,
        ]

        for enum_class in string_enums:
            assert issubclass(enum_class, str), f"{enum_class.__name__} should inherit from str"

    def test_daily_alignment_inherits_from_int(self):
        """Test that DailyAlignment inherits from int."""
        assert issubclass(DailyAlignment, int)
        assert isinstance(DailyAlignment.MIDNIGHT, int)


class TestEnumValidation:
    """Test enum validation and error handling."""

    def test_enum_value_validation(self):
        """Test that invalid enum values raise errors."""
        with pytest.raises(ValueError, match="is not a valid"):
            Currency("INVALID")

        with pytest.raises(ValueError, match="is not a valid"):
            OrderType("INVALID_ORDER")

        with pytest.raises(ValueError, match="is not a valid"):
            InstrumentName("INVALID_PAIR")

    def test_enum_case_sensitivity(self):
        """Test that enum values are case sensitive."""
        # Should work with correct case
        assert Currency("USD") == Currency.USD

        # Should fail with wrong case
        with pytest.raises(ValueError, match="is not a valid"):
            Currency("usd")

    def test_enum_iteration(self):
        """Test that enums can be iterated."""
        currencies = list(Currency)
        assert len(currencies) > 0
        assert Currency.USD in currencies

        order_types = list(OrderType)
        assert len(order_types) > 0
        assert OrderType.MARKET in order_types

    def test_enum_membership(self):
        """Test enum membership testing."""
        assert Currency.USD in Currency
        assert "INVALID" not in Currency.__members__

        assert OrderType.MARKET in OrderType
        assert "INVALID_ORDER" not in OrderType.__members__


class TestEnumComparison:
    """Test enum comparison operations."""

    def test_enum_equality(self):
        """Test enum equality comparisons."""
        assert Currency.USD == Currency.USD
        assert Currency.USD != Currency.EUR

        assert OrderType.MARKET == OrderType.MARKET
        assert OrderType.MARKET != OrderType.LIMIT

    def test_enum_identity(self):
        """Test enum identity (singleton behavior)."""
        usd1 = Currency.USD
        usd2 = Currency.USD
        assert usd1 is usd2  # Enum members are singletons

    def test_enum_hashability(self):
        """Test that enums are hashable."""
        currency_set = {Currency.USD, Currency.EUR, Currency.USD}
        assert len(currency_set) == 2  # USD should appear only once

        currency_dict = {Currency.USD: "US Dollar", Currency.EUR: "Euro"}
        assert currency_dict[Currency.USD] == "US Dollar"
