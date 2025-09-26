# Container Deployment

Deploy FiveTwenty applications using Docker containers with comprehensive monitoring and production-ready configuration.

## Overview

Container deployment provides a lightweight, portable solution for running FiveTwenty trading applications in production. This approach uses Docker containers with supporting services for monitoring, data persistence, and security.

**Best for**: Small to medium trading operations, development teams familiar with containers, hybrid cloud deployments.

## Environment Configuration

### Production Configuration Management

Create secure configuration management for containerized deployment:

```python
# config/production.py
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from fivetwenty import Environment


@dataclass
class ProductionConfig:
    """Production configuration management."""

    # OANDA API Configuration
    fivetwenty_token: str
    fivetwenty_environment: Environment
    account_id: str

    # Application Settings
    log_level: str = "INFO"
    max_position_size: int = 100000
    daily_loss_limit: str = "1000.0"  # Use string for Decimal conversion

    # Infrastructure Settings
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql://localhost/trading"
    metrics_port: int = 8080
    health_check_port: int = 8081

    # Security Settings
    enable_ssl: bool = True
    api_rate_limit: int = 100
    max_concurrent_connections: int = 50

    # Monitoring & Alerting
    sentry_dsn: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    email_alerts: bool = True

    @classmethod
    def from_environment(cls) -> 'ProductionConfig':
        """Load configuration from environment variables."""

        # Validate required environment variables
        required_vars = [
            'FIVETWENTY_LIVE_TOKEN',
            'FIVETWENTY_OANDA_ACCOUNT'
        ]

        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")

        # Determine environment
        env_name = os.getenv('FIVETWENTY_OANDA_ENVIRONMENT', 'PRACTICE').upper()
        if env_name == 'LIVE':
            oanda_env = Environment.LIVE
        else:
            oanda_env = Environment.PRACTICE

        return cls(
            fivetwenty_token=os.getenv('FIVETWENTY_LIVE_TOKEN'),
            fivetwenty_environment=oanda_env,
            account_id=os.getenv('FIVETWENTY_OANDA_ACCOUNT'),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            max_position_size=int(os.getenv('MAX_POSITION_SIZE', '100000')),
            daily_loss_limit=os.getenv('DAILY_LOSS_LIMIT', '1000.0000'),
            redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
            database_url=os.getenv('DATABASE_URL', 'postgresql://localhost/trading'),
            metrics_port=int(os.getenv('METRICS_PORT', '8080')),
            health_check_port=int(os.getenv('HEALTH_PORT', '8081')),
            sentry_dsn=os.getenv('SENTRY_DSN'),
            slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL')
        )

    def validate(self) -> bool:
        """Validate configuration for production deployment."""

        validation_errors = []

        # Security validations
        if self.fivetwenty_environment == Environment.LIVE and 'practice' in self.fivetwenty_token.lower():
            validation_errors.append("Live environment with practice token detected")

        if not self.enable_ssl and self.fivetwenty_environment == Environment.LIVE:
            validation_errors.append("SSL must be enabled for live trading")

        # Risk management validations
        if Decimal(self.daily_loss_limit) <= 0:
            validation_errors.append("Daily loss limit must be positive")

        if self.max_position_size <= 0:
            validation_errors.append("Max position size must be positive")

        # Infrastructure validations
        if not self.database_url.startswith('postgresql://'):
            validation_errors.append("PostgreSQL database required for production")

        if validation_errors:
            for error in validation_errors:
                print(f"❌ Config Error: {error}")
            return False

        print("✅ Production configuration validated")
        return True

# Load and validate configuration
try:
    config = ProductionConfig.from_environment()
    if not config.validate():
        exit(1)
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)
```

### Environment Variables File

Create secure environment file:

