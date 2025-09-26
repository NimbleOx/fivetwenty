# Best Practices & Production Deployment

Deploy robust streaming systems to production with comprehensive monitoring, error handling, and performance optimization.

---

## Production Architecture Patterns

```python
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from decimal import Decimal
from contextlib import asynccontextmanager
from fivetwenty import AsyncClient, Environment

@dataclass
class ProductionConfig:
    """Production-ready configuration."""
    api_token: str
    account_id: str
    environment: Environment = Environment.PRACTICE
    max_concurrent_streams: int = 5
    heartbeat_interval: int = 5
    reconnect_attempts: int = 10
    position_limits: Dict[str, float] = field(default_factory=dict)
    daily_loss_limit: float = 1000.0
    enable_metrics: bool = True
    log_level: str = "INFO"

class ProductionStreamingSystem:
    """Production-ready streaming system with comprehensive monitoring."""

    def __init__(self, config: ProductionConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.metrics = ProductionMetrics() if config.enable_metrics else None
        self.circuit_breaker = CircuitBreaker()
        self.is_running = False

        # Component initialization
        self.clients = []
        self.active_streams = {}
        self.health_monitors = []

    def _setup_logging(self) -> logging.Logger:
        """Configure production logging."""

        logger = logging.getLogger("production_streaming")
        logger.setLevel(getattr(logging, self.config.log_level))

        # Console handler with structured format
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        return logger

    async def start_production_system(self, instruments: List[str]):
        """Start production streaming system."""

        self.logger.info("Starting production streaming system")
        self.is_running = True

        try:
            # Initialize clients with connection pooling
            await self._initialize_clients()

            # Start health monitoring
            await self._start_health_monitoring()

            # Start streaming with fault tolerance
            await self._start_fault_tolerant_streaming(instruments)

        except Exception as e:
            self.logger.error(f"Failed to start production system: {e}")
            await self._emergency_shutdown()
            raise

    async def _initialize_clients(self):
        """Initialize multiple clients for redundancy."""

        for i in range(min(3, self.config.max_concurrent_streams)):
            client = AsyncClient(
                token=self.config.api_token,
                environment=self.config.environment
            )
            self.clients.append(client)

        self.logger.info(f"Initialized {len(self.clients)} clients")

    async def _start_fault_tolerant_streaming(self, instruments: List[str]):
        """Start streaming with fault tolerance and load balancing."""

        tasks = []

        # Primary data stream
        tasks.append(asyncio.create_task(
            self._run_primary_stream(instruments)
        ))

        # Backup streams
        for i in range(1, len(self.clients)):
            tasks.append(asyncio.create_task(
                self._run_backup_stream(instruments, i)
            ))

        # Monitoring tasks
        tasks.append(asyncio.create_task(
            self._monitor_system_health()
        ))

        # Risk monitoring
        tasks.append(asyncio.create_task(
            self._monitor_risk_limits()
        ))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _run_primary_stream(self, instruments: List[str]):
        """Run primary streaming connection with circuit breaker."""

        while self.is_running:
            try:
                if not self.circuit_breaker.can_execute():
                    await asyncio.sleep(self.circuit_breaker.timeout)
                    continue

                async with self.clients[0] as client:
                    async for price in client.pricing.get_pricing_stream(
                        account_id=self.config.account_id,
                        instruments=instruments
                    ):
                        if not self.is_running:
                            break

                        await self._process_production_data(price)
                        self.circuit_breaker.record_success()

            except Exception as e:
                self.logger.error(f"Primary stream error: {e}")
                self.circuit_breaker.record_failure()

                if self.metrics:
                    self.metrics.record_error("primary_stream", str(e))

                await asyncio.sleep(5)

    async def _process_production_data(self, price_data: Any):
        """Process data with comprehensive error handling."""

        try:
            start_time = datetime.now()

            # Validate data
            if not self._validate_price_data(price_data):
                self.logger.warning(f"Invalid price data: {price_data}")
                return

            # Process with timeout
            await asyncio.wait_for(
                self._execute_trading_logic(price_data),
                timeout=1.0  # 1 second timeout
            )

            # Record metrics
            if self.metrics:
                processing_time = (datetime.now() - start_time).total_seconds()
                self.metrics.record_processing_time(processing_time)

        except asyncio.TimeoutError:
            self.logger.warning("Processing timeout exceeded")
            if self.metrics:
                self.metrics.record_error("processing", "timeout")

        except Exception as e:
            self.logger.error(f"Processing error: {e}")
            if self.metrics:
                self.metrics.record_error("processing", str(e))

    def _validate_price_data(self, price_data: Any) -> bool:
        """Validate incoming price data."""

        # Implement comprehensive validation
        if not hasattr(price_data, 'instrument'):
            return False

        if not hasattr(price_data, 'bids') or not price_data.bids:
            return False

        if not hasattr(price_data, 'asks') or not price_data.asks:
            return False

        return True

    async def _execute_trading_logic(self, price_data: Any):
        """Execute trading logic with risk controls."""

        # Implement your trading logic here
        # This should include:
        # - Risk checks
        # - Position sizing
        # - Order execution
        # - Error handling

        pass

    async def _monitor_system_health(self):
        """Monitor overall system health."""

        while self.is_running:
            try:
                # Check memory usage
                health_status = await self._get_health_status()

                if not health_status['healthy']:
                    self.logger.warning(f"Health check failed: {health_status}")

                    if health_status['critical']:
                        await self._emergency_shutdown()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""

        import psutil

        # Memory check
        memory_percent = psutil.virtual_memory().percent

        # Active connections check
        active_connections = sum(1 for stream in self.active_streams.values()
                               if stream.get('status') == 'connected')

        # Recent error rate
        recent_errors = 0
        if self.metrics:
            recent_errors = self.metrics.get_error_rate(minutes=5)

        healthy = (
            memory_percent < 80 and
            active_connections > 0 and
            recent_errors < 10
        )

        critical = (
            memory_percent > 95 or
            active_connections == 0 or
            recent_errors > 50
        )

        return {
            'healthy': healthy,
            'critical': critical,
            'memory_percent': memory_percent,
            'active_connections': active_connections,
            'recent_errors': recent_errors,
            'timestamp': datetime.now()
        }

    async def _emergency_shutdown(self):
        """Emergency shutdown procedure."""

        self.logger.critical("Initiating emergency shutdown")

        # Stop all streaming
        self.is_running = False

        # Close all positions if needed
        # await self._close_all_positions()

        # Close all clients
        for client in self.clients:
            if hasattr(client, 'close'):
                await client.close()

        self.logger.critical("Emergency shutdown completed")

class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if execution is allowed."""

        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True

    def record_success(self):
        """Record successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed execution."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def _should_attempt_reset(self) -> bool:
        """Check if should attempt to reset circuit."""
        if self.last_failure_time:
            return (datetime.now() - self.last_failure_time).total_seconds() > self.timeout
        return True

class ProductionMetrics:
    """Production metrics collection."""

    def __init__(self):
        self.metrics = {
            'processing_times': [],
            'errors': [],
            'messages_processed': 0,
            'start_time': datetime.now()
        }

    def record_processing_time(self, time_seconds: float):
        """Record processing time."""
        self.metrics['processing_times'].append({
            'time': time_seconds,
            'timestamp': datetime.now()
        })
        self.metrics['messages_processed'] += 1

        # Keep only recent data
        cutoff = datetime.now() - timedelta(hours=1)
        self.metrics['processing_times'] = [
            pt for pt in self.metrics['processing_times']
            if pt['timestamp'] > cutoff
        ]

    def record_error(self, error_type: str, message: str):
        """Record error occurrence."""
        self.metrics['errors'].append({
            'type': error_type,
            'message': message,
            'timestamp': datetime.now()
        })

        # Keep only recent errors
        cutoff = datetime.now() - timedelta(hours=24)
        self.metrics['errors'] = [
            error for error in self.metrics['errors']
            if error['timestamp'] > cutoff
        ]

    def get_error_rate(self, minutes: int = 5) -> int:
        """Get error rate for specified time period."""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent_errors = [
            error for error in self.metrics['errors']
            if error['timestamp'] > cutoff
        ]
        return len(recent_errors)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        processing_times = [pt['time'] for pt in self.metrics['processing_times']]

        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            max_time = max(processing_times)
        else:
            avg_time = max_time = 0

        uptime = (datetime.now() - self.metrics['start_time']).total_seconds()

        return {
            'messages_processed': self.metrics['messages_processed'],
            'avg_processing_time_ms': avg_time * 1000,
            'max_processing_time_ms': max_time * 1000,
            'total_errors': len(self.metrics['errors']),
            'uptime_seconds': uptime,
            'messages_per_second': self.metrics['messages_processed'] / uptime if uptime > 0 else 0
        }

# Production deployment example
async def production_deployment_example():
    """Complete production deployment example."""

    config = ProductionConfig(
        api_token="your-production-token",
        account_id="your-account-id",
        environment=Environment.LIVE,  # Use LIVE for production
        max_concurrent_streams=3,
        position_limits={"EUR_USD": 10000, "GBP_USD": 8000},
        daily_loss_limit=Decimal("500.0"),
        enable_metrics=True,
        log_level="INFO"
    )

    system = ProductionStreamingSystem(config)

    try:
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        await system.start_production_system(instruments)

    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        await system._emergency_shutdown()

    except Exception as e:
        print(f"Production system error: {e}")
        await system._emergency_shutdown()

# Run production system
# await production_deployment_example()
```

