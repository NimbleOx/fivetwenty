# FiveTwenty Documentation Validation Patterns

This document captures the validation patterns discovered during comprehensive documentation analysis of the FiveTwenty SDK.

## Critical Financial Precision Patterns

### Pattern 1: Float Literal in Financial Context
**Problem Pattern:**
```python
# BAD - Float literal for financial value
stop_loss=1.0900
take_profit=1.1100
daily_loss_limit=200.0
```

**Solution Pattern:**
```python
# GOOD - Decimal string for financial precision
stop_loss=Decimal("1.0900")
take_profit=Decimal("1.1100")
daily_loss_limit=Decimal("200.0")
```

**Detection Regex:** `(price|amount|balance|stop_loss|take_profit|daily_loss_limit|spread|margin)\s*=\s*\d+\.\d+`

### Pattern 2: Float Arithmetic in Financial Calculations
**Problem Pattern:**
```python
# BAD - Float arithmetic for position sizing
units = int(base_units * 0.5)
max_position = int(account_balance * 0.1 / pip_value)
```

**Solution Pattern:**
```python
# GOOD - Decimal arithmetic for precision
units = int(base_units * Decimal("0.5"))
max_position = int(account_balance * Decimal("0.1") / pip_value)
```

**Detection Regex:** `\*\s*\d+\.\d+|\d+\.\d+\s*\*`

## Import Validation Patterns

### Pattern 3: Missing Decimal Import
**Problem Pattern:**
```python
# Code block using Decimal without import
price = Decimal("1.1234")  # ← Will fail to execute
```

**Solution Pattern:**
```python
from decimal import Decimal

price = Decimal("1.1234")  # ← Now executable
```

**Detection:** AST parsing to find Decimal usage without corresponding import statement.

### Pattern 4: Missing AsyncClient Import
**Problem Pattern:**
```python
# Code block using AsyncClient without import
async with AsyncClient(...) as client:  # ← Will fail
```

**Solution Pattern:**
```python
from fivetwenty import AsyncClient, Environment

async with AsyncClient(...) as client:  # ← Now executable
```

## Markdown Structure Patterns

### Pattern 5: Indented Code in Admonitions
**Problem Pattern:**
```markdown
!!! tip "Trading Pattern"
    ```python
    # This indentation confuses code extraction
    await client.orders.post_market_order(...)
    ```
```

**Solution:** Special handling for code blocks within markdown admonitions that maintain indentation.

### Pattern 6: Cross-Reference Validation
**Problem Pattern:**
```markdown
See [Trading Guide](../non-existent-file.md)
```

**Solution Pattern:**
```markdown
See [Trading Guide](../how-to-guides/manage-orders-effectively.md)
```

**Detection:** Path resolution validation for relative links.

## Error Code Accuracy Patterns

### Pattern 7: Deprecated Error Code Usage
**Problem Pattern:**
```python
from fivetwenty.exceptions import ErrorCode  # ← Wrong class name

if e.code == ErrorCode.INSUFFICIENT_FUNDS:  # ← Will fail
```

**Solution Pattern:**
```python
from fivetwenty.exceptions import FiveTwentyErrorCode  # ← Correct class

if e.code == FiveTwentyErrorCode.INSUFFICIENT_FUNDS:  # ← Will work
```

### Pattern 8: Placeholder Function Detection
**Problem Pattern:**
```python
async def handle_error():
    await refresh_token()  # ← Undefined function
    notify_operations_team()  # ← Undefined function
```

**Solution Pattern:**
```python
async def handle_error():
    # Implementation needed: token refresh logic
    # Implementation needed: notification logic
```

## Forex Trading Specific Patterns

### Pattern 9: Insufficient Forex Precision
**Problem Pattern:**
```python
daily_loss_limit = "1000.0"  # Only 1 decimal place
```

**Solution Pattern:**
```python
daily_loss_limit = "1000.0000"  # 4+ decimal places for EUR_USD
```

### Pattern 10: Unrealistic Forex Values
**Problem Pattern:**
```python
eur_usd_price = Decimal("5.0000")  # Unrealistic - EUR/USD ~1.0-1.5
```

**Solution Pattern:**
```python
eur_usd_price = Decimal("1.1234")  # Realistic EUR/USD price
```

**Detection Ranges:**
- EUR_USD: 0.8 - 1.5
- GBP_USD: 1.0 - 2.0
- USD_JPY: 80 - 150

## Async Pattern Validation

### Pattern 11: Missing Await Keywords
**Problem Pattern:**
```python
async def place_order():
    response = client.orders.post_market_order(...)  # ← Missing await
```

**Solution Pattern:**
```python
async def place_order():
    response = await client.orders.post_market_order(...)  # ← Correct
```

## Validation Priority Framework

### Critical Priority (Fix Immediately)
1. Financial precision errors (float literals in trading)
2. Missing imports that prevent code execution
3. Incorrect error code class references

### High Priority (Fix Before Release)
4. Unrealistic financial values
5. Missing await keywords in async code
6. Placeholder functions in examples

### Medium Priority (Fix for Quality)
7. Cross-reference validation
8. Forex precision consistency
9. Code style and formatting

### Low Priority (Enhancement)
10. Documentation completeness
11. Visual consistency
12. Performance optimizations

## Validation Metrics

### Success Criteria
- **Code Examples**: 100% syntactically correct and executable
- **Financial Precision**: 100% Decimal usage for trading calculations
- **Import Accuracy**: 100% complete imports for all dependencies
- **Cross-References**: 95%+ valid internal links
- **Error Handling**: 100% correct error code usage

### Quality Gates
- **Critical Issues**: 0 tolerance (blocks release)
- **High Priority Issues**: <5 allowed
- **Medium Priority Issues**: <20 allowed
- **Low Priority Issues**: Tracked but non-blocking

## Automated Detection Implementation

### Regex Patterns for Financial Issues
```python
FINANCIAL_FLOAT_PATTERNS = [
    r'(price|amount|balance|units|margin|spread)\s*=\s*\d+\.\d+',
    r'\*\s*\d+\.\d+|\d+\.\d+\s*\*',
    r'float\(\s*[\d.]+\s*\)',
]

MISSING_IMPORT_PATTERNS = [
    r'Decimal\(' => 'from decimal import Decimal',
    r'AsyncClient\(' => 'from fivetwenty import AsyncClient',
    r'Environment\.' => 'from fivetwenty import Environment',
]
```

### AST Analysis for Code Structure
```python
def validate_code_block(code):
    """Validate Python code block for common issues."""
    tree = ast.parse(code)

    # Check for Decimal usage without import
    # Check for async methods without await
    # Check for undefined function calls
    # Validate financial value ranges
```

This pattern library ensures consistent validation across all documentation sections and prevents regression of quality standards.