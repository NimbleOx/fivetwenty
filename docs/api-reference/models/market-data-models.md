# Market Data Models

**OANDA Reference**: [Pricing Data Definitions](https://developer.oanda.com/rest-live-v20/pricing-df/) | [Instrument Data Definitions](https://developer.oanda.com/rest-live-v20/instrument-df/)

Models for market pricing, instrument specifications, and candlestick (OHLC) data.

Field names are Python attributes. Required means required at model construction;
`None` in the type indicates a nullable value. Defaults and local validation do not
establish server eligibility. See [reading model tables](index.md#reading-model-tables).

---

## Pricing Models

### ClientPrice
Current market prices for an instrument.

🔗 **OANDA Definition**: [ClientPrice](https://developer.oanda.com/rest-live-v20/pricing-df/#collapse_definition_1)

🔗 **Source**: [ClientPrice](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ➖ | Price type identifier (default: "PRICE") |
| `instrument` | [InstrumentName](enum-models.md#instrumentname) \| str \| None | ➖ | Trading instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) \| None | ➖ | Timestamp when price was created |
| `status` | [PriceStatus](enum-models.md#pricestatus) \| None | ➖ | Price status (deprecated but may still be present) |
| `tradeable` | bool \| None | ➖ | Whether the instrument is currently tradeable |
| `bids` | list[[PriceBucket](#pricebucket)] | ➖ | Available bid prices and liquidity levels |
| `asks` | list[[PriceBucket](#pricebucket)] | ➖ | Available ask prices and liquidity levels |
| `closeout_bid` | [PriceValue](system-models.md#type-aliases) |✅ | Bid price used for position closeout (closing long positions) |
| `closeout_ask` | [PriceValue](system-models.md#type-aliases) |✅ | Ask price used for position closeout (closing short positions) |
| `quote_home_conversion_factors` | [QuoteHomeConversionFactors](#quotehomeconversionfactors) \| None | ➖ | Currency conversion factors for quote currency calculations |
| `units_available` | [UnitsAvailable](#unitsavailable) \| None | ➖ | Available units for trading different order types |

### QuoteHomeConversionFactors
Conversion factors for quote currency calculations.

🔗 **OANDA Definition**: [QuoteHomeConversionFactors](https://developer.oanda.com/rest-live-v20/pricing-df/#QuoteHomeConversionFactors)

🔗 **Source**: [QuoteHomeConversionFactors](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `positive_units` | Decimal | ✅ | Conversion factor for positive quote-currency amounts |
| `negative_units` | Decimal | ✅ | Conversion factor for negative quote-currency amounts |

### HomeConversions
Currency conversion factors for account calculations.

🔗 **OANDA Definition**: [HomeConversions](https://developer.oanda.com/rest-live-v20/pricing-df/#HomeConversions)

🔗 **Source**: [HomeConversions](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `currency` | [Currency](enum-models.md#currency) | ✅ | The currency being converted |
| `account_gain` | Decimal | ✅ | Factor for converting gains to account currency |
| `account_loss` | Decimal | ✅ | Factor for converting losses to account currency |
| `position_value` | Decimal | ✅ | Factor for converting position values |

### PricingHeartbeat
Heartbeat message for pricing streams.

🔗 **OANDA Definition**: [PricingHeartbeat](https://developer.oanda.com/rest-live-v20/pricing-df/#PricingHeartbeat)

🔗 **Source**: [PricingHeartbeat](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ➖ | Always "HEARTBEAT" |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Heartbeat timestamp |

### UnitsAvailable
Representation of how many units of an Instrument are available to be traded.

🔗 **OANDA Definition**: [UnitsAvailable](https://developer.oanda.com/rest-live-v20/order-df/#UnitsAvailable)

🔗 **Source**: [UnitsAvailable](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `default` | [UnitsAvailableDetails](market-data-models.md#unitsavailabledetails) | ✅ | Long and short availability under default position-fill behavior |
| `reduce_first` | [UnitsAvailableDetails](market-data-models.md#unitsavailabledetails) | ✅ | Long and short availability for reduce-first fills |
| `reduce_only` | [UnitsAvailableDetails](market-data-models.md#unitsavailabledetails) | ✅ | Long and short availability for reduce-only fills |
| `open_only` | [UnitsAvailableDetails](market-data-models.md#unitsavailabledetails) | ✅ | Long and short availability for open-only fills |

### PriceBucket
Price level with available liquidity.

🔗 **OANDA Definition**: [PriceBucket](https://developer.oanda.com/rest-live-v20/pricing-common-df/#collapse_definition_2)

🔗 **Source**: [PriceBucket](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | The quoted price at this level |
| `liquidity` | Decimal | ✅ | Available volume (units) at this price level |

### Candlestick
OHLC candlestick data for an instrument.

🔗 **OANDA Definition**: [Candlestick](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_3)

🔗 **Source**: [Candlestick](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Start time of the candlestick period |
| `bid` | [CandlestickData](#candlestickdata) \| None | ➖ | Bid-based OHLC data for the time period |
| `ask` | [CandlestickData](#candlestickdata) \| None | ➖ | Ask-based OHLC data for the time period |
| `mid` | [CandlestickData](#candlestickdata) \| None | ➖ | Mid-price OHLC data ((bid+ask)/2) for the time period |
| `volume` | int | ✅ | Number of prices created during the interval, not traded units |
| `complete` | bool | ✅ | Whether the candlestick is complete (end time is not in future) |

### CandlestickData
Open, High, Low, Close data for one price type.

🔗 **OANDA Definition**: [CandlestickData](https://developer.oanda.com/rest-live-v20/instrument-df/#collapse_definition_4)

🔗 **Source**: [CandlestickData](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `o` | [PriceValue](system-models.md#type-aliases) | ✅ | Opening price for the time period |
| `h` | [PriceValue](system-models.md#type-aliases) | ✅ | Highest price during the time period |
| `l` | [PriceValue](system-models.md#type-aliases) | ✅ | Lowest price during the time period |
| `c` | [PriceValue](system-models.md#type-aliases) | ✅ | Closing price for the time period |

---

## Instrument Models

### Instrument
Trading instrument information and specifications.

🔗 **OANDA Definition**: [Instrument](https://developer.oanda.com/rest-live-v20/primitives-df/#collapse_definition_10)

🔗 **Source**: [Instrument](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | [InstrumentName](enum-models.md#instrumentname) \| str | ✅ | Unique instrument identifier (e.g., "EUR_USD") |
| `type` | [InstrumentType](enum-models.md#instrumenttype) | ✅ | Classification of instrument (CURRENCY, CFD, METAL) |
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
| `minimum_guaranteed_stop_loss_distance` | Decimal \| None | ➖ | Minimum distance for guaranteed stop loss orders |
| `commission` | [InstrumentCommission](#instrumentcommission) \| None | ➖ | Commission structure for this instrument |
| `guaranteed_stop_loss_order_mode` | [GuaranteedStopLossOrderModeForInstrument](enum-models.md#guaranteedstoplossordermodeforinstrument) \| None | ➖ | Guaranteed stop loss availability (DISABLED, ALLOWED, REQUIRED) |
| `guaranteed_stop_loss_order_execution_premium` | Decimal \| None | ➖ | Premium charged for guaranteed stop loss execution |
| `guaranteed_stop_loss_order_level_restriction` | [GuaranteedStopLossOrderLevelRestriction](#guaranteedstoplossorderlevelrestriction) \| None | ➖ | Restrictions on guaranteed stop loss levels |
| `financing` | [InstrumentFinancing](#instrumentfinancing) \| None | ➖ | Daily financing rate details for long and short positions |
| `tags` | list[[Tag](#tag)] | ➖ | Descriptive tags for instrument categorization |

### InstrumentCommission
Commission structure for trading instruments.

🔗 **OANDA Definition**: [InstrumentCommission](https://developer.oanda.com/rest-live-v20/primitives-df/#InstrumentCommission)

🔗 **Source**: [InstrumentCommission](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `commission` | Decimal | ✅ | Commission rate per unit traded |
| `units_traded` | Decimal | ✅ | Units traded to apply commission |
| `minimum_commission` | Decimal | ✅ | Minimum commission amount |

### FinancingDayOfWeek
Daily financing rate details for specific days.

🔗 **OANDA Definition**: [FinancingDayOfWeek](https://developer.oanda.com/rest-live-v20/primitives-df/#FinancingDayOfWeek)

🔗 **Source**: [FinancingDayOfWeek](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `day_of_week` | [DayOfWeek](enum-models.md#dayofweek) | ✅ | Day of the week (SUNDAY through SATURDAY) |
| `days_charged` | int | ✅ | Number of days of financing charged for this day |

### InstrumentFinancing
Financing data for an instrument including long/short rates and daily schedule.

🔗 **OANDA Definition**: [InstrumentFinancing](https://developer.oanda.com/rest-live-v20/instrument-df/#InstrumentFinancing)

🔗 **Source**: [InstrumentFinancing](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `long_rate` | Decimal | ✅ | Financing rate applied to long positions |
| `short_rate` | Decimal | ✅ | Financing rate applied to short positions |
| `financing_days_of_week` | list[[FinancingDayOfWeek](#financingdayofweek)] | ✅ | Daily financing schedule for the week |

### Tag
A tag associated with an entity for categorization.

🔗 **OANDA Definition**: [Tag](https://developer.oanda.com/rest-live-v20/primitives-df/#Tag)

🔗 **Source**: [Tag](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | str | ✅ | Type of the tag |
| `name` | str | ✅ | Name of the tag |

### UnitsAvailableDetails
Units available for both long and short orders on an instrument.

🔗 **OANDA Definition**: [UnitsAvailableDetails](https://developer.oanda.com/rest-live-v20/pricing-df/#UnitsAvailableDetails)

🔗 **Source**: [UnitsAvailableDetails](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `long` | Decimal | ✅ | Long position units availability |
| `short` | Decimal | ✅ | Short position units availability |

### OrderBookBucket
Order book price partition with percentages of open orders on each side.

🔗 **OANDA Definition**: [OrderBookBucket](https://developer.oanda.com/rest-live-v20/instrument-df/#OrderBookBucket)

🔗 **Source**: [OrderBookBucket](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Lowest price (inclusive) covered by this bucket |
| `long_count_percent` | Decimal | ✅ | Percentage of total open orders in the bucket that are long |
| `short_count_percent` | Decimal | ✅ | Percentage of total open orders in the bucket that are short |

### OrderBook
Snapshot of open orders for an instrument, partitioned into price buckets.

🔗 **OANDA Definition**: [OrderBook](https://developer.oanda.com/rest-live-v20/instrument-df/#OrderBook)

🔗 **Source**: [OrderBook](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) \| str | ✅ | Instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Time when order book snapshot was created |
| `unix_time` | [DateTime](system-models.md#type-aliases) \| None |➖ | Snapshot time as a Unix timestamp |
| `price` | [PriceValue](system-models.md#type-aliases) \| None |➖ | Price (midpoint) at the time of the snapshot |
| `bucket_width` | [PriceValue](system-models.md#type-aliases) \| None |➖ | Width of each price bucket |
| `buckets` | list[[OrderBookBucket](#orderbookbucket)] | ➖ | Partitioned order book buckets; only buckets with a non-zero count are returned |

### PositionBookBucket
Position book price partition with percentages of open positions on each side.

🔗 **OANDA Definition**: [PositionBookBucket](https://developer.oanda.com/rest-live-v20/instrument-df/#PositionBookBucket)

🔗 **Source**: [PositionBookBucket](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `price` | [PriceValue](system-models.md#type-aliases) | ✅ | Lowest price (inclusive) covered by this bucket |
| `long_count_percent` | Decimal | ✅ | Percentage of total open positions in the bucket that are long |
| `short_count_percent` | Decimal | ✅ | Percentage of total open positions in the bucket that are short |

### PositionBook
Snapshot of open positions for an instrument, partitioned into price buckets.

🔗 **OANDA Definition**: [PositionBook](https://developer.oanda.com/rest-live-v20/instrument-df/#PositionBook)

🔗 **Source**: [PositionBook](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/pricing.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `instrument` | [InstrumentName](enum-models.md#instrumentname) \| str | ✅ | Instrument identifier |
| `time` | [DateTime](system-models.md#type-aliases) |✅ | Time when position book snapshot was created |
| `unix_time` | [DateTime](system-models.md#type-aliases) \| None |➖ | Snapshot time as a Unix timestamp |
| `price` | [PriceValue](system-models.md#type-aliases) \| None |➖ | Price (midpoint) at the time of the snapshot |
| `bucket_width` | [PriceValue](system-models.md#type-aliases) \| None |➖ | Width of each price bucket |
| `buckets` | list[[PositionBookBucket](#positionbookbucket)] | ➖ | Partitioned position book buckets; only buckets with a non-zero count are returned |

### GuaranteedStopLossOrderEntryData
Details required by clients to add a Guaranteed Stop Loss Order for a specific instrument.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderEntryData](https://developer.oanda.com/rest-live-v20/instrument-df/#GuaranteedStopLossOrderEntryData)

🔗 **Source**: [GuaranteedStopLossOrderEntryData](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `minimum_distance` | Decimal | ✅ | Minimum distance from current price for GSL order |
| `premium` | Decimal | ✅ | Premium charged for guaranteed execution |
| `level_restriction` | [GuaranteedStopLossOrderLevelRestriction](#guaranteedstoplossorderlevelrestriction) \| None | ➖ | Level restrictions for this instrument |

### GuaranteedStopLossOrderLevelRestriction
Volume and price range restrictions for guaranteed stop loss orders.

🔗 **OANDA Definition**: [GuaranteedStopLossOrderLevelRestriction](https://developer.oanda.com/rest-live-v20/instrument-df/#GuaranteedStopLossOrderLevelRestriction)

🔗 **Source**: [GuaranteedStopLossOrderLevelRestriction](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/models/instruments.py)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `volume` | Decimal | ✅ | Volume restriction level |
| `price_range` | Decimal | ✅ | Price range restriction |