---

## Security Best Practices

### API Token Management

```python
import os

from fivetwenty import AsyncClient, Environment


class SecureCredentialManager:
    """Secure credential management for production."""

    @staticmethod
    def get_api_token() -> str:
        """Get API token from secure source."""

        # Priority order:
        # 1. Environment variable
        # 2. Key management service
        # 3. Encrypted configuration file

        token = os.getenv('OANDA_API_TOKEN')
        if token:
            return token

        # Integrate with your key management system
        # token = get_from_key_vault('oanda-api-token')

        raise ValueError("API token not found in secure sources")

    @staticmethod
    def validate_token_permissions(token: str) -> bool:
        """Validate token has required permissions."""

        # Implement token validation logic
        # Check token scope and permissions

        return True

# Usage in production
def create_secure_client() -> AsyncClient:
    """Create client with secure credentials."""

    credential_manager = SecureCredentialManager()
    token = credential_manager.get_api_token()

    if not credential_manager.validate_token_permissions(token):
        raise ValueError("Token lacks required permissions")

    return AsyncClient(
        token=token,
        environment=Environment.LIVE
    )
```

### Network Security

```python
import ssl

import httpx

from fivetwenty import AsyncClient, Environment


def create_secure_client_with_tls() -> AsyncClient:
    """Create client with enhanced TLS security."""

    # Create secure TLS context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = True
    ssl_context.verify_mode = ssl.CERT_REQUIRED
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    # Configure httpx with secure settings
    http_client = httpx.AsyncClient(
        verify=ssl_context,
        timeout=httpx.Timeout(30.0)
    )

    return AsyncClient(
        token=SecureCredentialManager.get_api_token(),
        environment=Environment.LIVE,
        http_client=http_client
    )
```

