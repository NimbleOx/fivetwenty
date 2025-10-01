#!/usr/bin/env python3
"""
Enhanced Error Handling Example

Demonstrates robust error handling patterns:
- VeeTwentyError exception handling
- Retry strategies
- Rate limit handling
- Network error recovery
- Validation errors
- Production-ready error patterns
"""

import asyncio

from fivetwenty import AsyncClient
from fivetwenty.exceptions import VeeTwentyError
from fivetwenty.models import InstrumentName


async def main() -> None:
    """Enhanced error handling patterns example."""

    async with AsyncClient() as client:
        # Section 1: Basic error handling
        print("\n=== 1. Basic Error Handling ===")

        print("\nAll API errors are wrapped in VeeTwentyError:")

        try:
            # This will fail - invalid instrument
            await client.orders.post_market_order(account_id=client.account_id, instrument="INVALID_INSTRUMENT", units=1000)
        except VeeTwentyError as e:
            print("✅ Caught VeeTwentyError:")
            print(f"  Status Code: {e.status_code}")
            print(f"  Message: {e.message}")
            print(f"  Error Code: {e.code if e.code else 'N/A'}")

        # Section 2: HTTP status code errors
        print("\n=== 2. HTTP Status Errors ===")

        print("\nHandling different HTTP error types:\n")

        # 400 Bad Request - Validation error
        print("400 Bad Request (validation):")
        try:
            await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=InstrumentName.EUR_USD,
                units=0,  # Invalid - units cannot be zero
            )
        except VeeTwentyError as e:
            if e.status_code == 400:
                print(f"  ✅ Validation error caught: {e.message}")

        # 404 Not Found
        print("\n404 Not Found:")
        try:
            await client.orders.get_order(
                account_id=client.account_id,
                order_specifier="99999999",  # Non-existent order
            )
        except VeeTwentyError as e:
            if e.status_code == 404:
                print(f"  ✅ Resource not found: {e.message}")

        # Section 3: Validation errors
        print("\n=== 3. Validation Errors ===")

        print("\nCommon validation errors:\n")

        validation_tests = [
            ("Zero units", InstrumentName.EUR_USD, 0),
            ("Invalid units (too large)", InstrumentName.EUR_USD, 1000000000),
        ]

        for test_name, instrument, units in validation_tests:
            try:
                await client.orders.post_market_order(account_id=client.account_id, instrument=instrument, units=units)
            except VeeTwentyError as e:
                print(f"{test_name}:")
                print(f"  Error: {e.message}")

        # Section 4: Rate limiting
        print("\n=== 4. Rate Limiting ===")

        print("\nHandling 429 Too Many Requests:")
        print("  - OANDA enforces rate limits")
        print("  - SDK includes automatic retry with backoff")
        print("  - Respect Retry-After header when present")

        print("\n💡 Retry strategy example:")
        print("""
import asyncio

async def retry_with_backoff(func, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            return await func()
        except VeeTwentyError as e:
            if e.status_code == 429:
                # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise Exception("Max retry attempts reached")
        """)

        # Section 5: Network errors
        print("\n=== 5. Network Errors ===")

        print("\nHandling network issues:")
        print("  - Connection timeouts")
        print("  - Connection refused")
        print("  - DNS failures")
        print("  - Temporary network outages")

        print("\n💡 Retry logic with timeouts:")
        print("""
import httpx

try:
    async with AsyncClient(timeout=10.0) as client:
        result = await client.accounts.get_account_summary(client.account_id)
except httpx.TimeoutException:
    print("Request timed out - network issue")
except httpx.ConnectError:
    print("Connection failed - check network")
        """)

        # Section 6: Streaming errors
        print("\n=== 6. Streaming Errors ===")

        print("\nStreaming can encounter various errors:")
        print("  - StreamStall: No data received within timeout")
        print("  - Connection drops")
        print("  - Network interruptions")

        print("\n💡 Robust streaming:")
        print("""
from fivetwenty.models import ReconnectionPolicy, StreamingConfiguration

config = StreamingConfiguration(stall_timeout=30.0)
policy = ReconnectionPolicy(max_attempts=5)

try:
    async for event in client.pricing.stream_pricing_with_retries(
        account_id=client.account_id,
        instruments=[InstrumentName.EUR_USD],
        config=config,
        policy=policy
    ):
        # Handle events with automatic reconnection
        print(f"Price: {event.bids[0].price}")
except StreamStall:
    print("Stream stalled - exceeded timeout")
        """)

        # Section 7: Order rejection handling
        print("\n=== 7. Order Rejection Handling ===")

        print("\nOrders can be rejected for various reasons:\n")

        # Try to place an order that might be rejected
        try:
            # This might fail due to insufficient margin
            await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=InstrumentName.EUR_USD,
                units=10000000,  # Very large order
            )
        except VeeTwentyError as e:
            print("Order rejected:")
            print(f"  Reason: {e.message}")
            print("\nCommon rejection reasons:")
            print("  - Insufficient margin")
            print("  - Market closed")
            print("  - Invalid price")
            print("  - Instrument not tradeable")
            print("  - Account restrictions")

        # Section 8: Partial fills and slippage
        print("\n=== 8. Partial Fills ===")

        print("\nDetecting partial fills:")

        order = await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=1000)

        if order.order_fill_transaction:
            requested = 1000
            filled = int(order.order_fill_transaction.units)

            if filled < requested:
                print("⚠️  Partial fill detected!")
                print(f"  Requested: {requested}")
                print(f"  Filled: {filled}")
                print(f"  Unfilled: {requested - filled}")
            else:
                print(f"✅ Full fill: {filled} units")

        # Close the position
        await client.orders.post_market_order(account_id=client.account_id, instrument=InstrumentName.EUR_USD, units=-1000)

        # Section 9: Comprehensive retry decorator
        print("\n=== 9. Retry Decorator ===")

        print("\nReusable retry logic with exponential backoff:\n")

        print("""
def async_retry(max_attempts=3, base_delay=1.0, backoff=2.0, jitter=True):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except VeeTwentyError as e:
                    if attempt == max_attempts - 1:
                        raise  # Last attempt, re-raise

                    # Retry on specific errors
                    if e.status_code in [429, 500, 502, 503, 504]:
                        delay = base_delay * (backoff ** attempt)
                        if jitter:
                            delay *= (0.5 + random.random())

                        print(f"Retry {attempt + 1}/{max_attempts} after {delay:.1f}s")
                        await asyncio.sleep(delay)
                    else:
                        raise  # Don't retry client errors

            raise Exception("Should never reach here")
        return wrapper
    return decorator

@async_retry(max_attempts=3)
async def fetch_account_summary(client):
    return await client.accounts.get_account_summary(client.account_id)
        """)

        # Section 10: Production error patterns
        print("\n=== 10. Production Error Patterns ===")

        print("\nProduction-ready error handling:\n")

        print("""
import logging

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, client):
        self.client = client
        self.error_count = 0
        self.max_errors = 10

    async def place_order_safe(self, instrument, units):
        try:
            order = await self.client.orders.post_market_order(
                account_id=self.client.account_id,
                instrument=instrument,
                units=units
            )

            # Reset error count on success
            self.error_count = 0

            logger.info(f"Order placed: {order.order_fill_transaction.id}")
            return order

        except VeeTwentyError as e:
            self.error_count += 1

            logger.error(
                f"Order failed: {e.message}",
                extra={
                    "status_code": e.status_code,
                    "error_code": e.code,
                    "instrument": instrument,
                    "units": units
                }
            )

            # Circuit breaker pattern
            if self.error_count >= self.max_errors:
                logger.critical("Too many errors - stopping bot")
                raise Exception("Circuit breaker tripped")

            # Graceful degradation
            if e.status_code == 429:
                # Rate limited - back off
                await asyncio.sleep(60)

            return None
        """)

        # Section 11: Error recovery strategies
        print("\n=== 11. Error Recovery Strategies ===")

        print("\nRecovery approaches:")

        print("\n1. Retry with exponential backoff:")
        print("   - Network errors: Retry immediately")
        print("   - Rate limits: Back off exponentially")
        print("   - Server errors: Retry with delay")

        print("\n2. Fallback strategies:")
        print("   - Try alternative instrument")
        print("   - Reduce order size")
        print("   - Queue for later execution")

        print("\n3. Circuit breaker:")
        print("   - Track consecutive failures")
        print("   - Stop trading after threshold")
        print("   - Alert operators")

        print("\n4. Graceful degradation:")
        print("   - Continue with reduced functionality")
        print("   - Switch to read-only mode")
        print("   - Use cached data when available")

        print("\n💡 Example recovery:")
        print("""
async def place_order_with_recovery(client, instrument, units):
    try:
        # Try primary order
        return await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=instrument,
            units=units
        )
    except VeeTwentyError as e:
        if e.status_code == 400 and "INSUFFICIENT_MARGIN" in str(e.message):
            # Fallback: try with 50% size
            print(f"Insufficient margin, trying 50% size...")
            return await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=units // 2
            )
        raise
        """)

    print("\n✅ Enhanced error handling example completed!")


if __name__ == "__main__":
    asyncio.run(main())
