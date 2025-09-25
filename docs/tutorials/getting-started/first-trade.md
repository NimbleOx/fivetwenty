# Your First Trade

This guide walks you through placing your first trade using FiveTwenty. We'll cover the complete process from authentication to order execution using modern configuration patterns.

## Prerequisites

Before starting, ensure you have:

- ✅ [Installed the SDK](installation.md)
- ✅ [Set up authentication](authentication.md) and obtained your API token
- ✅ A practice account with OANDA
- ✅ Your credentials configured (see authentication guide for options)

## Configuration Options

FiveTwenty supports three ways to configure your credentials. Choose the approach that best fits your development style:

### Option 1: Environment Variables (Recommended)

Set these environment variables:
```bash
export FIVETWENTY_OANDA_TOKEN="your-practice-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
export FIVETWENTY_OANDA_ACCOUNT_ALIAS="my_first_trade"
```

Then use zero-config initialization:
```python
import asyncio

async def main():
    from fivetwenty import AsyncClient

    async with AsyncClient() as client:
        print(f"Connected: {client.config.summary()}")

asyncio.run(main())
```

### Option 2: Direct Parameters

Pass credentials directly to the client:
```python
from fivetwenty import AsyncClient, Environment

async with AsyncClient(
    token="your-practice-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE
) as client:
    print("Connected to OANDA!")
```

### Option 3: Configuration Objects

Use structured configuration (best for applications):
```python
from fivetwenty import AccountConfig, AsyncClient, Environment

# Create configuration
config = AccountConfig(
    token="your-practice-token",
    account_id="your-account-id",
    environment=Environment.PRACTICE,
    alias="first_trade_account"
)

# Use configuration
async with AsyncClient(config=config) as client:
    print(f"Trading on: {client.config.summary()}")
```

## Step 1: Check Account Balance

Before trading, verify your account status and available funds:

```python
async def check_account(client):
    """Check account balance and trading capacity."""
    # Get account list (we'll use the first one)
    accounts = await client.accounts.get_accounts()
    if not accounts:
        raise RuntimeError("No accounts found")

    # Get detailed account information
    account = await client.accounts.get(accounts[0].id)

    print(f"📊 Account Summary: {client.config.summary()}")
    print(f"💰 Balance: {account.balance} {account.currency}")
    print(f"📈 Unrealized P/L: {account.unrealized_pl}")
    print(f"🔄 Open Trades: {account.open_trade_count}")
    print(f"🔒 Margin Used: {account.margin_used}")
    print(f"✅ Margin Available: {account.margin_available}")

    return account
```

## Step 2: Get Current Prices

Check current market prices before placing orders:

```python
async def get_price(client, instrument="EUR_USD"):
    """Get current pricing for an instrument."""
    # The SDK automatically uses the configured account ID
    prices = await client.pricing.get_pricing(
        account_id=client.account_id,
        instruments=[instrument]
    )

    price = prices[0]
    print(f"\n💱 {instrument} Pricing:")
    print(f"   📉 Bid: {price.bids[0].price if price.bids else 'N/A'}")
    print(f"   📈 Ask: {price.asks[0].price if price.asks else 'N/A'}")
    print(f"   📊 Spread: {price.spread}")
    print(f"   🕒 Time: {price.time}")

    return price
```

## Step 3: Place a Market Order

Place your first market order using the configured account:

```python
async def place_market_order(client, instrument="EUR_USD", units=1000):
    """Place a market order."""
    print(f"\n🛒 Placing {('BUY' if units > 0 else 'SELL')} order:")
    print(f"   📈 Instrument: {instrument}")
    print(f"   📊 Units: {units}")

    # Place market order (SDK uses configured account ID)
    order_response = await client.orders.post_market_order(
        account_id=client.account_id,  # Uses configured account
        instrument=instrument,
        units=units  # Positive for buy, negative for sell
    )

    if order_response.order_fill_transaction:
        fill = order_response.order_fill_transaction
        print(f"\n✅ Order Executed Successfully!")
        print(f"   🆔 Trade ID: {fill.id}")
        print(f"   📈 Instrument: {fill.instrument}")
        print(f"   📊 Units: {fill.units}")
        print(f"   💰 Fill Price: {fill.price}")
        print(f"   💵 P/L: {fill.pl}")
        print(f"   🕒 Time: {fill.time}")

        # Show commission if any
        if hasattr(fill, 'commission') and fill.commission:
            print(f"   💳 Commission: {fill.commission}")

        return fill
    else:
        print("❌ Order was not filled")
        if hasattr(order_response, 'error_message'):
            print(f"   Error: {order_response.error_message}")
        return None
```

