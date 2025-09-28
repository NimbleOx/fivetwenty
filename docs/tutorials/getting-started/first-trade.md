# Your First Trade

This guide walks you through placing your first trade using FiveTwenty. We'll cover the complete process from authentication to order execution using modern configuration patterns.

## Prerequisites

Before starting, ensure you have:

- [Installed the SDK](installation.md)
- [Set up authentication](authentication.md) and obtained your API token
- A practice account with OANDA
- Your credentials configured (see authentication guide for options)

## Configuration Setup

Using your `.env` file from the authentication setup:

```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def main() -> None:
    # Zero-config initialization - automatically uses environment variables
    async with AsyncClient() as client:
        print(f"Connected: {client.config.summary()}")

asyncio.run(main())
```

## Check Account Balance

Before trading, verify your account status and available funds:

<!-- fragment: Demo account checking with return type annotations and exception handling -->
```python
async def check_account(client) -> None:
    """Check account balance and trading capacity."""
    # Get account list (we'll use the first one)
    accounts = await client.accounts.get_accounts()
    if not accounts:
        raise RuntimeError("No accounts found")

    # Get detailed account information
    account = await client.accounts.get_account(accounts[0].id)

    print(f"Account Summary: {client.config.summary()}")
    print(f"Balance: {account.balance} {account.currency}")
    print(f"Unrealized P/L: {account.unrealized_pl}")
    print(f"Open Trades: {account.open_trade_count}")
    print(f"Margin Used: {account.margin_used}")
    print(f"Margin Available: {account.margin_available}")

    return account
```

## Get Current Prices

Check current market prices before placing orders:

<!-- fragment: Demo price retrieval with return type annotations and attribute access issues -->
```python
async def get_price(client, instrument: str = "EUR_USD"):
    """Get current pricing for an instrument."""
    # The SDK automatically uses the configured account ID
    prices = await client.pricing.get_pricing(
        account_id=client.account_id,
        instruments=[instrument],
    )

    price = prices[0]
    print(f"\n{instrument} Pricing:")
    print(f"   Bid: {price.bids[0].price if price.bids else 'N/A'}")
    print(f"   Ask: {price.asks[0].price if price.asks else 'N/A'}")
    print(f"   Spread: {price.spread}")
    print(f"   Time: {price.time}")

    return price
```

## Place a Market Order

Place your first market order using the configured account:

<!-- fragment: Demo market order placement with f-string and return type patterns -->
```python
async def place_market_order(client, instrument: str = "EUR_USD", units: int = 1000):
    """Place a market order."""
    print(f"\nPlacing {('BUY' if units > 0 else 'SELL')} order:")
    print(f"   Instrument: {instrument}")
    print(f"   Units: {units}")

    # Place market order (SDK uses configured account ID)
    order_response = await client.orders.post_market_order(
        account_id=client.account_id,  # Uses configured account
        instrument=instrument,
        units=units,  # Positive for buy, negative for sell
    )

    if order_response.order_fill_transaction:
        fill = order_response.order_fill_transaction
        print(f"\n✅ Order Executed Successfully!")
        print(f"   Trade ID: {fill.id}")
        print(f"   Instrument: {fill.instrument}")
        print(f"   Units: {fill.units}")
        print(f"   Fill Price: {fill.price}")
        print(f"   P/L: {fill.pl}")
        print(f"   Time: {fill.time}")

        # Show commission if any
        if hasattr(fill, "commission") and fill.commission:
            print(f"   Commission: {fill.commission}")

        return fill
    else:
        print("❌ Order was not filled")
        if hasattr(order_response, "error_message"):
            print(f"   Error: {order_response.error_message}")
        return None
```

## Complete First Trade Example

Here's a complete example that combines all steps using the new configuration system:

