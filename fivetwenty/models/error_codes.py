"""OANDA API error codes and categories."""

from enum import Enum


class ErrorCategory(str, Enum):
    """OANDA API error categories."""

    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    VALIDATION = "VALIDATION"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    RATE_LIMITING = "RATE_LIMITING"
    SERVER_ERROR = "SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"


class ErrorSeverity(str, Enum):
    """Error severity levels."""

    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class FiveTwentyErrorCode(str, Enum):
    """Comprehensive OANDA API error codes.

    This enum contains all documented error codes from the OANDA v20 REST API
    reference documentation, organized by functional category.
    """

    # Authentication & Authorization Errors
    INSUFFICIENT_AUTHORIZATION = "INSUFFICIENT_AUTHORIZATION"
    INVALID_TOKEN = "INVALID_TOKEN"
    ACCOUNT_NOT_TRADEABLE = "ACCOUNT_NOT_TRADEABLE"

    # Request Validation Errors
    INVALID_REQUEST = "INVALID_REQUEST"
    INVALID_INSTRUMENT = "INVALID_INSTRUMENT"
    PRECISION_EXCEEDED = "PRECISION_EXCEEDED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_VALUE = "INVALID_VALUE"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"

    # Entity Not Found Errors
    TRADE_DOESNT_EXIST = "TRADE_DOESNT_EXIST"
    TRANSACTION_DOESNT_EXIST = "TRANSACTION_DOESNT_EXIST"
    ORDER_DOESNT_EXIST = "ORDER_DOESNT_EXIST"

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Market Order Rejections
    INSUFFICIENT_MARGIN = "INSUFFICIENT_MARGIN"
    INSUFFICIENT_LIQUIDITY = "INSUFFICIENT_LIQUIDITY"
    PRICE_BOUND_VIOLATED = "PRICE_BOUND_VIOLATED"
    INSTRUMENT_PRICE_UNKNOWN = "INSTRUMENT_PRICE_UNKNOWN"
    INSTRUMENT_NOT_TRADEABLE = "INSTRUMENT_NOT_TRADEABLE"
    MARKET_HALTED = "MARKET_HALTED"
    UNITS_INVALID = "UNITS_INVALID"
    CLIENT_TRADE_ID_ALREADY_EXISTS = "CLIENT_TRADE_ID_ALREADY_EXISTS"

    # Stop Loss/Take Profit Order Issues
    STOP_LOSS_ON_FILL_PRICE_PRECISION_EXCEEDED = "STOP_LOSS_ON_FILL_PRICE_PRECISION_EXCEEDED"
    STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID = "STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID"
    STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID = "STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID"
    TAKE_PROFIT_ON_FILL_PRICE_INVALID = "TAKE_PROFIT_ON_FILL_PRICE_INVALID"
    TAKE_PROFIT_ON_FILL_PRICE_MISSING = "TAKE_PROFIT_ON_FILL_PRICE_MISSING"

    # Guaranteed Stop Loss Issues
    GUARANTEED_STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID = "GUARANTEED_STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID"
    GUARANTEED_STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID = "GUARANTEED_STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID"
    GUARANTEED_STOP_LOSS_ORDER_HALTED_CREATE_VIOLATION = "GUARANTEED_STOP_LOSS_ORDER_HALTED_CREATE_VIOLATION"
    GUARANTEED_STOP_LOSS_ORDER_LEVEL_RESTRICTION_EXCEEDED = "GUARANTEED_STOP_LOSS_ORDER_LEVEL_RESTRICTION_EXCEEDED"

    # Position/Account Limits
    ACCOUNT_POSITION_VALUE_LIMIT_EXCEEDED = "ACCOUNT_POSITION_VALUE_LIMIT_EXCEEDED"
    POSITION_SIZE_EXCEEDED = "POSITION_SIZE_EXCEEDED"
    OPEN_TRADES_ALLOWED_EXCEEDED = "OPEN_TRADES_ALLOWED_EXCEEDED"
    PENDING_ORDERS_ALLOWED_EXCEEDED = "PENDING_ORDERS_ALLOWED_EXCEEDED"

    # Price and Distance Validation
    PRICE_INVALID = "PRICE_INVALID"
    PRICE_MISSING = "PRICE_MISSING"
    PRICE_PRECISION_EXCEEDED = "PRICE_PRECISION_EXCEEDED"
    PRICE_DISTANCE_INVALID = "PRICE_DISTANCE_INVALID"
    PRICE_DISTANCE_MAXIMUM_EXCEEDED = "PRICE_DISTANCE_MAXIMUM_EXCEEDED"
    PRICE_DISTANCE_PRECISION_EXCEEDED = "PRICE_DISTANCE_PRECISION_EXCEEDED"

    # Client ID and Extension Errors
    CLIENT_ORDER_ID_INVALID = "CLIENT_ORDER_ID_INVALID"
    CLIENT_ORDER_ID_ALREADY_EXISTS = "CLIENT_ORDER_ID_ALREADY_EXISTS"
    CLIENT_TRADE_ID_INVALID = "CLIENT_TRADE_ID_INVALID"
    CLIENT_ORDER_COMMENT_INVALID = "CLIENT_ORDER_COMMENT_INVALID"
    CLIENT_ORDER_TAG_INVALID = "CLIENT_ORDER_TAG_INVALID"

    # Market State Errors
    INSTRUMENT_ASK_HALTED = "INSTRUMENT_ASK_HALTED"
    INSTRUMENT_BID_HALTED = "INSTRUMENT_BID_HALTED"
    INSTRUMENT_ASK_REDUCE_ONLY = "INSTRUMENT_ASK_REDUCE_ONLY"
    INSTRUMENT_BID_REDUCE_ONLY = "INSTRUMENT_BID_REDUCE_ONLY"


