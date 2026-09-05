# How to Handle Connection Failures

**Problem**: Your FiveTwenty connection fails with authentication, network, or API errors.

**Solution**: Add error handling, retry logic, and connection validation so failures are caught and recovered instead of crashing your application.

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
```text
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
```text
ValueError: Invalid token format: token must be a non-empty string
```
**Cause:** Token is empty, None, or contains only whitespace.
**Solution:** Verify your token is copied correctly from OANDA without extra spaces:
```python
# Check your token
import os
token = os.environ.get("FIVETWENTY_OANDA_TOKEN", "").strip()
if not token:
    print("Error: Token is empty or missing")
else:
    print(f"Token loaded: {token[:8]}...")
```

**Account ID Mismatch**
```text
ValidationError: Account ID format invalid
```
**Cause:** Account ID doesn't match OANDA's format (XXX-XXX-XXXXXXX-XXX).
**Solution:** Copy the exact account ID from your OANDA account dashboard.

### API Authentication Errors

**HTTP 401 Unauthorized**
```text
HTTPError: 401 Client Error: Unauthorized for url: https://api-fxpractice.oanda.com/v3/accounts
```
**Cause:** Invalid or expired API token.
**Solutions:**
- Generate a new token in your OANDA account settings
- Verify you're using the correct token for the environment (practice vs live)
- Check if your token has expired (OANDA tokens don't expire but can be revoked)

**HTTP 403 Forbidden**
```text
HTTPError: 403 Client Error: Forbidden for url: https://api-fxpractice.oanda.com/v3/accounts/101-001-XXXXXXX-001
```
**Cause:** Token doesn't have access to the specified account.
**Solutions:**
- Verify the account ID belongs to your OANDA login
- Ensure you're using the correct environment (practice tokens can't access live accounts)
- Check if the account is active and not suspended

### Environment Mismatch Errors

**Wrong Environment URL**
```text
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
```text
HTTPError: 429 Client Error: Too Many Requests
```
**Cause:** Exceeded OANDA's rate limits (20 requests per second).
**Solutions:**
- Implement delays between requests
- Use built-in retry mechanisms
- Cache data to reduce API calls