---

## Performance Optimization

### Memory Management

```python
import gc
from datetime import datetime

import psutil


class MemoryOptimizer:
    """Optimize memory usage for long-running streams."""

    def __init__(self, max_memory_percent: float = 80.0):
        self.max_memory_percent = max_memory_percent
        self.last_cleanup = datetime.now()

    async def monitor_memory(self):
        """Monitor and manage memory usage."""

        while True:
            memory_percent = psutil.virtual_memory().percent

            if memory_percent > self.max_memory_percent:
                await self._perform_cleanup()

            await asyncio.sleep(30)  # Check every 30 seconds

    async def _perform_cleanup(self):
        """Perform memory cleanup."""

        # Force garbage collection
        gc.collect()

        # Clear old data from buffers
        # Implement buffer cleanup logic

        self.last_cleanup = datetime.now()
        print(f"Memory cleanup performed at {self.last_cleanup}")

# Integration with streaming system
class OptimizedStreamingSystem(ProductionStreamingSystem):
    """Streaming system with memory optimization."""

    def __init__(self, config: ProductionConfig):
        super().__init__(config)
        self.memory_optimizer = MemoryOptimizer()

    async def start_production_system(self, instruments: List[str]):
        """Start system with memory monitoring."""

        # Start memory monitoring
        memory_task = asyncio.create_task(
            self.memory_optimizer.monitor_memory()
        )

        # Start main system
        system_task = asyncio.create_task(
            super().start_production_system(instruments)
        )

        await asyncio.gather(memory_task, system_task)
```

