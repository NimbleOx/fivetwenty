# API Reference - Information-Oriented Documentation

## What is API Reference?

API Reference documentation is **information-oriented** content that provides comprehensive, accurate, and quickly scannable information about the FiveTwenty's classes, methods, parameters, and return values. It's designed for quick lookup during development.

## When to Use API Reference

**Use API reference when you:**

- **Need specific parameter details** for a method call
- **Want to see all available options** for a function
- **Need to understand return value structure**
- **Are looking for method signatures** and type information
- **Want to quickly scan** available functionality
- **Need authoritative information** about SDK behavior

**Don't use API reference when you:**

- Want to learn how to use the SDK (use [Tutorials](../tutorials/index.md))
- Need to solve a specific problem (use [How-to Guides](../how-to-guides/index.md))
- Want to understand design decisions (use [Explanations](../explanation/index.md))

## Reference Structure

Our API reference is organized for maximum lookup efficiency:

### **Core Components**
Essential SDK building blocks you'll use in every application.

- **[Client API](client.md)** - AsyncClient and Client class methods and configuration
- **[Models & Data Types](models/index.md)** - Complete model reference with field descriptions
- **[Exceptions & Error Handling](exceptions.md)** - Error types and handling patterns

### **Endpoints**
Trading functionality organized by OANDA API endpoints.

- **[Accounts](endpoints/accounts.md)** - Account information and configuration methods
- **[Orders](endpoints/orders.md)** - Order placement, modification, and cancellation
- **[Trades](endpoints/trades.md)** - Trade management and monitoring
- **[Positions](endpoints/positions.md)** - Position tracking and management
- **[Pricing](endpoints/pricing.md)** - Price feeds and market data
- **[Instruments](endpoints/instruments.md)** - Instrument information and historical data
- **[Transactions](endpoints/transactions.md)** - Transaction history and details

## Reference Features

### **Method Signatures**
Complete method signatures with parameter types and return values:

```python
async def post_order(
    self,
    account_id: str,
    order: OrderRequest,
    *,
    timeout: Optional[float] = None
) -> OrderResponse:
    pass
```

### **Parameter Details**
Comprehensive parameter documentation including:
- **Type information** - Exact Python types expected
- **Required vs optional** - Clear indication of mandatory parameters
- **Constraints** - Value ranges, formats, and validation rules
- **Default values** - When parameters are optional

### 🔄 **Return Value Structure**
Complete return value documentation with:
- **Return types** - Exact classes and data structures
- **Field descriptions** - What each field contains
- **Example values** - Representative data samples
- **Null handling** - When fields might be None/null

### **Error Information**
Exception documentation including:
- **Error conditions** - When exceptions are raised
- **Error types** - Specific exception classes
- **Error codes** - OANDA API error codes
- **Handling patterns** - Recommended error handling approaches

## Quick Lookup Sections

### **Most Common Methods**
- `client.accounts.get_account_summary(account_id)` - Get account overview
- `client.orders.post_order(account_id, order)` - Place new order
- `client.positions.get_positions(account_id)` - Get current positions
- `client.pricing.stream_pricing(instruments)` - Stream live prices

### **Essential Models**
- `OrderRequest` - Order placement parameters
- `Position` - Position information structure
- `Transaction` - Transaction details format
- `Candlestick` - Price history format

### **Quick References**
- **[Rate Limits](client.md#rate-limits)** - API call limits and timing
- **[Error Codes](exceptions.md#common-error-codes)** - Complete error code reference
- **[Field Constraints](models/system-models.md#validationviolation)** - Value limits and formats
- **[Type Mappings](models/system-models.md#type-aliases)** - Python to OANDA API type conversions

## Reference Principles

### **Information-Oriented**
- Provides facts without explanation
- Focuses on "what" not "how" or "why"
- Optimized for quick scanning
- Authoritative and accurate

### **Lookup-Optimized**
- Organized for fast navigation
- Consistent structure across sections
- Cross-referenced for related items
- Searchable and scannable format

### **Complete Coverage**
- 100% SDK functionality documented
- All parameters and return values
- Every error condition noted
- All model fields described

### **User Context Aware**
- Assumes existing SDK familiarity
- Provides minimal working examples
- Focuses on specification details
- Includes only essential usage notes

## SDK Coverage Statistics

- **Client Methods:** 50+ fully documented methods
- **Model Classes:** 75+ comprehensive data models
- **Endpoint Coverage:** 100% of OANDA v20 API
- **Error Types:** Complete exception hierarchy
- **Field Documentation:** Every model field described

## Need More Context?

If you need more than just the technical specifications:

- **Learn with [Tutorials](../tutorials/index.md)** for hands-on guidance
- **Solve problems with [How-to Guides](../how-to-guides/index.md)** for specific solutions
- **Understand with [Explanations](../explanation/index.md)** for background knowledge

---

**Ready to look something up?** Use the navigation above or search for specific methods, classes, or parameters you need.