```bash
# .env.production
FIVETWENTY_LIVE_TOKEN=your_live_oanda_token_here
FIVETWENTY_OANDA_ACCOUNT=your_account_id_here
FIVETWENTY_OANDA_ENVIRONMENT=LIVE

# Database Configuration
POSTGRES_PASSWORD=secure_password_here
DATABASE_URL=postgresql://trading:secure_password_here@postgres:5432/trading_prod

# Redis Configuration
REDIS_PASSWORD=secure_redis_password
REDIS_URL=redis://:secure_redis_password@redis:6379

# Monitoring
SENTRY_DSN=your_sentry_dsn_here
SLACK_WEBHOOK_URL=your_slack_webhook_here
GRAFANA_PASSWORD=secure_grafana_password

# Application Settings
LOG_LEVEL=INFO
MAX_POSITION_SIZE=100000
DAILY_LOSS_LIMIT=1000.0000
```

## Dockerfile Configuration

### Optimized Production Dockerfile

```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create application user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8081/health || exit 1

# Expose ports
EXPOSE 8080 8081

# Default command
CMD ["python", "-m", "src.main"]
```

### Requirements File

```txt
# requirements.txt
fivetwenty>=1.0.0
asyncio>=3.4.3
aiohttp>=3.8.0
prometheus-client>=0.16.0
sentry-sdk>=1.20.0
uvloop>=0.17.0
redis>=4.5.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
```

## Docker Compose Production Stack

### Complete Production Stack

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  trading-app:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    restart: unless-stopped
    environment:
      - FIVETWENTY_LIVE_TOKEN=${FIVETWENTY_LIVE_TOKEN}
      - FIVETWENTY_OANDA_ACCOUNT=${FIVETWENTY_OANDA_ACCOUNT}
      - FIVETWENTY_OANDA_ENVIRONMENT=LIVE
      - DATABASE_URL=postgresql://trading:${POSTGRES_PASSWORD}@postgres:5432/trading_prod
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - LOG_LEVEL=INFO
      - SENTRY_DSN=${SENTRY_DSN}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8080:8080"  # Metrics
      - "8081:8081"  # Health check
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - trading-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  postgres:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      - POSTGRES_DB=trading_prod
      - POSTGRES_USER=trading
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"
    networks:
      - trading-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading -d trading_prod"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - trading-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  prometheus:
    image: prom/prometheus:latest
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    networks:
      - trading-network

  grafana:
    image: grafana/grafana:latest
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    networks:
      - trading-network

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:

networks:
  trading-network:
    driver: bridge
```

## Production Application Code

### Main Application with Health Checks

```python
# src/main.py
import asyncio
import logging
import signal
import sys
from typing import Optional
from datetime import datetime
import aiohttp
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration

from fivetwenty import AsyncClient
from config.production import ProductionConfig, config

