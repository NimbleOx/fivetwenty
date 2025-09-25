# How to Handle Connection Failures

**Problem**: Your FiveTwenty connection fails with authentication, network, or API errors.

**Solution**: Implement proper error handling, retry logic, and connection validation for robust trading applications.

---

## Prerequisites

- FiveTwenty installed and configured
- Basic understanding of async/await patterns
- Valid OANDA account and API token

---

## Common Connection Errors

### Authentication Failures

**Error**: `401 Unauthorized` or invalid token errors

```python
import asyncio
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

async def validate_credentials(token: str, environment: Environment):
    """Validate OANDA credentials before use."""

    try:
        async with AsyncClient(token=token, environment=environment) as client:
            # Test connection with basic API call
            accounts = await client.accounts.get_accounts()

            if accounts:
                print("✅ Authentication successful")
                print(f"   Found {len(accounts)} accounts")
                return True
            else:
                print("❌ No accounts found - check permissions")
                return False

    except FiveTwentyError as e:
        if e.status_code == 401:
            print("❌ Authentication failed:")
            print("   • Check API token is correct")
            print("   • Verify token has required permissions")
            print("   • Ensure token hasn't expired")
        else:
            print(f"❌ API Error: {e.message}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

# Test credentials
token = "your-api-token"
is_valid = await validate_credentials(token, Environment.PRACTICE)
```

### Network and Timeout Issues

**Error**: `TimeoutError` or network connectivity problems

```python
import asyncio
from httpx import TimeoutException, ConnectError
from fivetwenty import AsyncClient, Environment

async def robust_connection(token: str, timeout: float = 30.0):
    """Create connection with custom timeout and error handling."""

    try:
        async with AsyncClient(
            token=token,
            environment=Environment.PRACTICE,
            timeout=timeout
        ) as client:

            # Test with basic request
            accounts = await client.accounts.get_accounts()
            print("✅ Connection established successfully")
            return client

    except TimeoutException:
        print("❌ Request timed out:")
        print("   • Check internet connection")
        print("   • Try increasing timeout value")
        print("   • OANDA API may be experiencing issues")
        return None

    except ConnectError as e:
        print("❌ Network connection failed:")
        print(f"   • Error: {e}")
        print("   • Check firewall settings")
        print("   • Verify DNS resolution")
        return None

# Usage with custom timeout
client = await robust_connection("your-token", timeout=60.0)
```

---

## Retry Logic Implementation

### Exponential Backoff Retry

```python
import asyncio
import random
from typing import Optional
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError

class RetryConfig:
    """Configuration for retry logic."""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

async def retry_with_backoff(func, retry_config: RetryConfig, *args, **kwargs):
    """Execute function with exponential backoff retry."""

    for attempt in range(retry_config.max_attempts):
        try:
            result = await func(*args, **kwargs)
            return result

        except (TimeoutException, ConnectError) as e:
            if attempt == retry_config.max_attempts - 1:
                print(f"❌ All {retry_config.max_attempts} attempts failed")
                raise e

            # Calculate delay with jitter
            delay = min(
                retry_config.base_delay * (2 ** attempt),
                retry_config.max_delay
            )
            jitter = random.uniform(0.1, 1.0)
            sleep_time = delay * jitter

            print(f"⏳ Attempt {attempt + 1} failed, retrying in {sleep_time:.1f}s...")
            await asyncio.sleep(sleep_time)

        except FiveTwentyError as e:
            # Don't retry authentication errors
            if e.status_code == 401:
                print("❌ Authentication error - not retrying")
                raise e

            if attempt == retry_config.max_attempts - 1:
                print(f"❌ API error after {retry_config.max_attempts} attempts")
                raise e

            print(f"⏳ API error on attempt {attempt + 1}, retrying...")
            await asyncio.sleep(retry_config.base_delay)

async def get_accounts_with_retry(token: str):
    """Get accounts with retry logic."""

    async def _get_accounts():
        async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
            return await client.accounts.get_accounts()

    retry_config = RetryConfig(max_attempts=3, base_delay=2.0)
    return await retry_with_backoff(_get_accounts, retry_config)

# Usage
try:
    accounts = await get_accounts_with_retry("your-token")
    print(f"✅ Retrieved {len(accounts)} accounts")
except Exception as e:
    print(f"❌ Failed to get accounts: {e}")
```

