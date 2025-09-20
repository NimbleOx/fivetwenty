# Pricing Endpoint

📖 **OANDA Reference**: [Pricing API Documentation](https://developer.oanda.com/rest-live-v20/pricing-ep/)

Market data and real-time pricing information for trading instruments.

---

## get
```python
pricing.get(account_id: AccountID, instruments: list[InstrumentName]) -> list[ClientPrice]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing`

📖 **OANDA Documentation**: [Get Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-pricing)

Get current prices for instruments.

**Parameters:**

- `account_id` (AccountID) - Target account
- `instruments` (list[InstrumentName]) - Instruments to price

**Returns:** Current market prices

**Raises:**

- `FiveTwentyError` - API errors or invalid instruments

---

## stream
```python
pricing.stream(account_id: AccountID, instruments: list[InstrumentName]) -> AsyncIterator[ClientPrice | PricingHeartbeat]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

📖 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream real-time prices (async only).

**Parameters:**

- `account_id` (AccountID) - Target account
- `instruments` (list[InstrumentName]) - Instruments to stream

**Yields:** Price updates and heartbeats

**Raises:**

- `FiveTwentyError` - API errors or connection issues

---

## stream_iter
```python
pricing.stream_iter(account_id: AccountID, instruments: list[InstrumentName]) -> Iterator[ClientPrice | PricingHeartbeat]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

📖 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream real-time prices (sync only).

**Parameters:**

- Same as async version

**Yields:** Price updates and heartbeats (blocking iteration)

**Raises:**

- `FiveTwentyError` - API errors

---

## candles
```python
pricing.candles(account_id: AccountID, instrument: InstrumentName, **kwargs) -> CandlestickResponse
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments/{instrument}/candles`

📖 **OANDA Documentation**: [Get Account Candles](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-account-candles)

Get account-specific candlestick data for an instrument.

**Parameters:**

- `account_id` (AccountID) - Target account
- `instrument` (InstrumentName) - Target instrument

**Optional Parameters:**

- `price` (PricingComponent) - Price component ("M", "B", "A", "BA", "MBA")
- `granularity` (CandlestickGranularity) - Timeframe ("S5", "M1", "H1", "D", etc.)
- `count` (int) - Number of candles (max 5000)
- `from_time` (DateTime) - Start time
- `to_time` (DateTime) - End time
- `smooth` (bool) - Apply smoothing to candles
- `include_first` (bool) - Include first candle in time range
- `daily_alignment` (int) - Hour for daily alignment (0-23)
- `alignment_timezone` (str) - Timezone for alignment
- `weekly_alignment` (WeeklyAlignment) - Day for weekly alignment

**Returns:** Candlestick data with account-specific pricing

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## latest_candles
```python
pricing.latest_candles(account_id: AccountID, candle_specifications: list[CandleSpecification], **kwargs) -> LatestCandleResponse
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/candles/latest`

📖 **OANDA Documentation**: [Get Latest Candles](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-latest-candles)

Get latest completed candles for multiple instrument/granularity combinations.

**Parameters:**

- `account_id` (AccountID) - Target account
- `candle_specifications` (list[CandleSpecification]) - List of candle specifications

**Optional Parameters:**

- `units` (Decimal) - Units for volume-weighted average calculation
- `smooth` (bool) - Apply smoothing to candles
- `daily_alignment` (int) - Hour for daily alignment (0-23)
- `alignment_timezone` (str) - Timezone for alignment
- `weekly_alignment` (WeeklyAlignment) - Day for weekly alignment

**Returns:** Latest candles for specified combinations

**Raises:**

- `FiveTwentyError` - API errors or invalid specifications

---