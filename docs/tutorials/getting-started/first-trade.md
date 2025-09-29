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

# Step 1: Load environment variables from .env file
# This reads FIVETWENTY_OANDA_TOKEN, FIVETWENTY_OANDA_ACCOUNT, and FIVETWENTY_OANDA_ENVIRONMENT
load_dotenv()

async def main() -> None:
    """Initialize FiveTwenty client with environment-based configuration."""

    # Step 2: Create AsyncClient with zero-config setup
    # AsyncClient automatically reads configuration from environment variables
    async with AsyncClient() as client:
        # Step 3: Verify successful connection and display configuration summary
        # The summary shows environment, account ID, and connection status
        print(f"Success Connected: {client.config.summary()}")

# Step 4: Execute the connection test
if __name__ == "__main__":
    asyncio.run(main())
```

## Check Account Balance

Before trading, verify your account status and available funds:

<!-- fragment: Demo account checking with return type annotations and exception handling -->
```python
async def check_account(client) -> None:
    """Comprehensive account status check for trading readiness assessment."""

    # Step 1: Retrieve all accounts accessible with current API token
    # Most users have one account, but business accounts may have multiple sub-accounts
    accounts = await client.accounts.get_accounts()
    if not accounts:
        raise RuntimeError("No trading accounts found - verify API token permissions")

    # Step 2: Get comprehensive account details for trading capacity analysis
    # Account object contains balance, margin, open positions, and trading statistics
    account = await client.accounts.get_account(accounts[0].id)

    # Step 3: Display comprehensive account status for trading assessment
    print(f"\nData Account Summary: {client.config.summary()}")

    # Step 4: Show account balance (total equity including unrealized P&L)
    # Balance represents your total account value in the account's base currency
    print(f"Balance Balance: {account.balance} {account.currency}")

    # Step 5: Display unrealized P&L from open positions
    # Unrealized P&L shows floating profit/loss that hasn't been locked in yet
    print(f"Analysis Unrealized P/L: {account.unrealized_pl} {account.currency}")

    # Step 6: Show current trading activity level
    # Open trade count indicates how many active positions require monitoring
    print(f"Processing Open Trades: {account.open_trade_count}")

    # Step 7: Display margin utilization for risk assessment
    # Margin used shows capital committed to maintaining open positions
    print(f"Secure Margin Used: {account.margin_used} {account.currency}")

    # Step 8: Show available trading capacity
    # Margin available determines maximum new position size you can open
    print(f"💸 Margin Available: {account.margin_available} {account.currency}")

    return account
```

## Get Current Prices

Check current market prices before placing orders:

<!-- fragment: Demo price retrieval with return type annotations and attribute access issues -->
```python
async def get_price(client, instrument: str = "EUR_USD"):
    """Retrieve real-time market pricing for informed trading decisions."""

    # Step 1: Request live market pricing from OANDA's price engine
    # Real-time pricing ensures orders execute at expected price levels
    prices = await client.pricing.get_pricing(
        account_id=client.account_id,  # Account context affects pricing precision
        instruments=[instrument],      # List format allows batch price requests
    )

    # Step 2: Extract pricing data for the requested currency pair
    # Prices array contains one price object per requested instrument
    price = prices[0]  # Get first (and only) price from our single-instrument request

    # Step 3: Display comprehensive market pricing analysis
    print(f"\nExchange {instrument} Market Pricing:")

    # Step 4: Show bid price (highest price buyers are willing to pay)
    # Bid represents the price you receive when selling this currency pair
    print(f"   📉 Bid: {price.bids[0].price if price.bids else 'N/A'} (sell price)")

    # Step 5: Show ask price (lowest price sellers are willing to accept)
    # Ask represents the price you pay when buying this currency pair
    print(f"   Analysis Ask: {price.asks[0].price if price.asks else 'N/A'} (buy price)")

    # Step 6: Display spread (trading cost in price terms)
    # Spread = Ask - Bid, represents the cost of entering and exiting trades
    print(f"   Balance Spread: {price.spread} (trading cost)")

    # Step 7: Show pricing timestamp for data freshness verification
    # Recent timestamps ensure you're making decisions on current market conditions
    print(f"   Time Time: {price.time} (price generation time)")

    return price
