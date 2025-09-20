# Basic Trading Tutorial

!!! success "🎓 Tutorial - Learning-oriented content"
    **Use this tutorial when:** You want to learn forex trading fundamentals through hands-on practice

    **Learning outcome:** Confidence with basic trading operations and FiveTwenty usage

    **Time commitment:** 30-45 minutes of guided practice

This comprehensive tutorial walks you through the fundamentals of forex trading using FiveTwenty. You'll learn how to place orders, manage positions, and implement basic trading strategies through guided, hands-on exercises.

## Prerequisites

- Python 3.8 or higher
- fivetwenty installed: `pip install fivetwenty`
- OANDA practice account with API token
- Basic understanding of forex markets

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Understand forex trading basics
- ✅ Connect to the OANDA API
- ✅ Place and manage orders
- ✅ Monitor positions and calculate P/L
- ✅ Implement a simple trading strategy

## 📈 Your Learning Journey

This tutorial is structured as a progressive journey with checkpoints to ensure you're building skills effectively:

!!! info "🎯 Skill Progression"
    **Level 1: Foundation** → Understand concepts and connect to API
    **Level 2: Basic Operations** → Place your first trade
    **Level 3: Position Management** → Monitor and manage trades
    **Level 4: Strategy Implementation** → Build a complete trading system

Each section includes:
- 📚 **Concept Explanation** - Learn the theory
- 💻 **Hands-on Exercise** - Practice with code
- ✅ **Skill Checkpoint** - Verify your understanding
- 🎉 **Success Celebration** - Acknowledge your progress

---

## 1. 📚 Level 1: Foundation - Forex Trading Fundamentals

!!! tip "🎯 Learning Goal"
    Master the essential concepts you need to understand before placing your first trade.

### Currency Pairs

Forex trading involves buying one currency while selling another. Currencies are quoted in pairs:

!!! example "💡 Interactive Example"
    **EUR/USD = 1.1000** means:

    - **1 Euro** = **1.1000 US Dollars**
    - To **buy EUR**, you **sell USD**
    - To **sell EUR**, you **buy USD**

    **Try this:** If EUR/USD moves from 1.1000 to 1.1050, the Euro got **stronger** against the Dollar.

**Major Currency Pairs:**

- **EUR/USD**: Euro vs US Dollar (most traded)
- **GBP/USD**: British Pound vs US Dollar
- **USD/JPY**: US Dollar vs Japanese Yen
- **AUD/USD**: Australian Dollar vs US Dollar

### Key Trading Concepts

!!! info "📖 Essential Vocabulary"
    **Pip**: The smallest price movement

    - Most pairs: 0.0001 (4th decimal place)
    - JPY pairs: 0.01 (2nd decimal place)
    - Example: EUR/USD moving from 1.1000 to 1.1001 = **1 pip**

    **Spread**: Difference between bid (sell) and ask (buy) prices

    - Bid: Price you can **sell** at
    - Ask: Price you can **buy** at
    - Spread = Ask - Bid (your trading cost)

    **Leverage**: Using borrowed capital to increase position size

    - 50:1 leverage means $1000 controls $50,000 position
    - Higher leverage = Higher profit potential **and risk**

    **Margin**: Required deposit to open a leveraged position

    - With 50:1 leverage, you need $1000 margin for $50,000 position

### Order Types You'll Use

!!! example "🔧 Order Types in Action"
    **Market Order**: "Buy EUR/USD right now at current price"

    - ✅ Executes immediately
    - ⚠️ Price may slip during execution

    **Limit Order**: "Buy EUR/USD only if price drops to 1.0950"

    - ✅ Controls exact entry price
    - ⚠️ May not execute if price doesn't reach level

    **Stop Loss**: "Close my position if I lose more than $100"

    - ✅ Limits your losses automatically
    - ✅ Essential for risk management

    **Take Profit**: "Close my position when I profit $200"

    - ✅ Secures profits automatically
    - ✅ Removes emotion from profit-taking

### 💻 Hands-on Exercise 1: Concept Exploration

Let's explore real currency pair data to understand these concepts:

```python
from fivetwenty import AsyncClient, Environment

# This exercise helps you understand currency pair pricing
async def explore_currency_concepts():
    """Interactive exploration of forex concepts."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as client:
        # Get current prices for major pairs
        pricing = await client.pricing.get_pricing(
            account_id="your-account-id",
            instruments=["EUR_USD", "GBP_USD", "USD_JPY"]
        )

        print("🔍 EXPLORING CURRENCY PAIR CONCEPTS")
        print("=" * 50)

        for price in pricing.prices:
            instrument = price.instrument
            bid = float(price.bids[0].price)
            ask = float(price.asks[0].price)
            spread = ask - bid

            print(f"\n📊 {instrument}:")
            print(f"   Bid (Sell): {bid:.5f}")
            print(f"   Ask (Buy):  {ask:.5f}")
            print(f"   Spread:     {spread:.5f} ({spread*10000:.1f} pips)")

            # Calculate pip value for different position sizes
            pip_value_1k = 0.0001 * 1000  # For 1,000 unit position
            pip_value_10k = 0.0001 * 10000  # For 10,000 unit position

            if "JPY" in instrument:
                pip_value_1k = 0.01 * 1000
                pip_value_10k = 0.01 * 10000

            print(f"   Pip Value (1K units):  ${pip_value_1k:.2f}")
            print(f"   Pip Value (10K units): ${pip_value_10k:.2f}")

# Run the exploration
await explore_currency_concepts()
```

