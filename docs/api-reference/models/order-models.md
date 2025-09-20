# Order Models

📖 **OANDA Reference**: [Order Data Definitions](https://developer.oanda.com/rest-live-v20/order-df/)

Models for creating, managing, and tracking orders across all order types and lifecycle states.

---

## Order Request Models

### MarketOrderRequest
Request to create a market order (immediate execution at current market price).

🔗 **OANDA Definition**: [MarketOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_12)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to MARKET) |
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (restricted to "FOK" or "IOC" for market orders) |
| `position_fill` | OrderPositionFill | ➖ | How positions are modified when order is filled (OPEN_ONLY, REDUCE_FIRST, REDUCE_ONLY, DEFAULT) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created by this order |

### LimitOrderRequest
Request to create a limit order (execution at specific price or better).

🔗 **OANDA Definition**: [LimitOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_13)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to LIMIT) |
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Price threshold for order execution (string, equal to or better price required) |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (GTC, GTD, GFD, FOK, IOC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ➖ | How positions are modified when order is filled |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created by this order |

### StopOrderRequest
Request to create a stop order (market order triggered at specific price).

🔗 **OANDA Definition**: [StopOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_14)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to STOP) |
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Stop price threshold (equal to or worse price triggers execution) |
| `price_bound` | PriceValue | ➖ | Worst acceptable fill price after trigger to prevent excessive slippage |
| `time_in_force` | TimeInForce | ➖ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ➖ | How positions are modified when order is filled |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created by this order |

### TakeProfitOrderRequest
Request to create a take profit order linked to an open trade.

🔗 **OANDA Definition**: [TakeProfitOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to TAKE_PROFIT) |
| `trade_id` | TradeID | ✅ | Trade identifier to close |
| `price` | PriceValue | ✅ | Price threshold for order execution |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |

### StopLossOrderRequest
Request to create a stop loss order linked to an open trade.