<!-- fragment: Demo comprehensive rate limiting management with intelligent request pacing -->
```python
import asyncio
import time
from typing import List, Any
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def demonstrate_intelligent_rate_limiting(token: str) -> None:
    """Demonstrate intelligent rate limiting management with comprehensive request pacing."""
    print(f"Intelligent Rate Limiting Management Demonstration")

    # Step 1: Initialize rate limiting parameters
    # OANDA allows 20 requests per second, so we use conservative limits
    print(f"\nRate Limiting Configuration:")
    print(f"   OANDA limit: 20 requests/second")
    print(f"   Controls Our limit: 10 requests/second (50% buffer for safety)")
    print(f"   Min delay: 100ms between requests")
    print(f"   Max burst: 5 requests before enforced delay")

    # Step 2: Rate limiting tracking and statistics
    rate_stats = {
        "total_requests": 0,
        "successful_requests": 0,
        "rate_limited_requests": 0,
        "total_delay_time": 0.0,
        "request_times": [],
        "avg_response_time": 0.0
    }

    print(f"\nStarting Rate-Limited Request Demonstration...")

    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        print(f"   Client initialized with practice environment")
        print(f"   Target: 8 sequential account requests with intelligent pacing")

        # Step 3: Execute rate-limited requests with comprehensive monitoring
        for request_number in range(1, 9):  # 8 requests for demonstration
            try:
                # Step 4: Record request start time for performance analysis
                request_start_time = time.perf_counter()
                rate_stats["total_requests"] += 1

                print(f"\n   📤 Request #{request_number}/8:")
                print(f"      🕐 Timestamp: {time.strftime('%H:%M:%S.%f')[:-3]}")

                # Step 5: Execute API request with timing measurement
                accounts = await client.accounts.get_accounts()
                request_end_time = time.perf_counter()
                response_time = request_end_time - request_start_time

                # Step 6: Process successful request and update statistics
                rate_stats["successful_requests"] += 1
                rate_stats["request_times"].append(response_time)

                print(f"      Success: Retrieved {len(accounts)} accounts")
                print(f"      Response time: {response_time:.3f} seconds")
                print(f"      Success: rate: {rate_stats['successful_requests']}/{rate_stats['total_requests']}")

                # Step 7: Intelligent delay calculation based on request patterns
                # Base delay of 100ms + adaptive delay based on response times
                base_delay = 0.100  # 100ms base delay (well under 1/20 second limit)
                adaptive_delay = min(response_time * 0.5, 0.200)  # Up to 200ms adaptive
                total_delay = base_delay + adaptive_delay

                if request_number < 8:  # Don't delay after last request
                    print(f"      Intelligent delay: {total_delay:.3f}s (base: {base_delay:.3f}s + adaptive: {adaptive_delay:.3f}s)")
                    rate_stats["total_delay_time"] += total_delay
                    await asyncio.sleep(total_delay)

            except FiveTwentyError as api_error:
                # Step 8: Handle rate limiting errors with exponential backoff
                if api_error.status == 429:  # Too Many Requests
                    rate_stats["rate_limited_requests"] += 1

                    print(f"      ⚠️ Rate limited (HTTP 429) - implementing recovery")
                    print(f"      Rate limit events: {rate_stats['rate_limited_requests']}")

                    # Exponential backoff for rate limit recovery
                    backoff_delay = 2.0 * (2 ** rate_stats["rate_limited_requests"])  # 2s, 4s, 8s...
                    backoff_delay = min(backoff_delay, 30.0)  # Cap at 30 seconds

                    print(f"      Recovery delay: {backoff_delay:.1f} seconds")
                    print(f"      Note: Strategy: Exponential backoff to allow server recovery")

                    rate_stats["total_delay_time"] += backoff_delay
                    await asyncio.sleep(backoff_delay)

                    # Retry the request after backoff
                    print(f"      Retrying request #{request_number}...")
                    try:
                        accounts = await client.accounts.get_accounts()
                        rate_stats["successful_requests"] += 1
                        print(f"      Retry successful: {len(accounts)} accounts")
                    except Exception as retry_error:
                        print(f"      Error: Retry failed: {retry_error}")
                else:
                    print(f"      Error: API Error: {api_error.message}")

            except Exception as unexpected_error:
                print(f"      Error: Unexpected error: {unexpected_error}")
                print(f"      Note: This may indicate network issues or client problems")

        # Step 9: Calculate and display comprehensive rate limiting statistics
        total_time = rate_stats["total_delay_time"] + sum(rate_stats["request_times"])
        effective_rate = rate_stats["successful_requests"] / total_time if total_time > 0 else 0
        avg_response_time = sum(rate_stats["request_times"]) / len(rate_stats["request_times"]) if rate_stats["request_times"] else 0

        print(f"\nRate Limiting Performance Analysis:")
        print(f"   Total requests attempted: {rate_stats['total_requests']}")
        print(f"   Successful requests: {rate_stats['successful_requests']}")
        print(f"   ⚠️ Rate limited events: {rate_stats['rate_limited_requests']}")
        print(f"   Total delay time: {rate_stats['total_delay_time']:.2f} seconds")
        print(f"   Average response time: {avg_response_time:.3f} seconds")
        print(f"   Effective request rate: {effective_rate:.2f} requests/second")
        print(f"   Success: rate: {rate_stats['successful_requests']/rate_stats['total_requests']*100:.1f}%")

        print(f"\nRate Limiting Best Practices Demonstrated:")
        print(f"   Conservative limits (50% below OANDA's 20 req/sec)")
        print(f"   Intelligent delays based on response times")
        print(f"   Exponential backoff for rate limit recovery")
        print(f"   Comprehensive monitoring and statistics")
        print(f"   Note: Adaptive strategy based on server performance")


# Educational demonstration execution
print(f"Starting Intelligent Rate Limiting Management Tutorial")
try:
    import asyncio
    # Replace with your actual token for testing
    demo_token = "your-practice-token-here"
    asyncio.run(demonstrate_intelligent_rate_limiting(demo_token))
except Exception as e:
    print(f"Rate limiting tutorial error: {e}")
    print(f"Ensure you have a valid practice token for testing")
print(f"Rate limiting management tutorial complete")
print(f"Next: Learn about comprehensive authentication validation patterns")
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

<!-- fragment: Demo comprehensive authentication validation with detailed security analysis -->
```python
import re
import time
from typing import Dict, Any, Tuple
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


