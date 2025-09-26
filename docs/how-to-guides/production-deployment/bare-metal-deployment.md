# Bare Metal Deployment

Deploy FiveTwenty applications directly on physical servers with optimized performance, minimal latency, and maximum control over the infrastructure.

## Overview

Bare metal deployment provides direct access to hardware resources without virtualization overhead. This approach offers the lowest possible latency and highest performance for high-frequency trading applications.

**Best for**: High-frequency trading operations, latency-sensitive applications, organizations with dedicated hardware, compliance requirements for data isolation.

## Server Requirements

### Hardware Specifications

#### Minimum Requirements
- **CPU**: Intel Xeon or AMD EPYC, 8+ cores, 3.0+ GHz
- **Memory**: 32GB DDR4-3200 or faster
- **Storage**: 1TB NVMe SSD (primary), 2TB HDD (backup)
- **Network**: 10Gbps Ethernet with low-latency switch
- **Redundancy**: Dual power supplies, RAID 1 for OS

#### Recommended High-Performance Setup
- **CPU**: Intel Xeon Platinum 8280 (28 cores, 2.7GHz) or AMD EPYC 7543 (32 cores, 2.8GHz)
- **Memory**: 128GB DDR4-3200 ECC RAM
- **Storage**: 2TB NVMe SSD RAID 1, 8TB SAS RAID 5 for data
- **Network**: 25Gbps/40Gbps Ethernet with dedicated trading VLAN
- **Additional**: Hardware timestamping NIC, precision time protocol (PTP)

### Operating System Setup

#### Ubuntu 22.04 LTS Configuration

```bash
#!/bin/bash
# server-setup.sh - Initial server configuration

set -e

echo "🖥️ Configuring Ubuntu 22.04 LTS for FiveTwenty trading"

# Update system
apt update && apt upgrade -y

# Install essential packages
apt install -y \
    build-essential \
    curl \
    wget \
    git \
    htop \
    iotop \
    sysstat \
    net-tools \
    tcpdump \
    wireshark-common \
    chrony \
    fail2ban \
    ufw \
    unattended-upgrades \
    postgresql-client \
    redis-tools \
    python3.11 \
    python3.11-dev \
    python3.11-venv \
    python3-pip \
    nginx \
    supervisor

# Configure time synchronization with high precision
systemctl stop systemd-timesyncd
systemctl disable systemd-timesyncd

# Install and configure chrony for precise time sync
cat > /etc/chrony/chrony.conf << 'EOF'
# High-precision time servers
server time.cloudflare.com iburst maxpoll 6
server time.google.com iburst maxpoll 6
server pool.ntp.org iburst maxpoll 6

# Performance optimizations
driftfile /var/lib/chrony/drift
makestep 1.0 3
rtcsync
hwtimestamp *
minsources 2
maxsources 8

# Logging
logdir /var/log/chrony
log measurements statistics tracking
EOF

systemctl enable chronyd
systemctl start chronyd

# Configure CPU performance
echo 'performance' | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make CPU governor persistent
cat > /etc/systemd/system/cpu-performance.service << 'EOF'
[Unit]
Description=Set CPU performance governor
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl enable cpu-performance.service

# Configure kernel parameters for low latency
cat >> /etc/sysctl.conf << 'EOF'

# Network performance tuning
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.rmem_default = 65536
net.core.wmem_default = 65536
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.ipv4.tcp_congestion_control = bbr
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_no_metrics_save = 1
net.ipv4.tcp_moderate_rcvbuf = 1
net.ipv4.tcp_timestamps = 0

# Memory management
vm.swappiness = 1
vm.dirty_ratio = 10
vm.dirty_background_ratio = 5
vm.vfs_cache_pressure = 50

# Process scheduling
kernel.sched_min_granularity_ns = 1000000
kernel.sched_wakeup_granularity_ns = 2000000
kernel.sched_migration_cost_ns = 5000000
EOF

sysctl -p

# Configure GRUB for low latency
sed -i 's/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"/GRUB_CMDLINE_LINUX_DEFAULT="quiet splash intel_idle.max_cstate=0 processor.max_cstate=1 intel_pstate=disable idle=poll isolcpus=2-7 nohz_full=2-7 rcu_nocbs=2-7"/' /etc/default/grub
update-grub

# Configure firewall
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 8080/tcp  # Metrics
ufw allow 8081/tcp  # Health check
ufw allow 443/tcp   # HTTPS
ufw allow 80/tcp    # HTTP
ufw --force enable

echo "✅ Server configuration completed"
echo "⚠️ Reboot required to apply kernel parameters"
```

