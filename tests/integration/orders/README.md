# Order Management Integration Tests

This directory contains focused integration tests extracted from the original monolithic `test_order_management.py` file to improve maintainability, test execution performance, and development workflow.

## File Structure

### 🎯 **Modular Integration Test Files** (12 tests total)

| File | Purpose | Test Count | Key Functionality Tested |
|------|---------|------------|-------------------------|
| `test_basic_order_operations.py` | Core order types | 4 | Market, Limit, Stop, Market-If-Touched orders |
| `test_order_modification.py` | Order management | 2 | Order replacement, cancellation, client extensions |
| `test_order_listing.py` | Data retrieval & bulk ops | 2 | Filtering, pagination, concurrent operations |
| `test_advanced_features.py` | Advanced order features | 2 | GTD/GFD time-in-force, trigger conditions |
| `test_post_trade_risk_management.py` | Risk management | 1 | TP/SL/TSL/GSL orders linked to trades |
| `test_error_scenarios.py` | Error handling | 1 | Invalid parameters, timeouts, edge cases |

## Test Organization by Functionality

### **Basic Order Operations** 🔄
Tests fundamental order creation and execution:
- **Market Orders**: Immediate execution with price validation
- **Limit Orders**: Threshold-based execution with TP/SL
- **Stop Orders**: Stop-loss with price bounds
- **MIT Orders**: Market-if-touched trigger behavior

### **Order Management** ⚙️
Tests order lifecycle management:
- **Order Modification**: PUT operations for order replacement
- **Order Cancellation**: Single and batch cancellation
- **Client Extensions**: Custom tags and metadata

### **Data & Bulk Operations** 📊
Tests data retrieval and performance:
- **Order Listing**: Filtering by state, instrument, pagination
- **Bulk Operations**: Sequential and concurrent order creation

### **Advanced Features** ⚡
Tests sophisticated order functionality:
- **Time-in-Force**: GTD/GFD with timezone handling
- **Trigger Conditions**: BID/ASK/MID/INVERSE triggers

### **Risk Management** 🛡️
Tests post-trade risk management:
- **Take Profit Orders**: Linked to existing trades
- **Stop Loss Orders**: Price and distance-based
- **Trailing Stop Loss**: Dynamic adjustment
- **Guaranteed Stop Loss**: Premium calculation

### **Error Handling** ⚠️
Tests edge cases and error scenarios:
- **Invalid Parameters**: Malformed requests
- **Account Validation**: Invalid account IDs
- **Market Conditions**: Insufficient margin, closed markets
- **Network Issues**: Timeout handling

## Benefits of Modular Structure

### 🚀 **Development Workflow**
- **Targeted Testing**: Run specific functionality (e.g., `pytest test_basic_order_operations.py`)
- **Faster Feedback**: Smaller test files execute more quickly
- **Focused Debugging**: Easier to isolate and fix issues
- **Parallel Execution**: Different teams can work on different test categories

### 📈 **Maintainability**
- **Clear Separation**: Each file has a single responsibility
- **Easier Navigation**: Find specific tests quickly
- **Reduced Complexity**: Smaller files are easier to understand
- **Better Documentation**: Focused test categories with clear purposes

### ⚡ **Performance**
- **Selective Execution**: Run only relevant tests during development
- **CI/CD Optimization**: Parallel test execution potential
- **Resource Efficiency**: Load only necessary test code

## Usage Examples

```bash
# Run all order management integration tests
pytest tests/integration/orders/ --run-integration-live

# Test specific functionality
pytest tests/integration/orders/test_basic_order_operations.py --run-integration-live
pytest tests/integration/orders/test_error_scenarios.py --run-integration-live

# Run with verbose output for debugging
pytest tests/integration/orders/test_order_modification.py -v --run-integration-live

# Run specific test method
pytest tests/integration/orders/test_advanced_features.py::TestAdvancedOrderFeatures::test_trigger_conditions --run-integration-live

# Run tests matching a pattern
pytest tests/integration/orders/ -k "market_order" --run-integration-live
```

## Test Execution Requirements

### 🔧 **Prerequisites**
- Valid OANDA practice account credentials
- Network connectivity to OANDA practice API
- Sufficient account balance for test operations

### ⚙️ **Configuration**
All tests use the same fixtures as the original:
- `sandbox_client`: AsyncClient configured for OANDA practice environment
- `test_account_id`: Valid practice account ID
- `test_instruments`: Dictionary of available instruments for testing

### 🏷️ **Pytest Markers**
All integration tests are marked with:
- `@pytest.mark.asyncio` - Async test execution
- `@pytest.mark.integration` - Integration test category
- `@pytest.mark.trading` - Trading functionality tests

## Migration Status

✅ **Successfully Extracted**: All 12 integration tests modularized  
📋 **Original File**: `tests/integration/test_order_management.py` remains for backward compatibility  
🔄 **Full Coverage**: Combined test count matches original (12 tests)

## Development Guidelines

- **New Integration Tests**: Add to appropriate modular file based on functionality
- **Cross-Category Tests**: If unclear, add to most relevant file or create new focused module
- **Error Handling**: Ensure graceful handling of market conditions and API limitations
- **Test Independence**: Each test should be able to run standalone without dependencies

This modular organization significantly improves the integration test experience while maintaining complete test coverage and backward compatibility with existing workflows.