### ✅ Skill Checkpoint 1: Foundation Knowledge

Before moving on, make sure you can answer these questions:

!!! question "🧠 Test Your Understanding"
    1. **If EUR/USD moves from 1.1000 to 1.1025, how many pips did it move?**
       <details>
       <summary>Click to reveal answer</summary>
       **25 pips** (1.1025 - 1.1000 = 0.0025, and each pip is 0.0001)
       </details>

    2. **If the EUR/USD bid is 1.1000 and ask is 1.1003, what's the spread in pips?**
       <details>
       <summary>Click to reveal answer</summary>
       **3 pips** (1.1003 - 1.1000 = 0.0003 = 3 pips)
       </details>

    3. **With a 10,000 unit EUR/USD position, how much do you make/lose per pip?**
       <details>
       <summary>Click to reveal answer</summary>
       **$1 per pip** (0.0001 × 10,000 = $1)
       </details>

!!! success "🎉 Level 1 Complete!"
    Congratulations! You now understand the fundamental concepts of forex trading. You're ready to connect to the OANDA API and start practicing with real market data.

---

## 2. 🔧 Level 2: Basic Operations - Setup and Your First Connection

!!! tip "🎯 Learning Goal"
    Connect to OANDA safely and understand your account setup before placing any trades.

### Step 1: Import Required Libraries

```python
import asyncio
from decimal import Decimal
from datetime import datetime

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError
```

!!! warning "⚠️ Safety First"
    **Always start with PRACTICE environment!** Never test with live money while learning.

    - **Practice Account**: Use fake money for learning
    - **Live Account**: Real money - only use after mastering the basics

### Step 2: Secure Configuration Setup

```python
# Configuration - Replace with your actual values
TOKEN = "your-api-token-here"  # Get this from your OANDA account
ENVIRONMENT = Environment.PRACTICE  # ALWAYS start with PRACTICE!

print("🔧 Configuration Check:")
print(f"Environment: {ENVIRONMENT}")
print(f"Token: {'✅ Set' if TOKEN != 'your-api-token-here' else '❌ Please set your token'}")
```

### 💻 Hands-on Exercise 2: Your First Connection

Let's establish your first connection to OANDA with detailed feedback:

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def connect_with_detailed_feedback():
    """Your first connection to OANDA with step-by-step feedback."""

    print("🚀 CONNECTING TO OANDA")
    print("=" * 30)

    try:
        print("1️⃣ Creating client connection...")
        async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:

            print("2️⃣ Requesting account list...")
            accounts = await client.accounts.list_accounts()

            if not accounts:
                print("❌ No accounts found - check your token and environment")
                return None

            print(f"3️⃣ Found {len(accounts)} account(s)")

            # Use the first account
            account_summary = accounts[0]
            account_id = account_summary.id

            print("4️⃣ Getting detailed account information...")
            account = await client.accounts.get_account_summary(account_id)

            print("\n✅ CONNECTION SUCCESSFUL!")
            print(f"Account ID: {account.id}")
            print(f"Alias: {account.alias}")
            print(f"Currency: {account.currency}")
            print(f"Balance: {account.balance}")
            print(f"Environment: {ENVIRONMENT.name}")

            return account_id

    except FiveTwentyError as e:
        print(f"\n❌ OANDA Error: {e.error_code}")
        print(f"   Message: {e.message}")
        print("\n🔧 Troubleshooting:")
        if "INVALID_API_TOKEN" in str(e.error_code):
            print("   • Check that your API token is correct")
            print("   • Verify the token is for the right environment (practice/live)")
        elif "INSUFFICIENT_AUTHORIZATION" in str(e.error_code):
            print("   • Check your token permissions")
        return None
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("   • Check your internet connection")
        print("   • Verify OANDA servers are accessible")
        return None

# Test your connection
account_id = await connect_with_detailed_feedback()
```

### Step 3: Understanding Your Account

Once connected, let's explore what your account information tells you:

```python
from fivetwenty import AsyncClient, Environment

