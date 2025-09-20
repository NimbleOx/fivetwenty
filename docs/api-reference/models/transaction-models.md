# Transaction Models

📖 **OANDA Reference**: [Transaction Data Definitions](https://developer.oanda.com/rest-live-v20/transaction-df/)

Models for transaction history, order fills, and account activity tracking.

---

## Base Transaction Models

### Transaction
Base transaction information (all transactions inherit these fields).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | TransactionID | ✅ | Transaction's identifier (positive integer assigned sequentially by OANDA) |
| `time` | DateTime | ✅ | Date/time when the transaction occurred |
| `user_id` | int | ✅ | User ID of the user that initiated the transaction |
| `account_id` | AccountID | ✅ | Account identifier for the account the transaction affects |
| `batch_id` | TransactionID | ✅ | Transaction batch identifier for grouping related transactions |
| `request_id` | RequestID | ➖ | Client-provided request identifier for correlating API requests with transactions |
| `type` | TransactionType | ✅ | Type of transaction (CREATE, MARKET_ORDER, STOP_LOSS_ORDER, etc.) |

### TransactionFilter
Filter criteria for transaction queries.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_` | str | ➖ | Starting transaction ID for filtering |
| `to` | str | ➖ | Ending transaction ID for filtering |
| `page_size` | int | ➖ | Maximum number of transactions to return |
| `type_filter` | list[TransactionType] | ➖ | Transaction types to include in results |

### TransactionIDRange
Range of transaction IDs for querying transaction history.

🔗 **OANDA Definition**: [TransactionIDRange](https://developer.oanda.com/rest-live-v20/transaction-df/#TransactionIDRange)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_` | str | ✅ | Starting transaction ID (inclusive) |
| `to` | str | ✅ | Ending transaction ID (inclusive) |

## Order Execution Transactions

### OrderFillTransaction
Transaction created when an order is filled.

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | OrderID | ➖ | ID of the Order that was filled |
| `client_order_id` | str | ➖ | Client-specified order identifier |
| `instrument` | InstrumentName | ✅ | Trading instrument for the fill |
| `units` | int | ✅ | Number of units filled by the order |
| `price` | Decimal | ✅ | Execution price for the fill |
| `pl` | Decimal | ✅ | Realized profit/loss from the fill |
| `financing` | Decimal | ✅ | Financing applied to the fill |
| `commission` | Decimal | ✅ | Commission charged for the fill |
| `dividend_adjustment` | Decimal | ✅ | Dividend adjustment applied to the fill |
| `account_balance` | Decimal | ✅ | Account balance after the fill transaction |
| `trade_opened` | TradeOpen | ➖ | Details of new trade created by the fill |
| `trades_closed` | list[TradeReduce] | ✅ | List of trades closed by the fill |
| `trade_reduced` | TradeReduce | ➖ | Details of trade reduced by the fill |
| `reason` | OrderFillReason | ✅ | Reason for the order fill |
| `guaranteed_execution_fee` | Decimal | ➖ | Guaranteed execution fee charged |
| `quote_guaranteed_execution_fee` | Decimal | ➖ | Guaranteed execution fee in quote currency |
| `half_spread_cost` | Decimal | ➖ | Half spread cost for the fill |
| `full_vwap` | Decimal | ➖ | Volume weighted average price for the fill |

### OrderCancelTransaction
Transaction created when an order is cancelled.

🔗 **OANDA Definition**: [OrderCancelTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#OrderCancelTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `order_id` | OrderID | ✅ | ID of the Order that was cancelled |
| `client_order_id` | str | ➖ | Client-specified order identifier |
| `reason` | OrderCancelReason | ✅ | Reason for the order cancellation |
| `replaced_by_order_id` | OrderID | ➖ | ID of the order that replaced this one |

## Order Creation Transactions

### MarketOrderTransaction
Transaction created when a Market Order is submitted.

🔗 **OANDA Definition**: [MarketOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | int | ✅ | Number of units to trade |
| `time_in_force` | TimeInForce | ✅ | Order duration policy (FOK or IOC only) |
| `price_bound` | Decimal | ➖ | Worst acceptable fill price |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trade_close` | MarketOrderTradeClose | ➖ | Trade close details |
| `long_position_closeout` | MarketOrderPositionCloseout | ➖ | Long position closeout details |
| `short_position_closeout` | MarketOrderPositionCloseout | ➖ | Short position closeout details |
| `margin_closeout` | MarketOrderMarginCloseout | ➖ | Margin closeout details |
| `delayed_trade_close` | MarketOrderDelayedTradeClose | ➖ | Delayed trade close details |
| `reason` | MarketOrderReason | ✅ | Reason for creating the market order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for created trades |

### LimitOrderTransaction
Transaction created when a Limit Order is submitted.

🔗 **OANDA Definition**: [LimitOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#LimitOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | int | ✅ | Number of units to trade |
| `price` | Decimal | ✅ | Price threshold for order execution |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `reason` | LimitOrderReason | ✅ | Reason for creating the limit order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for created trades |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `cancelling_transaction_id` | TransactionID | ➖ | ID of transaction that cancelled this order |

### StopOrderTransaction
Transaction created when a Stop Order is submitted.

🔗 **OANDA Definition**: [StopOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#StopOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Trading instrument for the order |
| `units` | int | ✅ | Number of units to trade |
| `price` | Decimal | ✅ | Stop price threshold |
| `price_bound` | Decimal | ➖ | Worst acceptable fill price after trigger |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `position_fill` | OrderPositionFill | ✅ | Position modification behavior |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `reason` | StopOrderReason | ✅ | Reason for creating the stop order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `take_profit_on_fill` | TakeProfitDetails | ➖ | Take profit order creation details |
| `stop_loss_on_fill` | StopLossDetails | ➖ | Stop loss order creation details |
| `trailing_stop_loss_on_fill` | TrailingStopLossDetails | ➖ | Trailing stop loss order creation details |
| `trade_client_extensions` | ClientExtensions | ➖ | Client extensions for created trades |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `cancelling_transaction_id` | TransactionID | ➖ | ID of transaction that cancelled this order |

## Specialized Order Transactions

### TakeProfitOrderTransaction
Transaction created when a Take Profit Order is submitted.

🔗 **OANDA Definition**: [TakeProfitOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | TradeID | ✅ | Trade to close with take profit order |
| `price` | Decimal | ✅ | Take profit trigger price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `reason` | TakeProfitOrderReason | ✅ | Reason for creating the take profit order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `order_fill_transaction_id` | TransactionID | ➖ | ID of transaction that filled this order |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `cancelling_transaction_id` | TransactionID | ➖ | ID of transaction that cancelled this order |

### StopLossOrderTransaction
Transaction created when a Stop Loss Order is submitted.

🔗 **OANDA Definition**: [StopLossOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#StopLossOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | TradeID | ✅ | Trade to close with stop loss order |
| `price` | Decimal | ➖ | Stop loss trigger price (either price or distance required) |
| `distance` | Decimal | ➖ | Distance from trade price (either price or distance required) |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `guaranteed` | bool | ✅ | Guaranteed execution flag |
| `reason` | StopLossOrderReason | ✅ | Reason for creating the stop loss order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `order_fill_transaction_id` | TransactionID | ➖ | ID of transaction that filled this order |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `cancelling_transaction_id` | TransactionID | ➖ | ID of transaction that cancelled this order |

### TrailingStopLossOrderTransaction
Transaction created when a Trailing Stop Loss Order is submitted.

🔗 **OANDA Definition**: [TrailingStopLossOrderTransaction](https://developer.oanda.com/rest-live-v20/transaction-df/#TrailingStopLossOrderTransaction)

**Inherits:** All Transaction fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `trade_id` | TradeID | ✅ | Trade to close with trailing stop loss order |
| `distance` | Decimal | ✅ | Trailing distance from trade price |
| `time_in_force` | TimeInForce | ✅ | Order duration policy |
| `gtd_time` | DateTime | ➖ | Good-till-date expiration timestamp |
| `trigger_condition` | OrderTriggerCondition | ✅ | Price component used for triggering |
| `reason` | TrailingStopLossOrderReason | ✅ | Reason for creating the trailing stop loss order |
| `client_extensions` | ClientExtensions | ➖ | Client extensions for the order |
| `order_fill_transaction_id` | TransactionID | ➖ | ID of transaction that filled this order |
| `replaces_order_id` | OrderID | ➖ | ID of the order being replaced |
| `cancelling_transaction_id` | TransactionID | ➖ | ID of transaction that cancelled this order |