# Transaction Models

**OANDA Reference**: [Transaction Data Definitions](https://developer.oanda.com/rest-live-v20/transaction-df/)

Models for transaction history, order fills, and account activity tracking.

---

## Base Transaction Models

### Transaction
Base transaction information (all transactions inherit these fields).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | [TransactionID](system-models.md#type-aliases) |✅ | Transaction's identifier (positive integer assigned sequentially by OANDA) |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Date/time when the transaction occurred |
| `user_id` | int | ✅ | User ID of the user that initiated the transaction |
| `account_id` | [AccountID](system-models.md#type-aliases) |✅ | Account identifier for the account the transaction affects |
| `batch_id` | [TransactionID](system-models.md#type-aliases) |✅ | Transaction batch identifier for grouping related transactions |
| `request_id` | [RequestID](system-models.md#type-aliases) | ➖ | Client-provided request identifier for correlating API requests with transactions |
| `type` | [TransactionType](enum-models.md#transactiontype) | ✅ | Type of transaction (CREATE, MARKET_ORDER, STOP_LOSS_ORDER, etc.) |

### TransactionFilter
Filter criteria for transaction queries.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_` | str | ➖ | Starting transaction ID for filtering |
| `to` | str | ➖ | Ending transaction ID for filtering |
| `page_size` | int | ➖ | Maximum number of transactions to return |
| `type_filter` | list[[TransactionType](enum-models.md#transactiontype)] | ➖ | Transaction types to include in results |

### TransactionIDRange
Range of transaction IDs for querying transaction history.

🔗 **OANDA Definition**: [TransactionIDRange](https://developer.oanda.com/rest-live-v20/transaction-df/#TransactionIDRange)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_` | str | ✅ | Starting transaction ID (inclusive) |
| `to` | str | ✅ | Ending transaction ID (inclusive) |

---

## Supporting Transaction Models

### TradeOpen
Details of a new trade created as part of an OrderFill.

🔗 **OANDA Definition**: [TradeOpen](https://developer.oanda.com/rest-live-v20/transaction-df/#TradeOpen)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) | ✅ | Unique identifier for the new trade |
| `units` | Decimal | ✅ | Number of units in the new trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Average price at which the trade was opened |
| `guaranteed_execution_fee` | [AccountUnits](system-models.md#type-aliases) | ➖ | Guaranteed execution fee charged for the trade in account currency |
| `quote_guaranteed_execution_fee` | Decimal | ➖ | Guaranteed execution fee in quote currency |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client-provided metadata for the trade |
| `half_spread_cost` | [AccountUnits](system-models.md#type-aliases) | ➖ | Half-spread cost for opening the trade in account currency |
| `initial_margin_required` | [AccountUnits](system-models.md#type-aliases) | ➖ | Initial margin requirement for the trade |

### TradeReduce
Details of a trade that was reduced or fully closed as part of an OrderFill.

🔗 **OANDA Definition**: [TradeReduce](https://developer.oanda.com/rest-live-v20/transaction-df/#TradeReduce)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) | ✅ | Unique identifier for the reduced/closed trade |
| `units` | Decimal | ✅ | Number of units reduced from the trade (positive for long, negative for short) |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Average price at which the trade was reduced/closed |
| `realized_pl` | [AccountUnits](system-models.md#type-aliases) | ➖ | Realized profit/loss from the reduction in account currency |
| `financing` | [AccountUnits](system-models.md#type-aliases) | ➖ | Financing charges/credits applied during reduction in account currency |
| `base_financing` | Decimal | ➖ | Financing in base currency |
| `quote_financing` | Decimal | ➖ | Financing in quote currency |
| `financing_rate` | Decimal | ➖ | Financing rate applied |
| `guaranteed_execution_fee` | [AccountUnits](system-models.md#type-aliases) | ➖ | Guaranteed execution fee charged in account currency |
| `quote_guaranteed_execution_fee` | Decimal | ➖ | Guaranteed execution fee in quote currency |
| `half_spread_cost` | [AccountUnits](system-models.md#type-aliases) | ➖ | Half-spread cost for closing the trade in account currency |

---

## Order Execution Transactions

### OrderFillTransaction
Transaction created when an order is filled.

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | [OrderID](system-models.md#type-aliases) |✅ | ID of the Order that was filled |
| `client_order_id` | str | ➖ | Client-specified order identifier |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the fill |
| `units` | Decimal | ✅ | Number of units filled by the order |
| `gain_quote_home_conversion_factor` | Decimal | ➖ | Conversion factor for gain calculation |
| `loss_quote_home_conversion_factor` | Decimal | ➖ | Conversion factor for loss calculation |
| `price` | [PriceValue](system-models.md#type-aliases) | ➖ | Execution price for the fill |
| `full_vwap` | [PriceValue](system-models.md#type-aliases) | ➖ | Volume weighted average price for the fill |
| `full_price` | FullPrice | ➖ | Complete pricing information including closeout bid/ask |
| `reason` | str | ➖ | Reason for the order fill |
| `pl` | Decimal | ➖ | Realized profit/loss from the fill |
| `financing` | Decimal | ➖ | Financing applied to the fill |
| `commission` | Decimal | ➖ | Commission charged for the fill |
| `guarantee_execution_fee` | Decimal | ➖ | Guaranteed execution fee charged |
| `account_balance` | Decimal | ➖ | Account balance after the fill transaction |
| `trade_opened` | [TradeOpen](#tradeopen) | ➖ | Details of new trade created by the fill |
| `trades_closed` | list[[TradeReduce](#tradereduce)] | ➖ | List of trades closed by the fill |
| `trade_reduced` | [TradeReduce](#tradereduce) | ➖ | Details of trade reduced by the fill |
| `half_spread_cost` | Decimal | ➖ | Half spread cost for the fill |

### OrderCancelTransaction
Transaction created when an order is cancelled.

🔗 **OANDA Definition**: [OrderCancelTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#OrderCancelTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | [OrderID](system-models.md#type-aliases) |✅ | ID of the Order that was cancelled |
| `client_order_id` | str | ➖ | Client-specified order identifier |
| `reason` | str | ➖ | Reason for the order cancellation |
| `replaced_by_order_id` | [OrderID](system-models.md#type-aliases) |➖ | ID of the order that replaced this one |

## Order Creation Transactions

### MarketOrderTransaction
Transaction created when a Market Order is submitted.

🔗 **OANDA Definition**: [MarketOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy (FOK or IOC only) |
| `price_bound` | [PriceValue](system-models.md#type-aliases) | ➖ | Worst acceptable fill price |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trade_close` | dict | ➖ | Trade close details |
| `long_position_closeout` | dict | ➖ | Long position closeout details |
| `short_position_closeout` | dict | ➖ | Short position closeout details |
| `margin_closeout` | dict | ➖ | Margin closeout details |
| `delayed_trade_close` | dict | ➖ | Delayed trade close details |
| `reason` | str | ➖ | Reason for creating the market order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |
| `take_profit_on_fill` | dict | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | dict | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | dict | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for created trades |

### LimitOrderTransaction
Transaction created when a Limit Order is submitted.

🔗 **OANDA Definition**: [LimitOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#LimitOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Price threshold for order execution |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `reason` | str | ➖ | Reason for creating the limit order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |
| `take_profit_on_fill` | dict | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | dict | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | dict | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for created trades |

### StopOrderTransaction
Transaction created when a Stop Order is submitted.

🔗 **OANDA Definition**: [StopOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#StopOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument for the order |
| `units` | Decimal | ✅ | Number of units to trade |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Stop price threshold |
| `price_bound` | [PriceValue](system-models.md#type-aliases) | ➖ | Worst acceptable fill price after trigger |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `position_fill` | [OrderPositionFill](system-models.md#orderpositionfill) | ✅ | Position modification behavior |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `reason` | str | ➖ | Reason for creating the stop order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |
| `take_profit_on_fill` | dict | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | dict | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | dict | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for created trades |

## Specialized Order Transactions

### TakeProfitOrderTransaction
Transaction created when a Take Profit Order is submitted.

🔗 **OANDA Definition**: [TakeProfitOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close with take profit order |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Take profit trigger price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `reason` | str | ➖ | Reason for creating the take profit order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |

### StopLossOrderTransaction
Transaction created when a Stop Loss Order is submitted.

🔗 **OANDA Definition**: [StopLossOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#StopLossOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close with stop loss order |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Stop loss trigger price |
| `distance` | Decimal | ➖ | Distance from trade price (alternative to price) |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `guaranteed` | bool | ➖ | Guaranteed execution flag (default: False) |
| `reason` | str | ➖ | Reason for creating the stop loss order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |

### TrailingStopLossOrderTransaction
Transaction created when a Trailing Stop Loss Order is submitted.

🔗 **OANDA Definition**: [TrailingStopLossOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#TrailingStopLossOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | [TradeID](system-models.md#type-aliases) |✅ | Trade to close with trailing stop loss order |
| `client_trade_id` | str | ➖ | Client-provided trade identifier |
| `distance` | Decimal | ✅ | Trailing distance from trade price |
| `time_in_force` | [TimeInForce](system-models.md#timeinforce) | ✅ | Order duration policy |
| `gtd_time` | [DateTime](system-models.md#type-aliases) |➖ | Good-till-date expiration timestamp |
| `trigger_condition` | [OrderTriggerCondition](system-models.md#ordertriggercondition) | ✅ | Price component used for triggering |
| `reason` | str | ➖ | Reason for creating the trailing stop loss order |
| `client_extensions` | [ClientExtensions](order-models.md#clientextensions) | ➖ | Client extensions for the order |