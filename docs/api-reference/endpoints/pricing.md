# Pricing Endpoint

**OANDA Reference**: [Pricing Endpoints](https://developer.oanda.com/rest-live-v20/pricing-ep/)

Real-time pricing data and streaming.

---

## get_pricing

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    # pricing.get_pricing(account_id: AccountID, instruments: list[str], *, since: str | None = None,
    #             include_units_available: bool = True, include_home_conversions: bool = False) -> GetPricingResponse
    # Returns: GetPricingResponse = {"prices": list[ClientPrice], "time": str, "homeConversions": list[HomeConversions] (optional)}

    async with AsyncClient() as client:
        result = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],
            include_units_available=True,
        )
        prices = result["prices"]
        time = result["time"]
        # homeConversions is optional, only present if include_home_conversions=True
        if "homeConversions" in result:
            home_conversions = result["homeConversions"]

asyncio.run(main())
```

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing`

**OANDA Documentation**: [Get Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-pricing)

Get current prices for instruments.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to get prices for |
| `since` | str | ➖ | Only get prices changed since this time (keyword-only) |
| `include_units_available` | bool | ➖ | Include units available info (default: True) (keyword-only) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) (keyword-only) |

**Returns:** `GetPricingResponse` - Dictionary containing prices (`list[ClientPrice]`), time (`str`), and optionally homeConversions (`list[HomeConversions]`)

**Raises:**

- `FiveTwentyError` - API errors

---

## get_pricing_stream

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    # pricing.get_pricing_stream(account_id: AccountID, instruments: list[str], *, snapshot: bool = True,
    #               include_home_conversions: bool = False, stall_timeout: float = 30.0)
    #               -> AsyncIterator[ClientPrice | PricingHeartbeat]

    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],
            snapshot=True
        ):
            print(f"Price update: {price}")

asyncio.run(main())
```

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

**OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream real-time pricing data.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `snapshot` | bool | ➖ | Include initial snapshot (default: True) (keyword-only) |
| `include_home_conversions` | bool | ➖ | Include home currency conversion factors (default: False) (keyword-only) |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls (default: 30.0) (keyword-only) |

**Returns:** `AsyncIterator[ClientPrice | PricingHeartbeat]` - Async iterator yielding ClientPrice or PricingHeartbeat objects

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - On stream timeout or connection issues

---

## get_account_instrument_candles

```python
import asyncio
from datetime import datetime
from fivetwenty import AsyncClient


async def main() -> None:
    # pricing.get_account_instrument_candles(account_id: AccountID, instrument: str, *, price: str = "M",
    #                granularity: str = "S5", count: int | None = None,
    #                from_time: datetime | None = None, to_time: datetime | None = None,
    #                smooth: bool = False, include_first: bool = True,
    #                daily_alignment: int = 17, alignment_timezone: str = "America/New_York",
    #                weekly_alignment: str = "Friday") -> CandlesResponse
    # Returns: CandlesResponse = {"instrument": InstrumentName, "granularity": CandlestickGranularity, "candles": list[Candlestick]}

    async with AsyncClient() as client:
        candles = await client.pricing.get_account_instrument_candles(
            account_id=client.account_id,
            instrument="EUR_USD",
            granularity="H1",
            count=100,
        )
        print(f"Got {len(candles['candles'])} candles for {candles['instrument']}")

asyncio.run(main())
```

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments/{instrument}/candles`

**OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

Get account-specific historical candle data for an instrument.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instrument` | str | ✅ | Instrument to get candles for |
| `price` | str | ➖ | Price type ("M", "B", "A", "BA", "BM", "AM", "BAM") (default: "M") (keyword-only) |
| `granularity` | str | ➖ | Granularity of candles (default: "S5") (keyword-only) |
| `count` | int | ➖ | Number of candles to return (max 5000) (keyword-only) |
| `from_time` | datetime | ➖ | Start time for candle range (keyword-only) |
| `to_time` | datetime | ➖ | End time for candle range (keyword-only) |
| `smooth` | bool | ➖ | Smooth candles (default: False) (keyword-only) |
| `include_first` | bool | ➖ | Include first candle (default: True) (keyword-only) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) (keyword-only) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") (keyword-only) |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") (keyword-only) |

**Returns:** `CandlesResponse` - Dictionary containing instrument, granularity, and list of candlesticks

**Raises:**

- `FiveTwentyError` - API errors
- `ValueError` - If both count and time range are specified

---

## get_latest_candles

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    # pricing.get_latest_candles(account_id: AccountID, candle_specifications: list[str], *,
    #                       units: int = 1, smooth: bool = False,
    #                       daily_alignment: int = 17, alignment_timezone: str = "America/New_York",
    #                       weekly_alignment: str = "Friday") -> LatestCandlesResponse
    # Returns: LatestCandlesResponse = {"latestCandles": list[CandlesResponse]}

    async with AsyncClient() as client:
        result = await client.pricing.get_latest_candles(
            account_id=client.account_id,
            candle_specifications=["EUR_USD:S5:BM", "GBP_USD:M1:BM"],
            units=50
        )
        for candle_data in result["latestCandles"]:
            print(f"{candle_data['instrument']}: {len(candle_data['candles'])} candles")

asyncio.run(main())
```

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/candles/latest`

**OANDA Documentation**: [Get Latest Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-latest-candles)

Get latest candles for multiple instruments.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `candle_specifications` | list[str] | ✅ | List of candle specifications (instrument:granularity:price) |
| `units` | int | ➖ | Number of units for each candle spec (1-5000, default: 1) (keyword-only) |
| `smooth` | bool | ➖ | Smooth candles (default: False) (keyword-only) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) (keyword-only) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") (keyword-only) |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") (keyword-only) |

**Returns:** `LatestCandlesResponse` - Dictionary containing latest candle data for multiple instruments

**Raises:**

- `FiveTwentyError` - API errors
- `ValueError` - On invalid parameters

---

## stream_pricing_with_retries

```python
import asyncio
from fivetwenty import AsyncClient
from fivetwenty.models.streaming import StreamingConfiguration, ReconnectionPolicy, StreamState


async def main() -> None:
    # pricing.stream_pricing_with_retries(account_id: AccountID, instruments: list[str], *,
    #                    snapshot: bool = True, include_home_conversions: bool = False,
    #                    config: StreamingConfiguration | None = None)
    #                    -> AsyncIterator[tuple[ClientPrice | PricingHeartbeat, StreamState]]

    async with AsyncClient() as client:
        config = StreamingConfiguration(
            reconnection_policy=ReconnectionPolicy(max_attempts=5, delay_seconds=2.0)
        )

        async for price_data, state in client.pricing.stream_pricing_with_retries(
            account_id=client.account_id,
            instruments=["EUR_USD", "GBP_USD"],
            config=config
        ):
            if state == StreamState.RECONNECTING:
                print("Connection lost, retrying...")
            elif state == StreamState.CONNECTED:
                print(f"Price update: {price_data}")

asyncio.run(main())
```

🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

**OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream pricing with automatic reconnection and configuration.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `snapshot` | bool | ➖ | Include snapshot of current prices (default: True) (keyword-only) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) (keyword-only) |
| `config` | StreamingConfiguration | ➖ | Streaming configuration with reconnection policy (keyword-only) |

**Returns:** `AsyncIterator[tuple[ClientPrice | PricingHeartbeat, StreamState]]` - Async iterator yielding tuples of (price_data, stream_state)

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - If all retry attempts are exhausted