<!-- fragment: Demo complete first trade with attribute access and call argument issues -->
```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

# Load environment variables from .env file
load_dotenv()

async def first_trade_example() -> None:
    """Complete first trade example using FiveTwenty."""

    # Zero-config initialization using .env file
    async with AsyncClient() as client:
        try:
            print("🚀 Starting your first trade with FiveTwenty!")
            print(f"Configuration: {client.config.summary()}")

            # 1. Check account status
            account = await check_account(client)

            # Verify we have sufficient margin
            if float(account.margin_available) < 100:
                print("⚠️ Warning: Low margin available for trading")
                return

            # 2. Get current market price
            instrument = "EUR_USD"
            current_price = await get_price(client, instrument)

            # 3. Place a small market order (1000 units)
            print(f"\nPlacing your first trade...")
            fill_transaction = await place_market_order(client, instrument, 1000)

            if fill_transaction:
                # 4. Check the resulting position
                await check_position(client, instrument)

                # 5. Show updated account balance
                print("\nUpdated Account Status:")
                updated_account = await client.accounts.get_account(client.account_id)
                print(f"   New Balance: {updated_account.balance}")
                print(f"   Unrealized P/L: {updated_account.unrealized_pl}")

                print("\n🎉 Congratulations! You've executed your first trade!")
                print("\nNext steps:")
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

async def check_position(client, instrument: str) -> None:
    """Check open position for an instrument."""
    positions = await client.positions.get_open_positions(client.account_id)

    for position in positions:
        if position.instrument == instrument:
            print(f"\nOpen Position for {instrument}:")

            if position.long.units != "0":
                print(f"   Long Position:")
                print(f"      Units: {position.long.units}")
                print(f"      Avg Price: {position.long.average_price}")
                print(f"      Unrealized P/L: {position.long.unrealized_pl}")

            if position.short.units != "0":
                print(f"   Short Position:")
                print(f"      Units: {position.short.units}")
                print(f"      Avg Price: {position.short.average_price}")
                print(f"      Unrealized P/L: {position.short.unrealized_pl}")

            break
    else:
        print(f"\nNo open position found for {instrument}")

# Run the complete example
if __name__ == "__main__":
    asyncio.run(first_trade_example())
```

## Close a Position

Once you have an open trade, you can close it using the dedicated `close_trade` method:

<!-- fragment: Demo trade closing with docstring format and f-string issues -->
```python
import asyncio
from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

# Load environment variables from .env file
load_dotenv()

async def close_trade_example() -> None:
    """Example of closing a trade."""
    async with AsyncClient() as client:
        try:
            # First, get list of open trades
            trades = await client.trades.get_open_trades(client.account_id)

            if not trades:
                print("No open trades to close")
                return

            # Close the first open trade (or find specific trade you want to close)
            trade_to_close = trades[0]
            print(f"Closing trade: {trade_to_close.id} ({trade_to_close.instrument})")

            # Close the trade
            close_response = await client.trades.close_trade(
                account_id=client.account_id,
                trade_id=trade_to_close.id
            )

            if close_response.order_fill_transaction:
                fill = close_response.order_fill_transaction
                print(f"\n✅ Trade Closed Successfully!")
                print(f"   Trade ID: {trade_to_close.id}")
                print(f"   Instrument: {trade_to_close.instrument}")
                print(f"   Close Price: {fill.price}")
                print(f"   Realized P/L: {fill.pl}")
                print(f"   Close Time: {fill.time}")

                # Check updated account balance
                account = await client.accounts.get_account(client.account_id)
                print(f"\nUpdated Account:")
                print(f"   Balance: {account.balance}")
                print(f"   Open Trade Count: {account.open_trade_count}")
            else:
                print("❌ Failed to close trade")

        except FiveTwentyError as e:
            print(f"❌ Error closing trade: {e}")

if __name__ == "__main__":
    asyncio.run(close_trade_example())
```

## Common Issues

If you encounter issues while making your first trade:

- **Authentication errors** - Verify your API token and account ID are correct
- **Insufficient margin** - Check your account balance and reduce position size
- **Market closed** - Forex markets are closed on weekends and holidays
- **Network issues** - Ensure stable internet connection

!!! warning "Troubleshooting Resources"
    For comprehensive error handling and troubleshooting guidance:

    - **Configuration issues**: See [Configuration Guide](../../guides/understanding/configuration.md#troubleshooting)
    - **Trading errors**: See [Error Handling Guide](../../api-reference/error-handling.md#common-trading-errors)
    - **Network problems**: See [Error Handling Guide](../../api-reference/error-handling.md#retry-strategies)

## Next Steps

🎉 **Congratulations!** You've successfully executed your first trade with FiveTwenty!


### Important Reminders

**Practice First**: Always test strategies in practice environment
**Risk Management**: Never risk more than you can afford to lose
**Security**: Keep your API tokens secure and rotate them regularly
**Monitoring**: Track your trading performance and learn from results

### Getting Help

If you encounter issues:

- Check the [Common Issues section](#common-issues) above
- Review the [error handling guide](../../api-reference/error-handling.md)
- Consult the [API documentation](../../api-reference/index.md) for detailed references

Happy trading with FiveTwenty! 🚀