```

## Place a Market Order

Place your first market order using the configured account:

<!-- fragment: Demo market order placement with f-string and return type patterns -->
```python
async def place_market_order(client, instrument: str = "EUR_USD", units: int = 1000):
    """Execute market order with immediate price execution and comprehensive reporting."""

    # Step 1: Display pre-execution order summary for confirmation
    direction = 'BUY' if units > 0 else 'SELL'  # Determine trade direction from units sign
    print(f"\nTarget Preparing {direction} order:")
    print(f"   Data Instrument: {instrument}")
    print(f"   Ruler Units: {units} ({'long position' if units > 0 else 'short position'})")

    # Step 2: Execute market order for immediate price execution
    # Market orders guarantee execution but not price - they fill at best available price
    order_response = await client.orders.post_market_order(
        account_id=client.account_id,  # Target account for order execution
        instrument=instrument,         # Currency pair identifier (e.g., "EUR_USD")
        units=units,                  # Position size: positive=long, negative=short
    )

    # Step 3: Verify successful order execution and extract trade details
    # Order fill transaction confirms the order was executed at market prices
    if order_response.order_fill_transaction:
        # Step 4: Extract comprehensive execution details for record keeping
        fill = order_response.order_fill_transaction

        print(f"\nSuccess Order Executed Successfully!")

        # Step 5: Display unique trade identifier for position tracking
        # Trade ID enables future position management and closing operations
        print(f"   ID Trade ID: {fill.id}")

        # Step 6: Confirm instrument execution (verification check)
        # Ensures the correct currency pair was traded as requested
        print(f"   Data Instrument: {fill.instrument}")

        # Step 7: Show actual units filled (should match request)
        # Confirms complete order execution without partial fills
        print(f"   Ruler Units: {fill.units} ({'LONG' if int(fill.units) > 0 else 'SHORT'} position)")

        # Step 8: Display actual execution price achieved
        # Fill price may differ slightly from quoted price due to market movement
        print(f"   Balance Fill Price: {fill.price} ({instrument.split('_')[1]} per {instrument.split('_')[0]})")

        # Step 9: Show immediate profit/loss (typically near zero for market orders)
        # P&L reflects difference between execution price and current market price
        print(f"   Analysis Immediate P/L: {fill.pl} {fill.account_currency if hasattr(fill, 'account_currency') else ''}")

        # Step 10: Record execution timestamp for trade history
        # Timestamp enables performance analysis and trade sequencing
        print(f"   Time Execution Time: {fill.time}")

        # Step 11: Display commission costs if applicable
        # Commission transparency helps calculate true trading costs
        if hasattr(fill, "commission") and fill.commission:
            print(f"   💸 Commission: {fill.commission}")

        return fill
    else:
        # Step 12: Handle rare case of unfilled market order
        # Market orders rarely fail but may be rejected due to market conditions
        print("Error Order was not filled - market may be closed or halted")

        # Step 13: Display specific error information if available
        # Error details help diagnose and resolve execution issues
        if hasattr(order_response, "error_message"):
            print(f"   ⚠️ Error Details: {order_response.error_message}")
        if hasattr(order_response, "order_reject_transaction"):
            print(f"   🚫 Rejection Reason: {order_response.order_reject_transaction.reject_reason}")

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

# Step 1: Load authentication and configuration from environment
# Reads FIVETWENTY_OANDA_TOKEN, FIVETWENTY_OANDA_ACCOUNT, and FIVETWENTY_OANDA_ENVIRONMENT
load_dotenv()