## Application Deployment

### Directory Structure

```bash
# Create application structure
mkdir -p /opt/fivetwenty-trading/{app,config,logs,data,backups,scripts}
cd /opt/fivetwenty-trading

# Set up directory structure
tree -d /opt/fivetwenty-trading/
```

```text
/opt/fivetwenty-trading/
├── app/                 # Application code
├── config/             # Configuration files
├── logs/               # Application logs
├── data/               # Application data
├── backups/            # Database backups
└── scripts/            # Deployment scripts
```

### Python Environment Setup

```bash
#!/bin/bash
# python-setup.sh - Configure Python environment

cd /opt/fivetwenty-trading

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install application dependencies
cat > requirements.txt << 'EOF'
fivetwenty>=1.0.0
asyncio>=3.4.3
aiohttp>=3.8.0
prometheus-client>=0.16.0
sentry-sdk>=1.20.0
uvloop>=0.17.0
redis>=4.5.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
systemd-python>=235
EOF

pip install -r requirements.txt

# Install performance optimizations
pip install cython numba
```

### Database Setup (PostgreSQL)

```bash
#!/bin/bash
# postgresql-setup.sh - Install and configure PostgreSQL

# Install PostgreSQL 15
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list

apt update
apt install -y postgresql-15 postgresql-contrib-15 postgresql-15-pgaudit

# Configure PostgreSQL for high performance
cp /etc/postgresql/15/main/postgresql.conf /etc/postgresql/15/main/postgresql.conf.backup

cat > /etc/postgresql/15/main/postgresql.conf << 'EOF'
# Performance tuning for trading application
listen_addresses = 'localhost'
port = 5432
max_connections = 200
shared_buffers = 8GB                # 25% of RAM
effective_cache_size = 24GB         # 75% of RAM
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 64MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 32MB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 16
max_parallel_workers_per_gather = 4
max_parallel_workers = 16
max_parallel_maintenance_workers = 4

# Logging
log_destination = 'stderr'
logging_collector = on
log_directory = '/var/log/postgresql'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Security
ssl = on
ssl_cert_file = '/etc/ssl/certs/ssl-cert-snakeoil.pem'
ssl_key_file = '/etc/ssl/private/ssl-cert-snakeoil.key'
EOF

# Create database and user
sudo -u postgres psql << 'EOF'
CREATE DATABASE trading_prod;
CREATE USER trading WITH ENCRYPTED PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE trading_prod TO trading;
\q
EOF

# Start and enable PostgreSQL
systemctl restart postgresql
systemctl enable postgresql

echo "✅ PostgreSQL setup completed"
```

### Redis Setup

```bash
#!/bin/bash
# redis-setup.sh - Install and configure Redis

# Install Redis
apt install -y redis-server

# Configure Redis for high performance
cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

cat > /etc/redis/redis.conf << 'EOF'
# Basic configuration
bind 127.0.0.1 ::1
port 6379
requirepass secure_redis_password_here

# Performance tuning
tcp-keepalive 60
timeout 300
maxmemory 4gb
maxmemory-policy allkeys-lru
maxclients 1000

# Persistence
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Security
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG "CONFIG_9ef6b4e8f7c2d5a1"
EOF

# Create Redis log directory
mkdir -p /var/log/redis
chown redis:redis /var/log/redis

# Start and enable Redis
systemctl restart redis-server
systemctl enable redis-server

echo "✅ Redis setup completed"
```

