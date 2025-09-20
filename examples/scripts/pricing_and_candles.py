"""
OANDA Pricing and Candle Data Example

This example demonstrates pricing operations including:
- Real-time price streaming
- Historical candle data retrieval
- Latest candle snapshots
- Various time frames and price types
"""

import asyncio
import os
from datetime import datetime, timedelta, timezone
from typing import Any, cast

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID


async def main() -> None:
    """Demonstrate pricing and candle data operations."""

    # Get token from environment
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("Please set FIVETWENTY_OANDA_TOKEN environment variable")
        return

    # Use practice environment for safety
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get account ID (use first available account)
        accounts = await client.accounts.get_accounts()
        if not accounts:
            print("No accounts available")
            return

        account_id = AccountID(accounts[0].id)
        print(f"Using account: {account_id}")
        print("=" * 70)

        # 1. Get current pricing
        print("1. Current Pricing Information:")
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]

        pricing = await client.pricing.get_pricing(account_id, instruments, include_units_available=True, include_home_conversions=True)

        prices = pricing.get("prices", [])
        for price in prices[:3]:  # Show first 3
            instrument = price.get("instrument", "N/A")
            bid = price.get("bids", [{}])[0].get("price", "N/A")
            ask = price.get("asks", [{}])[0].get("price", "N/A")
            spread = float(ask) - float(bid) if bid != "N/A" and ask != "N/A" else 0

            print(f"   {instrument}:")
            print(f"     Bid: {bid}")
            print(f"     Ask: {ask}")
            print(f"     Spread: {spread:.5f}")

            # Show tradeable units if available
            tradeable = price.get("tradeableUnits", "N/A")
            if tradeable != "N/A":
                print(f"     Tradeable Units: {tradeable}")
            print()

        # 2. Real-time price streaming demonstration
        print("2. Real-time Price Streaming:")
        print("   NOTE: This demonstrates the streaming pattern")

        try:
            # In a real application, this would stream continuously
            async for _price_update in client.pricing.get_pricing_stream(account_id, ["EUR_USD"], snapshot=True):
                # Just show we can access the stream (break after first item)
                print("   Stream established (demo response received)")
                print("   In production, this would yield price updates continuously")
                break
        except Exception as e:
            print(f"   Stream demo: {e}")

        print("\n   Example streaming pattern:")
        print("""
   async for price_update in client.pricing.get_pricing_stream(account_id, ["EUR_USD"]):
       if hasattr(price_update, 'bids'):
           print(f"EUR/USD: {price_update.bids[0].price}")
        """)

        # 3. Historical candle data
        print("3. Historical Candle Data:")

        # Get hourly candles for EUR/USD
        print("   a) EUR/USD Hourly Candles (last 24 hours):")
        candles = await client.instruments.get_instrument_candles(
            "EUR_USD",
            granularity="H1",
            count=24,
            price="M",  # Mid prices
        )

        candle_data = candles.get("candles", [])
        if candle_data:
            print(f"      Retrieved {len(candle_data)} candles")

            # Show first and last candle
            first_candle = candle_data[0]
            last_candle = candle_data[-1]

            print(f"      First: {first_candle.get('time', 'N/A')[:19]}")
            first_mid = first_candle.get("mid", {})
            print(f"        O:{first_mid.get('o', 'N/A')} H:{first_mid.get('h', 'N/A')} L:{first_mid.get('l', 'N/A')} C:{first_mid.get('c', 'N/A')}")

            print(f"      Last:  {last_candle.get('time', 'N/A')[:19]}")
            last_mid = last_candle.get("mid", {})
            print(f"        O:{last_mid.get('o', 'N/A')} H:{last_mid.get('h', 'N/A')} L:{last_mid.get('l', 'N/A')} C:{last_mid.get('c', 'N/A')}")

        # Account-specific candles demonstration
        print("\n   b) Account-Specific Candles (GBP/USD M30, last 12 hours):")
        print("      (Account-specific endpoint may return different data based on account permissions)")
        account_candles = await client.pricing.get_account_instrument_candles(
            account_id,
            "GBP_USD",
            granularity="M30",
            count=24,  # Last 12 hours of M30 candles
            price="BA",  # Bid and Ask prices
        )

        account_candle_data = account_candles.get("candles", [])
        if account_candle_data:
            print(f"      Retrieved {len(account_candle_data)} account-specific candles")

            # Show sample candle with bid/ask data
            sample_candle = account_candle_data[-1]  # Most recent
            print(f"      Latest candle: {sample_candle.get('time', 'N/A')[:19]}")

            if "bid" in sample_candle:
                bid_data = sample_candle["bid"]
                print(f"        Bid - O:{bid_data.get('o', 'N/A')} H:{bid_data.get('h', 'N/A')} L:{bid_data.get('l', 'N/A')} C:{bid_data.get('c', 'N/A')}")

            if "ask" in sample_candle:
                ask_data = sample_candle["ask"]
                print(f"        Ask - O:{ask_data.get('o', 'N/A')} H:{ask_data.get('h', 'N/A')} L:{ask_data.get('l', 'N/A')} C:{ask_data.get('c', 'N/A')}")

        # 4. Time range candle query
        print("\n   c) Time Range Query (last 7 days, daily candles):")
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)

        daily_candles = await client.instruments.get_instrument_candles(
            "GBP_USD",
            granularity="D",
            from_time=start_time,
            to_time=end_time,
            price="BA",  # Bid and Ask prices
            smooth=True,
        )

        daily_data = daily_candles.get("candles", [])
        print(f"      Retrieved {len(daily_data)} daily candles for GBP/USD")

        if daily_data:
            for candle in daily_data[-3:]:  # Show last 3 days
                time_str = candle.get("time", "N/A")[:10]  # Date only
                bid_data = candle.get("bid", {})
                ask_data = candle.get("ask", {})
                volume = candle.get("volume", 0)

                print(f"      {time_str}: Volume {volume}")
                print(f"        Bid  - O:{bid_data.get('o', 'N/A')} H:{bid_data.get('h', 'N/A')} L:{bid_data.get('l', 'N/A')} C:{bid_data.get('c', 'N/A')}")
                print(f"        Ask  - O:{ask_data.get('o', 'N/A')} H:{ask_data.get('h', 'N/A')} L:{ask_data.get('l', 'N/A')} C:{ask_data.get('c', 'N/A')}")

        # 5. Latest candle snapshots for multiple instruments
        print("\n4. Latest Candle Snapshots:")

        # Get latest candles for multiple instruments with different granularities
        candle_specs = [
            "EUR_USD:H1:M",  # EUR/USD hourly mid prices
            "GBP_USD:M30:BA",  # GBP/USD 30-min bid/ask
            "USD_JPY:M15:M",  # USD/JPY 15-min mid prices
            "AUD_USD:H4:M",  # AUD/USD 4-hour mid prices
        ]

        latest_candles = await client.pricing.get_latest_candles(
            account_id,
            candle_specs,
            units=3,  # Get last 3 candles for each spec
        )

        latest_data = latest_candles.get("latestCandles", [])
        print(f"   Retrieved latest candles for {len(latest_data)} specifications:")

        for candle_info in latest_data:
            instrument = candle_info.get("instrument", "N/A")
            granularity = candle_info.get("granularity", "N/A")
            candle_list = cast("list[dict[str, Any]]", candle_info.get("candles", []))

            print(f"\n     {instrument} ({granularity}):")
            for candle in candle_list[-2:]:  # Show last 2 candles
                time_str = candle.get("time", "N/A")[:19]
                volume = candle.get("volume", 0)
                complete = candle.get("complete", False)

                print(f"       {time_str} (Vol: {volume}, Complete: {complete})")

                # Show available price data
                if "mid" in candle:
                    mid = candle["mid"]
                    print(f"         Mid: O:{mid.get('o', 'N/A')} H:{mid.get('h', 'N/A')} L:{mid.get('l', 'N/A')} C:{mid.get('c', 'N/A')}")
                if "bid" in candle:
                    bid = candle["bid"]
                    print(f"         Bid: O:{bid.get('o', 'N/A')} H:{bid.get('h', 'N/A')} L:{bid.get('l', 'N/A')} C:{bid.get('c', 'N/A')}")
                if "ask" in candle:
                    ask = candle["ask"]
                    print(f"         Ask: O:{ask.get('o', 'N/A')} H:{ask.get('h', 'N/A')} L:{ask.get('l', 'N/A')} C:{ask.get('c', 'N/A')}")

        # 6. Advanced candle configurations
        print("\n5. Advanced Candle Configurations:")

        print("   a) Custom timezone alignment (London market hours):")
        london_candles = await client.instruments.get_instrument_candles(
            "GBP_USD",
            granularity="D",
            count=5,
            daily_alignment=8,  # 8 AM
            alignment_timezone="Europe/London",
            smooth=False,
        )

        london_data = london_candles.get("candles", [])
        print(f"      Retrieved {len(london_data)} daily candles aligned to London timezone")

        print("\n   b) Weekly candles (Monday alignment):")
        weekly_candles = await client.instruments.get_instrument_candles(
            "EUR_USD",
            granularity="W",
            count=4,
            weekly_alignment="Monday",
            include_first=False,  # Exclude incomplete first candle
        )

        weekly_data = weekly_candles.get("candles", [])
        print(f"      Retrieved {len(weekly_data)} weekly candles")

        # 7. Price type comparison
        print("\n6. Price Type Comparison (Mid vs Bid/Ask):")

        # Get same timeframe with different price types
        comparison_time = datetime.now(timezone.utc) - timedelta(hours=1)

        mid_candles = await client.instruments.get_instrument_candles("EUR_USD", granularity="M5", from_time=comparison_time, price="M")

        bid_ask_candles = await client.instruments.get_instrument_candles("EUR_USD", granularity="M5", from_time=comparison_time, price="BA")

        mid_count = len(mid_candles.get("candles", []))
        ba_count = len(bid_ask_candles.get("candles", []))

        print(f"   Mid prices: {mid_count} candles")
        print(f"   Bid/Ask prices: {ba_count} candles")

        if mid_count > 0 and ba_count > 0:
            mid_latest = mid_candles["candles"][-1].get("mid", {})
            ba_latest = bid_ask_candles["candles"][-1]
            bid_latest = ba_latest.get("bid", {})
            ask_latest = ba_latest.get("ask", {})

            print("   Latest candle comparison:")
            print(f"     Mid close: {mid_latest.get('c', 'N/A')}")
            print(f"     Bid close: {bid_latest.get('c', 'N/A')}")
            print(f"     Ask close: {ask_latest.get('c', 'N/A')}")

            # Calculate spread
            if bid_latest.get("c") and ask_latest.get("c"):
                spread = float(ask_latest["c"]) - float(bid_latest["c"])
                print(f"     Spread: {spread:.5f}")

        # 8. Best practices summary
        print("\n7. Best Practices for Pricing & Candles:")
        print("""
   Pricing:
   - Use streaming for real-time applications
   - Include units available for trade sizing
   - Handle heartbeats to detect stream health
   - Implement reconnection logic for production

   Candles:
   - Choose appropriate granularity for your strategy
   - Use time ranges for historical analysis
   - Consider timezone alignment for global markets
   - Use bid/ask data for precise entry/exit points
   - Smooth candles for trend analysis
   - Cache frequently requested candle data

   Candle Endpoints:
   - Use client.instruments.get_instrument_candles() for general historical data
   - Use client.pricing.get_account_candles() for account-specific permissions
   - Account-specific candles may vary based on account access levels
        """)

        print("Pricing and candle data demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