async def explore_account_details(account_id: str):
    """Interactive exploration of account information."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        account = await client.accounts.get_account_summary(account_id)

        print("\n📊 ACCOUNT ANALYSIS")
        print("=" * 25)

        print(f"💰 Financial Overview:")
        print(f"   Balance:           {account.balance} {account.currency}")
        print(f"   NAV (Net Value):   {account.nav} {account.currency}")
        print(f"   Unrealized P&L:    {account.unrealized_pl} {account.currency}")

        print(f"\n📈 Margin Information:")
        print(f"   Margin Used:       {account.margin_used} {account.currency}")
        print(f"   Margin Available:  {account.margin_available} {account.currency}")
        print(f"   Margin Rate:       {account.margin_rate}")

        print(f"\n📋 Position Summary:")
        print(f"   Open Trades:       {account.open_trades}")
        print(f"   Open Positions:    {account.open_positions}")
        print(f"   Pending Orders:    {account.pending_orders}")

        # Calculate some useful metrics
        if float(account.balance) > 0:
            margin_usage_pct = float(account.margin_used) / float(account.balance) * 100
            print(f"\n📊 Calculated Metrics:")
            print(f"   Margin Usage:      {margin_usage_pct:.1f}%")

            if margin_usage_pct > 80:
                print("   ⚠️  High margin usage - be careful with new positions")
            elif margin_usage_pct > 50:
                print("   📊 Moderate margin usage - monitor closely")
            else:
                print("   ✅ Low margin usage - room for new positions")

# Explore your account
if account_id:
    await explore_account_details(account_id)
```

### ✅ Skill Checkpoint 2: Connection & Account Understanding

Test your understanding before moving to trading:

!!! question "🧠 Test Your Understanding"
    1. **Why should you always start with PRACTICE environment?**
       <details>
       <summary>Click to reveal answer</summary>
       **Practice environment uses fake money**, so you can learn and make mistakes without losing real money. Always master the basics in practice before going live.
       </details>

    2. **What does 'Margin Available' tell you?**
       <details>
       <summary>Click to reveal answer</summary>
       **How much buying power you have left** for new positions. If margin available is $5000, you could open positions worth up to $5000 in margin requirements.
       </details>

    3. **If your account shows 'Open Trades: 3' but 'Open Positions: 1', what does this mean?**
       <details>
       <summary>Click to reveal answer</summary>
       **You have 3 individual trades that net into 1 position**. For example, you might have bought EUR/USD three times, and those trades combine into one overall long EUR/USD position.
       </details>

!!! success "🎉 Level 2 Complete!"
    Excellent! You can now connect to OANDA and understand your account status. Next, you'll place your first trade and learn position management.

---

### Check Account Status

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def check_account_status(account_id: str):
    """Get detailed account information."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            account = await client.accounts.get(account_id)

            print("💰 Account Status:")
            print(f"   Balance: {account.balance} {account.currency}")
            print(f"   NAV: {account.nav} {account.currency}")
            print(f"   Unrealized P/L: {account.unrealized_pl} {account.currency}")
            print(f"   Margin Used: {account.margin_used} {account.currency}")
            print(f"   Margin Available: {account.margin_available} {account.currency}")
            print(f"   Open Trades: {account.open_trade_count}")
            print(f"   Open Positions: {account.open_position_count}")

            return account

        except FiveTwentyError as e:
            print(f"❌ Error: {e.message}")
            return None

# Check account
if account_id:
    account_info = await check_account_status(account_id)
```

---

## 3. Market Data and Pricing

### Get Current Prices

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def get_current_prices(account_id: str, instruments: list):
    """Fetch current market prices."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            prices = await client.pricing.get(
                account_id=account_id,
                instruments=instruments
            )

            print("📈 Current Market Prices:")
            for price in prices:
                if price.bids and price.asks:
                    bid = float(price.bids[0].price)
                    ask = float(price.asks[0].price)
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
instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
if account_id:
    current_prices = await get_current_prices(account_id, instruments)
```

### Historical Data Analysis

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

from fivetwenty.models import CandlestickGranularity

