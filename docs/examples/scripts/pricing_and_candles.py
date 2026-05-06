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
        # ==============================
        # PRICING DATA is the foundation of all trading decisions
        # Two types of market data in trading:
        # 1. PRICING: Real-time bid/ask quotes (this section)
        # 2. CANDLES: Historical OHLC data (later sections)
        #
        # get_pricing() returns CURRENT market prices for instruments
        # This is a snapshot - not historical, not streaming
        #
        # When to use pricing:
        # - Pre-trade checks: "What's the current market price?"
        # - Order validation: Ensure your limit price is reasonable
        # - Spread analysis: Calculate trading costs
        # - One-time queries: Don't need continuous updates
        #
        # When NOT to use pricing:
        # - Real-time monitoring: Use streaming instead (Section 2)
        # - Historical analysis: Use candles instead (Section 4+)
        # - Backtesting: Use candle data (pricing is real-time only)
        print("\n=== 1. Current Pricing ===")

        # Request prices for multiple instruments at once
        # More efficient than making separate calls per instrument
        # Note: InstrumentName enum values must be converted to strings
        instruments = [InstrumentName.EUR_USD.value, InstrumentName.GBP_USD.value, InstrumentName.USD_JPY.value]

        print(f"\nFetching current prices for {len(instruments)} instruments...")

        # get_pricing returns dict with "prices", "time", and optionally "homeConversions"
        # Each Price object has bid/ask prices, spread, tradeable status, timestamp
        pricing_response = await client.pricing.get_pricing(account_id=client.account_id, instruments=instruments)

        prices = pricing_response["prices"]

        # Analyze each instrument's pricing
        for price in prices:
            # Check if pricing is available (market might be closed)
            if price.bids and price.asks:
                # BID = Price at which you can SELL
                # This is what the broker will pay you
                # Always lower than ask (broker's profit margin)
                bid = price.bids[0].price

                # ASK = Price at which you can BUY
                # This is what you pay the broker
                # Always higher than bid
                ask = price.asks[0].price

                # SPREAD = Ask - Bid
                # This is your transaction cost
                # Every trade costs you the spread immediately
                # Example: EUR/USD spread of 0.00010 means you lose 1 pip per round-trip
                #
                # Lower spread = Lower trading costs
                # Spread varies by:
                # - Instrument (majors have lowest spreads)
                # - Time (wider during off-hours)
                # - Volatility (wider during news events)
                # - Liquidity (tighter in liquid markets)
                spread = Decimal(ask) - Decimal(bid)

                print(f"\n{price.instrument}:")

                # Liquidity: Available volume at this price level
                # Higher liquidity = more volume you can trade without slippage
                # For large orders, check liquidity to avoid adverse price impact
                print(f"  Bid: {bid} (liquidity: {price.bids[0].liquidity})")
                print(f"  Ask: {ask} (liquidity: {price.asks[0].liquidity})")

                # Spread in price units (typically 0.0001 for EUR/USD = 1 pip)
                print(f"  Spread: {spread:.5f}")

                # Timestamp: When this quote was generated
                # Important: Prices can be stale if market is closed or illiquid
                print(f"  Time: {price.time}")

                # Tradeable: Can you place orders right now?
                # False reasons: Market closed, instrument halted, maintenance
                print(f"  Tradeable: {price.tradeable}")
            else:
                # No bid/ask available - market is likely closed
                # Or instrument is halted/unavailable
                print(f"\n{price.instrument}:")
                print(f"  Status: {price.status}")
                print(f"  Tradeable: {price.tradeable}")

        # Section 2: Stream real-time prices
        # ===================================
        # PRICE STREAMING is for real-time monitoring and high-frequency trading
        # Unlike get_pricing() (one-time snapshot), streaming gives continuous updates
        #
        # Streaming vs Polling:
        # - Streaming: Server pushes updates as they happen (efficient)
        #   - Lower latency: Get updates within milliseconds
        #   - Lower bandwidth: Only sends when prices change
        #   - Single connection: No repeated API calls
        #   - Use for: Real-time dashboards, automated trading, price alerts
        #
        # - Polling (calling get_pricing repeatedly): Client pulls updates (inefficient)
        #   - Higher latency: Depends on polling frequency
        #   - Higher bandwidth: Repeated full requests/responses
        #   - Multiple connections: One per poll
        #   - Use for: Occasional checks, simple scripts
        #
        # Stream events:
        # - PRICE events: Actual price updates (bid/ask changed)
        # - HEARTBEAT events: Keep-alive signals (no price change, connection alive)
        #
        # Heartbeats are CRITICAL:
        # - Prove connection is still alive
        # - Detect stalled connections
        # - Typically sent every 5 seconds if no price updates
        # - If no heartbeat for 10+ seconds → connection is stalled
        print("\n=== 2. Real-Time Price Streaming ===")

        print("\n💡 Demo: Stream EUR/USD prices for 3 seconds...")
        stream_count = 0
        start_time = asyncio.get_event_loop().time()

        # get_pricing_stream() returns async iterator
        # Use 'async for' to receive events as they arrive
        async for event in client.pricing.get_pricing_stream(account_id=client.account_id, instruments=[InstrumentName.EUR_USD]):
            # Check event type - PRICE or HEARTBEAT
            if event.type == "PRICE" and hasattr(event, "bids") and hasattr(event, "asks"):
                # PRICE event: Actual price update
                # Contains bid/ask prices, spread, timestamp
                stream_count += 1
                if event.bids and event.asks:
                    print(f"  Price update #{stream_count}: {event.bids[0].price}/{event.asks[0].price}")

                # IMPORTANT: Process price events quickly!
                # Slow processing can cause queue backlog and stale prices

            elif event.type == "HEARTBEAT":
                # HEARTBEAT event: Connection is alive but no price change
                # Use this to detect stalled connections
                pass

            # Stop after 3 seconds (always have exit condition!)
            # Infinite streams need proper shutdown mechanism
            if asyncio.get_event_loop().time() - start_time > 3:
                break

        print(f"✅ Received {stream_count} price updates in 3 seconds")

        # Section 3: Stream with automatic reconnection
        # ==============================================
        # Production streaming systems MUST handle connection failures
        # Network issues, server restarts, timeouts - all will break your stream
        #
        # Problems with basic streaming (Section 2):
        # - Connection drops → stream ends, no automatic recovery
        # - Stalled connections → hang forever, no data
        # - Network blips → lose price updates
        # - No retry logic → manual intervention required
        #
        # Solution: stream_pricing_with_retries()
        # - Automatic stall detection: Uses monotonic time to detect frozen connections
        # - Automatic reconnection: Retries with exponential backoff
        # - Seamless: Your code keeps receiving events during reconnections
        # - Configurable: Control timeouts, retry attempts, backoff strategy
        #
        # When to use retries:
        # - Production trading systems (always)
        # - Long-running monitors (dashboards, alerts)
        # - Automated trading bots
        # - Any critical streaming operation
        #
        # When basic streaming is OK:
        # - Short-term testing
        # - Development/debugging
        # - One-off data collection
        print("\n=== 3. Streaming with Reconnection ===")

        print("\nRobust streaming with automatic reconnection:")
        print("  - Detects stalled connections")
        print("  - Automatic reconnection with exponential backoff")
        print("  - Configurable timeout and retry policies")

        print("\n💡 How to use:")
        print("  1. Create StreamingConfiguration (stall_timeout, heartbeat_interval)")
        print("  2. Create ReconnectionPolicy (max_attempts, delays, backoff)")
        print("  3. Use stream_pricing_with_retries() instead of get_pricing_stream()")
        print("  4. Retries happen transparently - your code keeps receiving events")
        print("  5. If all retries fail, StreamStall exception is raised")

        # Section 4: Get candlestick data
        # ================================
        # CANDLESTICK DATA (OHLC) is the foundation of technical analysis
        # While pricing data (Section 1-3) is for real-time, candles are for analysis
        #
        # CANDLESTICK = Summary of price action over a time period
        # Each candle contains:
        # - O (Open): First price in the period
        # - H (High): Highest price in the period
        # - L (Low): Lowest price in the period
        # - C (Close): Last price in the period
        # - Volume: Number of trades in the period
        # - Time: Start time of the period
        #
        # Candles vs Pricing:
        # - Candles: Historical data, aggregated, for analysis
        #   - Use for: Backtesting, technical indicators, pattern recognition
        #   - Limited to past data (can't see intra-candle movement)
        #
        # - Pricing: Real-time data, tick-by-tick, for execution
        #   - Use for: Order placement, real-time monitoring, live decisions
        #   - No historical context (just current state)
        #
        # GRANULARITY = Time period per candle
        # Available granularities: S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30,
        #                          H1, H2, H3, H4, H6, H8, H12, D, W, M
        # Examples:
        # - M5 = 5-minute candles (good for intraday trading)
        # - H1 = 1-hour candles (good for swing trading)
        # - D = Daily candles (good for position trading)
        print("\n=== 4. Historical Candlestick Data ===")

        print("\nFetching M5 (5-minute) candles for EUR/USD...")

        # get_account_instrument_candles returns historical candle data
        # Specify granularity and count (how many candles)
        candles_response = await client.pricing.get_account_instrument_candles(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            granularity=CandlestickGranularity.M5,  # 5-minute candles
            count=20,  # Last 20 candles (100 minutes of data)
        )

        candles = candles_response.get("candles", [])

        print(f"Retrieved {len(candles)} candles:")

        # Display last 5 candles (most recent)
        for i, candle in enumerate(candles[-5:], start=len(candles) - 4):  # Show last 5
            if candle.mid:
                # MID prices: (Bid + Ask) / 2
                # Most common for analysis (neutral between buy and sell)
                # Alternative: candle.bid (for selling) or candle.ask (for buying)
                print(f"\n  Candle {i}:")

                # Timestamp: Start of the candle period
                # Example: M5 candle at 10:00 covers 10:00:00 - 10:04:59
                print(f"    Time: {candle.time}")

                # OHLC values - the core data
                print(f"    O: {candle.mid.o}")  # Open: First price
                print(f"    H: {candle.mid.h}")  # High: Peak price
                print(f"    L: {candle.mid.l}")  # Low: Lowest price
                print(f"    C: {candle.mid.c}")  # Close: Last price

                # Volume: Number of trades (NOT units traded)
                # Higher volume = more activity, more reliable patterns
                print(f"    Volume: {candle.volume}")

                # Complete: Is this candle finished?
                # TRUE = Candle period ended, OHLC is final
                # FALSE = Candle still forming, C might change
                #
                # CRITICAL: Only use complete=True candles for backtesting!
                # Incomplete candles will change as new prices arrive
                print(f"    Complete: {candle.complete}")

        # Section 5: Get latest candles
        # =============================
        # get_latest_candles() is an OPTIMIZED endpoint for fetching latest candles
        # It's faster than get_account_instrument_candles() for multiple instruments
        #
        # Key differences:
        # - get_account_instrument_candles(): One instrument at a time, full control
        # - get_latest_candles(): Multiple instruments at once, only latest
        #
        # Use get_latest_candles() when:
        # - You need latest candle for multiple instruments
        # - You don't need historical data (just most recent)
        # - You want faster response (one API call vs multiple)
        #
        # Candle Specifications Format:
        # "INSTRUMENT:GRANULARITY"
        # Example: "EUR_USD:H1" = EUR/USD 1-hour candles
        print("\n=== 5. Latest Candles ===")

        print("\nFetching latest H1 (1-hour) candles for multiple instruments...")

        # Request latest candles for multiple instruments in one call
        # This is more efficient than calling get_account_instrument_candles() multiple times
        latest_response = await client.pricing.get_latest_candles(
            account_id=client.account_id,
            candle_specifications=[
                f"{InstrumentName.EUR_USD.value}:{CandlestickGranularity.H1.value}:M",
                f"{InstrumentName.GBP_USD.value}:{CandlestickGranularity.H1.value}:M",
            ],
        )

        latest_candles = latest_response.get("latestCandles", [])

        # Response structure: list of dicts, each with "instrument" and "candles"
        for candle_data in latest_candles:
            instrument = candle_data.get("instrument")
            candles_list = candle_data.get("candles", [])

            if candles_list:
                # Get the most recent candle
                latest = candles_list[-1]
                print(f"\n{instrument} latest H1:")
                if latest.mid:
                    # Display OHLC in compact format
                    print(f"  OHLC: {latest.mid.o} / {latest.mid.h} / {latest.mid.l} / {latest.mid.c}")
                    print(f"  Volume: {latest.volume}")
                    print(f"  Time: {latest.time}")

        # Section 6: Get instrument candles (generic)
        # ===========================================
        # There are TWO endpoints for getting candles:
        # 1. client.pricing.get_account_instrument_candles() (used above)
        # 2. client.instruments.get_instrument_candles() (this section)
        #
        # Differences:
        # - pricing endpoint: Account-specific (requires account_id)
        #   - Returns bid/ask/mid candles
        #   - More detailed pricing breakdown
        #
        # - instruments endpoint: Generic (no account_id)
        #   - Returns only mid candles
        #   - Simpler, faster for basic analysis
        #
        # Use instruments endpoint when:
        # - You don't need bid/ask breakdown (mid is enough)
        # - Building generic tools (not account-specific)
        # - Faster response needed (less data)
        print("\n=== 6. Instrument Candles (Generic) ===")

        print("\nUsing generic instruments endpoint...")

        # instruments.get_instrument_candles() doesn't require account_id
        # This is useful for general market analysis tools
        generic_candles = await client.instruments.get_instrument_candles(
            instrument=InstrumentName.EUR_USD,
            granularity=CandlestickGranularity.D,  # Daily candles
            count=10,
        )

        daily_candles = generic_candles.get("candles", [])

        print("\nLast 5 daily candles for EUR/USD:")
        for candle in daily_candles[-5:]:
            if candle.mid:
                # Body size: Difference between open and close
                # Large body = strong directional movement
                # Small body = indecision, consolidation
                body_size = abs(Decimal(candle.mid.c) - Decimal(candle.mid.o))

                # Display date and OHLC with body size
                print(f"  {candle.time.strftime('%Y-%m-%d')}: O={candle.mid.o} H={candle.mid.h} L={candle.mid.l} C={candle.mid.c} (Body={body_size:.5f})")

        # Section 7: Analyze different time frames
        # ========================================
        # MULTI-TIMEFRAME ANALYSIS is a core technical analysis technique
        # Idea: Look at same instrument across multiple time periods
        #
        # Why multiple timeframes?
        # - Confirm trends: Trend on H1 + D = strong signal
        # - Find entry points: D trend + M5 pullback = entry
        # - Avoid false signals: M5 breakout but D resistance = risky
        # - Context: See bigger picture while timing entries
        #
        # Common combinations:
        # - Scalping: M1, M5, M15
        # - Day trading: M15, H1, H4
        # - Swing trading: H4, D, W
        # - Position trading: D, W, M
        #
        # Rule of thumb: Use 3 timeframes (lower, middle, higher)
        # - Higher: Identify trend
        # - Middle: Find setups
        # - Lower: Time entries
        print("\n=== 7. Multi-Timeframe Analysis ===")

        print("\nFetching multiple timeframes for EUR/USD...")

        # Define timeframes to analyze
        # Format: (granularity, number_of_candles)
        timeframes = [
            (CandlestickGranularity.M5, 20),  # 5-minute: Micro view (100 min)
            (CandlestickGranularity.M15, 20),  # 15-minute: Short-term (5 hours)
            (CandlestickGranularity.H1, 24),  # 1-hour: Medium-term (1 day)
            (CandlestickGranularity.D, 10),  # Daily: Long-term (10 days)
        ]

        # Fetch and display each timeframe
        for granularity, count in timeframes:
            tf_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=granularity, count=count)

            tf_candles = tf_response.get("candles", [])
            if tf_candles and tf_candles[-1].mid:
                latest_candle = tf_candles[-1]
                # Show latest close price for each timeframe
                # Useful for quick trend alignment check
                if latest_candle.mid:
                    print(f"\n{granularity.value} - Latest close: {latest_candle.mid.c} ({len(tf_candles)} candles)")

        # Section 8: Candlestick pattern analysis
        # ========================================
        # CANDLESTICK PATTERNS are visual representations of market psychology
        # Developed by Japanese rice traders in the 1700s
        # Used to identify potential reversals, continuations, indecision
        #
        # Pattern components:
        # - Body: Open to Close (filled/hollow shows direction)
        # - Upper Wick (Shadow): High to max(Open, Close)
        # - Lower Wick (Shadow): min(Open, Close) to Low
        #
        # This example shows SIMPLE pattern detection
        # Production systems use more sophisticated algorithms
        # - Consider multiple candles (patterns often span 2-3 candles)
        # - Account for context (trend, support/resistance)
        # - Combine with volume and other indicators
        print("\n=== 8. Candlestick Patterns ===")

        print("\nAnalyzing recent M5 candles for patterns...")

        # Get enough candles for pattern analysis
        analysis_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.M5, count=50)

        analysis_candles = analysis_response.get("candles", [])

        # Track pattern counts
        doji_count = 0
        hammer_count = 0
        body_sizes = []

        for candle in analysis_candles:
            # Only analyze complete candles (incomplete ones will change)
            if candle.mid and candle.complete:
                open_price = Decimal(candle.mid.o)
                high = Decimal(candle.mid.h)
                low = Decimal(candle.mid.l)
                close = Decimal(candle.mid.c)

                # Calculate candle components
                body = abs(close - open_price)
                total_range = high - low
                body_sizes.append(body)

                # DOJI PATTERN: Very small body relative to range
                # Interpretation: Indecision, potential reversal
                # Occurs when open ≈ close (battle between bulls/bears)
                # Body should be < 10% of total range
                if total_range > 0 and body / total_range < Decimal("0.1"):
                    doji_count += 1

                # HAMMER PATTERN: Small body at top, long lower wick
                # Interpretation: Potential bullish reversal (after downtrend)
                # Shows sellers pushed price down but buyers regained control
                # Requirements:
                # - Lower wick > 60% of total range (long rejection wick)
                # - Body < 30% of total range (small body)
                lower_wick = min(open_price, close) - low
                if total_range > 0:
                    if lower_wick / total_range > Decimal("0.6") and body / total_range < Decimal("0.3"):
                        hammer_count += 1

        if body_sizes:
            # Average body size helps understand market volatility
            # Large average body = strong directional moves
            # Small average body = consolidation, low volatility
            avg_body = sum(body_sizes) / len(body_sizes)
            print(f"\nPattern Analysis (last {len(analysis_candles)} candles):")
            print(f"  Doji candles: {doji_count}")
            print(f"  Hammer candles: {hammer_count}")
            print(f"  Average body size: {avg_body:.5f}")

        # Section 9: Calculate technical indicators
        # ==========================================
        # TECHNICAL INDICATORS are mathematical calculations on price/volume data
        # Used to identify trends, momentum, volatility, support/resistance
        #
        # Common indicator types:
        # - Trend: SMA, EMA, MACD (follow trend direction)
        # - Momentum: RSI, Stochastic (measure strength)
        # - Volatility: ATR, Bollinger Bands (measure price movement)
        # - Volume: OBV, Volume MA (confirm trends)
        #
        # This section shows SIMPLIFIED indicator calculations
        # Production systems typically use established libraries:
        # - ta-lib (Technical Analysis Library)
        # - pandas-ta
        # - tulipy
        #
        # Why calculate your own?
        # - Learning: Understand how indicators work
        # - Custom modifications: Tweak formulas for specific needs
        # - No external dependencies: Keep project lightweight
        print("\n=== 9. Technical Indicators ===")

        print("\nCalculating simple indicators from candle data...")

        # Get enough candles for meaningful calculations
        # Most indicators need historical data (14-50+ periods)
        indicator_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.H1, count=50)

        indicator_candles = indicator_response.get("candles", [])

        # Extract close prices from complete candles only
        # Using incomplete candles will give incorrect/changing results
        closes = [Decimal(c.mid.c) for c in indicator_candles if c.mid and c.complete]

        if len(closes) >= 20:
            # SIMPLE MOVING AVERAGE (SMA)
            # Average of last N closing prices
            # Smooths out price action, identifies trend direction
            # - Price above SMA = uptrend
            # - Price below SMA = downtrend
            # - SMA crossovers = potential trend changes
            sma_20 = sum(closes[-20:]) / 20
            print(f"\n20-period SMA: {sma_20:.5f}")

            # AVERAGE TRUE RANGE (ATR)
            # Measures volatility (how much price moves per period)
            # Higher ATR = higher volatility = bigger price swings
            # Used for:
            # - Stop loss placement (e.g., 2x ATR stop)
            # - Position sizing (adjust size for volatility)
            # - Breakout detection (ATR expansion = potential breakout)
            #
            # True Range = max(
            #   High - Low,                    # Today's range
            #   |High - Previous Close|,       # Gap up from yesterday
            #   |Low - Previous Close|         # Gap down from yesterday
            # )
            true_ranges = []
            for i in range(1, len(indicator_candles)):
                current_mid = indicator_candles[i].mid
                prev_mid = indicator_candles[i - 1].mid
                if current_mid and prev_mid:
                    high = Decimal(current_mid.h)
                    low = Decimal(current_mid.l)
                    prev_close = Decimal(prev_mid.c)

                    # True range accounts for gaps between candles
                    tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
                    true_ranges.append(tr)

            if len(true_ranges) >= 14:
                # ATR is simply average of last 14 true ranges
                atr_14 = sum(true_ranges[-14:]) / 14
                print(f"14-period ATR: {atr_14:.5f}")

            # BOLLINGER BANDS
            # Volatility bands around a moving average
            # - Upper Band = SMA + (2 * Standard Deviation)
            # - Middle Band = 20-period SMA
            # - Lower Band = SMA - (2 * Standard Deviation)
            #
            # Interpretation:
            # - Price at upper band = overbought, potential reversal down
            # - Price at lower band = oversold, potential reversal up
            # - Bands squeeze = low volatility, potential breakout coming
            # - Bands expand = high volatility, strong trend
            # - ~95% of prices should stay within bands (2 std dev)
            if len(closes) >= 20:
                # Calculate SMA
                sma = sum(closes[-20:]) / Decimal("20")

                # Calculate standard deviation
                # Variance = average of squared differences from mean
                # Std Dev = square root of variance
                variance = sum((c - sma) ** 2 for c in closes[-20:]) / Decimal("20")
                std_dev = variance ** Decimal("0.5")

                # Bands are 2 standard deviations from SMA
                upper_band = sma + (std_dev * 2)
                lower_band = sma - (std_dev * 2)

                print("\nBollinger Bands (20, 2):")
                print(f"  Upper: {upper_band:.5f}")
                print(f"  Middle: {sma:.5f}")
                print(f"  Lower: {lower_band:.5f}")

        # Section 10: Price vs candle data comparison
        # ============================================
        # UNDERSTANDING THE RELATIONSHIP between real-time pricing and candles
        # This is critical for avoiding bugs and understanding market data
        #
        # Key differences:
        # - PRICING: Real-time, constantly updating, bid/ask spread
        #   - Latency: Milliseconds
        #   - Frequency: Every tick (price change)
        #   - Use for: Order execution, real-time decisions
        #
        # - CANDLES: Aggregated, time-based, OHLC summary
        #   - Latency: Seconds to minutes (depends on granularity)
        #   - Frequency: Fixed intervals (M1, M5, H1, etc.)
        #   - Use for: Analysis, backtesting, indicators
        #
        # INCOMPLETE CANDLES:
        # - The most recent candle is often INCOMPLETE (still forming)
        # - complete=False means Close price will change
        # - Close of incomplete candle = current market price
        # - OHLC will update until candle period ends
        #
        # Common mistakes:
        # - Using incomplete candles for backtest signals (forward-looking bias)
        # - Not accounting for bid/ask spread in candles (mid price ≠ execution price)
        # - Assuming candle close = exact price at period end (it's an approximation)
        print("\n=== 10. Price vs Candle Data ===")

        # Get current real-time price
        current_pricing = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])
        current_price = current_pricing["prices"][0]

        # Calculate mid price: (Bid + Ask) / 2
        # This is the "fair" price between buying and selling
        live_mid_price = (Decimal(current_price.bids[0].price) + Decimal(current_price.asks[0].price)) / 2

        # Get latest M1 (1-minute) candles
        # M1 is the finest granularity commonly used for comparison with real-time prices
        m1_response = await client.pricing.get_account_instrument_candles(account_id=client.account_id, instrument=InstrumentName.EUR_USD, granularity=CandlestickGranularity.M1, count=2)

        m1_candles = m1_response.get("candles", [])

        if m1_candles:
            latest_m1 = m1_candles[-1]

            print("\nEUR/USD Current State:")

            # Real-time pricing data
            print(f"  Live Price (mid): {live_mid_price:.5f}")
            print(f"  Live Time: {current_price.time}")

            if latest_m1.mid:
                # Candle data for comparison
                print("\n  Latest M1 Candle:")
                print(f"    Open: {latest_m1.mid.o}")
                print(f"    High: {latest_m1.mid.h}")
                print(f"    Low: {latest_m1.mid.l}")
                print(f"    Close: {latest_m1.mid.c}")

                # Complete flag is CRITICAL
                # False = Candle still forming, values will change
                print(f"    Complete: {latest_m1.complete}")
                print(f"    Time: {latest_m1.time}")

                if not latest_m1.complete:
                    # INCOMPLETE CANDLE: Close price should match current market price
                    # (Or be very close, accounting for timing/lag)
                    print("\n  ⚠️  Candle in formation - close price is current market price")

                    # Calculate movement within this candle
                    # Shows how much price has moved since candle opened
                    candle_open = Decimal(latest_m1.mid.o)
                    movement = live_mid_price - candle_open

                    # Movement in pips (for EUR/USD, 0.0001 = 1 pip)
                    print(f"  Movement this candle: {movement:.5f} pips")

                    # Additional insight: How close is candle close to current price?
                    # Should be very close (within milliseconds of lag)
                    candle_close = Decimal(latest_m1.mid.c)
                    price_diff = abs(live_mid_price - candle_close)
                    print(f"  Price difference (live vs candle close): {price_diff:.5f}")
                    print("    (Should be very small - candle close tracks current price)")

    print("\n✅ Pricing and candles example completed!")
    print("\n📚 Summary:")
    print("   - get_pricing(): Real-time bid/ask quotes")
    print("   - get_pricing_stream(): Continuous price updates")
    print("   - stream_pricing_with_retries(): Robust streaming with reconnection")
    print("   - get_account_instrument_candles(): Historical OHLC data")
    print("   - get_latest_candles(): Latest candles for multiple instruments")
    print("   - get_instrument_candles(): Generic candle data (no account)")
    print("\n   Key concepts:")
    print("   - Pricing: Real-time, for execution")
    print("   - Candles: Historical, for analysis")
    print("   - Complete flag: Only use complete=True for backtesting")
    print("   - Mid price: (Bid + Ask) / 2")
    print("   - Spread: Transaction cost on every trade")
    print("   - Granularity: Time period per candle (M1, M5, H1, D, etc.)")
    print("   - Technical indicators: Calculated from candle data")


if __name__ == "__main__":
    asyncio.run(main())
