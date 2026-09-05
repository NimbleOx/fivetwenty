# Account Management with FiveTwenty

Learn how to monitor account health, manage multiple accounts, and track account-level metrics using FiveTwenty's account and position APIs.

!!! success "Practical Guide - Problem-oriented solutions"
    **Use this guide when:** You need to manage OANDA accounts and monitor account health

    **Learning outcome:** Effectively monitor and manage trading accounts using FiveTwenty

    **Time commitment:** 20-30 minutes

## Prerequisites

- Completed [Basic Trading](basic-trading/index.md) tutorial
- Understanding of margin and account concepts
- FiveTwenty setup with live or practice account

## Essential Account Operations

### Account Health Monitoring

Good account management starts with knowing your account's current financial state. Metrics like margin utilization, unrealized P&L, and active positions surface risk before it becomes critical. This example retrieves account details and calculates health indicators that warn you when the account approaches dangerous margin levels.

Margin calls occur when your margin utilization exceeds broker thresholds (typically 50% for OANDA). If you monitor your margin ratio and exposure continuously, you can reduce risk before a forced liquidation rather than after. The example buckets margin usage into three statuses: HEALTHY (<30%), CAUTION (30-50%), and RISK (>50%).

<!-- filepath: docs/tutorials/account-management/example_account_health.py -->
```python
"""Demonstrate comprehensive account health monitoring with real-time risk assessment.

This example shows how to:
- Retrieve detailed account information using TypedDict responses
- Calculate key financial metrics using Decimal for precision
- Assess margin usage and risk levels
- Monitor active positions and exposure
"""

import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def get_account_health(client: AsyncClient) -> dict[str, Any]:
    """Calculate comprehensive account health metrics with risk assessment."""

    # ==============================================================================
    # STEP 1: RETRIEVE CURRENT ACCOUNT DETAILS
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.accounts.get_account()
    # ==============================================================================
    #
    # Retrieve detailed account information and state
    #
    # Parameters:
    #   - account_id: Your OANDA account ID (available as client.account_id)
    #
    # Returns: TypedDict with structure:
    #   {
    #       "account": Account,           # Pydantic Account model
    #       "lastTransactionID": str
    #   }
    #
    # NOTE: Response is a TypedDict (use dictionary access: response["account"])
    #       Account is a Pydantic model (use attribute access: account.balance)

    account_response = await client.accounts.get_account(client.account_id)
    account = account_response["account"]  # Extract Account model from response

    # ==============================================================================
    # STEP 2: RETRIEVE ALL POSITIONS FOR RISK ASSESSMENT
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.positions.get_positions()
    # ==============================================================================
    #
    # Get all positions for an account
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #
    # Returns: TypedDict with structure:
    #   {
    #       "positions": list[Position],  # List of Pydantic Position models
    #       "lastTransactionID": str
    #   }
    #
    # NOTE: Each Position has long and short attributes with units and P&L

    positions_response = await client.positions.get_positions(client.account_id)
    positions_list = positions_response["positions"]  # Extract positions list

    # ==============================================================================
    # STEP 3: CALCULATE AGGREGATE EXPOSURE AND P&L
    # ==============================================================================

    # Initialize risk tracking variables
    # Use Decimal for all financial calculations to avoid floating-point errors
    total_exposure = Decimal("0")  # Sum of all position sizes
    unrealized_pnl = Decimal("0")  # Total unrealized profit/loss
    active_positions = 0            # Count of non-zero positions

    # Iterate through all positions and aggregate metrics
    for position in positions_list:
        # Check if position has any open long or short units
        if position.long.units != "0" or position.short.units != "0":
            # Convert string values to Decimal for precise arithmetic
            # OANDA returns units as strings to preserve precision
            long_units = Decimal(position.long.units) if position.long.units != "0" else Decimal("0")
            short_units = Decimal(position.short.units) if position.short.units != "0" else Decimal("0")
            net_units = long_units + short_units

            # Only count positions with net exposure
            if net_units != 0:
                active_positions += 1
                total_exposure += abs(net_units)
                unrealized_pnl += Decimal(position.unrealized_pl)  # Paper profit/loss

    # ==============================================================================
    # STEP 4: CALCULATE MARGIN UTILIZATION AND RISK METRICS
    # ==============================================================================

    # Extract core account metrics from Account model
    # All OANDA monetary values are strings - convert to Decimal for calculations
    balance = Decimal(account.balance)              # Total account value
    margin_used = Decimal(account.margin_used)      # Margin locked in positions
    margin_available = Decimal(account.margin_available)  # Margin free to use

    # Calculate margin utilization ratio as percentage
    # High margin ratio (>50%) indicates increased liquidation risk
    margin_ratio = (margin_used / balance) * 100 if balance > 0 else Decimal("0")
    margin_call_level = Decimal("50")  # OANDA typically issues margin calls at 50%

    # ==============================================================================
    # STEP 5: RETURN COMPREHENSIVE HEALTH ASSESSMENT
    # ==============================================================================

    # Health status provides quick visual indicator:
    # HEALTHY: <30% margin usage - low risk
    # CAUTION: 30-50% margin usage - moderate risk
    # RISK: >50% margin usage - high liquidation risk

    return {
        "account_balance": balance,
        "nav": Decimal(account.nav),  # Net Asset Value (balance + unrealized P&L)
        "unrealized_pnl": unrealized_pnl,
        "margin_used": margin_used,
        "margin_available": margin_available,
        "margin_ratio": margin_ratio,
        "margin_call_risk": margin_ratio > margin_call_level,
        "active_positions": active_positions,
        "total_exposure": total_exposure,
        "health_status": "HEALTHY" if margin_ratio < 30 else "CAUTION" if margin_ratio < 50 else "RISK"
    }


async def main() -> None:
    """Execute account health monitoring demonstration."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:

        # ==============================================================================
        # MONITOR ACCOUNT HEALTH
        # ==============================================================================

        # Get comprehensive health metrics
        health = await get_account_health(client)

        # Display key metrics for quick health assessment
        print(f"Account Balance: ${health['account_balance']}")
        print(f"Margin Used: {health['margin_ratio']:.1f}%")
        print(f"Health Status: {health['health_status']}")
        print(f"Active Positions: {health['active_positions']}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Multi-Account Management

You can create as many clients as you need to access different accounts with OANDA. Common scenarios include separating long and short positions to comply with US broker hedging rules, isolating different trading strategies to manage risk, or maintaining separate accounts for testing versus live trading.

For traders subject to US broker hedging rules, using separate long and short accounts provides a compliant way to maintain opposing positions in the same currency pair. This approach allows you to hedge positions without violating FIFO (First In, First Out) rules that prevent holding both long and short positions simultaneously in a single account.

<!-- filepath: docs/tutorials/account-management/example_multi_account_hedging.py -->
```python
"""Demonstrate multi-account hedging strategy for US broker compliance.

This example shows how to:
- Configure multiple AsyncClient instances with different accounts
- Use AccountConfig for explicit account configuration
- Manage separate long and short accounts for FIFO compliance
- Execute hedging strategies across multiple accounts
"""

