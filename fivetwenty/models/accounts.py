"""
Account-related models for OANDA API.

This module contains all account-related data structures including basic account
information, account summaries, account change tracking, and streaming updates.
"""

from __future__ import annotations

# Forward references for type checking
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from datetime import datetime

from pydantic import Field

from .base import ApiModel
from .enums import (
    AccountID,
    AccountUnits,
    Currency,
    GuaranteedStopLossOrderMode,
    GuaranteedStopLossOrderMutability,
    TransactionID,
)
from .orders import (
    DynamicOrderState,
    GuaranteedStopLossOrder,
    LimitOrder,
    MarketIfTouchedOrder,
    MarketOrder,
    StopLossOrder,
    StopOrder,
    TakeProfitOrder,
    TrailingStopLossOrder,
)

if TYPE_CHECKING:
    from decimal import Decimal

    from .positions import Position
    from .trades import TradeSummary

# Union type for all possible order types in an account
Order = (
    MarketOrder
    | LimitOrder
    | StopOrder
    | MarketIfTouchedOrder
    | TakeProfitOrder
    | StopLossOrder
    | GuaranteedStopLossOrder
    | TrailingStopLossOrder
)


class AccountProperties(ApiModel):
    """Basic account information."""

    id: AccountID
    mt4_account_id: int | None = Field(None, alias="mt4AccountID")
    tags: list[str] = Field(default_factory=list)


class Account(ApiModel):
    """Complete account details."""

    id: AccountID
    alias: str | None = None
    currency: Currency
    balance: AccountUnits
    created_by_user_id: int = Field(alias="createdByUserID")
    created_time: datetime = Field(alias="createdTime")
    guaranteed_stop_loss_order_parameters: GuaranteedStopLossOrderParameters | None = Field(None, alias="guaranteedStopLossOrderParameters")
    guaranteed_stop_loss_order_mode: GuaranteedStopLossOrderMode = Field(alias="guaranteedStopLossOrderMode", default=GuaranteedStopLossOrderMode.DISABLED)
    guaranteed_stop_loss_order_mutability: GuaranteedStopLossOrderMutability | None = Field(None, alias="guaranteedStopLossOrderMutability")  # Deprecated but still in API
    resettable_pl_time: datetime | None = Field(None, alias="resettablePLTime")
    margin_rate: Decimal | None = Field(None, alias="marginRate")
    open_trade_count: int = Field(alias="openTradeCount")
    open_position_count: int = Field(alias="openPositionCount")
    pending_order_count: int = Field(alias="pendingOrderCount")
    hedging_enabled: bool = Field(alias="hedgingEnabled")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    nav: AccountUnits = Field(alias="NAV")
    margin_used: AccountUnits = Field(alias="marginUsed")
    margin_available: AccountUnits = Field(alias="marginAvailable")
    position_value: AccountUnits = Field(alias="positionValue")
    margin_closeout_unrealized_pl: AccountUnits = Field(alias="marginCloseoutUnrealizedPL")
    margin_closeout_nav: AccountUnits = Field(alias="marginCloseoutNAV")
    margin_closeout_margin_used: AccountUnits = Field(alias="marginCloseoutMarginUsed")
    margin_closeout_percent: Decimal = Field(alias="marginCloseoutPercent")
    margin_closeout_position_value: Decimal = Field(alias="marginCloseoutPositionValue")
    withdrawal_limit: AccountUnits = Field(alias="withdrawalLimit")
    margin_call_margin_used: AccountUnits = Field(alias="marginCallMarginUsed")
    margin_call_percent: Decimal = Field(alias="marginCallPercent")
    pl: AccountUnits = Field(alias="pl")  # Total lifetime P&L
    resettable_pl: AccountUnits = Field(alias="resettablePL")
    financing: AccountUnits = Field(alias="financing")
    commission: AccountUnits = Field(alias="commission")
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment")
    guaranteed_execution_fees: AccountUnits = Field(alias="guaranteedExecutionFees")
    margin_call_enter_time: datetime | None = Field(None, alias="marginCallEnterTime")
    margin_call_extension_count: int | None = Field(None, alias="marginCallExtensionCount")
    last_margin_call_extension_time: datetime | None = Field(None, alias="lastMarginCallExtensionTime")
    last_transaction_id: TransactionID = Field(alias="lastTransactionID")
    trades: list[TradeSummary] = Field(default_factory=list)
    positions: list[Position] = Field(default_factory=list)
    orders: list[Order] = Field(default_factory=list)


