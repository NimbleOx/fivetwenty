# Documentation Code Block Enhancement Plan

This document outlines the systematic process for enhancing code blocks in FiveTwenty documentation to ensure they are complete, executable, and tutorial-quality.

## Phase 1: Discovery & Analysis

1. **Read the documentation page** - Understand the page's purpose and learning goals
2. **Identify all code blocks** - Note line numbers and current state of each block
3. **Check introductory text** - Verify each code block has at least one full paragraph of context explaining:
   - What the code demonstrates
   - Why it's important/useful
   - How it fits into the broader topic

More than one paragraph is fine if the topic merits it.

## Phase 2: Code Enhancement (Per Block)

For each code block:

4. **Extract to main.py** - Copy code to tutorial project for testing
5. **Ensure completeness**:
   - Add missing imports (`asyncio`, `Decimal`, etc.)
   - Add `load_dotenv()` if using `AsyncClient`
   - Add `async def main()` wrapper if needed
   - Add `if __name__ == "__main__": asyncio.run(main())`
   - Ensure it uses SDK for API operations (not hardcoded values)
6. **Review SDK usage** - Verify the code demonstrates proper SDK usage:
   - Uses `AsyncClient()` context manager for resource management
   - Calls appropriate SDK methods (e.g., `client.trades.get_trades()`, `client.pricing.get_pricing()`)
   - Handles TypedDict responses correctly (dictionary access with `["key"]`)
   - Accesses Pydantic model fields correctly (attribute access with `.field`)
   - Uses Pydantic models for request data (e.g., `StopLossDetails`, `TakeProfitDetails`)
   - Serializes Pydantic models with `.model_dump(by_alias=True, exclude_none=True)` when needed
   - Includes proper error handling with `FiveTwentyError` exceptions
   - Uses `Decimal` type for all financial values (never `float`)
7. **Add tutorial comments** following the established style guide:

   **Comment Style Guide:**

   a. **Section Headers** - Use 78-character separator style:
   ```python
   # ==============================================================================
   # SECTION TITLE
   # ==============================================================================
   ```

   b. **Environment Setup** - Always at the top with explanation:
   ```python
   # ==============================================================================
   # ENVIRONMENT SETUP
   # ==============================================================================

   # Load API credentials from .env file
   # The AsyncClient automatically reads these environment variables:
   #   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
   #   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
   #   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
   load_dotenv()
   ```

   c. **Step Markers** - Use full separator for major steps:
   ```python
   # ==============================================================================
   # STEP 1: RETRIEVE OPEN TRADES
   # ==============================================================================
   ```

   d. **SDK Method Documentation** - Document BEFORE the method call:
   ```python
   # The SDK method: client.trades.get_trades()
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
   trades = response["trades"]
   ```

   e. **Inline Explanations** - Clarify important lines:
   ```python
   entry_price = trade.price  # Already a Decimal from SDK (no conversion needed)
   is_long = int(trade.current_units) > 0  # Positive units = long, negative = short
   ```

   f. **Strategy/Concept Explanations** - Use multi-line format with use cases:
   ```python
   # ==============================================================================
   # STRATEGY 1: FIXED PIP STOP
   # ==============================================================================
   # Simple and predictable - risk a fixed number of pips regardless of market conditions
   #
   # Use case: Systematic strategies that require consistent risk per trade
   # Pros: Easy to calculate, predictable risk, simple to backtest
   # Cons: Doesn't adapt to volatility or market structure
   ```

   g. **Connection to Client** - Explain AsyncClient context manager:
   ```python
   # ==============================================================================
   # CONNECT TO OANDA
   # ==============================================================================

   # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
   # Context manager ensures proper cleanup of HTTP connections
   async with AsyncClient() as client:
   ```

   h. **Docstrings** - Keep them concise (1 line for simple functions):
   ```python
   async def update_prices(self, client: AsyncClient) -> bool:
       """Fetch latest price and add to price history."""
   ```

   **What to Include:**
   - Explain what SDK methods do and their parameters
   - Note return types (TypedDict vs Pydantic models)
   - Add step-by-step guidance with clear markers
   - Explain financial/trading concepts
   - Clarify important calculations with inline comments

   **What to Avoid:**
   - Overly verbose docstrings for straightforward methods
   - Redundant comments that just restate the code
   - SDK documentation inside class methods (put it before the call in main logic)

## Phase 3: Validation (Per Block)

8. **Type check** - `uv run mypy main.py` (must pass)
9. **Lint** - `uv run ruff check main.py` (must pass)
10. **Execute** - `uv run python main.py` (must run without errors, handle API restrictions gracefully)

## Phase 4: Integration

11. **Update documentation** - Replace code block with enhanced version
12. **Verify paragraph context** - Add or improve introductory paragraphs if needed
13. **Save standalone file** - Save the enhanced code block to `/Users/antares/dev/fivetwenty-tutorial/` with descriptive name (e.g., `example_stop_loss_strategies.py`, `example_take_profit.py`) so user can execute it independently
14. **Request user validation** - **STOP and ask user to confirm** the code block is correct before proceeding
15. **Move to next block** - After user confirmation, repeat Phase 2-4 for next code block

## Phase 5: Final Verification

16. **Review entire page** - Ensure flow and consistency
17. **Run documentation validation** - Verify with docs validation system if applicable

## Success Criteria

- ✅ Every code block is executable standalone
- ✅ All code passes mypy strict type checking
- ✅ All code passes ruff linting
- ✅ Every code block has contextual paragraph(s) before it
- ✅ Tutorial-quality comments throughout
- ✅ Uses SDK properly (no hardcoded mock data)
- ✅ Includes python-dotenv for environment setup

## Example Usage

```bash
# 1. Identify target page
TARGET_PAGE="docs/tutorials/basic-trading/position-management.md"

# 2. Work through each code block iteratively
cd /Users/antares/dev/fivetwenty-tutorial

# 3. For each code block:
#    - Extract to main.py
#    - Enhance with imports, dotenv, comments
#    - Test: uv run mypy main.py && uv run ruff check main.py && uv run python main.py
#    - Update documentation with enhanced version

# 4. Verify final page quality
cd /Users/antares/dev/fivetwenty
poe docs-validate-fast  # Run documentation validation
```

## Tips

- Focus on one code block at a time - don't try to do them all at once
- Test execution is critical - code must actually work
- Error handling is important - use try/except for OANDA restrictions
- Comments should teach, not just describe - explain the "why"
- Keep examples simple and focused on core concepts

## IMPORTANT! PAUSE AFTER EACH CODE BLOCK SO THE USER CAN VERIFY!
