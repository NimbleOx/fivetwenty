# Market Data & Analysis

!!! tip "Target Learning Goal"
    Understand how to retrieve and analyze market data to make informed trading decisions.

---

## Getting Current Prices

Real-time market pricing is the foundation of all trading decisions. Every currency pair has two prices: the bid (what buyers will pay) and the ask (what sellers want). The difference between these prices is the spread, which represents your trading cost. Before executing any trade, you must check current prices to understand the immediate cost of entry and whether market conditions are favorable.

FiveTwenty provides the `get_pricing()` method to fetch real-time bid/ask prices with microsecond-level timestamps. This example demonstrates how to retrieve current prices for multiple instruments, calculate spreads in pips (the standard unit for forex price movements), and use `Decimal` for precise financial calculations. Understanding spreads is critical - wide spreads during volatile periods or illiquid times can significantly erode your trading profits.

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import ClientPrice

# Load environment variables from .env file
load_dotenv()


async def get_current_prices(instruments: list[str]) -> list[ClientPrice] | None:
    """Fetch current market prices."""

    # Step 1: Create client using environment-based authentication
    # AsyncClient automatically reads FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT
    async with AsyncClient() as client:
        try:
            # Step 2: Request current pricing for specified instruments
            # This gets real-time bid/ask prices and spreads
            pricing_response = await client.pricing.get_pricing(
                account_id=client.account_id,  # Uses account from environment config
                instruments=instruments,  # List of currency pairs to get prices for
            )

            print("Analysis Current Market Prices:")
            # Step 3: Process each price response with financial precision
            for price in pricing_response["prices"]:
                if price.bids and price.asks:
                    # Convert to Decimal for exact financial calculations
                    bid = Decimal(
                        str(price.bids[0].price)
                    )  # Highest price buyers willing to pay
                    ask = Decimal(
                        str(price.asks[0].price)
                    )  # Lowest price sellers willing to accept
                    spread = ask - bid  # Cost of trading (broker's margin)

                    print(f"   {price.instrument}:")
                    print(f"     Bid: {bid:.5f}")  # Price you can sell at
                    print(f"     Ask: {ask:.5f}")  # Price you must pay to buy
                    print(
                        f"     Spread: {spread:.5f} ({spread / ask * 10000:.1f} pips)"
                    )  # Trading cost in pips
                    print(f"     Time: {price.time}")  # When this price was quoted

            return pricing_response["prices"]

        except FiveTwentyError as e:
            print(f"Error Error getting prices: {e.message}")
            return None


# Get prices for major pairs
if __name__ == "__main__":
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
    current_prices = asyncio.run(get_current_prices(instruments))
```

---

## Historical Data Analysis

Historical price data provides the context you need to understand current market conditions. While real-time prices show you where the market is now, historical candlestick data reveals where it's been - showing support and resistance levels, trend direction, and volatility patterns. Each candlestick represents price movement during a specific time period, displaying the opening price, closing price, highest price reached, and lowest price reached (OHLC data).

Analyzing recent price action helps you identify trading opportunities and avoid poor entries. For example, if price recently bounced off a support level multiple times, that level may hold again. If price is trending strongly in one direction with consistent higher highs, you might look for pullback entries in the trend direction. FiveTwenty's `get_instrument_candles()` method retrieves historical data with configurable granularity (1-minute, 5-minute, 1-hour, daily, etc.), allowing you to analyze the timeframe most relevant to your trading strategy:

```python
import asyncio
from typing import Any

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import CandlestickGranularity, InstrumentName

# Load environment variables from .env file
load_dotenv()


async def get_historical_data(instrument: InstrumentName | str, count: int = 100) -> Any:
    """Get historical candlestick data."""

    # Step 1: Create authenticated client for historical data access
    # Historical data doesn't require live pricing subscription
    async with AsyncClient() as client:
        try:
            # Step 2: Request historical candlestick data
            # Candlesticks show price movement over specific time periods
            candles_response = await client.instruments.get_instrument_candles(
                instrument=instrument,  # Currency pair to analyze
                count=count,  # Number of historical periods to retrieve
                granularity=CandlestickGranularity.H1,  # 1-hour time periods (other options: M1, M5, D, etc.)
            )

            print(f"Data Historical Data for {instrument}:")
            candles: list[Any] = candles_response["candles"]
            print(f"   Retrieved {len(candles)} candles")

            # Step 3: Display recent price action for market context
            print("   Recent 5 candles:")
            for candle in candles[-5:]:
                if candle.mid:
                    # OHLC = Open, High, Low, Close prices for the time period
                    print(
                        f"     {candle.time}: O={candle.mid.o} H={candle.mid.h} "
                        f"L={candle.mid.l} C={candle.mid.c} V={candle.volume}"
                    )
                    # Volume shows trading activity during the period

        except FiveTwentyError as e:
            print(f"Error Error getting historical data: {e.message}")
            return None
        else:
            return candles_response