# Error code categorization mapping
ERROR_CODE_CATEGORIES = {
    # Authentication & Authorization
    FiveTwentyErrorCode.INSUFFICIENT_AUTHORIZATION: ErrorCategory.AUTHORIZATION,
    FiveTwentyErrorCode.INVALID_TOKEN: ErrorCategory.AUTHENTICATION,
    FiveTwentyErrorCode.ACCOUNT_NOT_TRADEABLE: ErrorCategory.AUTHORIZATION,
    # Request Validation
    FiveTwentyErrorCode.INVALID_REQUEST: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.INVALID_INSTRUMENT: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRECISION_EXCEEDED: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.VALIDATION_ERROR: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.INVALID_VALUE: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.MISSING_REQUIRED_FIELD: ErrorCategory.VALIDATION,
    # Entity Not Found
    FiveTwentyErrorCode.TRADE_DOESNT_EXIST: ErrorCategory.NOT_FOUND,
    FiveTwentyErrorCode.TRANSACTION_DOESNT_EXIST: ErrorCategory.NOT_FOUND,
    FiveTwentyErrorCode.ORDER_DOESNT_EXIST: ErrorCategory.NOT_FOUND,
    # Rate Limiting
    FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED: ErrorCategory.RATE_LIMITING,
    # Business Logic - Market Order Rejections
    FiveTwentyErrorCode.INSUFFICIENT_MARGIN: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSUFFICIENT_LIQUIDITY: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.PRICE_BOUND_VIOLATED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSTRUMENT_PRICE_UNKNOWN: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.MARKET_HALTED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.UNITS_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.CLIENT_TRADE_ID_ALREADY_EXISTS: ErrorCategory.VALIDATION,
    # Business Logic - Stop Loss/Take Profit
    FiveTwentyErrorCode.STOP_LOSS_ON_FILL_PRICE_PRECISION_EXCEEDED: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.TAKE_PROFIT_ON_FILL_PRICE_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.TAKE_PROFIT_ON_FILL_PRICE_MISSING: ErrorCategory.VALIDATION,
    # Business Logic - Guaranteed Stop Loss
    FiveTwentyErrorCode.GUARANTEED_STOP_LOSS_ON_FILL_TIME_IN_FORCE_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.GUARANTEED_STOP_LOSS_ON_FILL_TRIGGER_CONDITION_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.GUARANTEED_STOP_LOSS_ORDER_HALTED_CREATE_VIOLATION: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.GUARANTEED_STOP_LOSS_ORDER_LEVEL_RESTRICTION_EXCEEDED: ErrorCategory.BUSINESS_LOGIC,
    # Business Logic - Position/Account Limits
    FiveTwentyErrorCode.ACCOUNT_POSITION_VALUE_LIMIT_EXCEEDED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.POSITION_SIZE_EXCEEDED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.OPEN_TRADES_ALLOWED_EXCEEDED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.PENDING_ORDERS_ALLOWED_EXCEEDED: ErrorCategory.BUSINESS_LOGIC,
    # Validation - Price and Distance
    FiveTwentyErrorCode.PRICE_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRICE_MISSING: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRICE_PRECISION_EXCEEDED: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRICE_DISTANCE_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRICE_DISTANCE_MAXIMUM_EXCEEDED: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.PRICE_DISTANCE_PRECISION_EXCEEDED: ErrorCategory.VALIDATION,
    # Validation - Client ID and Extensions
    FiveTwentyErrorCode.CLIENT_ORDER_ID_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.CLIENT_ORDER_ID_ALREADY_EXISTS: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.CLIENT_TRADE_ID_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.CLIENT_ORDER_COMMENT_INVALID: ErrorCategory.VALIDATION,
    FiveTwentyErrorCode.CLIENT_ORDER_TAG_INVALID: ErrorCategory.VALIDATION,
    # Business Logic - Market State
    FiveTwentyErrorCode.INSTRUMENT_ASK_HALTED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSTRUMENT_BID_HALTED: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSTRUMENT_ASK_REDUCE_ONLY: ErrorCategory.BUSINESS_LOGIC,
    FiveTwentyErrorCode.INSTRUMENT_BID_REDUCE_ONLY: ErrorCategory.BUSINESS_LOGIC,
}


