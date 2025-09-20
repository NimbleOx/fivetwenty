"""
OANDA Transaction Analysis Example

This example demonstrates transaction history and audit capabilities including:
- Transaction querying with time ranges and filtering
- Incremental transaction updates
- Transaction analysis and reporting
- Real-time transaction streaming
"""

import asyncio
import contextlib
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import AccountID


async def main() -> None:
    """Demonstrate transaction analysis and audit operations."""

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
        print("=" * 80)

        # 1. Get transaction ID range to understand available data
        print("1. Transaction Data Availability:")
        try:
            id_range = await client.transactions.get_transactions_by_id_range(account_id)
            first_id = id_range.get("firstTransactionID", "N/A")
            last_id = id_range.get("lastTransactionID", "N/A")

            print(f"   Available transaction ID range: {first_id} to {last_id}")

            if first_id != "N/A" and last_id != "N/A":
                total_transactions = int(last_id) - int(first_id) + 1
                print(f"   Total transactions available: {total_transactions}")
        except Exception as e:
            print(f"   Error getting ID range: {e}")

        print()

        # 2. Get recent transaction history
        print("2. Recent Transaction History:")
        try:
            recent_transactions = await client.transactions.get_recent_transactions(account_id, count=20)

            transactions_list = recent_transactions.get("transactions", [])
            if transactions_list:
                print(f"   Retrieved {len(transactions_list)} recent transactions:")

                for transaction in transactions_list[-5:]:  # Show last 5
                    tx_id = transaction.get("id", "N/A")
                    tx_type = transaction.get("type", "UNKNOWN")
                    tx_time = transaction.get("time", "N/A")

                    # Format time for display
                    if tx_time != "N/A":
                        try:
                            dt = datetime.fromisoformat(tx_time.replace("Z", "+00:00"))
                            tx_time = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                        except ValueError:
                            pass  # Keep original format if parsing fails

                    print(f"     TX {tx_id}: {tx_type} at {tx_time}")

                    # Show additional details based on transaction type
                    if tx_type == "ORDER_FILL":
                        instrument = transaction.get("instrument", "N/A")
                        units = transaction.get("units", "N/A")
                        price = transaction.get("price", "N/A")
                        pl = transaction.get("pl", "N/A")
                        print(f"       Fill: {units} {instrument} @ {price}, P&L: {pl}")
                    elif tx_type in ["MARKET_ORDER", "LIMIT_ORDER", "STOP_ORDER"]:
                        instrument = transaction.get("instrument", "N/A")
                        units = transaction.get("units", "N/A")
                        print(f"       Order: {units} {instrument}")
                    elif tx_type == "DAILY_FINANCING":
                        financing = transaction.get("financing", "N/A")
                        print(f"       Financing: {financing}")
            else:
                print("   No recent transactions found")
        except Exception as e:
            print(f"   Error getting recent transactions: {e}")

        print()

        # 3. Time-based transaction analysis
        print("3. Transaction Analysis (Last 7 Days):")

        # Get transactions from last week
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)

        try:
            weekly_transactions = await client.transactions.get_transactions(account_id, from_time=start_time, to_time=end_time, page_size=500)

            transactions_list = weekly_transactions.get("transactions", [])
            if transactions_list:
                print(f"   Analyzed {len(transactions_list)} transactions from the last 7 days:")

                # Analyze transaction types
                type_counts: dict[str, int] = defaultdict(int)
                fills_by_instrument: dict[str, list[dict[str, Any]]] = defaultdict(list)
                total_pl = 0.0
                total_financing = 0.0

                for transaction in transactions_list:
                    tx_type = transaction.get("type", "UNKNOWN")
                    type_counts[tx_type] += 1

                    # Collect order fills for instrument analysis
                    if tx_type == "ORDER_FILL":
                        instrument = transaction.get("instrument", "UNKNOWN")
                        fills_by_instrument[instrument].append(transaction)

                        # Sum up P&L
                        pl = transaction.get("pl", "0")
                        if pl != "0":
                            with contextlib.suppress(ValueError, TypeError):
                                total_pl += float(pl)

                    # Sum up financing
                    elif tx_type == "DAILY_FINANCING":
                        financing = transaction.get("financing", "0")
                        if financing != "0":
                            with contextlib.suppress(ValueError, TypeError):
                                total_financing += float(financing)

                # Display transaction type breakdown
                print("\n     Transaction Type Breakdown:")
                for tx_type, count in sorted(type_counts.items()):
                    print(f"       {tx_type}: {count}")

                # Display trading activity by instrument
                if fills_by_instrument:
                    print("\n     Trading Activity by Instrument:")
                    for instrument, fills in fills_by_instrument.items():
                        fill_count = len(fills)
                        total_units = sum(float(fill.get("units", "0")) for fill in fills if fill.get("units", "0") != "0")
                        print(f"       {instrument}: {fill_count} fills, {total_units:,.0f} units")

                # Display financial summary
                print("\n     Financial Summary:")
                print(f"       Total P&L: {total_pl:,.2f}")
                print(f"       Total Financing: {total_financing:,.2f}")
                print(f"       Net Result: {total_pl + total_financing:,.2f}")

            else:
                print("   No transactions found in the last 7 days")
        except Exception as e:
            print(f"   Error analyzing weekly transactions: {e}")

        print()

        # 4. Incremental transaction updates
        print("4. Incremental Transaction Updates:")
        try:
            # Get the latest transaction ID
            recent = await client.transactions.get_recent_transactions(account_id, count=1)
            recent_list = recent.get("transactions", [])

            if recent_list:
                latest_id = recent_list[0].get("id", "0")
                print(f"   Latest transaction ID: {latest_id}")

                # Demonstrate how to get transactions since a specific ID
                # (Using a slightly older ID for demonstration)
                try:
                    since_id = str(max(1, int(latest_id) - 10))

                    updates = await client.transactions.get_transactions_since_id(account_id, since_id, transaction_type=["ORDER_FILL", "MARKET_ORDER"])

                    updates_list = updates.get("transactions", [])
                    print(f"   Found {len(updates_list)} transactions since ID {since_id}")
                    print("   (Filtered for ORDER_FILL and MARKET_ORDER types)")

                    if updates_list:
                        print("   Recent updates:")
                        for update in updates_list[-3:]:  # Show last 3
                            update_id = update.get("id", "N/A")
                            update_type = update.get("type", "UNKNOWN")
                            update_time = update.get("time", "N/A")[:19] + "Z" if update.get("time") else "N/A"
                            print(f"     ID {update_id}: {update_type} at {update_time}")

                except (ValueError, TypeError):
                    print("   Cannot demonstrate incremental updates with non-numeric transaction ID")
            else:
                print("   No transactions available for incremental update demonstration")
        except Exception as e:
            print(f"   Error with incremental updates: {e}")

        print()

        # 5. Transaction filtering by type
        print("5. Transaction Type Filtering:")
        try:
            # Get only order-related transactions
            order_types = ["MARKET_ORDER", "LIMIT_ORDER", "STOP_ORDER", "ORDER_FILL", "ORDER_CANCEL"]

            order_transactions = await client.transactions.get_recent_transactions(account_id, count=50, transaction_type=order_types)

            order_list = order_transactions.get("transactions", [])
            print(f"   Found {len(order_list)} order-related transactions:")

            # Group by type
            type_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for tx in order_list:
                tx_type = tx.get("type", "UNKNOWN")
                type_groups[tx_type].append(tx)

            for tx_type, transactions in type_groups.items():
                print(f"     {tx_type}: {len(transactions)} transactions")

                # Show details for order fills
                if tx_type == "ORDER_FILL" and transactions:
                    fills_sample = transactions[:3]  # Show first 3
                    for fill in fills_sample:
                        instrument = fill.get("instrument", "N/A")
                        units = fill.get("units", "N/A")
                        price = fill.get("price", "N/A")
                        print(f"       • {units} {instrument} @ {price}")

                    if len(transactions) > 3:
                        print(f"       • ... and {len(transactions) - 3} more")

        except Exception as e:
            print(f"   Error filtering by transaction type: {e}")

        print()

        # 6. Real-time transaction streaming
        print("6. Real-time Transaction Streaming:")
        print("   NOTE: This demonstrates the streaming pattern for live monitoring")

        try:
            print("   Starting transaction stream monitor (demo - will timeout quickly)...")
            transaction_count = 0

            async for transaction in client.transactions.get_transactions_stream(account_id, stall_timeout=5.0):
                transaction_count += 1
                tx_type = transaction.get("type", "UNKNOWN")
                tx_id = transaction.get("id", "N/A")

                print(f"   Live: Transaction {tx_id} ({tx_type})")

                # Show relevant details
                if tx_type == "ORDER_FILL":
                    instrument = transaction.get("instrument", "N/A")
                    units = transaction.get("units", "N/A")
                    price = transaction.get("price", "N/A")
                    print(f"     Fill: {units} {instrument} @ {price}")

                # Limit demo to first few transactions
                if transaction_count >= 3:
                    print("   (Demo limit reached - stopping stream)")
                    break

        except Exception as e:
            print(f"   Stream demo: {e}")

        print("\n   Example production streaming pattern:")
        print("""
   # Production transaction monitoring
   async for transaction in client.transactions.stream(account_id):
       await process_transaction(transaction)
       await update_portfolio_state(transaction)
       await log_for_compliance(transaction)
        """)

        print()

        # 7. Transaction ID range queries
        print("7. Transaction ID Range Queries:")
        try:
            # Get a specific range of transactions (if we have enough history)
            recent = await client.transactions.get_recent_transactions(account_id, count=1)
            recent_list = recent.get("transactions", [])

            if recent_list:
                latest_id = recent_list[0].get("id", "0")
                try:
                    end_id = int(latest_id)
                    start_id = max(1, end_id - 20)  # Get 20 transactions

                    range_transactions = await client.transactions.get_transactions_range(account_id, str(start_id), str(end_id))

                    range_list = range_transactions.get("transactions", [])
                    print(f"   Retrieved {len(range_list)} transactions in ID range {start_id}-{end_id}")

                    if range_list:
                        # Show first and last transaction in range
                        first_tx = range_list[0]
                        last_tx = range_list[-1]

                        print(f"   First: TX {first_tx.get('id')} ({first_tx.get('type')})")
                        print(f"   Last:  TX {last_tx.get('id')} ({last_tx.get('type')})")

                except (ValueError, TypeError):
                    print("   Cannot demonstrate ID range queries with non-numeric transaction IDs")
            else:
                print("   No transactions available for range query demonstration")

        except Exception as e:
            print(f"   Error with ID range queries: {e}")

        print()

        # 8. Best practices and compliance
        print("8. Best Practices for Transaction Management:")
        print("""
   Audit & Compliance:
   - Store transaction logs for regulatory compliance
   - Implement daily transaction reconciliation
   - Monitor for unusual trading patterns
   - Archive historical transaction data

   Performance:
   - Use incremental updates (sinceID) for efficiency
   - Cache recent transactions for quick access
   - Implement proper pagination for large datasets
   - Use appropriate transaction type filtering

   Real-time Monitoring:
   - Stream live transactions for immediate processing
   - Implement heartbeat monitoring for stream health
   - Handle reconnection logic for production systems
   - Process transactions asynchronously to avoid blocking

   Analysis:
   - Aggregate transactions by time periods
   - Track P&L attribution by instrument/strategy
   - Monitor financing costs and funding
   - Calculate transaction costs and slippage
        """)

        print("Transaction analysis demonstration complete!")


if __name__ == "__main__":
    asyncio.run(main())
