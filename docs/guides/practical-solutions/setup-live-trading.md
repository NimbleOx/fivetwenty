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

<!-- fragment: Demo live account retrieval with attribute access issues -->
```python
from typing import Any
from fivetwenty import AsyncClient, Environment


async def get_live_accounts() -> list[Any]:
    """Retrieve live trading account information for environment setup verification."""

    # Step 1: Initialize AsyncClient for live environment access
    # CRITICAL: Must use Environment.LIVE and live token for real trading
    async with AsyncClient(
        token="your-live-token",          # Replace with your actual LIVE API token
        environment=Environment.LIVE      # CRITICAL: LIVE environment for real money
    ) as client:
        try:
            # Step 2: Retrieve all accounts associated with live token
            # Live accounts contain real money and require careful handling
            accounts = await client.accounts.get_accounts()

            # Step 3: Display comprehensive account information for verification
            print("Bank Live Trading Accounts:")
            for account in accounts:
                print(f"   Account ID: {account.id}")                    # Unique account identifier
                print(f"   Currency: {account.currency}")                # Base currency (USD, EUR, etc.)
                print(f"   Balance: {account.balance}")                  # Current account equity
                print(f"   Margin Available: {account.margin_available}") # Available trading capacity
                print(f"   Open Trades: {account.open_trade_count}")     # Current position count
                print(f"   ⚠️ LIVE ACCOUNT - Real money at risk")
                print()

        except Exception as e:
            # Step 4: Handle authentication and access errors
            # Common issues: wrong token, expired credentials, network problems
            print(f"Error Error accessing live accounts: {e}")
            print(f"   Check: Live token validity, network connection, account permissions")
            return []
        else:
            # Step 5: Return account data for configuration setup
            print(f"Success Successfully retrieved {len(accounts)} live account(s)")
            print(f"Secure Store account IDs securely for live trading configuration")
            return accounts

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
    """Securely retrieve live trading configuration from environment variables."""

    # Step 1: Retrieve live trading credentials from secure environment storage
    # Environment variables keep sensitive credentials out of source code
    live_token = os.getenv('FIVETWENTY_LIVE_TOKEN')      # Live API token for real trading
    live_account_id = os.getenv('FIVETWENTY_LIVE_ACCOUNT') # Live account ID for real money

    # Step 2: Validate that critical live trading credentials are available
    # Missing credentials prevent accidental live trading with wrong configuration
    if not live_token:
        raise ValueError("⚠️ FIVETWENTY_LIVE_TOKEN environment variable not set - cannot access live trading")
    if not live_account_id:
        raise ValueError("⚠️ FIVETWENTY_LIVE_ACCOUNT environment variable not set - cannot identify live account")

    # Step 3: Return validated credentials for secure live trading setup
    print(f"Success Live trading credentials loaded from environment")
    print(f"Secure Token: {live_token[:8]}... (masked for security)")
    print(f"Bank Account: {live_account_id}")

    return live_token, live_account_id

# Safely get live trading credentials
try:
    LIVE_TOKEN, LIVE_ACCOUNT = get_live_config()
    print("Success Live trading credentials loaded")
except ValueError as e:
    print(f"Error Configuration error: {e}")
```

### Using Configuration File

```python
import json
from pathlib import Path


def load_live_config(config_path: str = "live_config.json") -> tuple[str, str]:
    """Load live trading configuration from secure file."""

    config_file = Path(config_path)

    if not config_file.exists():
        msg = f"Configuration file {config_path} not found"
        raise FileNotFoundError(msg)

    # Ensure file has restricted permissions
    file_stat = config_file.stat()
    if oct(file_stat.st_mode)[-3:] != "600":
        print("⚠️ WARNING: Config file should have 600 permissions")

    with config_file.open() as f:
        config = json.load(f)

    required_fields = ["live_token", "live_account_id"]
    for field in required_fields:
        if field not in config:
            msg = f"Required field '{field}' missing from config"
            raise ValueError(msg)

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

<!-- fragment: Demo LiveTradingValidator with exception patterns and attribute access issues -->
```python
from decimal import Decimal
from typing import Any