## Step 4: Complete First Trade Example

Here's a complete example that combines all steps using the new configuration system:

```python
import asyncio
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

async def first_trade_example():
    """Complete first trade example using FiveTwenty."""

    # Using environment variables (recommended approach)
    # Set FIVETWENTY_OANDA_TOKEN, FIVETWENTY_OANDA_ACCOUNT, FIVETWENTY_OANDA_ENVIRONMENT
    async with AsyncClient() as client:
        try:
            print("🚀 Starting your first trade with FiveTwenty!")
            print(f"📋 Configuration: {client.config.summary()}")

            # 1. Check account status
            account = await check_account(client)

            # Verify we have sufficient margin
            if float(account.margin_available) < 100:
                print("⚠️  Warning: Low margin available for trading")
                return

            # 2. Get current market price
            instrument = "EUR_USD"
            current_price = await get_price(client, instrument)

            # 3. Place a small market order (1000 units)
            print(f"\n📝 Placing your first trade...")
            fill_transaction = await place_market_order(client, instrument, 1000)

            if fill_transaction:
                # 4. Check the resulting position
                await check_position(client, instrument)

                # 5. Show updated account balance
                print("\n📊 Updated Account Status:")
                updated_account = await client.accounts.get(client.account_id)
                print(f"   💰 New Balance: {updated_account.balance}")
                print(f"   📈 Unrealized P/L: {updated_account.unrealized_pl}")

                print("\n🎉 Congratulations! You've executed your first trade!")
                print("\n💡 Next steps:")
                print("   • Monitor your position")
                print("   • Consider setting stop-loss orders")
                print("   • Practice with different instruments")

        except FiveTwentyError as e:
            print(f"❌ OANDA API Error: {e}")
            print(f"   Error Code: {e.code if hasattr(e, 'code') else 'N/A'}")
            print(f"   Message: {e.message if hasattr(e, 'message') else str(e)}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print("   Check your configuration and network connection")

async def check_position(client, instrument):
    """Check open position for an instrument."""
    positions = await client.positions.list_open(client.account_id)

    for position in positions:
        if position.instrument == instrument:
            print(f"\n📊 Open Position for {instrument}:")

            if position.long.units != "0":
                print(f"   📈 Long Position:")
                print(f"      Units: {position.long.units}")
                print(f"      Avg Price: {position.long.average_price}")
                print(f"      Unrealized P/L: {position.long.unrealized_pl}")

            if position.short.units != "0":
                print(f"   📉 Short Position:")
                print(f"      Units: {position.short.units}")
                print(f"      Avg Price: {position.short.average_price}")
                print(f"      Unrealized P/L: {position.short.unrealized_pl}")

            break
    else:
        print(f"\n📊 No open position found for {instrument}")

# Run the complete example
if __name__ == "__main__":
    asyncio.run(first_trade_example())
```

### Alternative: Using Direct Parameters

If you prefer to pass credentials directly:

```python
import asyncio
from fivetwenty import AsyncClient, Environment

async def first_trade_direct_params():
    """First trade using direct parameter configuration."""

    async with AsyncClient(
        token="your-practice-token",
        account_id="your-account-id",
        environment=Environment.PRACTICE
    ) as client:
        print(f"Connected: {client.config.summary()}")

        # Same trading logic as above...
        account = await check_account(client)
        price = await get_price(client)
        fill = await place_market_order(client)

        if fill:
            print("🎉 Trade completed successfully!")

if __name__ == "__main__":
    asyncio.run(first_trade_direct_params())
```

## Step 5: Close a Position