async def get_historical_data(instrument: str, count: int = 100):
    """Get historical candlestick data."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
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

## 3. 📈 Level 3: Position Management - Your First Trade

!!! tip "🎯 Learning Goal"
    Place your first trade safely, monitor it in real-time, and understand position management fundamentals.

### Step 1: Market Analysis Before Trading

Before placing any trade, let's analyze the market to make informed decisions:

```python
from fivetwenty import AsyncClient, Environment

async def analyze_market_before_trading(account_id: str, instrument: str = "EUR_USD"):
    """Comprehensive market analysis before trading."""

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        print("🔍 MARKET ANALYSIS")
        print("=" * 30)

        # 1. Get current pricing
        pricing = await client.pricing.get_pricing(
            account_id=account_id,
            instruments=[instrument]
        )

        if pricing.prices:
            price = pricing.prices[0]
            bid = float(price.bids[0].price)
            ask = float(price.asks[0].price)
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
current_price = await analyze_market_before_trading(account_id, "EUR_USD")
```

### 💻 Hands-on Exercise 3: Your First Market Order

Now let's place your first trade with comprehensive safety checks:

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def place_first_trade_safely(account_id: str, instrument: str = "EUR_USD"):
    """Place your first trade with safety checks and detailed feedback."""

    print("🚀 PLACING YOUR FIRST TRADE")
    print("=" * 35)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        # Step 1: Pre-trade safety check
        print("1️⃣ Safety Check...")
        account = await client.accounts.get_account_summary(account_id)

        available_margin = float(account.margin_available)
        if available_margin < 100:  # Need at least $100 available
            print("❌ Insufficient margin available. Need at least $100.")
            return None

        print(f"✅ Margin available: ${available_margin:.2f}")

        # Step 2: Calculate safe position size
        print("2️⃣ Calculating safe position size...")

        # Risk 1% of account balance (conservative for first trade)
        account_balance = float(account.balance)
        risk_amount = account_balance * Decimal("0.01")  # 1% risk
        safe_units = min(1000, int(risk_amount * 100))  # Small position

        print(f"   Account Balance: ${account_balance:.2f}")
        print(f"   Risk Amount (1%): ${risk_amount:.2f}")
        print(f"   Safe Position Size: {safe_units} units")

        # Step 3: Place the trade with stop loss
        print("3️⃣ Placing market order...")

        try:
            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=safe_units,  # Small long position
                stop_loss=None,  # We'll add this after trade is opened
                take_profit=None
            )

            print("✅ ORDER PLACED SUCCESSFULLY!")

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"📊 Trade Details:")
                print(f"   Trade ID: {fill.id}")
                print(f"   Instrument: {fill.instrument}")
                print(f"   Units: {fill.units}")
                print(f"   Fill Price: {fill.price}")
                print(f"   Time: {fill.time}")

                return fill.id  # Return trade ID for monitoring
            else:
                print("⚠️ Order placed but not immediately filled")
                return None

        except FiveTwentyError as e:
            print(f"❌ Order failed: {e.error_code}")
            print(f"   Message: {e.message}")

            if e.error_code == "INSUFFICIENT_MARGIN":
                print("💡 Try a smaller position size")
            elif e.error_code == "INSTRUMENT_NOT_TRADEABLE":
                print("💡 Market may be closed or instrument restricted")

            return None

# Place your first trade
trade_id = await place_first_trade_safely(account_id)
```

### Step 2: Real-time Position Monitoring

Now let's monitor your position in real-time:

```python
from fivetwenty import AsyncClient, Environment

async def monitor_position_realtime(account_id: str, trade_id: str, duration_minutes: int = 5):
    """Monitor your position for a specified duration."""

    if not trade_id:
        print("❌ No trade to monitor")
        return

    print(f"👀 MONITORING POSITION FOR {duration_minutes} MINUTES")
    print("=" * 45)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < duration_minutes * 60:
            try:
                # Get current trade status
                trade = await client.trades.get_trade(account_id, trade_id)

                # Get current price for comparison
                pricing = await client.pricing.get_pricing(
                    account_id=account_id,
                    instruments=[trade.instrument]
                )

                current_price = None
                if pricing.prices and pricing.prices[0].asks:
                    if int(trade.current_units) > 0:  # Long position
                        current_price = float(pricing.prices[0].bids[0].price)  # Sell price
                    else:  # Short position
                        current_price = float(pricing.prices[0].asks[0].price)  # Buy price

                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Position Update:")
                print(f"   Instrument: {trade.instrument}")
                print(f"   Units: {trade.current_units}")
                print(f"   Entry Price: {trade.price}")
                if current_price:
                    print(f"   Current Price: {current_price:.5f}")

                    # Calculate pip movement
                    price_diff = current_price - float(trade.price)
                    if int(trade.current_units) < 0:  # Short position
                        price_diff = -price_diff

                    pip_movement = price_diff * 10000
                    if "JPY" in trade.instrument:
                        pip_movement = price_diff * 100

                    print(f"   Price Movement: {pip_movement:+.1f} pips")

                print(f"   Unrealized P&L: ${float(trade.unrealized_pl):+.2f}")
                print(f"   Margin Used: ${float(trade.margin_used):.2f}")

                # Add some interpretation
                pnl = float(trade.unrealized_pl)
                if pnl > 5:
                    print("   📈 Position is profitable!")
                elif pnl < -5:
                    print("   📉 Position has unrealized loss")
                else:
                    print("   ➡️ Position near breakeven")

                await asyncio.sleep(30)  # Update every 30 seconds

            except Exception as e:
                print(f"   ⚠️ Monitoring error: {e}")
                break

        print(f"\n✅ Monitoring complete after {duration_minutes} minutes")

# Monitor your position (run this after placing a trade)
if trade_id:
    await monitor_position_realtime(account_id, trade_id, duration_minutes=2)
```

### Step 3: Understanding Position Management

```python
from fivetwenty import AsyncClient, Environment

async def demonstrate_position_management(account_id: str, trade_id: str):
    """Learn position management techniques."""

    if not trade_id:
        print("❌ No trade for position management demo")
        return

    print("🎛️ POSITION MANAGEMENT TECHNIQUES")
    print("=" * 40)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        # Get current trade
        trade = await client.trades.get_trade(account_id, trade_id)

        print(f"📊 Current Position:")
        print(f"   Trade ID: {trade.id}")
        print(f"   Instrument: {trade.instrument}")
        print(f"   Units: {trade.current_units}")
        print(f"   Entry Price: {trade.price}")
        print(f"   Current P&L: ${float(trade.unrealized_pl):+.2f}")

        # Demonstrate different exit strategies
        print(f"\n🎯 Exit Strategy Options:")

        entry_price = float(trade.price)
        is_long = int(trade.current_units) > 0

        if is_long:
            stop_loss_price = entry_price - 0.0020  # 20 pips stop
            take_profit_price = entry_price + 0.0030  # 30 pips profit
            print(f"   Stop Loss: {stop_loss_price:.5f} (20 pips below entry)")
            print(f"   Take Profit: {take_profit_price:.5f} (30 pips above entry)")
        else:
            stop_loss_price = entry_price + 0.0020  # 20 pips stop
            take_profit_price = entry_price - 0.0030  # 30 pips profit
            print(f"   Stop Loss: {stop_loss_price:.5f} (20 pips above entry)")
            print(f"   Take Profit: {take_profit_price:.5f} (30 pips below entry)")

        print(f"   Risk/Reward Ratio: 1:1.5 (risking 20 pips to make 30 pips)")

        # Don't actually set stop loss in tutorial - just demonstrate
        print(f"\n💡 In real trading, you would set these levels using:")
        print(f"   • Stop Loss orders for risk management")
        print(f"   • Take Profit orders to secure gains")
        print(f"   • Trailing stops to capture more profit")

# Demonstrate position management
if trade_id:
    await demonstrate_position_management(account_id, trade_id)
```

### Step 4: Closing Your Position

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def close_position_safely(account_id: str, trade_id: str):
    """Close your position with detailed feedback."""

    if not trade_id:
        print("❌ No trade to close")
        return

    print("🔚 CLOSING YOUR POSITION")
    print("=" * 30)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        try:
            # Get trade details before closing
            trade = await client.trades.get_trade(account_id, trade_id)

            print(f"📊 Position to Close:")
            print(f"   Trade ID: {trade.id}")
            print(f"   Instrument: {trade.instrument}")
            print(f"   Units: {trade.current_units}")
            print(f"   Entry Price: {trade.price}")
            print(f"   Current P&L: ${float(trade.unrealized_pl):+.2f}")

            # Close the position
            response = await client.trades.close_trade(account_id, trade_id)

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"\n✅ POSITION CLOSED SUCCESSFULLY!")
                print(f"📊 Closing Details:")
                print(f"   Close Price: {fill.price}")
                print(f"   Final P&L: ${float(fill.pl):+.2f}")
                print(f"   Close Time: {fill.time}")

                # Calculate performance metrics
                entry_price = float(trade.price)
                close_price = float(fill.price)
                units = int(trade.current_units)

                if units > 0:  # Long position
                    pip_result = (close_price - entry_price) * 10000
                else:  # Short position
                    pip_result = (entry_price - close_price) * 10000

                if "JPY" in trade.instrument:
                    pip_result = pip_result / 100

                print(f"\n📈 Performance Analysis:")
                print(f"   Entry Price: {entry_price:.5f}")
                print(f"   Exit Price: {close_price:.5f}")
                print(f"   Pip Result: {pip_result:+.1f} pips")
                print(f"   Dollar Result: ${float(fill.pl):+.2f}")

                if float(fill.pl) > 0:
                    print("   🎉 Profitable trade! Well done!")
                elif float(fill.pl) < 0:
                    print("   📚 Learning experience - analyze what happened")
                else:
                    print("   ➡️ Breakeven trade - no gain or loss")

            else:
                print("⚠️ Close order placed but may not be immediately filled")

        except FiveTwentyError as e:
            print(f"❌ Error closing position: {e.error_code}")
            print(f"   Message: {e.message}")

# Close your position (uncomment to close)
# if trade_id:
#     await close_position_safely(account_id, trade_id)
```

### ✅ Skill Checkpoint 3: Position Management

Test your understanding of position management:

!!! question "🧠 Test Your Understanding"
    1. **You buy 1000 units of EUR/USD at 1.1000. The price moves to 1.1025. What's your unrealized P&L?**
       <details>
       <summary>Click to reveal answer</summary>
       **+$2.50**. Price moved +25 pips in your favor. For 1000 units, each pip = $0.10, so 25 pips × $0.10 = $2.50 profit.
       </details>

    2. **Why should you always set a stop loss on your first trade?**
       <details>
       <summary>Click to reveal answer</summary>
       **Risk management**. A stop loss limits your maximum loss and prevents emotional decision-making. It's especially important when learning because it protects your capital while you develop skills.
       </details>

    3. **If you risk 20 pips to make 30 pips, what's your risk-to-reward ratio?**
       <details>
       <summary>Click to reveal answer</summary>
       **1:1.5 risk-to-reward**. You risk 1 unit (20 pips) to potentially gain 1.5 units (30 pips). This is a favorable ratio for profitable trading.
       </details>

!!! success "🎉 Level 3 Complete!"
    Outstanding! You've successfully placed, monitored, and managed your first trade. You understand position management fundamentals and can analyze trade performance. Next, you'll learn to build a complete trading strategy.

---

## 4. 🏗️ Level 4: Strategy Implementation - Building a Complete Trading System

!!! tip "🎯 Learning Goal"
    Combine everything you've learned to build a complete, automated trading strategy with risk management and performance tracking.

### Step 1: Designing Your First Strategy

Let's build a simple but complete moving average crossover strategy:

```python
class SimpleMovingAverageCrossover:
    """A complete trading strategy with risk management."""

    def __init__(self, account_id: str, instrument: str = "EUR_USD"):
        self.account_id = account_id
        self.instrument = instrument
        self.position_size = 1000  # Conservative size
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.stop_loss_pips = 20
        self.take_profit_pips = 30
        self.fast_ma_period = 10
        self.slow_ma_period = 20

        # Strategy state
        self.prices = []
        self.current_position = None
        self.strategy_stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pnl': 0.0
        }

    def calculate_moving_average(self, prices: list, period: int) -> float:
        """Calculate simple moving average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / period

    def should_buy(self) -> bool:
        """Check if we should enter a long position."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Previous MAs for crossover detection
        prev_fast_ma = self.calculate_moving_average(self.prices[:-1], self.fast_ma_period)
        prev_slow_ma = self.calculate_moving_average(self.prices[:-1], self.slow_ma_period)

        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Buy signal: fast MA crosses above slow MA
        return (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)

    def should_sell(self) -> bool:
        """Check if we should enter a short position."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Previous MAs for crossover detection
        prev_fast_ma = self.calculate_moving_average(self.prices[:-1], self.fast_ma_period)
        prev_slow_ma = self.calculate_moving_average(self.prices[:-1], self.slow_ma_period)

        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Sell signal: fast MA crosses below slow MA
        return (prev_fast_ma >= prev_slow_ma) and (fast_ma < slow_ma)

    async def update_prices(self, client: AsyncClient):
        """Update price history for strategy calculations."""
        try:
            # Get recent historical data
            candles = await client.instruments.get_instrument_candles(
                instrument=self.instrument,
                count=max(50, self.slow_ma_period + 10),
                granularity="M5"  # 5-minute candles for more signals
            )

            if candles.candles:
                self.prices = [float(c.mid.c) for c in candles.candles if c.mid]
                return True
        except Exception as e:
            print(f"⚠️ Error updating prices: {e}")
        return False

