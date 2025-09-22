# Real-time Signal Generation

Create live trading signals from streaming data using real-time technical indicators and market event detection.

---

## Real-Time Signal Framework

```python
import asyncio
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class SignalType(Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"

@dataclass
class TradingSignal:
    instrument: str
    signal_type: SignalType
    strength: float  # 0.0 to 1.0
    timestamp: datetime
    indicators: Dict[str, float]
    reason: str

class RealTimeIndicators:
    """Calculate technical indicators in real-time."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.price_windows = {}

    async def update_price(self, instrument: str, price: float):
        """Update price and calculate indicators."""

        if instrument not in self.price_windows:
            self.price_windows[instrument] = []

        self.price_windows[instrument].append(price)

        # Maintain window size
        if len(self.price_windows[instrument]) > self.window_size:
            self.price_windows[instrument] = self.price_windows[instrument][-self.window_size:]

        return await self._calculate_indicators(instrument)

    async def _calculate_indicators(self, instrument: str) -> Dict[str, float]:
        """Calculate real-time technical indicators."""

        prices = np.array(self.price_windows[instrument])

        if len(prices) < 2:
            return {}

        indicators = {}

        # Simple Moving Average
        if len(prices) >= 5:
            indicators['sma_5'] = np.mean(prices[-5:])

        if len(prices) >= 10:
            indicators['sma_10'] = np.mean(prices[-10:])

        # RSI approximation for real-time
        if len(prices) >= 14:
            deltas = np.diff(prices[-14:])
            gains = np.where(deltas > 0, deltas, 0)
            losses = np.where(deltas < 0, -deltas, 0)

            avg_gain = np.mean(gains) if len(gains) > 0 else 0
            avg_loss = np.mean(losses) if len(losses) > 0 else 0

            if avg_loss != 0:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                indicators['rsi'] = rsi

        # Price momentum
        if len(prices) >= 5:
            momentum = (prices[-1] - prices[-5]) / prices[-5] * 100
            indicators['momentum_5'] = momentum

        return indicators

class LiveSignalGenerator:
    """Generate trading signals from real-time data."""

    def __init__(self):
        self.indicators = RealTimeIndicators()
        self.signal_history = {}
        self.signal_callbacks = []

    async def process_price_update(self, instrument: str, bid: float, ask: float):
        """Process price update and generate signals."""

        mid_price = (bid + ask) / 2

        # Update indicators
        indicators = await self.indicators.update_price(instrument, mid_price)

        if indicators:
            # Generate signal
            signal = await self._generate_signal(instrument, indicators, mid_price)

            if signal:
                # Store signal
                if instrument not in self.signal_history:
                    self.signal_history[instrument] = []

                self.signal_history[instrument].append(signal)

                # Limit history size
                if len(self.signal_history[instrument]) > 100:
                    self.signal_history[instrument] = self.signal_history[instrument][-50:]

                # Notify callbacks
                for callback in self.signal_callbacks:
                    await callback(signal)

    async def _generate_signal(self, instrument: str, indicators: Dict[str, float],
                             current_price: float) -> Optional[TradingSignal]:
        """Generate trading signal from indicators."""

        if not indicators:
            return None

        signal_strength = 0.0
        signal_type = SignalType.NEUTRAL
        reasons = []

        # RSI-based signals
        rsi = indicators.get('rsi')
        if rsi:
            if rsi < 30:
                signal_strength += 0.3
                signal_type = SignalType.BUY
                reasons.append(f"RSI oversold ({rsi:.1f})")
            elif rsi > 70:
                signal_strength += 0.3
                signal_type = SignalType.SELL
                reasons.append(f"RSI overbought ({rsi:.1f})")

        # Moving average crossover
        sma_5 = indicators.get('sma_5')
        sma_10 = indicators.get('sma_10')

        if sma_5 and sma_10:
            if sma_5 > sma_10 and current_price > sma_5:
                signal_strength += 0.2
                if signal_type != SignalType.SELL:
                    signal_type = SignalType.BUY
                reasons.append("Price above rising SMA")
            elif sma_5 < sma_10 and current_price < sma_5:
                signal_strength += 0.2
                if signal_type != SignalType.BUY:
                    signal_type = SignalType.SELL
                reasons.append("Price below falling SMA")

        # Momentum signals
        momentum = indicators.get('momentum_5')
        if momentum:
            if momentum > 2:  # 2% momentum
                signal_strength += 0.1
                reasons.append(f"Strong upward momentum ({momentum:.1f}%)")
            elif momentum < -2:
                signal_strength += 0.1
                reasons.append(f"Strong downward momentum ({momentum:.1f}%)")

        # Only generate signal if strength is significant
        if signal_strength >= 0.3:
            return TradingSignal(
                instrument=instrument,
                signal_type=signal_type,
                strength=min(signal_strength, 1.0),
                timestamp=datetime.now(),
                indicators=indicators.copy(),
                reason="; ".join(reasons)
            )

        return None

    def add_signal_callback(self, callback: Callable):
        """Add callback for signal notifications."""
        self.signal_callbacks.append(callback)

# Signal event handlers
async def signal_logger(signal: TradingSignal):
    """Log trading signals."""
    print(f"SIGNAL: {signal.instrument} {signal.signal_type.value} "
          f"(Strength: {signal.strength:.2f}) - {signal.reason}")

async def signal_trader(signal: TradingSignal):
    """Execute trades based on signals."""
    if signal.strength >= 0.7:  # High confidence threshold
        print(f"EXECUTING: {signal.instrument} {signal.signal_type.value}")
        # Implementation would include actual trade execution

# Example usage
async def live_signal_generation_example():
    """Demonstrate live signal generation."""

    generator = LiveSignalGenerator()

    # Add signal handlers
    generator.add_signal_callback(signal_logger)
    generator.add_signal_callback(signal_trader)

    # Simulate streaming price updates
    instruments = ["EUR_USD", "GBP_USD"]

    for i in range(100):
        for instrument in instruments:
            # Simulate price movement
            base_price = 1.1000 if instrument == "EUR_USD" else 1.3000
            price_change = np.random.normal(0, 0.0001)
            bid = base_price + price_change
            ask = bid + 0.0002

            await generator.process_price_update(instrument, bid, ask)

        await asyncio.sleep(0.1)  # 100ms intervals

# Run example
# await live_signal_generation_example()
```

---

## Next Steps

Continue to [Automated Trading Systems](automated-trading.md) to build complete trading engines.

---

## Related Tutorials

- [Advanced Data Management](advanced-data-management.md) - Data processing
- [Automated Trading Systems](automated-trading.md) - Complete systems
- [Best Practices](best-practices.md) - Production considerations