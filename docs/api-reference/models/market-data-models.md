# Market Data Models

**OANDA Reference**: [Pricing Data Definitions](https://developer.oanda.com/rest-live-v20/pricing-df/) | [Instrument Data Definitions](https://developer.oanda.com/rest-live-v20/instrument-df/)

Models for market pricing, instrument specifications, and candlestick (OHLC) data.

---

## Pricing Models

### ClientPrice
Current market prices for an instrument.

🔗 **OANDA Definition**: [ClientPrice](https://developer.oanda.com/rest-live-v20/pricing-df/#collapse_definition_1)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ➖ | Price type identifier (default: "PRICE") |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Timestamp when price was created |
| `status` | [PriceStatus](enum-models.md#pricestatus) | ➖ | Price status (deprecated but may still be present) |
| `tradeable` | bool | ✅ | Whether the instrument is currently tradeable |
| `bids` | list[[PriceBucket](#pricebucket)] | ✅ | Available bid prices and liquidity levels |
| `asks` | list[[PriceBucket](#pricebucket)] | ✅ | Available ask prices and liquidity levels |
| `closeout_bid` | [PriceValue](system-models.md#type-aliases) |✅ | Bid price used for position closeout (closing long positions) |
| `closeout_ask` | [PriceValue](system-models.md#type-aliases) |✅ | Ask price used for position closeout (closing short positions) |
| `quote_home_conversion_factors` | [QuoteHomeConversionFactors](#quotehomeconversionfactors) | ➖ | Currency conversion factors for quote currency calculations |
| `units_available` | [UnitsAvailable](#unitsavailable) | ➖ | Available units for trading different order types |

### QuoteHomeConversionFactors
Conversion factors for quote currency calculations.

🔗 **OANDA Definition**: [QuoteHomeConversionFactors](https://developer.oanda.com/rest-live-v20/pricing-df/#QuoteHomeConversionFactors)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `positive_units` | Decimal | ✅ | Conversion factor for positive (long) units |
| `negative_units` | Decimal | ✅ | Conversion factor for negative (short) units |

### HomeConversions
Currency conversion factors for account calculations.

🔗 **OANDA Definition**: [HomeConversions](https://developer.oanda.com/rest-live-v20/pricing-df/#HomeConversions)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `currency` | [Currency](system-models.md#currency) | ✅ | The currency being converted |
| `account_gain` | Decimal | ✅ | Factor for converting gains to account currency |
| `account_loss` | Decimal | ✅ | Factor for converting losses to account currency |
| `position_value` | Decimal | ✅ | Factor for converting position values |

### PricingHeartbeat
Heartbeat message for pricing streams.

🔗 **OANDA Definition**: [PricingHeartbeat](https://developer.oanda.com/rest-live-v20/pricing-df/#PricingHeartbeat)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ➖ | Always "HEARTBEAT" |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Heartbeat timestamp |

### Price
General price representation (alternative to ClientPrice for different contexts).

🔗 **OANDA Definition**: [Price](https://developer.oanda.com/rest-live-v20/pricing-df/#Price)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Timestamp when price was created |
| `tradeable` | bool | ✅ | Whether the instrument is currently tradeable |
| `bids` | list[[PriceBucket](#pricebucket)] | ✅ | Available bid prices and liquidity levels |
| `asks` | list[[PriceBucket](#pricebucket)] | ✅ | Available ask prices and liquidity levels |
| `closeout_bid` | [PriceValue](system-models.md#type-aliases) |✅ | Bid price used for position closeout (closing long positions) |
| `closeout_ask` | [PriceValue](system-models.md#type-aliases) |✅ | Ask price used for position closeout (closing short positions) |

### UnitsAvailable
Representation of how many units of an Instrument are available to be traded.

🔗 **OANDA Definition**: [UnitsAvailable](https://developer.oanda.com/rest-live-v20/order-df/#UnitsAvailable)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `default` | Decimal | ✅ | Default units available |
| `reduce_first` | Decimal | ✅ | Units available for reduce-first fills |
| `reduce_only` | Decimal | ✅ | Units available for reduce-only fills |
| `open_only` | Decimal | ✅ | Units available for open-only fills |

### PriceBucket
Price level with available liquidity.

🔗 **OANDA Definition**: [PriceBucket](https://developer.oanda.com/rest-live-v20/pricing-common-df/#collapse_definition_2)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | Decimal | ✅ | The quoted price at this level |
| `liquidity` | int | ✅ | Available volume (units) at this price level |

### Candlestick
OHLC candlestick data for an instrument.

🔗 **OANDA Definition**: [Candlestick](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_3)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Start time of the candlestick period |
| `bid` | [CandlestickData](#candlestickdata) | ➖ | Bid-based OHLC data for the time period |
| `ask` | [CandlestickData](#candlestickdata) | ➖ | Ask-based OHLC data for the time period |
| `mid` | [CandlestickData](#candlestickdata) | ➖ | Mid-price OHLC data ((bid+ask)/2) for the time period |
| `volume` | int | ✅ | Number of price ticks during the time period |
| `complete` | bool | ✅ | Whether the candlestick is complete (end time is not in future) |

### CandlestickData
Open, High, Low, Close data for one price type.

🔗 **OANDA Definition**: [CandlestickData](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_4)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `o` | Decimal | ✅ | Opening price for the time period |
| `h` | Decimal | ✅ | Highest price during the time period |
| `l` | Decimal | ✅ | Lowest price during the time period |
| `c` | Decimal | ✅ | Closing price for the time period |

---

## Instrument Models

### Instrument
Trading instrument information and specifications.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Unique instrument identifier (e.g., "EUR_USD") |
| `type` | [InstrumentType](system-models.md#instrumenttype) | ✅ | Classification of instrument (CURRENCY, CFD, METAL) |
| `display_name` | str | ✅ | Human-readable instrument name |
| `pip_location` | int | ✅ | Location of pip value (decimal places from right) |
| `display_precision` | int | ✅ | Number of decimal places for display formatting |
| `trade_units_precision` | int | ✅ | Decimal precision for trade unit values |
| `minimum_trade_size` | Decimal | ✅ | Smallest allowable trade size for this instrument |
| `maximum_trailing_stop_distance` | Decimal | ✅ | Maximum trailing stop distance allowed |
| `minimum_trailing_stop_distance` | Decimal | ✅ | Minimum trailing stop distance required |
| `maximum_position_size` | Decimal | ✅ | Maximum position size allowed for this instrument |
| `maximum_order_units` | Decimal | ✅ | Maximum order size allowed for this instrument |
| `margin_rate` | Decimal | ✅ | Margin requirement as decimal (e.g., "0.03333" for 30:1 leverage) |
| `minimum_guaranteed_stop_loss_distance` | Decimal | ➖ | Minimum distance for guaranteed stop loss orders |
| `commission` | [InstrumentCommission](#instrumentcommission) | ➖ | Commission structure for this instrument |
| `guaranteed_stop_loss_order_mode` | [GuaranteedStopLossOrderModeForInstrument](enum-models.md#guaranteedstoplossordermodeforinstrument) | ➖ | Guaranteed stop loss availability (DISABLED, ALLOWED, REQUIRED) |
| `guaranteed_stop_loss_order_execution_premium` | Decimal | ➖ | Premium charged for guaranteed stop loss execution |
| `guaranteed_stop_loss_order_level_restriction` | [GuaranteedStopLossOrderLevelRestriction](#guaranteedstoplossorderlevelrestriction) | ➖ | Restrictions on guaranteed stop loss levels |
| `financing` | [InstrumentFinancing](#instrumentfinancing) | ➖ | Daily financing rate details for long and short positions |
| `tags` | list[[Tag](#tag)] | ✅ | Descriptive tags for instrument categorization |

### CandlestickResponse
Container for multiple candlesticks with metadata.

🔗 **OANDA Definition**: [CandlestickResponse](https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickResponse)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Trading instrument identifier |
| `granularity` | [CandlestickGranularity](enum-models.md#candlestickgranularity) | ✅ | Time interval of the candlesticks |
| `candles` | list[[Candlestick](#candlestick)] | ✅ | Array of candlestick objects |

### CandlestickGranularity
Time intervals for candlestick data.

🔗 **OANDA Definition**: [CandlestickGranularity](https://developer.oanda.com/rest-live-v20/instrument-df/#CandlestickGranularity)

| Value | Description | Alignment |
|-------|-------------|-----------|
| `S5` | 5 second candlesticks | Minute aligned |
| `S10` | 10 second candlesticks | Minute aligned |
| `S15` | 15 second candlesticks | Minute aligned |
| `S30` | 30 second candlesticks | Minute aligned |
| `M1` | 1 minute candlesticks | Hour aligned |
| `M2` | 2 minute candlesticks | Hour aligned |
| `M4` | 4 minute candlesticks | Hour aligned |
| `M5` | 5 minute candlesticks | Hour aligned |
| `M10` | 10 minute candlesticks | Hour aligned |
| `M15` | 15 minute candlesticks | Hour aligned |
| `M30` | 30 minute candlesticks | Hour aligned |
| `H1` | 1 hour candlesticks | Day aligned |
| `H2` | 2 hour candlesticks | Day aligned |
| `H3` | 3 hour candlesticks | Day aligned |
| `H4` | 4 hour candlesticks | Day aligned |
| `H6` | 6 hour candlesticks | Day aligned |
| `H8` | 8 hour candlesticks | Day aligned |
| `H12` | 12 hour candlesticks | Day aligned |
| `D` | 1 day candlesticks | Week aligned |
| `W` | 1 week candlesticks | Month aligned |
| `M` | 1 month candlesticks | Year aligned |

### WeeklyAlignment
Days of the week for weekly alignment.

🔗 **OANDA Definition**: [WeeklyAlignment](https://developer.oanda.com/rest-live-v20/instrument-df/#WeeklyAlignment)

| Value | Description |
|-------|-------------|
| `Monday` | Weekly candlesticks aligned to Monday |
| `Tuesday` | Weekly candlesticks aligned to Tuesday |
| `Wednesday` | Weekly candlesticks aligned to Wednesday |
| `Thursday` | Weekly candlesticks aligned to Thursday |
| `Friday` | Weekly candlesticks aligned to Friday |
| `Saturday` | Weekly candlesticks aligned to Saturday |
| `Sunday` | Weekly candlesticks aligned to Sunday |

### InstrumentCommission
Commission structure for trading instruments.

🔗 **OANDA Definition**: [InstrumentCommission](https://developer.oanda.com/rest-live-v20/primitives-df/#InstrumentCommission)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `commission` | Decimal | ✅ | Commission rate per unit traded |
| `units_traded` | Decimal | ✅ | Units traded to apply commission |
| `minimum_commission` | Decimal | ✅ | Minimum commission amount |

### FinancingDayOfWeek
Daily financing rate details for specific days.

🔗 **OANDA Definition**: [FinancingDayOfWeek](https://developer.oanda.com/rest-live-v20/primitives-df/#FinancingDayOfWeek)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `day_of_week` | [DayOfWeek](enum-models.md#dayofweek) | ✅ | Day of the week (SUNDAY through SATURDAY) |
| `days_charged` | int | ✅ | Number of days of financing charged for this day |

### InstrumentFinancing
Financing data for an instrument including long/short rates and daily schedule.

🔗 **OANDA Definition**: [InstrumentFinancing](https://developer.oanda.com/rest-live-v20/instrument-df/#InstrumentFinancing)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `long_rate` | Decimal | ✅ | Financing rate applied to long positions |
| `short_rate` | Decimal | ✅ | Financing rate applied to short positions |
| `financing_days_of_week` | list[[FinancingDayOfWeek](#financingdayofweek)] | ✅ | Daily financing schedule for the week |

### Tag
A tag associated with an entity for categorization.

🔗 **OANDA Definition**: [Tag](https://developer.oanda.com/rest-live-v20/primitives-df/#Tag)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ✅ | Type of the tag |
| `name` | str | ✅ | Name of the tag |

### UnitsAvailableDetails
Units available for both long and short orders on an instrument.

🔗 **OANDA Definition**: [UnitsAvailableDetails](https://developer.oanda.com/rest-live-v20/pricing-df/#UnitsAvailableDetails)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `long` | [UnitsAvailable](#unitsavailable) | ✅ | Long position units availability |
| `short` | [UnitsAvailable](#unitsavailable) | ✅ | Short position units availability |

### OrderBook
Order book depth data for an instrument showing bid/ask levels.

🔗 **OANDA Definition**: [OrderBook](https://developer.oanda.com/rest-live-v20/pricing-df/#OrderBook)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) | ✅ | Instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Time when order book data was captured |
| `price` | [PriceValue](system-models.md#type-aliases) |➖ | Reference price for the order book |
| `bucket_width` | [PriceValue](system-models.md#type-aliases) |➖ | Width of each price bucket |
| `buckets` | list[[PriceBucket](#pricebucket)] | ✅ | Price buckets with bid/ask volume |

### GuaranteedStopLossOrderEntryData
Details required by clients to add a Guaranteed Stop Loss Order for a specific instrument.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderEntryData](https://developer.oanda.com/rest-live-v20/instrument-df/#GuaranteedStopLossOrderEntryData)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `minimum_distance` | Decimal | ✅ | Minimum distance from current price for GSL order |
| `premium` | Decimal | ✅ | Premium charged for guaranteed execution |
| `level_restriction` | [GuaranteedStopLossOrderLevelRestriction](#guaranteedstoplossorderlevelrestriction) | ➖ | Level restrictions for this instrument |

### GuaranteedStopLossOrderLevelRestriction
Volume and price range restrictions for guaranteed stop loss orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderLevelRestriction](https://developer.oanda.com/rest-live-v20/instrument-df/#GuaranteedStopLossOrderLevelRestriction)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `volume` | Decimal | ✅ | Volume restriction level |
| `price_range` | Decimal | ✅ | Price range restriction |