# Create your strategy instance
strategy = SimpleMovingAverageCrossover(account_id, "EUR_USD")
```

### 💻 Hands-on Exercise 4: Running Your Complete Trading Strategy

Now let's implement the full trading loop:

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

async def run_complete_trading_strategy(strategy: SimpleMovingAverageCrossover, duration_minutes: int = 10):
    """Run a complete trading strategy with full automation."""

    print("🤖 LAUNCHING AUTOMATED TRADING STRATEGY")
    print("=" * 45)
    print(f"Strategy: Moving Average Crossover")
    print(f"Instrument: {strategy.instrument}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Fast MA: {strategy.fast_ma_period} periods")
    print(f"Slow MA: {strategy.slow_ma_period} periods")

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        start_time = datetime.now()

        while (datetime.now() - start_time).seconds < duration_minutes * 60:
            try:
                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Strategy Check")

                # Step 1: Update market data
                if not await strategy.update_prices(client):
                    print("   ⚠️ Could not update prices, skipping this cycle")
                    await asyncio.sleep(60)  # Wait 1 minute before retry
                    continue

                current_price = strategy.prices[-1]
                print(f"   Current Price: {current_price:.5f}")

                # Step 2: Calculate indicators
                if len(strategy.prices) >= strategy.slow_ma_period:
                    fast_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.fast_ma_period
                    )
                    slow_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.slow_ma_period
                    )
                    print(f"   Fast MA: {fast_ma:.5f}")
                    print(f"   Slow MA: {slow_ma:.5f}")

                # Step 3: Check current position
                open_trades = await client.trades.list_trades(
                    strategy.account_id,
                    state="OPEN",
                    instrument=strategy.instrument
                )

                has_position = len(open_trades) > 0
                print(f"   Current Position: {'YES' if has_position else 'NONE'}")

                # Step 4: Strategy logic
                if not has_position:
                    # Look for entry signals
                    if strategy.should_buy():
                        print("   📈 BUY SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "BUY", current_price
                        )
                    elif strategy.should_sell():
                        print("   📉 SELL SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "SELL", current_price
                        )
                    else:
                        print("   ➡️ No signal - waiting")
                else:
                    print("   💼 Managing existing position...")
                    # In a real strategy, you might implement trailing stops,
                    # position sizing adjustments, or other management rules here

                # Step 5: Display strategy statistics
                print(f"   Strategy Stats: {strategy.strategy_stats['total_trades']} trades, "
                      f"${strategy.strategy_stats['total_pnl']:+.2f} total P&L")

                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                print(f"   ❌ Strategy error: {e}")
                await asyncio.sleep(60)

        print(f"\n✅ Strategy completed after {duration_minutes} minutes")
        print_strategy_performance(strategy)

async def execute_strategy_trade(client: AsyncClient, strategy: SimpleMovingAverageCrossover,
                               direction: str, current_price: float):
    """Execute a trade based on strategy signal."""

    try:
        units = strategy.position_size if direction == "BUY" else -strategy.position_size

        # Calculate stop loss and take profit levels
        if direction == "BUY":
            stop_loss_price = current_price - (strategy.stop_loss_pips * Decimal("0.0001"))
            take_profit_price = current_price + (strategy.take_profit_pips * Decimal("0.0001"))
        else:
            stop_loss_price = current_price + (strategy.stop_loss_pips * Decimal("0.0001"))
            take_profit_price = current_price - (strategy.take_profit_pips * Decimal("0.0001"))

        # Place the trade with risk management
        response = await client.orders.post_market_order(
            account_id=strategy.account_id,
            instrument=strategy.instrument,
            units=units,
            stop_loss=Decimal(str(stop_loss_price)),
            take_profit=Decimal(str(take_profit_price))
        )

        if response.order_fill_transaction:
            fill = response.order_fill_transaction
            strategy.strategy_stats['total_trades'] += 1

            print(f"   ✅ {direction} ORDER EXECUTED!")
            print(f"      Trade ID: {fill.id}")
            print(f"      Fill Price: {fill.price}")
            print(f"      Stop Loss: {stop_loss_price:.5f}")
            print(f"      Take Profit: {take_profit_price:.5f}")

    except Exception as e:
        print(f"   ❌ Trade execution failed: {e}")

def print_strategy_performance(strategy: SimpleMovingAverageCrossover):
    """Display comprehensive strategy performance."""

    print(f"\n📊 FINAL STRATEGY PERFORMANCE")
    print("=" * 35)

    stats = strategy.strategy_stats
    print(f"Total Trades: {stats['total_trades']}")

    if stats['total_trades'] > 0:
        win_rate = (stats['winning_trades'] / stats['total_trades']) * 100
        print(f"Winning Trades: {stats['winning_trades']}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${stats['total_pnl']:+.2f}")

        if stats['total_pnl'] > 0:
            print("🎉 Profitable strategy performance!")
        elif stats['total_pnl'] < 0:
            print("📚 Learning opportunity - analyze what happened")
        else:
            print("➡️ Breakeven performance")
    else:
        print("No trades executed during this period")

    print(f"\nStrategy Parameters:")
    print(f"   Instrument: {strategy.instrument}")
    print(f"   Position Size: {strategy.position_size} units")
    print(f"   Stop Loss: {strategy.stop_loss_pips} pips")
    print(f"   Take Profit: {strategy.take_profit_pips} pips")
    print(f"   Fast MA: {strategy.fast_ma_period} periods")
    print(f"   Slow MA: {strategy.slow_ma_period} periods")

# Run your complete strategy (uncomment to run)
# await run_complete_trading_strategy(strategy, duration_minutes=5)
```