async def demonstrate_comprehensive_authentication_validation(token: str, environment: Environment) -> Dict[str, Any]:
    """Demonstrate comprehensive authentication validation with detailed security analysis."""
    print(f"Comprehensive Authentication Validation Demonstration")

    # Step 1: Initialize validation tracking and security analysis
    validation_start_time = time.time()
    validation_results = {
        "token_format_valid": False,
        "authentication_successful": False,
        "account_access_granted": False,
        "environment_match": False,
        "permission_level": "none",
        "security_warnings": [],
        "performance_metrics": {},
        "error_details": None
    }

    print(f"\nAuthentication Validation Scope:")
    print(f"   Token format validation")
    print(f"   OANDA API authentication test")
    print(f"   Account access verification")
    print(f"   Environment compatibility check")
    print(f"   Permission level assessment")
    print(f"   Security analysis and warnings")

    # Step 2: Token format validation with security analysis
    print(f"\nPhase 1: Token Format Validation")

    # Basic token format checks
    if not token or not isinstance(token, str):
        validation_results["security_warnings"].append("Token is empty or not a string")
        print(f"   Error: Token format: Invalid (empty or not string)")
    elif len(token.strip()) != len(token):
        validation_results["security_warnings"].append("Token has leading/trailing whitespace")
        print(f"   ⚠️ Token format: Contains whitespace (will be stripped)")
        token = token.strip()

    # Token length and complexity analysis
    token_length = len(token)
    print(f"   Length Token length: {token_length} characters")

    if token_length < 20:
        validation_results["security_warnings"].append("Token appears too short for OANDA API")
        print(f"   ⚠️ Length warning: Token may be too short (expected >20 chars)")
    elif token_length > 200:
        validation_results["security_warnings"].append("Token appears unusually long")
        print(f"   ⚠️ Length warning: Token unusually long (>200 chars)")
    else:
        validation_results["token_format_valid"] = True
        print(f"   Token length: Acceptable range")

    # Token character composition analysis
    has_alphanumeric = bool(re.search(r'[a-zA-Z0-9]', token))
    has_special_chars = bool(re.search(r'[-_]', token))
    has_dangerous_chars = bool(re.search(r'[\s<>"\']', token))

    print(f"   Character analysis:")
    print(f"      Note: Alphanumeric: {'Present' if has_alphanumeric else 'Missing'}")
    print(f"      Valid special chars: {'Present' if has_special_chars else '⚠️ None found'}")
    print(f"      ⚠️ Dangerous characters: {'Found' if has_dangerous_chars else 'Clean'}")

    if has_dangerous_chars:
        validation_results["security_warnings"].append("Token contains potentially dangerous characters")

    # Environment context analysis
    print(f"\nPhase 2: Environment Context Analysis")
    print(f"   Target environment: {environment.value.upper()}")
    print(f"   API endpoint: {'api-fxtrade.oanda.com' if environment == Environment.LIVE else 'api-fxpractice.oanda.com'}")
    print(f"   Financial risk: {'REAL MONEY' if environment == Environment.LIVE else 'VIRTUAL MONEY'}")

    # Token-environment compatibility heuristics
    token_lower = token.lower()
    practice_indicators = ['practice', 'demo', 'test', 'sandbox']
    live_indicators = ['live', 'prod', 'production']

    token_suggests_practice = any(indicator in token_lower for indicator in practice_indicators)
    token_suggests_live = any(indicator in token_lower for indicator in live_indicators)

    if environment == Environment.PRACTICE and token_suggests_live:
        validation_results["security_warnings"].append("Token suggests live environment but practice selected")
        print(f"   ⚠️ Environment mismatch warning: Token may be for live environment")
    elif environment == Environment.LIVE and token_suggests_practice:
        validation_results["security_warnings"].append("Token suggests practice environment but live selected")
        print(f"   ⚠️ Environment mismatch warning: Token may be for practice environment")
    else:
        validation_results["environment_match"] = True
        print(f"   compatibility: No obvious mismatches detected")

    # Step 3: Live API authentication test with comprehensive error analysis
    print(f"\nPhase 3: Live API Authentication Test")
    print(f"   Attempting OANDA API connection...")
    print(f"   Timeout: 15 seconds for authentication test")
    print(f"   Test method: Account list retrieval")

    authentication_start = time.perf_counter()

    try:
        async with AsyncClient(token=token, environment=environment, timeout=15.0) as client:
            print(f"   Signal Client initialized successfully")
            print(f"   Connection established to OANDA servers")

            # Step 4: Execute authentication test with detailed analysis
            accounts = await client.accounts.get_accounts()
            authentication_time = time.perf_counter() - authentication_start

            validation_results["authentication_successful"] = True
            validation_results["performance_metrics"]["authentication_time"] = authentication_time

            print(f"   Authentication: SUCCESSFUL")
            print(f"   Authentication time: {authentication_time:.3f} seconds")
            print(f"   Accounts discovered: {len(accounts)}")

            if accounts:
                # Step 5: Account access and permission analysis
                validation_results["account_access_granted"] = True

                print(f"\nAccount Phase 4: Account Access and Permission Analysis")

                # Analyze each account for detailed permission assessment
                for i, account in enumerate(accounts, 1):
                    print(f"   Institution Account #{i}:")
                    print(f"      ID ID: {account.id}")
                    print(f"      Note: Alias: {account.alias or 'No alias set'}")
                    print(f"      Balance: {account.balance} {account.currency}")
                    print(f"      Margin available: {account.margin_available}")
                    print(f"      Open trades: {account.open_trade_count}")
                    print(f"      Open positions: {account.open_position_count}")

                # Step 6: Permission level assessment through API capability testing
                print(f"\nPhase 5: Permission Level Assessment")
                primary_account = accounts[0]

                # Test account detail access (basic permission)
                try:
                    account_details = await client.accounts.get_account(primary_account.id)
                    print(f"   Account details: Access granted")
                    validation_results["permission_level"] = "basic"
                except Exception as detail_error:
                    print(f"   Error: Account details: Access denied ({detail_error})")

                # Test order access (intermediate permission)
                try:
                    orders_response = await client.orders.get_orders(primary_account.id)
                    print(f"   Order access: Granted ({len(orders_response['orders'])} orders visible)")
                    if validation_results["permission_level"] == "basic":
                        validation_results["permission_level"] = "intermediate"
                except Exception as order_error:
                    print(f"   ⚠️ Order access: Limited ({order_error})")

                # Test position access (full permission indicator)
                try:
                    positions = await client.positions.get_positions(primary_account.id)
                    print(f"   Position access: Granted ({len(positions)} positions visible)")
                    validation_results["permission_level"] = "full"
                except Exception as position_error:
                    print(f"   ⚠️ Position access: Limited ({position_error})")

            else:
                print(f"   ⚠️ No accounts found - token has authentication but no account access")
                validation_results["security_warnings"].append("Token authenticates but no accounts accessible")

    except FiveTwentyError as api_error:
        # Step 7: Comprehensive API error analysis
        authentication_time = time.perf_counter() - authentication_start
        validation_results["performance_metrics"]["authentication_time"] = authentication_time
        validation_results["error_details"] = {"type": "FiveTwentyError", "code": api_error.status, "message": api_error.message}

        print(f"   Error: Authentication failed after {authentication_time:.3f} seconds")
        print(f"   Error: analysis:")

        if api_error.status == 401:
            print(f"      Blocked HTTP 401 Unauthorized")
            print(f"      Note: Diagnosis: Invalid or expired token")
            print(f"      Solutions:")
            print(f"         • Verify token is copied correctly from OANDA")
            print(f"         • Check token hasn't been revoked")
            print(f"         • Ensure token is for correct environment")
            print(f"         • Generate new token if needed")
            validation_results["security_warnings"].append("Authentication failed - invalid token")

        elif api_error.status == 403:
            print(f"      Blocked HTTP 403 Forbidden")
            print(f"      Note: Diagnosis: Token valid but insufficient permissions")
            print(f"      Solutions:")
            print(f"         • Check account ID matches token's authorized accounts")
            print(f"         • Verify account is active and not suspended")
            print(f"         • Ensure correct environment (practice/live)")
            validation_results["security_warnings"].append("Access forbidden - insufficient permissions")

        elif api_error.status == 429:
            print(f"      ⚠️ HTTP 429 Too Many Requests")
            print(f"      Note: Diagnosis: Rate limit exceeded")
            print(f"      Solutions:")
            print(f"         • Implement request delays (100ms minimum)")
            print(f"         • Use exponential backoff")
            print(f"         • Reduce request frequency")
            validation_results["security_warnings"].append("Rate limit exceeded during validation")

        else:
            print(f"      HTTP {api_error.status} {api_error.message}")
            print(f"      Note: Check OANDA API documentation for specific error")
            validation_results["security_warnings"].append(f"Unexpected API error: {api_error.status}")

    except Exception as unexpected_error:
        # Step 8: Handle network and system errors
        authentication_time = time.perf_counter() - authentication_start
        validation_results["performance_metrics"]["authentication_time"] = authentication_time
        validation_results["error_details"] = {"type": type(unexpected_error).__name__, "message": str(unexpected_error)}

        print(f"   Error: Connection failed after {authentication_time:.3f} seconds")
        print(f"   Error: analysis:")
        print(f"      Error: type: {type(unexpected_error).__name__}")
        print(f"      Details: {str(unexpected_error)}")

        error_msg = str(unexpected_error).lower()
        if "timeout" in error_msg:
            print(f"      Note: Diagnosis: Network timeout")
            print(f"      Solutions: Check internet connectivity, increase timeout")
        elif "ssl" in error_msg or "certificate" in error_msg:
            print(f"      Note: Diagnosis: SSL/TLS certificate issue")
            print(f"      Solutions: Update certificates, check system time")
        elif "dns" in error_msg or "resolve" in error_msg:
            print(f"      Note: Diagnosis: DNS resolution failure")
            print(f"      Solutions: Check DNS settings, try alternate DNS")
        else:
            print(f"      Note: Diagnosis: Network connectivity issue")
            print(f"      Solutions: Check firewall, proxy, internet connection")

        validation_results["security_warnings"].append(f"Network error: {type(unexpected_error).__name__}")

    # Step 9: Comprehensive validation summary and recommendations
    validation_duration = time.time() - validation_start_time
    validation_results["performance_metrics"]["total_validation_time"] = validation_duration

    print(f"\nComprehensive Authentication Validation Summary:")
    print(f"   Total validation time: {validation_duration:.2f} seconds")
    print(f"   Token format valid: {'Success' if validation_results['token_format_valid'] else 'Error'}")
    print(f"   Authentication successful: {'Success' if validation_results['authentication_successful'] else 'Error'}")
    print(f"   Account access granted: {'Success' if validation_results['account_access_granted'] else 'Error'}")
    print(f"   Environment match: {'Success' if validation_results['environment_match'] else '⚠️'}")
    print(f"   Permission level: {validation_results['permission_level'].upper()}")
    print(f"   Security warnings: {len(validation_results['security_warnings'])}")

    # Display security warnings if any
    if validation_results["security_warnings"]:
        print(f"\nSecurity Warnings and Recommendations:")
        for i, warning in enumerate(validation_results["security_warnings"], 1):
            print(f"   {i}. ⚠️ {warning}")

    # Final recommendation
    if validation_results["authentication_successful"] and validation_results["account_access_granted"]:
        if len(validation_results["security_warnings"]) == 0:
            print(f"\nComplete VALIDATION RESULT: EXCELLENT - Ready for production use")
        elif len(validation_results["security_warnings"]) <= 2:
            print(f"\nVALIDATION RESULT: GOOD - Minor warnings to address")
        else:
            print(f"\n⚠️ VALIDATION RESULT: ACCEPTABLE - Review security warnings")
    else:
        print(f"\nError: VALIDATION RESULT: FAILED - Authentication or access issues")

    return validation_results