# Get historical data
if __name__ == "__main__":
    historical_data = asyncio.run(get_historical_data(InstrumentName.EUR_USD, count=50))
```

---

## Hands-on Exercise: Market Analysis Before Trading

Before risking capital on any trade, professional traders perform comprehensive market analysis combining real-time pricing, historical context, and current conditions assessment. This pre-trade checklist helps you avoid entering during unfavorable conditions - like wide spreads during news events, or buying at resistance levels that historically reject price.

This example demonstrates a complete market analysis workflow: checking current spreads to assess trading costs, analyzing recent price highs and lows to identify support and resistance zones, and determining short-term trend direction. By combining these elements into a single analysis function, you create a systematic approach to evaluating whether market conditions favor your trading strategy:


```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity

# Load environment variables from .env file
load_dotenv()


async def analyze_market_before_trading(instrument: str = "EUR_USD") -> None:
    """Comprehensive market analysis before trading."""

    # Step 1: Initialize client for comprehensive market analysis
    # This function demonstrates pre-trade analysis workflow
    async with AsyncClient() as client:
        print("Search MARKET ANALYSIS")
        print("=" * 30)

        # Step 2: Get current pricing to assess trading costs
        # Always check spreads before trading to avoid high-cost periods
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,  # Account for pricing context
            instruments=[instrument],  # Single instrument for focused analysis
        )

        if pricing["prices"]:
            price = pricing["prices"][0]
            # Price values are already Decimal type for financial precision
            bid = price.bids[0].price  # Price you can sell at immediately
            ask = price.asks[0].price  # Price you must pay to buy immediately
            spread = ask - bid  # Trading cost (broker's profit)
            mid_price = (bid + ask) / 2  # Fair value estimate

            print(f"Data Current {instrument} Pricing:")
            print(f"   Bid: {bid:.5f}")  # Immediate sell price
            print(f"   Ask: {ask:.5f}")  # Immediate buy price
            print(f"   Mid: {mid_price:.5f}")  # Market consensus price
            print(
                f"   Spread: {spread:.5f} ({spread * 10000:.1f} pips)"
            )  # Cost to trade in pips

            # Step 3: Assess trading conditions based on spread
            # Wide spreads increase trading costs and reduce profitability
            if spread > Decimal("0.0005"):  # 5 pips threshold for major pairs
                print(
                    "   ⚠️ Wide spread detected - consider waiting for better conditions"
                )
            else:
                print("   Success Normal spread - good for trading")

        # Step 4: Get recent historical data for market context
        # Historical analysis helps identify support/resistance and trend direction
        try:
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,  # Same instrument for consistency
                count=24,  # Last 24 hours of data
                granularity=CandlestickGranularity.H1,  # 1-hour periods for detailed analysis
            )

            if candles["candles"]:
                # Extract closing prices for trend analysis
                # Candles are Pydantic models, use attribute access
                # Keep as Decimal for financial precision
                prices = [c.mid.c for c in candles["candles"] if c.mid]
                min_prices_for_analysis = 2
                if len(prices) >= min_prices_for_analysis:
                    # Calculate recent price levels for context
                    recent_high = max(
                        prices[-12:]
                    )  # Highest price in last 12 hours (resistance level)
                    recent_low = min(
                        prices[-12:]
                    )  # Lowest price in last 12 hours (support level)
                    current_price = prices[-1]  # Most recent closing price

                    print("\nAnalysis Recent Price Action (12H):")
                    print(f"   High: {recent_high:.5f}")  # Potential resistance level
                    print(f"   Low:  {recent_low:.5f}")  # Potential support level
                    print(f"   Current: {current_price:.5f}")  # Current market position

                    # Step 5: Perform simple trend analysis
                    # Compare current price to previous period for direction
                    if current_price > prices[-2]:
                        print(
                            "   Analysis Short-term trend: UP"
                        )  # Price rising (bullish)
                    elif current_price < prices[-2]:
                        print("    Short-term trend: DOWN")  # Price falling (bearish)
                    else:
                        print("   ➡️ Short-term trend: SIDEWAYS")  # Price consolidating

        except Exception as e:
            print(f"   ⚠️ Could not get historical data: {e}")


