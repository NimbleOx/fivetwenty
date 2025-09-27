# Practice vs Live Trading Environments

**Problem**: Understanding when and how to use OANDA's practice and live trading environments safely and effectively.

**Solution**: Learn the differences between environments, when to use each, and how to transition from development to production trading.

---

## Prerequisites

- FiveTwenty installed and configured
- Basic understanding of trading concepts
- OANDA account (practice accounts are free)

---

## Environment Overview

OANDA provides two distinct trading environments that serve different purposes in your trading development workflow.

### Practice Environment

The practice environment provides a risk-free trading experience with virtual funds:

**Key Features:**
- $100,000 virtual starting balance
- Real-time market data and spreads
- Complete API functionality
- No real money risk
- Instant account creation

**Best For:**
- Learning OANDA trading concepts
- Testing new trading strategies
- Developing and debugging code
- Experimenting with position sizes
- Algorithm backtesting with live data

```python
from fivetwenty import AsyncClient, Environment

# Practice environment - safe for experimentation
async with AsyncClient(
    token="your-practice-token",
    environment=Environment.PRACTICE
) as client:
    # All trading operations use virtual money
    accounts = await client.accounts.get_accounts()
    print(f"Virtual balance: {accounts[0].balance}")
```

### Live Environment

The live environment executes real trades with actual money:

**Key Features:**
- Real money trading
- Live market execution
- Production-grade infrastructure
- KYC verification required
- Account funding required

**Use Only When:**
- Strategy is thoroughly tested in practice
- Code is production-ready with proper error handling
- Risk management is implemented
- You understand the financial implications

```python
from fivetwenty import AsyncClient, Environment

# Live environment - real money at risk
async def check_live_balance():
    async with AsyncClient(
        token="your-live-token",
        environment=Environment.LIVE
    ) as client:
        # Real money trades - use with extreme caution
        accounts = await client.accounts.get_accounts()
        print(f"Live balance: {accounts[0].balance}")
        return accounts[0].balance
```

---

## Development Workflow

### Phase 1: Development (Practice Only)

Start all development in the practice environment:

```python
import os
from fivetwenty import AsyncClient, Environment

async def development_trading():
    """Development phase - practice environment only."""
    async with AsyncClient(
        token=os.environ["PRACTICE_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:
        # Safe to experiment with any strategy
        account = (await client.accounts.get_accounts())[0]

        # Test with larger positions to see strategy behavior
        test_order = await client.orders.post_market_order(
            account_id=account.id,
            instrument="EUR_USD",
            units=10000  # Safe to test with larger amounts
        )

        print(f"Practice trade executed: {test_order.order_fill_transaction.id}")
```

### Phase 2: Testing (Practice Environment)

Validate your strategy thoroughly:

```python
import os
from fivetwenty import AsyncClient, Environment

async def strategy_validation():
    """Validate strategy in practice environment."""
    async with AsyncClient(
        token=os.environ["PRACTICE_TOKEN"],
        environment=Environment.PRACTICE
    ) as client:
        # Run multiple test scenarios
        test_scenarios = [
            {"instrument": "EUR_USD", "units": 1000},
            {"instrument": "GBP_USD", "units": 2000},
            {"instrument": "USD_JPY", "units": 1500},
        ]

        for scenario in test_scenarios:
            try:
                _order = await client.orders.post_market_order(
                    account_id=client.account_id,
                    **scenario
                )
                print(f"Test successful: {scenario}")
            except Exception as e:
                print(f"Test failed for {scenario}: {e}")
```

### Phase 3: Production (Live Environment)

Transition to live trading with small positions:

```python
import os
from fivetwenty import AsyncClient, Environment

async def production_trading():
    """Production trading - start small."""
    async with AsyncClient(
        token=os.environ["LIVE_TOKEN"],
        environment=Environment.LIVE
    ) as client:
        # Start with minimal position sizes
        conservative_order = await client.orders.post_market_order(
            account_id=client.account_id,
            instrument="EUR_USD",
            units=100,  # Very small initial position
            stop_loss_on_fill={"price": "1.0800"}  # Always use risk management
        )

        print("Live trade executed with risk management")
```

---

## Environment Configuration Patterns

### Environment-Specific Configuration

Use environment variables to manage different environments:

```bash
# .env.practice
FIVETWENTY_OANDA_TOKEN=practice-token-here
FIVETWENTY_OANDA_ACCOUNT=practice-account-id
FIVETWENTY_OANDA_ENVIRONMENT=practice

# .env.live
FIVETWENTY_OANDA_TOKEN=live-token-here
FIVETWENTY_OANDA_ACCOUNT=live-account-id
FIVETWENTY_OANDA_ENVIRONMENT=live
```

### Environment Validation

