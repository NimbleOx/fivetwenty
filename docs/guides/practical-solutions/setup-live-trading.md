# How to Set Up Live Trading Environment
> ⚠️ **Security Warning**: Never commit real API keys, tokens, or account IDs to version control.
> Use environment variables or secure configuration files that are excluded from git.

**Problem**: You need to transition from practice trading to live trading with real money.

**Solution**: Configure the FiveTwenty for live trading environment with proper safety checks and risk management.

⚠️ **WARNING**: Live trading involves real money and financial risk. Ensure you understand all risks before proceeding.

---

## Prerequisites

- Completed practice trading and strategy testing
- OANDA live trading account with sufficient funds
- Live trading API token (different from practice token)
- Risk management strategy in place

---

## Step 1: Obtain Live Trading Credentials

### Get Live API Token

1. Log into your OANDA live trading account
2. Navigate to "Manage API Access"
3. Generate a new API token for live trading
4. **Store securely** - never commit to version control

### Identify Your Live Account ID

```python
from fivetwenty import AsyncClient, Environment


async def get_live_accounts() -> list[Any]:
    """Get your live trading account information."""

    async with AsyncClient(
        token="your-live-token",  # Use your LIVE token
        environment=Environment.LIVE  # CRITICAL: Use LIVE environment
    ) as client:
        try:
            accounts = await client.accounts.get_accounts()

            print("🏦 Live Trading Accounts:")
            for account in accounts:
                print(f"   Account ID: {account.id}")
                print(f"   Currency: {account.currency}")
                print(f"   Balance: {account.balance}")
                print(f"   Margin Available: {account.margin_available}")
                print(f"   Open Trades: {account.open_trade_count}")
                print()

            return accounts

        except Exception as e:
            print(f"❌ Error accessing live accounts: {e}")
            return []

# Get your live account details
# live_accounts = await get_live_accounts()
```

---

## Step 2: Configure Environment Variables

Set up secure environment variables for live trading:

### Using Environment Variables

```python
import os
from fivetwenty import AsyncClient, Environment

# Set environment variables (add to your .env file or system environment)
# FIVETWENTY_LIVE_TOKEN=your-live-token-here
# FIVETWENTY_LIVE_ACCOUNT=your-account-id-here


def get_live_config() -> tuple[str, str]:
    """Get live trading configuration from environment."""

    live_token = os.getenv('FIVETWENTY_LIVE_TOKEN')
    live_account_id = os.getenv('FIVETWENTY_LIVE_ACCOUNT')

    if not live_token:
        raise ValueError("FIVETWENTY_LIVE_TOKEN environment variable not set")
    if not live_account_id:
        raise ValueError("FIVETWENTY_LIVE_ACCOUNT environment variable not set")

    return live_token, live_account_id

# Safely get live trading credentials
try:
    LIVE_TOKEN, LIVE_ACCOUNT = get_live_config()
    print("✅ Live trading credentials loaded")
except ValueError as e:
    print(f"❌ Configuration error: {e}")
```

### Using Configuration File

```python
import json
from pathlib import Path


def load_live_config(config_path: str = "live_config.json") -> tuple[str, str]:
    """Load live trading configuration from secure file."""

    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file {config_path} not found")

    # Ensure file has restricted permissions
    file_stat = config_file.stat()
    if oct(file_stat.st_mode)[-3:] != "600":
        print("⚠️ WARNING: Config file should have 600 permissions")

    with open(config_file, "r") as f:
        config = json.load(f)

    required_fields = ["live_token", "live_account_id"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Required field '{field}' missing from config")

    return config["live_token"], config["live_account_id"]

# Example config file (live_config.json):
# {
#     "live_token": "your-live-token-here",
#     "live_account_id": "your-live-account-id-here",
#     "max_position_size": 10000,
#     "daily_loss_limit": 500
# }
```

---

## Step 3: Implement Safety Checks

### Pre-Trade Validation

