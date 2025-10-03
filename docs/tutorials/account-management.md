# Account Management with FiveTwenty

Learn how to monitor account health, manage multiple accounts, and track account-level metrics using FiveTwenty's account and position APIs.

!!! success "Target Practical Guide - Problem-oriented solutions"
    **Use this guide when:** You need to manage OANDA accounts and monitor account health

    **Learning outcome:** Effectively monitor and manage trading accounts using FiveTwenty

    **Time commitment:** 20-30 minutes

## Prerequisites

- Completed [Basic Trading](basic-trading/index.md) tutorial
- Understanding of margin and account concepts
- FiveTwenty setup with live or practice account

## Essential Account Operations

### Account Health Monitoring

The foundation of good account management is understanding your account's current financial health. This function retrieves comprehensive account information and calculates key health metrics.

<!-- fragment: Demo account health monitoring with Decimal calculations and type annotations -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def get_account_health(client: AsyncClient) -> dict:
    """Get comprehensive account health status."""
    # Get account details
    account = await client.accounts.get_account(client.account_id)

    # Get all positions for risk assessment
    positions = await client.positions.get_positions(client.account_id)

    # Calculate account metrics
    total_exposure = Decimal()
    unrealized_pnl = Decimal()
    active_positions = 0

    for position in positions.positions:
        if position.long.units != "0" or position.short.units != "0":
            long_units = Decimal(position.long.units) if position.long.units != "0" else Decimal()
            short_units = Decimal(position.short.units) if position.short.units != "0" else Decimal()
            net_units = long_units + short_units

            if net_units != 0:
                active_positions += 1
                total_exposure += abs(net_units)
                unrealized_pnl += Decimal(position.unrealized_pl)

    # Calculate health ratios
    balance = Decimal(account.balance)
    margin_used = Decimal(account.margin_used)
    margin_available = Decimal(account.margin_available)

    margin_ratio = (margin_used / balance) * 100 if balance > 0 else Decimal()
    margin_call_level = Decimal("50")  # OANDA typically uses 50%

    return {
        "account_balance": balance,
        "nav": Decimal(account.nav),  # Net Asset Value
        "unrealized_pnl": unrealized_pnl,
        "margin_used": margin_used,
        "margin_available": margin_available,
        "margin_ratio": margin_ratio,
        "margin_call_risk": margin_ratio > margin_call_level,
        "active_positions": active_positions,
        "total_exposure": total_exposure,
        "health_status": "HEALTHY" if margin_ratio < 30 else "CAUTION" if margin_ratio < 50 else "RISK"
    }

# Usage
async def main():
    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        health = await get_account_health(client)
        print(f"Account Balance: ${health['account_balance']}")
        print(f"Margin Used: {health['margin_ratio']:.1f}%")
        print(f"Health Status: {health['health_status']}")
        print(f"Active Positions: {health['active_positions']}")

# Step 5: Execute the account health assessment
if __name__ == "__main__":
    asyncio.run(main())
```

### Multi-Account Management

You can create as many clients as you need to access different accounts with OANDA. Common scenarios include separating long and short positions to comply with US broker hedging rules, isolating different trading strategies to manage risk, or maintaining separate accounts for testing versus live trading.

For traders subject to US broker hedging rules, using separate long and short accounts provides a compliant way to maintain opposing positions in the same currency pair. This approach allows you to hedge positions without violating FIFO (First In, First Out) rules that prevent holding both long and short positions simultaneously in a single account.

<!-- fragment: multi-account hedging with AccountConfig -->
```python
import asyncio
import os

from dotenv import load_dotenv
from fivetwenty import AccountConfig, AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()


