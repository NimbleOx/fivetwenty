# Order Models

**OANDA Reference**: [Order Data Definitions](https://developer.oanda.com/rest-live-v20/order-df/)

Models for creating, managing, and tracking orders across all order types and lifecycle states.

---

## Order Request Models

### MarketOrderRequest
Request to create a market order (immediate execution at current market price).

🔗 **OANDA Definition**: [MarketOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_12)

🔗 **Source**: [MarketOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to MARKET) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (restricted to "FOK" or "IOC" for market orders) |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ➖ | How positions are modified when order is filled (OPEN_ONLY, REDUCE_FIRST, REDUCE_ONLY, DEFAULT) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created by this order |

### LimitOrderRequest
Request to create a limit order (execution at specific price or better).

🔗 **OANDA Definition**: [LimitOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_13)

🔗 **Source**: [LimitOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to LIMIT) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold for order execution (string, equal to or better price required) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (GTC, GTD, GFD, FOK, IOC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ➖ | How positions are modified when order is filled |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created by this order |

### StopOrderRequest
Request to create a stop order (market order triggered at specific price).

🔗 **OANDA Definition**: [StopOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_14)

🔗 **Source**: [StopOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to STOP) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Stop price threshold (equal to or worse price triggers execution) |
| `price_bound` | [PriceValue](system-models.md#type-aliases) |➖ | Worst acceptable fill price after trigger to prevent excessive slippage |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ➖ | How positions are modified when order is filled |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created by this order |

### TakeProfitOrderRequest
Request to create a take profit order linked to an open trade.

🔗 **OANDA Definition**: [TakeProfitOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitOrderRequest)

🔗 **Source**: [TakeProfitOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to TAKE_PROFIT) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade identifier to close |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold for order execution |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |

### StopLossOrderRequest
Request to create a stop loss order linked to an open trade.

🔗 **OANDA Definition**: [StopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#StopLossOrderRequest)

🔗 **Source**: [StopLossOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to STOP_LOSS) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade identifier to close |
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Price threshold for order execution (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from current price (either price or distance required) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `guaranteed` | bool | ➖ | Guaranteed execution flag |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |

### TrailingStopLossOrderRequest
Request to create a trailing stop loss order linked to an open trade.

🔗 **OANDA Definition**: [TrailingStopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossOrderRequest)

🔗 **Source**: [TrailingStopLossOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to TRAILING_STOP_LOSS) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade identifier to close |
| `distance` | Decimal | ✅ | Trailing distance from current price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |

### GuaranteedStopLossOrderRequest
Request to create a guaranteed stop loss order linked to an open trade.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossOrderRequest)

🔗 **Source**: [GuaranteedStopLossOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to GUARANTEED_STOP_LOSS) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade identifier to close |
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Price threshold for order execution (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from current price (either price or distance required) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `guaranteed_execution_premium` | [AccountUnits](system-models.md#type-aliases) |➖ | Premium cost for guaranteed execution |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |

### MarketIfTouchedOrderRequest
Request to create a market-if-touched order (market order triggered at specific price).

🔗 **OANDA Definition**: [MarketIfTouchedOrderRequest](https://developer.oanda.com/rest-live-v20/order-df/#MarketIfTouchedOrderRequest)

🔗 **Source**: [MarketIfTouchedOrderRequest](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | [OrderType](system-models.md#ordertype) | ➖ | Order type identifier (automatically set to MARKET_IF_TOUCHED) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold that triggers market execution |
| `price_bound` | [PriceValue](system-models.md#type-aliases) |➖ | Worst acceptable fill price after trigger to prevent excessive slippage |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (required when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ➖ | How positions are modified when order is filled |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ➖ | Price component used for triggering (DEFAULT, INVERSE, BID, ASK) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order (not available for MT4 accounts) |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details to be applied on fill |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details to be applied on fill |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details to be applied on fill |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details to be applied on fill |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created by this order |


## Order Response Models

### MarketOrder
Market order that executes immediately at current market price.

🔗 **OANDA Definition**: [MarketOrder](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrder)

🔗 **Source**: [MarketOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "MARKET" (default) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `price_bound` | [PriceValue](system-models.md#type-aliases) |➖ | Worst acceptable fill price |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trade_close` | [MarketOrderTradeClose](#marketordertradeclose) | ➖ | Trade close details (conditional) |
| `long_position_closeout` | [MarketOrderPositionCloseout](#marketorderpositioncloseout) | ➖ | Long position closeout details |
| `short_position_closeout` | [MarketOrderPositionCloseout](#marketorderpositioncloseout) | ➖ | Short position closeout details |
| `margin_closeout` | [MarketOrderMarginCloseout](#marketordermargincloseout) | ➖ | Margin closeout details |
| `delayed_trade_close` | [MarketOrderDelayedTradeClose](#marketorderdelayedtradeclose) | ➖ | Delayed trade close details |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### LimitOrder
Limit order that executes only at specified price or better.

🔗 **OANDA Definition**: [LimitOrder](https://developer.oanda.com/rest-live-v20/order-df/#LimitOrder)

🔗 **Source**: [LimitOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "LIMIT" (default) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold for order execution |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### StopOrder
Stop order that becomes a market order when price threshold is reached.

🔗 **OANDA Definition**: [StopOrder](https://developer.oanda.com/rest-live-v20/order-df/#StopOrder)

🔗 **Source**: [StopOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "STOP" (default) |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold for order execution |
| `price_bound` | [PriceValue](system-models.md#type-aliases) |➖ | Worst acceptable fill price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for any trades created |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### GuaranteedStopLossOrder
Guaranteed stop loss order linked to an open trade with guaranteed execution.

🔗 **OANDA Definition**: [GuaranteedStopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossOrder)

🔗 **Source**: [GuaranteedStopLossOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "GUARANTEED_STOP_LOSS" (default) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Price threshold for order execution |
| `distance` | Decimal | ➖ | Distance from current price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `guaranteed_execution_premium` | Decimal | ✅ | Premium charged for guaranteed execution |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |
| `replaces_order_id` | [OrderID](system-models.md#type-aliases) |➖ | ID of the order being replaced |
| `replaced_by_order_id` | [OrderID](system-models.md#type-aliases) |➖ | ID of the order that replaced this one |


### TakeProfitOrder
A Take Profit Order linked to an open Trade and created with a price threshold.

🔗 **OANDA Definition**: [TakeProfitOrder](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitOrder)

🔗 **Source**: [TakeProfitOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "TAKE_PROFIT" |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Trigger price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering (default: DEFAULT) |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### StopLossOrder
A Stop Loss Order linked to an open Trade and created with a price threshold.

🔗 **OANDA Definition**: [StopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#StopLossOrder)

🔗 **Source**: [StopLossOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "STOP_LOSS" |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Trigger price |
| `distance` | Decimal | ➖ | Distance from current price (alternative to price) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering (default: DEFAULT) |
| `guaranteed` | bool | ➖ | Guaranteed execution flag |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### TrailingStopLossOrder
A Trailing Stop Loss Order linked to an open Trade with a dynamic price distance.

🔗 **OANDA Definition**: [TrailingStopLossOrder](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossOrder)

🔗 **Source**: [TrailingStopLossOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "TRAILING_STOP_LOSS" (default) |
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `distance` | Decimal | ✅ | Trailing distance |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `trailing_stop_value` | [PriceValue](system-models.md#type-aliases) |➖ | Current trailing stop price |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

### MarketIfTouchedOrder
A Market-If-Touched Order created with a price threshold.

🔗 **OANDA Definition**: [MarketIfTouchedOrder](https://developer.oanda.com/rest-live-v20/order-df/#MarketIfTouchedOrder)

🔗 **Source**: [MarketIfTouchedOrder](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |✅ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |✅ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ✅ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "MARKET_IF_TOUCHED" |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Trigger price threshold |
| `price_bound` | [PriceValue](system-models.md#type-aliases) |➖ | Worst acceptable fill price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior (default: DEFAULT) |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering (default: DEFAULT) |
| `initial_market_price` | [PriceValue](system-models.md#type-aliases) |➖ | Initial market price when order was created |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details |
| `guaranteed_stop_loss_on_fill` | [GuaranteedStopLossDetails](#guaranteedstoplossdetails) | ➖ | Guaranteed stop loss order creation details |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for created trades |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |✅ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |
| `replaces_order_id` | [OrderID](system-models.md#type-aliases) |➖ | Replaced order ID |
| `replaced_by_order_id` | [OrderID](system-models.md#type-aliases) |➖ | Replacing order ID |

### FixedPriceOrder
A Fixed Price Order filled immediately at specified price.

🔗 **OANDA Definition**: [FixedPriceOrder](https://developer.oanda.com/rest-live-v20/order-df/#FixedPriceOrder)

**Note**: Fixed price orders are typically created by OANDA for specific circumstances (e.g., dividend adjustments). They cannot be directly created via API requests.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [OrderID](system-models.md#type-aliases) |➖ | Order's identifier, unique within Account |
| `create_time` | [DateTime](system-models.md#type-aliases) |➖ | Time when Order was created |
| `state` | [OrderState](system-models.md#orderstate) | ➖ | Current state of the Order |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions (not for MT4 accounts) |
| `type` | str | ➖ | Always "FIXED_PRICE" |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument |
| `units` | Decimal | ✅ | Number of units to trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) |✅ | Exact fill price |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ➖ | Position modification behavior (default: DEFAULT) |
| `trade_state` | str | ✅ | Resulting trade state |
| `take_profit_on_fill` | [TakeProfitDetails](#takeprofitdetails) | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | [StopLossDetails](#stoplossdetails) | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | [TrailingStopLossDetails](#trailingstoplossdetails) | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for created trades |
| `filling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Fill transaction ID (when FILLED) |
| `filled_time` | [DateTime](system-models.md#type-aliases) |➖ | Fill timestamp (when FILLED) |
| `trade_opened_id` | [TradeID](system-models.md#type-aliases) |➖ | Opened trade ID (when FILLED) |
| `trade_reduced_id` | [TradeID](system-models.md#type-aliases) |➖ | Reduced trade ID (when FILLED) |
| `trade_closed_ids` | list[[TradeID](system-models.md#type-aliases)] |➖ | Closed trade IDs (when FILLED) |
| `cancelling_transaction_id` | [TransactionID](system-models.md#type-aliases) |➖ | Cancel transaction ID (when CANCELLED) |
| `cancelled_time` | [DateTime](system-models.md#type-aliases) |➖ | Cancel timestamp (when CANCELLED) |

## Order Details Models

### TakeProfitDetails
Details for creating a Take Profit Order on fill.

🔗 **OANDA Definition**: [TakeProfitDetails](https://developer.oanda.com/rest-live-v20/order-df/#TakeProfitDetails)

🔗 **Source**: [TakeProfitDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Take profit trigger price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the take profit order |

### StopLossDetails
Details for creating a Stop Loss Order on fill.

🔗 **OANDA Definition**: [StopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#StopLossDetails)

🔗 **Source**: [StopLossDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Stop loss trigger price (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from fill price (either price or distance required) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `guaranteed` | bool | ➖ | Guaranteed execution flag (default: False) |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the stop loss order |

### TrailingStopLossDetails
Details for creating a Trailing Stop Loss Order on fill.

🔗 **OANDA Definition**: [TrailingStopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#TrailingStopLossDetails)

🔗 **Source**: [TrailingStopLossDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `distance` | Decimal | ✅ | Trailing distance from fill price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (default: GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp (when time_in_force is "GTD") |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the trailing stop loss order |

### ClientExtensions
Client-provided metadata for Orders and Trades.

🔗 **OANDA Definition**: [ClientExtensions](https://developer.oanda.com/rest-live-v20/order-df/#ClientExtensions)

🔗 **Source**: [ClientExtensions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ➖ | Client-provided identifier (max 64 characters) |
| `tag` | str | ➖ | Client-provided tag (max 255 characters) |
| `comment` | str | ➖ | Client-provided comment (max 255 characters) |

### GuaranteedStopLossDetails
Details for guaranteed stop loss orders that ensure execution at guaranteed price.

🔗 **OANDA Definition**: [GuaranteedStopLossDetails](https://developer.oanda.com/rest-live-v20/order-df/#GuaranteedStopLossDetails)

🔗 **Source**: [GuaranteedStopLossDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `distance` | Decimal | ➖ | Distance from current price to guaranteed stop loss price |
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Price threshold for guaranteed stop loss execution |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ➖ | Order duration policy (defaults to GTC) |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `client_extensions` | [ClientExtensions](#clientextensions) | ➖ | Client extensions for the order |
| `guaranteed_execution_premium` | [AccountUnits](system-models.md#type-aliases) |➖ | Premium charged for guaranteed execution |

### DynamicOrderState
The dynamic state of an order, including current calculations and trigger information.

🔗 **OANDA Definition**: [DynamicOrderState](https://developer.oanda.com/rest-live-v20/order-df/#DynamicOrderState)

🔗 **Source**: [DynamicOrderState](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str | ✅ | Order identifier |
| `trailing_stop_value` | [PriceValue](system-models.md#type-aliases) |➖ | Current trailing stop value for trailing stop orders |
| `trigger_distance` | Decimal | ➖ | Current trigger distance for distance-based orders |
| `is_trigger_distance_exact` | bool | ➖ | Whether the trigger distance is exact or approximate |

## Order Support Models

### MarketOrderTradeClose
Details for closing specific trades with market orders.

🔗 **OANDA Definition**: [MarketOrderTradeClose](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderTradeClose)

🔗 **Source**: [MarketOrderTradeClose](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `units` | Decimal | ✅ | Number of units to close (ALL or partial amount) |

### MarketOrderPositionCloseout
Details for position closeout via market order.

🔗 **OANDA Definition**: [MarketOrderPositionCloseout](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderPositionCloseout)

🔗 **Source**: [MarketOrderPositionCloseout](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Instrument to close position for |
| `units` | Decimal | ✅ | Number of units to close (ALL or partial amount) |

### MarketOrderMarginCloseout
Details for margin closeout market order.

🔗 **OANDA Definition**: [MarketOrderMarginCloseout](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderMarginCloseout)

🔗 **Source**: [MarketOrderMarginCloseout](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `reason` | str | ✅ | Reason for margin closeout |

### MarketOrderDelayedTradeClose
Details for delayed trade close market order.

🔗 **OANDA Definition**: [MarketOrderDelayedTradeClose](https://developer.oanda.com/rest-live-v20/order-df/#MarketOrderDelayedTradeClose)

🔗 **Source**: [MarketOrderDelayedTradeClose](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/orders.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `source_transaction_id` | [TransactionID](system-models.md#type-aliases) |✅ | Transaction that initiated the delay |

