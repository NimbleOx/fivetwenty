"""
Enumerations for OANDA API.

Contains all enum types used throughout the OANDA API models.
"""

from decimal import Decimal
from enum import Enum


# Core Enums
class Currency(str, Enum):
    """ISO 4217 currency codes supported by OANDA."""

    AUD = "AUD"  # Australian Dollar
    CAD = "CAD"  # Canadian Dollar
    CHF = "CHF"  # Swiss Franc
    CNH = "CNH"  # Chinese Yuan (Offshore)
    CZK = "CZK"  # Czech Koruna
    DKK = "DKK"  # Danish Krone
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British Pound
    HKD = "HKD"  # Hong Kong Dollar
    HUF = "HUF"  # Hungarian Forint
    JPY = "JPY"  # Japanese Yen
    MXN = "MXN"  # Mexican Peso
    NOK = "NOK"  # Norwegian Krone
    NZD = "NZD"  # New Zealand Dollar
    PLN = "PLN"  # Polish Zloty
    SEK = "SEK"  # Swedish Krona
    SGD = "SGD"  # Singapore Dollar
    THB = "THB"  # Thai Baht
    TRY = "TRY"  # Turkish Lira
    USD = "USD"  # United States Dollar
    ZAR = "ZAR"  # South African Rand


class InstrumentName(str, Enum):
    """Available trading instruments - complete list from OANDA."""

    # AUD pairs
    AUD_CAD = "AUD_CAD"
    AUD_CHF = "AUD_CHF"
    AUD_HKD = "AUD_HKD"
    AUD_JPY = "AUD_JPY"
    AUD_NZD = "AUD_NZD"
    AUD_SGD = "AUD_SGD"
    AUD_USD = "AUD_USD"

    # CAD pairs
    CAD_CHF = "CAD_CHF"
    CAD_HKD = "CAD_HKD"
    CAD_JPY = "CAD_JPY"
    CAD_SGD = "CAD_SGD"

    # CHF pairs
    CHF_HKD = "CHF_HKD"
    CHF_JPY = "CHF_JPY"
    CHF_ZAR = "CHF_ZAR"

    # EUR pairs
    EUR_AUD = "EUR_AUD"
    EUR_CAD = "EUR_CAD"
    EUR_CHF = "EUR_CHF"
    EUR_CZK = "EUR_CZK"
    EUR_DKK = "EUR_DKK"
    EUR_GBP = "EUR_GBP"
    EUR_HKD = "EUR_HKD"
    EUR_HUF = "EUR_HUF"
    EUR_JPY = "EUR_JPY"
    EUR_NOK = "EUR_NOK"
    EUR_NZD = "EUR_NZD"
    EUR_PLN = "EUR_PLN"
    EUR_SEK = "EUR_SEK"
    EUR_SGD = "EUR_SGD"
    EUR_TRY = "EUR_TRY"
    EUR_USD = "EUR_USD"
    EUR_ZAR = "EUR_ZAR"

    # GBP pairs
    GBP_AUD = "GBP_AUD"
    GBP_CAD = "GBP_CAD"
    GBP_CHF = "GBP_CHF"
    GBP_HKD = "GBP_HKD"
    GBP_JPY = "GBP_JPY"
    GBP_NZD = "GBP_NZD"
    GBP_PLN = "GBP_PLN"
    GBP_SGD = "GBP_SGD"
    GBP_USD = "GBP_USD"
    GBP_ZAR = "GBP_ZAR"

    # HKD pairs
    HKD_JPY = "HKD_JPY"

    # NZD pairs
    NZD_CAD = "NZD_CAD"
    NZD_CHF = "NZD_CHF"
    NZD_HKD = "NZD_HKD"
    NZD_JPY = "NZD_JPY"
    NZD_SGD = "NZD_SGD"
    NZD_USD = "NZD_USD"

    # SGD pairs
    SGD_CHF = "SGD_CHF"
    SGD_JPY = "SGD_JPY"

    # TRY pairs
    TRY_JPY = "TRY_JPY"

    # USD pairs
    USD_CAD = "USD_CAD"
    USD_CHF = "USD_CHF"
    USD_CNH = "USD_CNH"
    USD_CZK = "USD_CZK"
    USD_DKK = "USD_DKK"
    USD_HKD = "USD_HKD"
    USD_HUF = "USD_HUF"
    USD_JPY = "USD_JPY"
    USD_MXN = "USD_MXN"
    USD_NOK = "USD_NOK"
    USD_PLN = "USD_PLN"
    USD_SEK = "USD_SEK"
    USD_SGD = "USD_SGD"
    USD_THB = "USD_THB"
    USD_TRY = "USD_TRY"
    USD_ZAR = "USD_ZAR"

    # ZAR pairs
    ZAR_JPY = "ZAR_JPY"