import asyncio
import os

from dotenv import load_dotenv
from pydantic import SecretStr

from fivetwenty import AccountConfig, AsyncClient, Environment

load_dotenv()


async def execute_long_strategy(client: AsyncClient) -> None:
    """Execute bullish trading strategy with account validation."""

    # ==============================================================================
    # VALIDATE LONG ACCOUNT ACCESSIBILITY
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.accounts.get_accounts()
    # ==============================================================================
    #
    # List all accounts associated with the authentication token
    #
    # Parameters: None (uses authenticated token to list accessible accounts)
    #
    # Returns: list[AccountProperties]  # Direct list of account summaries
    #
    # NOTE: This validates the account is accessible with the provided token
    #       Unlike most SDK methods, this returns a list directly (not a TypedDict)

    accounts_list = await client.accounts.get_accounts()  # Direct list return

    # Display strategy confirmation
    print(f"Long strategy executed on account: {client.config.alias}")
    print(f"Account validation: {len(accounts_list)} account(s) accessible")
    print("Ready for bullish position management")


async def execute_short_strategy(client: AsyncClient) -> None:
    """Execute bearish trading strategy with account validation."""

    # ==============================================================================
    # VALIDATE SHORT ACCOUNT ACCESSIBILITY
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.accounts.get_accounts()
    # ==============================================================================
    #
    # List all accounts associated with the authentication token
    #
    # Parameters: None (uses authenticated token to list accessible accounts)
    #
    # Returns: list[AccountProperties]  # Direct list of account summaries
    #
    # NOTE: Unlike most SDK methods, this returns a list directly (not a TypedDict)

    accounts_list = await client.accounts.get_accounts()  # Direct list return

    # Display strategy confirmation
    print(f"Short strategy executed on account: {client.config.alias}")
    print(f"Account validation: {len(accounts_list)} account(s) accessible")
    print("Ready for bearish position management and hedging")


