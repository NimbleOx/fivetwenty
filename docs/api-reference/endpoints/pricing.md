# Pricing Endpoint

📖 **OANDA Reference**: [Pricing Endpoints](https://developer.oanda.com/rest-live-v20/pricing-ep/)

Real-time pricing data and streaming.

---

## get_pricing
<!-- fragment: Demo get_pricing with unused imports and module attribute access issues -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration
from typing import Any


async def main() -> None:
    # pricing.get_pricing(account_id: AccountID, instruments: list[str], since: str | None = None,
    #             include_units_available: bool = True, include_home_conversions: bool = False) -> dict[str, Any]

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        prices = await client.pricing.get_pricing(
            account_id="123-456-789",
            instruments=["EUR_USD", "GBP_USD"],
            include_units_available=True,
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing`

📖 **OANDA Documentation**: [Get Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#get-pricing)

Get current prices for instruments.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to get prices for |
| `since` | str | ➖ | Only get prices changed since this time |
| `include_units_available` | bool | ➖ | Include units available info (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) |

**Returns:** Pricing information

**Raises:**

- `FiveTwentyError` - API errors

---

## get_pricing_stream
<!-- fragment: Demo get_pricing_stream with module attribute access patterns -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration


async def main() -> None:
    # pricing.get_pricing_stream(account_id: AccountID, instruments: list[str], snapshot: bool = True,
    #               include_home_conversions: bool = False, stall_timeout: float = 30.0)
    #               -> AsyncIterator[ClientPrice | PricingHeartbeat]

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        async for price in client.pricing.get_pricing_stream(
            account_id="123-456-789",
            instruments=["EUR_USD", "GBP_USD"],
            snapshot=True
        ):
            print(f"Price update: {price}")

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

📖 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream real-time pricing data.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `snapshot` | bool | ➖ | Include initial snapshot (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversion factors (default: False) |
| `stall_timeout` | float | ➖ | Timeout for detecting stream stalls (default: 30.0) |

**Returns:** AsyncIterator yielding ClientPrice or PricingHeartbeat objects

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - On stream timeout or connection issues

---

## get_instrument_candles
<!-- fragment: Demo get_instrument_candles with unused imports and call argument issues -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration
from typing import Any


async def main() -> None:
    # pricing.get_latest_candles(account_id: AccountID, instrument: str, price: str = "M",
    #                granularity: str = "S5", count: int | None = None,
    #                from_time: str | None = None, to_time: str | None = None,
    #                smooth: bool = False, include_first: bool = True,
    #                daily_alignment: int = 17, alignment_timezone: str = "America/New_York",
    #                weekly_alignment: str = "Friday") -> dict[str, Any]

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        candles = await client.pricing.get_latest_candles(
            account_id="123-456-789",
            instrument="EUR_USD",
            granularity="H1",
            count=100,
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/instruments/{instrument}/candles`

📖 **OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

Get historical candle data for an instrument.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instrument` | str | ✅ | Instrument to get candles for |
| `price` | str | ➖ | Price type ("M", "B", "A", "BA", "MB", "AM") (default: "M") |
| `granularity` | str | ➖ | Granularity of candles (default: "S5") |
| `count` | int | ➖ | Number of candles to return |
| `from_time` | str | ➖ | Start time for candle range |
| `to_time` | str | ➖ | End time for candle range |
| `smooth` | bool | ➖ | Smooth candles (default: False) |
| `include_first` | bool | ➖ | Include first candle (default: True) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") |

**Returns:** Dictionary containing candle data

**Raises:**

- `FiveTwentyError` - API errors

---

## get_latest_candles
<!-- fragment: Demo get_latest_candles with unused imports and unused variable patterns -->
```python
import asyncio
from fivetwenty import AsyncClient, Configuration
from typing import Any


async def main() -> None:
    # pricing.get_latest_candles(account_id: AccountID, candle_specifications: list[str],
    #                       units: int = 1, smooth: bool = False,
    #                       daily_alignment: int = 17, alignment_timezone: str = "America/New_York",
    #                       weekly_alignment: str = "Friday") -> dict[str, Any]

    config = Configuration(token="your-token", environment="practice")
    async with AsyncClient(config=config) as client:
        # Example usage:
        candles = await client.pricing.get_latest_candles(
            account_id="123-456-789",
            candle_specifications=["EUR_USD:S5:BM", "GBP_USD:M1:BM"],
            units=50
        )

asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/candles/latest`

📖 **OANDA Documentation**: [Get Latest Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-latest-candles)

Get latest candles for multiple instruments.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `candle_specifications` | list[str] | ✅ | List of candle specifications (instrument:granularity:price) |
| `units` | int | ➖ | Units for calculating volume-based candles (default: 1) |
| `smooth` | bool | ➖ | Smooth candles (default: False) |
| `daily_alignment` | int | ➖ | Daily alignment hour (default: 17) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") |

**Returns:** Dictionary containing latest candle data for multiple instruments

**Raises:**

- `FiveTwentyError` - API errors

---

## get_pricing_stream_iter
<!-- fragment: Demo get_pricing_stream_iter with module attribute access patterns -->
```python
from fivetwenty import Client, Configuration


def main() -> None:
    # pricing.get_pricing_stream(account_id: AccountID, instruments: list[str],
    #                    snapshot: bool = True, include_home_conversions: bool = False,
    #                    config: StreamingConfiguration | None = None)
    #                    -> AsyncIterator[ClientPrice | PricingHeartbeat]

    config = Configuration(token="your-token", environment="practice")
    with Client(config=config) as client:
        # Example usage:
        for price in client.pricing.get_pricing_stream(
            account_id="123-456-789",
            instruments=["EUR_USD", "GBP_USD"],
        ):
            print(f"Price update: {price}")

main()
```
🔗 **OANDA Endpoint**: `GET /v3/accounts/{accountID}/pricing/stream`

📖 **OANDA Documentation**: [Stream Pricing](https://developer.oanda.com/rest-live-v20/pricing-ep/#stream-pricing)

Stream pricing with automatic reconnection and configuration.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account_id` | AccountID | ✅ | Account ID |
| `instruments` | list[str] | ✅ | List of instruments to stream |
| `snapshot` | bool | ➖ | Include snapshot of current prices (default: True) |
| `include_home_conversions` | bool | ➖ | Include home currency conversions (default: False) |
| `config` | StreamingConfiguration | ➖ | Streaming configuration with reconnection policy |

**Returns:** AsyncIterator yielding ClientPrice or PricingHeartbeat objects

**Raises:**

- `FiveTwentyError` - API errors
- `StreamStall` - On stream timeout or connection issues