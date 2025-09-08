"""
Generated Pydantic models for OANDA API.

This file is auto-generated - do not edit manually!
Use scripts/generate_models.py to regenerate.
"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


def camel_to_snake(string: str) -> str:
    """Convert camelCase to snake_case for aliases."""
    result = []
    for i, char in enumerate(string):
        if char.isupper() and i > 0:
            result.append('_')
        result.append(char.lower())
    return ''.join(result)


class ApiModel(BaseModel):
    """Base model with camelCase aliases."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=camel_to_snake,
        use_enum_values=True,
        validate_assignment=True,
    )


# Core Enums
class Currency(str, Enum):
    """ISO 4217 currency codes."""
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    NZD = "NZD"
    USD = "USD"


class InstrumentName(str, Enum):
    """Available trading instruments."""
    # Major pairs
    EUR_USD = "EUR_USD"
    GBP_USD = "GBP_USD"
    USD_JPY = "USD_JPY"
    USD_CHF = "USD_CHF"
    AUD_USD = "AUD_USD"
    USD_CAD = "USD_CAD"
    NZD_USD = "NZD_USD"
    
    # More pairs would be added by codegen...
    # This is just a starter set


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


# Type aliases (not classes to avoid Pydantic issues)
AccountID = str
"""Account identifier in format: {site}-{division}-{user}-{account}."""

DecimalNumber = str
"""Decimal number encoded as string for precision."""

PriceValue = str
"""Price value encoded as string for precision."""

AccountUnits = str
"""Account currency units encoded as string for precision."""

DateTime = str
"""RFC3339 datetime string."""


# Complex Models
class AccountProperties(ApiModel):
    """Basic account information."""
    id: AccountID
    mt4_account_id: Optional[int] = None
    tags: List[str] = Field(default_factory=list)


class Account(ApiModel):
    """Complete account details."""
    id: AccountID
    alias: Optional[str] = None
    currency: Currency
    balance: Decimal
    created_by_user_id: int
    created_time: DateTime
    guaranteed_stop_loss_order_mode: str = Field(default="DISABLED")
    margin_used: Decimal = Field(default=Decimal("0"))
    margin_available: Decimal = Field(default=Decimal("0"))
    position_value: Decimal = Field(default=Decimal("0"))
    open_trade_count: int = Field(default=0)
    open_position_count: int = Field(default=0)
    pending_order_count: int = Field(default=0)
    hedging_enabled: bool = Field(default=False)
    unrealized_pl: Decimal = Field(default=Decimal("0"))
    nav: Decimal = Field(default=Decimal("0"))
    margin_rate: Decimal = Field(default=Decimal("0.02"))
    margin_call_margin_used: Decimal = Field(default=Decimal("0"))
    margin_call_percent: Decimal = Field(default=Decimal("0"))


class Instrument(ApiModel):
    """Trading instrument information."""
    name: InstrumentName
    type: InstrumentType
    display_name: str
    pip_location: int
    display_precision: int
    trade_units_precision: int
    minimum_trade_size: DecimalNumber
    maximum_trailing_stop_distance: DecimalNumber
    minimum_trailing_stop_distance: DecimalNumber
    maximum_position_size: DecimalNumber
    maximum_order_units: DecimalNumber
    margin_rate: DecimalNumber
    commission: Optional[Dict[str, Any]] = None
    financing: Optional[Dict[str, Any]] = None
    tags: List[Dict[str, str]] = Field(default_factory=list)


class ClientPrice(ApiModel):
    """Real-time price data."""
    type: str = Field(default="PRICE")
    instrument: InstrumentName
    time: DateTime
    status: str
    tradeable: bool
    bids: List[Dict[str, str]] = Field(default_factory=list)
    asks: List[Dict[str, str]] = Field(default_factory=list)
    closeout_bid: PriceValue
    closeout_ask: PriceValue
    
    @property
    def mid(self) -> Decimal:
        """Calculate mid price."""
        bid = Decimal(self.closeout_bid)
        ask = Decimal(self.closeout_ask)
        return (bid + ask) / 2
    
    @property
    def spread(self) -> Decimal:
        """Calculate spread."""
        return Decimal(self.closeout_ask) - Decimal(self.closeout_bid)


class PricingHeartbeat(ApiModel):
    """Pricing stream heartbeat."""
    type: str = Field(default="HEARTBEAT")
    time: DateTime


class MarketOrderRequest(ApiModel):
    """Market order request."""
    type: OrderType = OrderType.MARKET
    instrument: InstrumentName
    units: int
    time_in_force: str = Field(default="FOK")  # Fill or Kill
    position_fill: str = Field(default="DEFAULT")
    client_extensions: Optional[Dict[str, str]] = None
    take_profit_on_fill: Optional[Dict[str, Any]] = None
    stop_loss_on_fill: Optional[Dict[str, Any]] = None
    trailing_stop_loss_on_fill: Optional[Dict[str, Any]] = None
    trade_client_extensions: Optional[Dict[str, str]] = None


class OrderResponse(ApiModel):
    """Response from order creation."""
    order_create_transaction: Optional[Dict[str, Any]] = None
    order_fill_transaction: Optional[Dict[str, Any]] = None
    order_cancel_transaction: Optional[Dict[str, Any]] = None
    order_reissue_transaction: Optional[Dict[str, Any]] = None
    order_reissue_reject_transaction: Optional[Dict[str, Any]] = None
    related_transaction_ids: List[str] = Field(default_factory=list)
    last_transaction_id: str
    
    @property 
    def order(self) -> Optional[Dict[str, Any]]:
        """Get the created order from the response."""
        if self.order_create_transaction:
            return self.order_create_transaction
        return None


# More models would be generated here by scripts/generate_models.py...

# Export commonly used types
__all__ = [
    # Base model
    "ApiModel",
    
    # Enums
    "Currency",
    "InstrumentName", 
    "InstrumentType",
    "OrderType",
    "OrderState",
    "Direction",
    
    # Type aliases
    "AccountID",
    "DecimalNumber",
    "PriceValue", 
    "AccountUnits",
    "DateTime",
    
    # Complex models
    "AccountProperties",
    "Account",
    "Instrument",
    "ClientPrice",
    "PricingHeartbeat",
    "MarketOrderRequest",
    "OrderResponse",
]