Once you have an open position, you can close it by placing an opposite order:

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def close_position(client, instrument="EUR_USD"):
    """Close an open position for the specified instrument."""

    print(f"\n🔄 Closing position for {instrument}...")

    # Get current positions
    positions = await client.positions.list_open(client.account_id)
    position = next((p for p in positions if p.instrument == instrument), None)

    if not position:
        print(f"❌ No open position found for {instrument}")
        return None

    # Determine units to close
    units_to_close = 0
    if position.long.units != "0":
        # Close long position (sell)
        units_to_close = -int(Decimal(str(position.long.units)))
        print(f"   📉 Closing LONG position of {position.long.units} units")
    elif position.short.units != "0":
        # Close short position (buy)
        units_to_close = -int(Decimal(str(position.short.units)))
        print(f"   📈 Closing SHORT position of {position.short.units} units")

    if units_to_close == 0:
        print(f"❌ No units to close for {instrument}")
        return None

    # Place market order to close position
    close_response = await client.orders.post_market_order(
        account_id=client.account_id,
        instrument=instrument,
        units=units_to_close
    )

    if close_response.order_fill_transaction:
        fill = close_response.order_fill_transaction
        print(f"\n✅ Position Closed Successfully!")
        print(f"   💰 Close Price: {fill.price}")
        print(f"   💵 Realized P/L: {fill.pl}")
        print(f"   🆔 Transaction ID: {fill.id}")
        print(f"   🕒 Close Time: {fill.time}")

        return fill
    else:
        print(f"❌ Failed to close position")
        return None

# Example usage
async def close_position_example():
    """Example of closing a position."""

    async with AsyncClient() as client:
        try:
            # Close EUR/USD position if it exists
            result = await close_position(client, "EUR_USD")

            if result:
                print("\n📊 Position successfully closed!")

                # Check updated account balance
                account = await client.accounts.get(client.account_id)
                print(f"   💰 Updated Balance: {account.balance}")
                print(f"   📊 Open Trade Count: {account.open_trade_count}")

        except FiveTwentyError as e:
            print(f"❌ Error closing position: {e}")

if __name__ == "__main__":
    asyncio.run(close_position_example())
```

## Advanced Order Types

### Limit Order

Place an order to execute at a specific price level:

```python
from decimal import Decimal

async def place_limit_order(client, instrument="EUR_USD"):
    """Place a limit order to buy at a specific price."""

    # Get current price for reference
    current_price = await get_price(client, instrument)
    current_ask = Decimal(current_price.asks[0].price)

    # Set limit price 10 pips below current ask
    limit_price = current_ask - 0.0010  # 10 pips for EUR/USD

    print(f"\n📝 Placing LIMIT order:")
    print(f"   Current Ask: {current_ask}")
    print(f"   Limit Price: {limit_price}")

    limit_order = await client.orders.post_limit_order(
        account_id=client.account_id,
        instrument=instrument,
        units=1000,
        price=f"{limit_price:.5f}"
    )

    print(f"✅ Limit order placed: ID {limit_order.order_create_transaction.id}")
    return limit_order
```

### Stop Loss Order

Protect your positions with automatic stop losses:

```python
from decimal import Decimal

async def place_order_with_stop_loss(client, instrument="EUR_USD"):
    """Place market order with protective stop loss."""

    # Get current price to calculate stop loss
    current_price = await get_price(client, instrument)
    current_ask = Decimal(current_price.asks[0].price)

    # Set stop loss 50 pips below entry (for long position)
    stop_loss_price = current_ask - 0.0050

    print(f"\n📝 Placing order with STOP LOSS:")
    print(f"   Entry ~{current_ask}")
    print(f"   Stop Loss: {stop_loss_price}")

    order_with_sl = await client.orders.post_market_order(
        account_id=client.account_id,
        instrument=instrument,
        units=1000,
        stop_loss_on_fill={"price": f"{stop_loss_price:.5f}"}
    )

    if order_with_sl.order_fill_transaction:
        print(f"✅ Order filled with stop loss protection")
        print(f"   Fill Price: {order_with_sl.order_fill_transaction.price}")
        print(f"   Stop Loss: {stop_loss_price}")

    return order_with_sl
```

### Take Profit Order

Set profit targets for your trades:

```python
from decimal import Decimal