### Step 2: Strategy Enhancement Ideas

Here are ways to enhance your basic strategy:

```python
from decimal import Decimal

# Enhanced strategy concepts (for further learning)
class EnhancedTradingStrategy(SimpleMovingAverageCrossover):
    """Enhanced strategy with additional features."""

    def __init__(self, account_id: str, instrument: str = "EUR_USD"):
        super().__init__(account_id, instrument)

        # Enhanced features
        self.max_daily_trades = 5
        self.daily_trade_count = 0
        self.trend_filter_enabled = True
        self.volatility_filter_enabled = True

    async def check_market_conditions(self, client: AsyncClient) -> dict:
        """Advanced market condition analysis."""

        conditions = {
            'trend': 'neutral',
            'volatility': 'normal',
            'spread': 'normal',
            'tradeable': True
        }

        try:
            # Check spread conditions
            pricing = await client.pricing.get_pricing(
                self.account_id,
                [self.instrument]
            )

            if pricing.prices:
                price = pricing.prices[0]
                bid = float(price.bids[0].price)
                ask = float(price.asks[0].price)
                spread = ask - bid

                if spread > 0.0005:  # 5 pips
                    conditions['spread'] = 'wide'
                    conditions['tradeable'] = False

                # Add more sophisticated analysis here:
                # - Volatility measurement
                # - Trend strength calculation
                # - Economic calendar awareness
                # - Multi-timeframe analysis

        except Exception:
            conditions['tradeable'] = False

        return conditions

    def calculate_dynamic_position_size(self, account_balance: float,
                                      volatility: float) -> int:
        """Calculate position size based on account and market conditions."""

        # Base position size
        base_size = self.position_size

        # Adjust for volatility (reduce size in high volatility)
        if volatility > 0.002:  # High volatility threshold
            base_size = int(base_size * Decimal("0.5"))
        elif volatility < 0.001:  # Low volatility
            base_size = int(base_size * Decimal("1.2"))

        # Ensure we don't exceed risk limits
        max_size_by_risk = int(account_balance * self.max_risk_per_trade / 20)

        return min(base_size, max_size_by_risk, 2000)  # Cap at 2000 units

print("💡 Strategy Enhancement Ideas:")
print("- Add volatility filters to avoid trading in choppy markets")
print("- Implement dynamic position sizing based on market conditions")
print("- Add time-of-day filters (avoid trading during low liquidity)")
print("- Include economic calendar integration")
print("- Implement portfolio-level risk management")
print("- Add machine learning for signal optimization")
```