## Application Configuration

### Production Application Code

```python
# /opt/fivetwenty-trading/app/main.py
import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from typing import Optional
from datetime import datetime
import aiohttp
import uvloop
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from fivetwenty import AsyncClient, Environment
from config import ProductionConfig

# Use high-performance event loop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# Initialize monitoring
REQUEST_COUNT = Counter('oanda_requests_total', 'Total API requests', ['endpoint', 'status'])
REQUEST_LATENCY = Histogram('oanda_request_duration_seconds', 'Request latency', ['endpoint'])
ACTIVE_POSITIONS = Gauge('active_positions_total', 'Active trading positions')
ACCOUNT_BALANCE = Gauge('account_balance', 'Current account balance')
SYSTEM_UPTIME = Gauge('system_uptime_seconds', 'System uptime in seconds')

class BareMetalTradingSystem:
    """Bare metal optimized trading system."""

    def __init__(self, config: ProductionConfig):
        self.config = config
        self.client: Optional[AsyncClient] = None
        self.running = False
        self.start_time = datetime.utcnow()
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
        self.logger.info("Bare metal trading system initialized")

    def _setup_logging(self):
        """Configure high-performance logging."""

        # Ensure logs directory exists
        os.makedirs('/opt/fivetwenty-trading/logs', exist_ok=True)

        # Configure structured logging
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handlers with rotation
        import logging.handlers

        # Main application log
        app_handler = logging.handlers.RotatingFileHandler(
            '/opt/fivetwenty-trading/logs/trading.log',
            maxBytes=100*1024*1024,  # 100MB
            backupCount=10
        )
        app_handler.setFormatter(formatter)

        # Error log
        error_handler = logging.handlers.RotatingFileHandler(
            '/opt/fivetwenty-trading/logs/error.log',
            maxBytes=50*1024*1024,   # 50MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)

        # Console handler for systemd
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.config.log_level))
        root_logger.addHandler(app_handler)
        root_logger.addHandler(error_handler)
        root_logger.addHandler(console_handler)

    async def initialize(self):
        """Initialize all system components."""

        try:
            self.logger.info("Initializing bare metal trading system...")

            # Apply performance optimizations
            self._apply_performance_optimizations()

            # Initialize OANDA client with optimized settings
            self.client = AsyncClient(
                token=self.config.fivetwenty_token,
                environment=self.config.fivetwenty_environment,
                timeout=10.0,  # Reduced timeout for bare metal
                max_connections=20,
                max_connections_per_host=10
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

            self.health_status = {"status": "healthy", "last_check": datetime.utcnow().isoformat()}
            self.logger.info("System initialization completed successfully")

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.health_status = {"status": "unhealthy", "error": str(e), "last_check": datetime.utcnow().isoformat()}
            raise

    def _apply_performance_optimizations(self):
        """Apply bare metal performance optimizations."""

        import os
        import gc

        try:
            # Set process priority
            os.nice(-10)  # Higher priority

            # Optimize garbage collection
            gc.set_threshold(700, 10, 10)

            # Set CPU affinity to isolated cores (2-7 from kernel params)
            if hasattr(os, 'sched_setaffinity'):
                os.sched_setaffinity(0, {2, 3, 4, 5, 6, 7})

            self.logger.info("Performance optimizations applied")

        except Exception as e:
            self.logger.warning(f"Could not apply all performance optimizations: {e}")

    async def _start_monitoring_servers(self):
        """Start high-performance monitoring servers."""

        # Start Prometheus metrics server
        start_http_server(self.config.metrics_port, addr='0.0.0.0')
        self.logger.info(f"Metrics server started on port {self.config.metrics_port}")

        # Start health check server with minimal overhead
        app = aiohttp.web.Application()
        app.router.add_get('/health', self._health_check_handler)
        app.router.add_get('/ready', self._readiness_check_handler)
        app.router.add_get('/metrics', self._metrics_handler)

        runner = aiohttp.web.AppRunner(app, access_log=None)  # Disable access log for performance
        await runner.setup()

        site = aiohttp.web.TCPSite(
            runner,
            '0.0.0.0',
            self.config.health_check_port,
            reuse_address=True,
            reuse_port=True
        )
        await site.start()

        self.logger.info(f"Health check server started on port {self.config.health_check_port}")

    async def _health_check_handler(self, request):
        """Ultra-fast health check endpoint."""

        if self.running and self.client:
            return aiohttp.web.json_response({
                "status": "healthy",
                "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
                "last_check": datetime.utcnow().isoformat()
            })
        else:
            return aiohttp.web.json_response(
                {"status": "unhealthy", "reason": "system not running"},
                status=503
            )

    async def _readiness_check_handler(self, request):
        """Readiness check for load balancers."""

        if self.running and self.client:
            return aiohttp.web.json_response({"status": "ready"})
        else:
            return aiohttp.web.json_response({"status": "not ready"}, status=503)

    async def _metrics_handler(self, request):
        """Expose Prometheus metrics."""

        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

        metrics_data = generate_latest()
        return aiohttp.web.Response(
            body=metrics_data,
            content_type=CONTENT_TYPE_LATEST
        )

    async def start_trading(self):
        """Start the high-frequency trading loop."""

        self.running = True
        self.logger.info("Starting high-frequency trading operations...")

        try:
            # Ultra-tight trading loop for bare metal performance
            while self.running:
                start_time = asyncio.get_event_loop().time()

                try:
                    # Update system metrics
                    await self._update_metrics()

                    # Execute trading logic
                    await self._trading_cycle()

                    # Precise timing for high-frequency operations
                    elapsed = asyncio.get_event_loop().time() - start_time
                    target_cycle_time = 0.1  # 100ms cycle for HFT

                    if elapsed < target_cycle_time:
                        await asyncio.sleep(target_cycle_time - elapsed)

                except Exception as e:
                    self.logger.error(f"Trading cycle error: {e}")
                    # Minimal recovery time for HFT
                    await asyncio.sleep(0.1)

        except Exception as e:
            self.logger.error(f"Critical trading error: {e}")
            await self._send_alert(f"Trading system error: {e}")

        finally:
            self.logger.info("Trading operations stopped")

    async def _update_metrics(self):
        """Update metrics with minimal latency."""

        try:
            # Update uptime
            uptime = (datetime.utcnow() - self.start_time).total_seconds()
            SYSTEM_UPTIME.set(uptime)

            # Batch account info request for efficiency
            account = await self.client.accounts.get_account(
                account_id=self.config.account_id
            )

            # Update financial metrics (convert Decimal to float for Prometheus)
            balance_value = str(account.balance)
            ACCOUNT_BALANCE.set(float(balance_value))
            ACTIVE_POSITIONS.set(account.open_position_count)

            REQUEST_COUNT.labels(endpoint='accounts', status='success').inc()

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='accounts', status='error').inc()
            self.logger.error(f"Metrics update error: {e}")

    async def _trading_cycle(self):
        """Execute one high-frequency trading cycle."""

        try:
            # Your high-frequency trading logic here
            # This is optimized for minimal latency

            # Example: Quick position check
            positions = await self.client.positions.get_positions(
                account_id=self.config.account_id
            )

            # Fast risk check
            total_exposure = sum(
                abs(float(pos.long.units or "0")) + abs(float(pos.short.units or "0"))
                for pos in positions.positions
            )

            if total_exposure > self.config.max_position_size:
                await self._emergency_stop("Position size limit exceeded")

        except Exception as e:
            self.logger.error(f"Trading cycle error: {e}")
            raise

    async def _emergency_stop(self, reason: str):
        """Emergency stop optimized for speed."""

        self.logger.critical(f"EMERGENCY STOP: {reason}")
        self.running = False
        await self._send_alert(f"EMERGENCY STOP: {reason}")

    async def _send_alert(self, message: str):
        """Send high-priority alerts."""

        self.logger.critical(f"ALERT: {message}")

        # Send to systemd journal for immediate notification
        try:
            from systemd import journal
            journal.send(message, PRIORITY=journal.LOG_CRIT, SYSLOG_IDENTIFIER="fivetwenty-trading")
        except ImportError:
            pass

        # Optional: Send to external alerting
        if self.config.slack_webhook_url:
            try:
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "text": f"🚨 CRITICAL: {message}",
                        "channel": "#trading-alerts",
                        "username": "Trading Bot (Bare Metal)"
                    }
                    await asyncio.wait_for(
                        session.post(self.config.slack_webhook_url, json=payload),
                        timeout=5.0
                    )
            except Exception as e:
                self.logger.error(f"Failed to send alert: {e}")

    def setup_signal_handlers(self):
        """Setup optimized signal handlers."""

        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            self.running = False

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGHUP, signal_handler)

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

# Configuration loading
from config import load_production_config

async def main():
    """Main application entry point."""

    system = None

    try:
        # Load configuration
        config = load_production_config()

        # Initialize system
        system = BareMetalTradingSystem(config)
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

### Configuration Management

```python
# /opt/fivetwenty-trading/app/config.py
import os
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from fivetwenty import Environment