async def place_order_with_take_profit(client, instrument="EUR_USD"):
    """Place market order with take profit target."""

    # Get current price
    current_price = await get_price(client, instrument)
    current_ask = Decimal(current_price.asks[0].price)

    # Set take profit 100 pips above entry
    take_profit_price = current_ask + 0.0100

    print(f"\n📝 Placing order with TAKE PROFIT:")
    print(f"   Entry ~{current_ask}")
    print(f"   Take Profit: {take_profit_price}")

    order_with_tp = await client.orders.post_market_order(
        account_id=client.account_id,
        instrument=instrument,
        units=1000,
        take_profit_on_fill={"price": f"{take_profit_price:.5f}"}
    )

    if order_with_tp.order_fill_transaction:
        print(f"✅ Order filled with take profit target")
        print(f"   Fill Price: {order_with_tp.order_fill_transaction.price}")
        print(f"   Take Profit: {take_profit_price}")

    return order_with_tp
```

### Complete Risk Management Example

Combine stop loss and take profit for complete risk management:

```python
from decimal import Decimal

async def place_protected_trade(client, instrument="EUR_USD", units=1000):
    """Place a trade with both stop loss and take profit."""

    # Get current price
    current_price = await get_price(client, instrument)
    current_ask = Decimal(current_price.asks[0].price)

    # Risk management: 1:2 risk/reward ratio
    stop_loss_pips = 50  # 50 pips risk
    take_profit_pips = 100  # 100 pips reward

    stop_loss_price = current_ask - (stop_loss_pips * Decimal("0.0001"))
    take_profit_price = current_ask + (take_profit_pips * Decimal("0.0001"))

    print(f"\n🛡️  Protected Trade Setup:")
    print(f"   Entry ~{current_ask}")
    print(f"   Stop Loss: {stop_loss_price} ({stop_loss_pips} pips)")
    print(f"   Take Profit: {take_profit_price} ({take_profit_pips} pips)")
    print(f"   Risk:Reward = 1:{take_profit_pips/stop_loss_pips}")

    protected_order = await client.orders.post_market_order(
        account_id=client.account_id,
        instrument=instrument,
        units=units,
        stop_loss_on_fill={"price": f"{stop_loss_price:.5f}"},
        take_profit_on_fill={"price": f"{take_profit_price:.5f}"}
    )

    if protected_order.order_fill_transaction:
        print(f"\n✅ Protected trade executed!")
        print(f"   🎯 Position protected with SL & TP")

    return protected_order
```

## Using the Sync Client

If you prefer synchronous code, use the sync `Client` class:

```python
from fivetwenty import Client, Environment

# Sync client supports same configuration patterns
def sync_trading_example():
    """Synchronous trading example."""

    # Using environment variables (recommended)
    with Client() as client:
        print(f"📋 Connected: {client.config.summary()}")

        # All operations are synchronous
        accounts = client.accounts.get_accounts()
        print(f"📊 Found {len(accounts)} accounts")

        # Check balance
        account = client.accounts.get(client.account_id)
        print(f"💰 Balance: {account.balance} {account.currency}")

        # Get price
        prices = client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        )
        current_price = prices[0]
        print(f"💱 EUR/USD Ask: {current_price.asks[0].price}")

        # Place order
        order = client.orders.post_market_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=1000
        )

        if order.order_fill_transaction:
            fill = order.order_fill_transaction
            print(f"✅ Order executed: {fill.id}")
            print(f"💰 Fill price: {fill.price}")

        print("🎉 Sync trading complete!")

# Alternative: Direct parameter configuration
def sync_direct_params_example():
    """Sync client with direct parameters."""

    with Client(
        token="your-practice-token",
        account_id="your-account-id",
        environment=Environment.PRACTICE
    ) as client:
        # Same trading logic...
        account = client.accounts.get(client.account_id)
        print(f"Balance: {account.balance}")

if __name__ == "__main__":
    sync_trading_example()
```

### Sync vs Async: When to Use What

| Use Async Client When: | Use Sync Client When: |
|----------------------|---------------------|
| Building web applications | Writing scripts or tools |
| High-frequency trading | Basic automation |
| Concurrent operations | Sequential operations |
| Modern async frameworks | Legacy codebases |
| Maximum performance | Simplicity preferred |

```python
import asyncio
from fivetwenty import Client, AsyncClient, Environment

