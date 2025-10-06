# Your First Trade

This guide walks you through placing your first trade using FiveTwenty. We'll cover the complete process from authentication to order execution using modern configuration patterns.

## Prerequisites

Before starting, ensure you have:

- [Installed the SDK](installation.md)
- [Set up authentication](authentication.md) and obtained your API token
- A practice account with OANDA
- Your credentials configured (see authentication guide for options)

## Configuration Setup

FiveTwenty uses a zero-configuration approach that automatically reads your credentials from environment variables. This example demonstrates the simplest way to connect to OANDA - just load your `.env` file and create an `AsyncClient`. The client automatically discovers your API token, account ID, and environment (practice or live) from the `FIVETWENTY_OANDA_*` variables you configured during authentication setup.

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

Before placing any trades, it's essential to understand your account's financial position. This function retrieves comprehensive account information including your balance, unrealized profit/loss from open positions, margin usage, and available trading capacity. Checking these metrics helps you make informed decisions about position sizing and ensures you have sufficient margin to support new trades without risking a margin call.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """Comprehensive account status check for trading readiness assessment."""

    # Step 1: Initialize AsyncClient with automatic environment-based configuration
    async with AsyncClient() as client:
        # Step 2: Retrieve all accounts accessible with current API token
        # Most users have one account, but business accounts may have multiple sub-accounts
        accounts = await client.accounts.get_accounts()
        if not accounts:
            error_msg = "No trading accounts found - verify API token permissions"
            raise RuntimeError(error_msg)

        # Step 3: Get comprehensive account details for trading capacity analysis
        # Account response contains balance, margin, open positions, and trading statistics
        account_response = await client.accounts.get_account(accounts[0].id)
        account = account_response["account"]

        # Step 4: Display comprehensive account status for trading assessment
        print(f"\nData Account Summary: {client.config.summary()}")

        # Step 5: Show account balance (total equity including unrealized P&L)
        # Balance represents your total account value in the account's base currency
        print(f"Balance Balance: {account.balance} {account.currency}")

        # Step 6: Display unrealized P&L from open positions
        # Unrealized P&L shows floating profit/loss that hasn't been locked in yet
        print(f"Analysis Unrealized P/L: {account.unrealized_pl} {account.currency}")

        # Step 7: Show current trading activity level
        # Open trade count indicates how many active positions require monitoring
        print(f"Processing Open Trades: {account.open_trade_count}")

        # Step 8: Display margin utilization for risk assessment
        # Margin used shows capital committed to maintaining open positions
        print(f"Secure Margin Used: {account.margin_used} {account.currency}")

        # Step 9: Show available trading capacity
        # Margin available determines maximum new position size you can open
        print(f"💸 Margin Available: {account.margin_available} {account.currency}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Get Current Prices

Successful trading requires understanding current market conditions before executing orders. This function retrieves real-time pricing data from OANDA's streaming price engine, showing you the bid price (what you receive when selling), the ask price (what you pay when buying), and the spread between them. The spread represents your immediate trading cost - the difference between where you can buy and sell. Always check prices before trading to ensure you're getting fair execution and to understand your transaction costs.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """Retrieve real-time market pricing for informed trading decisions."""

    # Step 1: Initialize AsyncClient with automatic environment-based configuration
    async with AsyncClient() as client:
        # Step 2: Request live market pricing from OANDA's price engine
        # Real-time pricing ensures orders execute at expected price levels
        instrument = "EUR_USD"
        pricing_response = await client.pricing.get_pricing(
            account_id=client.account_id,  # Account context affects pricing precision
            instruments=[instrument],  # List format allows batch price requests
        )

        # Step 3: Extract pricing data for the requested currency pair
        # Pricing response contains prices array with one price object per instrument
        price = pricing_response["prices"][0]

        # Step 4: Display comprehensive market pricing analysis
        print(f"\nExchange {instrument} Market Pricing:")

        # Step 5: Show bid price (highest price buyers are willing to pay)
        # Bid represents the price you receive when selling this currency pair
        print(f"    Bid: {price.bids[0].price if price.bids else 'N/A'} (sell price)")

        # Step 6: Show ask price (lowest price sellers are willing to accept)
        # Ask represents the price you pay when buying this currency pair
        print(
            f"   Analysis Ask: {price.asks[0].price if price.asks else 'N/A'} (buy price)"
        )

        # Step 7: Display spread (trading cost in price terms)
        # Spread = Ask - Bid, represents the cost of entering and exiting trades
        if price.asks and price.bids:
            spread = price.asks[0].price - price.bids[0].price
            print(f"   Balance Spread: {spread:.5f} (trading cost)")

        # Step 8: Show pricing timestamp for data freshness verification
        # Recent timestamps ensure you're making decisions on current market conditions
        print(f"   Time Time: {price.time} (price generation time)")


if __name__ == "__main__":
    asyncio.run(main())
```

## Place a Market Order

Market orders are the simplest way to enter the market - they execute immediately at the best available price. Unlike limit orders that wait for a specific price, market orders guarantee execution but not price. This function demonstrates placing a market order by specifying the instrument (currency pair) and units (position size). Positive units create a long position (buying), while negative units create a short position (selling). The function provides detailed reporting of the execution, including the fill price, trade ID for future reference, and immediate profit/loss.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import InstrumentName

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """Execute market order with immediate price execution and comprehensive reporting."""

    # Step 1: Initialize AsyncClient with automatic environment-based configuration
    async with AsyncClient() as client:
        # Step 2: Display pre-execution order summary for confirmation
        instrument = InstrumentName.EUR_USD
        units = 1000
        direction = (
            "BUY" if units > 0 else "SELL"
        )  # Determine trade direction from units sign
        print(f"\nTarget Preparing {direction} order:")
        print(f"   Data Instrument: {instrument}")
        print(
            f"   Ruler Units: {units} ({'long position' if units > 0 else 'short position'})"
        )

        # Step 3: Execute market order for immediate price execution
        # Market orders guarantee execution but not price - they fill at best available price
        order_response = await client.orders.post_market_order(
            account_id=client.account_id,  # Target account for order execution
            instrument=instrument,  # Currency pair identifier (e.g., "EUR_USD")
            units=units,  # Position size: positive=long, negative=short
        )

        # Step 4: Verify successful order execution and extract trade details
        # Order fill transaction confirms the order was executed at market prices
        if order_response.order_fill_transaction:
            # Step 5: Extract comprehensive execution details for record keeping
            fill = order_response.order_fill_transaction

            print("\nSuccess Order Executed Successfully!")

            # Step 6: Display unique trade identifier for position tracking
            # Trade ID enables future position management and closing operations
            print(f"   ID Trade ID: {fill.id}")

            # Step 7: Confirm instrument execution (verification check)
            # Ensures the correct currency pair was traded as requested
            print(f"   Data Instrument: {fill.instrument}")

            # Step 8: Show actual units filled (should match request)
            # Confirms complete order execution without partial fills
            print(
                f"   Ruler Units: {fill.units} ({'LONG' if int(fill.units) > 0 else 'SHORT'} position)"
            )

            # Step 9: Display actual execution price achieved
            # Fill price may differ slightly from quoted price due to market movement
            instrument_parts = instrument.value.split("_")
            print(
                f"   Balance Fill Price: {fill.price} ({instrument_parts[1]} per {instrument_parts[0]})"
            )

            # Step 10: Show immediate profit/loss (typically near zero for market orders)
            # P&L reflects difference between execution price and current market price
            print(
                f"   Analysis Immediate P/L: {fill.pl} {fill.account_currency if hasattr(fill, 'account_currency') else ''}"
            )

            # Step 11: Record execution timestamp for trade history
            # Timestamp enables performance analysis and trade sequencing
            print(f"   Time Execution Time: {fill.time}")

            # Step 12: Display commission costs if applicable
            # Commission transparency helps calculate true trading costs
            if hasattr(fill, "commission") and fill.commission:
                print(f"   💸 Commission: {fill.commission}")
        else:
            # Step 13: Handle rare case of unfilled market order
            # Market orders rarely fail but may be rejected due to market conditions
            print("Error Order was not filled - market may be closed or halted")

            # Step 14: Display specific error information if available
            # Error details help diagnose and resolve execution issues
            if hasattr(order_response, "error_message"):
                print(f"   ⚠️ Error Details: {order_response.error_message}")
            if hasattr(order_response, "order_reject_transaction"):
                print(
                    f"   🚫 Rejection Reason: {order_response.order_reject_transaction.reject_reason}"
                )


if __name__ == "__main__":
    asyncio.run(main())

```

## Complete First Trade Example

This comprehensive example brings together all the pieces - authentication, account validation, price checking, and order execution - into a complete trading workflow. It demonstrates real-world patterns including margin validation (ensuring you have enough capital), risk assessment (checking if your position size is appropriate), and error handling (gracefully managing API errors or market conditions). The example uses a conservative 1000-unit position on EUR/USD, a highly liquid major currency pair with tight spreads, making it ideal for learning. Follow this pattern as a template for your own trading strategies.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import InstrumentName

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """Complete end-to-end trading example with comprehensive error handling and reporting."""

    # Step 1: Initialize AsyncClient with automatic environment-based configuration
    # Zero-config approach simplifies setup while maintaining security best practices
    async with AsyncClient() as client:
        try:
            print("Starting your first trade with FiveTwenty SDK!")
            print(f"Configuration: {client.config.summary()}")

            # Step 2: Perform comprehensive account assessment for trading readiness
            # Account check verifies balance, margin, and trading capacity before execution
            account_response = await client.accounts.get_account(client.account_id)
            account = account_response["account"]

            print(f"\nAccount Balance: {account.balance} {account.currency}")
            print(f"Margin Available: {account.margin_available} {account.currency}")

            # Step 3: Validate sufficient margin for safe trading operations
            # Margin check prevents over-leveraging and ensures position sustainability
            if float(account.margin_available) < 100:
                print("⚠️ WARNING: Insufficient margin for safe trading")
                print(f"   Available: {account.margin_available} {account.currency}")
                print(f"   Recommended minimum: 100 {account.currency}")
                return

            # Step 4: Retrieve real-time market pricing for informed decision making
            instrument = InstrumentName.EUR_USD
            pricing_response = await client.pricing.get_pricing(
                account_id=client.account_id, instruments=[instrument]
            )
            price = pricing_response["prices"][0]

            print(f"\n{instrument.value} Market Pricing:")
            print(f"   Bid: {price.bids[0].price if price.bids else 'N/A'}")
            print(f"   Ask: {price.asks[0].price if price.asks else 'N/A'}")

            # Step 5: Execute conservative market order for first trading experience
            # 1000 units represents a small position suitable for learning and practice
            print("\nExecuting your first trade...")
            units = 1000
            order_response = await client.orders.post_market_order(
                account_id=client.account_id, instrument=instrument, units=units
            )

            # Step 6: Process successful trade execution and analyze results
            if order_response.order_fill_transaction:
                fill = order_response.order_fill_transaction
                print("\nOrder Executed Successfully!")
                print(f"   Trade ID: {fill.id}")
                print(f"   Instrument: {fill.instrument}")
                print(f"   Units: {fill.units}")
                print(f"   Fill Price: {fill.price}")
                print(f"   P/L: {fill.pl}")

                # Step 7: Display updated account metrics post-trade
                # Account refresh shows immediate impact on balance and margin
                print("\nUpdated Account Status Post-Trade:")
                updated_response = await client.accounts.get_account(client.account_id)
                updated_account = updated_response["account"]
                print(
                    f"   New Balance: {updated_account.balance} {updated_account.currency}"
                )
                print(
                    f"   Unrealized P/L: {updated_account.unrealized_pl} {updated_account.currency}"
                )
                print(f"   Open Trades: {updated_account.open_trade_count}")

                print("\n SUCCESS! Your first trade has been executed successfully!")
                print("\n Recommended Next Steps:")
                print("   • Monitor your position regularly")
                print("   • Consider setting stop-loss orders for risk management")
                print("   • Practice with different currency pairs")
            else:
                print("Order was not filled - market may be closed or halted")

        except FiveTwentyError as e:
            # Step 8: Handle OANDA API-specific errors with detailed diagnostics
            # FiveTwentyError provides structured error information for troubleshooting
            print(f"OANDA API Error: {e}")
            print("Troubleshooting: Check API token, account ID, and market hours")
        except Exception as e:
            # Step 9: Handle unexpected errors with general guidance
            # Generic exception handling covers network, configuration, and system issues
            print(f"Unexpected Error: {e}")
            print("Verify: API credentials, internet connection, and environment setup")


if __name__ == "__main__":
    asyncio.run(main())
```

## Close a Position

Closing positions is just as important as opening them - it's how you realize profits or limit losses. This example demonstrates the complete trade closure workflow using FiveTwenty's `close_trade` method. The function retrieves your open trades, selects one to close (here we use the first trade, but in practice you'd select based on strategy or risk criteria), and executes an immediate market closure. Closing a trade converts unrealized P&L (floating profit/loss) into realized P&L (locked in), which directly impacts your account balance. The example shows comprehensive reporting including the close price, realized profit/loss, and updated account metrics.

```python
import asyncio

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import InstrumentName

# Load environment variables from .env file
load_dotenv()


async def close_trade_example() -> None:
    """Comprehensive trade lifecycle: open position, monitor status, then close with P/L analysis."""

    # Step 1: Initialize client for complete trade lifecycle management
    # AsyncClient handles order execution, trade monitoring, and closure operations
    async with AsyncClient() as client:
        try:
            print("Starting complete trade lifecycle demonstration...")
            print(f"Configuration: {client.config.summary()}\n")

            # Step 2: Open a new market position for demonstration
            # Market orders execute immediately at best available price
            instrument = InstrumentName.EUR_USD
            units = 1000  # Small position size for demonstration

            print(f"Opening {units} unit position in {instrument.value}...")
            order_response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units,
            )

            # Step 3: Verify order execution and extract trade information
            if not order_response.order_fill_transaction:
                print(" Order was not filled - market may be closed or halted")
                return

            fill = order_response.order_fill_transaction
            print(" Position opened successfully!")
            print(f"   Trade ID: {fill.id}")
            print(f"   Entry Price: {fill.price}")
            print(f"   Instrument: {fill.instrument}\n")

            # Step 4: Retrieve all currently open trades for closure selection
            # Open trades represent active market positions requiring management
            trades_response = await client.trades.get_open_trades(client.account_id)
            trades = trades_response["trades"]

            # Step 5: Validate that trades exist before attempting closure
            # Empty trade list indicates no active positions to close
            if not trades:
                print("📭 No open trades available for closure")
                print("   Account has no active market exposure")
                return

            # Step 6: Select trade for closure (using first trade as example)
            # In practice, you might select based on P&L, age, or risk criteria
            trade_to_close = trades[0]
            print(f"Preparing to close trade: {trade_to_close.id}")
            print(f"   Instrument: {trade_to_close.instrument}")
            print(f"   Units: {trade_to_close.current_units}")
            print(f"   Current P/L: {trade_to_close.unrealized_pl}\n")

            # Step 7: Execute immediate trade closure at market price
            # Close trade command liquidates position at best available market price
            print("Closing position...")
            close_response = await client.trades.close_trade(
                account_id=client.account_id,  # Target account for closure
                trade_specifier=trade_to_close.id,  # Specific trade to close
            )

            # Step 8: Process successful trade closure and analyze financial impact
            if close_response.get("orderFillTransaction"):
                # Step 9: Extract closure details for comprehensive reporting
                close_fill = close_response["orderFillTransaction"]

                print(" Trade closed successfully!")
                print(f"   Trade ID: {trade_to_close.id}")
                print(f"   Instrument: {trade_to_close.instrument}")
                print(f"   Close Price: {close_fill['price']}")
                print(f"   Realized P/L: {close_fill['pl']}")
                print(f"   Close Time: {close_fill['time']}\n")

                # Step 10: Display updated account status post-closure
                # Account refresh shows immediate impact of realized P&L on balance
                account_response = await client.accounts.get_account(client.account_id)
                account = account_response["account"]
                print("Updated Account Status:")
                print(f"   Balance: {account.balance} {account.currency}")
                print(f"   Remaining Open Trades: {account.open_trade_count}")
                print(
                    f"   Total Unrealized P/L: {account.unrealized_pl} {account.currency}"
                )

                # Step 11: Provide lifecycle completion confirmation
                profit_or_loss = "profit" if float(close_fill["pl"]) >= 0 else "loss"
                print(f"\n Complete trade lifecycle finished with {profit_or_loss}")
            else:
                # Step 12: Handle failed closure attempt
                print(
                    " Failed to close trade - market may be halted or trade already closed"
                )

        except FiveTwentyError as e:
            # Step 13: Handle trading errors with specific guidance
            # Trading errors may indicate market conditions, permissions, or connectivity issues
            print(f" Trading Error: {e}")
            print("   Troubleshooting:")
            print("   • Verify market hours (forex markets trade 24/5)")
            print("   • Check API token permissions")
            print("   • Ensure sufficient margin available")


# Execute complete trade lifecycle example
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

Happy trading with FiveTwenty!