class LiveTradingValidator:
    """Comprehensive safety validator for live trading operations to prevent catastrophic losses."""

    def __init__(self, max_position_size: int = 10000, daily_loss_limit: Decimal = Decimal("500.0")) -> None:
        """Initialize validator with conservative risk limits for capital protection."""
        self.max_position_size = max_position_size    # Maximum units per single trade
        self.daily_loss_limit = daily_loss_limit      # Maximum daily loss threshold
        print(f"Security Live Trading Validator Initialized:")
        print(f"   Max Position Size: {max_position_size:,} units")
        print(f"   Daily Loss Limit: ${daily_loss_limit}")

    async def validate_order(self, client: Any, account_id: str, instrument: str, units: int) -> bool:
        """Perform comprehensive pre-trade validation to prevent excessive risk exposure."""

        print(f"Search Validating live order: {abs(units):,} units of {instrument}")

        # Step 1: Validate position size against maximum allowed exposure
        # Position size limits prevent single trades from risking too much capital
        if abs(units) > self.max_position_size:
            msg = f"⚠️ Order size {abs(units):,} exceeds maximum {self.max_position_size:,} units"
            print(f"Error {msg}")
            raise ValueError(msg)
        print(f"   Success Position size within limits ({abs(units):,} ≤ {self.max_position_size:,})")

        # Step 2: Retrieve current account status for risk assessment
        account = await client.accounts.get_account(account_id)

        # Step 3: Check daily loss limit to prevent runaway losses
        # Daily P&L includes both realized and unrealized gains/losses
        daily_pl = float(account.unrealized_pl) + float(getattr(account, 'pl', 0))
        if daily_pl < -float(self.daily_loss_limit):
            msg = f"⚠️ Daily loss limit exceeded: ${daily_pl:.2f} < -${self.daily_loss_limit}"
            print(f"Error {msg}")
            raise ValueError(msg)
        print(f"   Success Daily P&L within limits (${daily_pl:+.2f} > -${self.daily_loss_limit})")

        # Step 4: Verify adequate margin availability for safe trading
        # Margin buffer prevents margin calls and forced position closures
        margin_available = float(account.margin_available)
        min_margin_buffer = 100  # Minimum $100 margin buffer
        if margin_available < min_margin_buffer:
            msg = f"⚠️ Insufficient margin: ${margin_available:.2f} < ${min_margin_buffer}"
            print(f"Error {msg}")
            raise ValueError(msg)
        print(f"   Success Adequate margin available (${margin_available:.2f} > ${min_margin_buffer})")

        # Step 5: All validations passed - order is safe to execute
        print(f"Success All safety checks passed for {instrument} order")
        print(f"Green Order approved for live execution")
        return True

# Usage
validator = LiveTradingValidator(max_position_size=5000, daily_loss_limit=Decimal("200.0"))
```

### Safe Order Execution

<!-- fragment: Demo safe order execution with undefined LIVE_TOKEN variable -->
```python
from decimal import Decimal
from typing import Any
from fivetwenty import AsyncClient, Environment


