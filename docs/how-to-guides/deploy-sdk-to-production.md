# How to Deploy SDK to Production

**Problem**: You need to deploy FiveTwenty applications to production with proper security, monitoring, and reliability.

**Solution**: Implement production deployment best practices including containerization, environment management, monitoring, and failover strategies.

---

## Prerequisites

- Working FiveTwenty application tested in practice environment
- Live OANDA trading account with API access
- Production server infrastructure (cloud or on-premises)
- Understanding of containerization and deployment concepts
- SSL certificates and domain setup (if applicable)

---

## Production Environment Setup

### Environment Configuration

Set up secure environment management:

```python
# config/production.py
import os
from typing import Dict, Optional
from dataclasses import dataclass
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
        if self.daily_loss_limit <= 0:
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

### Dockerfile for Production

Create optimized Docker container:

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

### Docker Compose for Production Stack

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
      - REDIS_URL=redis://redis:6379
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

---

## Application Production Code

### Production-Ready Main Application

```python
# src/main.py
import asyncio
import logging
import signal
import sys
from typing import Dict, List, Optional
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
            accounts = await self.client.accounts.list()
            if not accounts:
                raise RuntimeError("No accounts found")

            account_found = any(acc.id == self.config.account_id for acc in accounts)
            if not account_found:
                raise RuntimeError(f"Account {self.config.account_id} not found")

            self.logger.info(f"Connected to OANDA {self.config.fivetwenty_environment.value}")
            self.logger.info(f"Trading account: {self.config.account_id}")

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
                    self.client.accounts.list(),
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
        """Readiness check for Kubernetes deployments."""

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
            account = await self.client.accounts.get(self.config.account_id)

            # Update metrics
            ACCOUNT_BALANCE.set(float(account.balance))
            ACTIVE_POSITIONS.set(account.open_position_count)

            REQUEST_COUNT.labels(endpoint='accounts', status='success').inc()

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='accounts', status='error').inc()
            self.logger.error(f"Metrics update error: {e}")

    async def _trading_cycle(self):
        """Execute one trading cycle."""

        # Placeholder for your trading strategy
        # This is where you would implement your actual trading logic

        try:
            # Example: Check positions and manage risk
            positions = await self.client.positions.list_open(self.config.account_id)

            for position in positions:
                # Risk management logic
                unrealized_pl = float(position.unrealized_pl)
                if unrealized_pl < -self.config.daily_loss_limit:
                    await self._emergency_stop("Daily loss limit exceeded")

            self.logger.debug(f"Trading cycle completed - {len(positions)} positions")

        except Exception as e:
            self.logger.error(f"Trading cycle error: {e}")
            raise

    async def _emergency_stop(self, reason: str):
        """Emergency stop all trading activities."""

        self.logger.critical(f"EMERGENCY STOP: {reason}")

        try:
            # Close all positions
            positions = await self.client.positions.list_open(self.config.account_id)

            for position in positions:
                await self.client.positions.close(
                    self.config.account_id,
                    position.instrument,
                    long_units="ALL",
                    short_units="ALL"
                )

            # Cancel all pending orders
            orders = await self.client.orders.list_pending(self.config.account_id)
            for order in orders:
                await self.client.orders.cancel(self.config.account_id, order.id)

            await self._send_alert(f"EMERGENCY STOP EXECUTED: {reason}")

        except Exception as e:
            self.logger.error(f"Emergency stop error: {e}")
            await self._send_alert(f"EMERGENCY STOP FAILED: {e}")

    async def _send_alert(self, message: str):
        """Send alert notifications."""

        self.logger.critical(f"ALERT: {message}")

        # Send Slack notification if configured
        if self.config.slack_webhook_url:
            try:
                import aiohttp
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

---

## Deployment Scripts

### Production Deployment Script

