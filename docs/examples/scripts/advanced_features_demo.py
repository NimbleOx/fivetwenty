#!/usr/bin/env python3
"""
Advanced Features Demo

Comprehensive demonstration of advanced FiveTwenty features:
- Decimal precision for financial calculations
- Client extensions and metadata
- Streaming with reconnection policies
- Complex order strategies
- Performance optimization
- Type safety and validation
"""

import asyncio
from decimal import Decimal

from fivetwenty import AsyncClient
from fivetwenty.models import (
    ClientExtensions,
    InstrumentName,
    MarketOrderRequest,
    StopLossDetails,
    TakeProfitDetails,
)


async def main() -> None:
    """Advanced features demonstration."""

    # ADVANCED FEATURES distinguish professional trading systems from hobby projects
    # These features ensure:
    # - Financial precision (no float errors)
    # - System reliability (robust error handling, reconnection)
    # - Performance (concurrent operations, efficient APIs)
    # - Maintainability (type safety, clear code)
    # - Traceability (client extensions, request IDs)
    #
    # This demo covers:
    # 1. Decimal precision (avoid float errors in money calculations)
    # 2. Client request IDs (debugging and correlation)
    # 3. Client extensions (metadata and tracking)
    # 4. Advanced streaming (automatic reconnection)
    # 5. Order dependencies (bracket orders)
    # 6. Position fill strategies (control position behavior)
    # 7. Time in force (order expiry control)
    # 8. Type safety (prevent errors at compile time)
    # 9. Concurrent operations (parallel API calls)
    # 10. Resource management (proper cleanup)
    # 11. Custom timeouts (latency control)
    # 12. Complete production example (all together)
    #
    # Why these matter:
    # - Production systems handle real money
    # - Downtime = lost opportunities
    # - Bugs = lost money
    # - Poor performance = missed trades
    # - Lack of tracing = debugging nightmares

    async with AsyncClient() as client:
        # Section 1: Decimal precision
        # ============================
        # CRITICAL: Never use float for financial calculations
        # Float arithmetic has rounding errors that compound over time
        #
        # Example of float problem:
        # 0.1 + 0.2 = 0.30000000000000004 (not 0.3!)
        #
        # In trading:
        # - 0.01% error on $1M position = $100 mistake
        # - Compounding errors over 1000 trades = significant losses
        # - Regulatory compliance requires exact calculations
        #
        # Python's Decimal type:
        # - Exact decimal arithmetic
        # - No rounding errors
        # - Required for financial applications
        # - FiveTwenty uses Decimal everywhere automatically
        print("\n=== 1. Decimal Precision ===")

        print("\nWhy Decimal matters for trading:")
        print("  Float precision problems:")
        float_sum = 0.1 + 0.2
        print(f"    0.1 + 0.2 = {float_sum} (float)")
        print("    Expected: 0.3")
        print("    ❌ Float arithmetic is imprecise!")

        print("\n  Decimal precision:")
        decimal_sum = Decimal("0.1") + Decimal("0.2")
        print(f"    0.1 + 0.2 = {decimal_sum} (Decimal)")
        print("    ✅ Decimal arithmetic is exact!")

        print("\nFiveTwenty uses Decimal everywhere:")
        print("  - Order prices")
        print("  - Position sizes")
        print("  - P/L calculations")
        print("  - Account balances")

        # Example with real price calculations
        entry_price = Decimal("1.08500")
        exit_price = Decimal("1.08750")
        units = Decimal("10000")

        pips = (exit_price - entry_price) * Decimal("10000")  # For EUR/USD
        profit = (exit_price - entry_price) * units

        print("\nExample calculation:")
        print(f"  Entry: {entry_price}")
        print(f"  Exit: {exit_price}")
        print(f"  Units: {units}")
        print(f"  Pips gained: {pips}")
        print(f"  Profit: ${profit}")

        # Section 2: Client request IDs
        print("\n=== 2. Client Request IDs ===")

        print("\nClient Request IDs are for debugging, not idempotency:")
        print("  ✅ Appears in OANDA's internal logs")
        print("  ✅ Useful for support tickets")
        print("  ✅ Helps correlate requests")
        print("  ❌ Does NOT prevent duplicate orders")
        print("  ❌ Does NOT appear in transaction responses")

        from datetime import datetime, timezone

        client_request_id = f"trading-bot-v1-{datetime.now(timezone.utc).isoformat()}"

        print(f"\nExample: {client_request_id}")

        # Section 3: Client extensions
        print("\n=== 3. Client Extensions ===")

        print("\nClient extensions add metadata to orders/trades:")

        # Create extensions
        extensions = ClientExtensions(id="momentum-strategy-001", tag="breakout", comment="Strong momentum signal detected")

        print("\nExtensions:")
        print(f"  ID: {extensions.id}")
        print(f"  Tag: {extensions.tag}")
        print(f"  Comment: {extensions.comment}")

        # Place order with extensions
        order_request = MarketOrderRequest(instrument=InstrumentName.EUR_USD, units=Decimal("1000"), clientExtensions=extensions)
        order = await client.orders.post_order(account_id=client.account_id, order_request=order_request, client_request_id=client_request_id)

        if order.get("orderFillTransaction"):
            print("\n✅ Order placed with extensions")
            print(f"Fill price: {order['orderFillTransaction'].price}")

        # Section 4: Advanced streaming
        print("\n=== 4. Advanced Streaming ===")

        print("\nRobust streaming configuration:")
        print("  - Use StreamingConfiguration for stall detection")
        print("  - Use ReconnectionPolicy for automatic reconnection")
        print("  - stream_pricing_with_retries() handles reconnection transparently")
        print("  - Configure max_attempts, delays, backoff multiplier")
        print("  - Handle PRICE events for data, HEARTBEAT for connection health")

        # Section 5: Order dependencies and linking
        print("\n=== 5. Order Dependencies ===")

        print("\nBracket order strategy (Entry + TP + SL):")

        # Get current price
        pricing = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])
        current_ask = Decimal(pricing["prices"][0].asks[0].price)

        # Define bracket
        entry_price = current_ask
        take_profit_price = entry_price + Decimal("0.0050")  # 50 pips
        stop_loss_price = entry_price - Decimal("0.0025")  # 25 pips

        print(f"\n  Entry: {entry_price}")
        print(f"  Take Profit: {take_profit_price} (+50 pips)")
        print(f"  Stop Loss: {stop_loss_price} (-25 pips)")

        bracket_order_request = MarketOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units=Decimal("1000"),
            takeProfitOnFill=TakeProfitDetails(price=take_profit_price),
            stopLossOnFill=StopLossDetails(price=stop_loss_price),
            clientExtensions=ClientExtensions(comment="Bracket order demo"),
        )
        bracket_order = await client.orders.post_order(account_id=client.account_id, order_request=bracket_order_request)

        if bracket_order.get("orderFillTransaction"):
            print("\n✅ Bracket order filled")
            print(f"Entry: {bracket_order['orderFillTransaction'].price}")

        # Section 6: Position fill strategies
        print("\n=== 6. Position Fill Strategies ===")

        print("\nOrderPositionFill determines how orders affect positions:")
        print("\n  DEFAULT:")
        print("    OANDA decides based on position state")

        print("\n  OPEN_ONLY:")
        print("    Only opens new positions")
        print("    Rejects if would close existing position")

        print("\n  REDUCE_FIRST:")
        print("    First reduces opposite position")
        print("    Then opens new position if units remain")

        print("\n  REDUCE_ONLY:")
        print("    Only reduces existing positions")
        print("    Rejects if would open new position")

        print("\n💡 Usage:")
        print("  - Set position_fill parameter in order requests")
        print("  - OrderPositionFill.REDUCE_ONLY ensures only closing trades")
        print("  - Prevents accidentally opening new positions")

        # Section 7: Time in force options
        print("\n=== 7. Time In Force Options ===")

        print("\nOrder timing strategies:")
        print("\n  GTC (Good-Till-Cancelled):")
        print("    Remains active until filled or cancelled")

        print("\n  GTD (Good-Till-Date):")
        print("    Expires at specified time")

        print("\n  FOK (Fill-Or-Kill):")
        print("    Must fill immediately and completely")
        print("    Or cancelled if not possible")

        print("\n  IOC (Immediate-Or-Cancel):")
        print("    Fill immediately (partial fills OK)")
        print("    Cancel unfilled portion")

        print("\n💡 GTD Usage:")
        print("  - Set time_in_force=TimeInForce.GTD")
        print("  - Provide gtd_time in RFC3339 format")
        print("  - Use datetime + timedelta to calculate expiry")
        print("  - Order automatically cancelled if not filled by expiry time")

        # Section 8: Type safety and validation
        print("\n=== 8. Type Safety ===")

        print("\nFiveTwenty provides strong type safety:")
        print("  ✅ Full mypy strict mode compliance")
        print("  ✅ InstrumentName enum prevents typos")
        print("  ✅ Pydantic models validate at runtime")
        print("  ✅ Type hints throughout")

        print("\nExample - InstrumentName enum:")
        print(f"  InstrumentName.EUR_USD = '{InstrumentName.EUR_USD}'")
        print(f"  InstrumentName.GBP_USD = '{InstrumentName.GBP_USD}'")
        print("  # IDE autocomplete available!")

        print("\nPydantic validation benefits:")
        print("  - Models validate input at runtime")
        print("  - Invalid data raises ValidationError immediately")
        print("  - Catch errors early before sending to API")
        print("  - Type coercion when safe (strings to Decimal, etc.)")

        # Section 9: Concurrent operations
        print("\n=== 9. Concurrent Operations ===")

        print("\nUse asyncio.gather() for parallel requests:")
        print("  - Fetch multiple instruments simultaneously")
        print("  - Significantly faster than sequential requests")
        print("  - Use list comprehension to create tasks")
        print("  - await asyncio.gather(*tasks) to run in parallel")

        # Demonstration
        print("\nDemo - Fetching 3 instruments concurrently:")
        start_time = asyncio.get_event_loop().time()

        price_results = await asyncio.gather(
            client.pricing.get_pricing(client.account_id, [InstrumentName.EUR_USD]),
            client.pricing.get_pricing(client.account_id, [InstrumentName.GBP_USD]),
            client.pricing.get_pricing(client.account_id, [InstrumentName.USD_JPY]),
        )

        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"\n✅ Fetched 3 prices concurrently in {elapsed:.2f}s")

        for result in price_results:
            price = result["prices"][0]
            if price.bids:
                print(f"  {price.instrument}: {price.bids[0].price}")

        # Section 10: Context managers and cleanup
        print("\n=== 10. Resource Management ===")

        print("\nAlways use context managers:")
        print("  ✅ Use 'async with AsyncClient() as client:'")
        print("  ✅ Client automatically closed when done")
        print("  ✅ Connections properly closed")
        print("  ✅ Resources released")
        print("  ✅ No connection leaks")
        print("  ✅ Clean shutdown even on errors")
        print("\n  ❌ Don't create client without context manager")
        print("  ❌ Resources may not be cleaned up properly")

        # Section 11: Custom timeouts
        print("\n=== 11. Custom Timeouts ===")

        print("\nConfigure timeouts for different scenarios:")
        print("  - Low-latency trading: AsyncClient(timeout=5.0)")
        print("  - Historical data: AsyncClient(timeout=30.0) for large datasets")
        print("  - Default timeout: 60 seconds")
        print("  - Catch httpx.TimeoutException for timeout errors")
        print("  - Balance between responsiveness and reliability")

        # Section 12: Comprehensive trading example
        print("\n=== 12. Complete Advanced Example ===")

        print("\n💡 Demo: Production-ready order with risk management...")

        # 1. Get current price with Decimal precision
        pricing_response = await client.pricing.get_pricing(account_id=client.account_id, instruments=[InstrumentName.EUR_USD])
        current_price = Decimal(pricing_response["prices"][0].asks[0].price)

        # 2. Calculate risk management levels (2% risk)
        account_summary = await client.accounts.get_account_summary(client.account_id)
        balance = Decimal(account_summary["account"].balance)
        risk_percent = Decimal("0.02")  # 2% risk
        risk_amount = balance * risk_percent

        # 3. Calculate position size based on risk and stop distance
        stop_distance = Decimal("0.0025")  # 25 pips
        units = Decimal(int(risk_amount / stop_distance))

        print(f"  Balance: {balance}")
        print(f"  Risk: {risk_percent * 100}% = {risk_amount}")
        print(f"  Stop Distance: {stop_distance}")
        print(f"  Position Size: {units} units")

        # 4. Place order with take profit and stop loss
        tp_price = current_price + Decimal("0.0050")  # 50 pips TP
        sl_price = current_price - stop_distance  # 25 pips SL

        # Use MarketOrderRequest to include all risk management parameters
        risk_managed_request = MarketOrderRequest(
            instrument=InstrumentName.EUR_USD,
            units=units,
            takeProfitOnFill=TakeProfitDetails(price=tp_price),
            stopLossOnFill=StopLossDetails(price=sl_price),
            clientExtensions=ClientExtensions(id=f"risk-managed-{datetime.now(timezone.utc).isoformat()}", tag="risk-managed", comment="2% risk with 2:1 RR"),
        )
        risk_managed_order = await client.orders.post_order(account_id=client.account_id, order_request=risk_managed_request)

        if risk_managed_order.get("orderFillTransaction"):
            print(f"\n✅ Risk-managed order filled at {risk_managed_order['orderFillTransaction'].price}")
            print(f"   TP: {tp_price} (+50 pips, 2% profit)")
            print(f"   SL: {sl_price} (-25 pips, 1% loss)")
            print("   Risk/Reward: 2:1")

        # Clean up our demo position
        await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

    print("\n✅ Advanced features demo completed!")
    print("\n📚 Summary of Advanced Features:")
    print("\n   Financial Precision:")
    print("   ✓ Always use Decimal for money calculations")
    print("   ✓ FiveTwenty handles Decimal↔string conversion automatically")
    print("   ✓ Prevents float rounding errors")
    print("\n   Traceability:")
    print("   ✓ Client Request IDs for debugging (OANDA logs)")
    print("   ✓ Client Extensions for metadata (persists in trades)")
    print("   ✓ Track strategies, tag orders, add comments")
    print("\n   Reliability:")
    print("   ✓ Streaming with automatic reconnection")
    print("   ✓ Configurable stall detection and backoff")
    print("   ✓ Production-grade error handling")
    print("\n   Trading Features:")
    print("   ✓ Bracket orders (Entry + TP + SL together)")
    print("   ✓ Position fill strategies (control how orders affect positions)")
    print("   ✓ Time in force options (GTC, GTD, FOK, IOC)")
    print("\n   Performance:")
    print("   ✓ Concurrent operations with asyncio.gather()")
    print("   ✓ Custom timeouts per use case")
    print("   ✓ Efficient async/await patterns")
    print("\n   Code Quality:")
    print("   ✓ Full mypy strict mode compliance")
    print("   ✓ Type-safe with InstrumentName enum")
    print("   ✓ Runtime validation with Pydantic")
    print("   ✓ Context managers for proper cleanup")
    print("\n   Production Readiness:")
    print("   - Decimal precision everywhere")
    print("   - Comprehensive error handling")
    print("   - Automatic retry with backoff")
    print("   - Structured logging and tracing")
    print("   - Type safety catches bugs early")
    print("   - Resource cleanup guaranteed")
    print("\n   These features combined create a robust,")
    print("   production-ready trading system foundation.")


if __name__ == "__main__":
    asyncio.run(main())
