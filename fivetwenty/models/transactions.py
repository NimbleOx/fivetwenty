"""
Transaction models for OANDA API.

Contains all transaction-related data structures, including base transaction types,
specific transaction implementations, filters, and streaming models for the OANDA REST API.
These models represent the audit trail and history of all account activities.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field

from .base import ApiModel
from .enums import (
    AccountUnits,
    Currency,
    InstrumentName,
    OrderPositionFill,
    OrderTriggerCondition,
    PriceValue,
    TimeInForce,
    TransactionType,
)
from .orders import ClientExtensions

# Forward references for type checking


class Transaction(ApiModel):
    """Base transaction model with common fields for all transaction types."""

    id: str = Field(alias="id")
    time: str
    user_id: int = Field(alias="userID")
    account_id: str = Field(alias="accountID")
    batch_id: str = Field(alias="batchID")
    request_id: str | None = Field(None, alias="requestID")
    type: TransactionType


class OrderFillTransaction(Transaction):
    """Transaction representing the filling of an Order."""

    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    instrument: InstrumentName
    units: Decimal
    gain_quote_home_conversion_factor: Decimal | None = Field(None, alias="gainQuoteHomeConversionFactor")
    loss_quote_home_conversion_factor: Decimal | None = Field(None, alias="lossQuoteHomeConversionFactor")
    price: PriceValue | None = None
    full_vwap: PriceValue | None = Field(None, alias="fullVWAP")
    full_price: PriceValue | None = Field(None, alias="fullPrice")
    reason: str | None = None
    pl: Decimal | None = Field(None, alias="pl")
    financing: Decimal | None = None
    commission: Decimal | None = None
    guarantee_execution_fee: Decimal | None = Field(None, alias="guaranteeExecutionFee")
    account_balance: Decimal | None = Field(None, alias="accountBalance")
    trade_opened: dict[str, Any] | None = Field(None, alias="tradeOpened")
    trades_closed: list[dict[str, Any]] | None = Field(None, alias="tradesClosed")
    trade_reduced: dict[str, Any] | None = Field(None, alias="tradeReduced")
    half_spread_cost: Decimal | None = Field(None, alias="halfSpreadCost")


class OrderCancelTransaction(Transaction):
    """Transaction representing the cancellation of an Order."""

    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    reason: str | None = None
    replaced_by_order_id: str | None = Field(None, alias="replacedByOrderID")


class MarketOrderTransaction(Transaction):
    """Transaction representing the creation of a Market Order."""

    instrument: InstrumentName
    units: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trade_close: dict[str, Any] | None = Field(None, alias="tradeClose")
    long_position_closeout: dict[str, Any] | None = Field(None, alias="longPositionCloseout")
    short_position_closeout: dict[str, Any] | None = Field(None, alias="shortPositionCloseout")
    margin_closeout: dict[str, Any] | None = Field(None, alias="marginCloseout")
    delayed_trade_close: dict[str, Any] | None = Field(None, alias="delayedTradeClose")
    reason: str | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: dict[str, Any] | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="stopLossOnFill")
    trailing_stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")


class CreateTransaction(Transaction):
    """Account creation transaction."""

    type: TransactionType = Field(default=TransactionType.CREATE, frozen=True)
    division_id: int = Field(alias="divisionID")
    site_id: int = Field(alias="siteID")
    account_user_id: int = Field(alias="accountUserID")
    account_number: int = Field(alias="accountNumber")
    home_currency: Currency = Field(alias="homeCurrency")


class ClientConfigureTransaction(Transaction):
    """Client configuration change transaction."""

    type: TransactionType = Field(default=TransactionType.CLIENT_CONFIGURE, frozen=True)
    alias: str | None = None
    margin_rate: Decimal | None = Field(None, alias="marginRate")


class ClientConfigureRejectTransaction(Transaction):
    """Client configuration rejection transaction."""

    type: TransactionType = Field(default=TransactionType.CLIENT_CONFIGURE_REJECT, frozen=True)
    alias: str | None = None
    margin_rate: Decimal | None = Field(None, alias="marginRate")
    reject_reason: str = Field(alias="rejectReason")


class LimitOrderTransaction(Transaction):
    """Limit order creation transaction."""

    type: TransactionType = Field(default=TransactionType.LIMIT_ORDER, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: dict[str, Any] | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="stopLossOnFill")
    trailing_stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: str | None = None


class LimitOrderRejectTransaction(Transaction):
    """Limit order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.LIMIT_ORDER_REJECT, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class MarketOrderRejectTransaction(Transaction):
    """Market order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_ORDER_REJECT, frozen=True)
    instrument: InstrumentName
    units: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    reject_reason: str = Field(alias="rejectReason")


class StopOrderTransaction(Transaction):
    """Stop order creation transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_ORDER, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: dict[str, Any] | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="stopLossOnFill")
    trailing_stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: str | None = None


