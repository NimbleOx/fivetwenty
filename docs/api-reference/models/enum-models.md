# Enum Models

This page documents all enumeration types used throughout FiveTwenty. These enums provide type-safe constants for OANDA API parameters and values.

## Core Trading Enums

### InstrumentName

Available trading instruments supported by OANDA.

🔗 **OANDA Definition**: [InstrumentName](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_5)

🔗 **Source**: [InstrumentName](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `AUD_CAD` | Australian Dollar / Canadian Dollar |
| `AUD_CHF` | Australian Dollar / Swiss Franc |
| `AUD_HKD` | Australian Dollar / Hong Kong Dollar |
| `AUD_JPY` | Australian Dollar / Japanese Yen |
| `AUD_NZD` | Australian Dollar / New Zealand Dollar |
| `AUD_SGD` | Australian Dollar / Singapore Dollar |
| `AUD_USD` | Australian Dollar / US Dollar |
| `CAD_CHF` | Canadian Dollar / Swiss Franc |
| `CAD_HKD` | Canadian Dollar / Hong Kong Dollar |
| `CAD_JPY` | Canadian Dollar / Japanese Yen |
| `CAD_SGD` | Canadian Dollar / Singapore Dollar |
| `CHF_HKD` | Swiss Franc / Hong Kong Dollar |
| `CHF_JPY` | Swiss Franc / Japanese Yen |
| `CHF_ZAR` | Swiss Franc / South African Rand |
| `EUR_AUD` | Euro / Australian Dollar |
| `EUR_CAD` | Euro / Canadian Dollar |
| `EUR_CHF` | Euro / Swiss Franc |
| `EUR_CZK` | Euro / Czech Koruna |
| `EUR_DKK` | Euro / Danish Krone |
| `EUR_GBP` | Euro / British Pound |
| `EUR_HKD` | Euro / Hong Kong Dollar |
| `EUR_HUF` | Euro / Hungarian Forint |
| `EUR_JPY` | Euro / Japanese Yen |
| `EUR_NOK` | Euro / Norwegian Krone |
| `EUR_NZD` | Euro / New Zealand Dollar |
| `EUR_PLN` | Euro / Polish Zloty |
| `EUR_SEK` | Euro / Swedish Krona |
| `EUR_SGD` | Euro / Singapore Dollar |
| `EUR_TRY` | Euro / Turkish Lira |
| `EUR_USD` | Euro / US Dollar |
| `EUR_ZAR` | Euro / South African Rand |
| `GBP_AUD` | British Pound / Australian Dollar |
| `GBP_CAD` | British Pound / Canadian Dollar |
| `GBP_CHF` | British Pound / Swiss Franc |
| `GBP_HKD` | British Pound / Hong Kong Dollar |
| `GBP_JPY` | British Pound / Japanese Yen |
| `GBP_NZD` | British Pound / New Zealand Dollar |
| `GBP_PLN` | British Pound / Polish Zloty |
| `GBP_SGD` | British Pound / Singapore Dollar |
| `GBP_USD` | British Pound / US Dollar |
| `GBP_ZAR` | British Pound / South African Rand |
| `HKD_JPY` | Hong Kong Dollar / Japanese Yen |
| `NZD_CAD` | New Zealand Dollar / Canadian Dollar |
| `NZD_CHF` | New Zealand Dollar / Swiss Franc |
| `NZD_HKD` | New Zealand Dollar / Hong Kong Dollar |
| `NZD_JPY` | New Zealand Dollar / Japanese Yen |
| `NZD_SGD` | New Zealand Dollar / Singapore Dollar |
| `NZD_USD` | New Zealand Dollar / US Dollar |
| `SGD_CHF` | Singapore Dollar / Swiss Franc |
| `SGD_JPY` | Singapore Dollar / Japanese Yen |
| `TRY_JPY` | Turkish Lira / Japanese Yen |
| `USD_CAD` | US Dollar / Canadian Dollar |
| `USD_CHF` | US Dollar / Swiss Franc |
| `USD_CNH` | US Dollar / Chinese Yuan (Offshore) |
| `USD_CZK` | US Dollar / Czech Koruna |
| `USD_DKK` | US Dollar / Danish Krone |
| `USD_HKD` | US Dollar / Hong Kong Dollar |
| `USD_HUF` | US Dollar / Hungarian Forint |
| `USD_JPY` | US Dollar / Japanese Yen |
| `USD_MXN` | US Dollar / Mexican Peso |
| `USD_NOK` | US Dollar / Norwegian Krone |
| `USD_PLN` | US Dollar / Polish Zloty |
| `USD_SEK` | US Dollar / Swedish Krona |
| `USD_SGD` | US Dollar / Singapore Dollar |
| `USD_THB` | US Dollar / Thai Baht |
| `USD_TRY` | US Dollar / Turkish Lira |
| `USD_ZAR` | US Dollar / South African Rand |
| `ZAR_JPY` | South African Rand / Japanese Yen |

### Direction

Trade direction for buy/sell operations.

🔗 **OANDA Definition**: [Direction](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_16)

🔗 **Source**: [Direction](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `LONG` | Buy direction - go long on the instrument |
| `SHORT` | Sell direction - go short on the instrument |

### Currency

ISO 4217 currency codes for account and trading operations.

🔗 **OANDA Definition**: [Currency](https://developer.oanda.com/rest-live-v20/primitives-df/#Currency)

🔗 **Source**: [Currency](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `AUD` | Australian Dollar |
| `CAD` | Canadian Dollar |
| `CHF` | Swiss Franc |
| `CNH` | Chinese Yuan (Offshore) |
| `CZK` | Czech Koruna |
| `DKK` | Danish Krone |
| `EUR` | Euro |
| `GBP` | British Pound Sterling |
| `HKD` | Hong Kong Dollar |
| `HUF` | Hungarian Forint |
| `JPY` | Japanese Yen |
| `MXN` | Mexican Peso |
| `NOK` | Norwegian Krone |
| `NZD` | New Zealand Dollar |
| `PLN` | Polish Zloty |
| `SEK` | Swedish Krona |
| `SGD` | Singapore Dollar |
| `THB` | Thai Baht |
| `TRY` | Turkish Lira |
| `USD` | United States Dollar |
| `ZAR` | South African Rand |

### InstrumentType

Classification of tradeable instruments.

🔗 **OANDA Definition**: [InstrumentType](https://developer.oanda.com/rest-live-v20/primitives-df/#InstrumentType)

🔗 **Source**: [InstrumentType](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CURRENCY` | Currency pairs (forex) |
| `CFD` | Contracts for Difference |
| `METAL` | Precious metals |

### TransactionType

Types of transactions that can occur in an account.

🔗 **OANDA Definition**: [TransactionType](https://developer.oanda.com/rest-live-v20/transaction-df/#collapse_definition_41)

🔗 **Source**: [TransactionType](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CREATE` | Account created |
| `CLOSE` | Account closed |
| `REOPEN` | Account reopened |
| `CLIENT_CONFIGURE` | Client configuration changed |
| `CLIENT_CONFIGURE_REJECT` | Client configuration rejected |
| `TRANSFER_FUNDS` | Funds transferred |
| `TRANSFER_FUNDS_REJECT` | Fund transfer rejected |
| `MARKET_ORDER` | Market order placed |
| `MARKET_ORDER_REJECT` | Market order rejected |
| `FIXED_PRICE_ORDER` | Fixed price order placed |
| `LIMIT_ORDER` | Limit order placed |
| `LIMIT_ORDER_REJECT` | Limit order rejected |
| `STOP_ORDER` | Stop order placed |
| `STOP_ORDER_REJECT` | Stop order rejected |
| `MARKET_IF_TOUCHED_ORDER` | MIT order placed |
| `MARKET_IF_TOUCHED_ORDER_REJECT` | MIT order rejected |
| `TAKE_PROFIT_ORDER` | Take profit order placed |
| `TAKE_PROFIT_ORDER_REJECT` | Take profit order rejected |
| `STOP_LOSS_ORDER` | Stop loss order placed |
| `STOP_LOSS_ORDER_REJECT` | Stop loss order rejected |
| `GUARANTEED_STOP_LOSS_ORDER` | Guaranteed stop loss order placed |
| `GUARANTEED_STOP_LOSS_ORDER_REJECT` | Guaranteed stop loss order rejected |
| `TRAILING_STOP_LOSS_ORDER` | Trailing stop loss order placed |
| `TRAILING_STOP_LOSS_ORDER_REJECT` | Trailing stop loss order rejected |
| `ORDER_FILL` | Order filled |
| `ORDER_CANCEL` | Order canceled |
| `ORDER_CANCEL_REJECT` | Order cancellation rejected |
| `ORDER_CLIENT_EXTENSIONS_MODIFY` | Order client extensions modified |
| `ORDER_CLIENT_EXTENSIONS_MODIFY_REJECT` | Order client extensions modification rejected |
| `TRADE_CLIENT_EXTENSIONS_MODIFY` | Trade client extensions modified |
| `TRADE_CLIENT_EXTENSIONS_MODIFY_REJECT` | Trade client extensions modification rejected |
| `MARGIN_CALL_ENTER` | Margin call entered |
| `MARGIN_CALL_EXTEND` | Margin call extended |
| `MARGIN_CALL_EXIT` | Margin call exited |
| `DELAYED_TRADE_CLOSURE` | Delayed trade closure |
| `DAILY_FINANCING` | Daily financing applied |
| `DIVIDEND_ADJUSTMENT` | Dividend adjustment applied |
| `RESET_RESETTABLE_PL` | Resettable PL reset |

## Price and Market Data Enums

### CandlestickGranularity

Time intervals for candlestick data.

🔗 **OANDA Definition**: [CandlestickGranularity](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_1)

🔗 **Source**: [CandlestickGranularity](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description | Alignment |
|-------|-------------|-----------|
| `S5` | 5 seconds | Minute aligned |
| `S10` | 10 seconds | Minute aligned |
| `S15` | 15 seconds | Minute aligned |
| `S30` | 30 seconds | Minute aligned |
| `M1` | 1 minute | Hour aligned |
| `M2` | 2 minutes | Hour aligned |
| `M4` | 4 minutes | Hour aligned |
| `M5` | 5 minutes | Hour aligned |
| `M10` | 10 minutes | Hour aligned |
| `M15` | 15 minutes | Hour aligned |
| `M30` | 30 minutes | Hour aligned |
| `H1` | 1 hour | Day aligned |
| `H2` | 2 hours | Day aligned |
| `H3` | 3 hours | Day aligned |
| `H4` | 4 hours | Day aligned |
| `H6` | 6 hours | Day aligned |
| `H8` | 8 hours | Day aligned |
| `H12` | 12 hours | Day aligned |
| `D` | 1 day | Week aligned |
| `W` | 1 week | Month aligned |
| `M` | 1 month | Year aligned |

### PriceStatus

Status of price data.

🔗 **OANDA Definition**: [PriceStatus](https://developer.oanda.com/rest-live-v20/pricing-df/#collapse_definition_2)

🔗 **Source**: [PriceStatus](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `tradeable` | Price is tradeable |
| `non-tradeable` | Price is not tradeable |
| `invalid` | Price is invalid |

### WeeklyAlignment

Days of the week for weekly candlestick alignment.

🔗 **OANDA Definition**: [WeeklyAlignment](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_2)

🔗 **Source**: [WeeklyAlignment](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `Monday` | Week starts on Monday |
| `Tuesday` | Week starts on Tuesday |
| `Wednesday` | Week starts on Wednesday |
| `Thursday` | Week starts on Thursday |
| `Friday` | Week starts on Friday |
| `Saturday` | Week starts on Saturday |
| `Sunday` | Week starts on Sunday |

### DayOfWeek

Days of the week enumeration.

🔗 **OANDA Definition**: [DayOfWeek](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_7)

🔗 **Source**: [DayOfWeek](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `MONDAY` | Monday |
| `TUESDAY` | Tuesday |
| `WEDNESDAY` | Wednesday |
| `THURSDAY` | Thursday |
| `FRIDAY` | Friday |
| `SATURDAY` | Saturday |
| `SUNDAY` | Sunday |

## Order Management Enums

### OrderType

Types of orders that can be placed.

🔗 **OANDA Definition**: [OrderType](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_21)

🔗 **Source**: [OrderType](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `MARKET` | Market order - execute immediately at current market price |
| `LIMIT` | Limit order - execute when price reaches specified level |
| `STOP` | Stop order - execute when price crosses specified level |
| `MARKET_IF_TOUCHED` | MIT order - execute as market order when price reaches level |
| `TAKE_PROFIT` | Take profit order - close position at profit target |
| `STOP_LOSS` | Stop loss order - close position to limit loss |
| `TRAILING_STOP_LOSS` | Trailing stop loss - dynamic stop loss that follows price |
| `GUARANTEED_STOP_LOSS` | Guaranteed stop loss - stop loss with guaranteed execution |

### OrderState

Current state of an order.

🔗 **OANDA Definition**: [OrderState](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_23)

🔗 **Source**: [OrderState](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `PENDING` | Order is pending and can be filled |
| `FILLED` | Order has been filled |
| `TRIGGERED` | Order has been triggered |
| `CANCELLED` | Order has been cancelled |

### TimeInForce

Order duration policies defining how long an order remains active.

🔗 **OANDA Definition**: [TimeInForce](https://developer.oanda.com/rest-live-v20/order-df/#TimeInForce)

🔗 **Source**: [TimeInForce](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `GTC` | Good 'Til Cancelled - order remains active until cancelled |
| `GTD` | Good 'Til Date - order remains active until specified date |
| `GFD` | Good For Day - order remains active until end of trading day |
| `FOK` | Fill Or Kill - order must be filled immediately and completely |
| `IOC` | Immediate Or Cancel - order must be filled immediately (partial fills accepted) |

### OrderPositionFill

Defines how positions are modified when an order is filled.

🔗 **OANDA Definition**: [OrderPositionFill](https://developer.oanda.com/rest-live-v20/order-df/#OrderPositionFill)

🔗 **Source**: [OrderPositionFill](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `OPEN_ONLY` | Order can only open new positions |
| `REDUCE_FIRST` | Order reduces position first, then opens new position with remainder |
| `REDUCE_ONLY` | Order can only reduce existing positions |
| `DEFAULT` | Use default position fill behavior |

### OrderTriggerCondition

Specifies which price component to use for order triggering.

🔗 **OANDA Definition**: [OrderTriggerCondition](https://developer.oanda.com/rest-live-v20/order-df/#OrderTriggerCondition)

🔗 **Source**: [OrderTriggerCondition](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `DEFAULT` | Use default trigger condition (ask for buy, bid for sell) |
| `INVERSE` | Use inverse trigger condition (ask for sell, bid for buy) |
| `BID` | Use bid price as trigger condition |
| `ASK` | Use ask price as trigger condition |
| `MID` | Use mid price as trigger condition |

### OrderStateFilter

Filter for querying orders by state.

🔗 **OANDA Definition**: [OrderStateFilter](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_24)

🔗 **Source**: [OrderStateFilter](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `PENDING` | Include pending orders |
| `FILLED` | Include filled orders |
| `TRIGGERED` | Include triggered orders |
| `CANCELLED` | Include cancelled orders |
| `ALL` | Include orders in all states |

### CancellableOrderType

Types of orders that can be cancelled.

🔗 **OANDA Definition**: [CancellableOrderType](https://developer.oanda.com/rest-live-v20/order-df/#collapse_definition_22)

🔗 **Source**: [CancellableOrderType](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `LIMIT` | Limit orders can be cancelled |
| `STOP` | Stop orders can be cancelled |
| `MARKET_IF_TOUCHED` | MIT orders can be cancelled |
| `TAKE_PROFIT` | Take profit orders can be cancelled |
| `STOP_LOSS` | Stop loss orders can be cancelled |
| `TRAILING_STOP_LOSS` | Trailing stop loss orders can be cancelled |
| `GUARANTEED_STOP_LOSS` | Guaranteed stop loss orders can be cancelled |

## Account and Position Enums

### AccountFinancingMode

Financing mode for an account.

🔗 **OANDA Definition**: [AccountFinancingMode](https://developer.oanda.com/rest-live-v20/account-df/#collapse_definition_12)

🔗 **Source**: [AccountFinancingMode](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `NO_FINANCING` | No financing charges applied |
| `SECOND_BY_SECOND` | Financing applied second by second |
| `DAILY` | Financing applied daily |

### PositionAggregationMode

How positions are aggregated in the account.

🔗 **OANDA Definition**: [PositionAggregationMode](https://developer.oanda.com/rest-live-v20/account-df/#collapse_definition_14)

🔗 **Source**: [PositionAggregationMode](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `ABSOLUTE_SUM` | Sum absolute values of all positions |
| `MAXIMAL_SIDE` | Use the maximal side of net position |
| `NET_SUM` | Net sum of all positions |

### GuaranteedStopLossOrderMode

Guaranteed stop loss order modes for instruments.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderMode](https://developer.oanda.com/rest-live-v20/account-df/#collapse_definition_6)

🔗 **Source**: [GuaranteedStopLossOrderMode](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `DISABLED` | Guaranteed stop loss orders are disabled |
| `ALLOWED` | Guaranteed stop loss orders are allowed |
| `REQUIRED` | Guaranteed stop loss orders are required |

### GuaranteedStopLossOrderModeForInstrument

Guaranteed stop loss order modes specific to instruments.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderModeForInstrument](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_14)

🔗 **Source**: [GuaranteedStopLossOrderModeForInstrument](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `DISABLED` | GSL orders disabled for this instrument |
| `ALLOWED` | GSL orders allowed for this instrument |
| `REQUIRED` | GSL orders required for this instrument |

## Filtering and Querying Enums

### TradeState

Current state of a trade in its lifecycle.

🔗 **OANDA Definition**: [TradeState](https://developer.oanda.com/rest-live-v20/trade-df/#TradeState)

🔗 **Source**: [TradeState](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `OPEN` | Trade is currently open |
| `CLOSED` | Trade has been fully closed |
| `CLOSE_WHEN_TRADEABLE` | Trade will be closed as soon as the instrument becomes tradeable |

### TradeStateFilter

Filter for trade queries by state.

🔗 **OANDA Definition**: [TradeStateFilter](https://developer.oanda.com/rest-live-v20/trade-df/#collapse_definition_3)

🔗 **Source**: [TradeStateFilter](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `OPEN` | Open trades only |
| `CLOSED` | Closed trades only |
| `CLOSE_WHEN_TRADEABLE` | Trades set to close when tradeable |
| `ALL` | All trades regardless of state |

All enums are string-based and can be used directly with OANDA API endpoints or for type validation in your trading applications.