@dataclass
class ProductionConfig:
    """Bare metal production configuration."""

    # OANDA API Configuration
    fivetwenty_token: str
    fivetwenty_environment: Environment
    account_id: str

    # Performance Settings
    log_level: str = "INFO"
    max_position_size: int = 1000000  # Higher limits for bare metal
    daily_loss_limit: Decimal = Decimal("5000.0")
    cycle_time_ms: int = 100  # 100ms for HFT

    # Infrastructure Settings
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql://trading:password@localhost/trading_prod"
    metrics_port: int = 8080
    health_check_port: int = 8081

    # Security Settings
    enable_ssl: bool = True
    api_rate_limit: int = 1000  # Higher rate for bare metal
    max_concurrent_connections: int = 50

    # Monitoring & Alerting
    sentry_dsn: Optional[str] = None
    slack_webhook_url: Optional[str] = None
    enable_metrics: bool = True

def load_production_config() -> ProductionConfig:
    """Load production configuration from environment and files."""

    # Load from environment file if it exists
    env_file = "/opt/fivetwenty-trading/config/.env"
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)

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

    return ProductionConfig(
        fivetwenty_token=os.getenv('FIVETWENTY_LIVE_TOKEN'),
        fivetwenty_environment=oanda_env,
        account_id=os.getenv('FIVETWENTY_OANDA_ACCOUNT'),
        log_level=os.getenv('LOG_LEVEL', 'INFO'),
        max_position_size=int(os.getenv('MAX_POSITION_SIZE', '1000000')),
        daily_loss_limit=Decimal(os.getenv('DAILY_LOSS_LIMIT', '5000.0')),
        cycle_time_ms=int(os.getenv('CYCLE_TIME_MS', '100')),
        redis_url=os.getenv('REDIS_URL', 'redis://localhost:6379'),
        database_url=os.getenv('DATABASE_URL', 'postgresql://trading:password@localhost/trading_prod'),
        metrics_port=int(os.getenv('METRICS_PORT', '8080')),
        health_check_port=int(os.getenv('HEALTH_PORT', '8081')),
        sentry_dsn=os.getenv('SENTRY_DSN'),
        slack_webhook_url=os.getenv('SLACK_WEBHOOK_URL')
    )
