#!/usr/bin/env python3
"""
Pricing and Candlestick Data Example

Demonstrates market data operations including:
- Real-time pricing
- Price streaming
- Candlestick data retrieval
- Historical data analysis
- Instrument information
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity, InstrumentName


async def main() -> None:
    """Pricing and candlestick data operations example."""

    async with AsyncClient() as client:
        # Section 1: Get current pricing
        print("\n=== 1. Current Pricing ===")

        instruments = [InstrumentName.EUR_USD, InstrumentName.GBP_USD, InstrumentName.USD_JPY]

        print(f"\nFetching current prices for {len(instruments)} instruments...")

        pricing_response = await client.pricing.get_pricing(account_id=client.account_id, instruments=instruments)

        prices = pricing_response["prices"]

        for price in prices:
            if price.bids and price.asks:
                bid = price.bids[0].price
                ask = price.asks[0].price
                spread = Decimal(ask) - Decimal(bid)

                print(f"\n{price.instrument}:")
                print(f"  Bid: {bid} (liquidity: {price.bids[0].liquidity})")
                print(f"  Ask: {ask} (liquidity: {price.asks[0].liquidity})")
                print(f"  Spread: {spread:.5f}")
                print(f"  Time: {price.time}")
                print(f"  Tradeable: {price.tradeable}")
            else:
                print(f"\n{price.instrument}:")
                print(f"  Status: {price.status}")
                print(f"  Tradeable: {price.tradeable}")

        # Section 2: Stream real-time prices
        print("\n=== 2. Real-Time Price Streaming ===")

        print("\n💡 Example: Stream EUR/USD prices for 10 seconds")
        print("   (Code shown but not executed in this demo)\n")

        print("""
async def stream_prices():
    stream_count = 0
    start_time = asyncio.get_event_loop().time()

    async for event in client.pricing.get_pricing_stream(
        account_id=client.account_id,
        instruments=[InstrumentName.EUR_USD]
    ):
        if event.type == "PRICE":
            stream_count += 1
            print(f"Price update #{stream_count}: {event.bids[0].price}/{event.asks[0].price}")
        elif event.type == "HEARTBEAT":
            print(f"Heartbeat at {event.time}")

        # Stop after 10 seconds
        if asyncio.get_event_loop().time() - start_time > 10:
            break
        """)

        # Section 3: Stream with automatic reconnection
        print("\n=== 3. Streaming with Reconnection ===")

        print("\nRobust streaming with automatic reconnection:")
        print("  - Detects stalled connections")
        print("  - Automatic reconnection with exponential backoff")
        print("  - Configurable timeout and retry policies")

        print("\n💡 Example code:\n")
        print("""
from fivetwenty.models import ReconnectionPolicy, StreamingConfiguration

config = StreamingConfiguration(
    stall_timeout=10.0,  # Detect stalls after 10 seconds
    heartbeat_interval=5.0
)

policy = ReconnectionPolicy(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=30.0,
    backoff_multiplier=2.0
)