# Educational demonstration execution
print(f"Starting Comprehensive Authentication Validation Tutorial")
try:
    import asyncio
    # Replace with your actual credentials for testing
    demo_token = "your-practice-token-here"
    demo_environment = Environment.PRACTICE

    results = asyncio.run(demonstrate_comprehensive_authentication_validation(demo_token, demo_environment))

    print(f"\nFinal Validation Metrics:")
    print(f"   Permission level achieved: {results['permission_level']}")
    print(f"   Security warnings: {len(results['security_warnings'])}")
    print(f"   Performance: {results['performance_metrics']}")

except Exception as e:
    print(f"Error: Authentication validation tutorial error: {e}")
    print(f"Note: Ensure you have valid credentials for comprehensive testing")
print(f"Comprehensive authentication validation tutorial complete")
print(f"Education Next: Learn about network timeout handling and resilience patterns")
```

### Network and Timeout Issues

**Error**: `TimeoutError` or network connectivity problems

<!-- fragment: Demo comprehensive network timeout and resilience management -->
```python
import asyncio
import time
from typing import Any, Optional, Dict, List
from httpx import TimeoutException, ConnectError
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError


class NetworkResilienceManager:
    """Comprehensive network resilience manager for robust OANDA connections."""

    def __init__(self, base_timeout: float = 30.0, max_retries: int = 3) -> None:
        """Initialize network resilience manager with adaptive timeout strategies."""
        # Step 1: Initialize resilience parameters and monitoring
        self.base_timeout = base_timeout
        self.max_retries = max_retries
        self.adaptive_timeout = base_timeout
        self.connection_history: List[Dict[str, Any]] = []
        self.network_quality_score = 100  # Start with perfect score

        print(f"Network Resilience Manager Initialized:")
        print(f"   Base timeout: {base_timeout} seconds")
        print(f"   Max retries: {max_retries}")
        print(f"   Network quality score: {self.network_quality_score}/100")
        print(f"   Strategy: Adaptive timeout with intelligent error recovery")

    async def demonstrate_robust_connection_management(self, token: str, environment: Environment = Environment.PRACTICE) -> Optional[Dict[str, Any]]:
        """Demonstrate robust connection management with comprehensive network resilience."""
        print(f"\nRobust Connection Management Demonstration")

        # Step 2: Initialize connection attempt tracking
        connection_start_time = time.perf_counter()
        connection_results = {
            "successful_connection": False,
            "total_attempts": 0,
            "timeout_events": 0,
            "network_errors": 0,
            "api_errors": 0,
            "final_timeout_used": self.adaptive_timeout,
            "connection_quality": "unknown",
            "performance_metrics": {}
        }

        print(f"\nConnection Parameters:")
        print(f"   Environment: {environment.value}")
        print(f"   Initial timeout: {self.adaptive_timeout} seconds")
        print(f"   Max retry attempts: {self.max_retries}")
        print(f"   Network quality baseline: {self.network_quality_score}/100")

        # Step 3: Resilient connection loop with adaptive timeout
        for attempt in range(1, self.max_retries + 1):
            connection_results["total_attempts"] = attempt

            print(f"\nSignal Connection Attempt #{attempt}/{self.max_retries}:")
            print(f"   Using timeout: {self.adaptive_timeout:.1f} seconds")
            print(f"   Network quality: {self.network_quality_score}/100")

            attempt_start_time = time.perf_counter()

            try:
                # Step 4: Create client with adaptive timeout and comprehensive monitoring
                print(f"   Establishing OANDA connection...")

                async with AsyncClient(
                    token=token,
                    environment=environment,
                    timeout=self.adaptive_timeout
                ) as client:

                    # Step 5: Connection validation with performance monitoring
                    print(f"   Settings Validating connection with API test...")
                    validation_start = time.perf_counter()

                    accounts = await client.accounts.get_accounts()
                    validation_time = time.perf_counter() - validation_start
                    total_connection_time = time.perf_counter() - attempt_start_time

                    # Step 6: Successful connection - analyze and update metrics
                    connection_results["successful_connection"] = True
                    connection_results["performance_metrics"] = {
                        "validation_time": validation_time,
                        "total_connection_time": total_connection_time,
                        "attempts_required": attempt,
                        "final_timeout": self.adaptive_timeout
                    }

                    print(f"   Connection established successfully!")
                    print(f"   Validation time: {validation_time:.3f} seconds")
                    print(f"   Total connection time: {total_connection_time:.3f} seconds")
                    print(f"   Accounts discovered: {len(accounts)}")

                    # Step 7: Update network quality based on performance
                    await self._update_network_quality_score(validation_time, True)
                    connection_results["connection_quality"] = self._assess_connection_quality(validation_time)

                    print(f"   Connection quality: {connection_results['connection_quality'].upper()}")
                    print(f"   Updated network score: {self.network_quality_score}/100")

                    # Record successful connection
                    self.connection_history.append({
                        "timestamp": time.time(),
                        "success": True,
                        "attempt": attempt,
                        "timeout_used": self.adaptive_timeout,
                        "response_time": validation_time
                    })

                    return connection_results

            except TimeoutException as timeout_error:
                # Step 8: Handle timeout with adaptive strategy
                connection_results["timeout_events"] += 1
                attempt_time = time.perf_counter() - attempt_start_time

                print(f"   Request timed out after {attempt_time:.1f} seconds")
                print(f"   Timeout event #{connection_results['timeout_events']}")

                # Adaptive timeout strategy
                if attempt < self.max_retries:
                    await self._handle_timeout_adaptively(attempt)
                    print(f"   Next attempt will use {self.adaptive_timeout:.1f}s timeout")

                # Record timeout event
                self.connection_history.append({
                    "timestamp": time.time(),
                    "success": False,
                    "error_type": "timeout",
                    "attempt": attempt,
                    "timeout_used": self.adaptive_timeout
                })

                print(f"   Note: Timeout diagnosis:")
                print(f"      • Network latency may be high")
                print(f"      • OANDA servers may be under load")
                print(f"      • Internet connection may be unstable")
                print(f"      • Firewall may be causing delays")

            except ConnectError as connect_error:
                # Step 9: Handle network connection errors
                connection_results["network_errors"] += 1
                attempt_time = time.perf_counter() - attempt_start_time

                print(f"   Blocked Network connection failed after {attempt_time:.1f} seconds")
                print(f"   Network error #{connection_results['network_errors']}")
                print(f"   Error: details: {str(connect_error)}")

                # Network error diagnosis
                error_msg = str(connect_error).lower()
                print(f"   Note: Network error diagnosis:")
                if "dns" in error_msg or "resolve" in error_msg:
                    print(f"      • DNS resolution failure - check DNS settings")
                    print(f"      • Try alternate DNS servers (8.8.8.8, 1.1.1.1)")
                elif "refused" in error_msg:
                    print(f"      • Connection refused - check firewall settings")
                    print(f"      • Verify HTTPS port 443 is accessible")
                elif "unreachable" in error_msg:
                    print(f"      • Network unreachable - check internet connectivity")
                    print(f"      • Verify routing and network adapter status")
                else:
                    print(f"      • General network connectivity issue")
                    print(f"      • Check proxy, VPN, and firewall configurations")

                # Update network quality for connection errors
                await self._update_network_quality_score(0, False)

            except FiveTwentyError as api_error:
                # Step 10: Handle API-specific errors
                connection_results["api_errors"] += 1
                attempt_time = time.perf_counter() - attempt_start_time

                print(f"   API error after {attempt_time:.1f} seconds")
                print(f"   API error #{connection_results['api_errors']}")
                print(f"   HTTP {api_error.status}: {api_error.message}")

                # API error diagnosis
                if api_error.status == 401:
                    print(f"   Note: Authentication failure - don't retry")
                    break  # No point retrying auth errors
                elif api_error.status == 403:
                    print(f"   Note: Access forbidden - check account permissions")
                    break  # No point retrying access errors
                elif api_error.status >= 500:
                    print(f"   Note: Server error - may be temporary, will retry")
                else:
                    print(f"   Note: Client error - check request parameters")

            # Step 11: Inter-attempt delay with exponential backoff
            if attempt < self.max_retries:
                backoff_delay = min(2.0 * (2 ** (attempt - 1)), 30.0)  # Cap at 30 seconds
                print(f"   Waiting {backoff_delay:.1f} seconds before next attempt...")
                await asyncio.sleep(backoff_delay)

        # Step 12: All attempts failed - comprehensive failure analysis
        total_time = time.perf_counter() - connection_start_time
        connection_results["final_timeout_used"] = self.adaptive_timeout

        print(f"\nError: Connection Failed After All Attempts:")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Attempts made: {connection_results['total_attempts']}")
        print(f"   Timeout events: {connection_results['timeout_events']}")
        print(f"   Blocked Network errors: {connection_results['network_errors']}")
        print(f"   API errors: {connection_results['api_errors']}")
        print(f"   Final network quality: {self.network_quality_score}/100")

        connection_results["connection_quality"] = "failed"
        return connection_results

    async def _handle_timeout_adaptively(self, attempt: int) -> None:
        """Handle timeouts with adaptive timeout adjustment strategy."""
        # Step 13: Adaptive timeout strategy based on attempt and network quality
        if self.network_quality_score < 50:
            # Poor network - increase timeout more aggressively
            timeout_multiplier = 1.5 + (attempt * 0.3)
        elif self.network_quality_score < 80:
            # Moderate network - gradual increase
            timeout_multiplier = 1.2 + (attempt * 0.2)
        else:
            # Good network - conservative increase
            timeout_multiplier = 1.1 + (attempt * 0.1)

        self.adaptive_timeout = min(self.base_timeout * timeout_multiplier, 120.0)  # Cap at 2 minutes

        print(f"   Adaptive timeout adjustment:")
        print(f"      Network quality factor: {self.network_quality_score}/100")
        print(f"      Multiplier applied: {timeout_multiplier:.2f}x")
        print(f"      New timeout: {self.adaptive_timeout:.1f} seconds")

    async def _update_network_quality_score(self, response_time: float, success: bool) -> None:
        """Update network quality score based on connection performance."""
        # Step 14: Dynamic network quality assessment
        if success:
            # Improve score based on response time
            if response_time < 1.0:  # Excellent response
                score_change = min(5, 100 - self.network_quality_score)  # Cap improvement
            elif response_time < 3.0:  # Good response
                score_change = min(2, 100 - self.network_quality_score)
            else:  # Slow but successful
                score_change = min(1, 100 - self.network_quality_score)

            self.network_quality_score = min(100, self.network_quality_score + score_change)
        else:
            # Degrade score for failures
            score_penalty = max(10, self.network_quality_score * 0.1)  # At least 10 point penalty
            self.network_quality_score = max(0, self.network_quality_score - score_penalty)

    def _assess_connection_quality(self, response_time: float) -> str:
        """Assess connection quality based on response time and network score."""
        # Step 15: Connection quality assessment matrix
        if response_time < 0.5 and self.network_quality_score >= 90:
            return "excellent"
        elif response_time < 1.0 and self.network_quality_score >= 70:
            return "good"
        elif response_time < 3.0 and self.network_quality_score >= 50:
            return "moderate"
        elif response_time < 5.0:
            return "poor"
        else:
            return "very_poor"