class GuaranteedStopLossOrderParameters(ApiModel):
    """The current mutability and hedging settings related to guaranteed Stop Loss orders."""

    mutability_market_open: GuaranteedStopLossOrderMutability = Field(alias="mutabilityMarketOpen")
    mutability_market_halted: GuaranteedStopLossOrderMutability = Field(alias="mutabilityMarketHalted")


class AccountSummary(ApiModel):
    """A summary representation of a client's Account."""

    id: AccountID
    alias: str | None = None
    currency: Currency
    created_by_user_id: int = Field(alias="createdByUserID")
    created_time: datetime = Field(alias="createdTime")
    guaranteed_stop_loss_order_parameters: GuaranteedStopLossOrderParameters | None = Field(None, alias="guaranteedStopLossOrderParameters")
    guaranteed_stop_loss_order_mode: GuaranteedStopLossOrderMode = Field(alias="guaranteedStopLossOrderMode")
    resettable_pl_time: datetime | None = Field(None, alias="resettablePLTime")
    margin_rate: Decimal | None = Field(None, alias="marginRate")
    open_trade_count: int = Field(alias="openTradeCount")
    open_position_count: int = Field(alias="openPositionCount")
    pending_order_count: int = Field(alias="pendingOrderCount")
    hedging_enabled: bool = Field(alias="hedgingEnabled")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    nav: AccountUnits = Field(alias="NAV")
    margin_used: AccountUnits = Field(alias="marginUsed")
    margin_available: AccountUnits = Field(alias="marginAvailable")
    position_value: AccountUnits = Field(alias="positionValue")
    margin_closeout_unrealized_pl: AccountUnits = Field(alias="marginCloseoutUnrealizedPL")
    margin_closeout_nav: AccountUnits = Field(alias="marginCloseoutNAV")
    margin_closeout_margin_used: AccountUnits = Field(alias="marginCloseoutMarginUsed")
    margin_closeout_percent: Decimal = Field(alias="marginCloseoutPercent")
    margin_closeout_position_value: Decimal = Field(alias="marginCloseoutPositionValue")
    withdrawal_limit: AccountUnits = Field(alias="withdrawalLimit")
    margin_call_margin_used: AccountUnits = Field(alias="marginCallMarginUsed")
    margin_call_percent: Decimal = Field(alias="marginCallPercent")
    balance: AccountUnits
    pl: AccountUnits = Field(alias="pl")
    resettable_pl: AccountUnits = Field(alias="resettablePL")
    financing: AccountUnits = Field(alias="financing")
    commission: AccountUnits = Field(alias="commission")
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment")
    guaranteed_execution_fees: AccountUnits = Field(alias="guaranteedExecutionFees")
    margin_call_enter_time: datetime | None = Field(None, alias="marginCallEnterTime")
    margin_call_extension_count: int | None = Field(None, alias="marginCallExtensionCount")
    last_margin_call_extension_time: datetime | None = Field(None, alias="lastMarginCallExtensionTime")
    last_transaction_id: TransactionID = Field(alias="lastTransactionID")


class UserAttributes(ApiModel):
    """Contains the attributes of a user."""

    user_id: int = Field(alias="userID")
    username: str
    title: str
    name: str
    email: str
    division_abbreviation: str = Field(alias="divisionAbbreviation")
    language_abbreviation: str = Field(alias="languageAbbreviation")
    home_currency: Currency = Field(alias="homeCurrency")


class AccumulatedAccountState(ApiModel):
    """Interface for accumulated account state."""

    balance: AccountUnits
    pl: AccountUnits
    resettable_pl: AccountUnits = Field(alias="resettablePL")
    financing: AccountUnits
    commission: AccountUnits
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment")
    guaranteed_execution_fees: AccountUnits = Field(alias="guaranteedExecutionFees")


