# Lesson 1: Foundation - Forex Trading Fundamentals

!!! tip "🎯 Learning Goal"
    Master the essential concepts you need to understand before placing your first trade.

---

## Currency Pairs

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

---

## Key Trading Concepts

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

---

## Order Types You'll Use

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

---

## 💻 Hands-on Exercise: Concept Exploration

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

---

## ✅ Skill Checkpoint: Foundation Knowledge

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

---

## What You've Learned

✅ **Currency Pair Fundamentals**: How forex pairs work and what they represent

✅ **Trading Terminology**: Pips, spreads, leverage, and margin concepts

✅ **Order Types**: Market orders, limit orders, stop losses, and take profits

✅ **Practical Calculations**: Pip values and profit/loss calculations

!!! success "🎉 Foundation Complete!"
    Congratulations! You now understand the fundamental concepts of forex trading. You're ready to connect to the OANDA API and start practicing with real market data.

---

## Next Steps

Continue to [Lesson 2: Connection & Setup](lesson-2-connection-setup.md) to learn how to connect securely to the OANDA API and understand your trading account.

---

## Related Resources

- [Forex Trading Concepts](../../explanation/forex-trading-concepts.md) - Deeper theoretical background
- [API Reference](../../api-reference/index.md) - Technical documentation
- [Getting Started Guide](../getting-started/installation.md) - Installation and setup