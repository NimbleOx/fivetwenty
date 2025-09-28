# Fragment Marking System

The FiveTwenty documentation validation system supports HTML comment markers to control validation behavior for specific code blocks. This allows authors to mark code fragments that are intentionally incomplete or contain placeholder values.

## Overview

Documentation authors can use invisible HTML comments before code blocks to control which validators should run. This is particularly useful for:

- **Example fragments** - Partial code examples that are not meant to be complete
- **Placeholder code** - Code blocks containing placeholder tokens like `your-api-token`
- **Tutorial snippets** - Step-by-step code that builds up over multiple blocks
- **Configuration examples** - Code showing configuration patterns with dummy values

## HTML Comment Syntax

Place HTML comments on the line immediately before the code block you want to mark:

```markdown
<!-- validation: skip -->
```python
# This code block will be skipped by all validators
print("Hello world")
undefined_variable = 123
```
```

## Available Markers

### Skip All Validation

These markers skip **both** linting and type checking:

```html
<!-- validation: skip -->
<!-- validation: skip-all -->
<!-- fragment: partial example -->
<!-- partial: configuration snippet -->
<!-- example: incomplete code -->
<!-- skip-lint -->
<!-- no-lint -->
```

### Skip Linting Only

These markers skip **only** linting but allow type checking:

```html
<!-- validation: skip-linting -->
<!-- skip-linting -->
<!-- no-linting -->
```

### Skip Type Checking Only

These markers skip **only** type checking but allow linting:

```html
<!-- validation: skip-typing -->
<!-- skip-typing -->
<!-- no-typing -->
```

## Examples

### Complete Skip Example

```markdown
This example shows a configuration fragment with placeholder values:

<!-- fragment: configuration with placeholders -->
```python
config = AccountConfig(
    token="your-api-token",        # Would trigger linting errors
    account_id="your-account-id",  # Would trigger type errors
    environment=Environment.PRACTICE,
)
```
```

### Linting Skip Example

```markdown
This example has imports in the middle (poor style) but correct types:

<!-- validation: skip-linting -->
```python
def trading_function():
    from fivetwenty import AsyncClient  # Import in function (bad style)
    return AsyncClient()
```
```

### Type Skip Example

```markdown
This example has good style but intentionally loose typing:

<!-- validation: skip-typing -->
```python
from fivetwenty import AsyncClient

def get_client():
    return AsyncClient()  # No return type annotation
```
```

## Best Practices

### When to Use Fragment Marking

✅ **Good use cases:**
- Tutorial steps that build incrementally
- Configuration examples with placeholder values
- Code fragments showing specific patterns
- Examples that are intentionally incomplete for pedagogical reasons

❌ **Avoid using for:**
- Working around validation errors in production examples
- Hiding real code quality issues
- Complete, runnable examples that should be valid

### Placement Guidelines

1. **Place comments immediately before code blocks** - No blank lines between comment and code
2. **Use descriptive fragment markers** - `<!-- fragment: user configuration example -->` is better than `<!-- skip -->`
3. **Be consistent** - Use the same marker patterns throughout your documentation
4. **Document your usage** - When using many fragment markers, consider adding a note explaining why

### Marker Selection

- Use `<!-- validation: skip -->` for clear, explicit skipping
- Use `<!-- fragment: description -->` for educational examples
- Use specific markers (`skip-linting`, `skip-typing`) when you only need to skip one validator
- Be descriptive in fragment descriptions to help future maintainers

## Implementation Details

### Detection Range

The validation system checks **up to 3 lines before** each code block for HTML comments. This allows for:

```markdown
Some explanatory text.

<!-- fragment: example -->
```python
code_here()
```
```

### Case Insensitive

All marker detection is case-insensitive:

```html
<!-- VALIDATION: SKIP -->  ✅ Works
<!-- validation: skip -->  ✅ Works
<!-- Validation: Skip -->  ✅ Works
```

### Pattern Matching

The system looks for specific patterns within HTML comments. Partial matches work:

```html
<!-- This is a fragment: partial example for configuration -->  ✅ Matches "fragment:"
<!-- Please skip-linting this code block -->                   ✅ Matches "skip-linting"
```

## Troubleshooting

### Common Issues

**Comment not detected:**
- Ensure the HTML comment is within 3 lines before the code block
- Check that you're using a supported marker pattern
- Verify there are no typos in the comment

**Wrong validator skipped:**
- Double-check you're using the right marker (`skip-linting` vs `skip-typing`)
- Remember that `validation: skip` skips ALL validators

**Still getting validation errors:**
- The HTML comment may apply to a different code block than expected
- Check line numbers in validation errors to identify which code block is failing
- Consider using the `--files` option to test specific files

### Testing Your Markers

Use the validation CLI to test specific files:

```bash
# Test a specific file
uv run python -m docs_validation.src.cli validate --files "path/to/your/file.md"

# Use fast validation for quicker testing
uv run python -m docs_validation.src.cli validate --config docs_validation/config/validation-fast.yml --files "path/to/your/file.md"
```

## Migration from Inline Comments

If you have existing code with inline `# type: ignore` or similar comments, consider moving to HTML fragment markers:

**Before:**
```python
token = get_token()  # type: ignore
```

**After:**
```markdown
<!-- skip-typing: token retrieval example -->
```python
token = get_token()
```
```

This keeps the documentation clean while providing better control over validation behavior.