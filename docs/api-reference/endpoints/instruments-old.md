# Instruments Endpoint

📖 **OANDA Reference**: [Instruments API Documentation](https://developer.oanda.com/rest-live-v20/instrument-ep/)

Instrument specifications and historical data access.

---

## get_all
```python
instruments.get_all(account_id: AccountID) -> list[Instrument]
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments`

📖 **OANDA Documentation**: [Get Account Instruments](https://developer.oanda.com/rest-live-v20/account-ep/#get-account-instruments)

Get all tradeable instruments.

**Parameters:**

- `account_id` (AccountID) - Target account

**Returns:** List of instrument specifications

**Raises:**

- `FiveTwentyError` - API errors

---

## candles
```python
instruments.candles(instrument: InstrumentName, **kwargs) -> CandlestickResponse
```
🔗 **OANDA Endpoint**: `GET /v3/instruments/{instrument}/candles`

📖 **OANDA Documentation**: [Get Instrument Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-instrument-candles)

Get historical candlestick data.

**Parameters:**

- `instrument` (InstrumentName) - Target instrument

**Optional Parameters:**

- `granularity` (CandlestickGranularity) - Timeframe ("M1", "H1", "D", etc.)
- `count` (int) - Number of candles (max 5000)
- `from_time` (DateTime) - Start time
- `to_time` (DateTime) - End time
- `price` (str) - Price type ("M", "B", "A", "BA", "MBA")
- `include_first` (bool) - Include first candle
- `daily_alignment` (int) - Daily alignment hour
- `alignment_timezone` (str) - Alignment timezone
- `weekly_alignment` (WeeklyAlignment) - Weekly alignment

**Returns:** Candlestick response with OHLC data

**Raises:**

- `FiveTwentyError` - API errors or invalid parameters

---

## order_book
```python
instruments.order_book(instrument: InstrumentName, time: DateTime = None) -> OrderBook
```
🔗 **OANDA Endpoint**: `GET /v3/instruments/{instrument}/orderBook`

📖 **OANDA Documentation**: [Get Order Book](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-order-book)

Get order book snapshot.

**Parameters:**

- `instrument` (InstrumentName) - Target instrument
- `time` (DateTime, optional) - Snapshot time (default: current)

**Returns:** Order book with bid/ask levels

**Raises:**

- `FiveTwentyError` - API errors

---