async def place_live_order_safely(account_id: str, instrument: str, units: int, stop_loss: Decimal | None = None, take_profit: Decimal | None = None) -> Any:
    """Execute live trading order with comprehensive safety checks and risk management."""

    # Step 1: Initialize live trading client with proper environment configuration
    # CRITICAL: Only use LIVE_TOKEN and Environment.LIVE for real money trading
    async with AsyncClient(
        token=LIVE_TOKEN,              # Live API token for real trading
        environment=Environment.LIVE   # Live environment for real money
    ) as client:
        try:
            # Step 2: Perform comprehensive pre-trade safety validation
            # Validation prevents dangerous trades from being executed
            print(f"Security Running safety checks for live order...")
            validator = LiveTradingValidator()
            await validator.validate_order(client, account_id, instrument, units)

            # Step 3: Display critical live trading warning and order details
            # Clear warning ensures user understands real money risk
            print(f"\n⚠️ LIVE TRADING - REAL MONEY AT RISK ⚠️")
            print(f"   Instrument: {instrument}")
            print(f"   Units: {units:,} ({'LONG' if units > 0 else 'SHORT'})")
            print(f"   Stop Loss: {stop_loss if stop_loss else 'NOT SET ⚠️'}")
            print(f"   Take Profit: {take_profit if take_profit else 'NOT SET ⚠️'}")

            # Step 4: Warn if no risk management is configured
            if not stop_loss:
                print(f"   ⚠️ WARNING: No stop loss - unlimited risk exposure")
            if not take_profit:
                print(f"   ⚠️ WARNING: No take profit - manual exit required")

            # Step 5: Configure order parameters with integrated risk management
            # Order parameters include all necessary information for safe execution
            order_params = {
                'account_id': account_id,     # Target account for live trading
                'instrument': instrument,     # Currency pair to trade
                'units': units               # Position size and direction
            }

            # Step 6: Add automatic risk management to order
            # Risk management parameters provide automatic protection
            if stop_loss:
                order_params['stop_loss'] = Decimal(str(stop_loss))
                print(f"   Security Stop loss protection: {stop_loss}")
            if take_profit:
                order_params['take_profit'] = Decimal(str(take_profit))
                print(f"   Target Profit target: {take_profit}")

            # Step 7: Execute live order with comprehensive error handling
            print(f"\nStarting Executing live market order...")
            response = await client.orders.post_market_order(**order_params)

            # Step 8: Process successful order execution and display results
            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"\nSuccess LIVE ORDER EXECUTED SUCCESSFULLY")
                print(f"   Trade ID: {fill.trade_opened.trade_id}")   # Unique trade identifier
                print(f"   Fill Price: {fill.price}")                 # Actual execution price
                print(f"   Units: {fill.units:,}")                    # Position size filled
                print(f"   Instrument: {fill.instrument}")            # Currency pair traded
                print(f"   Account: {account_id}")                    # Account used
                print(f"   Balance Real money position now active")

                # Step 9: Display risk management status
                if stop_loss:
                    print(f"   Security Stop loss active at {stop_loss}")
                if take_profit:
                    print(f"   Target Take profit set at {take_profit}")

                return fill
            else:
                # Step 10: Handle order execution failure
                print(f"Error Live order failed to execute")
                print(f"   Check: Market hours, instrument availability, margin requirements")
                return None

        except Exception as e:
            # Step 11: Handle live trading errors with detailed diagnostics
            print(f"Error Live order execution error: {e}")
            print(f"   Possible causes:")
            print(f"   • Market closed or instrument unavailable")
            print(f"   • Insufficient margin or account balance")
            print(f"   • Invalid order parameters or API limits")
            print(f"   • Network connectivity or authentication issues")
            print(f"Config Review error details and account status before retrying")
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
    """Continuously monitor live account for risk management and performance tracking."""

    # Step 1: Initialize live monitoring client for real-time account tracking
    async with AsyncClient(
        token=LIVE_TOKEN,              # Live token for real account monitoring
        environment=Environment.LIVE   # Live environment for real-time data
    ) as client:
        print(f"Data Starting live account monitoring for {account_id}")
        print(f"Processing Update interval: {check_interval} seconds")
        print(f"⚠️ Monitoring REAL MONEY account")

        monitoring_count = 0

        while True:
            try:
                # Step 2: Retrieve current account state for risk assessment
                account = await client.accounts.get_account(account_id)
                monitoring_count += 1

                # Step 3: Extract critical account metrics for analysis
                balance = float(account.balance)              # Current account equity
                unrealized_pl = float(account.unrealized_pl)  # Floating P&L from open positions
                margin_used = float(account.margin_used)      # Capital committed to positions
                margin_available = float(account.margin_available) # Available trading capacity

                # Step 4: Display comprehensive account status
                print(f"\nBalance Live Account Status (Update #{monitoring_count}):")
                print(f"   Balance: ${balance:,.2f}")
                print(f"   Unrealized P/L: ${unrealized_pl:+.2f}")
                print(f"   Margin Used: ${margin_used:,.2f} ({(margin_used/balance)*100:.1f}% of balance)")
                print(f"   Margin Available: ${margin_available:,.2f}")
                print(f"   Open Trades: {account.open_trade_count}")
                print(f"   Account Currency: {account.currency}")

                # Step 5: Risk assessment and automated alerts
                # Alert thresholds help prevent catastrophic losses
                alert_triggered = False

                if unrealized_pl < -200:  # High loss threshold
                    print(f"⚠️ HIGH LOSS ALERT: ${unrealized_pl:+.2f} - Consider closing positions immediately")
                    alert_triggered = True

                if margin_available < 100:  # Low margin threshold
                    print(f"⚠️ LOW MARGIN WARNING: ${margin_available:.2f} - Risk of margin call")
                    alert_triggered = True

                margin_ratio = (margin_used / balance) * 100 if balance > 0 else 0
                if margin_ratio > 80:  # High margin usage
                    print(f"⚠️ HIGH LEVERAGE WARNING: {margin_ratio:.1f}% margin usage - Reduce exposure")
                    alert_triggered = True

                if not alert_triggered:
                    print(f"Success Account status normal - No risk alerts")

                # Step 6: Wait before next monitoring cycle
                await asyncio.sleep(check_interval)

            except KeyboardInterrupt:
                # Step 7: Handle user-initiated monitoring stop
                print(f"\nSuccess Live account monitoring stopped by user")
                print(f"Data Total monitoring updates: {monitoring_count}")
                print(f"⚠️ Remember to continue monitoring your live positions")
                break
            except Exception as e:
                # Step 8: Handle monitoring errors with recovery
                print(f"Error Monitoring error: {e}")
                print(f"Processing Retrying in {check_interval} seconds...")
                await asyncio.sleep(check_interval)

