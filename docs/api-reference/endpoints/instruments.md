# Instruments Endpoint

📖 **OANDA Reference**: [Instrument Endpoints](https://developer.oanda.com/rest-live-v20/instrument-ep/)

Instrument information and historical data.

---

## candles
```python
import asyncio
from typing import Any, Dict

from fivetwenty import AsyncClient


async def main() -> None:
    # instruments.get_instrument_candles(instrument: str, price: str = "M", granularity: str = "S5",
    #                    count: int | None = None, from_time: str | None = None,
    #                    to_time: str | None = None, smooth: bool = False,
    #                    include_first: bool = True, daily_alignment: int = 17,
    #                    alignment_timezone: str = "America/New_York",
    #                    weekly_alignment: str = "Friday") -> dict[str, Any]

    async with AsyncClient(token="demo-token", account_id="your-account-id") as client:
        # Example usage:
        candles = await client.instruments.get_instrument_candles(
            instrument="EUR_USD",
            granularity="H1",
            count=100,
        )
        print(f"Retrieved {len(candles.get('candles', []))} candles")


if __name__ == "__main__":
    asyncio.run(main())
```
🔗 **OANDA Endpoint**: `GET /v3/instruments/{instrument}/candles`

📖 **OANDA Documentation**: [Get Candles](https://developer.oanda.com/rest-live-v20/instrument-ep/#get-candles)

Get historical candle data for an instrument.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
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