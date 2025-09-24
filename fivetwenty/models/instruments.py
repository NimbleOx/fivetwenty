"""
Instrument-related models for OANDA API.

Contains models related to trading instruments, their properties, financing,
and associated metadata.
"""

from __future__ import annotations

from decimal import Decimal  # noqa: TC003

from pydantic import Field

from .base import ApiModel
from .enums import (  # noqa: TC001
    DayOfWeek,
    GuaranteedStopLossOrderModeForInstrument,
    InstrumentName,
    InstrumentType,
)


class Tag(ApiModel):
    """A tag associated with an entity."""

    type: str
    name: str


class FinancingDayOfWeek(ApiModel):
    """Financing schedule for a specific day of the week."""

    day_of_week: DayOfWeek = Field(alias="dayOfWeek")
    days_charged: int = Field(alias="daysCharged")


class InstrumentFinancing(ApiModel):
    """Financing data for an instrument."""

    long_rate: Decimal = Field(alias="longRate")
    short_rate: Decimal = Field(alias="shortRate")
    financing_days_of_week: list[FinancingDayOfWeek] = Field(alias="financingDaysOfWeek")


class GuaranteedStopLossOrderLevelRestriction(ApiModel):
    """GSL level restriction details."""

    volume: Decimal  # Volume restriction level
    price_range: Decimal = Field(alias="priceRange")  # Price range restriction


class GuaranteedStopLossOrderEntryData(ApiModel):
    """Details required by clients to add a Guaranteed Stop Loss Order for a specific instrument."""

    minimum_distance: Decimal = Field(alias="minimumDistance")
    premium: Decimal
    level_restriction: GuaranteedStopLossOrderLevelRestriction | None = Field(None, alias="levelRestriction")


class InstrumentCommission(ApiModel):
    """Commission structure for an instrument."""

    commission: Decimal
    units_traded: Decimal = Field(alias="unitsTraded")
    minimum_commission: Decimal = Field(alias="minimumCommission")


class Instrument(ApiModel):
    """Trading instrument information."""

    name: InstrumentName
    type: InstrumentType
    display_name: str = Field(alias="displayName")
    pip_location: int = Field(alias="pipLocation")
    display_precision: int = Field(alias="displayPrecision")
    trade_units_precision: int = Field(alias="tradeUnitsPrecision")
    minimum_trade_size: Decimal = Field(alias="minimumTradeSize")
    maximum_trailing_stop_distance: Decimal = Field(alias="maximumTrailingStopDistance")
    minimum_trailing_stop_distance: Decimal = Field(alias="minimumTrailingStopDistance")
    maximum_position_size: Decimal = Field(alias="maximumPositionSize")
    maximum_order_units: Decimal = Field(alias="maximumOrderUnits")
    margin_rate: Decimal = Field(alias="marginRate")
    minimum_guaranteed_stop_loss_distance: Decimal | None = Field(None, alias="minimumGuaranteedStopLossDistance")
    guaranteed_stop_loss_order_mode: GuaranteedStopLossOrderModeForInstrument | None = Field(None, alias="guaranteedStopLossOrderMode")
    guaranteed_stop_loss_order_execution_premium: Decimal | None = Field(None, alias="guaranteedStopLossOrderExecutionPremium")
    guaranteed_stop_loss_order_level_restriction: GuaranteedStopLossOrderLevelRestriction | None = Field(None, alias="guaranteedStopLossOrderLevelRestriction")
    commission: InstrumentCommission | None = None
    financing: InstrumentFinancing | None = None
    tags: list[Tag] = Field(default_factory=list)


__all__ = [
    "FinancingDayOfWeek",
    "GuaranteedStopLossOrderEntryData",
    "GuaranteedStopLossOrderLevelRestriction",
    "Instrument",
    "InstrumentCommission",
    "InstrumentFinancing",
    "Tag",
]
