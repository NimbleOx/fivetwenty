# Documentation Code Block Enhancement Plan

This document outlines the systematic process for enhancing code blocks in FiveTwenty documentation to ensure they are complete, executable, and tutorial-quality.

## ⚠️ CRITICAL: One Code Block at a Time

**PROCESS ONE CODE BLOCK AT A TIME. PAUSE AFTER EACH FOR USER VALIDATION.**

Do not proceed to the next code block until the user has explicitly validated the current one. This ensures quality and allows for corrections before moving forward.

## Directory Structure

**Tutorial Working Directory:** `/Users/antares/dev/fivetwenty-tutorial/`
- Used for developing and testing code blocks
- Contains `main.py` as temporary working file for validation
- Contains `.env` with OANDA credentials
- Final home for validated example files
- Each code block gets its own uniquely named file
- Files follow naming convention: `example_{descriptive_name}.py`

**Naming Convention Examples:**
- `example_stop_loss_strategies.py` - Stop loss placement strategies
- `example_volatility_adjusted_trailing.py` - ATR-based trailing stops
- `example_scale_in_strategy.py` - Position scaling implementation
- `example_market_adaptive.py` - Market condition adaptation
- `example_risk_management.py` - Risk-based position sizing

## Phase 1: Discovery & Analysis

1. **Read the documentation page** - Understand the page's purpose and learning goals
2. **Identify all code blocks** - Note line numbers and current state of each block
3. **Check introductory text** - Verify each code block has at least one full paragraph of context explaining:
   - What the code demonstrates
   - Why it's important/useful
   - How it fits into the broader topic

   (Multiple paragraphs are fine if the topic merits it)

## Phase 2: Code Enhancement (Current Block Only)

**⚠️ WORK ON ONE CODE BLOCK AT A TIME - DO NOT BATCH PROCESS**

4. **Ensure completeness**:
   - Add missing imports (`asyncio`, `Decimal`, etc.)
   - Add `load_dotenv()` at the top (without verbose environment setup comments)
   - Add `async def main()` wrapper if needed
   - Ensure it uses SDK for API operations (not hardcoded values)

5. **Review SDK usage** - Verify the code demonstrates proper SDK usage:
   - Uses `AsyncClient()` context manager for resource management
   - Calls appropriate SDK methods (e.g., `client.trades.get_trades()`, `client.pricing.get_pricing()`)
   - Handles TypedDict responses correctly (dictionary access with `["key"]`)
   - Accesses Pydantic model fields correctly (attribute access with `.field`)
   - Uses Pydantic models for request data (e.g., `StopLossDetails`, `TakeProfitDetails`)
   - Serializes Pydantic models with `.model_dump(by_alias=True, exclude_none=True)` when needed
   - Includes proper error handling with `FiveTwentyError` exceptions
   - Uses `Decimal` type for all financial values (never `float`)
   - Doesn't use `Decimal(str())` on values that were decimal to begin with

6. **Add tutorial comments** following the established style guide:

   **Comment Style Guide:**

   a. **Section Headers** - Use 78-character separator style:
   ```python
   # ==============================================================================
   # SECTION TITLE
   # ==============================================================================
   ```

   b. **Step Markers** - Use full separator for major steps:
   ```python
   # ==============================================================================
   # STEP 1: RETRIEVE OPEN TRADES
   # ==============================================================================
   ```

   c. **SDK Method Documentation** - Document BEFORE the method call:
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

   d. **Inline Explanations** - Clarify important lines:
   ```python
   entry_price = trade.price  # Already a Decimal from SDK (no conversion needed)
   is_long = int(trade.current_units) > 0  # Positive units = long, negative = short
   ```

   e. **Strategy/Concept Explanations** - Use multi-line format with use cases:
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

   f. **Connection to Client** - Explain AsyncClient context manager:
   ```python
   # ==============================================================================
   # CONNECT TO OANDA
   # ==============================================================================

   # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
   # Context manager ensures proper cleanup of HTTP connections
   async with AsyncClient() as client:
   ```

   g. **Docstrings** - Keep them concise

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
   - Emojis in code, comments, or output (use plain text only)

## Phase 3: Validation (Current Block Only)

7. **Type check** - `uv run mypy main.py` (must pass strict type checking)
8. **Lint** - `uv run ruff check main.py` (must pass)
9. **Execute** - `uv run python main.py` (must run without errors, handle API restrictions gracefully)