```bash
#!/bin/bash
# deploy.sh - Production deployment script

set -e  # Exit on any error

# Configuration
APP_NAME="FiveTwenty-trading-system"
DEPLOY_ENV="production"
DOCKER_REGISTRY="your-registry.com"
VERSION=${1:-latest}

echo "🚀 Starting production deployment of $APP_NAME:$VERSION"

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

# Build and tag Docker image
echo "🏗️ Building Docker image..."
docker build -t $DOCKER_REGISTRY/$APP_NAME:$VERSION .
docker tag $DOCKER_REGISTRY/$APP_NAME:$VERSION $DOCKER_REGISTRY/$APP_NAME:latest

# Push to registry
echo "📤 Pushing to registry..."
docker push $DOCKER_REGISTRY/$APP_NAME:$VERSION
docker push $DOCKER_REGISTRY/$APP_NAME:latest

# Database migrations
echo "🗃️ Running database migrations..."
docker-compose -f docker-compose.prod.yml run --rm trading-app python -m alembic upgrade head

# Deploy with zero-downtime
echo "🔄 Deploying with rolling update..."
docker-compose -f docker-compose.prod.yml up -d --no-deps --scale trading-app=2 trading-app

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

# Scale down old instances
docker-compose -f docker-compose.prod.yml up -d --scale trading-app=1

echo "✅ Deployment completed successfully"

# Post-deployment verification
echo "🔍 Running post-deployment tests..."
python scripts/deployment_tests.py --env production

echo "🎉 Production deployment of $APP_NAME:$VERSION completed!"
```

### Kubernetes Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: FiveTwenty-trading-system
  labels:
    app: FiveTwenty-trading-system
spec:
  replicas: 2
  selector:
    matchLabels:
      app: FiveTwenty-trading-system
  template:
    metadata:
      labels:
        app: FiveTwenty-trading-system
    spec:
      containers:
      - name: trading-app
        image: your-registry.com/FiveTwenty-trading-system:latest
        ports:
        - containerPort: 8080
          name: metrics
        - containerPort: 8081
          name: health
        env:
        - name: FIVETWENTY_LIVE_TOKEN
          valueFrom:
            secretKeyRef:
              name: OANDA-secrets
              key: live-token
        - name: FIVETWENTY_OANDA_ACCOUNT
          valueFrom:
            secretKeyRef:
              name: OANDA-secrets
              key: account-id
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8081
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8081
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        persistentVolumeClaim:
          claimName: trading-logs-pvc
      restartPolicy: Always

---
apiVersion: v1
kind: Service
metadata:
  name: OANDA-trading-service
spec:
  selector:
    app: FiveTwenty-trading-system
  ports:
  - name: metrics
    port: 8080
    targetPort: 8080
  - name: health
    port: 8081
    targetPort: 8081

---
apiVersion: v1
kind: Secret
metadata:
  name: OANDA-secrets
type: Opaque
data:
  live-token: <base64-encoded-token>
  account-id: <base64-encoded-account-id>
```

---

## Monitoring and Observability

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "trading_alerts.yml"

scrape_configs:
  - job_name: 'FiveTwenty-trading-system'
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

### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "OANDA Trading System",
    "panels": [
      {
        "title": "Account Balance",
        "type": "stat",
        "targets": [
          {
            "expr": "account_balance",
            "legendFormat": "Balance"
          }
        ]
      },
      {
        "title": "Active Positions",
        "type": "stat",
        "targets": [
          {
            "expr": "active_positions_total",
            "legendFormat": "Positions"
          }
        ]
      },
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(oanda_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Request Latency",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(oanda_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

---

## Security Best Practices

### Secrets Management

```python
from fivetwenty import AsyncClient, Environment

# src/security/secrets.py
import os
import boto3
from typing import Dict, Optional
import logging

