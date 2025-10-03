#!/usr/bin/env python3
"""
Transaction Analysis Example

Demonstrates transaction operations including:
- Transaction history retrieval
- Transaction filtering and ranges
- Transaction streaming
- Transaction types and analysis
"""

import asyncio
from collections import Counter
from decimal import Decimal

from fivetwenty import AsyncClient


async def main() -> None:
    """Transaction analysis operations example."""

    async with AsyncClient() as client:
        # Section 1: Understanding transactions
        # ======================================
        # TRANSACTIONS are the immutable record of all account activity
        # Think of them as your trading "ledger" or "blockchain"
        #
        # Why transactions matter:
        # - Audit trail: Complete history of every account change
        # - Debugging: Understand why balance changed
        # - Analytics: Calculate performance metrics
        # - Reconciliation: Verify account state is correct
        # - Compliance: Meet regulatory requirements
        # - Tax reporting: Track all P/L for taxes
        #
        # Key properties:
        # 1. IMMUTABLE: Once created, transactions never change
        # 2. SEQUENTIAL: Transaction IDs always increase (1, 2, 3, ...)
        # 3. COMPLETE: Every balance change has a transaction
        # 4. TIMESTAMPED: Precise time of each action
        # 5. TYPED: Different transaction types for different actions
        #
        # Transaction vs Trade vs Order vs Position:
        # - TRANSACTION: Record of an action (immutable log entry)
        # - ORDER: Request to buy/sell (can be cancelled)
        # - TRADE: Open position from filled order (can be closed)
        # - POSITION: Aggregate of trades for instrument
        #
        # Example flow:
        # 1. Place order → ORDER transaction created
        # 2. Order fills → ORDER_FILL transaction created
        # 3. Trade opened → TRADE_CLIENT_EXTENSIONS transaction (if extensions used)
        # 4. Close trade → Another ORDER_FILL transaction
        print("\n=== 1. Understanding Transactions ===")

        print("\nWhat are Transactions?")
        print("  Every action on your account creates a transaction")
        print("  Transaction IDs are sequential and always increasing")
        print("  Transactions are IMMUTABLE - never change after creation")
        print("  Provide complete audit trail of all account activity")
        print("\nCommon Transaction Types:")
        # ORDER-RELATED:
        print("  - ORDER: Order creation (placed but not filled)")
        print("  - ORDER_FILL: Order execution (actually filled)")
        print("  - ORDER_CANCEL: Order cancellation")
        print("  - MARKET_ORDER_REJECT: Rejected order (insufficient margin, etc.)")
        # RISK MANAGEMENT:
        print("  - STOP_LOSS_ORDER: Stop loss creation/modification")
        print("  - TAKE_PROFIT_ORDER: Take profit creation/modification")
        print("  - TRAILING_STOP_LOSS_ORDER: Trailing stop creation/modification")
        # ACCOUNT OPERATIONS:
        print("  - DAILY_FINANCING: Rollover charges (overnight position costs)")
        print("  - TRANSFER_FUNDS: Account deposits/withdrawals")
        print("  - RESET_RESETTABLE_PL: Reset P/L counter (practice accounts)")

        # Get account to find transaction range
        # Last transaction ID tells us the most recent transaction
        account_response = await client.accounts.get_account(client.account_id)
        account = account_response["account"]

        # Last Transaction ID: Monotonically increasing identifier
        # Use this for efficient change tracking (see Section 4)
        last_transaction_id = account.last_transaction_id

        print(f"\nYour account's last transaction ID: {last_transaction_id}")
        print("  (This is the highest transaction ID currently in your account)")
        print(f"  (New transactions will have IDs: {int(last_transaction_id) + 1}, {int(last_transaction_id) + 2}, etc.)")

        # Section 2: Get transactions by time range
        print("\n=== 2. Transactions by Time Range ===")

        # Get transactions from last 7 days
        print("\nFetching recent transactions...")

        transactions_response = await client.transactions.get_recent_transactions(account_id=client.account_id, count=100)

        transactions = transactions_response["transactions"]
        print(f"\nFound {len(transactions)} transaction(s)")

        if transactions:
            print("\nFirst 5 transactions:")
            for txn in transactions[:5]:
                print(f"\n  ID {txn.id}:")
                print(f"    Type: {txn.type}")
                print(f"    Time: {txn.time}")
                if hasattr(txn, "account_balance"):
                    print(f"    Account Balance: {txn.account_balance}")

        # Section 3: Get specific transaction
        print("\n=== 3. Specific Transaction Details ===")

        if transactions:
            # Get details of the first transaction
            first_txn_id = transactions[0].id

            print(f"\nFetching details for transaction {first_txn_id}...")

            txn_details = await client.transactions.get_transaction(account_id=client.account_id, transaction_id=first_txn_id)
            txn = txn_details["transaction"]

            print(f"\nTransaction {txn.id}:")
            print(f"  Type: {txn.type}")
            print(f"  Time: {txn.time}")
            print(f"  Account Balance: {txn.account_balance if hasattr(txn, 'account_balance') else 'N/A'}")

            # Show type-specific fields
            if txn.type == "ORDER_FILL":
                print(f"  Instrument: {txn.instrument}")
                print(f"  Units: {txn.units}")
                print(f"  Price: {txn.price}")
                print(f"  P/L: {txn.pl if hasattr(txn, 'pl') else 'N/A'}")
            elif txn.type == "ORDER":
                print(f"  Instrument: {txn.instrument}")
                print(f"  Units: {txn.units}")

        # Section 4: Get transactions since ID
        print("\n=== 4. Transactions Since ID ===")

        # Calculate an ID 100 transactions back
        since_id = max(1, int(last_transaction_id) - 100)

        print(f"\nFetching transactions since ID {since_id}...")

        since_response = await client.transactions.get_transactions_since_id(account_id=client.account_id, transaction_id=str(since_id))

        since_transactions = since_response.get("transactions", [])
        print(f"Found {len(since_transactions)} transaction(s) since ID {since_id}")

        # This is useful for incremental updates
        print("\n💡 Use case: Poll for new transactions periodically")
        print("   Store last_transaction_id, then fetch only new transactions")

        # Section 5: Get transactions in ID range
        print("\n=== 5. Transactions by ID Range ===")

        # Get last 50 transactions
        from_id = max(1, int(last_transaction_id) - 50)
        to_id = last_transaction_id

        print(f"\nFetching transactions from ID {from_id} to {to_id}...")

        range_response = await client.transactions.get_transactions_range(account_id=client.account_id, from_transaction_id=str(from_id), to_transaction_id=str(to_id))

        range_transactions = range_response.get("transactions", [])
        print(f"Found {len(range_transactions)} transaction(s) in range")

        # Section 6: Get recent transactions
        print("\n=== 6. Recent Transactions ===")

        print("\nFetching most recent transactions...")

        recent_response = await client.transactions.get_recent_transactions(account_id=client.account_id)

        recent_transactions = recent_response.get("transactions", [])
        print(f"Found {len(recent_transactions)} recent transaction(s)")

        if recent_transactions:
            print("\nMost recent 5:")
            for txn in recent_transactions[:5]:
                print(f"  {txn.id}: {txn.type} at {txn.time}")

        # Section 7: Stream transactions in real-time
        print("\n=== 7. Real-Time Transaction Stream ===")

        print("\n💡 Transaction streaming allows you to monitor account activity in real-time")
        print("   Use get_transactions_stream() with async for:")
        print("   - Streams all new transactions as they occur")
        print("   - Returns HEARTBEAT events and transaction events")
        print("   - Useful for real-time monitoring and alerting")
        print("   (Not executed in this demo)")

        # Section 8: Analyze transaction types
        print("\n=== 8. Transaction Type Analysis ===")

        # Get a good sample of transactions
        analysis_response = await client.transactions.get_transactions_since_id(account_id=client.account_id, transaction_id=str(max(1, int(last_transaction_id) - 200)))

        analysis_transactions = analysis_response.get("transactions", [])

        if analysis_transactions:
            # Count transaction types
            type_counts = Counter(txn.type for txn in analysis_transactions)

            print(f"\nTransaction Type Distribution (last {len(analysis_transactions)} transactions):")
            for txn_type, count in type_counts.most_common():
                print(f"  {txn_type}: {count}")

        # Section 9: Calculate trading metrics
        print("\n=== 9. Trading Metrics from Transactions ===")

        # Analyze ORDER_FILL transactions
        fills = [txn for txn in analysis_transactions if txn.type == "ORDER_FILL"]

        if fills:
            print(f"\nAnalyzing {len(fills)} order fills...")

            # Count wins vs losses
            wins = sum(1 for txn in fills if hasattr(txn, "pl") and float(txn.pl) > 0)
            losses = sum(1 for txn in fills if hasattr(txn, "pl") and float(txn.pl) < 0)

            print(f"  Wins: {wins}")
            print(f"  Losses: {losses}")

            if wins + losses > 0:
                win_rate = (wins / (wins + losses)) * 100
                print(f"  Win Rate: {win_rate:.1f}%")

            # Calculate total P/L from fills
            total_pl = sum(Decimal(txn.pl) for txn in fills if hasattr(txn, "pl") and txn.pl)
            print(f"  Total P/L from fills: {total_pl}")

            # Calculate total financing
            financing_txns = [txn for txn in analysis_transactions if txn.type == "DAILY_FINANCING"]
            if financing_txns:
                total_financing = sum(Decimal(txn.financing) for txn in financing_txns if hasattr(txn, "financing") and txn.financing)
                print(f"  Total Financing: {total_financing}")

        # Section 10: Transaction-based reconciliation
        print("\n=== 10. Transaction Reconciliation ===")

        print("\nUsing Transactions for Account Verification:")
        print("  1. Track all ORDER_FILL transactions for realized P/L")
        print("  2. Sum DAILY_FINANCING for total financing charges")
        print("  3. Track TRANSFER_FUNDS for deposits/withdrawals")
        print("  4. Compare with account.pl (realized P/L)")

        # Get current account state
        current_account = await client.accounts.get_account_summary(client.account_id)
        account_summary = current_account["account"]

        print("\nCurrent Account State:")
        print(f"  Balance: {account_summary.balance}")
        print(f"  Realized P/L: {account_summary.pl}")
        print(f"  Unrealized P/L: {account_summary.unrealized_pl}")

        print("\n💡 Audit Trail:")
        print("   Transactions provide a complete, immutable audit trail")
        print("   Every balance change is documented with a transaction")
        print("   Transaction IDs are sequential - gaps indicate missing data")

    print("\n✅ Transaction analysis example completed!")
    print("\n📚 Summary:")
    print("   Retrieval Methods:")
    print("   - get_transactions(): By time range (from_time, to_time)")
    print("   - get_transactions_since_id(): All transactions after ID")
    print("   - get_transactions_range(): Specific ID range")
    print("   - get_recent_transactions(): Most recent transactions")
    print("   - get_transaction(): Single transaction by ID")
    print("\n   Key concepts:")
    print("   - Transactions are immutable audit trail")
    print("   - IDs are sequential (gaps indicate missing data)")
    print("   - Each transaction type has specific fields")
    print("   - Use for analytics, reconciliation, compliance")
    print("   - Streaming provides real-time monitoring")


if __name__ == "__main__":
    asyncio.run(main())