# Async: Better for multiple concurrent operations
async def async_advantage():
    async with AsyncClient() as client:
        # These run concurrently
        accounts_task = client.accounts.get_accounts()
        prices_task = client.pricing.get_pricing(client.account_id, ["EUR_USD", "GBP_USD"])

        accounts, prices = await asyncio.gather(accounts_task, prices_task)

# Sync: Better for simple sequential operations
def sync_advantage():
    with Client() as client:
        # Simple, readable sequential flow
        account = client.accounts.get(client.account_id)
        if float(account.margin_available) > 1000:
            order = client.orders.post_market_order(
                account_id=client.account_id,
                instrument="EUR_USD",
                units=1000
            )
```

## Best Practices

### 1. **Security First**
- **Never hardcode tokens** in your source code
- **Use environment variables** or secure vaults for credentials
- **Keep practice and live tokens separate**
- **Rotate API tokens periodically**

```python
from fivetwenty import AsyncClient, Environment

# ❌ Bad - Never do this
client = AsyncClient(token="abc123def456", environment=Environment.PRACTICE)

# ✅ Good - Use environment variables
client = AsyncClient()  # Loads from FIVETWENTY_* env vars
```

### 2. **Risk Management**
- **Always use stop losses** to limit potential losses
- **Start small** with minimal position sizes while learning
- **Use practice accounts** extensively before going live
- **Set position size limits** based on account balance

```python
# Calculate position size based on account balance
async def calculate_position_size(client, expected_loss_per_unit):
    account = await client.accounts.get(client.account_id)
    max_risk = Decimal(str(account.balance)) * Decimal('0.02')  # 2% risk per trade
    position_size = min(1000, int(max_risk / expected_loss_per_unit))
    return position_size
```

### 3. **Order Management**
- **Check margin requirements** before placing orders
- **Monitor positions** regularly
- **Use limit orders** in volatile markets
- **Implement proper error handling**

```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

try:
    order = await client.orders.post_market_order(...)
except FiveTwentyError as e:
    if "INSUFFICIENT_MARGIN" in str(e):
        print("Reduce position size")
    elif "MARKET_HALTED" in str(e):
        print("Market closed, try later")
```

### 4. **Configuration Management**
- **Use descriptive aliases** for account configurations
- **Document your setup** in comments
- **Test configurations** before deploying
- **Use structured logging** for monitoring

```python
import os
from fivetwenty import AccountConfig, Environment

# Good configuration practice
config = AccountConfig(
    token=os.environ["PRACTICE_TOKEN"],
    account_id=os.environ["PRACTICE_ACCOUNT"],
    environment=Environment.PRACTICE,
    alias="strategy_testing"
)
```

### 5. **Development Workflow**
- **Test on practice first** - always validate strategies in practice environment
- **Use proper logging** - log trades but never log credentials
- **Handle network issues** - implement retry logic for transient failures
- **Monitor API usage** - stay within rate limits

## Troubleshooting Common Issues

### Configuration Problems

**Missing Environment Variables:**
```python
from fivetwenty import AsyncClient, Environment

# Error: "No configuration provided"
try:
    client = AsyncClient()
except ValueError as e:
    print("Set FIVETWENTY_OANDA_TOKEN and FIVETWENTY_OANDA_ACCOUNT environment variables")
    print("Or pass credentials directly to AsyncClient()")
```

**Invalid Token:**
```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

# Error: Authentication failed
try:
    accounts = await client.accounts.get_accounts()
except FiveTwentyError as e:
    if "401" in str(e):
        print("Invalid token - check your API credentials")
        print("Generate new token in OANDA account settings")
```

### Trading Issues

**Insufficient Margin:**
```python
# Check margin before trading
async def check_margin_requirements(client, units, instrument="EUR_USD"):
    account = await client.accounts.get(client.account_id)
    margin_available = float(account.margin_available)

    # Rough margin calculation (varies by instrument)
    estimated_margin = abs(units) * 0.03  # 3% margin for major pairs

    if margin_available < estimated_margin:
        print(f"❌ Insufficient margin:")
        print(f"   Required: ~{estimated_margin}")
        print(f"   Available: {margin_available}")
        return False

    return True

