# API Endpoint Documentation Review Plan
## Objective
Review API reference pages, including code blocks

## Code Block Extraction Directory
`/Users/antares/dev/fivetwenty-tutorial/api-reference-examples-endpoints/`

Each page gets its own directory, with one file per code block.

## Naming Convention
Add markdown comment before each code block with unique name that includes a prefix of the filename:

<!-- code-block: get_account_summary -->
```python
...code...
```

Save as:
- `docs/api-reference/endpoints/orders.md` → `orders/post_market_order.py`

## Process

1. **Name**: Add `<!-- code-block: unique_name -->` before each ````python` block
2. **Extract**: Save code blocks as `<page>/<unique_name>.py` with header:
   ```python
   # Source: docs/api-reference/endpoints/orders.md
   # Name: post_market_order
   ```
3. **Test**: Run `uv run python <file>` to verify execution
4. **Lint**: Run `ruff format --check`, `ruff check`, `mypy --strict`
5. **Review Code**:
   - Zero-config AsyncClient pattern, including use of python-dotenv
   - No emojis in code blocks
   - Explanatory, concise comments

6. **Fix**: Update documentation code blocks to pass all checks
7. **Review and Fix documentation**
   - Link to OANDA documentation (🔗 prefix on link line only, NOT on endpoint line)
   - Link to GitHub page for the pertinent element (🔗 prefix on link)
     - Use correct organization: `https://github.com/NimbleOx/fivetwenty/...`
   - List the endpoint in this format: `**OANDA Endpoint**: GET /v3/...` (no emoji on endpoint line)
   - Section order:
     1. Title (e.g., `## get_account_summary`)
     2. 1 Paragraph Summary of endpoint purpose
     3. OANDA Endpoint specification
     4. Code Block (with `<!-- code-block: name -->` comment)
     5. OANDA Documentation Link
     6. FiveTwenty SDK Link
     7. Parameters table
     8. Returns (as TypedDict definition)
     9. Raises (as bulleted list of exceptions)
7. **Pause**: Wait for user validation
8. **Commit**: Single-line commit message for that page, which the user must approve