# Analyze the market before trading
if __name__ == "__main__":
    asyncio.run(analyze_market_before_trading("EUR_USD"))
```

---

## Understanding Market Conditions

Different market conditions require different trading approaches:

### Normal Markets
- Spreads: 1-3 pips for major pairs
- Volume: Regular trading activity
- Volatility: Moderate price movements

### High Volatility Markets
- Spreads: May widen significantly
- Volume: Usually increased
- Risk: Higher potential profits and losses

### Low Liquidity Markets
- Spreads: Often wider than normal
- Volume: Reduced trading activity
- Risk: Prices may gap or move erratically

Market condition assessment transforms subjective judgment into objective metrics. Rather than guessing whether now is a good time to trade, you can systematically evaluate spread width, volatility levels, time of day, and other factors that impact trade quality. This function-based approach allows you to build trading rules that automatically filter out poor conditions.

The example below demonstrates a basic conditions assessment framework focused on spread analysis. In production systems, you would expand this to include additional factors like time-based filters (avoiding major news events or market rollover periods), volatility thresholds, and liquidity indicators. The goal is to create a consistent, repeatable process for determining trade suitability:

```python
import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def assess_market_conditions(instrument: str) -> dict[str, Any]:
    """Assess current market conditions for trading suitability."""

    # Step 1: Create client for market condition assessment
    # This function helps determine optimal trading times
    async with AsyncClient() as client:
        # Step 2: Get current pricing for condition analysis
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,  # Account context for pricing
            instruments=[instrument],  # Single instrument assessment
        )

        # Step 3: Validate pricing data availability
        # GetPricingResponse is a TypedDict, use dictionary access
        if not pricing["prices"]:
            return {"suitable": False, "reason": "No pricing data available"}

        # Step 4: Extract pricing components for analysis
        price = pricing["prices"][0]
        bid = price.bids[0].price  # Already Decimal type
        ask = price.asks[0].price  # Already Decimal type
        spread = ask - bid  # Trading cost calculation

        # Step 5: Initialize market condition assessment
        conditions: dict[str, Any] = {
            "suitable": True,  # Default to suitable unless issues found
            "spread_pips": spread * 10000,  # Convert spread to pips (stays Decimal for precision)
            "reasons": [],  # List of any issues detected
        }

        # Step 6: Evaluate spread conditions for trading viability
        # Wide spreads increase trading costs and reduce profit potential
        spread_threshold = Decimal("0.0005")  # 5 pips threshold for major pairs
        if spread > spread_threshold:
            conditions["suitable"] = False
            conditions["reasons"].append("Wide spread detected")

        # Step 7: Framework for additional condition checks
        # Future enhancements could include:
        # - Time of day analysis (avoid market rollover times)
        # - Economic calendar event checking
        # - Market volatility assessment
        # - Liquidity analysis

        return conditions


# Check trading conditions
if __name__ == "__main__":
    market_conditions = asyncio.run(assess_market_conditions("EUR_USD"))
    print(f"Market suitable for trading: {market_conditions['suitable']}")