---

## Connection Health Monitoring

### Connection Healthcheck

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def healthcheck_connection(client: AsyncClient, account_id: str) -> bool:
    """Check if connection is healthy."""

    try:
        # Quick API call to test connection
        account = await client.accounts.get_account(account_id)

        # Check response quality
        if account and hasattr(account, 'balance'):
            print("✅ Connection healthy")
            return True
        else:
            print("⚠️ Connection degraded")
            return False

    except FiveTwentyError as e:
        print(f"❌ Connection unhealthy: {e.message}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

async def monitor_connection_health(client: AsyncClient, account_id: str,
                                 interval: int = 30):
    """Monitor connection health continuously."""

    consecutive_failures = 0
    max_failures = 3

    while True:
        try:
            is_healthy = await healthcheck_connection(client, account_id)

            if is_healthy:
                consecutive_failures = 0
                print(f"💚 Connection OK ({interval}s check)")
            else:
                consecutive_failures += 1
                print(f"⚠️ Health check failed ({consecutive_failures}/{max_failures})")

                if consecutive_failures >= max_failures:
                    print("🚨 Connection lost - requires reconnection")
                    return False

            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("✅ Health monitoring stopped")
            break
        except Exception as e:
            print(f"❌ Health monitoring error: {e}")
            await asyncio.sleep(interval)

# Usage
async def main():
    async with AsyncClient(token="your-token", account_id="your-account-id", environment=Environment.PRACTICE) as client:
        accounts = await client.accounts.get_accounts()
        if accounts:
            # Monitor connection in background
            health_task = asyncio.create_task(
                monitor_connection_health(client, accounts[0].id)
            )

            # Your trading logic here
            await asyncio.sleep(300)  # Run for 5 minutes

            health_task.cancel()

# await main()
```

---

## Environment-Specific Issues

### Practice vs Live Environment

```python
def validate_environment_setup(token: str, expected_env: Environment):
    """Validate token matches expected environment."""

    # Practice tokens typically start with specific patterns
    if expected_env == Environment.PRACTICE:
        if not any(indicator in token.lower() for indicator in ['practice', 'demo', 'sandbox']):
            print("⚠️ Warning: Token may not be for practice environment")
            print("   • Double-check you're using practice token")
            print("   • Live tokens in practice environment will fail")

    elif expected_env == Environment.LIVE:
        print("🚨 LIVE ENVIRONMENT DETECTED")
        print("   • Ensure you intend to use real money")
        print("   • Verify risk management is in place")

    return True

# Environment validation
validate_environment_setup("your-token", Environment.PRACTICE)
```

### SSL/TLS Issues

```python
import ssl
from fivetwenty import AsyncClient, Environment

async def handle_ssl_issues(token: str):
    """Handle SSL/TLS connection issues."""

    try:
        # Default connection
        async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
            accounts = await client.accounts.get_accounts()

    except ssl.SSLError as e:
        print("❌ SSL Error encountered:")
        print(f"   • Error: {e}")
        print("   • Solutions:")
        print("     - Update certificates: pip install --upgrade certifi")
        print("     - Check system time/date")
        print("     - Verify firewall allows HTTPS")

        # Alternative: Create client with custom SSL context (use with caution)
        print("\n⚠️ Attempting connection with relaxed SSL...")
        # Note: Only for debugging - not recommended for production

    except Exception as e:
        print(f"❌ Other connection error: {e}")

# Test SSL connection
await handle_ssl_issues("your-token")
```

---

## Connection Recovery Patterns

### Automatic Reconnection

```python
from fivetwenty import AsyncClient, Environment

class ResilientClient:
    """Client wrapper with automatic reconnection."""

    def __init__(self, token: str, environment: Environment):
        self.token = token
        self.environment = environment
        self.client: Optional[AsyncClient] = None
        self.retry_config = RetryConfig(max_attempts=3, base_delay=1.0)

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        """Establish connection with retry logic."""
        try:
            self.client = AsyncClient(
                token=self.token,
                environment=self.environment,
                timeout=30.0
            )
            await self.client.__aenter__()
            print("✅ Connection established")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise

    async def ensure_connected(self):
        """Ensure client is connected before operations."""
        if not self.client:
            await self.connect()

    async def safe_request(self, func, *args, **kwargs):
        """Execute request with automatic reconnection."""
        try:
            await self.ensure_connected()
            return await func(*args, **kwargs)

        except (TimeoutException, ConnectError):
            print("🔄 Connection lost, attempting reconnection...")
            try:
                await self.connect()
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"❌ Reconnection failed: {e}")
                raise

