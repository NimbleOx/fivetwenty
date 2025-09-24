"""
Position-related models for OANDA API.

This module contains all position-related data structures used by the OANDA REST API,
including Position, PositionSide, and CalculatedPositionState models.

Position models represent the net aggregation of trades for specific instruments
and their calculated states for real-time P&L tracking.
"""

from decimal import Decimal

from pydantic import Field

from .base import ApiModel
from .enums import (
    AccountUnits,
    InstrumentName,
    PriceValue,
    TradeID,
)


class Position(ApiModel):
    """Net aggregation of trades for a specific instrument."""

    instrument: InstrumentName
    pl: AccountUnits = Field(alias="pl")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    margin_used: AccountUnits = Field(alias="marginUsed", default=Decimal("0"))
    resettable_pl: AccountUnits = Field(alias="resettablePL")
    financing: AccountUnits = Field(default=Decimal("0"))
    commission: AccountUnits = Field(default=Decimal("0"))
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment", default=Decimal("0"))
    guaranteed_execution_fees: AccountUnits = Field(alias="guaranteedExecutionFees", default=Decimal("0"))
    long: "PositionSide"
    short: "PositionSide"


class PositionSide(ApiModel):
    """Single direction (long or short) position representation."""

    units: Decimal
    average_price: PriceValue | None = Field(alias="averagePrice", default=None)
    trade_ids: list[TradeID] = Field(alias="tradeIDs", default_factory=list)
    pl: AccountUnits = Field(alias="pl")
    unrealized_pl: AccountUnits = Field(alias="unrealizedPL")
    resettable_pl: AccountUnits = Field(alias="resettablePL")
    financing: AccountUnits = Field(default=Decimal("0"))
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment", default=Decimal("0"))
    guaranteed_execution_fees: AccountUnits = Field(alias="guaranteedExecutionFees", default=Decimal("0"))


class CalculatedPositionState(ApiModel):
    """Dynamic calculated state of a position."""

    instrument: InstrumentName
    net_unrealized_pl: AccountUnits = Field(alias="netUnrealizedPL")
    long_unrealized_pl: AccountUnits = Field(alias="longUnrealizedPL")
    short_unrealized_pl: AccountUnits = Field(alias="shortUnrealizedPL")
    margin_used: AccountUnits = Field(alias="marginUsed", default=Decimal("0"))


# Export all position-related models
__all__ = [
    "CalculatedPositionState",
    "Position",
    "PositionSide",
]