# Initialize monitoring
REQUEST_COUNT = Counter('oanda_requests_total', 'Total API requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('oanda_request_duration_seconds', 'Request latency', ['endpoint'])
ACTIVE_POSITIONS = Gauge('active_positions_total', 'Active trading positions')
ACCOUNT_BALANCE = Gauge('account_balance', 'Current account balance')

class ProductionTradingSystem:
    """Production-ready trading system with FiveTwenty."""

    def __init__(self, config: ProductionConfig):
        self.config = config
        self.client: Optional[AsyncClient] = None
        self.running = False
        self.health_status = {"status": "starting", "last_check": None}

        # Initialize logging
        self._setup_logging()

        # Initialize monitoring
        if config.sentry_dsn:
            sentry_sdk.init(
                dsn=config.sentry_dsn,
                integrations=[AsyncioIntegration(auto_enabling=True)],
                traces_sample_rate=0.1
            )

        self.logger = logging.getLogger(__name__)
        self.logger.info("Production trading system initialized")

    def _setup_logging(self):
        """Configure production logging."""

        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)

        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('logs/trading.log'),
                logging.FileHandler('logs/error.log', level=logging.ERROR)
            ]
        )

    async def initialize(self):
        """Initialize all system components."""

        try:
            self.logger.info("Initializing production trading system...")

            # Initialize OANDA client
            self.client = AsyncClient(
                token=self.config.fivetwenty_token,
                environment=self.config.fivetwenty_environment,
                timeout=30.0
            )
            await self.client.__aenter__()

            # Validate connection and account
            account = await self.client.accounts.get_account(
                account_id=self.config.account_id
            )

            self.logger.info(f"Connected to OANDA {self.config.fivetwenty_environment.value}")
            self.logger.info(f"Trading account: {self.config.account_id}")
            self.logger.info(f"Account balance: {account.balance}")

            # Start monitoring servers
            await self._start_monitoring_servers()

            self.health_status = {"status": "healthy", "last_check": datetime.now().isoformat()}
            self.logger.info("System initialization completed successfully")

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.health_status = {"status": "unhealthy", "error": str(e), "last_check": datetime.now().isoformat()}
            raise

    async def _start_monitoring_servers(self):
        """Start Prometheus metrics and health check servers."""

        # Start Prometheus metrics server
        start_http_server(self.config.metrics_port)
        self.logger.info(f"Metrics server started on port {self.config.metrics_port}")

        # Start health check server
        app = aiohttp.web.Application()
        app.router.add_get('/health', self._health_check_handler)
        app.router.add_get('/ready', self._readiness_check_handler)

        runner = aiohttp.web.AppRunner(app)
        await runner.setup()

        site = aiohttp.web.TCPSite(runner, '0.0.0.0', self.config.health_check_port)
        await site.start()

        self.logger.info(f"Health check server started on port {self.config.health_check_port}")

    async def _health_check_handler(self, request):
        """Health check endpoint for load balancers."""

        try:
            # Quick system health check
            if self.client and self.running:
                # Simple API connectivity test
                await asyncio.wait_for(
                    self.client.accounts.get_account(account_id=self.config.account_id),
                    timeout=5.0
                )

                self.health_status = {
                    "status": "healthy",
                    "last_check": datetime.now().isoformat(),
                    "uptime": "running"
                }

                return aiohttp.web.json_response(self.health_status, status=200)
            else:
                return aiohttp.web.json_response(
                    {"status": "unhealthy", "reason": "system not running"},
                    status=503
                )

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return aiohttp.web.json_response(
                {"status": "unhealthy", "error": str(e)},
                status=503
            )

    async def _readiness_check_handler(self, request):
        """Readiness check for container orchestration."""

        if self.running and self.client:
            return aiohttp.web.json_response({"status": "ready"}, status=200)
        else:
            return aiohttp.web.json_response({"status": "not ready"}, status=503)

    async def start_trading(self):
        """Start the main trading loop."""

        self.running = True
        self.logger.info("Starting trading operations...")

        try:
            # Main trading loop
            while self.running:
                try:
                    # Update system metrics
                    await self._update_metrics()

                    # Execute trading logic
                    await self._trading_cycle()

                    # Wait before next cycle
                    await asyncio.sleep(1.0)  # 1-second cycle

                except Exception as e:
                    self.logger.error(f"Trading cycle error: {e}")
                    # Continue running despite errors
                    await asyncio.sleep(5.0)

        except Exception as e:
            self.logger.error(f"Critical trading error: {e}")
            await self._send_alert(f"Trading system error: {e}")

        finally:
            self.logger.info("Trading operations stopped")

    async def _update_metrics(self):
        """Update Prometheus metrics."""

        try:
            # Get account information
            account = await self.client.accounts.get_account(
                account_id=self.config.account_id
            )

            # Update metrics (convert Decimal to float for Prometheus)
            balance_value = str(account.balance)
            ACCOUNT_BALANCE.set(float(balance_value))
            ACTIVE_POSITIONS.set(account.open_position_count)

            REQUEST_COUNT.labels(endpoint='accounts', status='success').inc()

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='accounts', status='error').inc()
            self.logger.error(f"Metrics update error: {e}")

    async def _trading_cycle(self):
        """Execute one trading cycle - implement your strategy here."""

        try:
            # Get current positions
            positions = await self.client.positions.get_positions(
                account_id=self.config.account_id
            )

            # Risk management check
            total_unrealized_pl = sum(
                float(Decimal(str(pos.unrealized_pl or "0"))) for pos in positions.positions
                if pos.unrealized_pl
            )

            if abs(total_unrealized_pl) > float(Decimal(self.config.daily_loss_limit)):
                await self._emergency_stop("Daily loss limit exceeded")

            self.logger.debug(f"Trading cycle completed - {len(positions.positions)} positions")

        except Exception as e:
            self.logger.error(f"Trading cycle error: {e}")
            raise

    async def _emergency_stop(self, reason: str):
        """Emergency stop all trading activities."""

        self.logger.critical(f"EMERGENCY STOP: {reason}")
        await self._send_alert(f"EMERGENCY STOP EXECUTED: {reason}")

        # Stop main loop
        self.running = False

    async def _send_alert(self, message: str):
        """Send alert notifications."""

        self.logger.critical(f"ALERT: {message}")

        # Send Slack notification if configured
        if self.config.slack_webhook_url:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "text": f"🚨 Trading Alert: {message}",
                        "channel": "#trading-alerts",
                        "username": "Trading Bot"
                    }
                    await session.post(self.config.slack_webhook_url, json=payload)
            except Exception as e:
                self.logger.error(f"Failed to send Slack alert: {e}")

    def setup_signal_handlers(self):
        """Setup graceful shutdown signal handlers."""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    async def shutdown(self):
        """Graceful system shutdown."""

        self.logger.info("Shutting down trading system...")
        self.running = False

        try:
            if self.client:
                await self.client.__aexit__(None, None, None)

            self.logger.info("System shutdown completed")

        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")

