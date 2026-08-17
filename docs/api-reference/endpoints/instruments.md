# Instruments Endpoint

**OANDA Reference**: [Instrument Data Definitions](https://developer.oanda.com/rest-live-v20/instrument-df/)

Instrument-level candlestick data and order/position book snapshots, accessed via `client.instruments`.

> **Note**: OANDA's public documentation no longer publishes the instrument endpoints page, but the endpoints remain live. The orderBook and positionBook endpoints return buckets of `{price, longCountPercent, shortCountPercent}`.

| Method | Purpose |
|--------|---------|
| [get_instrument_candles](#get_instrument_candles) | Candlestick data for an instrument |
| [get_instrument_order_book](#get_instrument_order_book) | Order book snapshot for an instrument |
| [get_instrument_position_book](#get_instrument_position_book) | Position book snapshot for an instrument |

---

## get_instrument_candles

Get candlestick data for a specified instrument.

**OANDA Endpoint**: `GET /v3/instruments/{instrument}/candles`

<!-- code-block: instruments__get_instrument_candles -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get historical candlestick data for an instrument
        candles = await client.instruments.get_instrument_candles(
            "EUR_USD",  # Change to your instrument
            granularity="H1",  # Change to desired granularity (S5, M1, H1, D, etc.)
            count=100,  # Number of candles to retrieve (use count OR from_time/to_time)
        )
        print(f"Got {len(candles['candles'])} candles for {candles['instrument']}")


asyncio.run(main())
```

🔗 **Source**: [instruments.get_instrument_candles](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/instruments.py#L42)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instrument` | InstrumentName \| str | ✅ | Instrument enum or string (e.g., "EUR_USD") |
| `*` | | | **Keyword-only parameters below** |
| `price` | PricingComponent | ➖ | Price component(s) - "M", "B", "A", "BA", "BM", "AM", or "BAM" (default: "M") |
| `granularity` | CandlestickGranularity \| str | ➖ | Candlestick granularity enum or string (default: "S5") |
| `count` | int \| None | ➖ | Number of candlesticks to return (max 5000, conflicts with time range) |
| `from_time` | datetime \| None | ➖ | Start of time range for candlesticks |
| `to_time` | datetime \| None | ➖ | End of time range for candlesticks |
| `smooth` | bool | ➖ | Use previous candle's close as open price (default: False) |
| `include_first` | bool | ➖ | Include candlestick covered by from_time (default: True) |
| `daily_alignment` | int | ➖ | Hour of day for daily-aligned granularities, 0-23 (default: 17) |
| `alignment_timezone` | str | ➖ | Timezone for daily alignment (default: "America/New_York") |
| `weekly_alignment` | str | ➖ | Day of week for weekly alignment (default: "Friday") |

**Returns:** `CandlesResponse` - Dictionary containing instrument, granularity, and candles (`list[Candlestick]`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Instrument not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - If both count and time range are specified

---

## get_instrument_order_book

Get an order book snapshot for an instrument. The order book partitions open orders into price buckets, each with the percentage of long and short orders at that price.

**OANDA Endpoint**: `GET /v3/instruments/{instrument}/orderBook`

<!-- code-block: instruments__get_instrument_order_book -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get the most recent order book snapshot for an instrument
        result = await client.instruments.get_instrument_order_book(
            "EUR_USD",  # Change to your instrument
        )
        book = result["orderBook"]
        print(f"Order book for {book.instrument} at {book.time}")
        # Each bucket has price, longCountPercent, and shortCountPercent
        for bucket in book.buckets:
            if bucket.long_count_percent > Decimal("1.0"):
                print(f"{bucket.price}: {bucket.long_count_percent}% long / {bucket.short_count_percent}% short")


asyncio.run(main())
```

🔗 **Source**: [instruments.get_instrument_order_book](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/instruments.py#L155)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instrument` | InstrumentName \| str | ✅ | Instrument enum or string (e.g., "EUR_USD") |
| `*` | | | **Keyword-only parameters below** |
| `time` | datetime \| None | ➖ | Snapshot time; the most recent snapshot is returned when omitted |

**Returns:** `OrderBookResponse` - Dictionary containing orderBook (`OrderBook`), whose buckets are `{price, longCountPercent, shortCountPercent}` entries

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Instrument or snapshot not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_instrument_position_book

Get a position book snapshot for an instrument. The position book partitions open positions into price buckets, each with the percentage of long and short positions at that price.

**OANDA Endpoint**: `GET /v3/instruments/{instrument}/positionBook`

<!-- code-block: instruments__get_instrument_position_book -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get the most recent position book snapshot for an instrument
        result = await client.instruments.get_instrument_position_book(
            "EUR_USD",  # Change to your instrument
        )
        book = result["positionBook"]
        print(f"Position book for {book.instrument} at {book.time}")
        print(f"Bucket width: {book.bucket_width}, buckets: {len(book.buckets)}")


asyncio.run(main())
```

🔗 **Source**: [instruments.get_instrument_position_book](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/instruments.py#L196)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instrument` | InstrumentName \| str | ✅ | Instrument enum or string (e.g., "EUR_USD") |
| `*` | | | **Keyword-only parameters below** |
| `time` | datetime \| None | ➖ | Snapshot time; the most recent snapshot is returned when omitted |

**Returns:** `PositionBookResponse` - Dictionary containing positionBook (`PositionBook`), whose buckets are `{price, longCountPercent, shortCountPercent}` entries

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Instrument or snapshot not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)