async def first_trade_example() -> None:
    """Complete end-to-end trading example with comprehensive error handling and reporting."""

    # Step 2: Initialize AsyncClient with automatic environment-based configuration
    # Zero-config approach simplifies setup while maintaining security best practices
    async with AsyncClient() as client:
        try:
            print("Starting Starting your first trade with FiveTwenty SDK!")
            print(f"List Configuration: {client.config.summary()}")

            # Step 3: Perform comprehensive account assessment for trading readiness
            # Account check verifies balance, margin, and trading capacity before execution
            account = await check_account(client)

            # Step 4: Validate sufficient margin for safe trading operations
            # Margin check prevents over-leveraging and ensures position sustainability
            if float(account.margin_available) < 100:
                print("⚠️ WARNING: Insufficient margin for safe trading")
                print(f"   Available: {account.margin_available} {account.currency}")
                print(f"   Recommended minimum: 100 {account.currency}")
                return

            # Step 5: Retrieve real-time market pricing for informed decision making
            instrument = "EUR_USD"  # Major currency pair with tight spreads and high liquidity
            current_price = await get_price(client, instrument)

            # Step 6: Execute conservative market order for first trading experience
            # 1000 units represents a small position suitable for learning and practice
            print(f"\nTarget Executing your first trade...")
            fill_transaction = await place_market_order(client, instrument, 1000)

            # Step 7: Process successful trade execution and analyze results
            if fill_transaction:
                # Step 8: Examine resulting position for portfolio impact assessment
                # Position check shows how the trade affects overall account exposure
                await check_position(client, instrument)

                # Step 9: Display updated account metrics post-trade
                # Account refresh shows immediate impact on balance and margin
                print("\nData Updated Account Status Post-Trade:")
                updated_account = await client.accounts.get_account(client.account_id)
                print(f"   Balance New Balance: {updated_account.balance} {updated_account.currency}")
                print(f"   Analysis Unrealized P/L: {updated_account.unrealized_pl} {updated_account.currency}")
                print(f"   Processing Open Trades: {updated_account.open_trade_count}")

                print("\nComplete SUCCESS! Your first trade has been executed successfully!")
                print("\n📚 Recommended Next Steps:")
                print("   • 👀 Monitor your position regularly")
                print("   • Security Consider setting stop-loss orders for risk management")
                print("   • Processing Practice with different currency pairs")
                print("   • 📖 Study advanced order types and strategies")

        except FiveTwentyError as e:
            # Step 10: Handle OANDA API-specific errors with detailed diagnostics
            # FiveTwentyError provides structured error information for troubleshooting
            print(f"Error OANDA API Error Encountered: {e}")
            print(f"   Numbers Error Code: {e.code if hasattr(e, 'code') else 'N/A'}")
            print(f"   💬 Message: {e.message if hasattr(e, 'message') else str(e)}")
            print(f"   Config Troubleshooting: Check API token, account ID, and market hours")
        except Exception as e:
            # Step 11: Handle unexpected errors with general guidance
            # Generic exception handling covers network, configuration, and system issues
            print(f"Error Unexpected Error: {e}")
            print("   Search Common causes: Network connectivity, configuration issues, or system problems")
            print("   Success Verify: API credentials, internet connection, and environment setup")