async def main():
    """Main application entry point."""

    system = None

    try:
        # Initialize system
        system = ProductionTradingSystem(config)
        system.setup_signal_handlers()

        # Start system
        await system.initialize()
        await system.start_trading()

    except KeyboardInterrupt:
        logging.info("Received interrupt signal")
    except Exception as e:
        logging.error(f"Application error: {e}")
        if system:
            await system._send_alert(f"Application crashed: {e}")
        return 1
    finally:
        if system:
            await system.shutdown()

    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
```

## Deployment Scripts

### Production Deployment Script

```bash
#!/bin/bash
# deploy.sh - Container production deployment script

set -e  # Exit on any error

# Configuration
APP_NAME="fivetwenty-trading-system"
DEPLOY_ENV="production"
VERSION=${1:-latest}

echo "🚀 Starting container deployment of $APP_NAME:$VERSION"

# Pre-deployment checks
echo "📋 Running pre-deployment checks..."

# Check required environment variables
required_vars=(
    "FIVETWENTY_LIVE_TOKEN"
    "FIVETWENTY_OANDA_ACCOUNT"
    "POSTGRES_PASSWORD"
    "REDIS_PASSWORD"
    "SENTRY_DSN"
)

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Missing required environment variable: $var"
        exit 1
    fi
done

echo "✅ Environment variables validated"

# Build Docker image
echo "🏗️ Building Docker image..."
docker build -t $APP_NAME:$VERSION .
docker tag $APP_NAME:$VERSION $APP_NAME:latest

# Stop existing containers gracefully
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --timeout 30

# Start new deployment
echo "🔄 Starting new deployment..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for health check
echo "🏥 Waiting for health check..."
for i in {1..30}; do
    if curl -f http://localhost:8081/health > /dev/null 2>&1; then
        echo "✅ Health check passed"
        break
    fi
    echo "⏳ Waiting for service to be ready... ($i/30)"
    sleep 10
done

if [ $i -eq 30 ]; then
    echo "❌ Health check failed after 5 minutes"
    exit 1
fi

