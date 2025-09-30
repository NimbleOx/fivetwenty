#!/usr/bin/env python3
"""
Synchronous Client Usage Example

Demonstrates the synchronous Client wrapper:
- When to use sync vs async
- Client initialization
- Basic operations
- Streaming with sync client
- Thread-safety considerations
"""

from fivetwenty import Client
from fivetwenty.models import InstrumentName


def main() -> None:
    """Synchronous client usage example."""

    # Section 1: When to use the sync client
    print("\n=== 1. When to Use Sync Client ===")

    print("\nUse Synchronous Client When:")
    print("  ✅ Writing simple scripts or automation")
    print("  ✅ Working with legacy synchronous code")
    print("  ✅ Using interactive Python shells (REPL)")
    print("  ✅ Prototyping or learning")
    print("  ✅ Simplicity > performance")

    print("\nUse AsyncClient (Async) When:")
    print("  ⚡ Building production trading systems")
    print("  ⚡ Handling multiple concurrent operations")
    print("  ⚡ Need maximum performance")
    print("  ⚡ Working with other async libraries")

    # Section 2: Initialize sync client
    print("\n=== 2. Initialize Sync Client ===")

    print("\nSync client has same configuration options as AsyncClient:")

    with Client() as client:
        print(f"✅ Connected (sync)")
        print(f"Account: {client.account_id}")
        print(f"Environment: {client.environment.value}")

    # Section 3: Basic sync operations
    print("\n=== 3. Basic Sync Operations ===")

    print("\nNo async/await needed - just call methods directly:")

    with Client() as client:
        # Get account summary
        summary = client.accounts.get_account_summary(client.account_id)
        account = summary["account"]

        print(f"\nAccount Balance:")
        print(f"  Balance: {account.balance} {account.currency}")
        print(f"  NAV: {account.nav}")
        print(f"  Unrealized P/L: {account.unrealized_pl}")

        # Get current pricing
        pricing = client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.EUR_USD]
        )

        price = pricing["prices"][0]
        if price.bids and price.asks:
            print(f"\nEUR/USD:")
            print(f"  Bid: {price.bids[0].price}")
            print(f"  Ask: {price.asks[0].price}")

        # Place an order
        print("\n⚠️  Placing order...")
        order = client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000
        )

        if order.order_fill_transaction:
            print(f"✅ Order filled at {order.order_fill_transaction.price}")

        # Close position
        print("\n⚠️  Closing position...")
        close_order = client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=-1000
        )

        if close_order.order_fill_transaction:
            print(f"✅ Position closed")
            print(f"Realized P/L: {close_order.order_fill_transaction.pl}")

    # Section 4: Sync streaming
    print("\n=== 4. Synchronous Streaming ===")

    print("\nSync client provides stream_iter() for streaming:")
    print("Uses regular for loop (no async for needed)\n")

    print("💡 Example code (not running live):\n")
    print("""
with Client() as client:
    # Stream prices for 10 seconds
    import time
    start_time = time.time()
    count = 0

    for event in client.pricing.stream_iter(
        account_id=client.account_id,
        instruments=[InstrumentName.EUR_USD]
    ):
        if event.type == "PRICE":
            count += 1
            print(f"Price #{count}: {event.bids[0].price}/{event.asks[0].price}")

        # Stop after 10 seconds
        if time.time() - start_time > 10:
            break

    print(f"Received {count} price updates")
    """)

    # Section 5: Error handling in sync client
    print("\n=== 5. Sync Error Handling ===")

    print("\nError handling is the same, just no async:")

    print("""
from fivetwenty.exceptions import VeeTwentyError

with Client() as client:
    try:
        order = client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName.EUR_USD,
            units=1000000000  # Will fail - insufficient margin
        )
    except VeeTwentyError as e:
        print(f"Order rejected: {e.message}")
        print(f"Error code: {e.code}")
    """)

    # Section 6: Thread safety considerations
    print("\n=== 6. Thread Safety ===")

    print("\nImportant Thread Safety Notes:")
    print("  ⚠️  Sync client uses a background thread internally")
    print("  ⚠️  NOT thread-safe for concurrent access")
    print("  ⚠️  Don't share Client instances between threads")
    print("  ⚠️  Uses bounded queue for streaming")

    print("\n💡 If you need multi-threading:")
    print("  - Create separate Client instance per thread")
    print("  - Or use AsyncClient with asyncio for concurrency")

    print("\nExample - One Client Per Thread:")
    print("""
import threading

def trading_thread(account_id):
    # Each thread gets its own client
    with Client(account_id=account_id) as client:
        summary = client.accounts.get_account_summary(client.account_id)
        print(f"Thread {threading.current_thread().name}: {summary['account'].balance}")

thread1 = threading.Thread(target=trading_thread, args=("account-1",))
thread2 = threading.Thread(target=trading_thread, args=("account-2",))

thread1.start()
thread2.start()
    """)

    # Section 7: Converting async code to sync
    print("\n=== 7. Async to Sync Conversion ===")

    print("\nConversion is straightforward:\n")

    print("Async Code:")
    print("""
async with AsyncClient() as client:
    result = await client.accounts.get_account_summary(client.account_id)
    price = await client.pricing.get_pricing(...)
    """)

    print("\nSync Code:")
    print("""
with Client() as client:
    result = client.accounts.get_account_summary(client.account_id)
    price = client.pricing.get_pricing(...)
    """)

    print("\nKey Differences:")
    print("  async with → with")
    print("  await → (remove it)")
    print("  async for → for")
    print("  asyncio.run() → regular function call")

    # Section 8: Performance considerations
    print("\n=== 8. Performance Considerations ===")

    print("\nPerformance Comparison:")
    print("  AsyncClient:")
    print("    ⚡ More efficient for concurrent operations")
    print("    ⚡ Better for high-frequency trading")
    print("    ⚡ Scales well with multiple requests")
    print("    ⚡ Direct async/await support")

    print("\n  Client (Sync):")
    print("    🐢 Adds overhead (background thread + queue)")
    print("    🐢 Sequential operations only")
    print("    🐢 Simpler code but slower")
    print("    ✅ Easier for beginners")

    print("\n💡 Recommendation:")
    print("   Use AsyncClient for production trading systems")
    print("   Use Client for simple scripts and prototyping")

    # Section 9: Mixing sync and async
    print("\n=== 9. Mixing Sync and Async ===")

    print("\nYou CAN use Client in async code:")
    print("""
async def my_async_function():
    # Sync client works in async context
    with Client() as client:
        result = client.accounts.get_account_summary(client.account_id)
        return result
    """)

    print("\nBut you SHOULD use AsyncClient instead:")
    print("""
async def my_async_function():
    # Better - use AsyncClient in async code
    async with AsyncClient() as client:
        result = await client.accounts.get_account_summary(client.account_id)
        return result
    """)

    print("\n⚠️  Antipatterns to Avoid:")
    print("  ❌ Using asyncio.run() inside Client context")
    print("  ❌ Mixing Client and AsyncClient for same operations")
    print("  ❌ Sharing Client between async tasks")

    # Section 10: Complete sync example
    print("\n=== 10. Complete Sync Example ===")

    print("\nFull working example:")

    with Client() as client:
        print(f"\n1. Connected to {client.environment.value}")

        # Check balance
        summary = client.accounts.get_account_summary(client.account_id)
        print(f"2. Balance: {summary['account'].balance}")

        # Get price
        pricing = client.pricing.get_pricing(
            account_id=client.account_id,
            instruments=[InstrumentName.GBP_USD]
        )
        price = pricing["prices"][0]

        if price.bids and price.asks:
            print(f"3. GBP/USD: {price.bids[0].price}/{price.asks[0].price}")

        # Check positions
        positions = client.positions.get_open_positions(client.account_id)
        position_count = len(positions.get("positions", []))
        print(f"4. Open positions: {position_count}")

        print("\n✅ Sync example completed successfully!")

    print("\n💡 Key Takeaway:")
    print("   Sync Client is perfect for simple scripts")
    print("   Use AsyncClient for production systems")

    print("\n✅ Synchronous client usage example completed!")


if __name__ == "__main__":
    main()  # Note: regular function call, not asyncio.run()
