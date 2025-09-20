# Real-time Streaming Data Tutorial

This tutorial teaches you how to work with live market data streams, implement real-time trading systems, and build sophisticated market monitoring applications.

## Prerequisites

- Completed [Basic Trading Tutorial](basic-trading.md)
- Understanding of async programming in Python
- FiveTwenty setup with live data access

## Learning Objectives

By the end of this tutorial, you will:

- ✅ Master real-time data streaming
- ✅ Build live market monitoring systems
- ✅ Implement real-time trading signals
- ✅ Create automated trading systems
- ✅ Handle connection management and error recovery

---

## 1. Streaming Fundamentals

### Understanding Market Data Streams

**Types of Streaming Data:**

- **Price Streams**: Real-time bid/ask prices
- **Account Streams**: Account changes and trade updates
- **Transaction Streams**: Order fills and position changes

**Key Concepts:**

- **Heartbeats**: Keep-alive messages from server
- **Reconnection**: Automatic recovery from disconnections
- **Backpressure**: Handling fast-moving data
- **Stall Detection**: Identifying connection issues

---

## 2. Basic Streaming Implementation

```python
import asyncio
import time
from datetime import datetime, timedelta
from collections import deque
from typing import Dict, List, Optional, Callable
import pandas as pd
import numpy as np

from fivetwenty import AsyncClient, Environment
from fivetwenty.models import StreamingConfiguration, ReconnectionPolicy
from fivetwenty.exceptions import FiveTwentyError, StreamStall

# Configuration
TOKEN = "your-api-token-here"
ENVIRONMENT = Environment.PRACTICE

class BasicStreamProcessor:
    """Basic streaming data processor."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.running = False
        self.price_count = 0
        self.heartbeat_count = 0
        self.start_time = None

    async def start_basic_stream(self, instruments: List[str], duration: int = 60):
        """Start basic price streaming."""

        print(f"🚀 Starting basic stream for {instruments}")
        print(f"Duration: {duration} seconds")

        self.running = True
        self.start_time = time.time()

        try:
            async for event in self.client.pricing.stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                # Check duration
                if time.time() - self.start_time > duration:
                    print(f"\n⏰ Stream completed after {duration} seconds")
                    break

                await self._process_basic_event(event)

                if not self.running:
                    break

        except StreamStall as e:
            print(f"\n🚨 Stream stalled: {e}")
        except FiveTwentyError as e:
            print(f"\n❌ OANDA error: {e.message}")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
        finally:
            self._print_summary()

    async def _process_basic_event(self, event):
        """Process streaming events."""

        if event.type == "PRICE":
            self.price_count += 1

            if event.bids and event.asks:
                bid = float(event.bids[0].price)
                ask = float(event.asks[0].price)
                spread = ask - bid

                # Print every 10th price update
                if self.price_count % 10 == 0:
                    print(f"📈 {event.instrument}: {bid:.5f}/{ask:.5f} "
                          f"(spread: {spread:.5f}) [{self.price_count}]")

        elif event.type == "HEARTBEAT":
            self.heartbeat_count += 1
            if self.heartbeat_count % 5 == 0:
                elapsed = time.time() - self.start_time
                print(f"💓 Heartbeat #{self.heartbeat_count} "
                      f"(elapsed: {elapsed:.1f}s)")

    def stop_stream(self):
        """Stop the streaming process."""
        self.running = False
        print("🛑 Stopping stream...")

    def _print_summary(self):
        """Print streaming summary."""
        elapsed = time.time() - self.start_time if self.start_time else 0

        print(f"\n📊 Streaming Summary:")
        print(f"   Duration: {elapsed:.1f} seconds")
        print(f"   Price updates: {self.price_count:,}")
        print(f"   Heartbeats: {self.heartbeat_count}")
        if elapsed > 0:
            print(f"   Rate: {self.price_count/elapsed:.2f} updates/second")

# Demo basic streaming
async def demo_basic_streaming(account_id: str):
    """Demonstrate basic streaming functionality."""

    if not account_id:
        print("❌ No account ID")
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        processor = BasicStreamProcessor(client, account_id)

        # Stream EUR/USD and GBP/USD for 30 seconds
        await processor.start_basic_stream(["EUR_USD", "GBP_USD"], duration=30)

        return processor
```

---

## 3. Advanced Streaming with Data Management

### Real-time Data Buffer System

