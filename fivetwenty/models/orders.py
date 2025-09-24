"""
Order-related models for OANDA API.

This module contains all order-related data structures including order requests,
order details, and order responses used by the OANDA REST API.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import Field

from .base import ApiModel
from .enums import (
    AccountUnits,
    InstrumentName,
    OrderID,
    OrderPositionFill,
    OrderState,
    OrderTriggerCondition,
    OrderType,
    PriceValue,
    TimeInForce,
    TradeID,
    TransactionID,
)


class ClientExtensions(ApiModel):
    """Client-provided order and trade extensions."""

    id: str | None = None
    tag: str | None = None
    comment: str | None = None


class TakeProfitDetails(ApiModel):
    """Take Profit order details for on-fill orders."""

    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class StopLossDetails(ApiModel):
    """Stop Loss order details for on-fill orders."""

    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    guaranteed: bool = False
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class TrailingStopLossDetails(ApiModel):
    """Trailing Stop Loss order details for on-fill orders."""

    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class GuaranteedStopLossDetails(ApiModel):
    """Details for guaranteed stop loss orders."""

    distance: Decimal | None = None
    price: PriceValue | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    guaranteed_execution_premium: AccountUnits | None = Field(None, alias="guaranteedExecutionPremium")


class MarketOrderTradeClose(ApiModel):
    """Details for closing trades with market orders."""

    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    units: Decimal


class MarketOrderPositionCloseout(ApiModel):
    """Details for position closeout via market order."""

    instrument: InstrumentName
    units: Decimal


class MarketOrderMarginCloseout(ApiModel):
    """Details for margin closeout market order."""

    reason: str


class MarketOrderDelayedTradeClose(ApiModel):
    """Details for delayed trade close market order."""

    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    source_transaction_id: TransactionID = Field(alias="sourceTransactionID")


class MarketOrderRequest(ApiModel):
    """Market order request."""

    type: OrderType = OrderType.MARKET
    instrument: InstrumentName
    units: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.FOK)
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_on_fill: TakeProfitDetails | None = Field(alias="takeProfitOnFill", default=None)
    stop_loss_on_fill: StopLossDetails | None = Field(alias="stopLossOnFill", default=None)
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(alias="guaranteedStopLossOnFill", default=None)
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(alias="trailingStopLossOnFill", default=None)
    trade_client_extensions: ClientExtensions | None = Field(alias="tradeClientExtensions", default=None)


class LimitOrderRequest(ApiModel):
    """Limit order request."""

    type: OrderType = OrderType.LIMIT
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_on_fill: TakeProfitDetails | None = Field(alias="takeProfitOnFill", default=None)
    stop_loss_on_fill: StopLossDetails | None = Field(alias="stopLossOnFill", default=None)
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(alias="guaranteedStopLossOnFill", default=None)
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(alias="trailingStopLossOnFill", default=None)
    trade_client_extensions: ClientExtensions | None = Field(alias="tradeClientExtensions", default=None)


class StopOrderRequest(ApiModel):
    """Stop order request."""

    type: OrderType = OrderType.STOP
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(alias="priceBound", default=None)
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_on_fill: TakeProfitDetails | None = Field(alias="takeProfitOnFill", default=None)
    stop_loss_on_fill: StopLossDetails | None = Field(alias="stopLossOnFill", default=None)
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(alias="guaranteedStopLossOnFill", default=None)
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(alias="trailingStopLossOnFill", default=None)
    trade_client_extensions: ClientExtensions | None = Field(alias="tradeClientExtensions", default=None)


class TakeProfitOrderRequest(ApiModel):
    """Take profit order request.

    USAGE: This order type is linked to an existing trade and cannot be used to open new positions.
    It is designed for post-trade risk management. For setting take profit during order creation,
    use the takeProfitOnFill parameter in MarketOrderRequest, LimitOrderRequest, etc.
    """

    type: OrderType = OrderType.TAKE_PROFIT
    trade_id: TradeID = Field(alias="tradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class StopLossOrderRequest(ApiModel):
    """Stop loss order request.

    USAGE: This order type is linked to an existing trade and cannot be used to open new positions.
    It is designed for post-trade risk management. For setting stop loss during order creation,
    use the stopLossOnFill parameter in MarketOrderRequest, LimitOrderRequest, etc.
    """

    type: OrderType = OrderType.STOP_LOSS
    trade_id: TradeID = Field(alias="tradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    guaranteed: bool = False
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class MarketIfTouchedOrderRequest(ApiModel):
    """Market If Touched order request."""

    type: OrderType = OrderType.MARKET_IF_TOUCHED
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(alias="priceBound", default=None)
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)
    take_profit_on_fill: TakeProfitDetails | None = Field(alias="takeProfitOnFill", default=None)
    stop_loss_on_fill: StopLossDetails | None = Field(alias="stopLossOnFill", default=None)
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(alias="guaranteedStopLossOnFill", default=None)
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(alias="trailingStopLossOnFill", default=None)
    trade_client_extensions: ClientExtensions | None = Field(alias="tradeClientExtensions", default=None)


class TrailingStopLossOrderRequest(ApiModel):
    """Trailing Stop Loss order request.

    USAGE: This order type is linked to an existing trade and cannot be used to open new positions.
    It is designed for post-trade risk management. For setting trailing stop loss during order creation,
    use the trailingStopLossOnFill parameter in MarketOrderRequest, LimitOrderRequest, etc.
    """

    type: OrderType = OrderType.TRAILING_STOP_LOSS
    trade_id: TradeID = Field(alias="tradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class GuaranteedStopLossOrderRequest(ApiModel):
    """Guaranteed Stop Loss order request.

    USAGE: This order type is linked to an existing trade and cannot be used to open new positions.
    It provides guaranteed execution at a specified price with associated premium costs.
    May be used standalone for critical risk management scenarios where standard stop loss
    is insufficient. For setting guaranteed stop loss during order creation,
    use the guaranteedStopLossOnFill parameter in MarketOrderRequest, LimitOrderRequest, etc.
    """

    type: OrderType = OrderType.GUARANTEED_STOP_LOSS
    trade_id: TradeID = Field(alias="tradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(alias="gtdTime", default=None)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    guaranteed_execution_premium: AccountUnits | None = Field(alias="guaranteedExecutionPremium", default=None)
    client_extensions: ClientExtensions | None = Field(alias="clientExtensions", default=None)


class FixedPriceOrder(ApiModel):
    """A FixedPriceOrder is filled immediately upon creation using a fixed price."""

    # Base order fields
    id: OrderID | None = None
    create_time: datetime | None = Field(None, alias="createTime")
    state: OrderState | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Fixed price order specific fields
    type: str = Field(default="FIXED_PRICE")
    instrument: InstrumentName
    units: Decimal  # Required: +ve = long, -ve = short
    price: PriceValue  # Required: exact fill price
    position_fill: OrderPositionFill = Field(default=OrderPositionFill.DEFAULT, alias="positionFill")
    trade_state: str = Field(alias="tradeState")  # Required: resulting trade state

    # On-fill orders (conditional)
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")

    # Fill/cancel state fields (conditional)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] | None = Field(None, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class DynamicOrderState(ApiModel):
    """The dynamic state of an Order."""

    id: str
    trailing_stop_value: PriceValue | None = Field(None, alias="trailingStopValue")
    trigger_distance: Decimal | None = Field(None, alias="triggerDistance")
    is_trigger_distance_exact: bool | None = Field(None, alias="isTriggerDistanceExact")


class OrderResponse(ApiModel):
    """Response from order creation."""

    order_create_transaction: dict[str, Any] | None = Field(None, alias="orderCreateTransaction")
    order_fill_transaction: dict[str, Any] | None = Field(None, alias="orderFillTransaction")
    order_cancel_transaction: dict[str, Any] | None = Field(None, alias="orderCancelTransaction")
    order_reissue_transaction: dict[str, Any] | None = Field(None, alias="orderReissueTransaction")
    order_reissue_reject_transaction: dict[str, Any] | None = Field(None, alias="orderReissueRejectTransaction")
    related_transaction_ids: list[str] = Field(alias="relatedTransactionIDs", default_factory=list)
    last_transaction_id: str = Field(alias="lastTransactionID")


# === COMPLETE ORDER STATE MODELS ===
# These represent actual orders in the system (not just requests)


class MarketOrder(ApiModel):
    """A MarketOrder is an order that is filled immediately upon creation."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Market order specific fields
    type: str = Field(default="MARKET", frozen=True)
    instrument: InstrumentName
    units: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    position_fill: OrderPositionFill = Field(alias="positionFill")

    # Trade close details (conditional)
    trade_close: MarketOrderTradeClose | None = Field(None, alias="tradeClose")
    long_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="longPositionCloseout")
    short_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="shortPositionCloseout")
    margin_closeout: MarketOrderMarginCloseout | None = Field(None, alias="marginCloseout")
    delayed_trade_close: MarketOrderDelayedTradeClose | None = Field(None, alias="delayedTradeClose")

    # On-fill order details
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class LimitOrder(ApiModel):
    """A LimitOrder is an order that will only be filled by a price equal to or better than the threshold."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Limit order specific fields
    type: str = Field(default="LIMIT", frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")

    # On-fill order details
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class StopOrder(ApiModel):
    """A StopOrder is an order that will become a MarketOrder when the trade price meets or exceeds the threshold."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Stop order specific fields
    type: str = Field(default="STOP", frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")

    # On-fill order details
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class MarketIfTouchedOrder(ApiModel):
    """A MarketIfTouchedOrder is an order that is created with a price threshold, and will only be filled by a market price that touches or crosses the threshold."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Market-if-touched order specific fields
    type: str = Field(default="MARKET_IF_TOUCHED", frozen=True)
    instrument: InstrumentName
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    initial_market_price: PriceValue | None = Field(None, alias="initialMarketPrice")

    # On-fill order details
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    replaced_by_order_id: OrderID | None = Field(None, alias="replacedByOrderID")


class TakeProfitOrder(ApiModel):
    """A TakeProfitOrder is an order that is linked to an open Trade and will be filled when the trade price meets or exceeds the threshold."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Take profit order specific fields
    type: str = Field(default="TAKE_PROFIT", frozen=True)
    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class StopLossOrder(ApiModel):
    """A StopLossOrder is an order that is linked to an open Trade and will be filled when the trade price meets or exceeds the threshold."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Stop loss order specific fields
    type: str = Field(default="STOP_LOSS", frozen=True)
    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    guaranteed: bool = Field(default=False)

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


class GuaranteedStopLossOrder(ApiModel):
    """A GuaranteedStopLossOrder is an order that is linked to an open Trade and created with a price threshold which closes the Trade when the threshold is breached, with guaranteed execution."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Guaranteed stop loss order specific fields
    type: str = Field(default="GUARANTEED_STOP_LOSS", frozen=True)
    trade_id: TradeID = Field(alias="tradeID")
    price: PriceValue
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    guaranteed_execution_premium: Decimal = Field(alias="guaranteedExecutionPremium")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    replaced_by_order_id: OrderID | None = Field(None, alias="replacedByOrderID")


class TrailingStopLossOrder(ApiModel):
    """A TrailingStopLossOrder is an order that is linked to an open Trade with a trailing stop distance."""

    # Base order fields
    id: OrderID
    create_time: datetime = Field(alias="createTime")
    state: OrderState
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")

    # Trailing stop loss order specific fields
    type: str = Field(default="TRAILING_STOP_LOSS", frozen=True)
    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce")
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition")
    trailing_stop_value: PriceValue | None = Field(None, alias="trailingStopValue")

    # Fill/cancel state fields (when FILLED or CANCELLED)
    filling_transaction_id: TransactionID | None = Field(None, alias="fillingTransactionID")
    filled_time: datetime | None = Field(None, alias="filledTime")
    trade_opened_id: TradeID | None = Field(None, alias="tradeOpenedID")
    trade_reduced_id: TradeID | None = Field(None, alias="tradeReducedID")
    trade_closed_ids: list[TradeID] = Field(default_factory=list, alias="tradeClosedIDs")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    cancelled_time: datetime | None = Field(None, alias="cancelledTime")


# Export all order-related models
__all__ = [
    # Order details and supporting models
    "ClientExtensions",
    "DynamicOrderState",
    "FixedPriceOrder",
    "GuaranteedStopLossDetails",
    "GuaranteedStopLossOrder",
    "GuaranteedStopLossOrderRequest",
    "LimitOrder",
    "LimitOrderRequest",
    "MarketIfTouchedOrder",
    "MarketIfTouchedOrderRequest",
    # Order state models (actual orders in the system)
    "MarketOrder",
    "MarketOrderDelayedTradeClose",
    "MarketOrderMarginCloseout",
    "MarketOrderPositionCloseout",
    # Order request models (for creating orders)
    "MarketOrderRequest",
    "MarketOrderTradeClose",
    # Response models
    "OrderResponse",
    "StopLossDetails",
    "StopLossOrder",
    "StopLossOrderRequest",
    "StopOrder",
    "StopOrderRequest",
    "TakeProfitDetails",
    "TakeProfitOrder",
    "TakeProfitOrderRequest",
    "TrailingStopLossDetails",
    "TrailingStopLossOrder",
    "TrailingStopLossOrderRequest",
]
