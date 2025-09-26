# Lesson 2: Connection & Setup

!!! tip "🎯 Learning Goal"
    Connect to OANDA safely and understand your account setup before placing any trades.

---

## Import Required Libraries

```python

```

!!! warning "⚠️ Safety First"
    **Always start with PRACTICE environment!** Never test with live money while learning.

    - **Practice Account**: Use fake money for learning
    - **Live Account**: Real money - only use after mastering the basics

---

## Secure Configuration Setup

```python
from fivetwenty import Environment

# Configuration - Replace with your actual values

TOKEN = "your-api-token-here"  # Get this from your OANDA account
ENVIRONMENT = Environment.PRACTICE  # ALWAYS start with PRACTICE!

print("🔧 Configuration Check:")
print(f"Environment: {ENVIRONMENT}")
print(f"Token: {'✅ Set' if TOKEN != 'your-api-token-here' else '❌ Please set your token'}")
```

---

## Hands-on Exercise: Your First Connection

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
            accounts = await client.accounts.get_accounts()

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
if __name__ == "__main__":
    account_id = asyncio.run(connect_with_detailed_feedback())
```

---

## Understanding Your Account

Once connected, let's explore what your account information tells you:

```python
from fivetwenty import AsyncClient, Environment

async def explore_account_details(account_id: str):
    """Interactive exploration of account information."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
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
        if Decimal(str(account.balance)) > Decimal("0"):
            margin_usage_pct = Decimal(str(account.margin_used)) / Decimal(str(account.balance)) * Decimal("100")
            print(f"\n📊 Calculated Metrics:")
            print(f"   Margin Usage:      {margin_usage_pct:.1f}%")

            if margin_usage_pct > 80:
                print("   ⚠️  High margin usage - be careful with new positions")
            elif margin_usage_pct > 50:
                print("   📊 Moderate margin usage - monitor closely")
            else:
                print("   ✅ Low margin usage - room for new positions")

# Explore your account
if __name__ == "__main__":
    if account_id:
        asyncio.run(explore_account_details(account_id))
```

---

## Advanced Account Status Check

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def check_account_status(account_id: str):
    """Get detailed account information."""

    async with AsyncClient(token=TOKEN, account_id="your-account-id", environment=ENVIRONMENT) as client:
        try:
            account = await client.accounts.get_account(account_id)

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
if __name__ == "__main__":
    if account_id:
        account_info = asyncio.run(check_account_status(account_id))
```

---

## Skill Checkpoint: Connection & Account Understanding

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

---

## Common Connection Issues & Solutions

### Invalid API Token
- Verify token is copied correctly
- Check token is for correct environment (practice/live)
- Ensure token has required permissions

### Network Issues
- Check internet connection
- Verify firewall settings
- Try different network if needed

### Environment Mismatch
- Practice tokens only work with PRACTICE environment
- Live tokens only work with LIVE environment
- Never mix environments

---

## What You've Learned

✅ **Secure API Connection**: How to connect safely to OANDA's API

✅ **Account Management**: Understanding account balance, margin, and positions

✅ **Error Handling**: Troubleshooting common connection issues

✅ **Environment Safety**: Why practice environment is essential for learning

!!! success "🎉 Connection Mastery Complete!"
    Excellent! You can now connect to OANDA and understand your account status. Next, you'll learn to analyze market data before placing trades.

---

## Next Steps

Continue to [Lesson 3: Market Data & Analysis](lesson-3-market-data.md) to learn how to retrieve and analyze market data before trading.

---

## Related Resources

- [Authentication Basics](../getting-started/authentication.md) - Detailed authentication guide
- [Environment Configuration](../getting-started/environments.md) - Practice vs Live environments
- [Error Handling](../../api-reference/error-handling.md) - Understanding and handling API errors