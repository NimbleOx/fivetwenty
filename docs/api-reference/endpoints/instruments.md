# Instruments Endpoint

**OANDA Reference**: [Instrument Endpoints](https://developer.oanda.com/rest-live-v20/instrument-ep/)

Instrument information and historical data.

---

## candles
```python
import asyncio

from fivetwenty import AsyncClient
from fivetwenty.endpoints.instruments import CandlesResponse
from fivetwenty.models import CandlestickGranularity


async def main() -> None:
    # instruments.get_instrument_candles(instrument: InstrumentName | str, *, price: str = "M",
    #                    granularity: CandlestickGranularity, count: int | None = None,
    #                    from_time: datetime | None = None, to_time: datetime | None = None,
    #                    smooth: bool = False, include_first: bool = True,
    #                    daily_alignment: int = 17, alignment_timezone: str = "America/New_York",
    #                    weekly_alignment: str = "Friday") -> CandlesResponse
    # Returns: TypedDict with {"instrument": InstrumentName, "granularity": CandlestickGranularity, "candles": list[Candlestick]}

    async with AsyncClient() as client:
        # Get 100 H1 candles for EUR_USD
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
🔗 **OANDA Endpoint**: `GET /v3/instruments/{instrument}/candles`

**OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

Get historical candle data for an instrument.

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

- `FiveTwentyError` - API errors
- `ValueError` - If both count and time range are specified, or count exceeds 5000