async for event in client.pricing.stream_pricing_with_retries(
    account_id=client.account_id,
    instruments=[InstrumentName.EUR_USD],
    config=config,
    policy=policy
):
    # Handle price events with automatic reconnection
    print(f"Price: {event.bids[0].price}")
        """)

        # Section 4: Get candlestick data
        print("\n=== 4. Historical Candlestick Data ===")

        print("\nFetching M5 (5-minute) candles for EUR/USD...")

        candles_response = await client.pricing.get_account_instrument_candles(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            granularity=CandlestickGranularity.M5,
            count=20,  # Last 20 candles
        )

        candles = candles_response.get("candles", [])

        print(f"Retrieved {len(candles)} candles:")
        for i, candle in enumerate(candles[-5:], start=len(candles) - 4):  # Show last 5
            if candle.mid:
                print(f"\n  Candle {i}:")
                print(f"    Time: {candle.time}")
                print(f"    O: {candle.mid.o}")
                print(f"    H: {candle.mid.h}")
                print(f"    L: {candle.mid.l}")
                print(f"    C: {candle.mid.c}")
                print(f"    Volume: {candle.volume}")
                print(f"    Complete: {candle.complete}")

        # Section 5: Get latest candles
        print("\n=== 5. Latest Candles ===")

        print("\nFetching latest H1 (1-hour) candles for multiple instruments...")

        latest_response = await client.pricing.get_latest_candles(
            account_id=client.account_id,
            candleSpecifications=[
                f"{InstrumentName.EUR_USD}:{CandlestickGranularity.H1}",
                f"{InstrumentName.GBP_USD}:{CandlestickGranularity.H1}",
            ],
        )

        latest_candles = latest_response.get("latestCandles", [])

        for candle_data in latest_candles:
            instrument = candle_data.get("instrument")
            candles_list = candle_data.get("candles", [])

            if candles_list:
                latest = candles_list[-1]
                print(f"\n{instrument} latest H1:")
                if latest.mid:
                    print(f"  OHLC: {latest.mid.o} / {latest.mid.h} / {latest.mid.l} / {latest.mid.c}")
                    print(f"  Volume: {latest.volume}")
                    print(f"  Time: {latest.time}")

        # Section 6: Get instrument candles (generic)
        print("\n=== 6. Instrument Candles (Generic) ===")

        print("\nUsing generic instruments endpoint...")

        generic_candles = await client.instruments.get_instrument_candles(
            instrument=InstrumentName.EUR_USD,
            granularity=CandlestickGranularity.D,  # Daily candles
            count=10,
        )

        daily_candles = generic_candles.get("candles", [])

        print("\nLast 5 daily candles for EUR/USD:")
        for candle in daily_candles[-5:]:
            if candle.mid:
                body_size = abs(Decimal(candle.mid.c) - Decimal(candle.mid.o))
                print(f"  {candle.time[:10]}: O={candle.mid.o} H={candle.mid.h} L={candle.mid.l} C={candle.mid.c} (Body={body_size:.5f})")

        # Section 7: Analyze different time frames
        print("\n=== 7. Multi-Timeframe Analysis ===")

        print("\nFetching multiple timeframes for EUR/USD...")

        timeframes = [
            (CandlestickGranularity.M5, 20),
            (CandlestickGranularity.M15, 20),
            (CandlestickGranularity.H1, 24),
            (CandlestickGranularity.D, 10),
        ]

        for granularity, count in timeframes:
            tf_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=granularity, count=count)

            tf_candles = tf_response.get("candles", [])
            if tf_candles and tf_candles[-1].mid:
                latest_candle = tf_candles[-1]
                print(f"\n{granularity.value} - Latest close: {latest_candle.mid.c} ({len(tf_candles)} candles)")

        # Section 8: Candlestick pattern analysis
        print("\n=== 8. Candlestick Patterns ===")

        print("\nAnalyzing recent M5 candles for patterns...")

        analysis_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.M5, count=50)

        analysis_candles = analysis_response.get("candles", [])

        # Simple pattern detection
        doji_count = 0
        hammer_count = 0
        body_sizes = []

        for candle in analysis_candles:
            if candle.mid and candle.complete:
                open_price = Decimal(candle.mid.o)
                high = Decimal(candle.mid.h)
                low = Decimal(candle.mid.l)
                close = Decimal(candle.mid.c)

                body = abs(close - open_price)
                total_range = high - low
                body_sizes.append(body)

                # Doji: very small body relative to range
                if total_range > 0 and body / total_range < Decimal("0.1"):
                    doji_count += 1

                # Hammer: small body at top, long lower wick
                lower_wick = min(open_price, close) - low
                if total_range > 0:
                    if lower_wick / total_range > Decimal("0.6") and body / total_range < Decimal("0.3"):
                        hammer_count += 1

        if body_sizes:
            avg_body = sum(body_sizes) / len(body_sizes)
            print(f"\nPattern Analysis (last {len(analysis_candles)} candles):")
            print(f"  Doji candles: {doji_count}")
            print(f"  Hammer candles: {hammer_count}")
            print(f"  Average body size: {avg_body:.5f}")

        # Section 9: Calculate technical indicators
        print("\n=== 9. Technical Indicators ===")

        print("\nCalculating simple indicators from candle data...")

        # Get enough data for calculations
        indicator_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.H1, count=50)

        indicator_candles = indicator_response.get("candles", [])
        closes = [Decimal(c.mid.c) for c in indicator_candles if c.mid and c.complete]

        if len(closes) >= 20:
            # Simple Moving Average (SMA)
            sma_20 = sum(closes[-20:]) / 20
            print(f"\n20-period SMA: {sma_20:.5f}")

            # Calculate ATR (Average True Range) - simplified
            true_ranges = []
            for i in range(1, len(indicator_candles)):
                if indicator_candles[i].mid and indicator_candles[i - 1].mid:
                    high = Decimal(indicator_candles[i].mid.h)
                    low = Decimal(indicator_candles[i].mid.l)
                    prev_close = Decimal(indicator_candles[i - 1].mid.c)

                    tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                    true_ranges.append(tr)

            if len(true_ranges) >= 14:
                atr_14 = sum(true_ranges[-14:]) / 14
                print(f"14-period ATR: {atr_14:.5f}")

            # Simple Bollinger Bands
            if len(closes) >= 20:
                sma = sum(closes[-20:]) / 20
                variance = sum((c - sma) ** 2 for c in closes[-20:]) / 20
                std_dev = variance ** Decimal("0.5")
                upper_band = sma + (std_dev * 2)
                lower_band = sma - (std_dev * 2)

                print("\nBollinger Bands (20, 2):")
                print(f"  Upper: {upper_band:.5f}")
                print(f"  Middle: {sma:.5f}")
                print(f"  Lower: {lower_band:.5f}")

        # Section 10: Price vs candle data comparison
        print("\n=== 10. Price vs Candle Data ===")

        # Get current price
        current_pricing = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])
        current_price = current_pricing["prices"][0]
        current_mid = (Decimal(current_price.bids[0].price) + Decimal(current_price.asks[0].price)) / 2

        # Get latest M1 candle
        m1_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.M1, count=2)

        m1_candles = m1_response.get("candles", [])

        if m1_candles:
            latest_m1 = m1_candles[-1]

            print("\nEUR/USD Current State:")
            print(f"  Live Price (mid): {current_mid:.5f}")
            print(f"  Live Time: {current_price.time}")

            if latest_m1.mid:
                print("\n  Latest M1 Candle:")
                print(f"    Open: {latest_m1.mid.o}")
                print(f"    High: {latest_m1.mid.h}")
                print(f"    Low: {latest_m1.mid.l}")
                print(f"    Close: {latest_m1.mid.c}")
                print(f"    Complete: {latest_m1.complete}")
                print(f"    Time: {latest_m1.time}")

                if not latest_m1.complete:
                    print("\n  ⚠️  Candle in formation - close price is current market price")
                    candle_open = Decimal(latest_m1.mid.o)
                    movement = current_mid - candle_open
                    print(f"  Movement this candle: {movement:.5f} pips")

    print("\n✅ Pricing and candles example completed!")


if __name__ == "__main__":
    asyncio.run(main())
