# Documentation Code Blocks Review Plan

## Objective
Review code blocks in documentation pages (guides, tutorials, examples) outside of API reference

## Code Block Extraction Directory
`/Users/antares/dev/fivetwenty-tutorial/documentation-examples/`

Each page gets its own directory, with one file per code block.

## Naming Convention
Add markdown comment before each code block with unique name:

<!-- code-block: unique_descriptive_name -->
```python
...code...
```

Save code block as:
- `docs/getting-started.md` → `getting-started/first_trade.py`
- `docs/guides/streaming.md` → `guides-streaming/price_stream.py`

## Process

1. **Name**: Add `<!-- code-block: unique_name -->` before each ````python` block
2. **Extract**: Save code blocks as `<page-path>/<unique_name>.py` with header:
   ```python
   # Source: docs/getting-started.md
   # Name: first_trade
   ```
3. **Test**: Run `uv run python <file>` to verify execution
4. **Lint**: Run `ruff format --check`, `ruff check`, `mypy --strict`
   - Note: Use the linting and typing ignore rules from `docs_validation/config/validation-complete.yml`
5. **Review Code Quality**:
   - Zero-config AsyncClient pattern, including use of python-dotenv
   - No emojis in code blocks
   - Comments should explain what is being done, not restate signatures:
     - NO comments on boilerplate (imports, asyncio.run, load_dotenv)
     - NO comments on self-explanatory code (print statements)
     - YES comments on SDK API calls explaining what they do
     - YES comments on code building up to API calls (parameter preparation, etc.)
     - YES comments before any lines indicating that the value should be changed by the user (account id, order id, etc.)
     - Focus on "why" and "what" not "how" (which is obvious from the code)
   - Use async/await patterns correctly
   - Proper error handling with FiveTwentyError where appropriate
   - Type hints on all function definitions
7. **Fix**: Update documentation code blocks to pass all checks
8. **Pause**: Wait for user validation
9. **Commit**: Single-line commit message for that page, which the user must approve
