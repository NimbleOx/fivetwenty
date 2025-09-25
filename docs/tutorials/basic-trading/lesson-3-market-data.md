# Lesson 3: Market Data & Analysis

!!! tip "🎯 Learning Goal"
    Understand how to retrieve and analyze market data to make informed trading decisions.

---

## Getting Current Prices

Before placing any trade, you need to understand current market conditions:

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def get_current_prices(account_id: str, instruments: list):
    """Fetch current market prices."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            prices = await client.pricing.get_pricing(
                account_id=account_id,
                instruments=instruments
            )

            print("📈 Current Market Prices:")
            for price in prices:
                if price.bids and price.asks:
                    bid = Decimal(str(price.bids[0].price))
                    ask = Decimal(str(price.asks[0].price))
                    spread = ask - bid

                    print(f"   {price.instrument}:")
                    print(f"     Bid: {bid:.5f}")
                    print(f"     Ask: {ask:.5f}")
                    print(f"     Spread: {spread:.5f} ({spread/ask*10000:.1f} pips)")
                    print(f"     Time: {price.time}")

            return prices

        except FiveTwentyError as e:
            print(f"❌ Error getting prices: {e.message}")
            return None

# Get prices for major pairs
if __name__ == "__main__":
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
    if account_id:
        current_prices = asyncio.run(get_current_prices(account_id, instruments))
```

---

## Historical Data Analysis

Understanding recent price action helps with trading decisions:

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode
from fivetwenty.models import CandlestickGranularity

async def get_historical_data(instrument: str, count: int = 100):
    """Get historical candlestick data."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            candles = await client.instruments.candles(
                instrument=instrument,
                count=count,
                granularity=CandlestickGranularity.H1  # 1-hour candles
            )

            print(f"📊 Historical Data for {instrument}:")
            print(f"   Retrieved {len(candles.candles)} candles")

            # Show last 5 candles
            print(f"   Recent 5 candles:")
            for candle in candles.candles[-5:]:
                if candle.mid:
                    print(f"     {candle.time}: O={candle.mid.o} H={candle.mid.h} "
                          f"L={candle.mid.l} C={candle.mid.c} V={candle.volume}")

            return candles

        except FiveTwentyError as e:
            print(f"❌ Error getting historical data: {e.message}")
            return None

# Get historical data
if account_id:
    historical_data = await get_historical_data("EUR_USD", count=50)
```

---

## 💻 Hands-on Exercise: Market Analysis Before Trading

Let's create a comprehensive market analysis function:

```python
from fivetwenty import AsyncClient, Environment

async def analyze_market_before_trading(account_id: str, instrument: str = "EUR_USD"):
    """Comprehensive market analysis before trading."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        print("🔍 MARKET ANALYSIS")
        print("=" * 30)

        # 1. Get current pricing
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[instrument]
        )

        if pricing.prices:
            price = pricing.prices[0]
            bid = Decimal(str(price.bids[0].price))
            ask = Decimal(str(price.asks[0].price))
            spread = ask - bid
            mid_price = (bid + ask) / 2

            print(f"📊 Current {instrument} Pricing:")
            print(f"   Bid: {bid:.5f}")
            print(f"   Ask: {ask:.5f}")
            print(f"   Mid: {mid_price:.5f}")
            print(f"   Spread: {spread:.5f} ({spread*10000:.1f} pips)")

            if spread > 0.0005:  # 5 pips
                print("   ⚠️ Wide spread detected - consider waiting for better conditions")
            else:
                print("   ✅ Normal spread - good for trading")

        # 2. Get recent historical data for context
        try:
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,
                count=24,  # Last 24 hours
                granularity="H1"
            )

            if candles.candles:
                prices = [float(c.mid.c) for c in candles.candles if c.mid]
                if len(prices) >= 2:
                    recent_high = max(prices[-12:])  # 12-hour high
                    recent_low = min(prices[-12:])   # 12-hour low
                    current_price = prices[-1]

                    print(f"\n📈 Recent Price Action (12H):")
                    print(f"   High: {recent_high:.5f}")
                    print(f"   Low:  {recent_low:.5f}")
                    print(f"   Current: {current_price:.5f}")

                    # Simple trend analysis
                    if current_price > prices[-2]:
                        print("   📈 Short-term trend: UP")
                    elif current_price < prices[-2]:
                        print("   📉 Short-term trend: DOWN")
                    else:
                        print("   ➡️ Short-term trend: SIDEWAYS")

        except Exception as e:
            print(f"   ⚠️ Could not get historical data: {e}")

        return price if pricing.prices else None

# Analyze the market before trading
if __name__ == "__main__":
    current_price = asyncio.run(analyze_market_before_trading(account_id, "EUR_USD"))
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

```python
from fivetwenty import AsyncClient

async def assess_market_conditions(account_id: str, instrument: str):
    """Assess current market conditions for trading suitability."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[instrument]
        )

        if not pricing.prices:
            return {"suitable": False, "reason": "No pricing data available"}

        price = pricing.prices[0]
        bid = Decimal(str(price.bids[0].price))
        ask = Decimal(str(price.asks[0].price))
        spread = ask - bid

        # Define conditions
        conditions = {
            "suitable": True,
            "spread_pips": spread * 10000,
            "reasons": []
        }

        # Check spread conditions
        if spread > 0.0005:  # 5 pips
            conditions["suitable"] = False
            conditions["reasons"].append("Wide spread detected")

        # Add other condition checks here:
        # - Time of day (avoid rollover times)
        # - Economic news events
        # - Market volatility

        return conditions