Always validate your environment configuration:

```python
from fivetwenty import AsyncClient, Environment

async def validate_environment():
    """Validate environment configuration before trading."""
    async with AsyncClient() as client:
        # Check environment
        if client.config.environment == Environment.LIVE:
            print("🚨 LIVE ENVIRONMENT - Real money at risk!")
            print("Ensure all testing is complete")

            # Additional safety checks for live environment
            account = await client.accounts.get_account(client.account_id)
            if float(account.balance) < 1000:
                print("⚠️ Low account balance for live trading")

        else:
            print("✅ Practice environment - safe for testing")

        return client.config.environment
```

---

## Safety Considerations

### Pre-Live Checklist

Before transitioning to live trading:

- [ ] Strategy tested extensively in practice environment
- [ ] Error handling implemented for all scenarios
- [ ] Risk management rules defined and coded
- [ ] Position sizing appropriate for account balance
- [ ] Stop losses and take profits configured
- [ ] Maximum daily/weekly loss limits set
- [ ] Emergency stop procedures defined

### Environment Isolation

Keep environments completely separate:

```python
class TradingEnvironment:
    """Environment-specific trading configuration."""

    def __init__(self, env_type: str):
        if env_type == "practice":
            self.max_position_size = 100000  # Large positions OK for testing
            self.risk_checks = False  # Allow aggressive testing

        elif env_type == "live":
            self.max_position_size = 1000   # Conservative sizing
            self.risk_checks = True         # Strict risk management

    async def create_client(self) -> AsyncClient:
        """Create environment-appropriate client."""
        env = Environment.PRACTICE if self.env_type == "practice" else Environment.LIVE
        return AsyncClient(environment=env)
```

### Monitoring and Alerts

Implement environment-specific monitoring:

```python
async def environment_monitoring():
    """Monitor trading activity by environment."""
    async with AsyncClient() as client:
        account = await client.accounts.get_account(client.account_id)

        if client.config.environment == Environment.LIVE:
            # Strict monitoring for live trading
            if float(account.unrealized_pl) < -500:
                print("🚨 LIVE ACCOUNT: Significant unrealized loss!")
                # Implement emergency stop logic

        else:
            # Relaxed monitoring for practice
            print(f"Practice account P/L: {account.unrealized_pl}")
```

---

## Common Environment Issues

### Token Mismatch

**Problem**: Using practice token with live environment or vice versa.

**Solution**: Validate token/environment combinations:

```python
async def validate_token_environment():
    """Validate token matches intended environment."""
    try:
        async with AsyncClient() as client:
            accounts = await client.accounts.get_accounts()
            print(f"✅ Token valid for {client.config.environment.value} environment")

    except Exception as e:
        if "401" in str(e):
            print("❌ Token/environment mismatch")
            print("Check that practice tokens use PRACTICE environment")
            print("and live tokens use LIVE environment")
```

### Account Access Issues

**Problem**: Token doesn't have access to specified account.

**Solution**: Verify account ownership and permissions:

```python
async def verify_account_access():
    """Verify account access and permissions."""
    async with AsyncClient() as client:
        try:
            account = await client.accounts.get_account(client.account_id)
            print(f"✅ Account access verified: {account.alias}")

        except Exception as e:
            if "403" in str(e):
                print("❌ Account access denied")
                print("Verify account ID matches your OANDA account")
```

---

## Best Practices

### Development Best Practices

1. **Always start with practice** - Never develop directly in live environment
2. **Use realistic position sizes** - Test with sizes you'd actually trade
3. **Test edge cases** - Try invalid instruments, large orders, insufficient margin
4. **Validate error handling** - Ensure your code handles API failures gracefully

### Production Best Practices

1. **Start small** - Begin live trading with minimal position sizes
2. **Monitor closely** - Watch initial live trades carefully
3. **Have exit strategies** - Know how to quickly close all positions
4. **Regular reviews** - Assess performance and adjust strategies

### Security Best Practices

1. **Separate credentials** - Use different tokens for practice and live
2. **Environment validation** - Always confirm which environment you're using
3. **Access controls** - Limit who can access live trading credentials
4. **Regular rotation** - Rotate API tokens periodically

---

## Next Steps

Now that you understand environments:

- **Practice Development**: Start building strategies in practice environment
- **Configuration Management**: Set up proper environment configuration
- **Risk Management**: Implement appropriate risk controls for each environment
- **Monitoring Setup**: Create monitoring for both environments

**Related Guides:**
- [Configuration Patterns](configuration.md) - Advanced environment configuration
- [Best Practices](best-practices.md) - Production trading considerations
- [Security Guidelines](best-practices.md#security-considerations) - Protecting your credentials

**Task Complete**: Environment management provides the foundation for safe trading development and secure production deployment.