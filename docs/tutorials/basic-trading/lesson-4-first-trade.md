# Lesson 4: Your First Trade

!!! tip "🎯 Learning Goal"
    Place your first trade safely, monitor it in real-time, and understand the complete trade lifecycle.

---

## 💻 Hands-on Exercise: Your First Market Order

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

        available_margin = Decimal(str(account.margin_available))
        if available_margin < Decimal("100"):  # Need at least $100 available
            print("❌ Insufficient margin available. Need at least $100.")
            return None

        print(f"✅ Margin available: ${available_margin:.2f}")

        # Step 2: Calculate safe position size
        print("2️⃣ Calculating safe position size...")

        # Risk 1% of account balance (conservative for first trade)
        account_balance = Decimal(str(account.balance))
        risk_amount = account_balance * Decimal("0.01")  # 1% risk
        safe_units = min(1000, int(risk_amount * Decimal("100")))  # Small position

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
if __name__ == "__main__":
    trade_id = asyncio.run(place_first_trade_safely(account_id))
```

---

## Real-time Position Monitoring

Now let's monitor your position in real-time:

```python
from datetime import datetime
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
                        current_price = Decimal(str(pricing.prices[0].bids[0].price))  # Sell price
                    else:  # Short position
                        current_price = Decimal(str(pricing.prices[0].asks[0].price))  # Buy price

                print(f"\n⏰ {datetime.now().strftime('%H:%M:%S')} - Position Update:")
                print(f"   Instrument: {trade.instrument}")
                print(f"   Units: {trade.current_units}")
                print(f"   Entry Price: {trade.price}")
                if current_price:
                    print(f"   Current Price: {current_price:.5f}")

                    # Calculate pip movement
                    price_diff = current_price - Decimal(str(trade.price))
                    if int(trade.current_units) < 0:  # Short position
                        price_diff = -price_diff

                    pip_movement = price_diff * 10000
                    if "JPY" in trade.instrument:
                        pip_movement = price_diff * 100

                    print(f"   Price Movement: {pip_movement:+.1f} pips")

                print(f"   Unrealized P&L: ${Decimal(str(trade.unrealized_pl)):+.2f}")
                print(f"   Margin Used: ${Decimal(str(trade.margin_used)):.2f}")

                # Add some interpretation
                pnl = Decimal(str(trade.unrealized_pl))
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

---

## Closing Your Position

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

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            # Get trade details before closing
            trade = await client.trades.get_trade(account_id, trade_id)

            print(f"📊 Position to Close:")
            print(f"   Trade ID: {trade.id}")
            print(f"   Instrument: {trade.instrument}")
            print(f"   Units: {trade.current_units}")
            print(f"   Entry Price: {trade.price}")
            print(f"   Current P&L: ${Decimal(str(trade.unrealized_pl)):+.2f}")

            # Close the position
            response = await client.trades.close_trade(account_id, trade_id)

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"\n✅ POSITION CLOSED SUCCESSFULLY!")
                print(f"📊 Closing Details:")
                print(f"   Close Price: {fill.price}")
                print(f"   Final P&L: ${Decimal(str(fill.pl)):+.2f}")
                print(f"   Close Time: {fill.time}")

                # Calculate performance metrics
                entry_price = Decimal(str(trade.price))
                close_price = Decimal(str(fill.price))
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
                print(f"   Dollar Result: ${Decimal(str(fill.pl)):+.2f}")

                if Decimal(str(fill.pl)) > 0:
                    print("   🎉 Profitable trade! Well done!")
                elif Decimal(str(fill.pl)) < 0:
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

---

## ✅ Skill Checkpoint: Trade Execution

Test your understanding of trade execution:

!!! question "🧠 Test Your Understanding"
    1. **Why is it important to risk only 1% of your account on your first trade?**
       <details>
       <summary>Click to reveal answer</summary>
       **Capital preservation and learning**. Small risk allows you to practice without significant loss, build confidence, and learn from experience without damaging your account.
       </details>

    2. **What information do you need to monitor during a trade?**
       <details>
       <summary>Click to reveal answer</summary>
       **Entry price, current price, unrealized P&L, pip movement, and margin used**. This gives you complete picture of trade performance and risk exposure.
       </details>

    3. **When should you consider closing a position early?**
       <details>
       <summary>Click to reveal answer</summary>
       **When your analysis changes, stop loss is hit, profit target reached, or market conditions deteriorate**. Don't hold positions hoping they'll turn around.
       </details>

---

## Trade Analysis Framework

After each trade, analyze what happened:

### What Went Right
- Was your market analysis correct?
- Did you follow your risk management plan?
- Was your entry timing good?

### What Could Improve
- Could you have waited for better conditions?
- Was your position size appropriate?
- Did you exit at the right time?

### Lessons Learned
- What market conditions favor this approach?
- How can you improve your analysis?
- What adjustments will you make next time?

---

## What You've Learned

✅ **Safe Trade Execution**: How to place trades with proper risk controls

✅ **Real-time Monitoring**: Tracking position performance and market changes

✅ **Position Closure**: Properly exiting trades with performance analysis

✅ **Trade Analysis**: Framework for learning from each trading experience

!!! success "🎉 First Trade Complete!"
    Congratulations! You've successfully executed your first complete trade cycle. You understand the practical aspects of trade execution, monitoring, and closure. Next, you'll learn advanced position management techniques.

---

## Next Steps

Continue to [Lesson 5: Position Management Mastery](lesson-5-position-management.md) to learn advanced techniques for managing your trading positions.

---

## Related Resources

- [Order Management](../../how-to-guides/manage-orders-effectively.md) - Advanced order techniques
- [Risk Management](../risk-management/index.md) - Comprehensive risk control
- [Trading Models](../../api-reference/models/trading-models.md) - Technical documentation