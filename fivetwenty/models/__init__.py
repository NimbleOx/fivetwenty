"""
OANDA API model definitions.

This package contains Pydantic models for all OANDA API data structures,
organized by domain:

- base: Base model classes
- enums: Enumeration types and type aliases
- accounts: Account-related models
- instruments: Instrument-related models
- orders: Order-related models
- trades: Trade-related models
- positions: Position-related models
- pricing: Pricing and market data models
- transactions: Transaction-related models
- streaming: Streaming and real-time connection models
- error_codes: Error codes and categories
- error_details: Structured error information
"""

from .accounts import *
from .base import *
from .enums import *
from .error_codes import *
from .error_details import *
from .instruments import *
from .instruments import GuaranteedStopLossOrderLevelRestriction
from .orders import *
from .positions import *
from .positions import CalculatedPositionState, Position
from .pricing import *
from .pricing import OrderBook
from .streaming import *

# Removed streaming wrapper models - streaming endpoints return actual data models
from .trades import *

# Rebuild all models to resolve forward references
from .trades import CalculatedTradeState, Trade, TradeSummary
from .transactions import *

# AccountChanges and AccountChangesState moved to accounts.py

# Rebuild models that have forward references
AccountChangesState.model_rebuild()
AccountChanges.model_rebuild()
Account.model_rebuild()
AccountSummary.model_rebuild()
Trade.model_rebuild()

__all__ = [
    "Account",
    "AccountChanges",
    "AccountChanges",
    "AccountChangesState",
    "AccountChangesState",
    "AccountFinancingMode",
    # Type aliases
    "AccountID",
    # Account models
    "AccountProperties",
    "AccountSummary",
    "AccountUnits",
    "AccumulatedAccountState",
    "ApiErrorResponse",
    # Base model
    "ApiModel",
    "ApiRateLimitInfo",
    "ApiValidationSchema",
    "CalculatedAccountState",
    "CalculatedPositionState",
    "CalculatedTradeState",
    "CancellableOrderType",
    "Candlestick",
    "CandlestickData",
    "CandlestickGranularity",
    "CandlestickResponse",
    "ClientConfigureRejectTransaction",
    "ClientConfigureTransaction",
    # Order supporting models
    "ClientExtensions",
    # Pricing models
    "ClientPrice",
    "CloseTransaction",
    "CreateTransaction",
    # Enums and core types
    "Currency",
    "DailyAlignment",
    "DailyFinancingTransaction",
    "DayOfWeek",
    "DelayedTradeCloseTransaction",
    "Direction",
    "DividendAdjustmentTransaction",
    "DynamicOrderState",
    # Error handling
    "ErrorCategory",
    "ErrorContext",
    "ErrorDetails",
    "ErrorSeverity",
    "FieldValidation",
    "FiveTwentyErrorCode",
    "FixedPriceOrder",
    "FixedPriceOrderTransaction",
    "FundingReason",
    "GuaranteedStopLossDetails",
    "GuaranteedStopLossOrder",
    "GuaranteedStopLossOrderEntryData",
    "GuaranteedStopLossOrderLevelRestriction",
    "GuaranteedStopLossOrderMode",
    "GuaranteedStopLossOrderModeForInstrument",
    "GuaranteedStopLossOrderMutability",
    "GuaranteedStopLossOrderParameters",
    "GuaranteedStopLossOrderRequest",
    "GuaranteedStopLossOrderTransaction",
    "HomeConversions",
    # Instrument models
    "Instrument",
    "InstrumentCommission",
    "InstrumentFinancing",
    "InstrumentName",
    "InstrumentType",
    "LimitOrder",
    "LimitOrderRejectTransaction",
    "LimitOrderRequest",
    "LimitOrderTransaction",
    "MarginCallEnterTransaction",
    "MarginCallExitTransaction",
    "MarginCallExtendTransaction",
    "MarketIfTouchedOrder",
    "MarketIfTouchedOrderRequest",
    "MarketIfTouchedOrderTransaction",
    # Order state models
    "MarketOrder",
    "MarketOrderDelayedTradeClose",
    "MarketOrderMarginCloseout",
    "MarketOrderPositionCloseout",
    # Order models
    "MarketOrderRequest",
    "MarketOrderTradeClose",
    "MarketOrderTransaction",
    "OrderBook",
    "OrderCancelRejectTransaction",
    "OrderCancelTransaction",
    "OrderClientExtensionsModifyTransaction",
    "OrderFillTransaction",
    "OrderID",
    "OrderPositionFill",
    "OrderResponse",
    "OrderState",
    "OrderStateFilter",
    "OrderTriggerCondition",
    "OrderType",
    # Position models
    "Position",
    "PositionAggregationMode",
    "PositionSide",
    "PriceBucket",
    "PriceStatus",
    "PriceValue",
    "PricingHeartbeat",
    "QuoteHomeConversionFactors",
    "ReconnectionPolicy",
    "ReopenTransaction",
    "RequestID",
    "ResetResettablePLTransaction",
    "StopLossDetails",
    "StopLossOrder",
    "StopLossOrderRequest",
    "StopLossOrderTransaction",
    "StopOrder",
    "StopOrderRejectTransaction",
    "StopOrderRequest",
    "StopOrderTransaction",
    # Streaming utilities
    "StreamState",
    "StreamingConfiguration",
    "Tag",
    "TakeProfitDetails",
    "TakeProfitOrder",
    "TakeProfitOrderRequest",
    "TakeProfitOrderTransaction",
    "TimeInForce",
    # Trade models
    "Trade",
    "TradeClientExtensionsModifyTransaction",
    "TradeID",
    "TradePL",
    "TradeState",
    "TradeStateFilter",
    "TradeSummary",
    "TrailingStopLossDetails",
    "TrailingStopLossOrder",
    "TrailingStopLossOrderRequest",
    "TrailingStopLossOrderTransaction",
    # Transaction models
    "Transaction",
    "TransactionFilter",
    "TransactionID",
    "TransactionIDRange",
    "TransactionRejectReason",
    "TransactionType",
    "TransferFundsRejectTransaction",
    "TransferFundsTransaction",
    "UnitsAvailable",
    "UnitsAvailableDetails",
    "UserAttributes",
    "ValidationRuleViolation",
    "ValidationViolation",
    "WeeklyAlignment",
]
