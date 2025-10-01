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
    StopLossDetails,
    TakeProfitDetails,
)


async def main() -> None:
    """Advanced features demonstration."""

    async with AsyncClient() as client:
        # Section 1: Decimal precision
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

        from datetime import UTC, datetime

        client_request_id = f"trading-bot-v1-{datetime.now(UTC).isoformat()}"

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
        order = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000, client_extensions=extensions, client_request_id=client_request_id)

        if order.order_fill_transaction:
            print("\n✅ Order placed with extensions")
            print(f"Fill price: {order.order_fill_transaction.price}")

        # Section 4: Advanced streaming
        print("\n=== 4. Advanced Streaming ===")

        print("\nRobust streaming configuration:")
        print("""
from fivetwenty.models import ReconnectionPolicy, StreamingConfiguration

# Configure stall detection
config = StreamingConfiguration(
    stall_timeout=30.0,  # Detect stalls after 30s
    heartbeat_interval=5.0  # Expect heartbeats every 5s
)

# Configure reconnection policy
policy = ReconnectionPolicy(
    max_attempts=10,  # Try up to 10 times
    initial_delay=1.0,  # Start with 1s delay
    max_delay=60.0,  # Cap at 60s delay
    backoff_multiplier=2.0  # Double delay each time
)

# Stream with automatic reconnection
async for event in client.pricing.stream_pricing_with_retries(
    account_id=client.account_id,
    instruments=[InstrumentName.EUR_USD],
    config=config,
    policy=policy
):
    if event.type == "PRICE":
        print(f"Price: {event.bids[0].price}")
    elif event.type == "HEARTBEAT":
        # Connection is alive
        pass
        """)

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

        bracket_order = await client.orders.post_market_order(
            account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000, take_profit_on_fill=TakeProfitDetails(price=str(take_profit_price)), stop_loss_on_fill=StopLossDetails(price=str(stop_loss_price)), client_extensions=ClientExtensions(comment="Bracket order demo")
        )

        if bracket_order.order_fill_transaction:
            print("\n✅ Bracket order filled")
            print(f"Entry: {bracket_order.order_fill_transaction.price}")

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

        print("\n💡 Example - REDUCE_ONLY:")
        print("""
# Only close existing position, don't open new one
await client.orders.post_market_order(
    account_id=client.account_id,
    instrument=InstrumentName.EUR_USD,
    units=-1000,
    position_fill=OrderPositionFill.REDUCE_ONLY
)
        """)

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

        print("\n💡 Example - GTD:")
        print("""
from datetime import datetime, timedelta

expiry = datetime.utcnow() + timedelta(hours=24)

await client.orders.post_limit_order(
    account_id=client.account_id,
    instrument=InstrumentName.EUR_USD,
    units=1000,
    price="1.08500",
    time_in_force=TimeInForce.GTD,
    gtd_time=expiry.strftime("%Y-%m-%dT%H:%M:%S.000000000Z")
)
        """)

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

        print("\nPydantic validation:")
        print("""
from fivetwenty.models import ClientExtensions

# Valid
ext = ClientExtensions(id="test-123", tag="my-tag")

# Invalid - will raise validation error
try:
    ext = ClientExtensions(id="", tag="")  # Empty strings
except ValidationError as e:
    print(f"Validation error: {e}")
        """)

        # Section 9: Concurrent operations
        print("\n=== 9. Concurrent Operations ===")

        print("\nUse asyncio.gather() for parallel requests:")

        print("\n💡 Example:")
        print("""
# Fetch multiple instruments simultaneously
instruments = [
    InstrumentName.EUR_USD,
    InstrumentName.GBP_USD,
    InstrumentName.USD_JPY,
    InstrumentName.AUD_USD
]

# Concurrent requests
prices = await asyncio.gather(*[
    client.pricing.get_pricing(
        account_id=client.account_id,
        instruments=[instrument]
    )
    for instrument in instruments
])

# All prices fetched in parallel!
for price_data in prices:
    price = price_data["prices"][0]
    print(f"{price.instrument}: {price.bids[0].price}")
        """)

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

        print("\n✅ Correct:")
        print("""
async with AsyncClient() as client:
    # Client automatically closed when done
    result = await client.accounts.get_account_summary(client.account_id)
        """)

        print("\n❌ Incorrect:")
        print("""
client = AsyncClient()
# Resources may not be cleaned up properly!
result = await client.accounts.get_account_summary(client.account_id)
        """)

        print("\nContext managers ensure:")
        print("  ✅ Connections properly closed")
        print("  ✅ Resources released")
        print("  ✅ No connection leaks")
        print("  ✅ Clean shutdown even on errors")

        # Section 11: Custom timeouts
        print("\n=== 11. Custom Timeouts ===")

        print("\nConfigure timeouts for different scenarios:")

        print("\n💡 Examples:")
        print("""
# Fast timeout for low-latency trading
async with AsyncClient(timeout=5.0) as client:
    price = await client.pricing.get_pricing(...)

# Longer timeout for historical data
async with AsyncClient(timeout=30.0) as client:
    candles = await client.pricing.get_account_instrument_candles(
        count=5000  # Large dataset
    )

# Per-request timeout using httpx
import httpx

async with AsyncClient() as client:
    try:
        result = await client.accounts.get_account_summary(...)
    except httpx.TimeoutException:
        print("Request timed out")
        """)

        # Section 12: Comprehensive trading example
        print("\n=== 12. Complete Advanced Example ===")

        print("\nPutting it all together:")

        # Clean up our demo position
        await client.positions.close_position(account_id=client.account_id, instrument=InstrumentName.EUR_USD)

        # Complete example
        print("\n💡 Production-ready trading example:")
        print("""
async def execute_trade_with_risk_management(client):
    # 1. Get current price with Decimal precision
    pricing = await client.pricing.get_pricing(
        account_id=client.account_id,
        instruments=[InstrumentName.EUR_USD]
    )
    entry_price = Decimal(pricing["prices"][0].asks[0].price)

    # 2. Calculate risk management levels
    risk_percent = Decimal("0.02")  # 2% risk
    account = await client.accounts.get_account_summary(client.account_id)
    balance = Decimal(account["account"].balance)

    risk_amount = balance * risk_percent
    stop_distance = Decimal("0.0025")  # 25 pips
    units = int(risk_amount / stop_distance)

    # 3. Place order with full risk management
    order = await client.orders.post_market_order(
        account_id=client.account_id,
        instrument=InstrumentName.EUR_USD,
        units=units,
        take_profit_on_fill=TakeProfitDetails(
            price=str(entry_price + Decimal("0.0050"))  # 50 pips TP
        ),
        stop_loss_on_fill=StopLossDetails(
            price=str(entry_price - stop_distance)  # 25 pips SL
        ),
        client_extensions=ClientExtensions(
            id=f"trade-{datetime.utcnow().isoformat()}",
            tag="risk-managed",
            comment="Systematic entry with 2% risk"
        ),
        position_fill=OrderPositionFill.DEFAULT
    )

    return order
        """)

    print("\n✅ Advanced features demo completed!")


if __name__ == "__main__":
    asyncio.run(main())
