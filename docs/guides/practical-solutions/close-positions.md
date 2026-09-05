# How to Close Positions

!!! info "Config How-to Guide - Problem-solving content"
    **Use this guide when:** You have existing positions and need to close them

    **Expected outcome:** Successfully closed positions with proper confirmation

    **Assumed knowledge:** Basic familiarity with FiveTwenty and trading concepts

**Problem**: You need to close existing trading positions to realize profits/losses or reduce risk.

**Solution**: Use `client.positions.close_position()` to close the long and short sides explicitly, with proper error handling.

---

## Prerequisites

- Active OANDA account with existing positions
- FiveTwenty configured with valid token
- Account ID of the trading account

---

## Quick Close: Single Instrument

Close all positions for one specific instrument. The position-close endpoint works for hedging accounts too: an opposite market order with `positionFill=DEFAULT` can open a new hedge instead of closing a trade.

<!-- fragment: partial position closing example -->
```python
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def close_position(account_id: str, instrument: str) -> Any:
    """Close every open side of an instrument and confirm each requested fill."""
    async with AsyncClient(
        token="your-token",
        account_id=account_id,
        environment=Environment.PRACTICE,
    ) as client:
        try:
            positions_response = await client.positions.get_open_positions(account_id)
            position = next((p for p in positions_response["positions"] if p.instrument == instrument), None)
            if position is None:
                print(f"No open position for {instrument}")
                return None

            # Both sides can be open on a hedging account, even when net units are zero.
            has_long = position.long.units != 0
            has_short = position.short.units != 0
            if not has_long and not has_short:
                print(f"No units to close for {instrument}")
                return None

            response = await client.positions.close_position(
                account_id=account_id,
                instrument=instrument,
                long_units="ALL" if has_long else "NONE",
                short_units="ALL" if has_short else "NONE",
            )

            # Each requested side has its own fill or cancellation transaction.
            for side, requested in (("long", has_long), ("short", has_short)):
                if not requested:
                    continue
                fill = response.get(f"{side}OrderFillTransaction")
                if fill is None:
                    print(f"Closure incomplete for {instrument}: {side} side did not fill; check remaining positions")
                    return None
                print(f"Closed {side} side: {fill.units} units at {fill.price}, realized P/L {fill.pl}")

            return response
        except FiveTwentyError as e:
            print(f"OANDA error closing {instrument}: {e.message}")
            return None


# Usage
account_id = "your-account-id"
close_result = await close_position(account_id, "EUR_USD")
```

---

## Partial Close: Specific Units

Close only part of a position:

<!-- fragment: partial position closing example -->
```python
from typing import Any

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def close_partial_position(account_id: str, instrument: str, units_to_close: int) -> Any:
    """Positive units close the long side; negative units close the short side."""
    async with AsyncClient(
        token="your-token",
        account_id=account_id,
        environment=Environment.PRACTICE,
    ) as client:
        try:
            if units_to_close == 0:
                raise ValueError("units_to_close must be nonzero")

            positions_response = await client.positions.get_open_positions(account_id)
            position = next((p for p in positions_response["positions"] if p.instrument == instrument), None)
            if position is None:
                raise ValueError(f"No position found for {instrument}")

            side = "long" if units_to_close > 0 else "short"
            available = abs(position.long.units if units_to_close > 0 else position.short.units)
            quantity = abs(units_to_close)
            if quantity > available:
                raise ValueError(f"Cannot close {quantity} {side} units; only {available} are open")

            # Explicit NONE leaves the other side unchanged; close quantities are positive.
            response = await client.positions.close_position(
                account_id=account_id,
                instrument=instrument,
                long_units=str(quantity) if side == "long" else "NONE",
                short_units=str(quantity) if side == "short" else "NONE",
            )
            fill = response.get(f"{side}OrderFillTransaction")
            if fill is None:
                print(f"Partial closure did not fill for {instrument}; check remaining positions")
                return None
            print(f"Closed {quantity} {side} units at {fill.price}, realized P/L {fill.pl}")
            return response
        except (FiveTwentyError, ValueError) as e:
            print(f"Partial close error: {e}")
            return None


# Usage - close 500 units of long EUR_USD
result = await close_partial_position(account_id, "EUR_USD", 500)
```

---

## Batch Close: Multiple Instruments

Close positions across multiple instruments:

<!-- fragment: partial multiple position closing example -->
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Environment