```python
from fivetwenty import AsyncClient, Environment

class RealTimeDataManager:
    """Advanced real-time data management system."""

    def __init__(self, buffer_size: int = 1000):
        self.buffer_size = buffer_size
        self.price_buffers = {}
        self.statistics = {}
        self.callbacks = {}
        self.last_update = {}

    def register_instrument(self, instrument: str):
        """Register an instrument for data tracking."""

        if instrument not in self.price_buffers:
            self.price_buffers[instrument] = {
                'prices': deque(maxlen=self.buffer_size),
                'timestamps': deque(maxlen=self.buffer_size),
                'bids': deque(maxlen=self.buffer_size),
                'asks': deque(maxlen=self.buffer_size),
                'spreads': deque(maxlen=self.buffer_size)
            }

            self.statistics[instrument] = {
                'count': 0,
                'first_price': None,
                'last_price': None,
                'min_price': float('inf'),
                'max_price': float('-inf'),
                'price_sum': 0.0,
                'squared_sum': 0.0
            }

            self.callbacks[instrument] = []
            print(f"📊 Registered {instrument} for data tracking")

    def add_price_update(self, instrument: str, bid: float, ask: float, timestamp: datetime):
        """Add a price update to the buffer."""

        if instrument not in self.price_buffers:
            self.register_instrument(instrument)

        mid_price = (bid + ask) / 2
        spread = ask - bid

        # Add to buffers
        buffer = self.price_buffers[instrument]
        buffer['prices'].append(mid_price)
        buffer['timestamps'].append(timestamp)
        buffer['bids'].append(bid)
        buffer['asks'].append(ask)
        buffer['spreads'].append(spread)

        # Update statistics
        stats = self.statistics[instrument]
        stats['count'] += 1
        stats['last_price'] = mid_price
        stats['min_price'] = min(stats['min_price'], mid_price)
        stats['max_price'] = max(stats['max_price'], mid_price)
        stats['price_sum'] += mid_price
        stats['squared_sum'] += mid_price ** 2

        if stats['first_price'] is None:
            stats['first_price'] = mid_price

        self.last_update[instrument] = timestamp

        # Trigger callbacks
        for callback in self.callbacks[instrument]:
            try:
                callback(instrument, {
                    'bid': bid,
                    'ask': ask,
                    'mid': mid_price,
                    'spread': spread,
                    'timestamp': timestamp
                })
            except Exception as e:
                print(f"❌ Callback error for {instrument}: {e}")

    def register_callback(self, instrument: str, callback: Callable):
        """Register a callback for price updates."""

        if instrument not in self.callbacks:
            self.register_instrument(instrument)

        self.callbacks[instrument].append(callback)
        print(f"📞 Registered callback for {instrument}")

    def get_recent_prices(self, instrument: str, count: int = 100) -> pd.DataFrame:
        """Get recent price data as DataFrame."""

        if instrument not in self.price_buffers:
            return pd.DataFrame()

        buffer = self.price_buffers[instrument]

        # Get last 'count' entries
        prices = list(buffer['prices'])[-count:]
        timestamps = list(buffer['timestamps'])[-count:]
        bids = list(buffer['bids'])[-count:]
        asks = list(buffer['asks'])[-count:]
        spreads = list(buffer['spreads'])[-count:]

        if not prices:
            return pd.DataFrame()

        df = pd.DataFrame({
            'timestamp': timestamps,
            'bid': bids,
            'ask': asks,
            'mid': prices,
            'spread': spreads
        })

        df.set_index('timestamp', inplace=True)
        return df

    def calculate_statistics(self, instrument: str) -> Dict:
        """Calculate real-time statistics for an instrument."""

        if instrument not in self.statistics:
            return {}

        stats = self.statistics[instrument].copy()

        if stats['count'] > 0:
            # Calculate mean and standard deviation
            mean_price = stats['price_sum'] / stats['count']
            variance = (stats['squared_sum'] / stats['count']) - (mean_price ** 2)
            std_dev = np.sqrt(max(0, variance))

            # Calculate price change
            price_change = (stats['last_price'] - stats['first_price']) if stats['first_price'] else 0
            price_change_pct = (price_change / stats['first_price'] * 100) if stats['first_price'] else 0

            # Calculate recent volatility (if enough data)
            recent_volatility = 0
            if instrument in self.price_buffers and len(self.price_buffers[instrument]['prices']) > 10:
                recent_prices = list(self.price_buffers[instrument]['prices'])[-20:]
                if len(recent_prices) > 1:
                    returns = [((recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1])
                              for i in range(1, len(recent_prices))]
                    recent_volatility = np.std(returns) * 100 if returns else 0

            stats.update({
                'mean_price': mean_price,
                'std_dev': std_dev,
                'price_change': price_change,
                'price_change_pct': price_change_pct,
                'price_range': stats['max_price'] - stats['min_price'],
                'recent_volatility': recent_volatility,
                'last_update': self.last_update.get(instrument)
            })

        return stats

    def print_statistics_summary(self):
        """Print statistics summary for all instruments."""

        print(f"\n📊 Real-time Statistics Summary:")
        print("-" * 80)
        print(f"{'Instrument':<12} {'Count':<8} {'Price':<10} {'Change':<10} {'Range':<10} {'Vol %':<8}")
        print("-" * 80)

        for instrument in self.statistics:
            stats = self.calculate_statistics(instrument)

            if stats.get('count', 0) > 0:
                print(f"{instrument:<12} {stats['count']:<8,} "
                      f"{stats['last_price']:<10.5f} "
                      f"{stats['price_change_pct']:<+10.3f}% "
                      f"{stats['price_range']:<10.5f} "
                      f"{stats['recent_volatility']:<8.3f}%")

# Demo advanced data management
async def demo_advanced_data_management(account_id: str):
    """Demonstrate advanced data management."""

    if not account_id:
        return

    # Create data manager
    data_manager = RealTimeDataManager(buffer_size=500)

    # Register callback for monitoring
    def price_monitor(instrument: str, price_data: Dict):
        stats = data_manager.calculate_statistics(instrument)
        if stats.get('count', 0) % 50 == 0 and stats.get('count', 0) > 0:
            print(f"📊 {instrument}: {stats['count']} updates, "
                  f"Price: {stats['last_price']:.5f}, "
                  f"Change: {stats['price_change_pct']:+.3f}%")

    # Register instruments and callbacks
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
    for instrument in instruments:
        data_manager.register_callback(instrument, price_monitor)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        print(f"🚀 Starting advanced data streaming...")

        try:
            start_time = time.time()

            async for event in client.pricing.stream(
                account_id=account_id,
                instruments=instruments
            ):
                # Check duration (30 seconds)
                if time.time() - start_time > 30:
                    break

                if event.type == "PRICE" and event.bids and event.asks:
                    bid = float(event.bids[0].price)
                    ask = float(event.asks[0].price)
                    timestamp = datetime.utcnow()

                    data_manager.add_price_update(event.instrument, bid, ask, timestamp)

        except Exception as e:
            print(f"❌ Streaming error: {e}")

        # Print final statistics
        data_manager.print_statistics_summary()

        return data_manager
```