---

## Monitoring and Alerting

### Health Check Endpoints

```python
from datetime import datetime
from typing import Any, Dict


class HealthCheckServer:
    """Health check server for monitoring."""

    def __init__(self, streaming_system: ProductionStreamingSystem):
        self.system = streaming_system

    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""

        return {
            'status': 'healthy' if self.system.is_running else 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': self._get_uptime(),
            'active_streams': len(self.system.active_streams),
            'memory_usage': self._get_memory_usage(),
            'error_rate': self._get_error_rate(),
            'performance': self._get_performance_metrics()
        }

    def _get_uptime(self) -> float:
        """Get system uptime in seconds."""
        if hasattr(self.system, 'start_time'):
            return (datetime.now() - self.system.start_time).total_seconds()
        return 0

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent,
            'used_gb': memory.used / (1024**3),
            'available_gb': memory.available / (1024**3)
        }

    def _get_error_rate(self) -> float:
        """Get recent error rate."""
        if self.system.metrics:
            return self.system.metrics.get_error_rate(minutes=5)
        return 0

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        if self.system.metrics:
            return self.system.metrics.get_performance_summary()
        return {}
```

---

## Deployment Checklist

### Pre-Production Validation

- [ ] **Security Review**
  - API token stored securely
  - TLS configuration validated
  - Network security policies applied
  - Access controls configured

- [ ] **Performance Testing**
  - Load testing completed
  - Memory usage profiled
  - Latency benchmarks established
  - Error handling validated

- [ ] **Monitoring Setup**
  - Health check endpoints configured
  - Alerting rules defined
  - Log aggregation configured
  - Metrics collection enabled

- [ ] **Risk Controls**
  - Position limits configured
  - Daily loss limits set
  - Circuit breakers tested
  - Emergency shutdown procedures verified

- [ ] **Operational Readiness**
  - Deployment automation tested
  - Rollback procedures documented
  - On-call procedures established
  - Documentation updated

### Production Deployment Steps

1. **Environment Preparation**
   - Production credentials configured
   - Infrastructure provisioned
   - Monitoring deployed

2. **Gradual Rollout**
   - Deploy to staging environment
   - Run smoke tests
   - Deploy to production with limited traffic
   - Monitor and validate

3. **Post-Deployment Validation**
   - Verify all health checks
   - Confirm monitoring alerts
   - Validate trading functionality
   - Monitor for 24 hours

---

## Related Tutorials

- [Streaming Fundamentals](streaming-fundamentals.md) - Core concepts
- [Advanced Features](advanced-features.md) - Sophisticated capabilities
- [Signal Generation](signal-generation.md) - Trading signals