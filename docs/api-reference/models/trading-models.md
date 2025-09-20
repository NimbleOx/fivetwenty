# Trading Models

📖 **OANDA Reference**: [Trade Data Definitions](https://developer.oanda.com/rest-live-v20/trade-df/) | [Position Data Definitions](https://developer.oanda.com/rest-live-v20/position-df/)

Models for trade lifecycle management, position tracking, and P&L calculations.

---

## Trade Models

### Trade
Represents an open trade position.

🔗 **OANDA Definition**: [Trade](https://developer.oanda.com/rest-live-v20/trade-df/#collapse_definition_5)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | TradeID | ✅ | Trade's identifier, unique within the Account (OANDA-assigned positive integer as string) |
| `instrument` | InstrumentName | ✅ | Trade's Instrument (e.g., "EUR_USD") |
| `price` | PriceValue | ✅ | Execution price of the Trade (string for precision) |
| `open_time` | DateTime | ✅ | Date/time when Trade was opened |
| `state` | TradeState | ✅ | Current state of the Trade (OPEN, CLOSED, CLOSE_WHEN_TRADEABLE) |
| `initial_units` | Decimal | ✅ | Initial size of the Trade (positive for long, negative for short) |
| `initial_margin_required` | AccountUnits | ✅ | Margin required when trade was opened |
| `current_units` | Decimal | ✅ | Units currently open (reduces toward 0 when closed) |
| `realized_pl` | AccountUnits | ✅ | Total profit/loss realized on closed portion of Trade (string) |
| `unrealized_pl` | AccountUnits | ✅ | Unrealized profit/loss on open portion using current market prices (string) |
| `margin_used` | AccountUnits | ✅ | Margin currently used by the Trade (string) |
| `average_close_price` | PriceValue | ➖ | Average price of closed portions |
| `closing_transaction_ids` | list[TransactionID] | ✅ | IDs of transactions that closed portions of this trade |
| `dividend_adjustment` | AccountUnits | ➖ | Total dividend adjustments paid for the Trade (string, applicable to equity CFDs) |
| `financing` | AccountUnits | ➖ | Total financing paid/collected for the Trade (string, overnight swap charges/credits) |
| `close_time` | DateTime | ➖ | Date/time when Trade was fully closed (only present for CLOSED trades) |
| `client_extensions` | ClientExtensions | ➖ | Client extensions of the Trade |
| `take_profit_order` | TakeProfitOrder | ➖ | Full Take Profit Order representation (if exists) |
| `stop_loss_order` | StopLossOrder | ➖ | Full Stop Loss Order representation (if exists) |
| `guaranteed_stop_loss_order` | GuaranteedStopLossOrder | ➖ | Full Guaranteed Stop Loss Order representation (if exists) |
| `trailing_stop_loss_order` | TrailingStopLossOrder | ➖ | Full Trailing Stop Loss Order representation (if exists) |

### TradeSummary
Condensed trade information for lists and overviews.

🔗 **OANDA Definition**: [TradeSummary](https://developer.oanda.com/rest-live-v20/trade-df/#collapse_definition_6)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | TradeID | ✅ | Trade's identifier, unique within the Account |
| `instrument` | InstrumentName | ✅ | Trade's Instrument |
| `price` | PriceValue | ✅ | Execution price of the Trade (string for precision) |
| `open_time` | DateTime | ✅ | Date/time when Trade was opened |
| `state` | TradeState | ✅ | Current state of the Trade (OPEN, CLOSED, CLOSE_WHEN_TRADEABLE) |
| `initial_units` | Decimal | ✅ | Initial size of the Trade (positive for long, negative for short) |
| `initial_margin_required` | AccountUnits | ✅ | Margin required when trade was opened |
| `current_units` | Decimal | ✅ | Units currently open (reduces toward 0 when closed) |
| `realized_pl` | AccountUnits | ✅ | Total profit/loss realized on closed portion of Trade (string) |
| `unrealized_pl` | AccountUnits | ✅ | Unrealized profit/loss on open portion using current market prices |
| `margin_used` | AccountUnits | ✅ | Margin currently used by the Trade |
| `average_close_price` | PriceValue | ➖ | Average price of closed portions |
| `closing_transaction_ids` | list[TransactionID] | ✅ | IDs of transactions that closed portions of this trade |
| `financing` | AccountUnits | ➖ | Total financing paid/collected for the Trade |
| `dividend_adjustment` | AccountUnits | ➖ | Total dividend adjustments paid for the Trade |
| `close_time` | DateTime | ➖ | Date/time when Trade was fully closed |
| `client_extensions` | ClientExtensions | ➖ | Client extensions of the Trade |
| `take_profit_order_id` | OrderID | ➖ | Take Profit Order ID (if exists) |
| `stop_loss_order_id` | OrderID | ➖ | Stop Loss Order ID (if exists) |
| `guaranteed_stop_loss_order_id` | OrderID | ➖ | Guaranteed Stop Loss Order ID (if exists) |
| `trailing_stop_loss_order_id` | OrderID | ➖ | Trailing Stop Loss Order ID (if exists) |

### TradeSpecifier
The identification of a Trade as referred to by clients.

🔗 **OANDA Definition**: [TradeSpecifier](https://developer.oanda.com/rest-live-v20/trade-df/#TradeSpecifier)

| Type | Format | Description |
|------|--------|-------------|
| str | Trade ID or Client ID | Either the Trade's OANDA-assigned TradeID or the Trade's client-provided ClientID prefixed by the "@" symbol |

**Examples:**

- `"1523"` - OANDA-assigned Trade ID
- `"@my_trade_id"` - Client-provided ID with @ prefix

### TradeStateFilter
The state to filter the Trades by.

🔗 **OANDA Definition**: [TradeStateFilter](https://developer.oanda.com/rest-live-v20/trade-df/#TradeStateFilter)

| Value | Description |
|-------|-------------|
| `OPEN` | The Trades that are currently open |
| `CLOSED` | The Trades that have been fully closed |
| `CLOSE_WHEN_TRADEABLE` | The Trades that will be closed as soon as the trades' instrument becomes tradeable |
| `ALL` | The Trades that are in any of the possible states listed above |

### CalculatedTradeState
The dynamic (calculated) state of an open Trade.

🔗 **OANDA Definition**: [CalculatedTradeState](https://developer.oanda.com/rest-live-v20/trade-df/#CalculatedTradeState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | TradeID | ✅ | Trade's identifier |
| `unrealized_pl` | Decimal | ✅ | Trade's unrealized profit/loss |
| `margin_used` | Decimal | ✅ | Margin currently used by the Trade |

---

## Position Models

### Position
Aggregated position information for an instrument.

🔗 **OANDA Definition**: [Position](https://developer.oanda.com/rest-live-v20/position-df/#collapse_definition_1)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Position's Instrument |
| `long` | PositionSide | ✅ | Long side details (aggregation of all long trades) |
| `short` | PositionSide | ✅ | Short side details (aggregation of all short trades) |
| `pl` | Decimal | ✅ | Lifetime realized profit/loss for the Position |
| `unrealized_pl` | Decimal | ✅ | Unrealized profit/loss from all open Trades |
| `margin_used` | Decimal | ➖ | Margin currently used by the Position |
| `resettable_pl` | Decimal | ✅ | Realized profit/loss since last reset |
| `financing` | Decimal | ➖ | Total financing paid/collected for the Position (lifetime) |
| `commission` | Decimal | ➖ | Total commission paid for the Position (lifetime) |
| `dividend_adjustment` | Decimal | ➖ | Total dividend adjustments for the Position (lifetime) |
| `guaranteed_execution_fees` | Decimal | ➖ | Total guaranteed stop loss fees for the Position (lifetime) |

### PositionSide
One side (long or short) of a position.

🔗 **OANDA Definition**: [PositionSide](https://developer.oanda.com/rest-live-v20/position-df/#collapse_definition_2)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `units` | Decimal | ✅ | Position units (positive for long, negative for short) |
| `average_price` | PriceValue | ➖ | Volume-weighted average open price for this side |
| `trade_ids` | list[TradeID] | ✅ | Open Trade IDs contributing to this position side |
| `pl` | Decimal | ✅ | Lifetime realized profit/loss for this side |
| `unrealized_pl` | Decimal | ✅ | Unrealized profit/loss from open Trades on this side |
| `resettable_pl` | Decimal | ✅ | Realized profit/loss since last reset for this side |
| `financing` | Decimal | ➖ | Total financing for this side (lifetime) |
| `dividend_adjustment` | Decimal | ➖ | Total dividend adjustments for this side |
| `guaranteed_execution_fees` | Decimal | ➖ | Total guaranteed stop loss fees for this side (lifetime) |

### CalculatedPositionState
Dynamic calculated state of a position with real-time P&L calculations.

🔗 **OANDA Definition**: [CalculatedPositionState](https://developer.oanda.com/rest-live-v20/position-df/#CalculatedPositionState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | InstrumentName | ✅ | Position's instrument identifier |
| `net_unrealized_pl` | AccountUnits | ✅ | Net unrealized profit/loss for the entire position |
| `long_unrealized_pl` | AccountUnits | ✅ | Unrealized profit/loss for the long position side |
| `short_unrealized_pl` | AccountUnits | ✅ | Unrealized profit/loss for the short position side |
| `margin_used` | AccountUnits | ➖ | Current margin used by the position |