class CalculatedAccountState(ApiModel):
    """Interface for calculated account state."""

    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    nav: AccountUnits = Field(alias="NAV")
    margin_used: AccountUnits = Field(alias="marginUsed")
    margin_available: AccountUnits = Field(alias="marginAvailable")
    position_value: AccountUnits = Field(alias="positionValue")
    margin_closeout_unrealized_pl: AccountUnits = Field(alias="marginCloseoutUnrealizedPL")
    margin_closeout_nav: AccountUnits = Field(alias="marginCloseoutNAV")
    margin_closeout_margin_used: AccountUnits = Field(alias="marginCloseoutMarginUsed")
    margin_closeout_percent: Decimal = Field(alias="marginCloseoutPercent")
    margin_closeout_position_value: Decimal = Field(alias="marginCloseoutPositionValue")
    withdrawal_limit: AccountUnits = Field(alias="withdrawalLimit")
    margin_call_margin_used: AccountUnits = Field(alias="marginCallMarginUsed")
    margin_call_percent: Decimal = Field(alias="marginCallPercent")


# Missing official OANDA models that we need to add:


class AccountChanges(ApiModel):
    """Used to represent changes to an Account's Orders, Trades and Positions since a specified Account TransactionID."""

    orders_created: list[Order] = Field(default_factory=list, alias="ordersCreated")
    orders_cancelled: list[Order] = Field(default_factory=list, alias="ordersCancelled")
    orders_filled: list[Order] = Field(default_factory=list, alias="ordersFilled")
    orders_triggered: list[Order] = Field(default_factory=list, alias="ordersTriggered")
    trades_opened: list[TradeSummary] = Field(default_factory=list, alias="tradesOpened")
    trades_reduced: list[TradeSummary] = Field(default_factory=list, alias="tradesReduced")
    trades_closed: list[TradeSummary] = Field(default_factory=list, alias="tradesClosed")
    positions: list[Position] = Field(default_factory=list)
    transactions: list[dict[str, Any]] = Field(default_factory=list)


class AccountChangesState(ApiModel):
    """Represents an Account's current price-dependent state."""

    unrealized_pl: AccountUnits | None = Field(None, alias="unrealizedPL")
    nav: AccountUnits | None = Field(None, alias="NAV")
    margin_used: AccountUnits | None = Field(None, alias="marginUsed")
    margin_available: AccountUnits | None = Field(None, alias="marginAvailable")
    position_value: AccountUnits | None = Field(None, alias="positionValue")
    margin_closeout_unrealized_pl: AccountUnits | None = Field(None, alias="marginCloseoutUnrealizedPL")
    margin_closeout_nav: AccountUnits | None = Field(None, alias="marginCloseoutNAV")
    margin_closeout_margin_used: AccountUnits | None = Field(None, alias="marginCloseoutMarginUsed")
    margin_closeout_percent: Decimal | None = Field(None, alias="marginCloseoutPercent")
    margin_closeout_position_value: Decimal | None = Field(None, alias="marginCloseoutPositionValue")
    withdrawal_limit: AccountUnits | None = Field(None, alias="withdrawalLimit")
    margin_call_margin_used: AccountUnits | None = Field(None, alias="marginCallMarginUsed")
    margin_call_percent: Decimal | None = Field(None, alias="marginCallPercent")
    balance: AccountUnits | None = Field(None)
    pl: AccountUnits | None = Field(None)
    resettable_pl: AccountUnits | None = Field(None, alias="resettablePL")
    financing: AccountUnits | None = Field(None)
    commission: AccountUnits | None = Field(None)
    dividend_adjustment: AccountUnits | None = Field(None, alias="dividendAdjustment")
    guaranteed_execution_fees: AccountUnits | None = Field(None, alias="guaranteedExecutionFees")
    margin_call_enter_time: datetime | None = Field(None, alias="marginCallEnterTime")
    margin_call_extension_count: int | None = Field(None, alias="marginCallExtensionCount")
    last_margin_call_extension_time: datetime | None = Field(None, alias="lastMarginCallExtensionTime")
    orders: list[DynamicOrderState] = Field(default_factory=list)
    trades: list[dict[str, Any]] = Field(default_factory=list)  # CalculatedTradeState
    positions: list[dict[str, Any]] = Field(default_factory=list)  # CalculatedPositionState


# Export all account-related models
__all__ = [
    "Account",
    "AccountChanges",
    "AccountChangesState",
    "AccountProperties",
    "AccountSummary",
    "AccumulatedAccountState",
    "CalculatedAccountState",
    "GuaranteedStopLossOrderParameters",
    "UserAttributes",
]
