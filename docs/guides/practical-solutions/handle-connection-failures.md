# How to Handle Connection Failures

**Problem**: Your FiveTwenty connection fails with authentication, network, or API errors.

**Solution**: Implement proper error handling, retry logic, and connection validation for robust trading applications.

---

## Prerequisites

- FiveTwenty installed and configured
- Basic understanding of async/await patterns
- Valid OANDA account and API token

---

## Authentication Troubleshooting

Authentication issues are often the first barrier users encounter. This section provides detailed guidance for diagnosing and resolving authentication-specific problems.

### Configuration Errors

**Missing Environment Variables**
```
ValueError: FIVETWENTY_OANDA_TOKEN environment variable not set
```
**Cause:** The SDK cannot find your API token in environment variables.
**Solution:** Set the required environment variables:
```bash
export FIVETWENTY_OANDA_TOKEN="your-api-token"
export FIVETWENTY_OANDA_ACCOUNT="your-account-id"
export FIVETWENTY_OANDA_ENVIRONMENT="practice"
```

**Invalid Token Format**
```
ValueError: Invalid token format: token must be a non-empty string
```
**Cause:** Token is empty, None, or contains only whitespace.
**Solution:** Verify your token is copied correctly from OANDA without extra spaces:
```python
# Check your token
import os
token = os.environ.get("FIVETWENTY_OANDA_TOKEN", "").strip()
if not token:
    print("❌ Token is empty or missing")
else:
    print(f"✅ Token loaded: {token[:8]}...")
```

**Account ID Mismatch**
```
ValidationError: Account ID format invalid
```
**Cause:** Account ID doesn't match OANDA's format (XXX-XXX-XXXXXXX-XXX).
**Solution:** Copy the exact account ID from your OANDA account dashboard.

### API Authentication Errors

**HTTP 401 Unauthorized**
```
HTTPError: 401 Client Error: Unauthorized for url: https://api-fxpractice.oanda.com/v3/accounts
```
**Cause:** Invalid or expired API token.
**Solutions:**
- Generate a new token in your OANDA account settings
- Verify you're using the correct token for the environment (practice vs live)
- Check if your token has expired (OANDA tokens don't expire but can be revoked)

**HTTP 403 Forbidden**
```
HTTPError: 403 Client Error: Forbidden for url: https://api-fxpractice.oanda.com/v3/accounts/101-001-XXXXXXX-001
```
**Cause:** Token doesn't have access to the specified account.
**Solutions:**
- Verify the account ID belongs to your OANDA login
- Ensure you're using the correct environment (practice tokens can't access live accounts)
- Check if the account is active and not suspended

### Environment Mismatch Errors

**Wrong Environment URL**
```
HTTPError: 404 Client Error: Not Found
```
**Cause:** Using a practice token with live environment or vice versa.
**Solution:** Match your token type to the environment:
```python
from fivetwenty import AsyncClient, Environment

# Practice token → Practice environment
practice_token = "your-practice-token-here"  # Replace with actual practice token
client = AsyncClient(
    token=practice_token,
    environment=Environment.PRACTICE  # Uses api-fxpractice.oanda.com
)

# Live token → Live environment
live_token = "your-live-token-here"  # Replace with actual live token
client = AsyncClient(
    token=live_token,
    environment=Environment.LIVE  # Uses api-fxtrade.oanda.com
)
```

### Rate Limiting Issues

**HTTP 429 Too Many Requests**
```
HTTPError: 429 Client Error: Too Many Requests
```
**Cause:** Exceeded OANDA's rate limits (20 requests per second).
**Solutions:**
- Implement delays between requests
- Use built-in retry mechanisms
- Cache data to reduce API calls

```python
import asyncio
from fivetwenty import AsyncClient, Environment

# Add delays between requests
async def rate_limited_requests(token: str):
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        for i in range(5):
            accounts = await client.accounts.get_accounts()
            print(f"Request {i+1}: {len(accounts)} accounts")
            await asyncio.sleep(0.1)  # 100ms delay
```

### Common Error Patterns

**Pattern: "Works in code but fails in deployment"**
- Check environment variables are set in deployment environment
- Verify container/server has internet access
- Ensure firewall allows HTTPS to OANDA servers

**Pattern: "Worked yesterday but fails today"**
- OANDA may have rotated SSL certificates
- Check for any OANDA service announcements
- Verify system date/time is accurate

**Pattern: "Works in practice but fails in live"**
- Confirm you have a funded live account
- Verify live token permissions
- Check live account is active and not restricted