class SecretsManager:
    """Secure secrets management for production."""

    def __init__(self, provider: str = "env"):
        self.provider = provider
        self.logger = logging.getLogger(__name__)

        if provider == "aws":
            self.secrets_client = boto3.client('secretsmanager')
        elif provider == "vault":
            # HashiCorp Vault integration
            pass

    def get_secret(self, secret_name: str) -> Optional[str]:
        """Retrieve secret securely."""

        try:
            if self.provider == "env":
                return os.getenv(secret_name)

            elif self.provider == "aws":
                response = self.secrets_client.get_secret_value(SecretId=secret_name)
                return response['SecretString']

            elif self.provider == "vault":
                # Implement Vault retrieval
                pass

        except Exception as e:
            self.logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            return None

    def rotate_token(self, old_token: str, new_token: str) -> bool:
        """Implement token rotation."""

        try:
            # Validate new token
            test_client = AsyncClient(token=new_token, environment=Environment.PRACTICE)
            accounts = await test_client.accounts.list()

            if accounts:
                # Update secret store
                if self.provider == "aws":
                    self.secrets_client.update_secret(
                        SecretId="FIVETWENTY_LIVE_TOKEN",
                        SecretString=new_token
                    )

                self.logger.info("Token rotation successful")
                return True
            else:
                self.logger.error("New token validation failed")
                return False

        except Exception as e:
            self.logger.error(f"Token rotation failed: {e}")
            return False

# Network security
def configure_ssl_context():
    """Configure secure SSL context."""

    import ssl

    context = ssl.create_default_context()
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')

    return context
```

---

## Backup and Disaster Recovery

### Database Backup Strategy

```bash
#!/bin/bash
# backup.sh - Database backup script

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
DB_NAME="trading_prod"
S3_BUCKET="your-backup-bucket"

mkdir -p $BACKUP_DIR

# Create database backup
echo "📁 Creating database backup..."
pg_dump -h postgres -U trading $DB_NAME | gzip > $BACKUP_DIR/db_backup_$(date +%H%M%S).sql.gz

# Backup configuration files
echo "📋 Backing up configuration..."
cp -r /app/config $BACKUP_DIR/
cp docker-compose.prod.yml $BACKUP_DIR/

# Upload to S3
echo "☁️ Uploading to S3..."
aws s3 sync $BACKUP_DIR s3://$S3_BUCKET/$(date +%Y-%m-%d)/

# Cleanup old backups (keep 30 days)
find /backups -type d -mtime +30 -exec rm -rf {} \;

echo "✅ Backup completed successfully"
```

### Disaster Recovery Plan

```python
# scripts/disaster_recovery.py
import asyncio
import logging
from typing import List, Dict
from fivetwenty import AsyncClient, Environment

class DisasterRecoveryManager:
    """Manage disaster recovery procedures."""

    def __init__(self, primary_config: dict, backup_config: dict):
        self.primary_config = primary_config
        self.backup_config = backup_config
        self.logger = logging.getLogger(__name__)

    async def check_system_health(self) -> bool:
        """Check if primary system is healthy."""

        try:
            async with AsyncClient(
                token=self.primary_config['token'],
                environment=Environment.LIVE
            ) as client:
                accounts = await client.accounts.list()
                return len(accounts) > 0

        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    async def initiate_failover(self) -> bool:
        """Initiate failover to backup system."""

        self.logger.critical("INITIATING DISASTER RECOVERY FAILOVER")

        try:
            # 1. Stop primary system
            await self._stop_primary_system()

            # 2. Start backup system
            await self._start_backup_system()

            # 3. Verify backup system
            if await self._verify_backup_system():
                self.logger.info("Failover completed successfully")
                return True
            else:
                self.logger.error("Backup system verification failed")
                return False

        except Exception as e:
            self.logger.error(f"Failover failed: {e}")
            return False

    async def _stop_primary_system(self):
        """Emergency stop primary system."""

        # Close all positions
        async with AsyncClient(
            token=self.primary_config['token'],
            environment=Environment.LIVE
        ) as client:

            positions = await client.positions.list_open(self.primary_config['account_id'])
            for position in positions:
                await client.positions.close(
                    self.primary_config['account_id'],
                    position.instrument,
                    long_units="ALL",
                    short_units="ALL"
                )

    async def _start_backup_system(self):
        """Start backup trading system."""

        # Implementation depends on your backup infrastructure
        # This could involve starting backup containers, switching DNS, etc.
        pass

    async def _verify_backup_system(self) -> bool:
        """Verify backup system is operational."""

        try:
            async with AsyncClient(
                token=self.backup_config['token'],
                environment=Environment.LIVE
            ) as client:

                account = await client.accounts.get(self.backup_config['account_id'])
                return float(account.balance) > 0

        except Exception:
            return False

