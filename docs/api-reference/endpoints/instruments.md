# Instruments Endpoint

**OANDA Reference**: [Instrument Endpoints](https://developer.oanda.com/rest-live-v20/instrument-ep/)

Instrument information and historical data.

---

## get_instrument_candles

Get historical candle data for an instrument.

**OANDA Endpoint**: `GET /v3/instruments/{instrument}/candles`

<!-- code-block: instruments__get_instrument_candles -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.endpoints.instruments import CandlesResponse
from fivetwenty.models import CandlestickGranularity

load_dotenv()


async def main() -> None:
    async with AsyncClient() as client:
        # Get historical hourly candle data for EUR_USD
        result: CandlesResponse = await client.instruments.get_instrument_candles(
            instrument="EUR_USD",
            granularity=CandlestickGranularity.H1,
            count=100,
        )
        candles = result["candles"]
        print(f"Retrieved {len(candles)} candles for {result['instrument']}")


if __name__ == "__main__":
    asyncio.run(main())
```

🔗 **OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

🔗 **Source**: [instruments.get_instrument_candles](https://github.com/NimbleOx/fivetwenty/blob/main/fivetwenty/endpoints/instruments.py)

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instrument` | InstrumentName \| str | ✅ | Instrument to get candles for |
| `price` | str | ➖ | Price type ("M", "B", "A", "BA", "BM", "AM", "BAM") (default: "M") (keyword-only) |
| `granularity` | CandlestickGranularity | ✅ | Granularity enum (e.g., CandlestickGranularity.H1) (keyword-only) |
| `count` | int \| None | ➖ | Number of candles to return (max 5000, conflicts with time range) (keyword-only) |
| `from_time` | datetime \| None | ➖ | Start time for candle range (keyword-only) |
| `to_time` | datetime \| None | ➖ | End time for candle range (keyword-only) |
| `smooth` | bool | ➖ | Smooth candles (default: False) (keyword-only) |
| `include_first` | bool | ➖ | Include first candle (default: True) (keyword-only) |
| `daily_alignment` | int | ➖ | Daily alignment hour (0-23, default: 17) (keyword-only) |
| `alignment_timezone` | str | ➖ | Timezone for alignment (default: "America/New_York") (keyword-only) |
| `weekly_alignment` | str | ➖ | Weekly alignment day (default: "Friday") (keyword-only) |

**Returns:** `CandlesResponse` TypedDict containing:

- `instrument`: InstrumentName enum
- `granularity`: CandlestickGranularity enum
- `candles`: list of Candlestick models

**Raises:**

`FiveTwentyError` - API errors:

  - 401/403: Authentication failed (check `e.is_authentication_error`)
  - 404: Instrument not found (check `e.is_not_found`)
  - 429: Rate limit exceeded (check `e.is_rate_limited`, use `e.retry_after`)
  - 400: Invalid parameters (check `e.is_validation_error`)

- `ValueError` - If both count and time range are specified, or count exceeds 5000