# Educational demonstration function
async def demonstrate_network_resilience_patterns(token: str) -> None:
    """Demonstrate comprehensive network resilience patterns."""
    print(f"Network Resilience Patterns Demonstration")

    # Step 16: Test different resilience configurations
    resilience_configs = [
        {"name": "Conservative", "timeout": 30.0, "retries": 2},
        {"name": "Balanced", "timeout": 45.0, "retries": 3},
        {"name": "Aggressive", "timeout": 60.0, "retries": 5}
    ]

    for config in resilience_configs:
        print(f"\n{config['name']} Configuration:")
        manager = NetworkResilienceManager(base_timeout=config["timeout"], max_retries=config["retries"])

        result = await manager.demonstrate_robust_connection_management(token)

        if result and result["successful_connection"]:
            print(f"   {config['name']} config: SUCCESS")
            print(f"   Connection time: {result['performance_metrics']['total_connection_time']:.2f}s")
            break  # Stop on first success
        else:
            print(f"   Error: {config['name']} config: FAILED")


# Educational demonstration execution
print(f"Starting Comprehensive Network Resilience Tutorial")
try:
    import asyncio
    # Replace with your actual token for testing
    demo_token = "your-practice-token-here"
    asyncio.run(demonstrate_network_resilience_patterns(demo_token))
