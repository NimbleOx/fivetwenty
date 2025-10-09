#!/usr/bin/env python3
"""
Account Management Example

Demonstrates comprehensive account operations including:
- Account discovery and details
- Account configuration
- Account changes tracking
- Instrument information
"""

import asyncio

from fivetwenty import AsyncClient


async def main() -> None:
    """Account management operations example."""

    async with AsyncClient() as client:
        # Section 1: List all accounts
        # ============================
        # OANDA users can have multiple accounts (practice, live, sub-accounts)
        # This endpoint lists all accounts associated with your API token
        # Useful for:
        # - Multi-account management tools
        # - Verifying which accounts you have access to
        # - Finding account IDs programmatically
        print("\n=== 1. List All Accounts ===")

        # Returns a list of AccountProperties objects
        # Each contains basic account info (ID, tags, MT4 account ID if applicable)
        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} account(s):")

        for acc in accounts:
            print(f"\n  ID: {acc.id}")

            # Tags: Custom labels you can assign in OANDA's web interface
            # Useful for organizing accounts (e.g., "Production", "Testing", "Strategy-A")
            print(f"  Tags: {', '.join(acc.tags) if acc.tags else 'None'}")

            # MT4 Account ID: Only present if this is a MetaTrader 4 account
            # Most modern accounts won't have this
            print(f"  MT4 Account ID: {acc.mt4_account_id if acc.mt4_account_id else 'N/A'}")

        # Section 2: Get detailed account information
        # ===========================================
        # get_account() returns COMPREHENSIVE account data
        # This is more detailed than get_account_summary() but also heavier
        # Use this when you need full account state including:
        # - Complete balance breakdown
        # - Margin details
        # - Financing charges
        # - All position/trade/order counts
        print("\n=== 2. Account Details ===")

        account_response = await client.accounts.get_account(client.account_id)
        account = account_response["account"]

        print(f"\nAccount ID: {account.id}")

        # Alias: Friendly name for your account (set in OANDA web interface)
        print(f"Alias: {account.alias if account.alias else 'N/A'}")

        # Currency: The base currency of your account (USD, EUR, GBP, etc.)
        # All P/L calculations are in this currency
        print(f"Currency: {account.currency}")

        # Created Time: When this account was opened
        print(f"Created Time: {account.created_time}")

        print("\nBalance Information:")
        # Balance: Your account's current balance
        # = Starting balance + realized P/L + financing - commission
        print(f"  Balance: {account.balance}")

        # NAV: Net Asset Value = Balance + Unrealized P/L
        # This is your "true" account value including open positions
        # Most important metric for overall account health
        print(f"  NAV: {account.nav}")

        # Unrealized P/L: Profit/loss on currently open positions
        # Changes constantly as market moves
        # Not "locked in" yet - only realized when you close positions
        print(f"  Unrealized P/L: {account.unrealized_pl if account.unrealized_pl is not None else 'N/A'}")

        # Realized P/L: Total profit/loss from all closed trades
        # This is "locked in" - part of your balance
        print(f"  Realized P/L: {account.pl}")

        # Financing: Cumulative financing/rollover charges
        # Overnight positions accrue interest (positive or negative)
        # Based on interest rate differential between currency pairs
        print(f"  Financing: {account.financing}")

        print("\nMargin Information:")
        # Margin Used: Capital currently tied up in open positions
        # You can't use this for new trades
        print(f"  Margin Used: {account.margin_used if account.margin_used is not None else 'N/A'}")

        # Margin Available: Capital available for new trades
        # = NAV - Margin Used - Margin Required for Pending Orders
        # This is what you can still trade with
        print(f"  Margin Available: {account.margin_available}")

        # Margin Closeout Percent: When margin used reaches this % of NAV,
        # OANDA will start closing your positions automatically
        # Typically 50% (means you've lost half your account to margin)
        print(f"  Margin Closeout Percent: {account.margin_closeout_percent}")

        # Margin Call Percent: Warning level before closeout
        # When margin used reaches this %, you're in danger zone
        # Typically 100% (means NAV = Margin Used, no buffer left)
        print(f"  Margin Call Percent: {account.margin_call_percent}")

        print("\nPosition Information:")
        # Open Trade Count: Number of individual trade entries
        # Note: Multiple trades on same instrument = 1 position
        print(f"  Open Trade Count: {account.open_trade_count}")

        # Open Position Count: Number of instruments with non-zero position
        # A position aggregates all trades for an instrument
        print(f"  Open Position Count: {account.open_position_count}")

        # Pending Order Count: Orders placed but not yet filled
        # Includes limit orders, stop orders, etc.
        print(f"  Pending Order Count: {account.pending_order_count}")

        # Section 3: Get account summary
        # =============================
        # get_account_summary() is LIGHTER than get_account()
        # Use this for:
        # - Quick health checks
        # - Polling account status
        # - Dashboard displays
        # - When you don't need full details
        #
        # It returns the same structure but with fewer fields populated
        # Much faster and uses less bandwidth
        print("\n=== 3. Account Summary ===")

        summary_response = await client.accounts.get_account_summary(client.account_id)
        summary = summary_response["account"]

        print(f"\nSummary for Account: {summary.id}")
        print(f"Balance: {summary.balance} {summary.currency}")
        print(f"NAV: {summary.nav}")
        print(f"Margin Available: {summary.margin_available}")
        print(f"Open Trades: {summary.open_trade_count}")
        print(f"Open Positions: {summary.open_position_count}")
        print(f"Pending Orders: {summary.pending_order_count}")

        print("\nℹ️  Summary is lighter-weight than full account details")
        print("   Use summary for frequent polling, full details when needed")
        print("   Summary: ~10 key metrics, Full: ~30+ fields")

        # Section 4: Get available instruments
        # ====================================
        # Each OANDA account has access to specific instruments
        # This varies by account type, region, and regulations
        # Instrument details include trading rules and constraints
        print("\n=== 4. Available Instruments ===")

        # Get ALL instruments for this account
        # This can be hundreds of instruments (forex, CFDs, metals, etc.)
        instruments_response = await client.accounts.get_account_instruments(account_id=client.account_id)
        instruments = instruments_response.get("instruments", [])

        print(f"\nShowing first 10 of {len(instruments)} available instruments:")
        for instrument in instruments[:10]:
            # Name: The instrument identifier (e.g., EUR_USD)
            print(f"\n  {instrument.name}")

            # Display Name: Human-readable name (e.g., "EUR/USD")
            print(f"    Display Name: {instrument.display_name}")

            # Type: CURRENCY (forex), CFD (contracts for difference), METAL (gold, silver)
            print(f"    Type: {instrument.type}")

            # Pip Location: Where the "pip" digit is (e.g., -4 for EUR/USD = 4 decimals)
            # Used for calculating pip value
            print(f"    Pip Location: {instrument.pip_location}")

            # Display Precision: How many decimals to show in UI
            # EUR/USD typically shows 5 decimals (1.12345)
            print(f"    Display Precision: {instrument.display_precision}")

            # Trade Units Precision: How many decimals for order sizes
            # 0 = whole units only, -1 = increments of 10, etc.
            print(f"    Trade Units Precision: {instrument.trade_units_precision}")

            # Minimum Trade Size: Smallest order you can place
            # Often 1 unit (micro lot) for major pairs
            print(f"    Minimum Trade Size: {instrument.minimum_trade_size}")

            # Margin Rate: Required margin as decimal (e.g., 0.0333 = 30:1 leverage)
            # Lower margin rate = higher leverage
            # 0.02 = 50:1, 0.0333 = 30:1, 0.05 = 20:1
            print(f"    Margin Rate: {instrument.margin_rate}")

        # You can also query specific instruments instead of all
        # This is more efficient if you only care about a few pairs
        print("\n  Querying specific instruments (EUR/USD, GBP/USD):")
        specific_instruments = await client.accounts.get_account_instruments(account_id=client.account_id, instruments=["EUR_USD", "GBP_USD"])

        for instrument in specific_instruments.get("instruments", []):
            print(f"\n  {instrument.name}:")
            print(f"    Display Name: {instrument.display_name}")
            print(f"    Minimum Trade Size: {instrument.minimum_trade_size}")

            # Maximum Order Units: Largest single order you can place
            # Prevents accidentally placing huge orders
            # Often in millions for forex
            print(f"    Maximum Order Units: {instrument.maximum_order_units}")

        print("\n💡 Pro Tips:")
        print("   - Check minimum_trade_size before placing orders")
        print("   - Higher margin_rate = more capital required = less leverage")
        print("   - Different instruments have different trading hours")
        print("   - Some instruments may be tradeable only during specific sessions")

        # Section 5: Configure account settings
        # =====================================
        # Account configuration controls account-level settings
        # WARNING: Be careful modifying these in production!
        print("\n=== 5. Account Configuration ===")

        print("\nCurrent Configuration:")
        print(f"  Alias: {account.alias if account.alias else 'Not set'}")

        # Margin Rate: Account-level margin override (uncommon)
        # Usually instruments have their own margin rates
        print(f"  Margin Rate: {account.margin_rate if hasattr(account, 'margin_rate') else 'Default'}")

        # Note: We're NOT actually modifying the account here
        # because this is an example and we don't want to change user settings
        print("\nℹ️  Account configuration can be updated using:")
        print("  client.accounts.patch_account_configuration()")
        print("  - Update alias (friendly name)")
        print("  - Set margin rate (advanced users only)")
        print("  (Skipping actual modification in this example)")

        print("\n⚠️  Warning:")
        print("   - Changing margin rate affects all positions")
        print("   - Only modify configuration if you know what you're doing")
        print("   - Test in practice account first")

        # Section 6: Track account changes
        # ================================
        # Account changes tracking is an EFFICIENT way to poll for updates
        # Instead of fetching full account state repeatedly, you can ask:
        # "What changed since transaction ID X?"
        #
        # This is essential for:
        # - Real-time monitoring dashboards
        # - Event-driven trading systems
        # - Efficient polling (only fetch what changed)
        # - Reducing API calls and bandwidth
        print("\n=== 6. Account Changes Tracking ===")

        # Last Transaction ID: Monotonically increasing ID
        # Every action (order, trade, modification) gets a transaction ID
        # Save this, then poll for changes since this ID
        last_transaction_id = account.last_transaction_id

        print(f"\nLast Transaction ID: {last_transaction_id}")
        print("\nAccount changes can be tracked using:")
        print("  client.accounts.get_account_changes(account_id, since_transaction_id)")

        print("\nThis returns only what changed:")
        print("  - Changed orders (new, filled, cancelled)")
        print("  - Changed trades (opened, closed, modified)")
        print("  - Changed positions (size changes, closes)")
        print("  - State updates since the specified transaction")

        print("\n💡 Efficient Polling Pattern:")
        print("  1. Get initial account state and last_transaction_id")
        print("  2. Save last_transaction_id")
        print("  3. Poll: get_account_changes(account_id, last_transaction_id)")
        print("  4. Process only the changes returned")
        print("  5. Update last_transaction_id to the new one")
        print("  6. Repeat from step 3")

        print("\nℹ️  Benefits over full account polling:")
        print("   - Reduces API calls (only fetch when there are changes)")
        print("   - Lower bandwidth usage")
        print("   - Faster processing (only handle what changed)")
        print("   - Scale to monitoring many accounts")

        # Show how to use it (without actually calling it)
        print(f"\n  Example: get_account_changes('{client.account_id}', '{last_transaction_id}')")
        print("  Returns: Dict with 'changes', 'state', 'lastTransactionID'")

        print("\n⚠️  Important:")
        print("   - Transaction IDs are per-account, not global")
        print("   - Keep track of last_transaction_id per account")
        print("   - Don't use very old transaction IDs (may be expired)")

    print("\n✅ Account management example completed!")
    print("\n📚 Summary:")
    print("   - get_accounts(): List all accounts you have access to")
    print("   - get_account(): Full detailed account state (heavy)")
    print("   - get_account_summary(): Quick account health check (light)")
    print("   - get_account_instruments(): Available instruments and rules")
    print("   - get_account_changes(): Efficient change tracking")
    print("\n   Choose the right method for your use case:")
    print("   - Frequent polling? Use summary + changes")
    print("   - Initial load? Use full account details")
    print("   - Pre-trade checks? Use instruments")


if __name__ == "__main__":
    asyncio.run(main())