```

## Systemd Service Configuration

### Service Definition

```ini
# /etc/systemd/system/fivetwenty-trading.service
[Unit]
Description=FiveTwenty Trading System
After=network.target postgresql.service redis-server.service
Wants=postgresql.service redis-server.service
StartLimitIntervalSec=0

[Service]
Type=exec
User=trading
Group=trading
WorkingDirectory=/opt/fivetwenty-trading/app
Environment=PATH=/opt/fivetwenty-trading/venv/bin
ExecStart=/opt/fivetwenty-trading/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=30
Restart=always
RestartSec=5
StartLimitBurst=5

# Performance settings
Nice=-10
IOSchedulingClass=1
IOSchedulingPriority=4
CPUSchedulingPolicy=1
CPUSchedulingPriority=50

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/fivetwenty-trading/logs /opt/fivetwenty-trading/data
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

# Resource limits
LimitNOFILE=65536
LimitNPROC=32768
MemoryAccounting=true
MemoryMax=8G

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=fivetwenty-trading

[Install]
WantedBy=multi-user.target
```

### Service Management Scripts

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/service-management.sh

SERVICE_NAME="fivetwenty-trading"

case "$1" in
    start)
        echo "Starting FiveTwenty Trading Service..."
        systemctl start $SERVICE_NAME
        ;;
    stop)
        echo "Stopping FiveTwenty Trading Service..."
        systemctl stop $SERVICE_NAME
        ;;
    restart)
        echo "Restarting FiveTwenty Trading Service..."
        systemctl restart $SERVICE_NAME
        ;;
    status)
        systemctl status $SERVICE_NAME
        ;;
    logs)
        journalctl -u $SERVICE_NAME -f
        ;;
    enable)
        systemctl enable $SERVICE_NAME
        echo "Service enabled for automatic startup"
        ;;
    disable)
        systemctl disable $SERVICE_NAME
        echo "Service disabled from automatic startup"
        ;;
    reload)
        systemctl reload $SERVICE_NAME
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|enable|disable|reload}"
        exit 1
        ;;
esac
```

