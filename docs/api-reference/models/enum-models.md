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

### AcceptDatetimeFormat

Format for DateTime fields in OANDA requests and responses.

🔗 **OANDA Definition**: [AcceptDatetimeFormat](https://developer.oanda.com/rest-live-v20/primitives-df/#AcceptDatetimeFormat)

🔗 **Source**: [AcceptDatetimeFormat](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `UNIX` | DateTime fields are formatted as Unix timestamps |
| `RFC3339` | DateTime fields are formatted according to RFC 3339 |

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

### DailyAlignment

Hour of day (in the candlestick request's timezone) used for daily candlestick alignment. Integer-valued enum covering hours 0-23.

🔗 **OANDA Definition**: [dailyAlignment parameter](https://developer.oanda.com/rest-live-v20/instrument-ep/)

🔗 **Source**: [DailyAlignment](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `0` | Align to midnight (00:00) |
| `1` | Align to 01:00 |
| `2` | Align to 02:00 |
| `3` | Align to 03:00 |
| `4` | Align to 04:00 |
| `5` | Align to 05:00 |
| `6` | Align to 06:00 |
| `7` | Align to 07:00 |
| `8` | Align to 08:00 |
| `9` | Align to 09:00 |
| `10` | Align to 10:00 |
| `11` | Align to 11:00 |
| `12` | Align to noon (12:00) |
| `13` | Align to 13:00 |
| `14` | Align to 14:00 |
| `15` | Align to 15:00 |
| `16` | Align to 16:00 |
| `17` | Align to 17:00 |
| `18` | Align to 18:00 |
| `19` | Align to 19:00 |
| `20` | Align to 20:00 |
| `21` | Align to 21:00 |
| `22` | Align to 22:00 |
| `23` | Align to 23:00 |

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

## Order Reason Enums

### MarketOrderReason

The reason that a Market Order was created.

🔗 **OANDA Definition**: [MarketOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderReason)

🔗 **Source**: [MarketOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order created at the request of a client |
| `TRADE_CLOSE` | Order created to close a trade at the request of a client |
| `POSITION_CLOSEOUT` | Order created to close a position at the request of a client |
| `MARGIN_CLOSEOUT` | Order created as part of a margin closeout |
| `DELAYED_TRADE_CLOSE` | Order created to close a trade that was not tradeable at the original close time |

### MarketOrderMarginCloseoutReason

The reason that a Market Order was created to perform a margin closeout.

🔗 **OANDA Definition**: [MarketOrderMarginCloseoutReason](https://developer.oanda.com/rest-live-v20/transaction-df/#MarketOrderMarginCloseoutReason)

🔗 **Source**: [MarketOrderMarginCloseoutReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `MARGIN_CHECK_VIOLATION` | Trade closures resulted from violating OANDA's margin policy |
| `REGULATORY_MARGIN_CALL_VIOLATION` | Trade closures came from a margin closeout event resulting from regulatory conditions |
| `REGULATORY_MARGIN_CHECK_VIOLATION` | Trade closures resulted from violating the margin policy imposed by regulatory requirements |

### FixedPriceOrderReason

The reason that a Fixed Price Order was created.

🔗 **OANDA Definition**: [FixedPriceOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#FixedPriceOrderReason)

🔗 **Source**: [FixedPriceOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `PLATFORM_ACCOUNT_MIGRATION` | Order created as part of a platform account migration |
| `TRADE_CLOSE_DIVISION_ACCOUNT_MIGRATION` | Order created to close a trade as part of a division account migration |
| `TRADE_CLOSE_ADMINISTRATIVE_ACTION` | Order created to close a trade by an administrative action |

### LimitOrderReason

The reason that a Limit Order was initiated.

🔗 **OANDA Definition**: [LimitOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#LimitOrderReason)

🔗 **Source**: [LimitOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |

### StopOrderReason

The reason that a Stop Order was initiated.

🔗 **OANDA Definition**: [StopOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#StopOrderReason)

🔗 **Source**: [StopOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |

### MarketIfTouchedOrderReason

The reason that a Market-if-touched Order was initiated.

🔗 **OANDA Definition**: [MarketIfTouchedOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#MarketIfTouchedOrderReason)

🔗 **Source**: [MarketIfTouchedOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |

### TakeProfitOrderReason

The reason that a Take Profit Order was initiated.

🔗 **OANDA Definition**: [TakeProfitOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitOrderReason)

🔗 **Source**: [TakeProfitOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |
| `ON_FILL` | Order initiated automatically when an order was filled that opened a new trade requiring a take profit order |

### StopLossOrderReason

The reason that a Stop Loss Order was initiated.

🔗 **OANDA Definition**: [StopLossOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#StopLossOrderReason)

🔗 **Source**: [StopLossOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |
| `ON_FILL` | Order initiated automatically when an order was filled that opened a new trade requiring a stop loss order |

### GuaranteedStopLossOrderReason

The reason that a Guaranteed Stop Loss Order was initiated.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#GuaranteedStopLossOrderReason)

🔗 **Source**: [GuaranteedStopLossOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |
| `ON_FILL` | Order initiated automatically when an order was filled that opened a new trade requiring a guaranteed stop loss order |

### TrailingStopLossOrderReason

The reason that a Trailing Stop Loss Order was initiated.

🔗 **OANDA Definition**: [TrailingStopLossOrderReason](https://developer.oanda.com/rest-live-v20/transaction-df/#TrailingStopLossOrderReason)

🔗 **Source**: [TrailingStopLossOrderReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_ORDER` | Order initiated at the request of a client |
| `REPLACEMENT` | Order initiated as a replacement for an existing order |
| `ON_FILL` | Order initiated automatically when an order was filled that opened a new trade requiring a trailing stop loss order |

### OrderFillReason

The reason that an Order was filled.

🔗 **OANDA Definition**: [OrderFillReason](https://developer.oanda.com/rest-live-v20/transaction-df/#OrderFillReason)

🔗 **Source**: [OrderFillReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `LIMIT_ORDER` | Order filled was a Limit Order |
| `STOP_ORDER` | Order filled was a Stop Order |
| `MARKET_IF_TOUCHED_ORDER` | Order filled was a Market-if-touched Order |
| `TAKE_PROFIT_ORDER` | Order filled was a Take Profit Order |
| `STOP_LOSS_ORDER` | Order filled was a Stop Loss Order |
| `GUARANTEED_STOP_LOSS_ORDER` | Order filled was a Guaranteed Stop Loss Order |
| `TRAILING_STOP_LOSS_ORDER` | Order filled was a Trailing Stop Loss Order |
| `MARKET_ORDER` | Order filled was a Market Order |
| `MARKET_ORDER_TRADE_CLOSE` | Order filled was a Market Order used to explicitly close a trade |
| `MARKET_ORDER_POSITION_CLOSEOUT` | Order filled was a Market Order used to explicitly close a position |
| `MARKET_ORDER_MARGIN_CLOSEOUT` | Order filled was a Market Order used for a margin closeout |
| `MARKET_ORDER_DELAYED_TRADE_CLOSE` | Order filled was a Market Order used for a delayed trade close |
| `FIXED_PRICE_ORDER` | Order filled was a Fixed Price Order |
| `FIXED_PRICE_ORDER_PLATFORM_ACCOUNT_MIGRATION` | Order filled was a Fixed Price Order created as part of a platform account migration |
| `FIXED_PRICE_ORDER_DIVISION_ACCOUNT_MIGRATION` | Order filled was a Fixed Price Order created to close a trade as part of a division account migration |
| `FIXED_PRICE_ORDER_ADMINISTRATIVE_ACTION` | Order filled was a Fixed Price Order created to close a trade by an administrative action |

### OrderCancelReason

The reason that an Order was cancelled. This enum defines 65 values; the table below shows representative examples - see the source for the complete value set.

🔗 **OANDA Definition**: [OrderCancelReason](https://developer.oanda.com/rest-live-v20/transaction-df/#OrderCancelReason)

🔗 **Source**: [OrderCancelReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `INTERNAL_SERVER_ERROR` | Order cancelled because of an internal server error |
| `CLIENT_REQUEST` | Order cancelled at the request of the client |
| `CLIENT_REQUEST_REPLACED` | Order cancelled because it was replaced at the request of the client |
| `TIME_IN_FORCE_EXPIRED` | Order cancelled because its time in force expired |
| `INSUFFICIENT_MARGIN` | Order cancelled because the account had insufficient margin |
| `LINKED_TRADE_CLOSED` | Order cancelled because its linked trade was closed |
| `MARKET_HALTED` | Order cancelled because the market it would trade in was halted |
| `FIFO_VIOLATION` | Order cancelled because filling it would have violated FIFO rules |
| `INSUFFICIENT_LIQUIDITY` | Order cancelled because there was insufficient liquidity to fill it |

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

### GuaranteedStopLossOrderMutability

Actions that can be performed on guaranteed Stop Loss Orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderMutability](https://developer.oanda.com/rest-live-v20/account-df/#GuaranteedStopLossOrderMutability)

🔗 **Source**: [GuaranteedStopLossOrderMutability](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `FIXED` | Once created, guaranteed stop loss orders cannot be replaced or cancelled |
| `REPLACEABLE` | An existing guaranteed stop loss order can only be replaced, not cancelled |
| `CANCELABLE` | Once trading is disabled, guaranteed stop loss orders can be cancelled but not replaced |
| `PRICE_WIDEN_ONLY` | An existing guaranteed stop loss order can only be replaced to widen the gap from the current price, not cancelled |

### GuaranteedStopLossOrderModeForInstrument

Guaranteed stop loss order modes specific to instruments.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderModeForInstrument](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_14)

🔗 **Source**: [GuaranteedStopLossOrderModeForInstrument](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `DISABLED` | GSL orders disabled for this instrument |
| `ALLOWED` | GSL orders allowed for this instrument |
| `REQUIRED` | GSL orders required for this instrument |

## Transaction Enums

### TransactionFilter

Transaction type filters accepted by OANDA transaction list endpoints. This enum defines 42 values covering every transaction type plus aggregate filters; the table below shows representative examples - see the source for the complete value set.

🔗 **OANDA Definition**: [TransactionFilter](https://developer.oanda.com/rest-live-v20/transaction-df/#TransactionFilter)

🔗 **Source**: [TransactionFilter](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `ORDER` | Order-related transactions (aggregate filter) |
| `FUNDING` | Funding-related transactions (aggregate filter) |
| `ADMIN` | Administrative transactions (aggregate filter) |
| `MARKET_ORDER` | Market order transactions |
| `ORDER_FILL` | Order fill transactions |
| `ORDER_CANCEL` | Order cancel transactions |
| `MARGIN_CALL_ENTER` | Margin call entered transactions |
| `DAILY_FINANCING` | Daily financing transactions |
| `TRANSFER_FUNDS` | Fund transfer transactions |

### TransactionRejectReason

Reasons why a transaction may be rejected. This enum defines 198 values; the table below shows representative examples - see the source for the complete value set.

🔗 **OANDA Definition**: [TransactionRejectReason](https://developer.oanda.com/rest-live-v20/transaction-df/#TransactionRejectReason)

🔗 **Source**: [TransactionRejectReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `INTERNAL_SERVER_ERROR` | An internal server error prevented the transaction from being processed |
| `INSTRUMENT_MISSING` | The instrument specified is missing |
| `INSTRUMENT_NOT_TRADEABLE` | The instrument specified is not tradeable by the account |
| `UNITS_MISSING` | Order units have not been specified |
| `PRICE_INVALID` | The price specified is invalid |
| `INSUFFICIENT_MARGIN` | The account had insufficient margin for the transaction |
| `TIME_IN_FORCE_MISSING` | The time in force has not been specified |
| `CLIENT_ORDER_ID_ALREADY_EXISTS` | The client order ID specified is already assigned to another pending order |
| `MARKET_HALTED` | The market for the specified instrument is halted |

### FundingReason

Reasons for funding transactions.

🔗 **OANDA Definition**: [FundingReason](https://developer.oanda.com/rest-live-v20/transaction-df/#FundingReason)

🔗 **Source**: [FundingReason](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `CLIENT_FUNDING` | Funds visible in the account were pushed or pulled by the client |
| `ACCOUNT_TRANSFER` | Funds transferred between two accounts belonging to the same client |
| `DIVISION_MIGRATION` | Funds transferred as part of a division migration |
| `SITE_MIGRATION` | Funds transferred as part of a site migration |
| `ADJUSTMENT` | Funds transferred as part of an account adjustment |

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

### TradePL

The classification of a trade's profit/loss, used when filtering trade queries.

🔗 **OANDA Definition**: [TradePL](https://developer.oanda.com/rest-live-v20/trade-df/#TradePL)

🔗 **Source**: [TradePL](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/enums.py)

| Value | Description |
|-------|-------------|
| `POSITIVE` | An open trade currently in a positive (profitable) state |
| `NEGATIVE` | An open trade currently in a negative (losing) state |
| `ZERO` | An open trade currently at break-even |

All enums are string-based and can be used directly with OANDA API endpoints or for type validation in your trading applications.
