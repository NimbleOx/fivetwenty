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

Look at our poe commands to make sure they all work