## Monitoring and Performance

### System Monitoring

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/system-monitor.sh

echo "=== FiveTwenty Trading System Monitor ==="
echo ""

# Service status
echo "📊 Service Status:"
systemctl is-active fivetwenty-trading
echo ""

# System resources
echo "💻 System Resources:"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%\n", $3/$2 * 100.0)}')"
echo "Disk Usage: $(df -h /opt/fivetwenty-trading | awk 'NR==2{printf "%s\n", $5}')"
echo ""

# Network statistics
echo "🌐 Network Statistics:"
ss -tuln | grep -E ':(8080|8081|5432|6379)'
echo ""

# Application logs (last 10 lines)
echo "📝 Recent Application Logs:"
tail -n 10 /opt/fivetwenty-trading/logs/trading.log
echo ""

# Performance metrics
echo "⚡ Performance Metrics:"
curl -s http://localhost:8080/metrics | grep -E '(account_balance|active_positions|oanda_requests)'
echo ""

# Time synchronization
echo "🕐 Time Synchronization:"
chrony sources -v | head -5
```

### Performance Tuning Script

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/performance-tune.sh

echo "🚀 Applying performance optimizations..."

# CPU governor
echo 'performance' | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Disable CPU idle states for minimal latency
for cpu in /sys/devices/system/cpu/cpu*/cpuidle/state*/disable; do
    echo 1 > $cpu 2>/dev/null || true
done

# Network optimizations
echo 'net.core.busy_read=50' >> /etc/sysctl.conf
echo 'net.core.busy_poll=50' >> /etc/sysctl.conf
sysctl -p

# IRQ affinity (bind network interrupts to dedicated CPUs)
# This would be customized based on your network interface
echo 2 > /proc/irq/24/smp_affinity  # Example: bind to CPU 1

# Transparent huge pages
echo never > /sys/kernel/mm/transparent_hugepage/enabled
echo never > /sys/kernel/mm/transparent_hugepage/defrag

# Process priority
pgrep -f "fivetwenty-trading" | xargs -I {} renice -20 {}

echo "✅ Performance optimizations applied"
```

## Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/backup.sh

BACKUP_DIR="/opt/fivetwenty-trading/backups/$(date +%Y-%m-%d)"
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