except Exception as e:
    print(f"Error: Network resilience tutorial error: {e}")
    print(f"Note: Network resilience requires valid credentials for testing")
print(f"Network resilience and timeout management tutorial complete")
print(f"Education Next: Learn about retry logic and exponential backoff strategies")
```

---

## Retry Logic Implementation

### Exponential Backoff Retry

<!-- fragment: partial retry logic example -->
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
                print(f"Error: All {retry_config.max_attempts} attempts failed")
                raise e

            # Calculate delay with jitter
            delay = min(
                retry_config.base_delay * (2 ** attempt),
                retry_config.max_delay
            )
            jitter = random.uniform(0.1, 1.0)
            sleep_time = delay * jitter

            print(f"Attempt {attempt + 1} failed, retrying in {sleep_time:.1f}s...")
            await asyncio.sleep(sleep_time)

        except FiveTwentyError as e:
            # Don't retry authentication errors
            if e.status == 401:
                print("Error: Authentication error - not retrying")
                raise e

            if attempt == retry_config.max_attempts - 1:
                print(f"Error: API error after {retry_config.max_attempts} attempts")
                raise e

            print(f"API error on attempt {attempt + 1}, retrying...")
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
    print(f"Retrieved {len(accounts)} accounts")
except Exception as e:
    print(f"Error: Failed to get accounts: {e}")
```

