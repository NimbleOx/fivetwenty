# Data Models Reference

Complete API reference for FiveTwenty's comprehensive data model system, covering all OANDA v20 API data structures.

---

## Model Categories

FiveTwenty provides 130+ Pydantic models and 41 enums organized into logical categories:

### Enum Models
[**Enumerations & Constants →**](enum-models.md)

Type-safe enumerations for all OANDA API parameters and values.

| Enum | Purpose |
|------|---------|
| **Core Trading** | |
| [InstrumentName](enum-models.md#instrumentname) | Available trading instrument pairs (EUR_USD, GBP_JPY, etc.) |
| [Direction](enum-models.md#direction) | Trade direction (LONG, SHORT) |
| [Currency](enum-models.md#currency) | ISO 4217 currency codes (USD, EUR, GBP, etc.) |
| [InstrumentType](enum-models.md#instrumenttype) | Instrument classification (CURRENCY, CFD, METAL) |
| [TransactionType](enum-models.md#transactiontype) | Transaction categories (ORDER_FILL, DAILY_FINANCING, etc.) |
| **Price & Market Data** | |
| [CandlestickGranularity](enum-models.md#candlestickgranularity) | Time intervals for candlestick data (M1, H1, D, etc.) |
| [PriceStatus](enum-models.md#pricestatus) | Price data status (tradeable, non-tradeable, invalid) |
| [WeeklyAlignment](enum-models.md#weeklyalignment) | Day of week for weekly candlestick alignment |
| [DayOfWeek](enum-models.md#dayofweek) | Days of the week enumeration |
| **Order Management** | |
| [OrderType](enum-models.md#ordertype) | Order types (MARKET, LIMIT, STOP, etc.) |
| [OrderState](enum-models.md#orderstate) | Order lifecycle state (PENDING, FILLED, CANCELLED) |
| [TimeInForce](enum-models.md#timeinforce) | Order duration policies (GTC, GTD, GFD, FOK, IOC) |
| [OrderPositionFill](enum-models.md#orderpositionfill) | Position modification behavior for orders |
| [OrderTriggerCondition](enum-models.md#ordertriggercondition) | Price trigger conditions (DEFAULT, BID, ASK, MID) |
| [OrderStateFilter](enum-models.md#orderstatefilter) | Filter for querying orders by state |
| [CancellableOrderType](enum-models.md#cancellableordertype) | Types of orders that can be cancelled |
| **Account & Position** | |
| [AccountFinancingMode](enum-models.md#accountfinancingmode) | Account financing calculation modes |
| [PositionAggregationMode](enum-models.md#positionaggregationmode) | Position aggregation methods |
| [GuaranteedStopLossOrderMode](enum-models.md#guaranteedstoplossordermode) | GSL order availability for accounts |
| [GuaranteedStopLossOrderModeForInstrument](enum-models.md#guaranteedstoplossordermodeforinstrument) | GSL order availability for instruments |
| **Trade Filtering** | |
| [TradeState](enum-models.md#tradestate) | Trade lifecycle state (OPEN, CLOSED, CLOSE_WHEN_TRADEABLE) |
| [TradeStateFilter](enum-models.md#tradestatefilter) | Filter for querying trades by state |

### Account Models
[**Account Management →**](account-models.md)

Models for account information, balance tracking, and account state management.

| Model | Purpose |
|-------|---------|
| [Account](account-models.md#account) | Complete account information including balance, margin, and trading statistics |
| [AccountSummary](account-models.md#accountsummary) | Condensed account information for quick overview and monitoring |
| [AccountProperties](account-models.md#accountproperties) | Basic account identification and classification information |
| [AccountChanges](account-models.md#accountchanges) | Track changes to orders, trades, and positions since a transaction ID |
| [AccountChangesState](account-models.md#accountchangesstate) | Price-dependent account state for real-time monitoring |
| [CalculatedAccountState](account-models.md#calculatedaccountstate) | Dynamically calculated account state including margin calculations |
| [GuaranteedStopLossOrderParameters](account-models.md#guaranteedstoplossorderparameters) | Configuration settings for guaranteed stop loss order behavior |

### Trading Models
[**Trade & Position Management →**](trading-models.md)

Models for trade lifecycle, position management, and P&L tracking.

| Model | Purpose |
|-------|---------|
| [Trade](trading-models.md#trade) | Represents an open trade position with full lifecycle details |
| [TradeSummary](trading-models.md#tradesummary) | Condensed trade information for lists and overviews |
| [TradeSpecifier](trading-models.md#tradespecifier) | Trade identification format for API requests |
| [CalculatedTradeState](trading-models.md#calculatedtradestate) | Dynamic trade state with real-time P&L calculations |
| [Position](trading-models.md#position) | Aggregated position information for an instrument |
| [PositionSide](trading-models.md#positionside) | One side (long or short) of a position with detailed metrics |

### Order Models
[**Order Management →**](order-models.md)

Comprehensive order creation, management, and execution models.

| Model | Purpose |
|-------|---------|
| [MarketOrderRequest](order-models.md#marketorderrequest) | Request to create a market order for immediate execution at current market price |
| [LimitOrderRequest](order-models.md#limitorderrequest) | Request to create a limit order for execution at specific price or better |
| [StopOrderRequest](order-models.md#stoporderrequest) | Request to create a stop order triggered when price reaches stop level |
| [TakeProfitOrderRequest](order-models.md#takeprofitorderrequest) | Request to create a take profit order to close trade at profit target |
| [StopLossOrderRequest](order-models.md#stoplossorderrequest) | Request to create a stop loss order to limit trade losses |
| [TrailingStopLossOrderRequest](order-models.md#trailingstoplossorderrequest) | Request to create a trailing stop loss that follows favorable price movement |
| [MarketIfTouchedOrderRequest](order-models.md#marketiftouchedorderrequest) | Request to create an order that becomes market order when price touched |
| [GuaranteedStopLossOrderRequest](order-models.md#guaranteedstoplossorderrequest) | Request to create a guaranteed stop loss order with guaranteed execution |
| [TakeProfitOrder](order-models.md#takeprofitorder) | Active take profit order attached to a trade for profit realization |
| [StopLossOrder](order-models.md#stoplossorder) | Active stop loss order attached to a trade for loss limitation |
| [TrailingStopLossOrder](order-models.md#trailingstoplossorder) | Active trailing stop that automatically adjusts with favorable price moves |
| [MarketIfTouchedOrder](order-models.md#marketiftouchedorder) | Pending order that triggers market execution when price level touched |
| [FixedPriceOrder](order-models.md#fixedpriceorder) | System-created order with fixed execution price (typically for dividends) |
| [TakeProfitDetails](order-models.md#takeprofitdetails) | Configuration details for take profit order creation |
| [StopLossDetails](order-models.md#stoplossdetails) | Configuration details for stop loss order creation |
| [TrailingStopLossDetails](order-models.md#trailingstoplossdetails) | Configuration details for trailing stop loss order creation |
| [GuaranteedStopLossDetails](order-models.md#guaranteedstoplossdetails) | Configuration details for guaranteed stop loss order creation |
| [ClientExtensions](order-models.md#clientextensions) | Custom metadata and tags for client-side order tracking |

### Market Data Models
[**Pricing & Instruments →**](market-data-models.md)

Models for real-time pricing, historical data, and instrument specifications.

| Model | Purpose |
|-------|---------|
| [ClientPrice](market-data-models.md#clientprice) | Real-time tradeable prices with bid/ask spreads and closeout rates for immediate trading decisions |
| [QuoteHomeConversionFactors](market-data-models.md#quotehomeconversionfactors) | Currency conversion factors for calculating quote currency amounts in account home currency |
| [HomeConversions](market-data-models.md#homeconversions) | Pre-calculated conversion factors for converting instrument P&L to account home currency |
| [PricingHeartbeat](market-data-models.md#pricingheartbeat) | Streaming heartbeat message to confirm active price stream connection and prevent timeouts |
| [UnitsAvailable](market-data-models.md#unitsavailable) | Maximum tradeable units available for different order scenarios and position states |
| [PriceBucket](market-data-models.md#pricebucket) | Market depth information showing available liquidity at specific price levels |
| [Candlestick](market-data-models.md#candlestick) | Historical OHLC price data with volume for technical analysis and charting |
| [CandlestickData](market-data-models.md#candlestickdata) | Open, High, Low, Close price values for a specific time period |
| [Instrument](market-data-models.md#instrument) | Trading instrument specifications including precision, margins, and trading rules |
| [InstrumentCommission](market-data-models.md#instrumentcommission) | Commission structure definition showing costs per trade for specific instruments |
| [FinancingDayOfWeek](market-data-models.md#financingdayofweek) | Daily financing charge configuration specifying rollover costs by day of week |

### Transaction Models
[**Transaction History →**](transaction-models.md)

Models for transaction tracking, audit trails, and order execution history.

| Model | Purpose |
|-------|---------|
| [Transaction](transaction-models.md#transaction) | Base transaction record providing audit trail for all account activity and state changes |
| [OrderFillTransaction](transaction-models.md#orderfilltransaction) | Record of order execution showing trade details, fill price, and resulting position changes |
| [OrderCancelTransaction](transaction-models.md#ordercanceltransaction) | Record of order cancellation with reason code for audit and debugging purposes |
| [MarketOrderTransaction](transaction-models.md#marketordertransaction) | Record of market order creation request with execution parameters and timing |
| [LimitOrderTransaction](transaction-models.md#limitordertransaction) | Record of limit order creation with price level and conditional execution parameters |
| [StopOrderTransaction](transaction-models.md#stopordertransaction) | Record of stop order creation with trigger price and risk management settings |
| [TakeProfitOrderTransaction](transaction-models.md#takeprofitordertransaction) | Record of take profit order creation for automated profit realization on trades |
| [StopLossOrderTransaction](transaction-models.md#stoplossordertransaction) | Record of stop loss order creation for automated loss limitation on trades |
| [TrailingStopLossOrderTransaction](transaction-models.md#trailingstoplossordertransaction) | Record of trailing stop creation with dynamic distance-based profit protection |

### System Models
[**System & Utilities →**](system-models.md)

Models for streaming configuration, error handling, and type aliases.

| Model | Purpose |
|-------|---------|
| [StreamingConfiguration](system-models.md#streamingconfiguration) | Configuration for real-time price streaming including heartbeat and timeout settings |
| [ReconnectionPolicy](system-models.md#reconnectionpolicy) | Automated reconnection strategy with exponential backoff for resilient streaming connections |
| [ErrorDetails](system-models.md#errordetails) | Structured API error information with codes and messages for error handling and debugging |
| [ValidationViolation](system-models.md#validationviolation) | Field-level validation error details showing rejected values and constraint violations |