async def check_position(client, instrument: str) -> None:
    """Comprehensive position analysis for risk assessment and portfolio monitoring."""

    # Step 1: Retrieve all open positions for portfolio analysis
    # Position data includes size, direction, average price, and current P&L
    positions = await client.positions.get_open_positions(client.account_id)

    # Step 2: Search for specific instrument position in portfolio
    # Iterate through positions to find matching instrument
    for position in positions:
        if position.instrument == instrument:
            print(f"\nData Open Position Analysis for {instrument}:")

            # Step 3: Analyze long position details if present
            # Long positions profit when price increases above average entry price
            if position.long.units != "0":
                print(f"   Analysis Long Position (Bullish):")
                print(f"      Ruler Units: {position.long.units} (buy exposure)")
                print(f"      Balance Average Entry Price: {position.long.average_price}")
                print(f"      Data Current P/L: {position.long.unrealized_pl} (floating)")

            # Step 4: Analyze short position details if present
            # Short positions profit when price decreases below average entry price
            if position.short.units != "0":
                print(f"   📉 Short Position (Bearish):")
                print(f"      Ruler Units: {position.short.units} (sell exposure)")
                print(f"      Balance Average Entry Price: {position.short.average_price}")
                print(f"      Data Current P/L: {position.short.unrealized_pl} (floating)")

            break
    else:
        # Step 5: Handle case where no position exists for specified instrument
        print(f"\n🚫 No open position found for {instrument}")
        print(f"   Success Account has clean slate for this currency pair")

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
    """Comprehensive trade closure example with profit/loss analysis and account impact."""

    # Step 1: Initialize client for trade management operations
    # AsyncClient provides trade closure capabilities with immediate execution
    async with AsyncClient() as client:
        try:
            # Step 2: Retrieve all currently open trades for closure selection
            # Open trades represent active market positions requiring management
            trades = await client.trades.get_open_trades(client.account_id)

            # Step 3: Validate that trades exist before attempting closure
            # Empty trade list indicates no active positions to close
            if not trades:
                print("📭 No open trades available for closure")
                print("   Success Account has no active market exposure")
                return

            # Step 4: Select trade for closure (using first trade as example)
            # In practice, you might select based on P&L, age, or risk criteria
            trade_to_close = trades[0]
            print(f"Target Preparing to close trade: {trade_to_close.id}")
            print(f"   Data Instrument: {trade_to_close.instrument}")
            print(f"   Ruler Units: {trade_to_close.current_units}")
            print(f"   Analysis Current P/L: {trade_to_close.unrealized_pl}")

            # Step 5: Execute immediate trade closure at market price
            # Close trade command liquidates position at best available market price
            close_response = await client.trades.close_trade(
                account_id=client.account_id,    # Target account for closure
                trade_id=trade_to_close.id       # Specific trade to close
            )

            # Step 6: Process successful trade closure and analyze financial impact
            if close_response.order_fill_transaction:
                # Step 7: Extract closure details for comprehensive reporting
                fill = close_response.order_fill_transaction

                print(f"\nSuccess Trade Closed Successfully!")
                print(f"   ID Trade ID: {trade_to_close.id}")
                print(f"   Data Instrument: {trade_to_close.instrument}")
                print(f"   Balance Close Price: {fill.price}")
                print(f"   Analysis Realized P/L: {fill.pl} (locked in)")
                print(f"   Time Close Time: {fill.time}")

                # Step 8: Display updated account status post-closure
                # Account refresh shows immediate impact of realized P&L on balance
                account = await client.accounts.get_account(client.account_id)
                print(f"\nData Updated Account Status:")
                print(f"   Balance New Balance: {account.balance} {account.currency}")
                print(f"   Processing Remaining Open Trades: {account.open_trade_count}")
                print(f"   Analysis Total Unrealized P/L: {account.unrealized_pl} {account.currency}")

                # Step 9: Provide closure success confirmation
                profit_or_loss = "profit" if float(fill.pl) >= 0 else "loss"
                print(f"\nTarget Trade closure completed with {profit_or_loss}")
            else:
                # Step 10: Handle failed closure attempt
                print("Error Failed to close trade - market may be halted or trade already closed")

        except FiveTwentyError as e:
            # Step 11: Handle trade closure errors with specific guidance
            # Closure errors may indicate market conditions or trade state issues
            print(f"Error Trade Closure Error: {e}")
            print(f"   Config Possible causes: Market closed, trade already closed, or insufficient permissions")
            print(f"   Success Verify: Trade still exists, market hours, and account permissions")

# Step 12: Execute trade closure example
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

Complete **Congratulations!** You've successfully executed your first trade with FiveTwenty!


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

## Glossary

Understanding key terms used in this tutorial:

**Account ID**: Unique identifier for your OANDA trading account (format: XXX-XXX-XXXXXXX-XXX)

**API Token**: Authentication credential that grants access to your OANDA account via the API

**AsyncClient**: FiveTwenty's primary client for asynchronous operations - ideal for production applications

**Bid/Ask**: Bid is the price you can sell at, Ask is the price you can buy at - the difference is the spread

**Environment**: Trading context - PRACTICE uses virtual money, LIVE uses real funds

**Instrument**: Trading pair identifier (e.g., "EUR_USD" for Euro vs US Dollar)

**Market Order**: Order that executes immediately at the best available market price

**Position**: Your current exposure in a particular instrument (long = buying, short = selling)

**Spread**: Difference between bid and ask prices - represents the cost of trading

**Trade**: Individual order execution - multiple trades can contribute to one position

**Units**: Position size - positive numbers for long positions, negative for short positions

Happy trading with FiveTwenty! Starting