# Verify deployment
echo "🔍 Verifying deployment..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ Container deployment completed successfully"
echo "📊 Access monitoring at:"
echo "   - Metrics: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo "   - Health: http://localhost:8081/health"
```

### Backup Script

```bash
#!/bin/bash
# backup.sh - Database and configuration backup

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
DB_NAME="trading_prod"

mkdir -p $BACKUP_DIR

# Create database backup
echo "📁 Creating database backup..."
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U trading $DB_NAME | gzip > $BACKUP_DIR/db_backup_$(date +%H%M%S).sql.gz

# Backup configuration files
echo "📋 Backing up configuration..."
cp -r config $BACKUP_DIR/
cp docker-compose.prod.yml $BACKUP_DIR/
cp .env.production $BACKUP_DIR/

# Backup logs
echo "📝 Backing up logs..."
cp -r logs $BACKUP_DIR/

echo "✅ Backup completed successfully to $BACKUP_DIR"

# Cleanup old backups (keep 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} \;
```

## Monitoring Configuration

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "trading_alerts.yml"

scrape_configs:
  - job_name: 'fivetwenty-trading-system'
    static_configs:
      - targets: ['trading-app:8080']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

### Alert Rules

```yaml
# monitoring/trading_alerts.yml
groups:
  - name: trading_alerts
    rules:
      - alert: AccountBalanceLow
        expr: account_balance < 5000
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "Account balance is low"
          description: "Account balance is {{ $value }}"

      - alert: TradingSystemDown
        expr: up{job="fivetwenty-trading-system"} == 0
        for: 30s
        labels:
          severity: critical
        annotations:
          summary: "Trading system is down"
          description: "Trading system has been down for more than 30 seconds"

      - alert: HighErrorRate
        expr: rate(oanda_requests_total{status="error"}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High API error rate"
          description: "Error rate is {{ $value }} errors per second"
```

## Security Considerations

### Container Security Best Practices

1. **Non-root User**: Always run containers as non-root user
2. **Minimal Base Image**: Use slim or alpine base images
3. **Security Scanning**: Scan images for vulnerabilities
4. **Secrets Management**: Never include secrets in images
5. **Network Isolation**: Use custom networks for service isolation

### SSL/TLS Configuration

```yaml
# docker-compose.ssl.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./ssl:/etc/nginx/ssl
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - trading-app
    networks:
      - trading-network

  trading-app:
    # Remove port exposure - access through nginx only
    ports: []
    # ... rest of configuration
```

## Troubleshooting

### Common Container Issues

**Health Check Failures**:
```bash
# Check application logs
docker-compose -f docker-compose.prod.yml logs trading-app

# Check health endpoint directly
curl -v http://localhost:8081/health
```

**Database Connection Issues**:
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test database connection
docker-compose -f docker-compose.prod.yml exec postgres psql -U trading -d trading_prod -c "SELECT 1;"
```

**Memory Issues**:
```bash
# Monitor container resource usage
docker stats

# Check application metrics
curl http://localhost:8080/metrics | grep memory
```

### Performance Optimization

1. **Resource Limits**: Set appropriate CPU and memory limits
2. **Volume Mounts**: Use volumes for persistent data
3. **Network Optimization**: Use custom networks for better performance
4. **Log Management**: Implement log rotation and cleanup

## Maintenance Procedures

### Regular Maintenance Tasks

1. **Daily**: Check health status and logs
2. **Weekly**: Review metrics and performance
3. **Monthly**: Update base images and dependencies
4. **Quarterly**: Security audit and penetration testing

### Scaling Considerations

For higher throughput requirements:

1. **Horizontal Scaling**: Run multiple container instances
2. **Load Balancing**: Use nginx or HAProxy
3. **Database Optimization**: Consider read replicas
4. **Caching**: Implement Redis caching strategies

Container deployment provides a robust, portable solution for production FiveTwenty trading applications with comprehensive monitoring and security features.