```

---

## Price Movement Analysis

Price movement patterns reveal market behavior that can inform your trading decisions. Volatility metrics tell you how much prices typically move, helping you set realistic stop losses and profit targets. Range analysis identifies support and resistance boundaries where price may reverse. Understanding where current price sits within recent ranges helps you avoid buying near resistance or selling near support.

This example demonstrates advanced price analysis techniques using higher-frequency data (15-minute candles) to calculate volatility, identify trading ranges, and assess current price position. The analysis provides tactical insights: if price is near the top of its recent range, you might look for short entries or avoid new longs; if price is near the bottom, the opposite may be true. By quantifying these patterns with precise calculations, you remove emotion from your analysis and make data-driven trading decisions:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import Candlestick, CandlestickGranularity

# Load environment variables from .env file
load_dotenv()


async def analyze_price_movements(instrument: str, periods: int = 20):
    """Analyze recent price movements for trading insights."""

    # Step 1: Initialize client for detailed price movement analysis
    # This provides volatility and range analysis for trading decisions
    async with AsyncClient() as client:
        try:
            # Step 2: Request higher-frequency historical data
            # 15-minute candles provide detailed recent price action
            candles_response = await client.instruments.get_instrument_candles(
                instrument=instrument,  # Currency pair to analyze
                count=periods,  # Number of time periods to examine
                granularity=CandlestickGranularity.M15,  # 15-minute intervals for detailed analysis
            )

            candles: list[Candlestick] = candles_response["candles"]
            if not candles:
                return None

            # Step 3: Extract OHLC price data (already Decimal type from API)
            # Pydantic models return price values as Decimal for accurate financial calculations
            highs = [c.mid.h for c in candles if c.mid]  # High prices per period
            lows = [c.mid.l for c in candles if c.mid]  # Low prices per period
            closes = [c.mid.c for c in candles if c.mid]  # Closing prices per period

            if len(closes) < 2:
                return None

            # Step 4: Calculate price volatility metrics
            # Volatility indicates how much prices are moving (risk/opportunity)
            price_changes = [
                abs(closes[i] - closes[i - 1]) for i in range(1, len(closes))
            ]
            avg_volatility = sum(price_changes) / len(price_changes)

            # Step 5: Calculate trading range metrics
            # Range analysis helps identify support and resistance levels
            recent_high = max(highs)  # Highest price in period (resistance)
            recent_low = min(lows)  # Lowest price in period (support)
            price_range = recent_high - recent_low  # Total price movement range

            # Step 6: Determine current position within trading range
            current_price = closes[-1]  # Most recent closing price
            range_position = (
                (current_price - recent_low) / price_range
                if price_range > 0
                else Decimal("0.5")
            )

            print(f"Data Price Movement Analysis for {instrument}:")
            print(f"   Recent High: {recent_high:.5f}")  # Potential resistance level
            print(f"   Recent Low:  {recent_low:.5f}")  # Potential support level
            print(f"   Current:     {current_price:.5f}")  # Current market price
            print(
                f"   Range:       {price_range:.5f} ({price_range * 10000:.1f} pips)"
            )  # Total movement in pips
            print(
                f"   Position in Range: {range_position:.1%}"
            )  # Where price sits in range
            print(
                f"   Avg Volatility: {avg_volatility:.5f} ({avg_volatility * 10000:.1f} pips)"
            )  # Average price movement

            # Step 7: Provide tactical trading interpretation
            # Position in range suggests potential support/resistance reactions
            if range_position > Decimal("0.8"):
                print("   Analysis Near recent highs - potential resistance")
            elif range_position < Decimal("0.2"):
                print("    Near recent lows - potential support")
            else:
                print("   ➡️ Middle of range - less clear direction")

            return {
                "high": recent_high,
                "low": recent_low,
                "current": current_price,
                "volatility": avg_volatility,
                "range_position": range_position,
            }

        except Exception as e:
            print(f"Error Error analyzing price movements: {e}")
            return None


# Analyze price movements
if __name__ == "__main__":
    price_analysis = asyncio.run(analyze_price_movements("EUR_USD"))

```

---

## Using FiveTwenty for Market Analysis

Use FiveTwenty's pricing API to check current spreads and recent price action before placing trades. The historical data endpoints help you understand market context and volatility patterns.

---

## What You've Learned

Success **Real-time Pricing**: How to retrieve and interpret current market prices

Success **Historical Analysis**: Using past data to understand market context

Success **Market Conditions**: Assessing when markets are suitable for trading

Success **Price Movement Patterns**: Understanding volatility and range analysis

!!! success "Complete Market Analysis Mastery Complete!"
    Excellent! You can now analyze market conditions effectively before trading. Next, you'll place your first actual trade with proper analysis and risk management.

---

## Next Steps

Continue to [Position Management](position-management.md) to learn advanced techniques for managing your trading positions.

---

## Related Resources

- [Market Data Models](../../api-reference/models/market-data-models.md) - Technical documentation
- [Streaming Data Tutorial](../streaming-data.md) - Real-time data processing
- [Forex Trading Concepts](../../guides/trading-concepts/forex-trading-concepts.md) - Market fundamentals
