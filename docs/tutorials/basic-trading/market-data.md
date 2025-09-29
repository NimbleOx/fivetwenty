# Market Data & Analysis

!!! tip "Target Learning Goal"
    Understand how to retrieve and analyze market data to make informed trading decisions.

---

## Getting Current Prices

Before placing any trade, you need to understand current market conditions:

<!-- fragment: Demo market data retrieval with attribute access and type annotation issues -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

# Load environment variables from .env file
load_dotenv()

async def get_current_prices(instruments: list):
    """Fetch current market prices."""

    # Step 1: Create client using environment-based authentication
    # AsyncClient automatically reads FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT
    async with AsyncClient() as client:
        try:
            # Step 2: Request current pricing for specified instruments
            # This gets real-time bid/ask prices and spreads
            prices = await client.pricing.get_pricing(
                account_id=client.account_id,  # Uses account from environment config
                instruments=instruments         # List of currency pairs to get prices for
            )

            print("Analysis Current Market Prices:")
            # Step 3: Process each price response with financial precision
            for price in prices:
                if price.bids and price.asks:
                    # Convert to Decimal for exact financial calculations
                    bid = Decimal(str(price.bids[0].price))  # Highest price buyers willing to pay
                    ask = Decimal(str(price.asks[0].price))  # Lowest price sellers willing to accept
                    spread = ask - bid                       # Cost of trading (broker's margin)

                    print(f"   {price.instrument}:")
                    print(f"     Bid: {bid:.5f}")                                        # Price you can sell at
                    print(f"     Ask: {ask:.5f}")                                        # Price you must pay to buy
                    print(f"     Spread: {spread:.5f} ({spread/ask*10000:.1f} pips)")   # Trading cost in pips
                    print(f"     Time: {price.time}")                                   # When this price was quoted

            return prices

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

Understanding recent price action helps with trading decisions:

<!-- fragment: Demo historical data analysis with f-string and return type issues -->
```python
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import CandlestickGranularity

# Load environment variables from .env file
load_dotenv()

async def get_historical_data(instrument: str, count: int = 100) -> Any:
    """Get historical candlestick data."""

    # Step 1: Create authenticated client for historical data access
    # Historical data doesn't require live pricing subscription
    async with AsyncClient() as client:
        try:
            # Step 2: Request historical candlestick data
            # Candlesticks show price movement over specific time periods
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,                    # Currency pair to analyze
                count=count,                             # Number of historical periods to retrieve
                granularity=CandlestickGranularity.H1   # 1-hour time periods (other options: M1, M5, D, etc.)
            )

            print(f"Data Historical Data for {instrument}:")
            print(f"   Retrieved {len(candles.candles)} candles")

            # Step 3: Display recent price action for market context
            print(f"   Recent 5 candles:")
            for candle in candles.candles[-5:]:
                if candle.mid:
                    # OHLC = Open, High, Low, Close prices for the time period
                    print(f"     {candle.time}: O={candle.mid.o} H={candle.mid.h} "
                          f"L={candle.mid.l} C={candle.mid.c} V={candle.volume}")
                    # Volume shows trading activity during the period

            return candles

        except FiveTwentyError as e:
            print(f"Error Error getting historical data: {e.message}")
            return None

# Get historical data
if __name__ == "__main__":
    historical_data = asyncio.run(get_historical_data("EUR_USD", count=50))
```

---

## Hands-on Exercise: Market Analysis Before Trading

Let's create a comprehensive market analysis function:

<!-- fragment: Demo comprehensive market analysis with magic numbers and attribute access ---->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def analyze_market_before_trading(instrument: str = "EUR_USD"):
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
            instruments=[instrument]        # Single instrument for focused analysis
        )

        if pricing.prices:
            price = pricing.prices[0]
            # Calculate precise pricing metrics using Decimal for accuracy
            bid = Decimal(str(price.bids[0].price))  # Price you can sell at immediately
            ask = Decimal(str(price.asks[0].price))  # Price you must pay to buy immediately
            spread = ask - bid                       # Trading cost (broker's profit)
            mid_price = (bid + ask) / 2             # Fair value estimate

            print(f"Data Current {instrument} Pricing:")
            print(f"   Bid: {bid:.5f}")                              # Immediate sell price
            print(f"   Ask: {ask:.5f}")                              # Immediate buy price
            print(f"   Mid: {mid_price:.5f}")                        # Market consensus price
            print(f"   Spread: {spread:.5f} ({spread*10000:.1f} pips)")  # Cost to trade in pips

            # Step 3: Assess trading conditions based on spread
            # Wide spreads increase trading costs and reduce profitability
            if spread > Decimal("0.0005"):  # 5 pips threshold for major pairs
                print("   ⚠️ Wide spread detected - consider waiting for better conditions")
            else:
                print("   Success Normal spread - good for trading")

        # Step 4: Get recent historical data for market context
        # Historical analysis helps identify support/resistance and trend direction
        try:
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,    # Same instrument for consistency
                count=24,                # Last 24 hours of data
                granularity="H1"         # 1-hour periods for detailed analysis
            )

            if candles.candles:
                # Extract closing prices for trend analysis
                prices = [float(c.mid.c) for c in candles.candles if c.mid]
                if len(prices) >= 2:
                    # Calculate recent price levels for context
                    recent_high = max(prices[-12:])  # Highest price in last 12 hours (resistance level)
                    recent_low = min(prices[-12:])   # Lowest price in last 12 hours (support level)
                    current_price = prices[-1]       # Most recent closing price

                    print(f"\nAnalysis Recent Price Action (12H):")
                    print(f"   High: {recent_high:.5f}")    # Potential resistance level
                    print(f"   Low:  {recent_low:.5f}")     # Potential support level
                    print(f"   Current: {current_price:.5f}") # Current market position

                    # Step 5: Perform simple trend analysis
                    # Compare current price to previous period for direction
                    if current_price > prices[-2]:
                        print("   Analysis Short-term trend: UP")      # Price rising (bullish)
                    elif current_price < prices[-2]:
                        print("   📉 Short-term trend: DOWN")    # Price falling (bearish)
                    else:
                        print("   ➡️ Short-term trend: SIDEWAYS") # Price consolidating

        except Exception as e:
            print(f"   ⚠️ Could not get historical data: {e}")

        return price if pricing.prices else None

