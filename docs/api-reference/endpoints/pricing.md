# Pricing Endpoint

**OANDA Reference**: [Pricing Endpoints](https://developer.oanda.com/rest-live-v20/pricing-ep/)

Real-time pricing data and streaming.

---

## get_pricing

Get current prices for instruments.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing`

<!-- code-block: pricing__get_pricing -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get current pricing for multiple instruments
        result = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],  # Change to your instruments
            include_units_available=True,
        )
        print(f"Got {len(result['prices'])} prices at {result['time']}")
        # homeConversions is optional, only present if include_home_conversions=True
        if "homeConversions" in result:
            print(f"Got {len(result['homeConversions'])} home conversions")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-pricing)

🔗 **FiveTwenty SDK**: [pricing.get_pricing](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/pricing.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to get prices for |
| `*` | | | **Keyword-only parameters below** |
| `since` | str \| None | ➖ | Only get prices changed since this time |
| `include_units_available` | bool | ➖ | Include units available info (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) |

**Returns:** `GetPricingResponse` - Dictionary containing prices (`list[ClientPrice]`), time (`str`), and optionally homeConversions (`list[HomeConversions]`)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

---

## get_pricing_stream

Stream real-time pricing data.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

<!-- code-block: pricing__get_pricing_stream -->
```python
import asyncio
from contextlib import aclosing

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Stream real-time pricing data for instruments
        count = 0
        stream = client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],  # Change to your instruments
            snapshot=True,
        )
        async with aclosing(stream):  # type: ignore[type-var]
            async for price in stream:
                print(f"Price update: {price}")
                count += 1
                if count >= 5:  # Stop after 5 updates for testing
                    break


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

🔗 **FiveTwenty SDK**: [pricing.get_pricing_stream](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/pricing.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `*` | | | **Keyword-only parameters below** |
| `snapshot` | bool | ➖ | Include initial snapshot (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversion factors (default: False) |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls in seconds (default: 30.0) |

**Returns:** `AsyncIterator[ClientPrice | PricingHeartbeat]` - Async iterator yielding ClientPrice or PricingHeartbeat objects

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

`StreamStall` - On stream timeout or connection issues

---

## get_account_instrument_candles

Get account-specific historical candle data for an instrument.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments/{instrument}/candles`

<!-- code-block: pricing__get_account_instrument_candles -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get historical candlestick data for an instrument
        candles = await client.pricing.get_account_instrument_candles(
            account_id=client.account_id,
            instrument="EUR_USD",  # Change to your instrument
            granularity="H1",  # Change to desired granularity (S5, M1, H1, D, etc.)
            count=100,  # Number of candles to retrieve (use count OR from_time/to_time)
        )
        print(f"Got {len(candles['candles'])} candles for {candles['instrument']}")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

🔗 **FiveTwenty SDK**: [pricing.get_account_instrument_candles](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/pricing.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instrument` | str | ✅ | Instrument to get candles for |
| `*` | | | **Keyword-only parameters below** |
| `price` | str | ➖ | Price type ("M", "B", "A", "BA", "BM", "AM", "BAM") (default: "M") |
| `granularity` | str | ➖ | Granularity of candles (default: "S5") |
| `count` | int \| None | ➖ | Number of candles to return (max 5000) |
| `from_time` | datetime \| None | ➖ | Start time for candle range |
| `to_time` | datetime \| None | ➖ | End time for candle range |
| `smooth` | bool | ➖ | Smooth candles (default: False) |
| `include_first` | bool | ➖ | Include first candle (default: True, only used with from_time) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") |

**Returns:** `CandlesResponse` - Dictionary containing instrument, granularity, and list of candlesticks

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Instrument or account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - If both count and time range are specified

---

## get_latest_candles

Get latest candles for multiple instruments.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/candles/latest`

<!-- code-block: pricing__get_latest_candles -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get latest candles for multiple instrument/granularity combinations
        result = await client.pricing.get_latest_candles(
            account_id=client.account_id,
            # Format: instrument:granularity:price_type
            candle_specifications=["EUR_USD:S5:BM", "GBP_USD:M1:BM"],
            units=50,  # Number of candles per specification
        )
        for candle_data in result["latestCandles"]:
            print(f"{candle_data['instrument']}: {len(candle_data['candles'])} candles")


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Latest Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-latest-candles)

🔗 **FiveTwenty SDK**: [pricing.get_latest_candles](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/pricing.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `candle_specifications` | list[str] | ✅ | List of candle specifications (instrument:granularity:price) |
| `*` | | | **Keyword-only parameters below** |
| `units` | int | ➖ | Number of units for each candle spec (1-5000, default: 1) |
| `smooth` | bool | ➖ | Smooth candles (default: False) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") |

**Returns:** `LatestCandlesResponse` - Dictionary containing latest candle data for multiple instruments

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

`ValueError` - On invalid parameters

---

## stream_pricing_with_retries

Stream pricing with automatic reconnection and configuration.

**OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

<!-- code-block: pricing__stream_pricing_with_retries -->
```python
import asyncio
from contextlib import aclosing

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models.streaming import (
    ReconnectionPolicy,
    StreamingConfiguration,
    StreamState,
)

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Configure automatic reconnection for robust streaming
        config = StreamingConfiguration(
            reconnection_policy=ReconnectionPolicy(
                max_attempts=5,
                delay_seconds=2.0,  # Retry up to 5 times with 2s delay
            )
        )

        # Stream pricing with automatic reconnection on failures
        count = 0
        stream = client.pricing.stream_pricing_with_retries(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],  # Change to your instruments
            config=config,
        )
        async with aclosing(stream):  # type: ignore[type-var]
            async for price_data, state in stream:
                if state == StreamState.RECONNECTING:
                    print("Connection lost, retrying...")
                elif state == StreamState.CONNECTED:
                    print(f"Price update: {price_data}")
                    count += 1
                    if count >= 5:  # Stop after 5 updates for testing
                        break


asyncio.run(main())
```

🔗 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

🔗 **FiveTwenty SDK**: [pricing.stream_pricing_with_retries](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/pricing.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `*` | | | **Keyword-only parameters below** |
| `snapshot` | bool | ➖ | Include snapshot of current prices (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) |
| `config` | StreamingConfiguration \| None | ➖ | Streaming configuration with reconnection policy |

**Returns:** `AsyncIterator[tuple[ClientPrice | PricingHeartbeat, StreamState]]` - Async iterator yielding tuples of (price_data, stream_state)

**Raises:**

`FiveTwentyError` - API errors:

- 400: Invalid request parameters (check `e.is_bad_request`)
- 401/403: Authentication failed (check `e.is_authentication_error`)
- 404: Account not found (check `e.is_not_found`)
- 429: Rate limit exceeded (check `e.is_rate_limited`)

`StreamStall` - If all retry attempts are exhausted