# Check trading conditions
if __name__ == "__main__":
    market_conditions = asyncio.run(assess_market_conditions(account_id, "EUR_USD"))
    print(f"Market suitable for trading: {market_conditions['suitable']}")
```

---

## Price Movement Analysis

Understanding how prices move helps with entry and exit decisions:

```python
from fivetwenty import AsyncClient

async def analyze_price_movements(instrument: str, periods: int = 20):
    """Analyze recent price movements for trading insights."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            candles = await client.instruments.get_instrument_candles(
                instrument=instrument,
                count=periods,
                granularity="M15"  # 15-minute candles
            )

            if not candles.candles:
                return None

            # Extract price data
            highs = [Decimal(str(c.mid.h)) for c in candles.candles if c.mid]
            lows = [Decimal(str(c.mid.l)) for c in candles.candles if c.mid]
            closes = [Decimal(str(c.mid.c)) for c in candles.candles if c.mid]

            if len(closes) < 2:
                return None

            # Calculate volatility
            price_changes = [abs(closes[i] - closes[i-1]) for i in range(1, len(closes))]
            avg_volatility = sum(price_changes) / len(price_changes)

            # Calculate range
            recent_high = max(highs)
            recent_low = min(lows)
            price_range = recent_high - recent_low

            current_price = closes[-1]
            range_position = (current_price - recent_low) / price_range if price_range > 0 else 0.5

            print(f"📊 Price Movement Analysis for {instrument}:")
            print(f"   Recent High: {recent_high:.5f}")
            print(f"   Recent Low:  {recent_low:.5f}")
            print(f"   Current:     {current_price:.5f}")
            print(f"   Range:       {price_range:.5f} ({price_range*10000:.1f} pips)")
            print(f"   Position in Range: {range_position:.1%}")
            print(f"   Avg Volatility: {avg_volatility:.5f} ({avg_volatility*10000:.1f} pips)")

            # Provide interpretation
            if range_position > 0.8:
                print("   📈 Near recent highs - potential resistance")
            elif range_position < 0.2:
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
            print(f"❌ Error analyzing price movements: {e}")
            return None

# Analyze price movements
if __name__ == "__main__":
    price_analysis = asyncio.run(analyze_price_movements("EUR_USD"))
```

---

## ✅ Skill Checkpoint: Market Data Analysis

Test your understanding of market data:

!!! question "🧠 Test Your Understanding"
    1. **If EUR/USD spread is 5 pips, is this good for trading?**
       <details>
       <summary>Click to reveal answer</summary>
       **No, this is a wide spread**. Normal EUR/USD spreads are 1-3 pips. Wide spreads increase your trading costs and make profitable trading more difficult.
       </details>

    2. **What does it mean if current price is at 80% of recent range?**
       <details>
       <summary>Click to reveal answer</summary>
       **Near recent highs - potential resistance level**. The price may have difficulty moving higher and could reverse downward from this level.
       </details>

    3. **Why is historical data important before trading?**
       <details>
       <summary>Click to reveal answer</summary>
       **Context for current conditions**. Historical data shows recent volatility, support/resistance levels, and trend direction, helping you make informed trading decisions.
       </details>

---

## Best Practices for Market Analysis

### Before Every Trade
1. **Check current spreads** - Avoid trading with wide spreads
2. **Analyze recent price action** - Understand context
3. **Assess volatility** - Adjust position size accordingly
4. **Check economic calendar** - Avoid major news events

### Red Flags to Avoid
- Spreads wider than 5 pips for major pairs
- Extremely low volume periods
- Just before major economic announcements
- During market open/close times with high volatility

---

## What You've Learned

✅ **Real-time Pricing**: How to retrieve and interpret current market prices

✅ **Historical Analysis**: Using past data to understand market context

✅ **Market Conditions**: Assessing when markets are suitable for trading

✅ **Price Movement Patterns**: Understanding volatility and range analysis

!!! success "🎉 Market Analysis Mastery Complete!"
    Excellent! You can now analyze market conditions effectively before trading. Next, you'll place your first actual trade with proper analysis and risk management.

---

## Next Steps

Continue to [Lesson 4: Your First Trade](lesson-4-first-trade.md) to place your first trade using the market analysis skills you've learned.

---

## Related Resources

- [Market Data Models](../../api-reference/models/market-data-models.md) - Technical documentation
- [Streaming Data Tutorial](../streaming-data/index.md) - Real-time data processing
- [Forex Trading Concepts](../../explanation/forex-trading-concepts.md) - Market fundamentals