---

## Connection Health Monitoring

### Connection Healthcheck

<!-- fragment: partial connection healthcheck example -->
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
            print("Connection healthy")
            return True
        else:
            print("⚠️ Connection degraded")
            return False

    except FiveTwentyError as e:
        print(f"Error: Connection unhealthy: {e.message}")
        return False
    except Exception as e:
        print(f"Error: Connection test failed: {e}")
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
                print(f"Heart Connection OK ({interval}s check)")
            else:
                consecutive_failures += 1
                print(f"⚠️ Health check failed ({consecutive_failures}/{max_failures})")

                if consecutive_failures >= max_failures:
                    print("⚠️ Connection lost - requires reconnection")
                    return False

            await asyncio.sleep(interval)

        except KeyboardInterrupt:
            print("Health monitoring stopped")
            break
        except Exception as e:
            print(f"Error: Health monitoring error: {e}")
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
        print("⚠️ LIVE ENVIRONMENT DETECTED")
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
        print("Error: SSL Error encountered:")
        print(f"   • Error: {e}")
        print("   • Solutions:")
        print("     - Update certificates: uv add --upgrade certifi")
        print("     - Check system time/date")
        print("     - Verify firewall allows HTTPS")

        # Alternative: Create client with custom SSL context (use with caution)
        print("\n⚠️ Attempting connection with relaxed SSL...")
        # Note: Only for debugging - not recommended for production

    except Exception as e:
        print(f"Error: Other connection error: {e}")

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
            print("Connection established")
        except Exception as e:
            print(f"Error: Connection failed: {e}")
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
            print("Connection lost, attempting reconnection...")
            try:
                await self.connect()
                return await func(*args, **kwargs)
            except Exception as e:
                print(f"Error: Reconnection failed: {e}")
                raise