```python
from decimal import Decimal
from typing import Any


class LiveTradingValidator:
    """Safety validator for live trading operations."""

    def __init__(self, max_position_size: int = 10000, daily_loss_limit: Decimal = Decimal("500.0")) -> None:
        self.max_position_size = max_position_size
        self.daily_loss_limit = daily_loss_limit

    async def validate_order(self, client: Any, account_id: str, instrument: str, units: int) -> bool:
        """Validate order before execution in live environment."""

        # Check position size limits
        if abs(units) > self.max_position_size:
            raise ValueError(f"Order size {abs(units)} exceeds maximum {self.max_position_size}")

        # Check daily loss limit
        account = await client.accounts.get_account(account_id)
        daily_pl = float(account.unrealized_pl) + float(account.pl)

        if daily_pl < -self.daily_loss_limit:
            raise ValueError(f"Daily loss limit reached: {daily_pl:.2f}")

        # Check margin requirements
        margin_available = float(account.margin_available)
        if margin_available < 100:  # Minimum margin buffer
            raise ValueError(f"Insufficient margin: {margin_available:.2f}")

        print(f"✅ Order validation passed for {instrument}")
        return True

# Usage
validator = LiveTradingValidator(max_position_size=5000, daily_loss_limit=Decimal("200.0"))
```

### Safe Order Execution

```python
from decimal import Decimal
from typing import Any
from fivetwenty import AsyncClient, Environment


async def place_live_order_safely(account_id: str, instrument: str, units: int, stop_loss: Decimal | None = None, take_profit: Decimal | None = None) -> Any:
    """Place order in live environment with safety checks."""

    async with AsyncClient(
        token=LIVE_TOKEN,
        environment=Environment.LIVE
    ) as client:
        try:
            # Validate order first
            validator = LiveTradingValidator()
            await validator.validate_order(client, account_id, instrument, units)

            # Confirm live environment
            print("🚨 LIVE TRADING - REAL MONEY AT RISK")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units}")
            print(f"   Stop Loss: {stop_loss}")
            print(f"   Take Profit: {take_profit}")

            # Create order parameters
            order_params = {
                'account_id': account_id,
                'instrument': instrument,
                'units': units
            }

            # Add risk management
            if stop_loss:
                order_params['stop_loss'] = Decimal(str(stop_loss))
            if take_profit:
                order_params['take_profit'] = Decimal(str(take_profit))

            # Execute order
            response = await client.orders.post_market_order(**order_params)

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ LIVE ORDER EXECUTED")
                print(f"   Trade ID: {fill.trade_opened.trade_id}")
                print(f"   Fill Price: {fill.price}")
                print(f"   Units: {fill.units}")
                return fill
            else:
                print("❌ Order failed to execute")
                return None

        except Exception as e:
            print(f"❌ Live order error: {e}")
            return None

# Usage with safety checks
# live_fill = await place_live_order_safely(
#     account_id=LIVE_ACCOUNT,
#     instrument="EUR_USD",
#     units=1000,
#     stop_loss=Decimal("1.0900"),
#     take_profit=Decimal("1.1100")
# )
```

---

## Step 4: Set Up Monitoring

### Real-Time Account Monitoring

```python
import asyncio
from fivetwenty import AsyncClient, Environment

async def monitor_live_account(account_id: str, check_interval: int = 30) -> None:
    """Monitor live account for risk management."""

    async with AsyncClient(
        token=LIVE_TOKEN,
        environment=Environment.LIVE
    ) as client:
        print("📊 Starting live account monitoring...")

        while True:
            try:
                account = await client.accounts.get_account(account_id)

                # Key metrics
                balance = account.balance
                unrealized_pl = account.unrealized_pl
                margin_used = account.margin_used
                margin_available = account.margin_available

                print(f"\n💰 Live Account Status:")
                print(f"   Balance: ${balance:,.2f}")
                print(f"   Unrealized P/L: ${unrealized_pl:+.2f}")
                print(f"   Margin Used: ${margin_used:,.2f}")
                print(f"   Margin Available: ${margin_available:,.2f}")
                print(f"   Open Trades: {account.open_trade_count}")

                # Risk alerts
                if unrealized_pl < -200:  # Alert threshold
                    print("🚨 HIGH LOSS ALERT: Consider closing positions")

                if margin_available < 100:  # Low margin alert
                    print("⚠️ LOW MARGIN WARNING: Risk of margin call")

                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                print("\n✅ Monitoring stopped")
                break
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(check_interval)

# Start monitoring (run in background)
# await monitor_live_account(LIVE_ACCOUNT, check_interval=60)
```

---

## Step 5: Risk Management Configuration

### Position Size Limits