async def main() -> None:
    """Demonstrate multi-account hedging for US FIFO compliance."""

    # ==============================================================================
    # CONFIGURE DEDICATED LONG ACCOUNT
    # ==============================================================================

    # AccountConfig provides explicit configuration for multi-account scenarios
    # Separate long account enables compliance with US FIFO regulations
    #
    # US broker rules prevent holding both long and short positions in a single
    # account. Using separate accounts allows hedging without FIFO violations.

    # For demonstration, fall back to default account if multi-account vars not set
    # In production, you would use separate LONG_ACCOUNT_* and SHORT_ACCOUNT_* variables
    long_token = os.environ.get("LONG_ACCOUNT_TOKEN") or os.environ["FIVETWENTY_OANDA_TOKEN"]
    long_account = os.environ.get("LONG_ACCOUNT_ID") or os.environ["FIVETWENTY_OANDA_ACCOUNT"]
    short_token = os.environ.get("SHORT_ACCOUNT_TOKEN") or os.environ["FIVETWENTY_OANDA_TOKEN"]
    short_account = os.environ.get("SHORT_ACCOUNT_ID") or os.environ["FIVETWENTY_OANDA_ACCOUNT"]

    long_config = AccountConfig(
        token=SecretStr(long_token),    # Dedicated token for long account
        account_id=SecretStr(long_account),  # Long position account identifier
        environment=Environment.PRACTICE,  # Practice environment for demonstration
        alias="long_positions",  # Descriptive alias for identification
    )

    # ==============================================================================
    # CONFIGURE DEDICATED SHORT ACCOUNT
    # ==============================================================================

    # Separate short account allows hedging without violating broker rules
    # Each account can hold positions in the same instrument without conflicts
    # For demonstration, falls back to same account if separate account not configured

    short_config = AccountConfig(
        token=SecretStr(short_token),   # Dedicated token for short account
        account_id=SecretStr(short_account), # Short position account identifier
        environment=Environment.PRACTICE,  # Practice environment for demonstration
        alias="short_positions",  # Descriptive alias for identification
    )

    # ==============================================================================
    # EXECUTE HEDGED TRADING STRATEGY
    # ==============================================================================

    # Multiple AsyncClient instances enable simultaneous management of separate accounts
    # Context managers ensure proper cleanup of HTTP connections for both clients

    async with AsyncClient(config=long_config) as long_client:
        async with AsyncClient(config=short_config) as short_client:

            print("Executing multi-account hedging strategy")
            print("Long positions will be managed on dedicated account")
            print("Short positions will be managed on separate account")

            # ==============================================================================
            # EXECUTE BULLISH STRATEGY ON LONG ACCOUNT
            # ==============================================================================

            # Long account handles all buy positions for the strategy
            await execute_long_strategy(long_client)

            # ==============================================================================
            # EXECUTE BEARISH STRATEGY ON SHORT ACCOUNT
            # ==============================================================================

            # Short account provides hedge against long positions
            await execute_short_strategy(short_client)


if __name__ == "__main__":
    asyncio.run(main())
```

### Account Performance Tracking

This example analyzes your transaction history to calculate win rate, average profit per trade, and total realized P&L. Tracked over time, these numbers tell you which strategies are working and flag deteriorating performance before it does much damage to your account.

The transaction history API exposes all ORDER_FILL transactions, which represent completed trades with realized profit or loss. Filter for those and aggregate the P&L, and you have an objective record of how your trading approach actually performs, whether the trades came from a systematic strategy or discretionary decisions.

<!-- filepath: docs/tutorials/account-management/example_performance_tracking.py -->
```python
"""Demonstrate account performance tracking with transaction analysis.

This example shows how to:
- Track account performance over a specified time period
- Analyze transaction history for realized P&L
- Calculate win rate and average profit per trade
- Monitor Net Asset Value (NAV) changes
"""

