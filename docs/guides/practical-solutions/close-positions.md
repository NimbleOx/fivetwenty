# How to Close Positions

!!! info "Config How-to Guide - Problem-solving content"
    **Use this guide when:** You have existing positions and need to close them

    **Expected outcome:** Successfully closed positions with proper confirmation

    **Assumed knowledge:** Basic familiarity with FiveTwenty and trading concepts

**Problem**: You need to close existing trading positions to realize profits/losses or reduce risk.

**Solution**: Use the FiveTwenty to close positions via market orders with proper error handling.

---

## Prerequisites

- Active OANDA account with existing positions
- FiveTwenty configured with valid token
- Account ID of the trading account

---

## Quick Close: Single Instrument

Close all positions for one specific instrument:

<!-- fragment: partial position closing example -->
```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def close_position(account_id: str, instrument: str) -> Any:
    """Close all positions for a specific instrument with comprehensive error handling."""

    # Step 1: Initialize AsyncClient with proper environment configuration
    # Environment.PRACTICE ensures safe testing without real money impact
    async with AsyncClient(
        token="your-token",           # Your OANDA API token for authentication
        environment=Environment.PRACTICE  # Practice environment for safe testing
    ) as client:
        try:
            # Step 2: Retrieve current positions to analyze what needs closing
            # get_open_positions() returns only positions with non-zero units
            positions = await client.positions.get_open_positions(account_id)

            # Step 3: Find the specific position for the target instrument
            # Using next() with generator expression for efficient position lookup
            position = next((p for p in positions if p.instrument == instrument), None)

            if not position:
                # Step 4: Handle case where no position exists for this instrument
                print(f"Error: No open position for {instrument}")
                print(f"Note: Check if position was already closed or instrument symbol is correct")
                return None

            # Step 5: Extract position details for both long and short sides
            # OANDA represents long/short as separate unit counts
            # long.units: positive for long positions, "0" for no long position
            # short.units: negative for short positions, "0" for no short position
            long_units = int(position.long.units) if position.long.units != "0" else 0
            short_units = int(position.short.units) if position.short.units != "0" else 0

            if long_units == 0 and short_units == 0:
                # Step 6: Double-check for edge case of zero net position
                print(f"Error: No net position for {instrument}")
                print(f"Note: Position may have been closed between retrieval and processing")
                return None

            # Step 7: Calculate closing order parameters
            # Net position = long_units + short_units (short_units already negative)
            # To close: submit order in opposite direction with equal magnitude
            net_units = long_units + short_units  # Total net position (positive = long, negative = short)
            close_units = -net_units              # Opposite direction to close position

            print(f"Closing position for {instrument}:")
            print(f"   Long units: {long_units}")
            print(f"   Short units: {short_units}")
            print(f"   Net position: {net_units} units")
            print(f"   Closing with: {close_units} units")

            # Step 8: Submit market order to close position
            # Market orders execute immediately at current market price
            # Using opposite units ensures position closure
            response = await client.orders.post_market_order(
                account_id=account_id,    # Target trading account
                instrument=instrument,    # Currency pair to trade
                units=close_units        # Units to trade (negative of current position)
            )

            # Step 9: Process successful closure and extract transaction details
            if response.order_fill_transaction:
                # order_fill_transaction contains execution details when order fills
                fill = response.order_fill_transaction

                print(f"Position closed successfully!")
                print(f"   Close Price: {fill.price}")
                print(f"   Realized P/L: {fill.pl} {fill.account_currency}")
                print(f"   Transaction ID: {fill.id}")
                print(f"   Execution Time: {fill.time}")
                print(f"   Units Filled: {fill.units}")

                return fill
            else:
                # Step 10: Handle case where order was created but not filled
                print("Error: Order created but not filled immediately")
                print("Note: Check order status - may be pending or partially filled")
                return None

        except FiveTwentyError as e:
            # Step 11: Handle API-specific errors with detailed logging
            print(f"Error: OANDA API error closing position: {e.message}")
            print(f"   Error: code: {e.code}")
            print(f"Note: Common causes: insufficient margin, market closed, invalid instrument")
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
    """Close specific units of a position with comprehensive validation and error handling."""

    # Step 1: Initialize client connection for partial position management
    async with AsyncClient(
        token="your-token",           # OANDA API authentication token
        environment=Environment.PRACTICE  # Practice environment for safe testing
    ) as client:
        try:
            # Step 2: Retrieve and validate position existence
            # Critical to verify position exists before attempting partial closure
            positions = await client.positions.get_open_positions(account_id)
            position = next((p for p in positions if p.instrument == instrument), None)

            if not position:
                # Step 3: Handle non-existent position with descriptive error
                raise ValueError(f"No position found for {instrument}")
                # ValueError appropriate here as this indicates invalid input parameters

            # Step 4: Extract position details for validation logic
            # Need to handle both long and short positions separately
            # long.units: positive integer for long positions
            # short.units: negative integer for short positions (need abs() for comparison)
            long_units = int(position.long.units) if position.long.units != "0" else 0
            short_units = abs(int(position.short.units)) if position.short.units != "0" else 0

            print(f"Current position analysis for {instrument}:")
            print(f"   Long units: {long_units}")
            print(f"   Short units: {short_units}")
            print(f"   Requested closure: {units_to_close} units")

            # Step 5: Determine closure direction and validate sufficient units
            # Positive units_to_close = closing long position
            # Negative units_to_close = closing short position
            if units_to_close > 0:
                # Step 6: Closing long position - validate sufficient long units exist
                if units_to_close > long_units:
                    raise ValueError(
                        f"Cannot close {units_to_close} long units - only {long_units} long units available. "
                        f"Reduce units_to_close to maximum of {long_units}."
                    )
                close_units = -units_to_close  # Negative units to close long position
                print(f"   Operation: Closing {units_to_close} long units")

            else:
                # Step 7: Closing short position - validate sufficient short units exist
                units_to_close = abs(units_to_close)  # Convert to positive for comparison
                if units_to_close > short_units:
                    raise ValueError(
                        f"Cannot close {units_to_close} short units - only {short_units} short units available. "
                        f"Reduce units_to_close to maximum of {short_units}."
                    )
                close_units = units_to_close   # Positive units to close short position
                print(f"   Operation: Closing {units_to_close} short units")

            # Step 8: Execute partial closure with market order
            print(f"Executing partial closure: {abs(close_units)} units of {instrument}")
            print(f"   Market order units: {close_units}")

            response = await client.orders.post_market_order(
                account_id=account_id,    # Target trading account
                instrument=instrument,    # Currency pair to trade
                units=close_units        # Calculated units for partial closure
            )

            # Step 9: Process successful partial closure and provide detailed feedback
            if response.order_fill_transaction:
                fill = response.order_fill_transaction

                print(f"Partial position closed successfully!")
                print(f"   Units closed: {abs(close_units)}")
                print(f"   Close price: {fill.price}")
                print(f"   Realized P/L: {fill.pl} {fill.account_currency}")
                print(f"   Transaction ID: {fill.id}")
                print(f"   Remaining position: Check current positions for updated units")

                return fill
            else:
                # Step 10: Handle unfilled order scenario
                print(f"Error: Partial close order created but not filled")
                print(f"Note: Check order status and market conditions")
                return None

        except (FiveTwentyError, ValueError) as e:
            # Step 11: Comprehensive error handling for both API and validation errors
            print(f"Error: Partial close error: {e}")
            if isinstance(e, ValueError):
                print(f"Note: Validation error - check position size and units_to_close parameter")
            else:
                print(f"Note: API error - check network connection and account status")
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
        environment=Environment.PRACTICE  # Use PRACTICE for testing emergency procedures
    ) as client:
        try:
            # Step 2: Alert operators and begin emergency closure sequence
            print("⚠️ EMERGENCY CLOSE INITIATED: Closing all positions immediately!")
            print("⚠️ This will close ALL open positions - use with extreme caution")
            print("Note: Recommend logging this emergency event for post-incident analysis")

            # Step 3: Retrieve all open positions for emergency closure
            # get_open_positions() only returns positions with non-zero units
            positions = await client.positions.get_open_positions(account_id)

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
                if (int(position.long.units) != 0 or int(position.short.units) != 0):
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
        environment=Environment.PRACTICE  # Practice environment for testing verification
    ) as client:

        # Step 2: Retrieve current positions to verify closure
        # get_open_positions() only returns positions with non-zero units
        # If instrument not in results, position is definitely closed
        positions = await client.positions.get_open_positions(account_id)

        # Step 3: Search for the target instrument in open positions
        # Using next() with generator for efficient single-match lookup
        position = next((p for p in positions if p.instrument == instrument), None)

        # Step 4: Comprehensive position closure verification
        if position and (int(position.long.units) != 0 or int(position.short.units) != 0):
            # Step 5: Position still exists with non-zero units - closure failed
            print(f"⚠️ VERIFICATION FAILED: Position still open for {instrument}")
            print(f"   Current long units: {position.long.units}")
            print(f"   Current short units: {position.short.units}")
            print(f"   Net position: {int(position.long.units) + int(position.short.units)}")
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