### ✅ Skill Checkpoint 4: Complete Trading System

Test your understanding of complete trading systems:

!!! question "🧠 Test Your Understanding"
    1. **Why is it important to include stop losses in automated strategies?**
       <details>
       <summary>Click to reveal answer</summary>
       **Risk management and capital preservation**. Automated strategies can't make emotional decisions, so programmed risk controls are essential to prevent large losses that could destroy your account.
       </details>

    2. **What's the advantage of using moving average crossovers as signals?**
       <details>
       <summary>Click to reveal answer</summary>
       **Trend following with clear entry/exit rules**. MA crossovers help you enter trends early and stay with them, while providing objective, rules-based signals that remove emotion from trading decisions.
       </details>

    3. **How would you improve this strategy's performance?**
       <details>
       <summary>Click to reveal answer</summary>
       **Multiple improvements possible**: Add volatility filters, implement dynamic position sizing, include time-of-day filters, add trend strength confirmation, use multiple timeframes, and implement proper backtesting for optimization.
       </details>

!!! success "🎉 Level 4 Complete - You're Now a Trading System Developer!"
    Incredible achievement! You've built a complete automated trading strategy from scratch. You understand market analysis, risk management, position sizing, and system automation. You're ready to explore advanced trading concepts and live trading (with proper preparation).