import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def track_account_performance(
    client: AsyncClient,
    account_id: str,
    transaction_count: int = 100
) -> dict[str, Any]:
    """Track account performance metrics from recent transactions."""

    # ==============================================================================
    # STEP 1: RETRIEVE CURRENT ACCOUNT STATE
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.accounts.get_account()
    # ==============================================================================
    #
    # Retrieve detailed account information and state
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #
    # Returns: TypedDict with structure:
    #   {
    #       "account": Account,           # Pydantic Account model
    #       "lastTransactionID": str
    #   }

    account_response = await client.accounts.get_account(account_id)
    account = account_response["account"]  # Extract Account model
    current_nav = Decimal(account.nav)  # Net Asset Value (balance + unrealized P&L)

    # ==============================================================================
    # STEP 2: RETRIEVE RECENT TRANSACTION HISTORY
    # ==============================================================================

    # ==============================================================================
    # SDK METHOD: client.transactions.get_recent_transactions()
    # ==============================================================================
    #
    # Get the most recent transactions for an account
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #   - count: Number of recent transactions to retrieve (max 500)
    #
    # Returns: TypedDict with structure:
    #   {
    #       "transactions": list[Transaction],  # List of Transaction union models
    #       "lastTransactionID": str
    #   }
    #
    # NOTE: Transaction models vary by type (ORDER_FILL, STOP_LOSS_ORDER, etc.)
    #       Only ORDER_FILL transactions have realized P&L (pl attribute)
    #
    # For demonstration, retrieve recent transactions
    # In production, adjust count based on your analysis needs (max 500)

    transactions_response = await client.transactions.get_recent_transactions(
        account_id=account_id,
        count=transaction_count
    )
    transactions_list = transactions_response["transactions"]  # Extract list

    # ==============================================================================
    # STEP 3: CALCULATE PERFORMANCE METRICS FROM TRANSACTIONS
    # ==============================================================================

    # Initialize performance tracking variables
    total_realized_pnl = Decimal("0")  # Sum of all realized profit/loss
    total_trades = 0                    # Count of closed positions
    winning_trades = 0                  # Count of profitable trades

    # Analyze each transaction for realized P&L
    for transaction in transactions_list:
        # Check if transaction has realized profit/loss (ORDER_FILL transactions)
        # Use hasattr for type safety since not all transaction types have pl attribute
        if hasattr(transaction, 'pl') and transaction.pl:
            realized_pnl = Decimal(transaction.pl)  # Realized profit/loss for this trade
            total_realized_pnl += realized_pnl
            total_trades += 1

            # Track winning vs losing trades
            if realized_pnl > 0:
                winning_trades += 1

    # ==============================================================================
    # STEP 4: CALCULATE AGGREGATE PERFORMANCE RATIOS
    # ==============================================================================

    # Calculate win rate percentage (avoid division by zero)
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else Decimal("0")

    # Calculate average profit per trade
    avg_pnl_per_trade = total_realized_pnl / total_trades if total_trades > 0 else Decimal("0")

    # ==============================================================================
    # STEP 5: RETURN COMPREHENSIVE PERFORMANCE METRICS
    # ==============================================================================

    return {
        "transactions_analyzed": transaction_count,
        "current_nav": current_nav,
        "total_realized_pnl": total_realized_pnl,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "win_rate": win_rate,
        "avg_pnl_per_trade": avg_pnl_per_trade
    }


async def main() -> None:
    """Execute account performance tracking demonstration."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:

        # ==============================================================================
        # TRACK ACCOUNT PERFORMANCE
        # ==============================================================================

        # Analyze recent transaction history (last 100 transactions)
        performance = await track_account_performance(client, client.account_id, transaction_count=100)

        # Display performance summary
        print("Account Performance Summary:")
        print(f"Transactions Analyzed: {performance['transactions_analyzed']}")
        print(f"Current NAV: ${performance['current_nav']}")
        print(f"Realized P&L: ${performance['total_realized_pnl']:+}")
        print(f"Win Rate: {performance['win_rate']:.1f}%")
        print(f"Total Trades: {performance['total_trades']}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Learn [Risk Management](risk-management.md) for account-level risk controls
- Explore [Advanced Orders](advanced-orders/index.md) for more order types and management techniques
- See [Best Practices](../guides/understanding/best-practices.md) for production account management

If you need dashboards or reporting beyond this, the account data retrieved through FiveTwenty is a reasonable base to build on, whether in a BI tool or a custom dashboard.
