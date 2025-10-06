#!/usr/bin/env python3
"""
Enhanced Error Handling Example

Demonstrates robust error handling patterns:
- FiveTwentyError exception handling
- Retry strategies
- Rate limit handling
- Network error recovery
- Validation errors
- Production-ready error patterns
"""

import asyncio

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import InstrumentName


async def main() -> None:
    """Enhanced error handling patterns example."""

    # ERROR HANDLING is CRITICAL for production trading systems
    # Poor error handling = lost money, missed opportunities, system crashes
    #
    # Why comprehensive error handling matters:
    # - Network issues: Internet drops, timeouts, DNS failures
    # - API errors: Rate limits, validation failures, rejected orders
    # - Market conditions: Insufficient margin, market closed, low liquidity
    # - System failures: Server errors, maintenance windows, bugs
    #
    # Without proper error handling:
    # - System crashes on minor issues
    # - Silent failures (orders not placed)
    # - Cascade failures (one error causes many)
    # - No visibility into problems
    # - Manual intervention required constantly
    #
    # With proper error handling:
    # - Graceful degradation
    # - Automatic recovery
    # - Clear error messages
    # - Monitoring and alerting
    # - High availability
    #
    # This example demonstrates:
    # 1. Exception types and handling
    # 2. Retry strategies with backoff
    # 3. Rate limit handling
    # 4. Network error recovery
    # 5. Production-ready patterns

    async with AsyncClient() as client:
        # Section 1: Basic error handling
        # ===============================
        # ALL API errors are wrapped in FiveTwentyError
        # This provides consistent error handling across all endpoints
        #
        # FiveTwentyError attributes:
        # - status: HTTP status code (400, 404, 429, 500, etc.)
        # - message: Human-readable error description
        # - code: OANDA error code (if provided)
        # - details: Additional error details
        #
        # Common error categories:
        # - 400 Bad Request: Validation errors (invalid parameters)
        # - 401 Unauthorized: Authentication failed (bad token)
        # - 403 Forbidden: Not allowed (permissions)
        # - 404 Not Found: Resource doesn't exist
        # - 429 Too Many Requests: Rate limited
        # - 500 Internal Server Error: Server-side issue
        # - 503 Service Unavailable: Maintenance or overload
        print("\n=== 1. Basic Error Handling ===")

        print("\nAll API errors are wrapped in FiveTwentyError:")
        print("  - Consistent exception type across all operations")
        print("  - Structured error information (status, message, code)")
        print("  - Easy to catch and handle systematically")

        try:
            # This will fail - invalid instrument
            await client.orders.post_market_order(account_id=client.account_id, instrument="INVALID_INSTRUMENT", units=1000)  # type: ignore[arg-type]
        except FiveTwentyError as e:
            print("✅ Caught FiveTwentyError:")
            print(f"  Status Code: {e.status}")
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
        except FiveTwentyError as e:
            if e.status == 400:
                print(f"  ✅ Validation error caught: {e.message}")

        # 404 Not Found
        print("\n404 Not Found:")
        try:
            await client.orders.get_order(
                account_id=client.account_id,
                order_specifier="99999999",  # Non-existent order
            )
        except FiveTwentyError as e:
            if e.status == 404:
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
            except FiveTwentyError as e:
                print(f"{test_name}:")
                print(f"  Error: {e.message}")

        # Section 4: Rate limiting
        print("\n=== 4. Rate Limiting ===")

        print("\nHandling 429 Too Many Requests:")
        print("  - OANDA enforces rate limits")
        print("  - SDK includes automatic retry with backoff")
        print("  - Respect Retry-After header when present")

        print("\n💡 Retry strategy example:")

        # Simple retry function with exponential backoff
        from collections.abc import Callable
        from typing import Any

        async def retry_with_backoff(func: Callable[[], Any], max_attempts: int = 3) -> Any:
            """Retry function with exponential backoff for rate limits."""
            for attempt in range(max_attempts):
                try:
                    return await func()
                except FiveTwentyError as e:
                    if e.status == 429 and attempt < max_attempts - 1:
                        # Rate limited
                        wait_time = 2**attempt  # Exponential backoff
                        print(f"  Rate limited, would wait {wait_time}s...")
                        # await asyncio.sleep(wait_time)  # Commented out for demo
                    else:
                        raise
            raise RuntimeError("Max retry attempts reached")

        print("✅ Retry function defined (see code for implementation)")
        print("   - Catches 429 errors")
        print("   - Exponential backoff: 1s, 2s, 4s...")
        print("   - Configurable max attempts")

        # Section 5: Network errors
        print("\n=== 5. Network Errors ===")

        print("\nHandling network issues:")
        print("  - Connection timeouts")
        print("  - Connection refused")
        print("  - DNS failures")
        print("  - Temporary network outages")

        print("\n💡 Retry logic with timeouts:")
        print("  - Set timeout parameter on AsyncClient(timeout=10.0)")
        print("  - Catch httpx.TimeoutException for timeout errors")
        print("  - Catch httpx.ConnectError for connection failures")
        print("  - Implement retry logic for transient network issues")

        # Section 6: Streaming errors
        print("\n=== 6. Streaming Errors ===")

        print("\nStreaming can encounter various errors:")
        print("  - StreamStall: No data received within timeout")
        print("  - Connection drops")
        print("  - Network interruptions")

        print("\n💡 Robust streaming:")
        print("  - Use stream_pricing_with_retries() instead of get_pricing_stream()")
        print("  - Configure StreamingConfiguration with stall_timeout")
        print("  - Configure ReconnectionPolicy with max_attempts and backoff")
        print("  - Catch StreamStall exception after all retries exhausted")

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
        except FiveTwentyError as e:
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

        if order.get("orderFillTransaction"):
            requested = 1000
            filled = abs(int(order["orderFillTransaction"].units))

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

        print("\nReusable retry logic with exponential backoff:")
        print("  - Create decorator with max_attempts, base_delay, backoff, jitter")
        print("  - Only retry on specific errors: 429, 500, 502, 503, 504")
        print("  - Don't retry client errors (4xx except 429)")
        print("  - Use jitter to prevent thundering herd")
        print("  - Calculate delay: base_delay * (backoff ** attempt)")
        print("  - Apply decorator to async functions needing retry logic")

        # Section 10: Production error patterns
        print("\n=== 10. Production Error Patterns ===")

        print("\nProduction-ready error handling patterns:")
        print("  - Track error_count to detect cascading failures")
        print("  - Reset counter on successful operations")
        print("  - Implement circuit breaker: stop after max_errors threshold")
        print("  - Log errors with structured context (status, code, params)")
        print("  - Graceful degradation: back off on rate limits")
        print("  - Return None or default on recoverable errors")
        print("  - Raise critical exceptions on circuit breaker trip")

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

        print("\n💡 Example recovery pattern:")
        print("  - Catch specific errors (e.g., INSUFFICIENT_MARGIN)")
        print("  - Implement fallback: reduce order size by 50%")
        print("  - Retry operation with adjusted parameters")
        print("  - Re-raise if fallback also fails")

    print("\n✅ Enhanced error handling example completed!")
    print("\n📚 Summary:")
    print("   Error Categories:")
    print("   - 4xx: Client errors (your fault - fix your code)")
    print("   - 5xx: Server errors (OANDA's fault - retry)")
    print("   - Network: Connection issues (transient - retry)")
    print("\n   Best Practices:")
    print("   - Catch FiveTwentyError for all API operations")
    print("   - Implement exponential backoff for retries")
    print("   - Respect rate limits (429 errors)")
    print("   - Use circuit breakers for cascading failures")
    print("   - Log errors with context for debugging")
    print("   - Monitor error rates and alert on spikes")
    print("   - Graceful degradation over crashes")
    print("\n   Production Checklist:")
    print("   ✓ Comprehensive try/except blocks")
    print("   ✓ Retry logic with backoff")
    print("   ✓ Rate limit handling")
    print("   ✓ Structured logging")
    print("   ✓ Error metrics/monitoring")
    print("   ✓ Circuit breakers")
    print("   ✓ Fallback strategies")
    print("   ✓ Alerting on critical errors")


if __name__ == "__main__":
    asyncio.run(main())