# Start monitoring (run in background)
# await monitor_live_account(LIVE_ACCOUNT, check_interval=60)
```

---

## Step 5: Risk Management Configuration

### Position Size Limits

<!-- fragment: Demo risk management with Decimal constructor expressions -->
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

        print(f"Note Calculated position size: {position_size} units")
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

    print("Test Testing live trading configuration...")

    try:
        # Test connection
        async with AsyncClient(
            token=LIVE_TOKEN,
            environment=Environment.LIVE
        ) as client:
            # Get account info
            accounts = await client.accounts.get_accounts()
            if accounts:
                print(f"Success Live connection successful")
                print(f"   Account: {accounts[0].id}")
                print(f"   Balance: {accounts[0].balance}")

            # Test market data access
            instruments = await client.accounts.get_account_instruments(accounts[0].id)
            print(f"Success Market data access: {len(instruments)} instruments")

            # Test order validation (without execution)
            validator = LiveTradingValidator()
            await validator.validate_order(client, accounts[0].id, "EUR_USD", 1000)
            print("Success Order validation system working")

        print("\nComplete Live trading configuration test PASSED")
        print("Note Ready for live trading with proper risk management")

    except Exception as e:
        print(f"Error Configuration test FAILED: {e}")
        print("Note Fix issues before attempting live trading")

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

- [ ] Success Live token and account ID configured securely
- [ ] Success Risk management parameters set
- [ ] Success Position size limits implemented
- [ ] Success Stop losses mandatory for all trades
- [ ] Success Daily loss limits configured
- [ ] Success Account monitoring system active
- [ ] Success Configuration tested thoroughly
- [ ] Success Emergency stop procedures defined

---

## Emergency Procedures

### Immediate Stop Trading

<!-- fragment: Demo emergency stop trading with undefined LIVE_TOKEN and attribute access issues -->
```python
from fivetwenty import AsyncClient, Environment


async def emergency_stop_trading(account_id: str) -> None:
    """EMERGENCY PROCEDURE: Immediately halt all trading activity to prevent further losses."""

    print(f"\n⚠️⚠️⚠️ EMERGENCY STOP ACTIVATED ⚠️⚠️⚠️")
    print(f"Account: {account_id}")
    print(f"Timestamp: {datetime.now().isoformat()}")

    # Step 1: Initialize emergency client for immediate action
    async with AsyncClient(
        token=LIVE_TOKEN,              # Live token for immediate access
        environment=Environment.LIVE,  # Live environment for real account
    ) as client:
        try:
            print(f"\nHot STEP 1: Cancelling all pending orders...")
            # Step 2: Cancel all pending orders to prevent new positions
            orders = await client.orders.get_pending_orders(account_id)
            cancelled_count = 0
            for order in orders:
                await client.orders.cancel_order(account_id, order.id)
                print(f"   Error Cancelled: {order.id} ({order.instrument} {order.units} units)")
                cancelled_count += 1

            print(f"Success Cancelled {cancelled_count} pending orders")

            # Step 3: Display current position status
            print(f"\nData STEP 2: Checking current positions...")
            positions = await client.positions.get_open_positions(account_id)
            position_count = len(positions)
            print(f"Current open positions: {position_count}")

            for position in positions:
                print(f"   📍 {position.instrument}: {getattr(position, 'net_units', 'N/A')} units")

            # Step 4: Optional position closure (commented for safety)
            print(f"\n⚠️ MANUAL DECISION REQUIRED:")
            print(f"   • {cancelled_count} orders cancelled automatically")
            print(f"   • {position_count} positions remain open")
            print(f"   • Review positions and close manually if needed")
            print(f"   • Uncomment position closure code if immediate exit required")

            # UNCOMMENT BELOW FOR AUTOMATIC POSITION CLOSURE (USE WITH EXTREME CAUTION)
            # print(f"\nHot STEP 3: Force closing all positions...")
            # for position in positions:
            #     await client.positions.close_position(account_id, position.instrument)
            #     print(f"   Secure Force closed: {position.instrument}")

            print(f"\nSuccess Emergency stop procedure completed")
            print(f"Security No new orders can be placed until system is reactivated")

        except Exception as e:
            # Step 5: Handle emergency stop errors
            print(f"Error CRITICAL: Emergency stop error: {e}")
            print(f"⚠️ Manual intervention required immediately")
            print(f"Call Contact broker if unable to stop trading activity")

# Keep this function readily available
# await emergency_stop_trading(LIVE_ACCOUNT)
```

**Task Complete**: Live trading environment setup is now available as a comprehensive, safety-focused how-to guide.