class StopOrderRejectTransaction(Transaction):
    """Stop order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_ORDER_REJECT, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class TakeProfitOrderTransaction(Transaction):
    """Take profit order creation transaction."""

    type: TransactionType = Field(default=TransactionType.TAKE_PROFIT_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: str | None = None


class TakeProfitOrderRejectTransaction(Transaction):
    """Take profit order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TAKE_PROFIT_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class StopLossOrderTransaction(Transaction):
    """Stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    guaranteed: bool = Field(default=False)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: str | None = None


class StopLossOrderRejectTransaction(Transaction):
    """Stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class TrailingStopLossOrderTransaction(Transaction):
    """Trailing stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.TRAILING_STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: str | None = None


class TrailingStopLossOrderRejectTransaction(Transaction):
    """Trailing stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TRAILING_STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class GuaranteedStopLossOrderTransaction(Transaction):
    """Guaranteed stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.GUARANTEED_STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    guaranteed_execution_premium: AccountUnits = Field(alias="guaranteedExecutionPremium")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: str | None = None


class GuaranteedStopLossOrderRejectTransaction(Transaction):
    """Guaranteed stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.GUARANTEED_STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class MarketIfTouchedOrderTransaction(Transaction):
    """Market if touched order creation transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_IF_TOUCHED_ORDER, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: dict[str, Any] | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="stopLossOnFill")
    trailing_stop_loss_on_fill: dict[str, Any] | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: str | None = None


class MarketIfTouchedOrderRejectTransaction(Transaction):
    """Market if touched order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_IF_TOUCHED_ORDER_REJECT, frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    reject_reason: str = Field(alias="rejectReason")


class OrderCancelRejectTransaction(Transaction):
    """Order cancel rejection transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_CANCEL_REJECT, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    reject_reason: str = Field(alias="rejectReason")


class OrderClientExtensionsModifyTransaction(Transaction):
    """Order client extensions modification transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_CLIENT_EXTENSIONS_MODIFY, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    client_extensions_modify: ClientExtensions = Field(alias="clientExtensionsModify")
    trade_client_extensions_modify: ClientExtensions | None = Field(None, alias="tradeClientExtensionsModify")


