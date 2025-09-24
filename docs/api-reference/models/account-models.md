# Account Models

📖 **OANDA Reference**: [Account Data Definitions](https://developer.oanda.com/rest-live-v20/account-df/)

Models for managing account information, balance tracking, margin calculations, and account state monitoring.

---

### Account
Complete account information including balance, margin, and trading statistics.

🔗 **OANDA Definition**: [Account](https://developer.oanda.com/rest-live-v20/account-df/#collapse_definition_2)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | AccountID | ✅ | Account's identifier using format "{siteID}-{divisionID}-{userID}-{accountNumber}" |
| `alias` | str | ➖ | Client-assigned alias for the account (optional) |
| `currency` | Currency | ✅ | Home currency of the account |
| `balance` | AccountUnits | ✅ | Current account balance in account currency |
| `created_by_user_id` | int | ✅ | User ID that created the account |
| `created_time` | DateTime | ✅ | Account creation timestamp |
| `guaranteed_stop_loss_order_parameters` | GuaranteedStopLossOrderParameters | ➖ | GSL order parameters (optional) |
| `guaranteed_stop_loss_order_mode` | GuaranteedStopLossOrderMode | ➖ | Overall behavior regarding guaranteed Stop Loss Orders (default: DISABLED) |
| `guaranteed_stop_loss_order_mutability` | GuaranteedStopLossOrderMutability | ➖ | GSL order mutability (deprecated but may still be present) |
| `resettable_pl_time` | DateTime | ➖ | Time when P&L was last reset |
| `margin_rate` | Decimal | ➖ | Account margin rate |
| `open_trade_count` | int | ✅ | Number of currently open trades |
| `open_position_count` | int | ✅ | Number of open positions |
| `pending_order_count` | int | ✅ | Number of pending orders |
| `hedging_enabled` | bool | ✅ | Whether hedging is enabled for the account |
| `unrealized_pl` | AccountUnits | ✅ | Total unrealized profit/loss from all open trades |
| `nav` | AccountUnits | ✅ | Net Asset Value (balance + unrealized P&L) |
| `margin_used` | AccountUnits | ✅ | Currently used margin in account currency |
| `margin_available` | AccountUnits | ✅ | Available margin for opening new positions |
| `position_value` | AccountUnits | ✅ | Total value of all open positions in home currency |
| `margin_closeout_unrealized_pl` | AccountUnits | ✅ | Margin closeout unrealized P&L |
| `margin_closeout_nav` | AccountUnits | ✅ | Margin closeout NAV |
| `margin_closeout_margin_used` | AccountUnits | ✅ | Margin closeout margin used |
| `margin_closeout_percent` | Decimal | ✅ | Margin closeout percentage (≥1.0 = closeout) |
| `margin_closeout_position_value` | Decimal | ✅ | Margin closeout position value |
| `withdrawal_limit` | AccountUnits | ✅ | Current withdrawal limit |
| `margin_call_margin_used` | AccountUnits | ✅ | Margin call margin used |
| `margin_call_percent` | Decimal | ✅ | Margin call percentage (≥1.0 = margin call) |
| `pl` | AccountUnits | ✅ | Total lifetime profit/loss |
| `resettable_pl` | AccountUnits | ✅ | Realized profit/loss since last reset |
| `financing` | AccountUnits | ✅ | Total lifetime financing |
| `commission` | AccountUnits | ✅ | Total lifetime commission |
| `dividend_adjustment` | AccountUnits | ✅ | Total dividend adjustments |
| `guaranteed_execution_fees` | AccountUnits | ✅ | Total guaranteed execution fees |
| `margin_call_enter_time` | DateTime | ➖ | Margin call entry time (conditional) |
| `margin_call_extension_count` | int | ➖ | Number of margin call extensions |
| `last_margin_call_extension_time` | DateTime | ➖ | Last margin call extension time |
| `last_transaction_id` | TransactionID | ✅ | Last transaction ID for the account |
| `trades` | list[TradeSummary] | ✅ | List of open trades |
| `positions` | list[Position] | ✅ | List of positions |
| `orders` | list[Order] | ✅ | List of orders |

### AccountSummary
Condensed account information for quick overview.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | AccountID | ✅ | Account's identifier |
| `alias` | str | ➖ | Client-assigned alias for the account (optional) |
| `currency` | Currency | ✅ | Home currency of the account |
| `created_by_user_id` | int | ✅ | User ID that created the account |
| `created_time` | DateTime | ✅ | Account creation timestamp |
| `guaranteed_stop_loss_order_parameters` | GuaranteedStopLossOrderParameters | ➖ | GSL order parameters (optional) |
| `guaranteed_stop_loss_order_mode` | GuaranteedStopLossOrderMode | ✅ | Overall behavior regarding guaranteed Stop Loss Orders |
| `resettable_pl_time` | DateTime | ➖ | Time when P&L was last reset |
| `margin_rate` | Decimal | ➖ | Account margin rate |
| `open_trade_count` | int | ✅ | Number of currently open trades |
| `open_position_count` | int | ✅ | Number of open positions |
| `pending_order_count` | int | ✅ | Number of pending orders |
| `hedging_enabled` | bool | ✅ | Whether hedging is enabled for the account |
| `unrealized_pl` | AccountUnits | ✅ | Total unrealized profit/loss from all open trades |
| `nav` | AccountUnits | ✅ | Net Asset Value (balance + unrealized P&L) |
| `margin_used` | AccountUnits | ✅ | Currently used margin in account currency |
| `margin_available` | AccountUnits | ✅ | Available margin for opening new positions |
| `position_value` | AccountUnits | ✅ | Total value of all open positions in home currency |
| `margin_closeout_unrealized_pl` | AccountUnits | ✅ | Margin closeout unrealized P&L |
| `margin_closeout_nav` | AccountUnits | ✅ | Margin closeout NAV |
| `margin_closeout_margin_used` | AccountUnits | ✅ | Margin closeout margin used |
| `margin_closeout_percent` | Decimal | ✅ | Margin closeout percentage (≥1.0 = closeout) |
| `margin_closeout_position_value` | Decimal | ✅ | Margin closeout position value |
| `withdrawal_limit` | AccountUnits | ✅ | Current withdrawal limit |
| `margin_call_margin_used` | AccountUnits | ✅ | Margin call margin used |
| `margin_call_percent` | Decimal | ✅ | Margin call percentage (≥1.0 = margin call) |
| `balance` | AccountUnits | ✅ | Current account balance in account currency |
| `pl` | AccountUnits | ✅ | Total lifetime profit/loss |
| `resettable_pl` | AccountUnits | ✅ | Realized profit/loss since last reset |
| `financing` | AccountUnits | ✅ | Total lifetime financing |
| `commission` | AccountUnits | ✅ | Total lifetime commission |
| `dividend_adjustment` | AccountUnits | ✅ | Total dividend adjustments |
| `guaranteed_execution_fees` | AccountUnits | ✅ | Total guaranteed execution fees |
| `margin_call_enter_time` | DateTime | ➖ | Margin call entry time (conditional) |
| `margin_call_extension_count` | int | ➖ | Number of margin call extensions |
| `last_margin_call_extension_time` | DateTime | ➖ | Last margin call extension time |
| `last_transaction_id` | TransactionID | ✅ | Last transaction ID for the account |

### AccountProperties
Basic account identification information.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | AccountID | ✅ | Account's identifier |
| `mt4_account_id` | int | ➖ | Associated MT4 Account ID (only present if account is an MT4 account) |
| `tags` | list[str] | ✅ | Account classification tags for categorization and filtering |

### AccountChanges
Used to represent changes to an Account's Orders, Trades and Positions since a specified Account TransactionID.

🔗 **OANDA Definition**: [AccountChanges](https://developer.oanda.com/rest-live-v20/account-df/#AccountChanges)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `orders_created` | list[Order] | ✅ | Orders created (may be filled/cancelled/triggered) |
| `orders_cancelled` | list[Order] | ✅ | Orders cancelled |
| `orders_filled` | list[Order] | ✅ | Orders filled |
| `orders_triggered` | list[Order] | ✅ | Orders triggered |
| `trades_opened` | list[TradeSummary] | ✅ | Trades opened |
| `trades_reduced` | list[TradeSummary] | ✅ | Trades reduced |
| `trades_closed` | list[TradeSummary] | ✅ | Trades closed |
| `positions` | list[Position] | ✅ | Positions changed |
| `transactions` | list[Transaction] | ✅ | Transactions generated |

### AccountChangesState
Represents an Account's current price-dependent state. Fields are omitted if their value hasn't changed since the specified transaction ID.

🔗 **OANDA Definition**: [AccountChangesState](https://developer.oanda.com/rest-live-v20/account-df/#AccountChangesState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unrealized_pl` | Decimal | ➖ | Total unrealized profit/loss from all open trades |
| `nav` | Decimal | ➖ | Net Asset Value (balance + unrealized P&L) |
| `margin_used` | Decimal | ➖ | Currently used margin in account currency |
| `margin_available` | Decimal | ➖ | Available margin for opening new positions |
| `position_value` | Decimal | ➖ | Total value of all open positions in home currency |
| `margin_closeout_unrealized_pl` | Decimal | ➖ | Margin closeout unrealized P&L |
| `margin_closeout_nav` | Decimal | ➖ | Margin closeout NAV |
| `margin_closeout_margin_used` | Decimal | ➖ | Margin closeout margin used |
| `margin_closeout_percent` | Decimal | ➖ | Margin closeout percentage (≥1.0 = closeout) |
| `margin_closeout_position_value` | Decimal | ➖ | Margin closeout position value |
| `withdrawal_limit` | Decimal | ➖ | Current withdrawal limit |
| `margin_call_margin_used` | Decimal | ➖ | Margin call margin used |
| `margin_call_percent` | Decimal | ➖ | Margin call percentage (≥1.0 = margin call) |
| `balance` | Decimal | ➖ | Current account balance in account currency |
| `pl` | Decimal | ➖ | Total lifetime profit/loss |
| `resettable_pl` | Decimal | ➖ | Realized profit/loss since last reset |
| `financing` | Decimal | ➖ | Total lifetime financing |
| `commission` | Decimal | ➖ | Total lifetime commission |
| `dividend_adjustment` | Decimal | ➖ | Total dividend adjustments |
| `guaranteed_execution_fees` | Decimal | ➖ | Total guaranteed execution fees |
| `margin_call_enter_time` | DateTime | ➖ | Margin call entry time (conditional) |
| `margin_call_extension_count` | int | ➖ | Number of margin call extensions |
| `last_margin_call_extension_time` | DateTime | ➖ | Last margin call extension time |
| `orders` | list[DynamicOrderState] | ✅ | Price-dependent order states |
| `trades` | list[CalculatedTradeState] | ✅ | Price-dependent trade states |
| `positions` | list[CalculatedPositionState] | ✅ | Price-dependent position states |

### CalculatedAccountState
The dynamically calculated state of a client's Account.

🔗 **OANDA Definition**: [CalculatedAccountState](https://developer.oanda.com/rest-live-v20/account-df/#CalculatedAccountState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unrealized_pl` | Decimal | ✅ | Total unrealized profit/loss from all open trades |
| `nav` | Decimal | ✅ | Net Asset Value (balance + unrealized P&L) |
| `margin_used` | Decimal | ✅ | Currently used margin in account currency |
| `margin_available` | Decimal | ✅ | Available margin for opening new positions |
| `position_value` | Decimal | ✅ | Total value of all open positions in home currency |
| `margin_closeout_unrealized_pl` | Decimal | ✅ | Margin closeout unrealized P&L |
| `margin_closeout_nav` | Decimal | ✅ | Margin closeout NAV |
| `margin_closeout_margin_used` | Decimal | ✅ | Margin closeout margin used |
| `margin_closeout_percent` | Decimal | ✅ | Margin closeout percentage (≥1.0 = closeout) |
| `margin_closeout_position_value` | Decimal | ✅ | Margin closeout position value |
| `withdrawal_limit` | Decimal | ✅ | Current withdrawal limit |
| `margin_call_margin_used` | Decimal | ✅ | Margin call margin used |
| `margin_call_percent` | Decimal | ✅ | Margin call percentage (≥1.0 = margin call) |

### AccumulatedAccountState
Interface for accumulated account state tracking.

🔗 **OANDA Definition**: [AccumulatedAccountState](https://developer.oanda.com/rest-live-v20/account-df/#AccumulatedAccountState)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `balance` | AccountUnits | ✅ | Current account balance in account currency |
| `pl` | AccountUnits | ✅ | Total lifetime profit/loss |
| `resettable_pl` | AccountUnits | ✅ | Realized profit/loss since last reset |
| `financing` | AccountUnits | ✅ | Total lifetime financing |
| `commission` | AccountUnits | ✅ | Total lifetime commission |
| `dividend_adjustment` | AccountUnits | ✅ | Total dividend adjustments |
| `guaranteed_execution_fees` | AccountUnits | ✅ | Total guaranteed execution fees |

### GuaranteedStopLossOrderParameters
The current mutability and hedging settings related to guaranteed Stop Loss orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderParameters](https://developer.oanda.com/rest-live-v20/account-df/#GuaranteedStopLossOrderParameters)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `mutability_market_open` | GuaranteedStopLossOrderMutability | ✅ | GSL mutability when market open |
| `mutability_market_halted` | GuaranteedStopLossOrderMutability | ✅ | GSL mutability when market halted |

### UserAttributes
Contains the attributes of a user associated with an account.

🔗 **OANDA Definition**: [UserAttributes](https://developer.oanda.com/rest-live-v20/account-df/#UserAttributes)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user_id` | int | ✅ | Unique user identifier |
| `username` | str | ✅ | User's login username |
| `title` | str | ✅ | User's title |
| `name` | str | ✅ | User's full name |
| `email` | str | ✅ | User's email address |
| `division_abbreviation` | str | ✅ | Division abbreviation |
| `language_abbreviation` | str | ✅ | Language preference abbreviation |
| `home_currency` | Currency | ✅ | User's home currency |

### GuaranteedStopLossOrderMutability
Describes the actions that can be performed on guaranteed Stop Loss Orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderMutability](https://developer.oanda.com/rest-live-v20/account-df/#GuaranteedStopLossOrderMutability)

| Value | Description |
|-------|-------------|
| `FIXED` | Once a guaranteed Stop Loss Order has been created it cannot be replaced or cancelled |
| `REPLACEABLE` | An existing guaranteed Stop Loss Order can only be replaced, not cancelled |
| `CANCELABLE` | Once a guaranteed Stop Loss Order has been created it can be either replaced or cancelled |
| `PRICE_WIDEN_ONLY` | An existing guaranteed Stop Loss Order can only be replaced to widen the gap from the current price, not cancelled |