class InstrumentType(str, Enum):
    """Types of trading instruments."""

    CURRENCY = "CURRENCY"
    CFD = "CFD"
    METAL = "METAL"


class OrderType(str, Enum):
    """Order types."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET_IF_TOUCHED = "MARKET_IF_TOUCHED"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    GUARANTEED_STOP_LOSS = "GUARANTEED_STOP_LOSS"
    TRAILING_STOP_LOSS = "TRAILING_STOP_LOSS"


class OrderState(str, Enum):
    """Order states."""

    PENDING = "PENDING"
    FILLED = "FILLED"
    TRIGGERED = "TRIGGERED"
    CANCELLED = "CANCELLED"


class Direction(str, Enum):
    """Position direction."""

    LONG = "LONG"
    SHORT = "SHORT"


class TradeState(str, Enum):
    """The current state of a Trade."""

    OPEN = "OPEN"
    CLOSED = "CLOSED"
    CLOSE_WHEN_TRADEABLE = "CLOSE_WHEN_TRADEABLE"


class TimeInForce(str, Enum):
    """Time in force for orders."""

    GTC = "GTC"  # Good Till Cancelled
    GTD = "GTD"  # Good Till Date
    GFD = "GFD"  # Good For Day
    FOK = "FOK"  # Fill Or Kill
    IOC = "IOC"  # Immediate Or Cancel


class OrderPositionFill(str, Enum):
    """How an Order should be filled into existing Positions."""

    OPEN_ONLY = "OPEN_ONLY"
    REDUCE_FIRST = "REDUCE_FIRST"
    REDUCE_ONLY = "REDUCE_ONLY"
    DEFAULT = "DEFAULT"


class OrderTriggerCondition(str, Enum):
    """Condition that must be satisfied before Order becomes fillable."""

    DEFAULT = "DEFAULT"
    INVERSE = "INVERSE"
    BID = "BID"
    ASK = "ASK"
    MID = "MID"


class CandlestickGranularity(str, Enum):
    """Time intervals for candlestick data."""

    # Second-based intervals (minute aligned)
    S5 = "S5"
    S10 = "S10"
    S15 = "S15"
    S30 = "S30"

    # Minute-based intervals (hour aligned)
    M1 = "M1"
    M2 = "M2"
    M4 = "M4"
    M5 = "M5"
    M10 = "M10"
    M15 = "M15"
    M30 = "M30"

    # Hour-based intervals (day aligned)
    H1 = "H1"
    H2 = "H2"
    H3 = "H3"
    H4 = "H4"
    H6 = "H6"
    H8 = "H8"
    H12 = "H12"

    # Day-based intervals (week aligned)
    D = "D"

    # Week-based intervals (month aligned)
    W = "W"

    # Month-based intervals (year aligned)
    M = "M"


class WeeklyAlignment(str, Enum):
    """Days of the week for weekly alignment."""

    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"


class DailyAlignment(int, Enum):
    """Hours for daily alignment (0-23)."""

    MIDNIGHT = 0
    H01 = 1
    H02 = 2
    H03 = 3
    H04 = 4
    H05 = 5
    H06 = 6
    H07 = 7
    H08 = 8
    H09 = 9
    H10 = 10
    H11 = 11
    NOON = 12
    H13 = 13
    H14 = 14
    H15 = 15
    H16 = 16
    H17 = 17
    H18 = 18
    H19 = 19
    H20 = 20
    H21 = 21
    H22 = 22
    H23 = 23


class TransactionType(str, Enum):
    """Types of transactions that can occur."""

    # Account Management
    CREATE = "CREATE"
    CLOSE = "CLOSE"
    REOPEN = "REOPEN"
    CLIENT_CONFIGURE = "CLIENT_CONFIGURE"
    CLIENT_CONFIGURE_REJECT = "CLIENT_CONFIGURE_REJECT"

    # Fund Management
    TRANSFER_FUNDS = "TRANSFER_FUNDS"
    TRANSFER_FUNDS_REJECT = "TRANSFER_FUNDS_REJECT"

    # Order Management
    MARKET_ORDER = "MARKET_ORDER"
    MARKET_ORDER_REJECT = "MARKET_ORDER_REJECT"
    FIXED_PRICE_ORDER = "FIXED_PRICE_ORDER"
    LIMIT_ORDER = "LIMIT_ORDER"
    LIMIT_ORDER_REJECT = "LIMIT_ORDER_REJECT"
    STOP_ORDER = "STOP_ORDER"
    STOP_ORDER_REJECT = "STOP_ORDER_REJECT"
    MARKET_IF_TOUCHED_ORDER = "MARKET_IF_TOUCHED_ORDER"
    MARKET_IF_TOUCHED_ORDER_REJECT = "MARKET_IF_TOUCHED_ORDER_REJECT"
    TAKE_PROFIT_ORDER = "TAKE_PROFIT_ORDER"
    TAKE_PROFIT_ORDER_REJECT = "TAKE_PROFIT_ORDER_REJECT"
    STOP_LOSS_ORDER = "STOP_LOSS_ORDER"
    STOP_LOSS_ORDER_REJECT = "STOP_LOSS_ORDER_REJECT"
    GUARANTEED_STOP_LOSS_ORDER = "GUARANTEED_STOP_LOSS_ORDER"
    GUARANTEED_STOP_LOSS_ORDER_REJECT = "GUARANTEED_STOP_LOSS_ORDER_REJECT"
    TRAILING_STOP_LOSS_ORDER = "TRAILING_STOP_LOSS_ORDER"
    TRAILING_STOP_LOSS_ORDER_REJECT = "TRAILING_STOP_LOSS_ORDER_REJECT"

    # Order Lifecycle
    ORDER_FILL = "ORDER_FILL"
    ORDER_CANCEL = "ORDER_CANCEL"
    ORDER_CANCEL_REJECT = "ORDER_CANCEL_REJECT"
    ORDER_CLIENT_EXTENSIONS_MODIFY = "ORDER_CLIENT_EXTENSIONS_MODIFY"
    ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT = "ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT"

    # Trade Management
    TRADE_CLIENT_EXTENSIONS_MODIFY = "TRADE_CLIENT_EXTENSIONS_MODIFY"
    TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT = "TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT"

    # Position Management
    MARGIN_CALL_ENTER = "MARGIN_CALL_ENTER"
    MARGIN_CALL_EXTEND = "MARGIN_CALL_EXTEND"
    MARGIN_CALL_EXIT = "MARGIN_CALL_EXIT"
    DELAYED_TRADE_CLOSURE = "DELAYED_TRADE_CLOSURE"

    # Financing
    DAILY_FINANCING = "DAILY_FINANCING"
    DIVIDEND_ADJUSTMENT = "DIVIDEND_ADJUSTMENT"

    # Miscellaneous
    RESET_RESETTABLE_PL = "RESET_RESETTABLE_PL"


class TransactionRejectReason(str, Enum):
    """Reasons why a transaction may be rejected."""

    # General
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    INSTRUMENT_PRICE_UNKNOWN = "INSTRUMENT_PRICE_UNKNOWN"
    ACCOUNT_NOT_ACTIVE = "ACCOUNT_NOT_ACTIVE"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_ORDER_CREATION_LOCKED = "ACCOUNT_ORDER_CREATION_LOCKED"
    ACCOUNT_CONFIGURATION_LOCKED = "ACCOUNT_CONFIGURATION_LOCKED"
    ACCOUNT_DEPOSIT_LOCKED = "ACCOUNT_DEPOSIT_LOCKED"
    ACCOUNT_WITHDRAWAL_LOCKED = "ACCOUNT_WITHDRAWAL_LOCKED"
    INSTRUMENT_NOT_TRADEABLE = "INSTRUMENT_NOT_TRADEABLE"
    INSUFFICIENT_MARGIN = "INSUFFICIENT_MARGIN"
    MARKET_HALTED = "MARKET_HALTED"
    PENDING_ORDERS_ALLOWED_EXCEEDED = "PENDING_ORDERS_ALLOWED_EXCEEDED"
    ORDER_ID_UNSPECIFIED = "ORDER_ID_UNSPECIFIED"
    ORDER_ID_INVALID = "ORDER_ID_INVALID"
    ORDER_PARTIAL_FILL_OPTION_MISSING = "ORDER_PARTIAL_FILL_OPTION_MISSING"
    ORDER_PARTIAL_FILL_OPTION_INVALID = "ORDER_PARTIAL_FILL_OPTION_INVALID"


class FundingReason(str, Enum):
    """Reasons for funding transactions."""

    CLIENT_FUNDING = "CLIENT_FUNDING"
    ACCOUNT_TRANSFER = "ACCOUNT_TRANSFER"
    DIVISION_MIGRATION = "DIVISION_MIGRATION"
    SITE_MIGRATION = "SITE_MIGRATION"
    ADJUSTMENT = "ADJUSTMENT"


class GuaranteedStopLossOrderMode(str, Enum):
    """The overall behaviour of an Account regarding guaranteed Stop Loss Orders."""

    DISABLED = "DISABLED"
    ALLOWED = "ALLOWED"
    REQUIRED = "REQUIRED"


class GuaranteedStopLossOrderMutability(str, Enum):
    """Actions that can be performed on guaranteed Stop Loss Orders."""

    FIXED = "FIXED"
    REPLACEABLE = "REPLACEABLE"
    CANCELABLE = "CANCELABLE"
    PRICE_WIDEN_ONLY = "PRICE_WIDEN_ONLY"


class AccountFinancingMode(str, Enum):
    """The financing mode of an Account."""

    NO_FINANCING = "NO_FINANCING"
    SECOND_BY_SECOND = "SECOND_BY_SECOND"
    DAILY = "DAILY"


class PositionAggregationMode(str, Enum):
    """The way that position values for an Account are calculated and aggregated."""

    ABSOLUTE_SUM = "ABSOLUTE_SUM"
    MAXIMAL_SIDE = "MAXIMAL_SIDE"
    NET_SUM = "NET_SUM"


class DayOfWeek(str, Enum):
    """Standard day-of-week enumeration."""

    SUNDAY = "SUNDAY"
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"


class GuaranteedStopLossOrderModeForInstrument(str, Enum):
    """Guaranteed stop loss availability per instrument."""

    DISABLED = "DISABLED"  # Not available for this instrument
    ALLOWED = "ALLOWED"  # Available but optional
    REQUIRED = "REQUIRED"  # Required for all positions


class TradeStateFilter(str, Enum):
    """The state to filter the Trades by."""

    OPEN = "OPEN"  # Currently open trades
    CLOSED = "CLOSED"  # Fully closed trades
    CLOSE_WHEN_TRADEABLE = "CLOSE_WHEN_TRADEABLE"  # Pending closure
    ALL = "ALL"  # All trades regardless of state


class TradePL(str, Enum):
    """The classification of TradePLs."""

    POSITIVE = "POSITIVE"  # Profitable trade P/L
    NEGATIVE = "NEGATIVE"  # Losing trade P/L
    ZERO = "ZERO"  # Zero P/L trade


class OrderStateFilter(str, Enum):
    """Filter Orders by OrderState for aggregation."""

    PENDING = "PENDING"  # Only pending orders
    FILLED = "FILLED"  # Only filled orders
    TRIGGERED = "TRIGGERED"  # Only triggered orders
    CANCELLED = "CANCELLED"  # Only cancelled orders
    ALL = "ALL"  # All orders regardless of state


class CancellableOrderType(str, Enum):
    """The type of Order that can be cancelled."""

    LIMIT = "LIMIT"
    STOP = "STOP"
    MARKET_IF_TOUCHED = "MARKET_IF_TOUCHED"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS = "STOP_LOSS"
    GUARANTEED_STOP_LOSS = "GUARANTEED_STOP_LOSS"
    TRAILING_STOP_LOSS = "TRAILING_STOP_LOSS"


class PriceStatus(str, Enum):
    """Current status of an instrument's pricing."""

    tradeable = "tradeable"  # Instrument is actively tradeable
    non_tradeable = "non-tradeable"  # Instrument is not currently tradeable
    invalid = "invalid"  # Pricing information is invalid


# Type aliases (not classes to avoid Pydantic issues)
AccountID = str
"""Account identifier in format: {site}-{division}-{user}-{account}."""

TradeID = str
"""Trade identifier unique within the Account."""

OrderID = str
"""Order identifier unique within the Account."""

TransactionID = str
"""Transaction identifier unique within the Account."""

RequestID = str
"""Request identifier for correlation."""

PriceValue = Decimal
"""Price value handled as Decimal internally, serialized as string for API precision."""

AccountUnits = Decimal
"""Account currency units handled as Decimal internally, serialized as string for API precision."""