async def close_multiple_positions(account_id: str, instruments: list[str]) -> dict[str, Any]:
    """Close positions for multiple instruments with rate limiting and error isolation."""

    # Step 1: Initialize client for batch position closing operations
    async with AsyncClient(
        token="your-token",           # OANDA API authentication token
        account_id=account_id,
        environment=Environment.PRACTICE  # Practice environment for safe batch operations
    ) as client:

        # Step 2: Initialize results dictionary to track outcomes per instrument
        # Key: instrument symbol, Value: transaction result or None for failures
        results: dict[str, Any] = {}

        print(f"Starting batch closure for {len(instruments)} instruments...")
        print(f"Target instruments: {', '.join(instruments)}")

        # Step 3: Process each instrument sequentially to avoid overwhelming API
        # Sequential processing prevents rate limiting and allows error isolation
        for i, instrument in enumerate(instruments, 1):
            try:
                print(f"\nProcessing {instrument} ({i}/{len(instruments)})...")

                # Step 4: Call position closure function for each instrument
                # Reusing close_position() function ensures consistent logic
                result = await close_position(account_id, instrument)
                results[instrument] = result

                # Step 5: Provide immediate feedback on closure attempt
                if result:
                    print(f"   {instrument}: Successfully closed position")
                else:
                    print(f"   Error: {instrument}: No position found or closure failed")

                # Step 6: Rate limiting protection to avoid API throttling
                # 100ms delay prevents exceeding OANDA's rate limits
                # Adjust delay based on account tier and API limits
                await asyncio.sleep(0.1)
                print(f"   Rate limit delay applied (100ms)")

            except Exception as e:
                # Step 7: Isolate errors per instrument to prevent batch failure
                # One failed instrument shouldn't stop processing others
                print(f"Error: Failed to close {instrument}: {e}")
                print(f"   Note: Error isolated - continuing with remaining instruments")
                results[instrument] = None

        # Step 8: Generate comprehensive batch operation summary
        successful_closes = sum(1 for r in results.values() if r is not None)
        failed_closes = len(instruments) - successful_closes

        print(f"\nBatch Closure Summary:")
        print(f"   Successful closures: {successful_closes}")
        print(f"   Error: Failed closures: {failed_closes}")
        print(f"   Success: rate: {(successful_closes/len(instruments)*100):.1f}%")

        # Step 9: Detailed breakdown of results per instrument
        print(f"\nDetailed Results:")
        for instrument, result in results.items():
            status = "Success CLOSED" if result else "Error FAILED"
            print(f"   {instrument}: {status}")

        return results

