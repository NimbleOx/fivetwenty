# TODO

## Distribution
- [ ] **PyPI Publishing** - Make package publicly available

## Testing & Quality
- [ ] **Integration Tests** - Add tests against OANDA sandbox environment (currently 427 unit tests)
- [ ] **Advanced Streaming Tests** - Test reconnection, heartbeat handling, error scenarios in live streams
- [ ] **More Examples** - Expand beyond current basic examples in examples/
- [ ] **API Contract Tests** - Automated contract testing against OANDA API
- [ ] **Performance Benchmarks** - Comprehensive performance testing suite
- [ ] **Load Testing** - High-throughput testing scenarios

## Architecture & Implementation

### Configuration Management
- [ ] **Centralized Configuration** - Consolidate scattered config (client, streaming, environment)
- [ ] **Environment Profiles** - Support for dev/staging/prod configurations with validation

### Enhanced Connection Management
- [ ] **Connection Health Checks** - Basic connection health monitoring
- [ ] **Load Balancing** - Multi-endpoint load balancing for improved reliability

### Streaming Enhancements
- [ ] **Stream Processing Pipeline** - Pipeline-based stream data processing
- [ ] **Real-time Aggregation** - Built-in OHLC and moving average calculations
- [ ] **Stream Multiplexing** - Support multiple consumers on single stream

## Implementation Notes

### Design Principles
- Keep it simple - avoid over-engineering
- Let users handle their own retry strategies, caching, monitoring, and error recovery
- Fail fast and provide clear error information
- Maintain minimal dependencies (httpx, pydantic only)

### Backward Compatibility
- All improvements maintain existing public API
- Feature flags for new functionality
- Gradual migration paths for any breaking changes

## Documentation Validation Framework

### 🔧 Potential New Validators
Based on spec, we could add:

- [ ] **Vale prose validator** - Writing quality checking (vale integration)
- [ ] **Link validator** - External link checking (currently internal only)
- [ ] **Educational progression** - Tutorial learning flow validation
- [ ] **Tutorial structure** - Tutorial organization checking
- [ ] **Python style validator** - Code style beyond syntax (ruff integration)

### Priority
**High**: Fix CLI examples in spec (breaks copy-paste)
**Medium**: Add prose/link validators if needed
**Low**: Full spec rewrite



Need to add a disclaimer to main page
Need to add outline of modern tools (uv, typing) to main page
Remove all the emojiis from our code blocks
Flesh out the examples