# Use before placing orders (inside an async function)
async def trading_example(client):
    if await check_margin_requirements(client, 10000):
        order = await client.orders.post_market_order(...)
```

**Market Closed:**
```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

# Check trading hours
async def check_market_hours(client, instrument="EUR_USD"):
    try:
        # Try to get current price
        prices = await client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[instrument]
        )
        return True  # Market is open
    except FiveTwentyError as e:
        if "MARKET_HALTED" in str(e) or "MARKET_CLOSED" in str(e):
            print(f"Market closed for {instrument}")
            return False
        raise  # Re-raise other errors
```

**Invalid Units:**
```python
# Validate units before trading
async def validate_trade_size(client, units, instrument="EUR_USD"):
    instruments = await client.accounts.get_account_instruments(
        account_id=client.account_id,
        instruments=[instrument]
    )

    instrument_info = instruments[0]
    min_size = int(instrument_info.minimum_trade_size)
    max_size = int(instrument_info.maximum_order_units)

    if abs(units) < min_size:
        print(f"❌ Units too small. Minimum: {min_size}")
        return False

    if abs(units) > max_size:
        print(f"❌ Units too large. Maximum: {max_size}")
        return False

    print(f"✅ Trade size {units} is valid")
    return True
```

### Network and API Issues

**Rate Limiting:**
```python
# Handle rate limits gracefully
import asyncio
from fivetwenty.exceptions import FiveTwentyError

async def robust_api_call(client, operation):
    """Make API call with retry logic."""
    max_retries = 3

    for attempt in range(max_retries):
        try:
            return await operation()
        except FiveTwentyError as e:
            if "429" in str(e):  # Rate limited
                delay = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {delay}s...")
                await asyncio.sleep(delay)
                continue
            raise  # Re-raise other errors

    raise Exception(f"Failed after {max_retries} attempts")

# Usage (inside an async function)
async def api_example(client):
    accounts = await robust_api_call(
        client,
        lambda: client.accounts.get_accounts()
    )
    return accounts
```

**Connection Issues:**
```python
import asyncio

async def main():
    from fivetwenty import AsyncClient, Environment

    # Handle connection problems
    import httpx

    try:
        async with AsyncClient() as client:
            accounts = await client.accounts.get_accounts()
    except httpx.ConnectError:
        print("❌ Network connection failed")
        print("   Check internet connection and firewall settings")
    except httpx.TimeoutError:
        print("❌ Request timed out")
        print("   Try again or increase timeout setting")

asyncio.run(main())
```

## Next Steps

🎉 **Congratulations!** You've successfully executed your first trade with FiveTwenty!

### Immediate Next Steps
1. **Monitor your position** - Check profit/loss regularly
2. **Practice closing positions** - Learn to exit trades properly
3. **Experiment with order types** - Try limit orders and stop losses
4. **Test different instruments** - Explore various currency pairs

### Advanced Learning Path

Once comfortable with basic trading:

- **[Configuration Guide](../../explanation/configuration.md)** - Master all configuration patterns
- **[Streaming Data](../../explanation/streaming.md)** - Real-time price feeds for your applications
- **[Error Handling](../../explanation/error-handling.md)** - Production-ready error management
- **[Best Practices](../../explanation/best-practices.md)** - Trading application patterns and best practices

### Building Trading Applications

Ready to build more sophisticated systems:

- **[API Reference](../../api-reference/client.md)** - Complete client documentation
- **[Models Reference](../../api-reference/models/index.md)** - All available data models
- **[Examples](https://github.com/NimbleOx/fivetwenty/blob/main/docs/examples/notebooks/quick-start.ipynb)** - Real-world implementation examples

### Important Reminders

⚠️  **Practice First**: Always test strategies in practice environment
💰 **Risk Management**: Never risk more than you can afford to lose
🔐 **Security**: Keep your API tokens secure and rotate them regularly
📊 **Monitoring**: Track your trading performance and learn from results

### Getting Help

If you encounter issues:

- Check the [troubleshooting section](#troubleshooting-common-issues) above
- Review the [error handling guide](../../explanation/error-handling.md)
- Consult the [API documentation](../../api-reference/index.md) for detailed references

Happy trading with FiveTwenty! 🚀