---

## 🏆 Tutorial Complete - Your Trading Journey Begins

### What You've Accomplished

Congratulations! You've successfully completed the comprehensive FiveTwenty trading tutorial. You now possess:

✅ **Level 1 - Foundation Knowledge**
- Deep understanding of forex concepts, pips, spreads, and order types
- Ability to analyze currency pair pricing and market dynamics

✅ **Level 2 - Technical Proficiency**
- Skill connecting to OANDA API safely and securely
- Understanding of account management and margin concepts

✅ **Level 3 - Trading Execution**
- Practical experience placing, monitoring, and closing trades
- Knowledge of position management and risk assessment

✅ **Level 4 - System Development**
- Ability to build complete automated trading strategies
- Understanding of strategy design, backtesting, and optimization

### Your Next Steps

!!! tip "🚀 Ready for Advanced Learning?"
    **For Strategy Development:**
    - Explore our [Strategy Backtesting Notebook](https://github.com/NimbleOx/fivetwenty/blob/main/examples/notebooks/backtesting.ipynb)
    - Read [Advanced Stop-Loss Strategies](../how-to-guides/implement-stop-loss-strategies.md)
    - Study [High-Frequency Trading Optimization](../how-to-guides/optimize-high-frequency-trading.md)

    **For Production Trading:**
    - Follow [Deploy SDK to Production](../how-to-guides/deploy-sdk-to-production.md)
    - Set up [Live Trading Safely](../how-to-guides/setup-live-trading.md)
    - Learn [External Data Integration](../how-to-guides/integrate-external-data-sources.md)

    **For Deep Understanding:**
    - Study [SDK Architecture](../explanation/sdk-architecture.md)
    - Understand [Forex Trading Concepts](../explanation/forex-trading-concepts.md)
    - Master [API Reference Documentation](../api-reference/index.md)

### Safety Reminders

!!! warning "⚠️ Before Live Trading"
    1. **Practice extensively** with paper trading first
    2. **Start small** - use minimum position sizes initially
    3. **Never risk** more than you can afford to lose
    4. **Always use stop losses** and proper risk management
    5. **Keep learning** - markets constantly evolve

### Community & Support

- 📖 **Documentation**: Complete [API Reference](../api-reference/index.md)
- 🐛 **Issues**: [GitHub Issues](#)
- 💬 **Discussions**: [GitHub Discussions](#)
- 📚 **Examples**: [Jupyter Notebooks](https://github.com/NimbleOx/fivetwenty/blob/main/examples/notebooks/quick-start.ipynb)

---

**🎉 Congratulations on completing your trading education foundation!**

Remember: **Successful trading requires practice, discipline, and continuous learning.** You've built the technical skills - now focus on developing the psychological discipline and market knowledge needed for long-term success.

**Happy Trading!** 🚀