---

## 4. Real-time Signal Generation

### Live Trading Signal System

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

class RealTimeSignalGenerator:
    """Generate trading signals from real-time data."""

    def __init__(self, data_manager: RealTimeDataManager):
        self.data_manager = data_manager
        self.signals = {}
        self.signal_history = {}

        # Signal parameters
        self.ma_short_period = 10
        self.ma_long_period = 20
        self.rsi_period = 14
        self.bollinger_period = 20
        self.bollinger_std = 2.0

        # Signal thresholds
        self.rsi_oversold = 30
        self.rsi_overbought = 70
        self.momentum_threshold = 0.1  # 0.1% price change threshold

    def register_signal_generation(self, instrument: str):
        """Register signal generation for an instrument."""

        def signal_callback(instrument: str, price_data: Dict):
            signals = self._generate_signals(instrument, price_data)
            if signals:
                self._update_signals(instrument, signals)

        self.data_manager.register_callback(instrument, signal_callback)

        # Initialize signal storage
        self.signals[instrument] = {}
        self.signal_history[instrument] = deque(maxlen=100)

        print(f"🎯 Signal generation enabled for {instrument}")

    def _generate_signals(self, instrument: str, price_data: Dict) -> Dict:
        """Generate trading signals based on current data."""

        # Get recent price data
        df = self.data_manager.get_recent_prices(instrument, count=50)

        if len(df) < self.ma_long_period:
            return {}  # Not enough data

        signals = {
            'timestamp': price_data['timestamp'],
            'price': price_data['mid'],
            'bid': price_data['bid'],
            'ask': price_data['ask'],
            'spread': price_data['spread']
        }

        # Moving Average signals
        if len(df) >= self.ma_long_period:
            short_ma = df['mid'].tail(self.ma_short_period).mean()
            long_ma = df['mid'].tail(self.ma_long_period).mean()

            signals['ma_short'] = short_ma
            signals['ma_long'] = long_ma
            signals['ma_signal'] = 'BUY' if short_ma > long_ma else 'SELL'
            signals['ma_strength'] = abs(short_ma - long_ma) / long_ma * 100

        # RSI signals
        if len(df) >= self.rsi_period + 1:
            rsi = self._calculate_rsi(df['mid'].values)
            signals['rsi'] = rsi

            if rsi < self.rsi_oversold:
                signals['rsi_signal'] = 'BUY'
            elif rsi > self.rsi_overbought:
                signals['rsi_signal'] = 'SELL'
            else:
                signals['rsi_signal'] = 'HOLD'

        # Bollinger Bands signals
        if len(df) >= self.bollinger_period:
            bb_signals = self._calculate_bollinger_signals(df['mid'].values)
            signals.update(bb_signals)

        # Momentum signals
        if len(df) >= 5:
            momentum = self._calculate_momentum(df['mid'].values)
            signals['momentum'] = momentum

            if momentum > self.momentum_threshold:
                signals['momentum_signal'] = 'BUY'
            elif momentum < -self.momentum_threshold:
                signals['momentum_signal'] = 'SELL'
            else:
                signals['momentum_signal'] = 'HOLD'

        # Composite signal
        signals['composite_signal'] = self._generate_composite_signal(signals)

        return signals

    def _calculate_rsi(self, prices: np.ndarray) -> float:
        """Calculate RSI indicator."""

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-self.rsi_period:])
        avg_loss = np.mean(losses[-self.rsi_period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def _calculate_bollinger_signals(self, prices: np.ndarray) -> Dict:
        """Calculate Bollinger Bands signals."""

        recent_prices = prices[-self.bollinger_period:]

        sma = np.mean(recent_prices)
        std = np.std(recent_prices)

        upper_band = sma + (self.bollinger_std * std)
        lower_band = sma - (self.bollinger_std * std)

        current_price = prices[-1]

        bb_signal = 'HOLD'
        if current_price <= lower_band:
            bb_signal = 'BUY'
        elif current_price >= upper_band:
            bb_signal = 'SELL'

        return {
            'bb_upper': upper_band,
            'bb_middle': sma,
            'bb_lower': lower_band,
            'bb_signal': bb_signal,
            'bb_position': (current_price - lower_band) / (upper_band - lower_band)
        }

    def _calculate_momentum(self, prices: np.ndarray) -> float:
        """Calculate price momentum."""

        if len(prices) < 5:
            return 0

        current_price = prices[-1]
        old_price = prices[-5]

        momentum = (current_price - old_price) / old_price * 100
        return momentum

    def _generate_composite_signal(self, signals: Dict) -> str:
        """Generate composite signal from individual indicators."""

        buy_votes = 0
        sell_votes = 0
        total_votes = 0

        # Count votes from each indicator
        for signal_key in ['ma_signal', 'rsi_signal', 'bb_signal', 'momentum_signal']:
            if signal_key in signals:
                if signals[signal_key] == 'BUY':
                    buy_votes += 1
                elif signals[signal_key] == 'SELL':
                    sell_votes += 1
                total_votes += 1

        if total_votes == 0:
            return 'HOLD'

        # Require majority consensus
        if buy_votes > total_votes * Decimal("0.6"):
            return 'BUY'
        elif sell_votes > total_votes * Decimal("0.6"):
            return 'SELL'
        else:
            return 'HOLD'

    def _update_signals(self, instrument: str, signals: Dict):
        """Update signal storage and history."""

        self.signals[instrument] = signals

        # Add to history
        self.signal_history[instrument].append({
            'timestamp': signals['timestamp'],
            'price': signals['price'],
            'composite_signal': signals['composite_signal'],
            'ma_signal': signals.get('ma_signal'),
            'rsi': signals.get('rsi'),
            'momentum': signals.get('momentum')
        })

        # Print strong signals
        if signals['composite_signal'] in ['BUY', 'SELL']:
            strength = signals.get('ma_strength', 0)
            if strength > 0.05:  # 0.05% threshold
                print(f"🎯 SIGNAL: {instrument} {signals['composite_signal']} "
                      f"@ {signals['price']:.5f} (strength: {strength:.3f}%)")

    def get_current_signals(self, instrument: str) -> Dict:
        """Get current signals for an instrument."""
        return self.signals.get(instrument, {})

    def get_signal_history(self, instrument: str, count: int = 20) -> List[Dict]:
        """Get recent signal history."""

        if instrument not in self.signal_history:
            return []

        return list(self.signal_history[instrument])[-count:]

    def print_signal_summary(self):
        """Print current signals summary."""

        print(f"\n🎯 Current Trading Signals:")
        print("-" * 70)
        print(f"{'Instrument':<12} {'Price':<10} {'Composite':<10} {'MA':<6} {'RSI':<6} {'Mom':<6}")
        print("-" * 70)

        for instrument, signals in self.signals.items():
            if signals:
                rsi_str = f"{signals.get('rsi', 0):.0f}" if 'rsi' in signals else "N/A"
                momentum_str = f"{signals.get('momentum', 0):+.2f}" if 'momentum' in signals else "N/A"

                print(f"{instrument:<12} {signals['price']:<10.5f} "
                      f"{signals['composite_signal']:<10} "
                      f"{signals.get('ma_signal', 'N/A'):<6} "
                      f"{rsi_str:<6} {momentum_str:<6}")

# Demo signal generation
async def demo_signal_generation(account_id: str):
    """Demonstrate real-time signal generation."""

    if not account_id:
        return

    # Create data manager and signal generator
    data_manager = RealTimeDataManager(buffer_size=200)
    signal_generator = RealTimeSignalGenerator(data_manager)

    # Register instruments for signal generation
    instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
    for instrument in instruments:
        signal_generator.register_signal_generation(instrument)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        print(f"🎯 Starting real-time signal generation...")

        try:
            start_time = time.time()

            async for event in client.pricing.stream(
                account_id=account_id,
                instruments=instruments
            ):
                # Check duration (45 seconds)
                if time.time() - start_time > 45:
                    break

                if event.type == "PRICE" and event.bids and event.asks:
                    bid = float(event.bids[0].price)
                    ask = float(event.asks[0].price)
                    timestamp = datetime.utcnow()

                    data_manager.add_price_update(event.instrument, bid, ask, timestamp)

        except Exception as e:
            print(f"❌ Signal generation error: {e}")

        # Print final signal summary
        signal_generator.print_signal_summary()

        return signal_generator
```

---

## 5. Automated Trading System

### Live Trading Engine

```python
from decimal import Decimal

from fivetwenty import AsyncClient, Environment

class LiveTradingEngine:
    """Automated live trading engine."""

    def __init__(self, client: AsyncClient, account_id: str,
                 signal_generator: RealTimeSignalGenerator):
        self.client = client
        self.account_id = account_id
        self.signal_generator = signal_generator

        # Trading parameters
        self.position_size = 1000
        self.max_positions = 3
        self.min_signal_strength = 0.05  # 0.05% minimum signal strength
        self.enabled = False

        # Trading state
        self.active_trades = {}
        self.trade_count = 0
        self.pnl_total = 0.0

        # Risk management
        self.max_daily_trades = 10
        self.max_daily_loss = Decimal("500.0")  # $500 max daily loss
        self.daily_trades = 0
        self.daily_pnl = 0.0

    def enable_trading(self, enabled: bool = True):
        """Enable or disable live trading."""

        self.enabled = enabled
        status = "ENABLED" if enabled else "DISABLED"
        print(f"🎛️ Live trading {status}")

        if enabled:
            print("⚠️ WARNING: Live trading is now active!")
            print("   Trades will be executed automatically based on signals")

    async def start_automated_trading(self, instruments: List[str], duration: int = 300):
        """Start automated trading system."""

        print(f"🤖 Starting Automated Trading System")
        print(f"   Instruments: {', '.join(instruments)}")
        print(f"   Duration: {duration} seconds")
        print(f"   Trading: {'ENABLED' if self.enabled else 'DISABLED'}")
        print(f"   Max Positions: {self.max_positions}")
        print(f"   Position Size: {self.position_size:,} units")

        # Register trading callbacks
        for instrument in instruments:
            self._register_trading_callback(instrument)

        try:
            start_time = time.time()

            async for event in self.client.pricing.stream(
                account_id=self.account_id,
                instruments=instruments
            ):
                # Check duration
                if time.time() - start_time > duration:
                    print(f"\n⏰ Trading session completed")
                    break

                # Process price events (signals are generated automatically)
                if event.type == "PRICE":
                    await self._monitor_active_trades()

                # Print periodic status
                elapsed = time.time() - start_time
                if int(elapsed) % 60 == 0 and elapsed > 0:  # Every minute
                    await self._print_trading_status()

        except Exception as e:
            print(f"❌ Automated trading error: {e}")
        finally:
            await self._print_final_summary()

    def _register_trading_callback(self, instrument: str):
        """Register trading callback for an instrument."""

        def trading_callback(instrument: str, price_data: Dict):
            if self.enabled:
                asyncio.create_task(self._process_trading_signal(instrument, price_data))

        self.signal_generator.data_manager.register_callback(instrument, trading_callback)

    async def _process_trading_signal(self, instrument: str, price_data: Dict):
        """Process trading signals and execute trades."""

        # Check daily limits
        if self.daily_trades >= self.max_daily_trades:
            return

        if self.daily_pnl <= -self.max_daily_loss:
            print(f"🚨 Daily loss limit reached - trading halted")
            self.enabled = False
            return

        # Get current signals
        signals = self.signal_generator.get_current_signals(instrument)

        if not signals:
            return

        composite_signal = signals.get('composite_signal', 'HOLD')
        signal_strength = signals.get('ma_strength', 0)

        # Check if we already have a position for this instrument
        has_position = instrument in self.active_trades

        # Entry logic
        if (not has_position and
            composite_signal in ['BUY', 'SELL'] and
            signal_strength >= self.min_signal_strength and
            len(self.active_trades) < self.max_positions):

            await self._execute_entry_trade(instrument, composite_signal, signals)

        # Exit logic (simplified - exit on opposite signal)
        elif (has_position and
              composite_signal != 'HOLD'):

            current_position = self.active_trades[instrument]

            # Check for exit conditions
            should_exit = False

            if (current_position['direction'] == 'BUY' and composite_signal == 'SELL'):
                should_exit = True
            elif (current_position['direction'] == 'SELL' and composite_signal == 'BUY'):
                should_exit = True

            if should_exit:
                await self._execute_exit_trade(instrument, signals)

    async def _execute_entry_trade(self, instrument: str, signal: str, signals: Dict):
        """Execute entry trade."""

        try:
            units = self.position_size if signal == 'BUY' else -self.position_size
            current_price = signals['price']

            # Calculate stop loss and take profit
            stop_loss_pips = 20
            take_profit_pips = 40

            pip_value = 0.01 if instrument.endswith('JPY') else 0.0001

            if signal == 'BUY':
                stop_loss = current_price - (stop_loss_pips * pip_value)
                take_profit = current_price + (take_profit_pips * pip_value)
            else:
                stop_loss = current_price + (stop_loss_pips * pip_value)
                take_profit = current_price - (take_profit_pips * pip_value)

            print(f"🎯 ENTRY SIGNAL: {signal} {instrument}")
            print(f"   Signal Strength: {signals.get('ma_strength', 0):.3f}%")
            print(f"   Entry Price: ~{current_price:.5f}")
            print(f"   Stop Loss: {stop_loss:.5f}")
            print(f"   Take Profit: {take_profit:.5f}")

            # Execute trade
            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=units,
                stop_loss_on_fill={'price': f"{stop_loss:.5f}"},
                take_profit_on_fill={'price': f"{take_profit:.5f}"}
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                trade_id = fill.trade_opened.trade_id if fill.trade_opened else None

                # Record active trade
                self.active_trades[instrument] = {
                    'trade_id': trade_id,
                    'direction': signal,
                    'entry_price': float(fill.price),
                    'entry_time': datetime.utcnow(),
                    'units': units,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit
                }

                self.trade_count += 1
                self.daily_trades += 1

                print(f"✅ Trade executed: {units} units @ {fill.price}")
                print(f"   Trade ID: {trade_id}")
            else:
                print(f"❌ Trade execution failed")

        except Exception as e:
            print(f"❌ Entry trade error: {e}")

    async def _execute_exit_trade(self, instrument: str, signals: Dict):
        """Execute exit trade."""

        try:
            trade_info = self.active_trades[instrument]

            # Close position with market order
            close_units = -trade_info['units']

            print(f"🔄 EXIT SIGNAL: {instrument}")
            print(f"   Closing {trade_info['units']} units")

            response = await self.client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=close_units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                exit_price = float(fill.price)

                # Calculate P/L
                if trade_info['direction'] == 'BUY':
                    pnl = (exit_price - trade_info['entry_price']) * abs(trade_info['units'])
                else:
                    pnl = (trade_info['entry_price'] - exit_price) * abs(trade_info['units'])

                self.pnl_total += pnl
                self.daily_pnl += pnl

                print(f"✅ Position closed @ {exit_price}")
                print(f"   P/L: ${pnl:+.2f}")

                # Remove from active trades
                del self.active_trades[instrument]
            else:
                print(f"❌ Exit trade failed")

        except Exception as e:
            print(f"❌ Exit trade error: {e}")

    async def _monitor_active_trades(self):
        """Monitor active trades for updates."""
        # This is simplified - in practice you'd check for fills,
        # stop loss hits, take profit hits, etc.
        pass

    async def _print_trading_status(self):
        """Print current trading status."""

        print(f"\n🤖 Trading Status Update:")
        print(f"   Active Positions: {len(self.active_trades)}")
        print(f"   Total Trades: {self.trade_count}")
        print(f"   Daily Trades: {self.daily_trades}/{self.max_daily_trades}")
        print(f"   Total P/L: ${self.pnl_total:+.2f}")
        print(f"   Daily P/L: ${self.daily_pnl:+.2f}")

        if self.active_trades:
            print(f"   Active Positions:")
            for instrument, trade in self.active_trades.items():
                duration = datetime.utcnow() - trade['entry_time']
                print(f"     {instrument}: {trade['direction']} "
                      f"@ {trade['entry_price']:.5f} "
                      f"({duration.total_seconds()/60:.0f}m ago)")

    async def _print_final_summary(self):
        """Print final trading session summary."""

        print(f"\n🏁 AUTOMATED TRADING SESSION SUMMARY")
        print("=" * 50)
        print(f"   Total Trades Executed: {self.trade_count}")
        print(f"   Final P/L: ${self.pnl_total:+.2f}")
        print(f"   Active Positions Remaining: {len(self.active_trades)}")

        if self.active_trades:
            print(f"   Open Positions:")
            for instrument, trade in self.active_trades.items():
                print(f"     {instrument}: {trade['direction']} "
                      f"{abs(trade['units']):,} units @ {trade['entry_price']:.5f}")

        print(f"   Trading Status: {'ENABLED' if self.enabled else 'DISABLED'}")

# Demo automated trading
async def demo_automated_trading(account_id: str):
    """Demonstrate automated trading system."""

    if not account_id:
        return

    print("🤖 AUTOMATED TRADING DEMO")
    print("=" * 40)
    print("⚠️ This demo shows automated trading capabilities")
    print("   Trading will be DISABLED by default for safety")
    print("   Enable with caution in practice environment only!")

    # Create components
    data_manager = RealTimeDataManager(buffer_size=100)
    signal_generator = RealTimeSignalGenerator(data_manager)

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        trading_engine = LiveTradingEngine(client, account_id, signal_generator)

        # Register instruments
        instruments = ["EUR_USD"]  # Start with one instrument
        for instrument in instruments:
            signal_generator.register_signal_generation(instrument)

        # Enable trading (set to False for demo safety)
        trading_engine.enable_trading(enabled=False)  # Set to True to enable actual trading

        # Start automated trading for 60 seconds
        await trading_engine.start_automated_trading(instruments, duration=60)

        return trading_engine
```

---

## 6. Advanced Streaming Features

### Connection Management and Error Recovery

```python
from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import FiveTwentyError, FiveTwentyErrorCode

class RobustStreamingManager:
    """Robust streaming with connection management and error recovery."""

    def __init__(self, client: AsyncClient, account_id: str):
        self.client = client
        self.account_id = account_id
        self.running = False
        self.reconnect_count = 0
        self.total_reconnects = 0

        # Event handlers
        self.price_handlers = []
        self.heartbeat_handlers = []
        self.error_handlers = []

        # Statistics
        self.stats = {
            'price_updates': 0,
            'heartbeats': 0,
            'errors': 0,
            'reconnections': 0,
            'start_time': None,
            'last_update': None
        }

    def add_price_handler(self, handler: Callable):
        """Add price update handler."""
        self.price_handlers.append(handler)

    def add_heartbeat_handler(self, handler: Callable):
        """Add heartbeat handler."""
        self.heartbeat_handlers.append(handler)

    def add_error_handler(self, handler: Callable):
        """Add error handler."""
        self.error_handlers.append(handler)

    async def start_robust_streaming(self, instruments: List[str],
                                   max_reconnects: int = 10,
                                   reconnect_delay: float = 5.0):
        """Start robust streaming with automatic reconnection."""

        print(f"🚀 Starting robust streaming...")
        print(f"   Instruments: {', '.join(instruments)}")
        print(f"   Max reconnects: {max_reconnects}")

        self.running = True
        self.stats['start_time'] = time.time()
        self.reconnect_count = 0

        while self.running and self.reconnect_count <= max_reconnects:
            try:
                # Configure streaming with robust settings
                config = StreamingConfiguration(
                    heartbeat_timeout=30.0,
                    stall_timeout=60.0
                )

                reconnection_policy = ReconnectionPolicy(
                    max_retries=5,
                    base_delay=1.0,
                    max_delay=30.0,
                    exponential_base=2.0,
                    jitter=True
                )

                print(f"🔗 Connecting to stream... (attempt {self.reconnect_count + 1})")

                async for event in self.client.pricing.stream(
                    account_id=self.account_id,
                    instruments=instruments,
                    configuration=config,
                    reconnection_policy=reconnection_policy
                ):
                    if not self.running:
                        break

                    await self._process_stream_event(event)

                # If we get here, stream ended normally
                print("📡 Stream ended normally")
                break

            except StreamStall as e:
                self.stats['errors'] += 1
                self._call_error_handlers('STREAM_STALL', str(e))
                print(f"🚨 Stream stalled: {e}")
                await self._handle_reconnection(reconnect_delay)

            except FiveTwentyError as e:
                self.stats['errors'] += 1
                self._call_error_handlers('OANDA_ERROR', e.message)
                print(f"❌ OANDA error: {e.message}")
                await self._handle_reconnection(reconnect_delay)

            except Exception as e:
                self.stats['errors'] += 1
                self._call_error_handlers('UNEXPECTED_ERROR', str(e))
                print(f"💥 Unexpected error: {e}")
                await self._handle_reconnection(reconnect_delay)

        if self.reconnect_count > max_reconnects:
            print(f"🚨 Maximum reconnection attempts ({max_reconnects}) exceeded")

        print(f"🛑 Streaming stopped")
        self._print_final_statistics()

    async def _process_stream_event(self, event):
        """Process streaming events."""

        current_time = time.time()
        self.stats['last_update'] = current_time

        if event.type == "PRICE":
            self.stats['price_updates'] += 1

            # Call price handlers
            for handler in self.price_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"❌ Price handler error: {e}")

        elif event.type == "HEARTBEAT":
            self.stats['heartbeats'] += 1

            # Call heartbeat handlers
            for handler in self.heartbeat_handlers:
                try:
                    await handler(event)
                except Exception as e:
                    print(f"❌ Heartbeat handler error: {e}")

    async def _handle_reconnection(self, delay: float):
        """Handle reconnection logic."""

        self.reconnect_count += 1
        self.total_reconnects += 1
        self.stats['reconnections'] += 1

        if self.running:
            print(f"🔄 Reconnecting in {delay:.1f} seconds... (attempt {self.reconnect_count})")
            await asyncio.sleep(delay)

    def _call_error_handlers(self, error_type: str, message: str):
        """Call error handlers."""

        for handler in self.error_handlers:
            try:
                handler(error_type, message)
            except Exception as e:
                print(f"❌ Error handler error: {e}")

    def stop_streaming(self):
        """Stop the streaming process."""

        self.running = False
        print("🛑 Stopping streaming...")

    def _print_final_statistics(self):
        """Print final streaming statistics."""

        duration = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0

        print(f"\n📊 STREAMING SESSION STATISTICS")
        print("=" * 40)
        print(f"   Duration: {duration:.1f} seconds")
        print(f"   Price Updates: {self.stats['price_updates']:,}")
        print(f"   Heartbeats: {self.stats['heartbeats']}")
        print(f"   Errors: {self.stats['errors']}")
        print(f"   Reconnections: {self.stats['reconnections']}")

        if duration > 0:
            print(f"   Update Rate: {self.stats['price_updates']/duration:.2f} updates/sec")

        # Connection stability
        if self.stats['price_updates'] > 0:
            uptime_pct = ((duration - (self.stats['reconnections'] * 5)) / duration) * 100
            print(f"   Uptime: {uptime_pct:.1f}%")

# Demo robust streaming
async def demo_robust_streaming(account_id: str):
    """Demonstrate robust streaming capabilities."""

    if not account_id:
        return

    async with AsyncClient(token=TOKEN, environment=ENVIRONMENT) as client:
        manager = RobustStreamingManager(client, account_id)

        # Add event handlers
        async def price_handler(event):
            if hasattr(event, 'instrument') and event.bids and event.asks:
                bid = float(event.bids[0].price)
                ask = float(event.asks[0].price)

                # Print every 20th update
                if manager.stats['price_updates'] % 20 == 0:
                    print(f"📈 {event.instrument}: {bid:.5f}/{ask:.5f} "
                          f"[{manager.stats['price_updates']}]")

        async def heartbeat_handler(event):
            if manager.stats['heartbeats'] % 10 == 0:
                elapsed = time.time() - manager.stats['start_time']
                print(f"💓 Heartbeat #{manager.stats['heartbeats']} "
                      f"(uptime: {elapsed:.0f}s)")

        def error_handler(error_type: str, message: str):
            print(f"🚨 Error [{error_type}]: {message}")

        # Register handlers
        manager.add_price_handler(price_handler)
        manager.add_heartbeat_handler(heartbeat_handler)
        manager.add_error_handler(error_handler)

        # Start robust streaming for 60 seconds
        streaming_task = asyncio.create_task(
            manager.start_robust_streaming(
                instruments=["EUR_USD", "GBP_USD"],
                max_reconnects=5,
                reconnect_delay=3.0
            )
        )

        # Let it run for 60 seconds then stop
        await asyncio.sleep(60)
        manager.stop_streaming()

        # Wait for streaming to finish
        await streaming_task

        return manager
```

---

## 7. Best Practices and Summary

### Streaming Best Practices Checklist

```python
class StreamingBestPractices:
    """Best practices guide for streaming implementations."""

    @staticmethod
    def print_best_practices():
        """Print comprehensive best practices guide."""

        print("📚 STREAMING DATA BEST PRACTICES")
        print("=" * 50)

        practices = [
            "🔗 Connection Management:",
            "   • Implement automatic reconnection with exponential backoff",
            "   • Monitor heartbeats to detect connection issues",
            "   • Use proper timeout settings (30s heartbeat, 60s stall)",
            "   • Handle all exception types gracefully",
            "",
            "💾 Data Management:",
            "   • Use bounded buffers to prevent memory leaks",
            "   • Implement efficient data structures (deque, circular buffers)",
            "   • Clean up old data regularly",
            "   • Separate storage by data type and timeframe",
            "",
            "🎯 Signal Processing:",
            "   • Wait for sufficient data before generating signals",
            "   • Use moving windows for indicator calculations",
            "   • Implement signal filtering to reduce noise",
            "   • Combine multiple indicators for robust signals",
            "",
            "🤖 Automated Trading:",
            "   • Implement comprehensive risk controls",
            "   • Use position size limits and daily loss limits",
            "   • Log all trading decisions and outcomes",
            "   • Test thoroughly in practice environment first",
            "",
            "⚡ Performance Optimization:",
            "   • Process events asynchronously",
            "   • Use callbacks for decoupled event handling",
            "   • Batch database writes if persisting data",
            "   • Monitor memory usage and CPU performance",
            "",
            "🛡️ Error Handling:",
            "   • Log all errors with timestamps and context",
            "   • Implement circuit breakers for repeated failures",
            "   • Have fallback procedures for critical failures",
            "   • Monitor error rates and patterns",
            "",
            "📊 Monitoring and Alerting:",
            "   • Track connection uptime and stability",
            "   • Monitor data quality and gaps",
            "   • Set up alerts for trading system failures",
            "   • Keep detailed performance metrics"
        ]

        for practice in practices:
            print(practice)

    @staticmethod
    def validate_streaming_setup(components: Dict) -> Dict:
        """Validate streaming setup configuration."""

        validation = {
            'score': 0,
            'max_score': 100,
            'recommendations': [],
            'critical_issues': []
        }

        # Check data management (25 points)
        if 'data_manager' in components:
            validation['score'] += 25
        else:
            validation['critical_issues'].append("No data management system")

        # Check signal generation (20 points)
        if 'signal_generator' in components:
            validation['score'] += 20
        else:
            validation['recommendations'].append("Consider adding signal generation")

        # Check error handling (20 points)
        if 'error_handlers' in components:
            validation['score'] += 20
        else:
            validation['critical_issues'].append("No error handling implemented")

        # Check reconnection logic (15 points)
        if 'reconnection_policy' in components:
            validation['score'] += 15
        else:
            validation['recommendations'].append("Implement automatic reconnection")

        # Check risk management (10 points)
        if 'risk_controls' in components:
            validation['score'] += 10
        else:
            validation['recommendations'].append("Add risk management controls")

        # Check monitoring (10 points)
        if 'monitoring' in components:
            validation['score'] += 10
        else:
            validation['recommendations'].append("Add performance monitoring")

        return validation

# Demo best practices validation
def demo_best_practices():
    """Demonstrate best practices validation."""

    StreamingBestPractices.print_best_practices()

    # Example component validation
    components = {
        'data_manager': True,
        'signal_generator': True,
        'error_handlers': True,
        'reconnection_policy': True,
        # Missing: risk_controls, monitoring
    }

    validation = StreamingBestPractices.validate_streaming_setup(components)

    print(f"\n🔍 SETUP VALIDATION RESULTS:")
    print(f"   Score: {validation['score']}/{validation['max_score']} "
          f"({validation['score']/validation['max_score']*100:.0f}%)")

    if validation['critical_issues']:
        print(f"   🚨 Critical Issues:")
        for issue in validation['critical_issues']:
            print(f"     - {issue}")

    if validation['recommendations']:
        print(f"   💡 Recommendations:")
        for rec in validation['recommendations']:
            print(f"     - {rec}")

    return validation
```

---

## Summary

You've mastered comprehensive real-time streaming data capabilities:

- ✅ **Basic Streaming**: Connection setup and event processing
- ✅ **Data Management**: Efficient real-time data buffering and storage
- ✅ **Signal Generation**: Live trading signal calculation and monitoring
- ✅ **Automated Trading**: Complete automated trading system implementation
- ✅ **Connection Management**: Robust error handling and reconnection
- ✅ **Best Practices**: Production-ready streaming architecture

### Key Components Implemented

1. **RealTimeDataManager**: Efficient price data buffering
2. **RealTimeSignalGenerator**: Live indicator calculation
3. **LiveTradingEngine**: Automated trade execution
4. **RobustStreamingManager**: Connection reliability

### Next Steps

Continue your education:

- **[Data Analysis](examples/notebooks/data-analysis.ipynb)** - Historical validation of streaming strategies
- **[Portfolio Analysis](portfolio-analysis.md)** - Real-time portfolio monitoring
- **[Risk Management](risk-management.md)** - Live risk control systems
- **[Advanced Orders](advanced-orders.md)** - Sophisticated execution strategies

### Production Considerations

**Before going live:**
1. **Test extensively** in practice environment
2. **Implement comprehensive logging** and monitoring
3. **Set up alerts** for system failures
4. **Start with small position sizes**
5. **Monitor performance** continuously

### Remember

**Real-time trading systems require extreme care and testing. Always prioritize risk management and system reliability over profit generation.** ⚡

**Your streaming system is only as good as its weakest link - invest in robust error handling and monitoring.** 🔗