echo "📁 Starting backup to $BACKUP_DIR"

# Database backup
echo "🗃️ Backing up PostgreSQL database..."
pg_dump -h localhost -U trading trading_prod | gzip > $BACKUP_DIR/database_$(date +%H%M%S).sql.gz

# Configuration backup
echo "📋 Backing up configuration..."
cp -r /opt/fivetwenty-trading/config $BACKUP_DIR/
cp /etc/systemd/system/fivetwenty-trading.service $BACKUP_DIR/

# Application data backup
echo "💾 Backing up application data..."
tar -czf $BACKUP_DIR/app_data_$(date +%H%M%S).tar.gz /opt/fivetwenty-trading/data/

# Log files backup (last 7 days)
echo "📝 Backing up recent logs..."
find /opt/fivetwenty-trading/logs -name "*.log*" -mtime -7 | tar -czf $BACKUP_DIR/logs_$(date +%H%M%S).tar.gz -T -

# System configuration backup
echo "⚙️ Backing up system configuration..."
tar -czf $BACKUP_DIR/system_config_$(date +%H%M%S).tar.gz \
    /etc/postgresql/15/main/postgresql.conf \
    /etc/redis/redis.conf \
    /etc/systemd/system/fivetwenty-trading.service \
    /etc/nginx/sites-available/fivetwenty-trading 2>/dev/null || true

# Cleanup old backups
echo "🧹 Cleaning up old backups..."
find /opt/fivetwenty-trading/backups -type d -mtime +$RETENTION_DAYS -exec rm -rf {} \;

# Backup size report
echo "📊 Backup completed:"
du -sh $BACKUP_DIR

echo "✅ Backup completed successfully"
```

### Disaster Recovery Script

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/disaster-recovery.sh

BACKUP_DATE=${1:-$(date +%Y-%m-%d)}
BACKUP_DIR="/opt/fivetwenty-trading/backups/$BACKUP_DATE"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "🚨 Starting disaster recovery from $BACKUP_DIR"

# Stop services
echo "🛑 Stopping services..."
systemctl stop fivetwenty-trading
systemctl stop nginx

# Restore database
echo "🗃️ Restoring database..."
DB_BACKUP=$(find $BACKUP_DIR -name "database_*.sql.gz" | head -1)
if [ -f "$DB_BACKUP" ]; then
    dropdb -U postgres trading_prod --if-exists
    createdb -U postgres trading_prod
    gunzip -c $DB_BACKUP | psql -U trading trading_prod
    echo "✅ Database restored"
else
    echo "❌ Database backup not found"
fi

# Restore configuration
echo "📋 Restoring configuration..."
if [ -d "$BACKUP_DIR/config" ]; then
    cp -r $BACKUP_DIR/config/* /opt/fivetwenty-trading/config/
    echo "✅ Configuration restored"
fi

# Restore application data
echo "💾 Restoring application data..."
DATA_BACKUP=$(find $BACKUP_DIR -name "app_data_*.tar.gz" | head -1)
if [ -f "$DATA_BACKUP" ]; then
    tar -xzf $DATA_BACKUP -C /
    echo "✅ Application data restored"
fi

# Restore system configuration
echo "⚙️ Restoring system configuration..."
SYSTEM_BACKUP=$(find $BACKUP_DIR -name "system_config_*.tar.gz" | head -1)
if [ -f "$SYSTEM_BACKUP" ]; then
    tar -xzf $SYSTEM_BACKUP -C /
    echo "✅ System configuration restored"
fi

# Restart services
echo "🔄 Restarting services..."
systemctl daemon-reload
systemctl start postgresql
systemctl start redis-server
systemctl start fivetwenty-trading
systemctl start nginx

# Verify recovery
echo "🔍 Verifying recovery..."
sleep 10
if systemctl is-active --quiet fivetwenty-trading; then
    echo "✅ Disaster recovery completed successfully"
    curl -f http://localhost:8081/health && echo "✅ Health check passed"
else
    echo "❌ Service failed to start after recovery"
    journalctl -u fivetwenty-trading --since "1 minute ago"
fi
```

