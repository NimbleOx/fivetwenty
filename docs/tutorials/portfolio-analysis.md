# Account Management with FiveTwenty

Learn how to monitor account health, manage multiple accounts, and track account-level metrics using FiveTwenty's account and position APIs.

!!! success "🎯 Practical Guide - Problem-oriented solutions"
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

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient

async def get_account_health(client: AsyncClient, account_id: str) -> dict:
    """Get comprehensive account health status."""
    # Get account details
    account = await client.accounts.get_account(account_id)

    # Get all positions for risk assessment
    positions = await client.positions.get_positions(account_id)

    # Calculate account metrics
    total_exposure = Decimal("0")
    unrealized_pnl = Decimal("0")
    active_positions = 0

    for position in positions.positions:
        if position.long.units != "0" or position.short.units != "0":
            long_units = Decimal(position.long.units) if position.long.units != "0" else Decimal("0")
            short_units = Decimal(position.short.units) if position.short.units != "0" else Decimal("0")
            net_units = long_units + short_units

            if net_units != 0:
                active_positions += 1
                total_exposure += abs(net_units)
                unrealized_pnl += Decimal(position.unrealized_pl)

    # Calculate health ratios
    balance = Decimal(account.balance)
    margin_used = Decimal(account.margin_used)
    margin_available = Decimal(account.margin_available)

    margin_ratio = (margin_used / balance) * 100 if balance > 0 else Decimal("0")
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
    async with AsyncClient(token="your-token", account_id="your-account") as client:
        account_id = "your-account-id"

        health = await get_account_health(client, account_id)
        print(f"Account Balance: ${health['account_balance']}")
        print(f"Margin Used: {health['margin_ratio']:.1f}%")
        print(f"Health Status: {health['health_status']}")
        print(f"Active Positions: {health['active_positions']}")

asyncio.run(main())
```

### Multi-Account Management

When trading with multiple OANDA accounts (such as separate accounts for different strategies or compliance with hedging rules), you need centralized account monitoring across all your accounts.

```python
async def monitor_multiple_accounts(account_configs: list[dict]) -> dict:
    """Monitor health across multiple trading accounts."""

    account_summaries = {}
    total_nav = Decimal("0")
    total_margin_used = Decimal("0")

    for config in account_configs:
        async with AsyncClient(
            token=config["token"],
            account_id=config["account_id"]
        ) as client:

            # Get account health for each account
            health = await get_account_health(client, config["account_id"])

            account_summaries[config["name"]] = {
                "account_id": config["account_id"],
                "balance": health["account_balance"],
                "nav": health["nav"],
                "margin_used": health["margin_used"],
                "margin_ratio": health["margin_ratio"],
                "health_status": health["health_status"],
                "active_positions": health["active_positions"]
            }

            total_nav += health["nav"]
            total_margin_used += health["margin_used"]

    # Calculate aggregate metrics
    aggregate_margin_ratio = (total_margin_used / total_nav * 100) if total_nav > 0 else Decimal("0")

    return {
        "accounts": account_summaries,
        "aggregate": {
            "total_nav": total_nav,
            "total_margin_used": total_margin_used,
            "aggregate_margin_ratio": aggregate_margin_ratio,
            "account_count": len(account_configs)
        }
    }

# Example usage for multiple accounts
async def main():
    # Configure your accounts
    accounts = [
        {
            "name": "Long Strategy Account",
            "token": "your-long-token",
            "account_id": "long-account-id"
        },
        {
            "name": "Short Strategy Account",
            "token": "your-short-token",
            "account_id": "short-account-id"
        }
    ]

    multi_account_summary = await monitor_multiple_accounts(accounts)

    print(f"Total NAV across accounts: ${multi_account_summary['aggregate']['total_nav']}")
    print(f"Aggregate margin usage: {multi_account_summary['aggregate']['aggregate_margin_ratio']:.1f}%")

    for name, account in multi_account_summary['accounts'].items():
        print(f"{name}: {account['health_status']} - {account['active_positions']} positions")

asyncio.run(main())
```

### Account Performance Tracking

Track account performance over time to understand profitability and identify areas for improvement.

```python
from datetime import datetime, timedelta

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
    async with AsyncClient(token="your-token", account_id="your-account") as client:
        account_id = "your-account-id"

        performance = await track_account_performance(client, account_id, days_back=30)

        print(f"30-Day Performance Summary:")
        print(f"Current NAV: ${performance['current_nav']}")
        print(f"Realized P&L: ${performance['total_realized_pnl']:+}")
        print(f"Win Rate: {performance['win_rate']:.1f}%")
        print(f"Total Trades: {performance['total_trades']}")

asyncio.run(main())
```

## Next Steps

- Learn [Risk Management](risk-management.md) for account-level risk controls
- Explore [Advanced Orders](advanced-orders/index.md) for sophisticated account management
- See [Best Practices](../guides/understanding/best-practices.md) for production account management

For comprehensive account analytics and reporting, consider integrating with business intelligence tools or building custom dashboards using the account data retrieved through FiveTwenty.