# Error severity mapping
ERROR_CODE_SEVERITIES = {
    # Critical - Authentication/Authorization issues
    FiveTwentyErrorCode.INSUFFICIENT_AUTHORIZATION: ErrorSeverity.CRITICAL,
    FiveTwentyErrorCode.INVALID_TOKEN: ErrorSeverity.CRITICAL,
    FiveTwentyErrorCode.ACCOUNT_NOT_TRADEABLE: ErrorSeverity.CRITICAL,
    # Error - Validation issues
    FiveTwentyErrorCode.INVALID_REQUEST: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.INVALID_INSTRUMENT: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.PRECISION_EXCEEDED: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.VALIDATION_ERROR: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.INVALID_VALUE: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.MISSING_REQUIRED_FIELD: ErrorSeverity.ERROR,
    # Warning - Entity not found
    FiveTwentyErrorCode.TRADE_DOESNT_EXIST: ErrorSeverity.WARNING,
    FiveTwentyErrorCode.TRANSACTION_DOESNT_EXIST: ErrorSeverity.WARNING,
    FiveTwentyErrorCode.ORDER_DOESNT_EXIST: ErrorSeverity.WARNING,
    # Warning - Rate limiting
    FiveTwentyErrorCode.RATE_LIMIT_EXCEEDED: ErrorSeverity.WARNING,
    # Error - Business logic rejections
    FiveTwentyErrorCode.INSUFFICIENT_MARGIN: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.INSUFFICIENT_LIQUIDITY: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.PRICE_BOUND_VIOLATED: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.INSTRUMENT_PRICE_UNKNOWN: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.INSTRUMENT_NOT_TRADEABLE: ErrorSeverity.ERROR,
    FiveTwentyErrorCode.MARKET_HALTED: ErrorSeverity.ERROR,
}


def get_error_category(error_code: str | FiveTwentyErrorCode | None) -> ErrorCategory | None:
    """Get the category for an error code."""
    if error_code is None:
        return None

    if isinstance(error_code, str):
        try:
            error_code = FiveTwentyErrorCode(error_code)
        except ValueError:
            return None

    return ERROR_CODE_CATEGORIES.get(error_code)


def get_error_severity(error_code: str | FiveTwentyErrorCode | None) -> ErrorSeverity:
    """Get the severity for an error code."""
    if error_code is None:
        return ErrorSeverity.ERROR

    if isinstance(error_code, str):
        try:
            error_code = FiveTwentyErrorCode(error_code)
        except ValueError:
            return ErrorSeverity.ERROR

    return ERROR_CODE_SEVERITIES.get(error_code, ErrorSeverity.ERROR)
