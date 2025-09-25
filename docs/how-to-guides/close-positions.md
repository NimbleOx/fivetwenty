# How to Close Positions

!!! info "🔧 How-to Guide - Problem-solving content"
    **Use this guide when:** You have existing positions and need to close them efficiently

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

```python
import asyncio
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

async def close_position(account_id: str, instrument: str):
    """Close all positions for a specific instrument."""

    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Check current position
            positions = await client.positions.get_open_positions(account_id)
            position = next((p for p in positions if p.instrument == instrument), None)

            if not position:
                print(f"❌ No open position for {instrument}")
                return None

            # Calculate total units to close
            long_units = int(position.long.units) if position.long.units != "0" else 0
            short_units = int(position.short.units) if position.short.units != "0" else 0

            if long_units == 0 and short_units == 0:
                print(f"❌ No net position for {instrument}")
                return None

            # Close position with market order
            net_units = long_units + short_units  # short_units is already negative
            close_units = -net_units  # Opposite direction to close

            print(f"🔄 Closing position for {instrument}:")
            print(f"   Current position: {net_units} units")
            print(f"   Closing with: {close_units} units")

            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=close_units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Position closed!")
                print(f"   Close Price: {fill.price}")
                print(f"   Realized P/L: {fill.pl}")
                print(f"   Time: {fill.time}")

                return fill
            else:
                print("❌ Failed to close position")
                return None

        except FiveTwentyError as e:
            print(f"❌ Error closing position: {e.message}")
            return None

# Usage
account_id = "your-account-id"
close_result = await close_position(account_id, "EUR_USD")
```

---

## Partial Close: Specific Units

Close only part of a position:

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def close_partial_position(account_id: str, instrument: str, units_to_close: int):
    """Close specific units of a position."""

    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        try:
            # Validate position exists and has sufficient units
            positions = await client.positions.get_open_positions(account_id)
            position = next((p for p in positions if p.instrument == instrument), None)

            if not position:
                raise ValueError(f"No position found for {instrument}")

            # Check direction and available units
            long_units = int(position.long.units) if position.long.units != "0" else 0
            short_units = abs(int(position.short.units)) if position.short.units != "0" else 0

            if units_to_close > 0:  # Closing long position
                if units_to_close > long_units:
                    raise ValueError(f"Cannot close {units_to_close} units, only {long_units} long units available")
                close_units = -units_to_close
            else:  # Closing short position
                units_to_close = abs(units_to_close)
                if units_to_close > short_units:
                    raise ValueError(f"Cannot close {units_to_close} units, only {short_units} short units available")
                close_units = units_to_close

            print(f"🔄 Partially closing {abs(close_units)} units of {instrument}")

            response = await client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=close_units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Partial position closed!")
                print(f"   Units closed: {abs(close_units)}")
                print(f"   Close price: {fill.price}")
                print(f"   Realized P/L: {fill.pl}")
                return fill

        except (FiveTwentyError, ValueError) as e:
            print(f"❌ Error: {e}")
            return None

# Usage - close 500 units of long EUR_USD
result = await close_partial_position(account_id, "EUR_USD", 500)
```

---

## Batch Close: Multiple Instruments

Close positions across multiple instruments:

```python
from fivetwenty import AsyncClient, Environment

async def close_multiple_positions(account_id: str, instruments: list):
    """Close positions for multiple instruments."""

    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        results = {}

        for instrument in instruments:
            try:
                print(f"\n🔄 Processing {instrument}...")
                result = await close_position(account_id, instrument)
                results[instrument] = result

                # Small delay to avoid rate limiting
                await asyncio.sleep(0.1)

            except Exception as e:
                print(f"❌ Failed to close {instrument}: {e}")
                results[instrument] = None

        # Summary
        successful_closes = sum(1 for r in results.values() if r is not None)
        print(f"\n📊 Summary: {successful_closes}/{len(instruments)} positions closed")

        return results

# Usage
instruments_to_close = ["EUR_USD", "GBP_USD", "USD_JPY"]
close_results = await close_multiple_positions(account_id, instruments_to_close)
```

---

## Emergency Close: All Positions

Close all open positions immediately:

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def emergency_close_all(account_id: str):
    """Emergency close all open positions."""

    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        try:
            print("🚨 EMERGENCY CLOSE: Closing all positions...")

            # Get all open positions
            positions = await client.positions.get_open_positions(account_id)

            if not positions:
                print("✅ No open positions to close")
                return []

            close_tasks = []
            for position in positions:
                if (int(position.long.units) != 0 or int(position.short.units) != 0):
                    task = close_position(account_id, position.instrument)
                    close_tasks.append(task)

            # Execute all closes concurrently
            results = await asyncio.gather(*close_tasks, return_exceptions=True)

            successful_closes = sum(1 for r in results if r is not None and not isinstance(r, Exception))
            print(f"🚨 Emergency close complete: {successful_closes}/{len(close_tasks)} positions closed")

            return results

        except FiveTwentyError as e:
            print(f"❌ Emergency close failed: {e.message}")
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

## Success Verification

After closing positions, verify the operation:

```python
from fivetwenty import AsyncClient, Environment

async def verify_position_closed(account_id: str, instrument: str):
    """Verify a position was successfully closed."""

    async with AsyncClient(
        token="your-token",
        environment=Environment.PRACTICE
    ) as client:
        positions = await client.positions.get_open_positions(account_id)
        position = next((p for p in positions if p.instrument == instrument), None)

        if position and (int(position.long.units) != 0 or int(position.short.units) != 0):
            print(f"⚠️ Position still open for {instrument}")
            return False
        else:
            print(f"✅ Position confirmed closed for {instrument}")
            return True

# Verify closure
is_closed = await verify_position_closed(account_id, "EUR_USD")
```

**Task Complete**: Position closing operations are now available as dedicated, problem-focused how-to guides.