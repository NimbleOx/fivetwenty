"""
Trade-related models for OANDA API.

This module contains all trade-related data structures including:
- Trade: Complete trade representation with dependent orders
- TradeSummary: Condensed trade representation
- CalculatedTradeState: Dynamic calculated state of an open trade

These models provide comprehensive trade management functionality for the OANDA trading platform.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from pydantic import Field

from .base import ApiModel
from .enums import (
    AccountUnits,
    InstrumentName,
    OrderID,
    PriceValue,
    TradeID,
    TradeState,
    TransactionID,
)
from .orders import ClientExtensions

if TYPE_CHECKING:
    from .orders import GuaranteedStopLossOrder, StopLossOrder, TakeProfitOrder, TrailingStopLossOrder


class Trade(ApiModel):
    """Complete trade representation with dependent orders."""

    id: TradeID
    instrument: InstrumentName
    price: PriceValue
    open_time: datetime = Field(alias="openTime")
    state: TradeState
    initial_units: Decimal = Field(alias="initialUnits")
    initial_margin_required: AccountUnits = Field(alias="initialMarginRequired")
    current_units: Decimal = Field(alias="currentUnits")
    realized_pl: AccountUnits = Field(alias="realizedPL")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    margin_used: AccountUnits = Field(alias="marginUsed")
    average_close_price: PriceValue | None = Field(alias="averageClosePrice", default=None)
    closing_transaction_ids: list[TransactionID] = Field(alias="closingTransactionIDs", default_factory=list)
    financing: AccountUnits = Field(default=Decimal("0"))
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment", default=Decimal("0"))
    close_time: datetime | None = Field(alias="closeTime", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_order: "TakeProfitOrder | None" = Field(alias="takeProfitOrder", default=None)
    stop_loss_order: "StopLossOrder | None" = Field(alias="stopLossOrder", default=None)
    guaranteed_stop_loss_order: "GuaranteedStopLossOrder | None" = Field(alias="guaranteedStopLossOrder", default=None)
    trailing_stop_loss_order: "TrailingStopLossOrder | None" = Field(alias="trailingStopLossOrder", default=None)


class TradeSummary(ApiModel):
    """Condensed trade representation without full dependent orders."""

    id: TradeID
    instrument: InstrumentName
    price: PriceValue
    open_time: datetime = Field(alias="openTime")
    state: TradeState
    initial_units: Decimal = Field(alias="initialUnits")
    initial_margin_required: AccountUnits = Field(alias="initialMarginRequired")
    current_units: Decimal = Field(alias="currentUnits")
    realized_pl: AccountUnits = Field(alias="realizedPL")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    margin_used: AccountUnits = Field(alias="marginUsed")
    average_close_price: PriceValue | None = Field(alias="averageClosePrice", default=None)
    closing_transaction_ids: list[TransactionID] = Field(alias="closingTransactionIDs", default_factory=list)
    financing: AccountUnits = Field(default=Decimal("0"))
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment", default=Decimal("0"))
    close_time: datetime | None = Field(alias="closeTime", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_order_id: OrderID | None = Field(alias="takeProfitOrderID", default=None)
    stop_loss_order_id: OrderID | None = Field(alias="stopLossOrderID", default=None)
    guaranteed_stop_loss_order_id: OrderID | None = Field(alias="guaranteedStopLossOrderID", default=None)
    trailing_stop_loss_order_id: OrderID | None = Field(alias="trailingStopLossOrderID", default=None)


class CalculatedTradeState(ApiModel):
    """Dynamic calculated state of an open trade."""

    id: TradeID
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    margin_used: AccountUnits = Field(alias="marginUsed")


# Export all trade-related models
__all__ = [
    "CalculatedTradeState",
    "Trade",
    "TradeSummary",
]