# Usage
async def resilient_example():
    async with ResilientClient("your-token", Environment.PRACTICE) as client:
        # Safe request with automatic reconnection
        accounts = await client.safe_request(client.client.accounts.list)
        print(f"✅ Found {len(accounts)} accounts")

# await resilient_example()
```

---

## Troubleshooting Checklist

### Quick Diagnostics

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def connection_diagnostics(token: str, environment: Environment):
    """Run comprehensive connection diagnostics."""

    print("🔍 Running OANDA Connection Diagnostics...\n")

    # 1. Token format check
    print("1. Token Format Check:")
    if len(token) < 20:
        print("   ❌ Token appears too short")
    elif '-' not in token:
        print("   ⚠️ Token format may be incorrect")
    else:
        print("   ✅ Token format looks valid")

    # 2. Environment check
    print(f"\n2. Environment: {environment.value}")
    if environment == Environment.LIVE:
        print("   🚨 LIVE environment - real money at risk")
    else:
        print("   ✅ Practice environment - safe for testing")

    # 3. Connection test
    print("\n3. Connection Test:")
    try:
        async with AsyncClient(token=token, environment=environment, timeout=10.0) as client:
            start_time = asyncio.get_event_loop().time()
            accounts = await client.accounts.get_accounts()
            response_time = asyncio.get_event_loop().time() - start_time

            print(f"   ✅ Connection successful ({response_time:.2f}s)")
            print(f"   ✅ Found {len(accounts)} accounts")

            if accounts:
                account = accounts[0]
                print(f"   ✅ Account balance: {account.balance} {account.currency}")

    except FiveTwentyError as e:
        print(f"   ❌ API Error: {e.message}")
        if e.status_code == 401:
            print("   💡 Check token validity and permissions")
        elif e.status_code == 403:
            print("   💡 Check account permissions")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Check internet connection and firewall")

    print("\n📋 Troubleshooting completed")

# Run diagnostics
await connection_diagnostics("your-token", Environment.PRACTICE)
```

---

## Common Fixes

### Token Issues
- **Invalid token**: Generate new token in OANDA account dashboard
- **Expired token**: Tokens don't expire but can be revoked - regenerate
- **Wrong environment**: Practice tokens won't work with live URLs and vice versa

### Network Issues
- **Firewall**: Ensure ports 443 (HTTPS) is open
- **DNS**: Try using 8.8.8.8 if DNS resolution fails
- **Proxy**: Configure proxy settings if behind corporate firewall

### SSL Issues
- **Certificate problems**: Update certificates with `pip install --upgrade certifi`
- **System time**: Ensure system time is accurate for SSL validation

### Rate Limiting
- **429 errors**: Implement delays between requests (100ms minimum)
- **Burst limits**: Use connection pooling and request queuing

**Task Complete**: Connection failure handling guide provides comprehensive troubleshooting and recovery patterns for robust FiveTwenty applications.