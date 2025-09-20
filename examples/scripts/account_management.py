"""
OANDA Account Management Example

This example demonstrates account configuration and change tracking including:
- Account information retrieval and display
- Account configuration updates (alias, margin rate)
- Account change polling for state synchronization
- Best practices for account management
"""

import asyncio
import os

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID


async def main() -> None:
    """Demonstrate account management and configuration operations."""

    # Get token from environment
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("Please set FIVETWENTY_OANDA_TOKEN environment variable")
        return

    # Use practice environment for safety
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        # Get account ID (use first available account)
        accounts = await client.accounts.get_accounts()
        if not accounts:
            print("No accounts available")
            return

        account_id = AccountID(accounts[0].id)
        print(f"Using account: {account_id}")
        print("=" * 70)

        # 1. Display current account information
        print("1. Current Account Information:")
        try:
            account = await client.accounts.get_account(account_id)

            print(f"   Account ID: {account.id}")
            print(f"   Alias: {account.alias or 'Not set'}")
            print(f"   Currency: {account.currency}")
            print(f"   Balance: {account.balance}")
            print(f"   NAV: {account.nav}")
            print(f"   Margin Used: {account.margin_used}")
            print(f"   Margin Available: {account.margin_available}")
            print(f"   Margin Rate: {account.margin_rate}")
            print(f"   Open Trade Count: {account.open_trade_count}")
            print(f"   Open Position Count: {account.open_position_count}")
            print(f"   Pending Order Count: {account.pending_order_count}")
            print(f"   Created Time: {account.created_time}")

        except Exception as e:
            print(f"   Error getting account info: {e}")

        print()

        # 2. Account Configuration Management
        print("2. Account Configuration Management:")

        # Note: Configuration updates are demonstrated but not executed
        # to avoid modifying the actual account
        print("   Account configuration update patterns:")
        print()

        print("   a) Updating account alias:")
        print("      # Set a descriptive name for your account")
        print("      await client.accounts.patch_account_configuration(")
        print("          account_id,")
        print('          alias="My Primary Trading Account"')
        print("      )")
        print()

        print("   b) Updating margin rate:")
        print("      # Adjust margin requirements (if permitted)")
        print("      await client.accounts.patch_account_configuration(")
        print("          account_id,")
        print('          margin_rate="0.05"  # 5% margin rate')
        print("      )")
        print()

        print("   c) Updating both alias and margin rate:")
        print("      await client.accounts.patch_account_configuration(")
        print("          account_id,")
        print('          alias="Conservative Trading Account",')
        print('          margin_rate="0.10"  # 10% margin rate')
        print("      )")
        print()

        # 3. Account Changes Polling
        print("3. Account Changes Monitoring:")
        try:
            # Get initial account state
            print("   Getting initial account state...")
            changes = await client.accounts.get_account_changes(account_id)

            # Extract useful information from changes
            last_transaction_id = changes.get("lastTransactionID", "N/A")
            orders = changes.get("orders", [])
            trades = changes.get("trades", [])
            positions = changes.get("positions", [])

            print(f"   Last Transaction ID: {last_transaction_id}")
            print(f"   Current Orders: {len(orders)}")
            print(f"   Current Trades: {len(trades)}")
            print(f"   Current Positions: {len(positions)}")

            # Show recent orders if any
            if orders:
                print("   Recent Orders:")
                for order in orders[:3]:  # Show first 3
                    order_id = order.get("id", "N/A")
                    order_type = order.get("type", "UNKNOWN")
                    instrument = order.get("instrument", "N/A")
                    state = order.get("state", "UNKNOWN")
                    print(f"     Order {order_id}: {order_type} {instrument} ({state})")

                if len(orders) > 3:
                    print(f"     ... and {len(orders) - 3} more orders")

            # Show recent trades if any
            if trades:
                print("   Recent Trades:")
                for trade in trades[:3]:  # Show first 3
                    trade_id = trade.get("id", "N/A")
                    instrument = trade.get("instrument", "N/A")
                    units = trade.get("currentUnits", "N/A")
                    unrealized_pl = trade.get("unrealizedPL", "N/A")
                    print(f"     Trade {trade_id}: {units} {instrument} (P&L: {unrealized_pl})")

                if len(trades) > 3:
                    print(f"     ... and {len(trades) - 3} more trades")

            # Show recent positions if any
            if positions:
                print("   Current Positions:")
                for position in positions[:3]:  # Show first 3
                    instrument = position.get("instrument", "N/A")
                    long_units = position.get("long", {}).get("units", "0")
                    short_units = position.get("short", {}).get("units", "0")
                    unrealized_pl = position.get("unrealizedPL", "N/A")
                    print(f"     {instrument}: Long {long_units}, Short {short_units} (P&L: {unrealized_pl})")

                if len(positions) > 3:
                    print(f"     ... and {len(positions) - 3} more positions")

            # Demonstrate polling for changes
            if last_transaction_id != "N/A":
                print(f"\n   Polling for changes since transaction {last_transaction_id}:")
                print("   (This would be used in a real-time monitoring loop)")

                try:
                    # In practice, you would poll this periodically
                    recent_changes = await client.accounts.get_account_changes(account_id, since_transaction_id=last_transaction_id)

                    new_last_id = recent_changes.get("lastTransactionID", "N/A")
                    state_changes = recent_changes.get("changes", {})

                    if new_last_id != last_transaction_id:
                        print(f"   New changes detected! Last transaction ID: {new_last_id}")

                        # Check what changed
                        changed_orders = state_changes.get("ordersCreated", []) + state_changes.get("ordersCancelled", [])
                        changed_trades = state_changes.get("tradesOpened", []) + state_changes.get("tradesClosed", [])
                        changed_positions = state_changes.get("positions", [])

                        print(f"   Changes: {len(changed_orders)} orders, {len(changed_trades)} trades, {len(changed_positions)} positions")
                    else:
                        print("   No new changes since last check")

                except Exception as e:
                    print(f"   Error checking for changes: {e}")

        except Exception as e:
            print(f"   Error getting account changes: {e}")

        print()

        # 4. Account State Synchronization Pattern
        print("4. Account State Synchronization Pattern:")
        print("""
   Efficient account monitoring pattern:

   1. Initial State:
      changes = await client.accounts.get_account_changes(account_id)
      last_transaction_id = changes["lastTransactionID"]

   2. Periodic Polling:
      while monitoring:
          changes = await client.accounts.get_account_changes(
              account_id,
              since_transaction_id=last_transaction_id
          )

          new_last_id = changes["lastTransactionID"]
          if new_last_id != last_transaction_id:
              # Process changes
              await process_account_changes(changes["changes"])
              last_transaction_id = new_last_id

          await asyncio.sleep(poll_interval)  # e.g., 5 seconds
        """)

        # 5. Configuration Management Best Practices
        print("5. Configuration Management Best Practices:")
        print("""
   Account Alias:
   - Use descriptive names that identify account purpose
   - Consider including strategy or trader information
   - Keep names professional for shared/managed accounts
   - Examples: "EUR/USD Scalping", "Conservative Portfolio", "Test Account"

   Margin Rate:
   - Only modify if you understand margin requirements
   - Higher rates = more conservative (more margin required)
   - Lower rates = more aggressive (less margin required)
   - Changes may require account approval in some cases

   Change Monitoring:
   - Poll regularly but not excessively (5-30 second intervals)
   - Use sinceTransactionID for efficiency
   - Process changes asynchronously to avoid blocking
   - Implement error handling for network issues

   State Management:
   - Maintain local state synchronized with OANDA
   - Use change polling to detect external modifications
   - Handle race conditions in multi-threaded environments
   - Log all configuration changes for audit trails
        """)

        # 6. Error Handling and Edge Cases
        print("6. Error Handling Examples:")
        print("""
   Configuration Errors:
   try:
       await client.accounts.patch_account_configuration(
           account_id,
           alias="New Account Name"
       )
   except FiveTwentyError as e:
       if e.error_code == "ACCOUNT_CONFIGURATION_INVALID":
           print("Invalid configuration parameters")
       elif e.error_code == "ACCOUNT_NOT_FOUND":
           print("Account not found or not accessible")
       else:
           print(f"Configuration update failed: {e}")

   Change Polling Errors:
   try:
       changes = await client.accounts.get_account_changes(account_id, since_transaction_id=last_id)
   except FiveTwentyError as e:
       if e.error_code == "INVALID_TRANSACTION_ID":
           # Transaction ID too old, get fresh state
           changes = await client.accounts.get_account_changes(account_id)
       else:
           print(f"Error getting changes: {e}")
        """)

        # 7. Production Monitoring Example
        print("7. Production Account Monitoring (Demo Pattern):")
        print("   This demonstrates how you would set up continuous monitoring:")

        try:
            # Get initial state for monitoring
            initial_changes = await client.accounts.get_account_changes(account_id)
            monitoring_transaction_id = initial_changes.get("lastTransactionID", "0")

            print(f"   Starting monitoring from transaction ID: {monitoring_transaction_id}")
            print("   Monitoring for 10 seconds (demo)...")

            # Simulate monitoring for a short period
            start_time = asyncio.get_event_loop().time()
            poll_count = 0

            while asyncio.get_event_loop().time() - start_time < 10:  # 10 seconds
                try:
                    changes = await client.accounts.get_account_changes(account_id, since_transaction_id=monitoring_transaction_id)

                    new_transaction_id = changes.get("lastTransactionID", monitoring_transaction_id)

                    if new_transaction_id != monitoring_transaction_id:
                        print(f"   Change detected at poll #{poll_count}: Transaction ID {new_transaction_id}")

                        # In production, process the changes here
                        state_changes = changes.get("changes", {})
                        if state_changes:
                            print("   Processing account state changes...")

                        monitoring_transaction_id = new_transaction_id

                    poll_count += 1
                    await asyncio.sleep(2)  # Poll every 2 seconds

                except Exception as e:
                    print(f"   Monitoring error: {e}")
                    await asyncio.sleep(5)  # Back off on errors

            print(f"   Monitoring completed. Performed {poll_count} polls.")

        except Exception as e:
            print(f"   Error setting up monitoring: {e}")

        print("\nAccount management demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
