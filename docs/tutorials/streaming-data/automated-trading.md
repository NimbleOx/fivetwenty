# Automated Trading Systems

Build complete automated trading engines that integrate streaming data, signal generation, and order management.

---

## Live Trading Engine Architecture

```python
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from fivetwenty import AsyncClient, Environment

@dataclass
class TradingConfig:
    max_position_size: float = 10000
    risk_per_trade: float = 0.02
    max_daily_trades: int = 10
    stop_loss_pct: float = 0.005
    take_profit_pct: float = 0.01

class LiveTradingEngine:
    """Complete automated trading engine with streaming integration."""

    def __init__(self, client: AsyncClient, account_id: str, config: TradingConfig):
        self.client = client
        self.account_id = account_id
        self.config = config
        self.is_running = False
        self.positions = {}
        self.daily_trades = 0
        self.signal_generator = None
        self.risk_manager = None

    async def start_trading(self, instruments: List[str]):
        """Start the automated trading engine."""

        print("Starting automated trading engine...")
        self.is_running = True

        # Initialize components
        await self._initialize_components(instruments)

        # Start concurrent tasks
        await asyncio.gather(
            self._stream_prices(instruments),
            self._monitor_positions(),
            self._daily_reset_task()
        )

    async def _initialize_components(self, instruments: List[str]):
        """Initialize trading components."""

        # Initialize signal generator (from previous tutorial)
        from .signal_generation import LiveSignalGenerator
        self.signal_generator = LiveSignalGenerator()
        self.signal_generator.add_signal_callback(self._handle_trading_signal)

        # Initialize risk manager
        self.risk_manager = RiskManager(self.config)

        # Get current positions
        await self._update_positions()

    async def _stream_prices(self, instruments: List[str]):
        """Stream prices and generate signals."""

        try:
            async for price in self.client.pricing.stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                if self.is_running:
                    bid = float(price.bids[0].price)
                    ask = float(price.asks[0].price)

                    # Process price for signal generation
                    await self.signal_generator.process_price_update(
                        price.instrument, bid, ask
                    )

                    # Update position monitoring
                    await self._update_position_pnl(price.instrument, bid, ask)

        except Exception as e:
            print(f"Price streaming error: {e}")
            if self.is_running:
                await asyncio.sleep(5)
                await self._stream_prices(instruments)  # Restart

    async def _handle_trading_signal(self, signal):
        """Handle trading signals from signal generator."""

        # Check trading conditions
        if not await self._can_trade(signal):
            return

        # Calculate position size
        position_size = await self._calculate_position_size(signal)

        if position_size == 0:
            return

        # Execute trade
        await self._execute_trade(signal, position_size)

    async def _can_trade(self, signal) -> bool:
        """Check if trading is allowed."""

        # Daily trade limit
        if self.daily_trades >= self.config.max_daily_trades:
            return False

        # Risk checks
        if not await self.risk_manager.check_pre_trade_risk(signal):
            return False

        # Position limits
        current_exposure = abs(self.positions.get(signal.instrument, {}).get('units', 0))
        if current_exposure >= self.config.max_position_size:
            return False

        return True

    async def _calculate_position_size(self, signal) -> int:
        """Calculate appropriate position size."""

        # Get account balance
        account = await self.client.accounts.get(self.account_id)
        balance = float(account.balance)

        # Risk-based position sizing
        risk_amount = balance * self.config.risk_per_trade
        stop_distance = self.config.stop_loss_pct

        # Calculate position size based on risk
        if stop_distance > 0:
            base_position_size = risk_amount / stop_distance
        else:
            base_position_size = self.config.max_position_size

        # Adjust for signal strength
        adjusted_size = base_position_size * signal.strength

        # Apply position limits
        max_size = min(adjusted_size, self.config.max_position_size)

        # Convert to units (simplified)
        units = int(max_size)

        # Apply signal direction
        if signal.signal_type.value == "SELL":
            units = -units

        return units

    async def _execute_trade(self, signal, units: int):
        """Execute trading order."""

        try:
            # Place market order
            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=signal.instrument,
                units=units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"TRADE EXECUTED: {signal.instrument} {units} @ {fill.price}")

                # Update position tracking
                await self._update_positions()

                # Place stop loss and take profit
                await self._place_protective_orders(signal.instrument, float(fill.price), units)

                # Update daily trade count
                self.daily_trades += 1

            else:
                print(f"TRADE REJECTED: {signal.instrument}")

        except Exception as e:
            print(f"Trade execution error: {e}")

    async def _place_protective_orders(self, instrument: str, entry_price: float, units: int):
        """Place stop loss and take profit orders."""

        try:
            if units > 0:  # Long position
                stop_price = entry_price * (1 - self.config.stop_loss_pct)
                profit_price = entry_price * (1 + self.config.take_profit_pct)
            else:  # Short position
                stop_price = entry_price * (1 + self.config.stop_loss_pct)
                profit_price = entry_price * (1 - self.config.take_profit_pct)

            # Place stop loss
            await self.client.orders.post_stop_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-units,  # Opposite direction
                price=str(stop_price)
            )

            # Place take profit
            await self.client.orders.post_limit_order(
                account_id=self.account_id,
                instrument=instrument,
                units=-units,  # Opposite direction
                price=str(profit_price)
            )

        except Exception as e:
            print(f"Error placing protective orders: {e}")

    async def _monitor_positions(self):
        """Monitor open positions for management."""

        while self.is_running:
            try:
                await self._update_positions()
                await self._check_position_management()
                await asyncio.sleep(10)  # Check every 10 seconds

            except Exception as e:
                print(f"Position monitoring error: {e}")
                await asyncio.sleep(30)

    async def _update_positions(self):
        """Update current position information."""

        try:
            account = await self.client.accounts.get(self.account_id)

            self.positions = {}

            if hasattr(account, 'positions') and account.positions:
                for position in account.positions:
                    self.positions[position.instrument] = {
                        'units': float(position.long.units) - float(position.short.units),
                        'unrealized_pnl': float(position.unrealized_pl),
                        'avg_price': float(position.long.average_price) if float(position.long.units) > 0 else float(position.short.average_price)
                    }

        except Exception as e:
            print(f"Error updating positions: {e}")

    async def _update_position_pnl(self, instrument: str, bid: float, ask: float):
        """Update position P&L with current prices."""

        if instrument in self.positions:
            position = self.positions[instrument]
            units = position['units']

            if units != 0:
                # Calculate current P&L
                if units > 0:  # Long position
                    current_price = bid  # Use bid for long exit
                else:  # Short position
                    current_price = ask  # Use ask for short exit

                entry_price = position['avg_price']
                pnl = units * (current_price - entry_price)

                position['current_pnl'] = pnl
                position['current_price'] = current_price

    async def _check_position_management(self):
        """Check positions for management actions."""

        for instrument, position in self.positions.items():
            if position['units'] != 0:
                # Check for emergency exit conditions
                current_pnl = position.get('current_pnl', 0)

                # Emergency stop if large loss
                if current_pnl < -1000:  # $1000 loss threshold
                    await self._emergency_close_position(instrument)

    async def _emergency_close_position(self, instrument: str):
        """Emergency position closure."""

        try:
            position = self.positions[instrument]
            close_units = -int(position['units'])  # Opposite direction

            await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=close_units
            )

            print(f"EMERGENCY CLOSE: {instrument}")

        except Exception as e:
            print(f"Emergency close error: {e}")

    async def _daily_reset_task(self):
        """Reset daily counters."""

        while self.is_running:
            # Reset daily trade count at midnight
            await asyncio.sleep(86400)  # 24 hours
            self.daily_trades = 0
            print("Daily trade counter reset")

    def stop_trading(self):
        """Stop the trading engine."""
        self.is_running = False
        print("Trading engine stopped")

class RiskManager:
    """Risk management for automated trading."""

    def __init__(self, config: TradingConfig):
        self.config = config

    async def check_pre_trade_risk(self, signal) -> bool:
        """Perform pre-trade risk checks."""

        # Signal strength check
        if signal.strength < 0.5:
            return False

        # Market hours check (simplified)
        # Implementation would include proper market hours validation

        # Volatility check
        # Implementation would include volatility-based risk control

        return True

# Example usage
async def automated_trading_example():
    """Demonstrate automated trading system."""

    TOKEN = "your-api-token"
    ACCOUNT_ID = "your-account-id"

    config = TradingConfig(
        max_position_size=5000,
        risk_per_trade=0.01,
        max_daily_trades=5
    )

    async with AsyncClient(token=TOKEN, environment=Environment.PRACTICE) as client:
        engine = LiveTradingEngine(client, ACCOUNT_ID, config)

        # Start trading
        instruments = ["EUR_USD", "GBP_USD"]
        await engine.start_trading(instruments)

# Run example
# await automated_trading_example()
```

---

## Next Steps

Continue to [Advanced Streaming Features](advanced-features.md) for sophisticated streaming capabilities.

---

## Related Tutorials

- [Signal Generation](signal-generation.md) - Trading signals
- [Advanced Features](advanced-features.md) - Advanced capabilities
- [Best Practices](best-practices.md) - Production considerations