# Usage
instruments_to_close = ["EUR_USD", "GBP_USD", "USD_JPY"]
close_results = await close_multiple_positions(account_id, instruments_to_close)
```

---

## Emergency Close: All Positions

Close all open positions immediately:

<!-- fragment: Demo emergency close with top-level await and exception code patterns -->
```python
import asyncio
from typing import Any
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def emergency_close_all(account_id: str) -> list[Any]:
    """Emergency close all open positions with maximum speed and comprehensive error handling."""

    # Step 1: Initialize client for emergency operations
    # Emergency situations require immediate action with all available speed
    async with AsyncClient(
        token="your-token",           # OANDA API authentication token
        account_id=account_id,
        environment=Environment.PRACTICE  # Use PRACTICE for testing emergency procedures
    ) as client:
        try:
            # Step 2: Alert operators and begin emergency closure sequence
            print("⚠️ EMERGENCY CLOSE INITIATED: Closing all positions immediately!")
            print("⚠️ This will close ALL open positions - use with extreme caution")
            print("Note: Recommend logging this emergency event for post-incident analysis")

            # Step 3: Retrieve all open positions for emergency closure
            # get_open_positions() only returns positions with non-zero units
            positions = (await client.positions.get_open_positions(account_id))["positions"]

            if not positions:
                # Step 4: Handle scenario where no positions exist
                print("Emergency scan complete: No open positions to close")
                print("Note: Account is already flat - no action required")
                return []

            # Step 5: Prepare concurrent closure tasks for maximum speed
            # Concurrent execution minimizes time to close all positions
            close_tasks = []
            print(f"Emergency closure scope: {len(positions)} positions found")

            for position in positions:
                # Step 6: Validate position has actual units before creating close task
                # Both long.units and short.units must be checked
                if (position.long.units != 0 or position.short.units != 0):
                    print(f"   Targeting {position.instrument}: "
                          f"Long={position.long.units}, Short={position.short.units}")

                    # Step 7: Create concurrent closure task for each position
                    # Using previously defined close_position() function for consistency
                    task = close_position(account_id, position.instrument)
                    close_tasks.append((position.instrument, task))

            if not close_tasks:
                # Step 8: Handle edge case where positions exist but have zero units
                print("⚠️ Positions found but all have zero units - already flat")
                return []

            # Step 9: Execute all position closures concurrently for maximum speed
            # asyncio.gather() with return_exceptions=True prevents one failure from stopping others
            print(f"Executing {len(close_tasks)} concurrent closures...")

            # Extract just the tasks for gather()
            tasks = [task for _, task in close_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Step 10: Analyze emergency closure results and provide comprehensive feedback
            successful_closes = sum(1 for r in results if r is not None and not isinstance(r, Exception))
            failed_closes = len(close_tasks) - successful_closes

            print(f"\n⚠️ EMERGENCY CLOSE COMPLETE:")
            print(f"   Successful closures: {successful_closes}")
            print(f"   Error: Failed closures: {failed_closes}")
            print(f"   Emergency success rate: {(successful_closes/len(close_tasks)*100):.1f}%")

            # Step 11: Detailed emergency results for incident analysis
            print(f"\nEmergency Closure Details:")
            for i, (instrument, result) in enumerate(zip([inst for inst, _ in close_tasks], results)):
                if isinstance(result, Exception):
                    print(f"   Error: {instrument}: FAILED - {result}")
                elif result is not None:
                    print(f"   {instrument}: CLOSED successfully")
                else:
                    print(f"   ⚠️ {instrument}: No position found")

            # Step 12: Post-emergency recommendations
            if failed_closes > 0:
                print(f"\n⚠️ EMERGENCY ALERT: {failed_closes} positions failed to close")
                print(f"Note: Immediate action required: manually verify and close remaining positions")
                print(f"Consider contacting OANDA support if issues persist")
            else:
                print(f"\nEmergency closure successful - all positions closed")
                print(f"Recommend account reconciliation and incident documentation")

            return results

        except FiveTwentyError as e:
            # Step 13: Handle catastrophic API failure during emergency
            print(f"Error: CRITICAL EMERGENCY FAILURE: {e.message}")
            print(f"   Error: code: {e.code}")
            print(f"⚠️ IMMEDIATE ACTION REQUIRED:")
            print(f"   1. Check network connectivity")
            print(f"   2. Verify API token validity")
            print(f"   3. Contact OANDA support immediately")
            print(f"   4. Consider manual position closure via OANDA platform")
            return []

# Usage (use with extreme caution!)
# emergency_results = await emergency_close_all(account_id)
```

---

## Troubleshooting

### Common Issues

**"No open position found"**
- Verify the instrument symbol is correct
- Check if position was already closed
- Ensure you're using the correct account ID

**"Insufficient units to close"**
- Check actual position size before closing
- Account for any pending orders that might affect position

**Rate limiting errors**
- Add delays between multiple close operations
- Use batch operations instead of individual closes

### Best Practices

- Always verify position exists before attempting to close
- Handle partial fills - not all market orders execute in full
- Log all close operations for audit trail
- Use practice environment for testing close logic
- Consider using stop-loss orders instead of manual closes for risk management

---

## Good: Verification

After closing positions, verify the operation:

<!-- fragment: Demo position verification with return statement patterns -->
```python
from typing import Any
from fivetwenty import AsyncClient, Environment


async def verify_position_closed(account_id: str, instrument: str) -> bool:
    """Verify a position was successfully closed with comprehensive validation and detailed feedback."""

    # Step 1: Initialize client connection for position verification
    async with AsyncClient(
        token="your-token",           # OANDA API authentication token
        account_id=account_id,
        environment=Environment.PRACTICE  # Practice environment for testing verification
    ) as client:

        # Step 2: Retrieve current positions to verify closure
        # get_open_positions() only returns positions with non-zero units
        # If instrument not in results, position is definitely closed
        positions = (await client.positions.get_open_positions(account_id))["positions"]

        # Step 3: Search for the target instrument in open positions
        # Using next() with generator for efficient single-match lookup
        position = next((p for p in positions if p.instrument == instrument), None)

        # Step 4: Comprehensive position closure verification
        if position and (position.long.units != 0 or position.short.units != 0):
            # Step 5: Position still exists with non-zero units - closure failed
            print(f"⚠️ VERIFICATION FAILED: Position still open for {instrument}")
            print(f"   Current long units: {position.long.units}")
            print(f"   Current short units: {position.short.units}")
            print(f"   Net position: {position.long.units + position.short.units}")
            print(f"Note: Possible causes:")
            print(f"   - Partial fill on close order")
            print(f"   - Market order rejected due to insufficient margin")
            print(f"   - New position opened after close attempt")
            print(f"   - Close order still pending execution")
            return False
        else:
            # Step 6: Position successfully closed or never existed
            if position is None:
                # Position not found in open positions list
                print(f"VERIFICATION SUCCESSFUL: Position confirmed closed for {instrument}")
                print(f"   Status: No open position found (fully closed)")
            else:
                # Position exists but with zero units (edge case)
                print(f"VERIFICATION SUCCESSFUL: Position has zero units for {instrument}")
                print(f"   Status: Position object exists but no active units")

            print(f"Note: Position closure verification complete")
            print(f"Account is flat for {instrument} - no exposure remaining")
            return True

# Verify closure
is_closed = await verify_position_closed(account_id, "EUR_USD")
```

You can now close a single position, close partial units, batch-close multiple instruments, and verify the result.