class TradeClientExtensionsModifyTransaction(Transaction):
    """Trade client extensions modification transaction."""

    type: TransactionType = Field(default=TransactionType.TRADE_CLIENT_EXTENSIONS_MODIFY, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    trade_client_extensions_modify: ClientExtensions = Field(alias="tradeClientExtensionsModify")


class MarginCallEnterTransaction(Transaction):
    """Margin call enter transaction."""

    type: TransactionType = Field(default=TransactionType.MARGIN_CALL_ENTER, frozen=True)


class MarginCallExitTransaction(Transaction):
    """Margin call exit transaction."""

    type: TransactionType = Field(default=TransactionType.MARGIN_CALL_EXIT, frozen=True)


class DailyFinancingTransaction(Transaction):
    """Daily financing transaction."""

    type: TransactionType = Field(default=TransactionType.DAILY_FINANCING, frozen=True)
    financing: AccountUnits
    account_balance: AccountUnits = Field(alias="accountBalance")
    position_financings: list[dict[str, Any]] = Field(default_factory=list, alias="positionFinancings")


class DividendAdjustmentTransaction(Transaction):
    """Dividend adjustment transaction."""

    type: TransactionType = Field(default=TransactionType.DIVIDEND_ADJUSTMENT, frozen=True)
    instrument: InstrumentName
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment")
    account_balance: AccountUnits = Field(alias="accountBalance")


class ResetResettablePLTransaction(Transaction):
    """Reset resettable P&L transaction."""

    type: TransactionType = Field(default=TransactionType.RESET_RESETTABLE_PL, frozen=True)


class CloseTransaction(Transaction):
    """Account close transaction."""

    type: TransactionType = Field(default=TransactionType.CLOSE, frozen=True)


class ReopenTransaction(Transaction):
    """Account reopen transaction."""

    type: TransactionType = Field(default=TransactionType.REOPEN, frozen=True)


class TransferFundsTransaction(Transaction):
    """Fund transfer transaction."""

    type: TransactionType = Field(default=TransactionType.TRANSFER_FUNDS, frozen=True)
    amount: AccountUnits
    funding_reason: str = Field(alias="fundingReason")
    comment: str | None = None


class TransferFundsRejectTransaction(Transaction):
    """Fund transfer rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TRANSFER_FUNDS_REJECT, frozen=True)
    amount: AccountUnits
    funding_reason: str = Field(alias="fundingReason")
    comment: str | None = None
    reject_reason: str = Field(alias="rejectReason")


class MarginCallExtendTransaction(Transaction):
    """Margin call extension transaction."""

    type: TransactionType = Field(default=TransactionType.MARGIN_CALL_EXTEND, frozen=True)
    extension_number: int = Field(alias="extensionNumber")


class FixedPriceOrderTransaction(Transaction):
    """Fixed price order transaction (for dividend adjustments, etc.)."""

    type: TransactionType = Field(default=TransactionType.ORDER_FILL, frozen=True)  # Use closest match
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trade_state: str = Field(alias="tradeState")
    reason: str


class DelayedTradeCloseTransaction(Transaction):
    """Delayed trade close transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_FILL, frozen=True)  # Use closest match
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    reason: str
    source_transaction_id: str = Field(alias="sourceTransactionID")


class TransactionFilter(ApiModel):
    """Filter for transaction queries."""

    from_: str | None = Field(None, alias="from")
    to: str | None = None
    page_size: int | None = Field(None, alias="pageSize")
    type_filter: list[TransactionType] | None = Field(None, alias="type")


class TransactionIDRange(ApiModel):
    """Range of transaction IDs."""

    from_: str = Field(alias="from")
    to: str


# Removed extra transaction models that are not part of official OANDA v20 API:
# - TransactionHeartbeat, TransactionRejectDetails, TransactionSummary, TransactionBatch
# - AccountChangesState, AccountChanges (these are now properly in accounts.py)


# Export all transaction-related models
__all__ = [
    "ClientConfigureRejectTransaction",
    "ClientConfigureTransaction",
    "CloseTransaction",
    "CreateTransaction",
    "DailyFinancingTransaction",
    "DelayedTradeCloseTransaction",
    "DividendAdjustmentTransaction",
    "FixedPriceOrderTransaction",
    "GuaranteedStopLossOrderRejectTransaction",
    "GuaranteedStopLossOrderTransaction",
    "LimitOrderRejectTransaction",
    "LimitOrderTransaction",
    "MarginCallEnterTransaction",
    "MarginCallExitTransaction",
    "MarginCallExtendTransaction",
    "MarketIfTouchedOrderRejectTransaction",
    "MarketIfTouchedOrderTransaction",
    "MarketOrderRejectTransaction",
    "MarketOrderTransaction",
    "OrderCancelRejectTransaction",
    "OrderCancelTransaction",
    "OrderClientExtensionsModifyTransaction",
    "OrderFillTransaction",
    "ReopenTransaction",
    "ResetResettablePLTransaction",
    "StopLossOrderRejectTransaction",
    "StopLossOrderTransaction",
    "StopOrderRejectTransaction",
    "StopOrderTransaction",
    "TakeProfitOrderRejectTransaction",
    "TakeProfitOrderTransaction",
    "TradeClientExtensionsModifyTransaction",
    "TrailingStopLossOrderRejectTransaction",
    "TrailingStopLossOrderTransaction",
    "Transaction",
    "TransactionFilter",
    "TransactionIDRange",
    "TransferFundsRejectTransaction",
    "TransferFundsTransaction",
]