---

## Common Connection Errors

### Authentication Failures

**Error**: `401 Unauthorized` or invalid token errors

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def validate_credentials(token: str, environment: Environment) -> Any:
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
from typing import Any
from httpx import TimeoutException, ConnectError
from fivetwenty import AsyncClient, Environment


async def robust_connection(token: str, timeout: float = 30.0) -> Any:
    """Create connection with custom timeout and error handling."""

    try:
        async with AsyncClient(
            token=token,
            environment=Environment.PRACTICE,
            timeout=timeout
        ) as client:

            # Test with basic request
            _accounts = await client.accounts.get_accounts()
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
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


class RetryConfig:
    """Configuration for retry logic."""
    def __init__(self, max_attempts: int = 3, base_delay: float = 1.0, max_delay: float = 60.0) -> None:
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay

async def retry_with_backoff(func: Any, retry_config: RetryConfig, *args: Any, **kwargs: Any) -> Any:
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

async def get_accounts_with_retry(token: str) -> Any:
    """Get accounts with retry logic."""

    async def _get_accounts() -> Any:
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

async def monitor_connection_health(client: AsyncClient, account_id: str, interval: int = 30) -> Any:
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
async def main() -> Any:
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
from typing import Any
from fivetwenty import Environment


def validate_environment_setup(token: str, expected_env: Environment) -> Any:
    """Validate token matches expected environment."""

    # Practice tokens typically start with specific patterns
    if expected_env == Environment.PRACTICE:
        if not any(indicator in token.lower() for indicator in ["practice", "demo", "sandbox"]):
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
        print("     - Update certificates: uv add --upgrade certifi")
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

    def __init__(self, token: str, environment: Environment) -> None:
        self.token = token
        self.environment = environment
        self.client: Optional[AsyncClient] = None
        self.retry_config = RetryConfig(max_attempts=3, base_delay=1.0)

    async def __aenter__(self) -> Any:
        await self.connect()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> Any:
        if self.client:
            await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self) -> Any:
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

    async def ensure_connected(self) -> Any:
        """Ensure client is connected before operations."""
        if not self.client:
            await self.connect()

    async def safe_request(self, func: Any, *args: Any, **kwargs: Any) -> Any:
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

## Debugging Tools and Diagnostics

### Configuration Checker

```python
import os
from fivetwenty import AsyncClient

def check_configuration():
    """Comprehensive configuration check."""

    # Check environment variables
    required_vars = [
        "FIVETWENTY_OANDA_TOKEN",
        "FIVETWENTY_OANDA_ACCOUNT",
        "FIVETWENTY_OANDA_ENVIRONMENT"
    ]

    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"❌ Missing environment variables: {missing_vars}")
        return False

    # Test client creation
    try:
        client = AsyncClient()
        print(f"✅ Client created successfully")
        print(f"Environment: {client.config.environment.value}")
        print(f"Account: {client.account_id}")
        return True
    except Exception as e:
        print(f"❌ Client creation failed: {e}")
        return False

# Run configuration check
check_configuration()
```

### Connection Test

```python
import asyncio
from fivetwenty import AsyncClient, Environment

async def test_connection():
    """Test actual API connectivity."""

    try:
        async with AsyncClient() as client:
            # Test basic API call
            accounts = await client.accounts.get_accounts()
            print(f"✅ API connection successful: {len(accounts)} accounts")

            # Test account access
            account = await client.accounts.get_account(client.account_id)
            print(f"✅ Account access successful: {account.balance} {account.currency}")

    except Exception as e:
        error_type = type(e).__name__
        print(f"❌ Connection test failed ({error_type}): {e}")

        # Provide specific guidance based on error type
        if "401" in str(e):
            print("💡 Check your API token is valid and not expired")
        elif "403" in str(e):
            print("💡 Verify account ID matches your OANDA account")
        elif "timeout" in str(e).lower():
            print("💡 Check network connectivity and firewall settings")
        elif "ssl" in str(e).lower():
            print("💡 Update SSL certificates or check system time")

# Run connection test
asyncio.run(test_connection())
```

### Comprehensive Diagnostics

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
- **Certificate problems**: Update certificates with `uv add --upgrade certifi`
- **System time**: Ensure system time is accurate for SSL validation

### Rate Limiting
- **429 errors**: Implement delays between requests (100ms minimum)
- **Burst limits**: Use connection pooling and request queuing

**Task Complete**: Connection failure handling guide provides comprehensive troubleshooting and recovery patterns for robust FiveTwenty applications.