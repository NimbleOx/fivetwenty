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
    AccountFinancingMode,
    AccountUnits,
    Currency,
    FixedPriceOrderReason,
    FundingReason,
    GuaranteedStopLossOrderReason,
    InstrumentName,
    LimitOrderReason,
    MarketIfTouchedOrderReason,
    MarketOrderReason,
    OrderCancelReason,
    OrderFillReason,
    OrderID,
    OrderPositionFill,
    OrderTriggerCondition,
    PriceValue,
    StopLossOrderReason,
    StopOrderReason,
    TakeProfitOrderReason,
    TimeInForce,
    TradeID,
    TrailingStopLossOrderReason,
    TransactionID,
    TransactionRejectReason,
    TransactionType,
)
from .orders import (
    ClientExtensions,
    GuaranteedStopLossDetails,
    MarketOrderDelayedTradeClose,
    MarketOrderMarginCloseout,
    MarketOrderPositionCloseout,
    MarketOrderTradeClose,
    StopLossDetails,
    TakeProfitDetails,
    TrailingStopLossDetails,
)
from .pricing import ClientPrice, HomeConversionFactors

# Forward references for type checking


class TransactionHeartbeat(ApiModel):
    """Transaction stream heartbeat message.

    Sent every 5 seconds on the transaction stream to maintain connection
    and verify stream is alive.
    """

    type: str = Field(default="HEARTBEAT")
    time: datetime
    last_transaction_id: TransactionID | None = Field(None, alias="lastTransactionID")


class Transaction(ApiModel):
    """Base transaction model with common fields for all transaction types."""

    id: str = Field(alias="id")
    time: datetime
    user_id: int = Field(alias="userID")
    account_id: str = Field(alias="accountID")
    batch_id: str = Field(alias="batchID")
    request_id: str | None = Field(None, alias="requestID")
    type: TransactionType


class TradeOpen(ApiModel):
    """Represents a Trade that was opened as part of an OrderFill."""

    trade_id: str = Field(alias="tradeID")
    units: Decimal
    price: PriceValue
    guaranteed_execution_fee: AccountUnits | None = Field(None, alias="guaranteedExecutionFee")
    quote_guaranteed_execution_fee: Decimal | None = Field(None, alias="quoteGuaranteedExecutionFee")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    half_spread_cost: AccountUnits | None = Field(None, alias="halfSpreadCost")
    initial_margin_required: AccountUnits | None = Field(None, alias="initialMarginRequired")


class TradeReduce(ApiModel):
    """Represents a Trade that was reduced or closed as part of an OrderFill."""

    trade_id: str = Field(alias="tradeID")
    units: Decimal
    price: PriceValue
    realized_pl: AccountUnits | None = Field(None, alias="realizedPL")
    financing: AccountUnits | None = None
    base_financing: Decimal | None = Field(None, alias="baseFinancing")
    quote_financing: Decimal | None = Field(None, alias="quoteFinancing")
    financing_rate: Decimal | None = Field(None, alias="financingRate")
    guaranteed_execution_fee: AccountUnits | None = Field(None, alias="guaranteedExecutionFee")
    quote_guaranteed_execution_fee: Decimal | None = Field(None, alias="quoteGuaranteedExecutionFee")
    half_spread_cost: AccountUnits | None = Field(None, alias="halfSpreadCost")


class FullPrice(ApiModel):
    """Complete pricing information for an order fill."""

    closeout_bid: PriceValue = Field(alias="closeoutBid")
    closeout_ask: PriceValue = Field(alias="closeoutAsk")
    liquidity: int | None = None


class OpenTradeDividendAdjustment(ApiModel):
    """Dividend adjustment paid or collected for an open trade."""

    trade_id: TradeID | None = Field(None, alias="tradeID")
    dividend_adjustment: AccountUnits | None = Field(None, alias="dividendAdjustment")
    quote_dividend_adjustment: Decimal | None = Field(None, alias="quoteDividendAdjustment")


class LiquidityRegenerationScheduleStep(ApiModel):
    """Single step in a liquidity regeneration schedule."""

    timestamp: datetime | None = None
    bid_liquidity_used: Decimal | None = Field(None, alias="bidLiquidityUsed")
    ask_liquidity_used: Decimal | None = Field(None, alias="askLiquidityUsed")


