"""
Pricing and market data models for OANDA API.

Contains models for real-time pricing data, candlestick data, order books,
currency conversions, and pricing-related calculations.
"""

from datetime import datetime
from decimal import Decimal

from pydantic import Field

from .base import ApiModel
from .enums import (
    Currency,
    InstrumentName,
    PriceStatus,
    PriceValue,
)


class PricingHeartbeat(ApiModel):
    """Pricing stream heartbeat."""

    type: str = Field(default="HEARTBEAT")
    time: datetime


class PriceBucket(ApiModel):
    """Price level with available liquidity."""

    price: PriceValue
    liquidity: Decimal


class HomeConversions(ApiModel):
    """Currency conversion factors for account calculations."""

    currency: Currency
    account_gain: Decimal = Field(alias="accountGain")
    account_loss: Decimal = Field(alias="accountLoss")
    position_value: Decimal = Field(alias="positionValue")


class QuoteHomeConversionFactors(ApiModel):
    """Conversion factors for quote currency calculations."""

    positive_units: Decimal = Field(alias="positiveUnits")
    negative_units: Decimal = Field(alias="negativeUnits")


class ConversionFactor(ApiModel):
    """Factor used to convert an instrument amount to account home currency."""

    factor: Decimal | None = None


class HomeConversionFactors(ApiModel):
    """Conversion factors for instrument base and quote currency amounts."""

    gain_quote_home: ConversionFactor | None = Field(None, alias="gainQuoteHome")
    loss_quote_home: ConversionFactor | None = Field(None, alias="lossQuoteHome")
    gain_base_home: ConversionFactor | None = Field(None, alias="gainBaseHome")
    loss_base_home: ConversionFactor | None = Field(None, alias="lossBaseHome")


class UnitsAvailableDetails(ApiModel):
    """Units available for both long and short orders."""

    long: Decimal  # Long units availability
    short: Decimal  # Short units availability


class UnitsAvailable(ApiModel):
    """Available units for trading calculations."""

    default: UnitsAvailableDetails
    reduce_first: UnitsAvailableDetails = Field(alias="reduceFirst")
    reduce_only: UnitsAvailableDetails = Field(alias="reduceOnly")
    open_only: UnitsAvailableDetails = Field(alias="openOnly")


class ClientPrice(ApiModel):
    """Real-time price data."""

    type: str = Field(default="PRICE")
    instrument: InstrumentName
    time: datetime
    status: PriceStatus | None = None  # Deprecated but may still be present
    tradeable: bool
    bids: list[PriceBucket] = Field(default_factory=list)
    asks: list[PriceBucket] = Field(default_factory=list)
    closeout_bid: PriceValue = Field(alias="closeoutBid")
    closeout_ask: PriceValue = Field(alias="closeoutAsk")
    quote_home_conversion_factors: QuoteHomeConversionFactors | None = Field(None, alias="quoteHomeConversionFactors")  # Deprecated
    units_available: UnitsAvailable | None = Field(None, alias="unitsAvailable")  # Deprecated


class CandlestickData(ApiModel):
    """OHLC price data for a candlestick."""

    o: PriceValue  # Open price
    h: PriceValue  # High price
    l: PriceValue  # Low price  # noqa: E741
    c: PriceValue  # Close price


class Candlestick(ApiModel):
    """Complete candlestick information with metadata."""

    time: datetime
    complete: bool
    volume: int
    bid: CandlestickData | None = None
    ask: CandlestickData | None = None
    mid: CandlestickData | None = None


class OrderBook(ApiModel):
    """Represents an order book for an instrument."""

    instrument: InstrumentName
    time: datetime
    price: PriceValue | None = None
    bucket_width: PriceValue | None = Field(None, alias="bucketWidth")
    buckets: list[PriceBucket] = Field(default_factory=list)


# Removed extra models that are not part of official OANDA v20 API:
# - MarketDepth, PositionBook, PriceAlert, MarketHours, PriceMovement


# Export all pricing-related models
__all__ = [
    "Candlestick",
    "CandlestickData",
    "ClientPrice",
    "ConversionFactor",
    "HomeConversionFactors",
    "HomeConversions",
    "OrderBook",
    "PriceBucket",
    "PricingHeartbeat",
    "QuoteHomeConversionFactors",
    "UnitsAvailable",
    "UnitsAvailableDetails",
]