## Phase 4: Integration (Current Block Only)

10. **Save to tutorial directory** - Write enhanced code to `/Users/antares/dev/fivetwenty-tutorial/main.py`
    - This temporary file is used for validation with mypy and execution

11. **Copy to example file** - After validation passes, copy to `/Users/antares/dev/fivetwenty/docs/tutorials/{topic}/example_{descriptive_name}.py`
    - Choose a unique, descriptive name that clearly identifies what the code demonstrates
    - Each code block must have its own uniquely named file

12. **Update documentation** - Replace code block with enhanced version and add filepath comment:
    ```markdown
    <!-- filepath: docs/tutorials/{topic}/example_{name}.py -->
    ```python
    # Enhanced code here...
    ```
    ```

13. **Verify paragraph context** - Add or improve introductory paragraphs if needed

## 🛑 MANDATORY PAUSE FOR USER VALIDATION

14. **STOP HERE** - Present the completed code block to the user and wait for explicit confirmation:
    - Show what file was created
    - Summarize what the code demonstrates
    - **DO NOT proceed to the next code block until user confirms**

15. **After user approval** - Move to the next code block and repeat Phases 2-4

## Phase 5: Final Verification (After All Blocks Complete)

16. **Review entire page** - Ensure flow and consistency across all enhanced code blocks
17. **Run documentation validation** - Verify with docs validation system if applicable

## Success Criteria

- ✅ Every code block is executable standalone
- ✅ All code passes mypy strict type checking
- ✅ All code passes ruff linting
- ✅ Every code block has contextual paragraph(s) before it
- ✅ Tutorial-quality comments throughout
- ✅ Uses SDK properly (no hardcoded mock data)
- ✅ Includes python-dotenv for environment setup
- ✅ Each code block saved as uniquely named example file

## Example Workflow - Single Code Block

**This workflow is for ONE code block. Complete all steps, then STOP for user validation.**

```bash
# ============================================================================
# WORKFLOW FOR CODE BLOCK #1 (Example)
# ============================================================================

# 1. Navigate to tutorial directory
cd /Users/antares/dev/fivetwenty-tutorial

# 2. Write enhanced code to main.py
# (Write complete, executable code following all guidelines)

# 3. Validate the code
uv run mypy main.py        # Must pass strict type checking
uv run ruff check main.py  # Must pass linting
uv run python main.py      # Must execute without errors

# 4. Copy to final example location with unique name
cp main.py /Users/antares/dev/fivetwenty/docs/tutorials/basic-trading/example_stop_loss_strategies.py

# 5. Update documentation with filepath comment
# Add: <!-- filepath: docs/tutorials/basic-trading/example_stop_loss_strategies.py -->

# 🛑 STOP HERE - Present to user for validation

# ============================================================================
# AFTER USER APPROVES: WORKFLOW FOR CODE BLOCK #2 (Example)
# ============================================================================

# 1. Write enhanced code for NEXT block to main.py
# (Overwrite previous code)

# 2. Validate again
uv run mypy main.py
uv run ruff check main.py
uv run python main.py

# 3. Copy with DIFFERENT unique name
cp main.py /Users/antares/dev/fivetwenty/docs/tutorials/basic-trading/example_take_profit_strategies.py

# 4. Update documentation for this block

# 🛑 STOP HERE - Present to user for validation

# Continue this pattern for each code block...
```

## Best Practices

- **ONE CODE BLOCK AT A TIME** - Never process multiple code blocks without user validation between them
- **PAUSE FOR VALIDATION** - Always stop and present the completed code to the user before moving to the next block
- **Test execution is critical** - Code must actually work, not just pass type checking
- **Error handling is important** - Use try/except for OANDA restrictions (market hours, etc.)
- **Comments should teach** - Explain the "why", not just the "what"
- **Keep examples focused** - Each code block should demonstrate one clear concept
- **Unique filenames** - Every code block gets its own distinctly named example file

## ⚠️ CRITICAL REMINDER

**WORK ON ONE CODE BLOCK AT A TIME.**

**PAUSE AFTER EACH CODE BLOCK FOR USER VALIDATION.**

**DO NOT PROCEED TO THE NEXT CODE BLOCK WITHOUT EXPLICIT USER APPROVAL.**

This iterative approach ensures quality, allows for corrections, and prevents wasted effort on code blocks that might need different approaches based on earlier feedback.