# Analyze the market before trading
if __name__ == "__main__":
    current_price = asyncio.run(analyze_market_before_trading("EUR_USD"))
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

<!-- fragment: Demo market condition assessment with magic numbers and asyncio usage -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def assess_market_conditions(instrument: str):
    """Assess current market conditions for trading suitability."""

    # Step 1: Create client for market condition assessment
    # This function helps determine optimal trading times
    async with AsyncClient() as client:
        # Step 2: Get current pricing for condition analysis
        pricing = await client.pricing.get_pricing(
            account_id=client.account_id,  # Account context for pricing
            instruments=[instrument]        # Single instrument assessment
        )

        # Step 3: Validate pricing data availability
        if not pricing.prices:
            return {"suitable": False, "reason": "No pricing data available"}

        # Step 4: Extract pricing components for analysis
        price = pricing.prices[0]
        bid = Decimal(str(price.bids[0].price))  # Current sell price
        ask = Decimal(str(price.asks[0].price))  # Current buy price
        spread = ask - bid                       # Trading cost calculation

        # Step 5: Initialize market condition assessment
        conditions = {
            "suitable": True,                    # Default to suitable unless issues found
            "spread_pips": spread * 10000,     # Convert spread to pips for readability
            "reasons": []                       # List of any issues detected
        }

        # Step 6: Evaluate spread conditions for trading viability
        # Wide spreads increase trading costs and reduce profit potential
        if spread > Decimal("0.0005"):  # 5 pips threshold for major pairs
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

Understanding how prices move helps with entry and exit decisions:

<!-- fragment: Demo price movement analysis with attribute access and return type issues -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

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
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,    # Currency pair to analyze
                count=periods,           # Number of time periods to examine
                granularity="M15"        # 15-minute intervals for detailed analysis
            )

            if not candles.candles:
                return None

            # Step 3: Extract OHLC price data with Decimal precision
            # Using Decimal ensures accurate financial calculations
            highs = [Decimal(str(c.mid.h)) for c in candles.candles if c.mid]   # High prices per period
            lows = [Decimal(str(c.mid.l)) for c in candles.candles if c.mid]    # Low prices per period
            closes = [Decimal(str(c.mid.c)) for c in candles.candles if c.mid]  # Closing prices per period

            if len(closes) < 2:
                return None

            # Step 4: Calculate price volatility metrics
            # Volatility indicates how much prices are moving (risk/opportunity)
            price_changes = [abs(closes[i] - closes[i-1]) for i in range(1, len(closes))]
            avg_volatility = sum(price_changes) / len(price_changes)

            # Step 5: Calculate trading range metrics
            # Range analysis helps identify support and resistance levels
            recent_high = max(highs)                              # Highest price in period (resistance)
            recent_low = min(lows)                               # Lowest price in period (support)
            price_range = recent_high - recent_low               # Total price movement range

            # Step 6: Determine current position within trading range
            current_price = closes[-1]  # Most recent closing price
            range_position = (current_price - recent_low) / price_range if price_range > 0 else Decimal("0.5")

            print(f"Data Price Movement Analysis for {instrument}:")
            print(f"   Recent High: {recent_high:.5f}")                           # Potential resistance level
            print(f"   Recent Low:  {recent_low:.5f}")                            # Potential support level
            print(f"   Current:     {current_price:.5f}")                        # Current market price
            print(f"   Range:       {price_range:.5f} ({price_range*10000:.1f} pips)")  # Total movement in pips
            print(f"   Position in Range: {range_position:.1%}")                 # Where price sits in range
            print(f"   Avg Volatility: {avg_volatility:.5f} ({avg_volatility*10000:.1f} pips)")  # Average price movement

            # Step 7: Provide tactical trading interpretation
            # Position in range suggests potential support/resistance reactions
            if range_position > Decimal("0.8"):
                print("   Analysis Near recent highs - potential resistance")
            elif range_position < Decimal("0.2"):
                print("   📉 Near recent lows - potential support")
            else:
                print("   ➡️ Middle of range - less clear direction")

            return {
                "high": recent_high,
                "low": recent_low,
                "current": current_price,
                "volatility": avg_volatility,
                "range_position": range_position
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