# Monitoring script for automated failover
async def disaster_recovery_monitor():
    """Monitor system and trigger failover if needed."""

    dr_manager = DisasterRecoveryManager(primary_config, backup_config)

    consecutive_failures = 0
    max_failures = 3

    while True:
        try:
            if await dr_manager.check_system_health():
                consecutive_failures = 0
                print("✅ System healthy")
            else:
                consecutive_failures += 1
                print(f"❌ Health check failed ({consecutive_failures}/{max_failures})")

                if consecutive_failures >= max_failures:
                    print("🚨 Initiating disaster recovery failover...")
                    await dr_manager.initiate_failover()
                    break

        except Exception as e:
            print(f"Monitoring error: {e}")

        await asyncio.sleep(30)  # Check every 30 seconds
```

---

## Performance Optimization

### Production Performance Tuning

```python
# src/performance/optimization.py
import asyncio
import uvloop  # High-performance event loop
import gc
from typing import Dict, Any

class ProductionOptimizer:
    """Production performance optimizations."""

    @staticmethod
    def optimize_event_loop():
        """Install high-performance event loop."""

        try:
            # Use uvloop for better performance on Linux
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("✅ uvloop installed for better performance")
        except ImportError:
            print("⚠️ uvloop not available, using default event loop")

    @staticmethod
    def optimize_garbage_collection():
        """Optimize garbage collection for production."""

        # Disable automatic GC for predictable latency
        gc.disable()

        # Set more aggressive thresholds
        gc.set_threshold(700, 10, 10)
        print("✅ Garbage collection optimized")

    @staticmethod
    def optimize_process_settings():
        """Optimize process settings for trading."""

        import os
        import resource

        # Increase file descriptor limit
        try:
            resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))
            print("✅ File descriptor limit increased")
        except Exception as e:
            print(f"⚠️ Could not set file descriptor limit: {e}")

        # Set process priority
        try:
            os.nice(-10)  # Higher priority
            print("✅ Process priority increased")
        except Exception as e:
            print(f"⚠️ Could not set process priority: {e}")

    @classmethod
    def apply_all_optimizations(cls):
        """Apply all production optimizations."""

        print("🚀 Applying production optimizations...")
        cls.optimize_event_loop()
        cls.optimize_garbage_collection()
        cls.optimize_process_settings()
        print("✅ All optimizations applied")

# Apply optimizations at startup
ProductionOptimizer.apply_all_optimizations()
```

---

## Final Production Checklist

### Pre-Deployment Checklist

```bash
#!/bin/bash
# production_checklist.sh

echo "📋 Production Deployment Checklist"
echo "=================================="

checks=(
    "Environment variables configured"
    "SSL certificates installed"
    "Database migrations completed"
    "Backup strategy implemented"
    "Monitoring configured"
    "Alert notifications setup"
    "Security scans passed"
    "Load testing completed"
    "Disaster recovery tested"
    "Documentation updated"
)

for check in "${checks[@]}"; do
    echo "☐ $check"
done

echo ""
echo "⚠️ IMPORTANT REMINDERS:"
echo "• Verify you're using LIVE tokens for production"
echo "• Confirm risk management limits are appropriate"
echo "• Ensure emergency stop procedures are tested"
echo "• Validate all alert channels are working"
echo "• Double-check account permissions and balances"
echo ""
echo "🚨 This system will trade with REAL MONEY"
echo "   Ensure all safety measures are in place!"
```

**Task Complete**: Production deployment guide provides comprehensive infrastructure, security, monitoring, and reliability strategies for deploying FiveTwenty applications to production environments.