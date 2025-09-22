# Model Tests Organization

This directory contains unit tests with **perfect 1:1 alignment** between model files and test files, providing optimal maintainability and intuitive organization.

## Perfect Model-Test Alignment

### **Complete 1:1 Structure** (126 tests total)

| Model File | Test File | Test Count | Key Models Tested |
|------------|-----------|------------|------------------|
| `accounts.py` | `test_accounts.py` | 3 | Account, AccountProperties |
| `base.py` | `test_base.py` | 7 | ApiModel configuration, camelCase aliases |
| `enums.py` | `test_enums.py` | 10 | Currency, InstrumentName, OrderType, TimeInForce |
| `error_codes.py` | `test_error_codes.py` | 13 | ErrorCode, InsufficientLiquidity, etc. |
| `error_details.py` | `test_error_details.py` | 11 | ErrorDetails, reject reasons |
| `instruments.py` | `test_instruments.py` | 1 | Instrument model validation |
| `orders.py` | `test_orders.py` | 19 | Order requests, responses, advanced order types |
| `positions.py` | `test_positions.py` | 6 | Position, CalculatedPositionState |
| `pricing.py` | `test_pricing.py` | 19 | ClientPrice, PricingHeartbeat, candlestick data |
| `streaming.py` | `test_streaming.py` | 14 | Streaming configurations, reconnection policies |
| `trades.py` | `test_trades.py` | 6 | Trade, TradeSummary, CalculatedTradeState |
| `transactions.py` | `test_transactions.py` | 17 | Transaction models, OrderFillTransaction |

## Benefits of 1:1 Alignment

### **Intuitive Navigation**
- **Predictable Structure**: Every model file has exactly one corresponding test file
- **Easy Discovery**: Find tests for any model instantly by name
- **Logical Organization**: No guessing which test file covers which models

### **Development Efficiency**
- **Focused Testing**: Test specific model categories independently
- **Parallel Development**: Teams can work on model-test pairs simultaneously
- **Faster Feedback**: Run only tests for models being modified

### **Enhanced Maintainability**
- **Single Responsibility**: Each test file focuses on exactly one model file
- **Clear Boundaries**: No overlap between test file responsibilities
- **Consistent Structure**: Uniform organization across the entire codebase

## Usage Patterns

### **Working with Specific Models**
```bash
# Test the models you're working on
pytest tests/unit/models/test_orders.py    # When modifying orders.py
pytest tests/unit/models/test_pricing.py   # When modifying pricing.py
pytest tests/unit/models/test_trades.py    # When modifying trades.py
```

### **Development Workflow**
```bash
# 1. Modify a model file
vim fivetwenty/models/accounts.py

# 2. Test the corresponding test file
pytest tests/unit/models/test_accounts.py -v

# 3. Add new tests if needed
vim tests/unit/models/test_accounts.py
```

### **Category-Based Testing**
```bash
# Test all model tests
pytest tests/unit/models/

# Test specific functionality patterns
pytest tests/unit/models/ -k "alias"     # camelCase alias tests
pytest tests/unit/models/ -k "enum"      # Enum validation tests
pytest tests/unit/models/ -k "request"   # Request model tests
```

## Test Structure Patterns

### **Standard Test File Pattern**
Every test file follows this consistent structure:
1. **Imports**: Only models from the corresponding model file
2. **Test Classes**: Named to match model categories
3. **Test Methods**: Comprehensive coverage of model functionality
4. **Validation**: Includes OANDA API compatibility testing

### **Common Test Categories**
- **Model Instantiation**: Basic object creation and validation
- **Field Validation**: Required/optional field testing
- **Default Values**: Default field value verification
- **camelCase Aliases**: OANDA API compatibility testing
- **Business Logic**: Calculated properties and methods
- **Edge Cases**: Error handling and boundary conditions

## Advanced Testing Features

### **OANDA API Compatibility**
All model tests include comprehensive camelCase alias testing to ensure perfect compatibility with OANDA's REST API v20:

```python
# Example: Round-trip API compatibility test
def test_order_api_roundtrip(self):
    # Receive from API (camelCase)
    api_data = {"timeInForce": "GTC", "positionFill": "DEFAULT"}
    order = LimitOrderRequest(**api_data)
    
    # Send to API (camelCase)
    back_to_api = order.model_dump(by_alias=True)
    assert back_to_api["timeInForce"] == "GTC"
```

### **Field and Data Validation**
Tests include validation of model fields and data integrity:

```python
# Example: Trade field validation
def test_trade_fields(self):
    trade = Trade(realized_pl="5.00", unrealized_pl="10.00")
    assert trade.realized_pl == Decimal("5.00")  # Field validation
```

## Migration Benefits

### **From Previous Organization**
- **Eliminated confusion** about which tests cover which models
- **Reduced cognitive load** when working with specific models
- **Improved test discovery** with predictable naming
- **Enhanced maintainability** with clear boundaries

### **Perfect Coverage**
- **126 total tests** across 12 model files
- **Complete extraction** from original monolithic test file
- **No test duplication** or missing coverage
- **Consistent patterns** across all test files

## Development Guidelines

### **Adding New Models**
When creating a new model file:
1. Create `fivetwenty/models/new_feature.py`
2. Create `tests/unit/models/test_new_feature.py`
3. Follow existing test patterns for consistency

### **Modifying Existing Models**
When changing a model:
1. Update the model in `fivetwenty/models/{name}.py`
2. Update tests in `tests/unit/models/test_{name}.py`
3. Ensure all tests pass with the changes

### **Test Quality Standards**
- Include basic instantiation tests for all models
- Test both snake_case and camelCase field access
- Validate default values and optional fields
- Test calculated properties and business logic
- Include edge cases and error conditions

This 1:1 alignment creates an intuitive, maintainable, and efficient testing structure that scales perfectly with the model architecture.