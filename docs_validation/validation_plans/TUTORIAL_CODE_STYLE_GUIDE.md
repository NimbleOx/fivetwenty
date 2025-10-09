# Tutorial Code Block Style Guide

## Core Requirements

All code examples must be:
- **Executable** - Run as-is with proper environment setup
- **Complete** - Include all imports and structure
- **Professional** - No emojis anywhere (code, comments, documentation)

## Standard Structure

```python
import asyncio
from fivetwenty import AsyncClient


async def main() -> None:
    async with AsyncClient() as client:
        # Your code here
        pass

asyncio.run(main())
```

## Comment Standards

### Section Headers (78 characters)
```python
# ==============================================================================
# SECTION TITLE
# ==============================================================================
```

### SDK Method Documentation
```python
# ==============================================================================
# SDK METHOD: client.trades.get_trades()
# ==============================================================================
#
# Parameters:
#   - account_id: Your OANDA account ID (available as client.account_id)
#
# Returns: TypedDict with structure:
#   {
#       "trades": list[Trade],        # List of Pydantic Trade models
#       "lastTransactionID": str
#   }
#
# NOTE: Response is a TypedDict (use dictionary access: response["trades"])
#       Each Trade is a Pydantic model (use attribute access: trade.price)

response = await client.trades.get_trades(client.account_id)
```

**Concise format for simple methods:**
```python
# client.accounts.get_account_summary(account_id: AccountID) -> AccountSummaryResponse
# Returns: {"account": AccountSummary, "lastTransactionID": str}

result = await client.accounts.get_account_summary(account_id=client.account_id)
```

### Comment Guidelines

**DO:**
- Explain "why" not "what"
- Document SDK method signatures and return types
- Clarify TypedDict vs Pydantic model access
- Use 78-character separators for sections
- Add warnings for non-obvious behavior

**DON'T:**
- Use emojis in comments
- State the obvious
- Use informal language
- Leave commented-out code

## Key Patterns

### Zero-Config (Always Preferred)
```python
# AsyncClient reads from environment variables:
# - FIVETWENTY_OANDA_TOKEN
# - FIVETWENTY_OANDA_ACCOUNT
# - FIVETWENTY_OANDA_ENVIRONMENT (optional, defaults to practice)

async with AsyncClient() as client:
    result = await client.accounts.get_account_summary(
        account_id=client.account_id  # Use client.account_id, not hardcoded
    )
```

### Show Return Value Usage
```python
result = await client.orders.post_market_order(
    account_id=client.account_id,
    instrument="EUR_USD",
    units=1000,
)

# Always demonstrate what to do with the result
if "orderFillTransaction" in result:
    fill = result["orderFillTransaction"]
    print(f"Order filled at {fill.price}")
```

### Error Handling
```python
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

try:
    result = await client.orders.post_market_order(...)
except FiveTwentyError as e:
    # Use properties for error checking
    if e.is_rate_limited:
        print(f"Rate limited - retry after {e.retry_after}s")
    # Use .value for enum comparisons
    elif e.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS.value:
        print("Not enough margin")
```

## Anti-Patterns

❌ **Incomplete examples** - Missing imports, async structure, or result usage
❌ **Hardcoded IDs** - Use `client.account_id` not `"123-456-789"`
❌ **Emojis** - Never use emojis anywhere
❌ **String literals** - Use enums: `CandlestickGranularity.H1` not `"H1"`
❌ **Wrong enum comparison** - Use `e.code == ErrorCode.FOO.value` not `ErrorCode.FOO`

## Checklist

- [ ] All imports present and necessary
- [ ] Uses `async def main() -> None:`
- [ ] Uses `async with AsyncClient() as client:`
- [ ] Uses `client.account_id` not hardcoded IDs
- [ ] Ends with `asyncio.run(main())`
- [ ] Demonstrates using return values
- [ ] No emojis anywhere
- [ ] Helpful comments with 78-char separators
- [ ] Proper enum usage
- [ ] Code is executable and tested