## Security Hardening

### Security Configuration

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/security-hardening.sh

echo "🔒 Applying security hardening..."

# Create dedicated user
useradd -r -s /bin/bash -d /opt/fivetwenty-trading -c "FiveTwenty Trading User" trading
chown -R trading:trading /opt/fivetwenty-trading

# File permissions
chmod 750 /opt/fivetwenty-trading
chmod 640 /opt/fivetwenty-trading/config/.env
chmod 600 /opt/fivetwenty-trading/config/secrets.*

# SSH hardening
cat >> /etc/ssh/sshd_config << 'EOF'
# FiveTwenty Trading Security
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
ClientAliveInterval 300
ClientAliveCountMax 2
EOF

# Fail2ban configuration
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
filter = sshd
action = iptables[name=SSH, port=ssh, protocol=tcp]
logpath = /var/log/auth.log
maxretry = 3
EOF

# Configure automatic security updates
cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Download-Upgradeable-Packages "1";
APT::Periodic::AutocleanInterval "7";
APT::Periodic::Unattended-Upgrade "1";
EOF

# Restart services
systemctl restart ssh
systemctl restart fail2ban
systemctl enable unattended-upgrades

echo "✅ Security hardening completed"
```

## Deployment Process

### Complete Deployment Script

```bash
#!/bin/bash
# /opt/fivetwenty-trading/scripts/deploy.sh

set -e

VERSION=${1:-latest}
BACKUP_ON_DEPLOY=${2:-true}

echo "🚀 Starting bare metal deployment of FiveTwenty Trading v$VERSION"

# Pre-deployment backup
if [ "$BACKUP_ON_DEPLOY" = "true" ]; then
    echo "💾 Creating pre-deployment backup..."
    /opt/fivetwenty-trading/scripts/backup.sh
fi

# Download and update application
echo "📦 Updating application code..."
cd /opt/fivetwenty-trading

# Backup current version
if [ -d "app" ]; then
    mv app app.backup.$(date +%Y%m%d-%H%M%S)
fi

# Deploy new version (this would be customized for your deployment method)
# Example: git clone, wget, scp, etc.
git clone https://github.com/your-org/fivetwenty-trading-app.git app
cd app

# Install/update dependencies
echo "📚 Installing dependencies..."
source ../venv/bin/activate
pip install -r requirements.txt

# Run database migrations if needed
echo "🗃️ Running database migrations..."
# Your migration commands here

# Configuration validation
echo "📋 Validating configuration..."
python -c "from config import load_production_config; load_production_config()"

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ --quiet

# Update systemd service
echo "⚙️ Updating systemd service..."
systemctl daemon-reload

# Rolling restart
echo "🔄 Performing rolling restart..."
systemctl restart fivetwenty-trading

# Wait for service to be ready
echo "⏳ Waiting for service to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8081/health > /dev/null 2>&1; then
        echo "✅ Service is healthy"
        break
    fi
    echo "⏳ Waiting for service... ($i/30)"
    sleep 5
done

if [ $i -eq 30 ]; then
    echo "❌ Service failed to start"
    echo "📝 Recent logs:"
    journalctl -u fivetwenty-trading --since "2 minutes ago" --no-pager
    exit 1
fi

# Cleanup old backups
echo "🧹 Cleaning up old application backups..."
find /opt/fivetwenty-trading -name "app.backup.*" -mtime +7 -exec rm -rf {} \;

echo "✅ Bare metal deployment completed successfully"
echo "📊 Monitoring URLs:"
echo "   - Health: http://localhost:8081/health"
echo "   - Metrics: http://localhost:8080/metrics"
echo "   - Logs: journalctl -u fivetwenty-trading -f"
```

Bare metal deployment provides maximum performance and control for FiveTwenty trading applications, with optimized configurations for high-frequency trading and minimal latency requirements.