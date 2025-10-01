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
        print("\n=== 1. List All Accounts ===")

        accounts = await client.accounts.get_accounts()
        print(f"Found {len(accounts)} account(s):")

        for acc in accounts:
            print(f"\n  ID: {acc.id}")
            print(f"  Tags: {', '.join(acc.tags) if acc.tags else 'None'}")
            print(f"  MT4 Account ID: {acc.mt4_account_id if acc.mt4_account_id else 'N/A'}")

        # Section 2: Get detailed account information
        print("\n=== 2. Account Details ===")

        account_response = await client.accounts.get_account(client.account_id)
        account = account_response["account"]

        print(f"\nAccount ID: {account.id}")
        print(f"Alias: {account.alias if account.alias else 'N/A'}")
        print(f"Currency: {account.currency}")
        print(f"Created Time: {account.created_time}")
        print("\nBalance Information:")
        print(f"  Balance: {account.balance}")
        print(f"  NAV: {account.nav}")
        print(f"  Unrealized P/L: {account.unrealized_pl}")
        print(f"  Realized P/L: {account.pl}")
        print(f"  Financing: {account.financing}")
        print("\nMargin Information:")
        print(f"  Margin Used: {account.margin_used}")
        print(f"  Margin Available: {account.margin_available}")
        print(f"  Margin Closeout Percent: {account.margin_closeout_percent}")
        print(f"  Margin Call Percent: {account.margin_call_percent}")
        print("\nPosition Information:")
        print(f"  Open Trade Count: {account.open_trade_count}")
        print(f"  Open Position Count: {account.open_position_count}")
        print(f"  Pending Order Count: {account.pending_order_count}")

        # Section 3: Get account summary
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

        # Section 4: Get available instruments
        print("\n=== 4. Available Instruments ===")

        # Get first 10 instruments
        instruments_response = await client.accounts.get_account_instruments(account_id=client.account_id)
        instruments = instruments_response.get("instruments", [])

        print(f"\nShowing first 10 of {len(instruments)} available instruments:")
        for instrument in instruments[:10]:
            print(f"\n  {instrument.name}")
            print(f"    Display Name: {instrument.display_name}")
            print(f"    Type: {instrument.type}")
            print(f"    Pip Location: {instrument.pip_location}")
            print(f"    Display Precision: {instrument.display_precision}")
            print(f"    Trade Units Precision: {instrument.trade_units_precision}")
            print(f"    Minimum Trade Size: {instrument.minimum_trade_size}")
            print(f"    Margin Rate: {instrument.margin_rate}")

        # Get specific instruments
        print("\n  Querying specific instruments (EUR/USD, GBP/USD):")
        specific_instruments = await client.accounts.get_account_instruments(account_id=client.account_id, instruments=["EUR_USD", "GBP_USD"])

        for instrument in specific_instruments.get("instruments", []):
            print(f"\n  {instrument.name}:")
            print(f"    Display Name: {instrument.display_name}")
            print(f"    Minimum Trade Size: {instrument.minimum_trade_size}")
            print(f"    Maximum Order Units: {instrument.maximum_order_units}")

        # Section 5: Configure account settings
        print("\n=== 5. Account Configuration ===")

        print("\nCurrent Configuration:")
        print(f"  Alias: {account.alias if account.alias else 'Not set'}")
        print(f"  Margin Rate: {account.margin_rate if hasattr(account, 'margin_rate') else 'Default'}")

        # Note: Actually modifying account configuration in an example could be disruptive
        print("\nℹ️  Account configuration can be updated using:")
        print("  client.accounts.patch_account_configuration()")
        print("  - Update alias")
        print("  - Set margin rate")
        print("  (Skipping actual modification in this example)")

        # Section 6: Track account changes
        print("\n=== 6. Account Changes Tracking ===")

        # Get last transaction ID from account
        last_transaction_id = account.last_transaction_id

        print(f"\nLast Transaction ID: {last_transaction_id}")
        print("\nAccount changes can be tracked using:")
        print("  client.accounts.get_account_changes(account_id, since_transaction_id)")
        print("\nThis returns:")
        print("  - Changed orders")
        print("  - Changed trades")
        print("  - Changed positions")
        print("  - State updates since the specified transaction")

        # Show how to use it (without actually calling unless there are recent changes)
        print("\nℹ️  Use this for efficient polling: only fetch what changed")
        print(f"  Example: get_account_changes('{client.account_id}', '{last_transaction_id}')")

    print("\n✅ Account management example completed!")


if __name__ == "__main__":
    asyncio.run(main())
