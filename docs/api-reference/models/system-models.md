# System Models

📖 **OANDA Reference**: [Primitives Data Definitions](https://developer.oanda.com/rest-live-v20/primitives-df/)

Models for streaming configuration, error handling, and system enums used throughout the OANDA API.

---

## Streaming Models

### StreamingConfiguration
Configuration for streaming connections.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `include_heartbeats` | bool | ➖ | Include heartbeat messages (default: True) |
| `stall_timeout` | float | ➖ | Seconds before considering stream stalled (default: 30.0) |
| `reconnection_policy` | ReconnectionPolicy | ✅ | Reconnection settings (default: ReconnectionPolicy()) |

### ReconnectionPolicy
Policy for automatic reconnection.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `max_attempts` | int | ➖ | Maximum reconnection attempts (default: 3) |
| `delay_seconds` | float | ➖ | Delay between reconnection attempts in seconds (default: 1.0) |

---

## Error Models

### ErrorDetails
Structured error information from API responses.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error_code` | FiveTwentyErrorCode | ✅ | Standardized error code |
| `error_message` | str | ✅ | Human-readable error description |
| `details` | dict | ✅ | Additional error context |
| `violations` | list[ValidationViolation] | ✅ | Field validation errors |

### ValidationViolation
Specific field validation error.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `field` | str | ✅ | Field name with validation error |
| `message` | str | ✅ | Validation error message |
| `rejected_value` | any | ✅ | Value that failed validation |

---

## Enums and Type Aliases

### Core Trading Enums

#### Currency
ISO 4217 currency codes for account and trading operations.

🔗 **OANDA Definition**: [Currency](https://developer.oanda.com/rest-live-v20/primitives-df/#Currency)

| Value | Description |
|-------|-------------|
| `USD` | United States Dollar |
| `EUR` | Euro |
| `GBP` | British Pound Sterling |
| `JPY` | Japanese Yen |
| `AUD` | Australian Dollar |
| `CAD` | Canadian Dollar |
| `CHF` | Swiss Franc |
| `NZD` | New Zealand Dollar |
| `SEK` | Swedish Krona |
| `NOK` | Norwegian Krone |
| `DKK` | Danish Krone |
| `PLN` | Polish Zloty |
| `CZK` | Czech Koruna |
| `HUF` | Hungarian Forint |

#### InstrumentType
Classification of tradeable instruments.

🔗 **OANDA Definition**: [InstrumentType](https://developer.oanda.com/rest-live-v20/primitives-df/#InstrumentType)

| Value | Description |
|-------|-------------|
| `CURRENCY` | Currency pairs (forex) |
| `CFD` | Contracts for Difference |
| `METAL` | Precious metals |

#### OrderType
Types of orders that can be created.

🔗 **OANDA Definition**: [OrderType](https://developer.oanda.com/rest-live-v20/order-df/#OrderType)

| Value | Description |
|-------|-------------|
| `MARKET` | Market Order - immediate execution at current market price |
| `LIMIT` | Limit Order - execution when price reaches favorable threshold |
| `STOP` | Stop Order - execution when price reaches stop threshold |
| `MARKET_IF_TOUCHED` | Market-if-Touched Order - market execution when price touches threshold |
| `TAKE_PROFIT` | Take Profit Order - closes trade at profit target |
| `STOP_LOSS` | Stop Loss Order - closes trade to limit losses |
| `GUARANTEED_STOP_LOSS` | Guaranteed Stop Loss Order - guaranteed execution with slippage protection |
| `TRAILING_STOP_LOSS` | Trailing Stop Loss Order - dynamic stop loss that follows price |
| `FIXED_PRICE` | Fixed Price Order - immediate execution at specified price |

#### OrderState
Current state of an order in its lifecycle.

🔗 **OANDA Definition**: [OrderState](https://developer.oanda.com/rest-live-v20/order-df/#OrderState)

| Value | Description |
|-------|-------------|
| `PENDING` | Order is pending and can be filled |
| `FILLED` | Order has been filled |
| `TRIGGERED` | Order has been triggered |
| `CANCELLED` | Order has been cancelled |

#### TradeState
Current state of a trade in its lifecycle.

🔗 **OANDA Definition**: [TradeState](https://developer.oanda.com/rest-live-v20/trade-df/#TradeState)

| Value | Description |
|-------|-------------|
| `OPEN` | Trade is currently open |
| `CLOSED` | Trade has been fully closed |
| `CLOSE_WHEN_TRADEABLE` | Trade will be closed as soon as the instrument becomes tradeable |

#### TimeInForce
Order duration policies defining how long an order remains active.

🔗 **OANDA Definition**: [TimeInForce](https://developer.oanda.com/rest-live-v20/order-df/#TimeInForce)

| Value | Description |
|-------|-------------|
| `GTC` | Good 'Til Cancelled - order remains active until cancelled |
| `GTD` | Good 'Til Date - order remains active until specified date |
| `GFD` | Good For Day - order remains active until end of trading day |
| `FOK` | Fill Or Kill - order must be filled immediately and completely |
| `IOC` | Immediate Or Cancel - order must be filled immediately (partial fills accepted) |

#### OrderPositionFill
Defines how positions are modified when an order is filled.

🔗 **OANDA Definition**: [OrderPositionFill](https://developer.oanda.com/rest-live-v20/order-df/#OrderPositionFill)

| Value | Description |
|-------|-------------|
| `OPEN_ONLY` | Order can only open new positions |
| `REDUCE_FIRST` | Order reduces position first, then opens new position with remainder |
| `REDUCE_ONLY` | Order can only reduce existing positions |
| `DEFAULT` | Use default position fill behavior |

#### OrderTriggerCondition
Specifies which price component to use for order triggering.

🔗 **OANDA Definition**: [OrderTriggerCondition](https://developer.oanda.com/rest-live-v20/order-df/#OrderTriggerCondition)

| Value | Description |
|-------|-------------|
| `DEFAULT` | Use default trigger condition (ask for buy, bid for sell) |
| `INVERSE` | Use inverse trigger condition (ask for sell, bid for buy) |
| `BID` | Use bid price as trigger condition |
| `ASK` | Use ask price as trigger condition |
| `MID` | Use mid price as trigger condition |

### Market Data Enums

#### CandlestickGranularity
Time intervals for candlestick data.

🔗 **OANDA Definition**: [CandlestickGranularity](https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickGranularity)

**Second-based Intervals:**
`S5`, `S10`, `S15`, `S30`

**Minute-based Intervals:**
`M1`, `M2`, `M4`, `M5`, `M10`, `M15`, `M30`

**Hour-based Intervals:**
`H1`, `H2`, `H3`, `H4`, `H6`, `H8`, `H12`

**Higher Timeframes:**
`D` (daily), `W` (weekly), `M` (monthly)

#### DayOfWeek
Standard day-of-week enumeration for scheduling and alignment.

🔗 **OANDA Definition**: [DayOfWeek](https://developer.oanda.com/rest-live-v20/primitives-df/#DayOfWeek)

| Value | Description |
|-------|-------------|
| `SUNDAY` | Sunday |
| `MONDAY` | Monday |
| `TUESDAY` | Tuesday |
| `WEDNESDAY` | Wednesday |
| `THURSDAY` | Thursday |
| `FRIDAY` | Friday |
| `SATURDAY` | Saturday |

### Account Management Enums

#### AccountFinancingMode
The financing mode of an Account.

🔗 **OANDA Definition**: [AccountFinancingMode](https://developer.oanda.com/rest-live-v20/account-df/#AccountFinancingMode)

| Value | Description |
|-------|-------------|
| `NO_FINANCING` | No financing is paid/charged for open trades |
| `SECOND_BY_SECOND` | Second-by-second financing for open trades |
| `DAILY` | Daily financing at 5 p.m. New York time |

#### GuaranteedStopLossOrderMode
Account behavior regarding guaranteed Stop Loss orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderMode](https://developer.oanda.com/rest-live-v20/account-df/#GuaranteedStopLossOrderMode)

| Value | Description |
|-------|-------------|
| `DISABLED` | Account is not permitted to create guaranteed Stop Loss orders |
| `ALLOWED` | Account can create guaranteed Stop Loss orders but it's not required |
| `REQUIRED` | Account is required to have guaranteed Stop Loss orders for all open trades |

### Transaction Type Enum

#### TransactionType
Complete enumeration of all transaction types in the OANDA system.

🔗 **OANDA Definition**: [TransactionType](https://developer.oanda.com/rest-live-v20/transaction-df/#TransactionType)

**Account Management:**
`CREATE`, `CLOSE`, `REOPEN`, `CLIENT_CONFIGURE`, `CLIENT_CONFIGURE_REJECT`

**Fund Management:**
`TRANSFER_FUNDS`, `TRANSFER_FUNDS_REJECT`

**Order Creation:**
`MARKET_ORDER`, `MARKET_ORDER_REJECT`, `FIXED_PRICE_ORDER`, `LIMIT_ORDER`, `LIMIT_ORDER_REJECT`, `STOP_ORDER`, `STOP_ORDER_REJECT`, `MARKET_IF_TOUCHED_ORDER`, `MARKET_IF_TOUCHED_ORDER_REJECT`

**Specialized Orders:**
`TAKE_PROFIT_ORDER`, `TAKE_PROFIT_ORDER_REJECT`, `STOP_LOSS_ORDER`, `STOP_LOSS_ORDER_REJECT`, `GUARANTEED_STOP_LOSS_ORDER`, `GUARANTEED_STOP_LOSS_ORDER_REJECT`, `TRAILING_STOP_LOSS_ORDER`, `TRAILING_STOP_LOSS_ORDER_REJECT`

**Order Management:**
`ORDER_FILL`, `ORDER_CANCEL`, `ORDER_CANCEL_REJECT`, `ORDER_CLIENT_EXTENSIONS_MODIFY`, `ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT`

**Trade Management:**
`TRADE_CLIENT_EXTENSIONS_MODIFY`, `TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT`

**Risk Management:**
`MARGIN_CALL_ENTER`, `MARGIN_CALL_EXTEND`, `MARGIN_CALL_EXIT`, `DELAYED_TRADE_CLOSURE`

**Financial Operations:**
`DAILY_FINANCING`, `DIVIDEND_ADJUSTMENT`, `RESET_RESETTABLE_PL`

### Type Aliases
- `AccountID` - str: Account identifier using format "{siteID}-{divisionID}-{userID}-{accountNumber}"
- `TradeID` - str: Trade identifier (OANDA-assigned positive integer as string)
- `OrderID` - str: Order identifier (unique within account)
- `TransactionID` - str: Transaction identifier (positive integer assigned sequentially by OANDA)
- `PriceValue` - str: Price value encoded as string for precision
- `AccountUnits` - str: Account currency amounts encoded as strings
- `DateTime` - str: RFC3339 format ("YYYY-MM-DDTHH:MM:SS.nnnnnnnnnZ") or UNIX timestamp with nanosecond precision