```python
from decimal import Decimal


class LiveTradingRiskManager:
    """Comprehensive risk management for live trading."""

    def __init__(self, account_balance: Decimal) -> None:
        self.account_balance = account_balance
        self.max_risk_per_trade = 0.02  # 2% max risk per trade
        self.max_daily_loss = Decimal("0.05")      # 5% max daily loss
        self.max_position_correlation = 0.7  # Max correlation between positions

    def calculate_position_size(self, stop_loss_pips: int, pip_value: Decimal) -> int:
        """Calculate safe position size based on risk parameters."""

        max_loss_amount = self.account_balance * self.max_risk_per_trade
        position_size = int(max_loss_amount / (stop_loss_pips * pip_value))

        # Apply maximum position size cap
        max_position = int(self.account_balance * Decimal("0.1") / pip_value)  # 10% of balance max
        position_size = min(position_size, max_position)

        print(f"💡 Calculated position size: {position_size} units")
        print(f"   Max risk: ${max_loss_amount:.2f}")
        print(f"   Stop loss distance: {stop_loss_pips} pips")

        return position_size

# Usage
risk_manager = LiveTradingRiskManager(account_balance=Decimal("10000"))
safe_position_size = risk_manager.calculate_position_size(stop_loss_pips=50, pip_value=Decimal("1.0"))
```

---

## Testing Live Configuration

### Dry Run Test

```python
from fivetwenty import AsyncClient, Environment

async def test_live_configuration() -> None:
    """Test live trading configuration without placing orders."""

    print("🧪 Testing live trading configuration...")

    try:
        # Test connection
        async with AsyncClient(
            token=LIVE_TOKEN,
            environment=Environment.LIVE
        ) as client:
            # Get account info
            accounts = await client.accounts.get_accounts()
            if accounts:
                print(f"✅ Live connection successful")
                print(f"   Account: {accounts[0].id}")
                print(f"   Balance: {accounts[0].balance}")

            # Test market data access
            instruments = await client.accounts.get_account_instruments(accounts[0].id)
            print(f"✅ Market data access: {len(instruments)} instruments")

            # Test order validation (without execution)
            validator = LiveTradingValidator()
            await validator.validate_order(client, accounts[0].id, "EUR_USD", 1000)
            print("✅ Order validation system working")

        print("\n🎉 Live trading configuration test PASSED")
        print("💡 Ready for live trading with proper risk management")

    except Exception as e:
        print(f"❌ Configuration test FAILED: {e}")
        print("💡 Fix issues before attempting live trading")

# Run configuration test
# await test_live_configuration()
```

---

## Troubleshooting

### Common Issues

**"Authentication failed"**
- Verify you're using the LIVE token (not practice token)
- Check token hasn't expired
- Ensure account has live trading permissions

**"Insufficient funds"**
- Verify account has adequate balance
- Check margin requirements for intended trades
- Consider reducing position sizes

**"Market closed"**
- Forex markets are closed weekends and holidays
- Check market hours for your instruments
- Some instruments have limited trading hours

### Safety Checklist

Before starting live trading:

- [ ] ✅ Live token and account ID configured securely
- [ ] ✅ Risk management parameters set
- [ ] ✅ Position size limits implemented
- [ ] ✅ Stop losses mandatory for all trades
- [ ] ✅ Daily loss limits configured
- [ ] ✅ Account monitoring system active
- [ ] ✅ Configuration tested thoroughly
- [ ] ✅ Emergency stop procedures defined

---

## Emergency Procedures

### Immediate Stop Trading

```python
from fivetwenty import AsyncClient, Environment


async def emergency_stop_trading(account_id: str) -> None:
    """Emergency procedure to stop all trading activity."""

    print("🚨 EMERGENCY STOP ACTIVATED")

    async with AsyncClient(
        token=LIVE_TOKEN,
        environment=Environment.LIVE,
    ) as client:
        try:
            # Cancel all pending orders
            orders = await client.orders.get_pending_orders(account_id)
            for order in orders:
                await client.orders.cancel_order(account_id, order.id)
                print(f"❌ Cancelled order: {order.id}")

            # Close all positions (optional - use with extreme caution)
            # positions = await client.positions.get_open_positions(account_id)
            # for position in positions:
            #     await close_position(account_id, position.instrument)

            print("✅ Emergency stop completed")

        except Exception as e:
            print(f"❌ Emergency stop error: {e}")

# Keep this function readily available
# await emergency_stop_trading(LIVE_ACCOUNT)
```

**Task Complete**: Live trading environment setup is now available as a comprehensive, safety-focused how-to guide.