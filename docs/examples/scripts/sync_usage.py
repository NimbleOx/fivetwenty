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
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import InstrumentName


def main() -> None:
    """Synchronous client usage example."""

    # Section 1: When to use the sync client
    # =======================================
    # The sync Client is a wrapper around AsyncClient that provides a simpler,
    # synchronous interface. Under the hood, it runs AsyncClient in a background
    # thread and uses a queue to communicate between threads.
    print("\n=== 1. When to Use Sync Client ===")

    print("\nUse Synchronous Client When:")
    print("  ✅ Writing simple scripts or automation")
    print("     - One-off tasks, cron jobs, admin scripts")
    print("  ✅ Working with legacy synchronous code")
    print("     - Integrating with existing non-async codebases")
    print("  ✅ Using interactive Python shells (REPL)")
    print("     - Jupyter notebooks, IPython, quick testing")
    print("  ✅ Prototyping or learning")
    print("     - Simpler mental model without async/await")
    print("  ✅ Simplicity > performance")
    print("     - Acceptable overhead (~1-2ms per call)")

    print("\nUse AsyncClient (Async) When:")
    print("  ⚡ Building production trading systems")
    print("     - Low latency requirements, high throughput")
    print("  ⚡ Handling multiple concurrent operations")
    print("     - Monitoring multiple instruments, parallel API calls")
    print("  ⚡ Need maximum performance")
    print("     - No thread overhead, direct async I/O")
    print("  ⚡ Working with other async libraries")
    print("     - WebSockets, async HTTP clients, async databases")

    # Section 2: Initialize sync client
    # ==================================
    # The sync Client has the same initialization as AsyncClient
    # It accepts all the same parameters (token, account_id, environment, etc.)
    print("\n=== 2. Initialize Sync Client ===")

    print("\nSync client has same configuration options as AsyncClient:")
    print("  - Reads from environment variables by default")
    print("  - Or pass token/account_id directly")
    print("  - Uses context manager for resource cleanup")

    # The 'with' statement ensures proper cleanup (closes background thread and connections)
    with Client() as client:
        print("✅ Connected (sync)")
        print(f"Account: {client.account_id}")

        # _environment shows whether you're in practice or live mode
        # This is important to verify before trading!
        print(f"Environment: {client._environment.value}")

    # When the 'with' block exits:
    # 1. The background thread is signaled to stop
    # 2. The async event loop is closed
    # 3. All HTTP connections are cleaned up
    # This happens automatically - you don't need to call client.close()

    # Section 3: Basic sync operations
    # =================================
    # The sync client mirrors all AsyncClient methods but without async/await
    # This makes code look more "traditional" and easier to understand
    print("\n=== 3. Basic Sync Operations ===")

    print("\nNo async/await needed - just call methods directly:")
    print("  - No 'async def' function")
    print("  - No 'await' keyword")
    print("  - No 'asyncio.run()'")
    print("  - Just regular Python function calls!")

    with Client() as client:
        # Get account summary - blocks until response received
        # Behind the scenes: queues request → background thread executes → waits for result
        summary = client.accounts.get_account_summary(client.account_id)
        account = summary["account"]

        print("\nAccount Balance:")
        print(f"  Balance: {account.balance} {account.currency}")
        print(f"  NAV: {account.nav}")
        print(f"  Unrealized P/L: {account.unrealized_pl if account.unrealized_pl is not None else 'N/A'}")

        # Get current pricing - another blocking call
        # Each call waits for completion before moving to next line
        pricing = client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])

        price = pricing["prices"][0]
        if price.bids and price.asks:
            print("\nEUR/USD:")
            print(f"  Bid: {price.bids[0].price}")
            print(f"  Ask: {price.asks[0].price}")

        # Place an order - this is a real trade!
        # The method blocks until order is filled or rejected
        print("\n⚠️  Placing order...")
        order = client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        # Check if order was filled
        # Market orders usually fill immediately (if market is open)
        if order.order_fill_transaction:
            print(f"✅ Order filled at {order.order_fill_transaction.price}")

        # Close position - negative units to reverse the trade
        # This demonstrates how simple position management is with sync client
        print("\n⚠️  Closing position...")
        close_order = client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=-1000)

        if close_order.order_fill_transaction:
            print("✅ Position closed")
            # Realized P/L is locked in - it's now part of your account balance
            print(f"Realized P/L: {close_order.order_fill_transaction.pl}")

    # Section 4: Sync streaming
    # =========================
    # Streaming is the most complex operation for sync client
    # It uses stream_iter() instead of async iteration
    print("\n=== 4. Synchronous Streaming ===")

    print("\nSync client provides stream_iter() for streaming:")
    print("  - Returns a regular Python iterator (not async iterator)")
    print("  - Uses regular 'for' loop (no 'async for' needed)")
    print("  - Blocks on each iteration waiting for next event")
    print("  - Uses bounded queue internally (default 100 items)")

    print("\n💡 Demo: Stream EUR/USD prices for 3 seconds...")
    import time

    start_time = time.time()
    event_count = 0

    with Client() as client:
        pricing_stream = client.pricing

        # Regular for loop (not async for)
        # Each iteration blocks waiting for next price event
        for event in pricing_stream.stream_iter(account_id=client.account_id, instruments=[InstrumentName.EUR_USD]):
            # Check event type - PRICE events contain market data
            if event.type == "PRICE" and hasattr(event, "bids") and hasattr(event, "asks"):
                event_count += 1
                if event.bids and event.asks:
                    print(f"  Price #{event_count}: {event.bids[0].price}/{event.asks[0].price}")

            # Stop after 3 seconds
            # Important: always have a way to exit the loop!
            if time.time() - start_time > 3:
                break

    print(f"✅ Received {event_count} price updates in 3 seconds")

    print("\n⚠️  Stream Iterator Notes:")
    print("  - Background thread receives events and queues them")
    print("  - Main thread blocks on queue.get() for each event")
    print("  - If queue fills up (100 items), old events are dropped")
    print("  - Always use 'break' or timeout to exit stream")

    # Section 5: Error handling in sync client
    # ========================================
    # Error handling is simpler without async - just use try/except
    print("\n=== 5. Sync Error Handling ===")

    print("\nError handling is the same, just no async:")
    print("  - Same FiveTwentyError exception")
    print("  - Same error codes and messages")
    print("  - Just use regular try/except (no 'await')")

    print("\n💡 Demo: Catch validation error...")
    # A Client only works inside its own 'with' block - the background thread that
    # runs the calls is shut down on exit, so every section opens a fresh client
    with Client() as client:
        try:
            # This will fail - units cannot be zero
            client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=0)
        except FiveTwentyError as e:
            print(f"✅ Caught error: {e.message}")
            print(f"   Status code: {e.status}")

    # Section 6: Thread safety considerations
    # ========================================
    # This is CRITICAL to understand - the sync client is NOT thread-safe!
    print("\n=== 6. Thread Safety ===")

    print("\nImportant Thread Safety Notes:")
    print("  ⚠️  Sync client uses a background thread internally")
    print("     - Runs AsyncClient in its own event loop")
    print("     - Communicates via thread-safe queue")
    print("  ⚠️  NOT thread-safe for concurrent access from multiple threads")
    print("     - Don't call client methods from different threads")
    print("     - Race conditions and corrupted state are possible")
    print("  ⚠️  Don't share Client instances between threads")
    print("     - Each thread should create its own Client")
    print("  ⚠️  Uses bounded queue for streaming")
    print("     - Queue can overflow if consumer is too slow")

    print("\n💡 If you need multi-threading:")
    print("  - Create separate Client instance per thread")
    print("  - Or better: use AsyncClient with asyncio for concurrency")
    print("     (AsyncClient + asyncio.gather() is more efficient)")

    # Section 7: Converting async code to sync
    # ========================================
    # Migration between sync and async is straightforward
    print("\n=== 7. Async to Sync Conversion ===")

    print("\nConversion is straightforward:")
    print("  1. Change AsyncClient → Client")
    print("  2. Change 'async with' → 'with'")
    print("  3. Remove all 'await' keywords")
    print("  4. Change 'async for' → 'for'")
    print("  5. Remove 'asyncio.run()' wrapper")

    # Section 8: Performance considerations
    # =====================================
    # Understanding the performance tradeoffs helps you choose wisely
    print("\n=== 8. Performance Considerations ===")

    print("\nPerformance Comparison:")
    print("  AsyncClient:")
    print("    ⚡ More efficient for concurrent operations")
    print("       - Can await multiple requests simultaneously")
    print("    ⚡ Supports concurrent reads and asynchronous processing")
    print("       - No thread/queue overhead")
    print("    ⚡ Scales well with multiple requests")
    print("       - asyncio.gather() for parallel execution")
    print("    ⚡ Direct async/await support")
    print("       - No blocking, just suspension points")

    print("\n  Client (Sync):")
    print("    🐢 Adds overhead (background thread + queue)")
    print("       - Each call: queue → thread → await → queue → return")
    print("       - Overhead ~1-2ms per call")
    print("    🐢 Sequential operations only")
    print("       - Can't easily parallelize multiple requests")
    print("    🐢 Simpler code but slower")
    print("       - Trade-off: simplicity for performance")
    print("    ✅ Easier for beginners")
    print("       - No async concepts needed")

    print("\n💡 Recommendation:")
    print("   Use AsyncClient for production trading systems")
    print("     - Latency matters in trading")
    print("     - Better resource utilization")
    print("   Use Client for simple scripts and prototyping")
    print("     - Quick admin tasks")
    print("     - Learning and experimentation")

    # Section 9: Mixing sync and async
    # =================================
    # Sometimes you need to use sync client in async code
    print("\n=== 9. Mixing Sync and Async ===")

    print("\n⚠️  Don't use Client in async code:")
    print("  - Sync client blocks the async event loop")
    print("  - Other async tasks can't run while Client is waiting")
    print("  - Always use AsyncClient in async functions instead")

    print("\n⚠️  Antipatterns to Avoid:")
    print("  ❌ Using asyncio.run() inside Client context")
    print("     - Creates nested event loops (will fail)")
    print("  ❌ Mixing Client and AsyncClient for same operations")
    print("     - Confusing and error-prone")
    print("  ❌ Sharing Client between async tasks")
    print("     - Not thread-safe, will cause issues")
    print("  ❌ Using Client when AsyncClient is more appropriate")
    print("     - Unnecessary overhead and complexity")

    # Section 10: Complete sync example
    # ==================================
    # Putting it all together in a real working example
    print("\n=== 10. Complete Sync Example ===")

    print("\nFull working example demonstrating common operations:")

    with Client() as client:
        # Step 1: Verify connection
        print(f"\n1. Connected to {client._environment.value}")

        # Step 2: Check balance before trading
        # Always verify you have sufficient funds!
        summary = client.accounts.get_account_summary(client.account_id)
        print(f"2. Balance: {summary['account'].balance}")

        # Step 3: Get current market price
        # Check market conditions before placing orders
        pricing = client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.GBP_USD])
        price = pricing["prices"][0]

        if price.bids and price.asks:
            print(f"3. GBP/USD: {price.bids[0].price}/{price.asks[0].price}")

        # Step 4: Check existing positions
        # Know what you already have open before trading
        positions = client.positions.get_open_positions(client.account_id)
        position_count = len(positions.get("positions", []))
        print(f"4. Open positions: {position_count}")

        print("\n✅ Sync example completed successfully!")

    # When context exits, everything is cleaned up automatically
    # - Background thread stops
    # - HTTP connections close
    # - Resources are freed

    print("\n💡 Key Takeaway:")
    print("   Sync Client is perfect for simple scripts")
    print("     - Easy to write and understand")
    print("     - No async complexity")
    print("     - Sufficient for most automation tasks")
    print("   Use AsyncClient for production systems")
    print("     - Better performance at scale")
    print("     - Proper async/await patterns")
    print("     - Useful for asynchronous applications")

    print("\n✅ Synchronous client usage example completed!")


if __name__ == "__main__":
    # Note: This is a regular function call, not asyncio.run()
    # The simplicity of not needing asyncio.run() is a key benefit of sync client
    main()