🔗 **OANDA Definition**: [StopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#StopLossOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to STOP_LOSS) |
| `trade_id` | TradeID | ✅ | Trade identifier to close |
| `price` | PriceValue | ➖ | Price threshold for order execution (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from current price (either price or distance required) |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `guaranteed` | bool | ➖ | Guaranteed execution flag |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |

### TrailingStopLossOrderRequest
Request to create a trailing stop loss order linked to an open trade.

🔗 **OANDA Definition**: [TrailingStopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to TRAILING_STOP_LOSS) |
| `trade_id` | TradeID | ✅ | Trade identifier to close |
| `distance` | Decimal | ✅ | Trailing distance from current price |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |

### GuaranteedStopLossOrderRequest
Request to create a guaranteed stop loss order linked to an open trade.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to GUARANTEED_STOP_LOSS) |
| `trade_id` | TradeID | ✅ | Trade identifier to close |
| `price` | PriceValue | ➖ | Price threshold for order execution (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from current price (either price or distance required) |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `guaranteed_execution_premium` | AccountUnits | ➖ | Premium cost for guaranteed execution |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |

### MarketIfTouchedOrderRequest
Request to create a market-if-touched order (market order triggered at specific price).

🔗 **OANDA Definition**: [MarketIfTouchedOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#MarketIfTouchedOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to MARKET_IF_TOUCHED) |
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Price threshold that triggers market execution |
| `price_bound` | PriceValue | ➖ | Worst acceptable fill price after trigger to prevent excessive slippage |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ➖ | How positions are modified when order is filled |
| `trigger_condition` | OrderTriggerCondition | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created by this order |

### FixedPriceOrderRequest
Request to create a fixed price order (immediate execution at specified price).

🔗 **OANDA Definition**: [FixedPriceOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#FixedPriceOrderRequest)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | OrderType | ➖ | Order type identifier (automatically set to FIXED_PRICE) |
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Exact execution price |
| `position_fill` | OrderPositionFill | ➖ | How positions are modified when order is filled (default: DEFAULT) |
| `trade_state` | str | ✅ | Resulting trade state |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created by this order |

## Order Response Models

### MarketOrder
Market order that executes immediately at current market price.

🔗 **OANDA Definition**: [MarketOrder](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "MARKET" (default) |
| `instrument` | InstrumentName | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `price_bound` | PriceValue | ➖ | Worst acceptable fill price |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trade_close` | MarketOrderTradeClose | ➖ | Trade close details (conditional) |
| `long_position_closeout` | MarketOrderPositionCloseout | ➖ | Long position closeout details |
| `short_position_closeout` | MarketOrderPositionCloseout | ➖ | Short position closeout details |
| `margin_closeout` | MarketOrderMarginCloseout | ➖ | Margin closeout details |
| `delayed_trade_close` | MarketOrderDelayedTradeClose | ➖ | Delayed trade close details |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### LimitOrder
Limit order that executes only at specified price or better.

🔗 **OANDA Definition**: [LimitOrder](https://developer.oanda.com/rest-live-v20/order-df/#LimitOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "LIMIT" (default) |
| `instrument` | InstrumentName | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Price threshold for order execution |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### StopOrder
Stop order that becomes a market order when price threshold is reached.

🔗 **OANDA Definition**: [StopOrder](https://developer.oanda.com/rest-live-v20/order-df/#StopOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "STOP" (default) |
| `instrument` | InstrumentName | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Price threshold for order execution |
| `price_bound` | PriceValue | ➖ | Worst acceptable fill price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### GuaranteedStopLossOrder
Guaranteed stop loss order linked to an open trade with guaranteed execution.

🔗 **OANDA Definition**: [GuaranteedStopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "GUARANTEED_STOP_LOSS" (default) |
| `trade_id` | TradeID | ✅ | Trade to close |
| `price` | PriceValue | ✅ | Price threshold for order execution |
| `distance` | Decimal | ➖ | Distance from current price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `guaranteed_execution_premium` | Decimal | ✅ | Premium charged for guaranteed execution |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `replaced_by_order_id` | OrderID | ➖ | ID of the order that replaced this one |

### OrderResponse
Response from order creation/modification requests.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_create_transaction` | Transaction | ➖ | Transaction that created the order |
| `order_fill_transaction` | OrderFillTransaction | ➖ | Transaction that filled the order (if immediately filled) |
| `order_cancel_transaction` | OrderCancelTransaction | ➖ | Transaction that cancelled the order |
| `order_reissue_transaction` | Transaction | ➖ | Transaction that reissued the order |
| `order_reissue_reject_transaction` | Transaction | ➖ | Transaction that rejected order reissue |
| `related_transaction_ids` | list[TransactionID] | ✅ | IDs of all transactions related to this order request |
| `last_transaction_id` | TransactionID | ✅ | Most recent transaction ID in the account |

### TakeProfitOrder
A Take Profit Order linked to an open Trade and created with a price threshold.

🔗 **OANDA Definition**: [TakeProfitOrder](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "TAKE_PROFIT" |
| `trade_id` | TradeID | ✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | PriceValue | ✅ | Trigger price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering (default: DEFAULT) |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### StopLossOrder
A Stop Loss Order linked to an open Trade and created with a price threshold.

🔗 **OANDA Definition**: [StopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#StopLossOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "STOP_LOSS" |
| `trade_id` | TradeID | ✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | PriceValue | ➖ | Trigger price |
| `distance` | Decimal | ➖ | Distance from current price (alternative to price) |
| `time_in_force` | TimeInForce | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering (default: DEFAULT) |
| `guaranteed` | bool | ➖ | Guaranteed execution flag |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### TrailingStopLossOrder
A Trailing Stop Loss Order linked to an open Trade with a dynamic price distance.

🔗 **OANDA Definition**: [TrailingStopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "TRAILING_STOP_LOSS" (default) |
| `trade_id` | TradeID | ✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `distance` | Decimal | ✅ | Trailing distance |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `trailing_stop_value` | PriceValue | ➖ | Current trailing stop price |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

### MarketIfTouchedOrder
A Market-If-Touched Order created with a price threshold.

🔗 **OANDA Definition**: [MarketIfTouchedOrder](https://developer.oanda.com/rest-live-v20/order-df/#MarketIfTouchedOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ✅ | Order's identifier, unique within Account |
| `create_time` | DateTime | ✅ | Time when Order was created |
| `state` | OrderState | ✅ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "MARKET_IF_TOUCHED" |
| `instrument` | InstrumentName | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Trigger price threshold |
| `price_bound` | PriceValue | ➖ | Worst acceptable fill price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior (default: DEFAULT) |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering (default: DEFAULT) |
| `initial_market_price` | PriceValue | ➖ | Initial market price when order was created |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | GuaranteedStopLossDetails | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for created trades |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |
| `replaces_order_id` | OrderID | ➖ | Replaced order ID |
| `replaced_by_order_id` | OrderID | ➖ | Replacing order ID |

### FixedPriceOrder
A Fixed Price Order filled immediately at specified price.

🔗 **OANDA Definition**: [FixedPriceOrder](https://developer.oanda.com/rest-live-v20/order-df/#FixedPriceOrder)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | OrderID | ➖ | Order's identifier, unique within Account |
| `create_time` | DateTime | ➖ | Time when Order was created |
| `state` | OrderState | ➖ | Current state of the Order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "FIXED_PRICE" |
| `instrument` | InstrumentName | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | PriceValue | ✅ | Exact fill price |
| `position_fill` | OrderPositionFill | ➖ | Position modification behavior (default: DEFAULT) |
| `trade_state` | str | ✅ | Resulting trade state |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for created trades |
| `filling_transaction_id` | TransactionID | ➖ | Fill transaction ID (when FILLED) |
| `filled_time` | DateTime | ➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | TradeID | ➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | TradeID | ➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[TradeID] | ➖ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | TransactionID | ➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | DateTime | ➖ | Cancel timestamp (when CANCELLED) |

## Order Details Models

### TakeProfitDetails
Details for creating a Take Profit Order on fill.

🔗 **OANDA Definition**: [TakeProfitDetails](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitDetails)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | Decimal | ✅ | Take profit trigger price |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the take profit order |

### StopLossDetails
Details for creating a Stop Loss Order on fill.

🔗 **OANDA Definition**: [StopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#StopLossDetails)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | PriceValue | ➖ | Stop loss trigger price (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from fill price (either price or distance required) |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `guaranteed` | bool | ➖ | Guaranteed execution flag (default: False) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the stop loss order |

### TrailingStopLossDetails
Details for creating a Trailing Stop Loss Order on fill.

🔗 **OANDA Definition**: [TrailingStopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossDetails)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `distance` | Decimal | ✅ | Trailing distance from fill price |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the trailing stop loss order |

### ClientExtensions
Client-provided metadata for Orders and Trades.

🔗 **OANDA Definition**: [ClientExtensions](https://developer.oanda.com/rest-live-v20/order-df/#ClientExtensions)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ➖ | Client-provided identifier (max 64 characters) |
| `tag` | str | ➖ | Client-provided tag (max 255 characters) |
| `comment` | str | ➖ | Client-provided comment (max 255 characters) |

### GuaranteedStopLossDetails
Details for guaranteed stop loss orders that ensure execution at guaranteed price.

🔗 **OANDA Definition**: [GuaranteedStopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossDetails)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `distance` | Decimal | ➖ | Distance from current price to guaranteed stop loss price |
| `price` | PriceValue | ➖ | Price threshold for guaranteed stop loss execution |
| `time_in_force` | TimeInForce | ➖ | Order duration policy (defaults to GTC) |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `guaranteed_execution_premium` | AccountUnits | ➖ | Premium charged for guaranteed execution |

### DynamicOrderState
The dynamic state of an order, including current calculations and trigger information.

🔗 **OANDA Definition**: [DynamicOrderState](https://developer.oanda.com/rest-live-v20/order-df/#DynamicOrderState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ✅ | Order identifier |
| `trailing_stop_value` | PriceValue | ➖ | Current trailing stop value for trailing stop orders |
| `trigger_distance` | Decimal | ➖ | Current trigger distance for distance-based orders |
| `is_trigger_distance_exact` | bool | ➖ | Whether the trigger distance is exact or approximate |

## Order Support Models

### MarketOrderTradeClose
Details for closing specific trades with market orders.

🔗 **OANDA Definition**: [MarketOrderTradeClose](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderTradeClose)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | TradeID | ✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `units` | Decimal | ✅ | Number of units to close (ALL or partial amount) |

### MarketOrderPositionCloseout
Details for position closeout via market order.

🔗 **OANDA Definition**: [MarketOrderPositionCloseout](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderPositionCloseout)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Instrument to close position for |
| `units` | Decimal | ✅ | Number of units to close (ALL or partial amount) |

### MarketOrderMarginCloseout
Details for margin closeout market order.

🔗 **OANDA Definition**: [MarketOrderMarginCloseout](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderMarginCloseout)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | str | ✅ | Reason for margin closeout |

### MarketOrderDelayedTradeClose
Details for delayed trade close market order.

🔗 **OANDA Definition**: [MarketOrderDelayedTradeClose](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderDelayedTradeClose)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | TradeID | ✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `source_transaction_id` | TransactionID | ✅ | Transaction that initiated the delay |

### OrderIdentifier
Identification information for an Order.

🔗 **OANDA Definition**: [OrderIdentifier](https://developer.oanda.com/rest-live-v20/order-df/#OrderIdentifier)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | OrderID | ✅ | Order's OANDA-assigned identifier |
| `client_order_id` | str | ➖ | Client-provided order identifier |