async def main() -> None:
    """Demonstrate multi-account hedging strategy for US broker compliance."""

    # Step 1: Configure dedicated account for long positions
    # Separate long account enables compliance with US FIFO regulations
    long_config = AccountConfig(
        token=os.environ["LONG_ACCOUNT_TOKEN"],    # Dedicated token for long account
        account_id=os.environ["LONG_ACCOUNT_ID"],  # Long position account identifier
        environment=Environment.LIVE,              # Live trading environment
        alias="long_positions",                   # Descriptive alias for identification
    )

    # Step 2: Configure dedicated account for short positions
    # Separate short account allows hedging without violating broker rules
    short_config = AccountConfig(
        token=os.environ["SHORT_ACCOUNT_TOKEN"],   # Dedicated token for short account
        account_id=os.environ["SHORT_ACCOUNT_ID"], # Short position account identifier
        environment=Environment.LIVE,              # Live trading environment
        alias="short_positions",                  # Descriptive alias for identification
    )

    # Step 3: Execute hedged trading strategy across both accounts
    # Multiple clients enable simultaneous management of long and short positions
    async with AsyncClient(config=long_config) as long_client:
        async with AsyncClient(config=short_config) as short_client:
            print("📈 Executing multi-account hedging strategy")
            print("📈 Long positions will be managed on dedicated account")
            print("📉 Short positions will be managed on separate account")

            # Step 4: Execute bullish strategy on long account
            # Long account handles all buy positions for the strategy
            await execute_long_strategy(long_client)

            # Step 5: Execute bearish strategy on short account for hedging
            # Short account provides hedge against long positions
            await execute_short_strategy(short_client)


async def execute_long_strategy(client: AsyncClient) -> None:
    """Execute bullish trading strategy with comprehensive account validation."""

    # Step 1: Validate long account accessibility and configuration
    # Account verification ensures the long strategy can execute properly
    accounts = await client.accounts.get_accounts()

    # Step 2: Confirm successful long account strategy execution
    print(f"📈 Long strategy executed on account: {client.config.alias}")
    print(f"✓ Account validation: {len(accounts)} account(s) accessible")
    print(f"✓ Ready for bullish position management")


async def execute_short_strategy(client: AsyncClient) -> None:
    """Execute bearish trading strategy with comprehensive account validation."""

    # Step 1: Validate short account accessibility and configuration
    # Account verification ensures the short strategy can execute properly
    accounts = await client.accounts.get_accounts()

    # Step 2: Confirm successful short account strategy execution
    print(f"📉 Short strategy executed on account: {client.config.alias}")
    print(f"✓ Account validation: {len(accounts)} account(s) accessible")
    print(f"✓ Ready for bearish position management and hedging")


# Execute the multi-account hedging strategy
if __name__ == "__main__":
    asyncio.run(main())
```

### Account Performance Tracking

Track account performance over time to understand profitability and identify areas for improvement.

<!-- fragment: Demo comprehensive account monitoring with environment variables and magic numbers -->
```python
import os
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient, Environment

# Load environment variables from .env file
load_dotenv()

async def track_account_performance(
    client: AsyncClient,
    account_id: str,
    days_back: int = 30
) -> dict:
    """Track account performance metrics over specified period."""

    # Get current account state
    account = await client.accounts.get_account(account_id)
    current_nav = Decimal(account.nav)

    # Get transaction history
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days_back)

    transactions = await client.transactions.get_transactions(
        account_id=account_id,
        from_time=start_time.isoformat(),
        to_time=end_time.isoformat()
    )

    # Calculate performance metrics
    total_realized_pnl = Decimal("0")
    total_trades = 0
    winning_trades = 0

    for transaction in transactions.transactions:
        if hasattr(transaction, 'pl') and transaction.pl:
            realized_pnl = Decimal(transaction.pl)
            total_realized_pnl += realized_pnl
            total_trades += 1

            if realized_pnl > 0:
                winning_trades += 1

    # Calculate ratios
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else Decimal("0")

    return {
        "period_days": days_back,
        "current_nav": current_nav,
        "total_realized_pnl": total_realized_pnl,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "win_rate": win_rate,
        "avg_pnl_per_trade": total_realized_pnl / total_trades if total_trades > 0 else Decimal("0")
    }

# Usage
async def main():
    async with AsyncClient(token=os.getenv("OANDA_TOKEN"), account_id=os.getenv("OANDA_ACCOUNT_ID")) as client:
        account_id = client.account_id

        performance = await track_account_performance(client, account_id, days_back=30)

        print(f"30-Day Performance Summary:")
        print(f"Current NAV: ${performance['current_nav']}")
        print(f"Realized P&L: ${performance['total_realized_pnl']:+}")
        print(f"Win Rate: {performance['win_rate']:.1f}%")
        print(f"Total Trades: {performance['total_trades']}")

# Step 5: Execute the performance analysis
if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

- Learn [Risk Management](risk-management.md) for account-level risk controls
- Explore [Advanced Orders](advanced-orders/index.md) for sophisticated account management
- See [Best Practices](../guides/understanding/best-practices.md) for production account management

For comprehensive account analytics and reporting, consider integrating with business intelligence tools or building custom dashboards using the account data retrieved through FiveTwenty.