class LiquidityRegenerationSchedule(ApiModel):
    """Schedule describing regenerated liquidity after an order fill."""

    steps: list[LiquidityRegenerationScheduleStep] = Field(default_factory=list)


class OpenTradeFinancing(ApiModel):
    """Daily financing paid or collected for an open trade."""

    trade_id: TradeID | None = Field(None, alias="tradeID")
    financing: AccountUnits | None = None
    base_financing: Decimal | None = Field(None, alias="baseFinancing")
    quote_financing: Decimal | None = Field(None, alias="quoteFinancing")
    financing_rate: Decimal | None = Field(None, alias="financingRate")


class PositionFinancing(ApiModel):
    """Daily financing paid or collected for a position."""

    instrument: InstrumentName | str | None = None
    financing: AccountUnits | None = None
    base_financing: Decimal | None = Field(None, alias="baseFinancing")
    quote_financing: Decimal | None = Field(None, alias="quoteFinancing")
    home_conversion_factors: HomeConversionFactors | None = Field(None, alias="homeConversionFactors")
    open_trade_financings: list[OpenTradeFinancing] = Field(default_factory=list, alias="openTradeFinancings")
    account_financing_mode: AccountFinancingMode | None = Field(None, alias="accountFinancingMode")


class OrderFillTransaction(Transaction):
    """Transaction representing the filling of an Order."""

    type: TransactionType = Field(default=TransactionType.ORDER_FILL, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    instrument: InstrumentName | str
    units: Decimal
    gain_quote_home_conversion_factor: Decimal | None = Field(None, alias="gainQuoteHomeConversionFactor")
    loss_quote_home_conversion_factor: Decimal | None = Field(None, alias="lossQuoteHomeConversionFactor")
    price: PriceValue | None = None
    full_vwap: PriceValue | None = Field(None, alias="fullVWAP")
    full_price: ClientPrice | None = Field(None, alias="fullPrice")
    reason: OrderFillReason | None = None
    pl: Decimal | None = Field(None, alias="pl")
    quote_pl: Decimal | None = Field(None, alias="quotePL")
    financing: Decimal | None = None
    base_financing: Decimal | None = Field(None, alias="baseFinancing")
    quote_financing: Decimal | None = Field(None, alias="quoteFinancing")
    commission: Decimal | None = None
    guaranteed_execution_fee: AccountUnits | None = Field(None, alias="guaranteedExecutionFee")
    quote_guaranteed_execution_fee: Decimal | None = Field(None, alias="quoteGuaranteedExecutionFee")
    home_conversion_factors: HomeConversionFactors | None = Field(None, alias="homeConversionFactors")
    account_balance: Decimal | None = Field(None, alias="accountBalance")
    trade_opened: TradeOpen | None = Field(None, alias="tradeOpened")
    trades_closed: list[TradeReduce] | None = Field(None, alias="tradesClosed")
    trade_reduced: TradeReduce | None = Field(None, alias="tradeReduced")
    half_spread_cost: Decimal | None = Field(None, alias="halfSpreadCost")


class OrderCancelTransaction(Transaction):
    """Transaction representing the cancellation of an Order."""

    type: TransactionType = Field(default=TransactionType.ORDER_CANCEL, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    reason: OrderCancelReason | None = None
    replaced_by_order_id: str | None = Field(None, alias="replacedByOrderID")


class MarketOrderTransaction(Transaction):
    """Transaction representing the creation of a Market Order."""

    type: TransactionType = Field(default=TransactionType.MARKET_ORDER, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.FOK)
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trade_close: MarketOrderTradeClose | None = Field(None, alias="tradeClose")
    long_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="longPositionCloseout")
    short_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="shortPositionCloseout")
    margin_closeout: MarketOrderMarginCloseout | None = Field(None, alias="marginCloseout")
    delayed_trade_close: MarketOrderDelayedTradeClose | None = Field(None, alias="delayedTradeClose")
    reason: MarketOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
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
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class LimitOrderTransaction(Transaction):
    """Limit order creation transaction."""

    type: TransactionType = Field(default=TransactionType.LIMIT_ORDER, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: LimitOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")


class LimitOrderRejectTransaction(Transaction):
    """Limit order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.LIMIT_ORDER_REJECT, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: LimitOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class MarketOrderRejectTransaction(Transaction):
    """Market order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_ORDER_REJECT, frozen=True)
    # Optional: rejects generated from a trade close / position closeout carry the
    # request in tradeClose/longPositionCloseout etc. with no top-level instrument
    # or units (observed live, e.g. rejectReason=TRADE_DOESNT_EXIST).
    instrument: InstrumentName | str | None = None
    units: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.FOK)
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trade_close: MarketOrderTradeClose | None = Field(None, alias="tradeClose")
    long_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="longPositionCloseout")
    short_position_closeout: MarketOrderPositionCloseout | None = Field(None, alias="shortPositionCloseout")
    margin_closeout: MarketOrderMarginCloseout | None = Field(None, alias="marginCloseout")
    delayed_trade_close: MarketOrderDelayedTradeClose | None = Field(None, alias="delayedTradeClose")
    reason: MarketOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class StopOrderTransaction(Transaction):
    """Stop order creation transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_ORDER, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: StopOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")


class StopOrderRejectTransaction(Transaction):
    """Stop order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_ORDER_REJECT, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: StopOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class TakeProfitOrderTransaction(Transaction):
    """Take profit order creation transaction."""

    type: TransactionType = Field(default=TransactionType.TAKE_PROFIT_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: TakeProfitOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")


class TakeProfitOrderRejectTransaction(Transaction):
    """Take profit order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TAKE_PROFIT_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: TakeProfitOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class StopLossOrderTransaction(Transaction):
    """Stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    guaranteed: bool = Field(default=False)
    guaranteed_execution_premium: Decimal | None = Field(None, alias="guaranteedExecutionPremium")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: StopLossOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")


class StopLossOrderRejectTransaction(Transaction):
    """Stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    guaranteed: bool | None = None
    reason: StopLossOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class TrailingStopLossOrderTransaction(Transaction):
    """Trailing stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.TRAILING_STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: TrailingStopLossOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")


class TrailingStopLossOrderRejectTransaction(Transaction):
    """Trailing stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TRAILING_STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    distance: Decimal
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: TrailingStopLossOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class GuaranteedStopLossOrderTransaction(Transaction):
    """Guaranteed stop loss order creation transaction."""

    type: TransactionType = Field(default=TransactionType.GUARANTEED_STOP_LOSS_ORDER, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    guaranteed_execution_premium: AccountUnits = Field(alias="guaranteedExecutionPremium")
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    reason: GuaranteedStopLossOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")


class GuaranteedStopLossOrderRejectTransaction(Transaction):
    """Guaranteed stop loss order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.GUARANTEED_STOP_LOSS_ORDER_REJECT, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    price: PriceValue | None = None
    distance: Decimal | None = None
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: GuaranteedStopLossOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    order_fill_transaction_id: TransactionID | None = Field(None, alias="orderFillTransactionID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class MarketIfTouchedOrderTransaction(Transaction):
    """Market if touched order creation transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_IF_TOUCHED_ORDER, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    reason: MarketIfTouchedOrderReason | None = None
    replaces_order_id: OrderID | None = Field(None, alias="replacesOrderID")
    cancelling_transaction_id: TransactionID | None = Field(None, alias="cancellingTransactionID")


class MarketIfTouchedOrderRejectTransaction(Transaction):
    """Market if touched order rejection transaction."""

    type: TransactionType = Field(default=TransactionType.MARKET_IF_TOUCHED_ORDER_REJECT, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    price_bound: PriceValue | None = Field(None, alias="priceBound")
    time_in_force: TimeInForce = Field(alias="timeInForce", default=TimeInForce.GTC)
    gtd_time: datetime | None = Field(None, alias="gtdTime")
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trigger_condition: OrderTriggerCondition = Field(alias="triggerCondition", default=OrderTriggerCondition.DEFAULT)
    reason: MarketIfTouchedOrderReason | None = None
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")
    intended_replaces_order_id: OrderID | None = Field(None, alias="intendedReplacesOrderID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class OrderCancelRejectTransaction(Transaction):
    """Order cancel rejection transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_CANCEL_REJECT, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class OrderClientExtensionsModifyTransaction(Transaction):
    """Order client extensions modification transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_CLIENT_EXTENSIONS_MODIFY, frozen=True)
    order_id: str = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    client_extensions_modify: ClientExtensions | None = Field(None, alias="clientExtensionsModify")
    trade_client_extensions_modify: ClientExtensions | None = Field(None, alias="tradeClientExtensionsModify")


class OrderClientExtensionsModifyRejectTransaction(Transaction):
    """Order client extensions modification rejection transaction."""

    type: TransactionType = Field(default=TransactionType.ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT, frozen=True)
    order_id: OrderID = Field(alias="orderID")
    client_order_id: str | None = Field(None, alias="clientOrderID")
    client_extensions_modify: ClientExtensions | None = Field(None, alias="clientExtensionsModify")
    trade_client_extensions_modify: ClientExtensions | None = Field(None, alias="tradeClientExtensionsModify")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class TradeClientExtensionsModifyTransaction(Transaction):
    """Trade client extensions modification transaction."""

    type: TransactionType = Field(default=TransactionType.TRADE_CLIENT_EXTENSIONS_MODIFY, frozen=True)
    trade_id: str = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    trade_client_extensions_modify: ClientExtensions = Field(alias="tradeClientExtensionsModify")


class TradeClientExtensionsModifyRejectTransaction(Transaction):
    """Trade client extensions modification rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT, frozen=True)
    trade_id: TradeID = Field(alias="tradeID")
    client_trade_id: str | None = Field(None, alias="clientTradeID")
    trade_client_extensions_modify: ClientExtensions | None = Field(None, alias="tradeClientExtensionsModify")
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


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
    account_financing_mode: AccountFinancingMode | None = Field(None, alias="accountFinancingMode")
    position_financings: list[PositionFinancing] = Field(default_factory=list, alias="positionFinancings")


class DividendAdjustmentTransaction(Transaction):
    """Dividend adjustment transaction."""

    type: TransactionType = Field(default=TransactionType.DIVIDEND_ADJUSTMENT, frozen=True)
    instrument: InstrumentName | str
    dividend_adjustment: AccountUnits = Field(alias="dividendAdjustment")
    quote_dividend_adjustment: Decimal | None = Field(None, alias="quoteDividendAdjustment")
    home_conversion_factors: HomeConversionFactors | None = Field(None, alias="homeConversionFactors")
    open_trade_dividend_adjustments: list[OpenTradeDividendAdjustment] = Field(default_factory=list, alias="openTradeDividendAdjustments")
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
    funding_reason: FundingReason = Field(alias="fundingReason")
    comment: str | None = None
    account_balance: AccountUnits | None = Field(None, alias="accountBalance")


class TransferFundsRejectTransaction(Transaction):
    """Fund transfer rejection transaction."""

    type: TransactionType = Field(default=TransactionType.TRANSFER_FUNDS_REJECT, frozen=True)
    amount: AccountUnits
    funding_reason: FundingReason = Field(alias="fundingReason")
    comment: str | None = None
    reject_reason: TransactionRejectReason = Field(alias="rejectReason")


class MarginCallExtendTransaction(Transaction):
    """Margin call extension transaction."""

    type: TransactionType = Field(default=TransactionType.MARGIN_CALL_EXTEND, frozen=True)
    extension_number: int = Field(alias="extensionNumber")


class FixedPriceOrderTransaction(Transaction):
    """Fixed price order transaction (for dividend adjustments, etc.)."""

    type: TransactionType = Field(default=TransactionType.FIXED_PRICE_ORDER, frozen=True)
    instrument: InstrumentName | str
    units: Decimal
    price: PriceValue
    position_fill: OrderPositionFill = Field(alias="positionFill", default=OrderPositionFill.DEFAULT)
    trade_state: str = Field(alias="tradeState")
    reason: FixedPriceOrderReason
    client_extensions: ClientExtensions | None = Field(None, alias="clientExtensions")
    take_profit_on_fill: TakeProfitDetails | None = Field(None, alias="takeProfitOnFill")
    stop_loss_on_fill: StopLossDetails | None = Field(None, alias="stopLossOnFill")
    guaranteed_stop_loss_on_fill: GuaranteedStopLossDetails | None = Field(None, alias="guaranteedStopLossOnFill")
    trailing_stop_loss_on_fill: TrailingStopLossDetails | None = Field(None, alias="trailingStopLossOnFill")
    trade_client_extensions: ClientExtensions | None = Field(None, alias="tradeClientExtensions")


class DelayedTradeClosureTransaction(Transaction):
    """Delayed trade close transaction."""

    type: TransactionType = Field(default=TransactionType.DELAYED_TRADE_CLOSURE, frozen=True)
    trade_ids: TradeID = Field(alias="tradeIDs")
    reason: MarketOrderReason


class TransactionQueryFilter(ApiModel):
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
# - TransactionRejectDetails, TransactionSummary, TransactionBatch
# - AccountChangesState, AccountChanges (these are now properly in accounts.py)
# Note: TransactionHeartbeat IS part of the OANDA API (used in transaction streaming)


# Union type for all possible transaction types
TransactionUnion = (
    OrderFillTransaction
    | OrderCancelTransaction
    | MarketOrderTransaction
    | CreateTransaction
    | ClientConfigureTransaction
    | ClientConfigureRejectTransaction
    | LimitOrderTransaction
    | LimitOrderRejectTransaction
    | MarketOrderRejectTransaction
    | StopOrderTransaction
    | StopOrderRejectTransaction
    | TakeProfitOrderTransaction
    | TakeProfitOrderRejectTransaction
    | StopLossOrderTransaction
    | StopLossOrderRejectTransaction
    | TrailingStopLossOrderTransaction
    | TrailingStopLossOrderRejectTransaction
    | GuaranteedStopLossOrderTransaction
    | GuaranteedStopLossOrderRejectTransaction
    | MarketIfTouchedOrderTransaction
    | MarketIfTouchedOrderRejectTransaction
    | OrderCancelRejectTransaction
    | OrderClientExtensionsModifyTransaction
    | OrderClientExtensionsModifyRejectTransaction
    | TradeClientExtensionsModifyTransaction
    | TradeClientExtensionsModifyRejectTransaction
    | MarginCallEnterTransaction
    | MarginCallExitTransaction
    | DailyFinancingTransaction
    | DividendAdjustmentTransaction
    | ResetResettablePLTransaction
    | CloseTransaction
    | ReopenTransaction
    | TransferFundsTransaction
    | TransferFundsRejectTransaction
    | MarginCallExtendTransaction
    | FixedPriceOrderTransaction
    | DelayedTradeClosureTransaction
)


# Maps every OANDA transaction type discriminator to its model. Must stay
# exhaustive over the official TransactionType set — verified by unit test.
_TRANSACTION_TYPE_MAP: dict[str, type[TransactionUnion]] = {
    "CREATE": CreateTransaction,
    "CLOSE": CloseTransaction,
    "REOPEN": ReopenTransaction,
    "CLIENT_CONFIGURE": ClientConfigureTransaction,
    "CLIENT_CONFIGURE_REJECT": ClientConfigureRejectTransaction,
    "TRANSFER_FUNDS": TransferFundsTransaction,
    "TRANSFER_FUNDS_REJECT": TransferFundsRejectTransaction,
    "MARKET_ORDER": MarketOrderTransaction,
    "MARKET_ORDER_REJECT": MarketOrderRejectTransaction,
    "FIXED_PRICE_ORDER": FixedPriceOrderTransaction,
    "LIMIT_ORDER": LimitOrderTransaction,
    "LIMIT_ORDER_REJECT": LimitOrderRejectTransaction,
    "STOP_ORDER": StopOrderTransaction,
    "STOP_ORDER_REJECT": StopOrderRejectTransaction,
    "MARKET_IF_TOUCHED_ORDER": MarketIfTouchedOrderTransaction,
    "MARKET_IF_TOUCHED_ORDER_REJECT": MarketIfTouchedOrderRejectTransaction,
    "TAKE_PROFIT_ORDER": TakeProfitOrderTransaction,
    "TAKE_PROFIT_ORDER_REJECT": TakeProfitOrderRejectTransaction,
    "STOP_LOSS_ORDER": StopLossOrderTransaction,
    "STOP_LOSS_ORDER_REJECT": StopLossOrderRejectTransaction,
    "GUARANTEED_STOP_LOSS_ORDER": GuaranteedStopLossOrderTransaction,
    "GUARANTEED_STOP_LOSS_ORDER_REJECT": GuaranteedStopLossOrderRejectTransaction,
    "TRAILING_STOP_LOSS_ORDER": TrailingStopLossOrderTransaction,
    "TRAILING_STOP_LOSS_ORDER_REJECT": TrailingStopLossOrderRejectTransaction,
    "ORDER_FILL": OrderFillTransaction,
    "ORDER_CANCEL": OrderCancelTransaction,
    "ORDER_CANCEL_REJECT": OrderCancelRejectTransaction,
    "ORDER_CLIENT_EXTENSIONS_MODIFY": OrderClientExtensionsModifyTransaction,
    "ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT": OrderClientExtensionsModifyRejectTransaction,
    "TRADE_CLIENT_EXTENSIONS_MODIFY": TradeClientExtensionsModifyTransaction,
    "TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT": TradeClientExtensionsModifyRejectTransaction,
    "MARGIN_CALL_ENTER": MarginCallEnterTransaction,
    "MARGIN_CALL_EXTEND": MarginCallExtendTransaction,
    "MARGIN_CALL_EXIT": MarginCallExitTransaction,
    "DELAYED_TRADE_CLOSURE": DelayedTradeClosureTransaction,
    "DAILY_FINANCING": DailyFinancingTransaction,
    "DIVIDEND_ADJUSTMENT": DividendAdjustmentTransaction,
    "RESET_RESETTABLE_PL": ResetResettablePLTransaction,
}


def parse_transaction(transaction_data: dict[str, Any]) -> TransactionUnion:
    """Parse a concrete transaction consistently in responses and nested account data."""
    transaction_type = transaction_data.get("type")
    model = _TRANSACTION_TYPE_MAP.get(transaction_type or "")
    if model is None:
        raise ValueError(f"Unknown transaction type: {transaction_type}")
    return model.model_validate(transaction_data)


# Export all transaction-related models
__all__ = [
    "ClientConfigureRejectTransaction",
    "ClientConfigureTransaction",
    "CloseTransaction",
    "CreateTransaction",
    "DailyFinancingTransaction",
    "DelayedTradeClosureTransaction",
    "DividendAdjustmentTransaction",
    "FixedPriceOrderTransaction",
    "GuaranteedStopLossOrderRejectTransaction",
    "GuaranteedStopLossOrderTransaction",
    "LimitOrderRejectTransaction",
    "LimitOrderTransaction",
    "LiquidityRegenerationSchedule",
    "LiquidityRegenerationScheduleStep",
    "MarginCallEnterTransaction",
    "MarginCallExitTransaction",
    "MarginCallExtendTransaction",
    "MarketIfTouchedOrderRejectTransaction",
    "MarketIfTouchedOrderTransaction",
    "MarketOrderRejectTransaction",
    "MarketOrderTransaction",
    "OpenTradeDividendAdjustment",
    "OpenTradeFinancing",
    "OrderCancelRejectTransaction",
    "OrderCancelTransaction",
    "OrderClientExtensionsModifyRejectTransaction",
    "OrderClientExtensionsModifyTransaction",
    "OrderFillTransaction",
    "PositionFinancing",
    "ReopenTransaction",
    "ResetResettablePLTransaction",
    "StopLossOrderRejectTransaction",
    "StopLossOrderTransaction",
    "StopOrderRejectTransaction",
    "StopOrderTransaction",
    "TakeProfitOrderRejectTransaction",
    "TakeProfitOrderTransaction",
    "TradeClientExtensionsModifyRejectTransaction",
    "TradeClientExtensionsModifyTransaction",
    "TradeOpen",
    "TradeReduce",
    "TrailingStopLossOrderRejectTransaction",
    "TrailingStopLossOrderTransaction",
    "Transaction",
    "TransactionHeartbeat",
    "TransactionIDRange",
    "TransactionQueryFilter",
    "TransferFundsRejectTransaction",
    "TransferFundsTransaction",
]