# Usage
async def resilient_example():
    async with ResilientClient("your-token", Environment.PRACTICE) as client:
        # Safe request with automatic reconnection
        accounts = await client.safe_request(client.client.accounts.list)
        print(f"Found {len(accounts)} accounts")

# await resilient_example()
```

---

## Debugging Tools and Diagnostics

### Configuration Checker

<!-- fragment: partial configuration checking example -->
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
        print(f"Error: Missing environment variables: {missing_vars}")
        return False

    # Test client creation
    try:
        client = AsyncClient()
        print(f"Client created successfully")
        print(f"Environment: {client.config.environment.value}")
        print(f"Account: {client.account_id}")
        return True
    except Exception as e:
        print(f"Error: Client creation failed: {e}")
        return False

# Run configuration check
check_configuration()
```

### Connection Test

<!-- fragment: partial connection testing example -->
```python
import asyncio
from fivetwenty import AsyncClient, Environment

async def test_connection():
    """Test actual API connectivity."""

    try:
        async with AsyncClient() as client:
            # Test basic API call
            accounts = await client.accounts.get_accounts()
            print(f"API connection successful: {len(accounts)} accounts")

            # Test account access
            account = await client.accounts.get_account(client.account_id)
            print(f"Account access successful: {account.balance} {account.currency}")

    except Exception as e:
        error_type = type(e).__name__
        print(f"Error: Connection test failed ({error_type}): {e}")

        # Provide specific guidance based on error type
        if "401" in str(e):
            print("Note: Check your API token is valid and not expired")
        elif "403" in str(e):
            print("Note: Verify account ID matches your OANDA account")
        elif "timeout" in str(e).lower():
            print("Note: Check network connectivity and firewall settings")
        elif "ssl" in str(e).lower():
            print("Note: Update SSL certificates or check system time")

# Run connection test
asyncio.run(test_connection())
```

### Full Diagnostics

<!-- fragment: partial connection diagnostics example -->
```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

async def connection_diagnostics(token: str, environment: Environment):
    """Run comprehensive connection diagnostics."""

    print("Running OANDA Connection Diagnostics...\n")

    # 1. Token format check
    print("1. Token Format Check:")
    if len(token) < 20:
        print("   Error: Token appears too short")
    elif '-' not in token:
        print("   ⚠️ Token format may be incorrect")
    else:
        print("   Token format looks valid")

    # 2. Environment check
    print(f"\n2. Environment: {environment.value}")
    if environment == Environment.LIVE:
        print("   ⚠️ LIVE environment - real money at risk")
    else:
        print("   Practice environment - safe for testing")

    # 3. Connection test
    print("\n3. Connection Test:")
    try:
        async with AsyncClient(token=token, environment=environment, timeout=10.0) as client:
            start_time = asyncio.get_event_loop().time()
            accounts = await client.accounts.get_accounts()
            response_time = asyncio.get_event_loop().time() - start_time

            print(f"   Connection successful ({response_time:.2f}s)")
            print(f"   Found {len(accounts)} accounts")

            if accounts:
                account = accounts[0]
                print(f"   Account balance: {account.balance} {account.currency}")

    except FiveTwentyError as e:
        print(f"   Error: API Error: {e.message}")
        if e.status == 401:
            print("   Note: Check token validity and permissions")
        elif e.status == 403:
            print("   Note: Check account permissions")
    except Exception as e:
        print(f"   Error: Connection failed: {e}")
        print("   Note: Check internet connection and firewall")

    print("\nTroubleshooting completed")

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

Your application can now diagnose authentication, network, SSL, and rate-limit failures and recover from them with retry logic.
