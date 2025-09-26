# Technical Indicators Integration

**Problem**: You need to enhance your trading decisions with advanced technical analysis indicators beyond basic price data.

**Solution**: Integrate external technical analysis libraries like TA-Lib with FiveTwenty to calculate comprehensive technical indicators and generate sophisticated trading signals.

---

## Prerequisites

- FiveTwenty configured and working
- Understanding of technical analysis concepts
- TA-Lib library installed (`pip install TA-Lib`)
- Pandas and NumPy for data manipulation
- Knowledge of common technical indicators (RSI, MACD, Bollinger Bands, etc.)

---

## External Technical Indicators

Integrate with technical analysis libraries:

```python
from fivetwenty import AsyncClient, Environment

import pandas as pd
import numpy as np
import talib
from typing import Dict, List, Optional, Tuple
import asyncio

class TechnicalAnalysisProvider:
    """Advanced technical analysis using external libraries."""

    def __init__(self, fivetwenty_client: AsyncClient):
        self.fivetwenty_client = fivetwenty_client

    async def get_enhanced_analysis(self, instrument: str, timeframe: str = "H1",
                                  periods: int = 200) -> Dict[str, float]:
        """Get comprehensive technical analysis for an instrument."""

        # Fetch historical data
        candles_response = await self.fivetwenty_client.instruments.get_instrument_candles(
            instrument=instrument,
            count=periods,
            granularity=timeframe
        )

        # Convert to pandas DataFrame
        df = self._candles_to_dataframe(candles_response.candles)

        if len(df) < 50:
            print(f"Insufficient data for analysis: {len(df)} candles")
            return {}

        # Calculate technical indicators
        analysis = {}

        # Trend indicators
        analysis.update(self._calculate_trend_indicators(df))

        # Momentum indicators
        analysis.update(self._calculate_momentum_indicators(df))

        # Volatility indicators
        analysis.update(self._calculate_volatility_indicators(df))

        # Volume indicators (if available)
        if 'volume' in df.columns:
            analysis.update(self._calculate_volume_indicators(df))

        # Support/Resistance levels
        analysis.update(self._calculate_support_resistance(df))

        return analysis

    def _candles_to_dataframe(self, candles) -> pd.DataFrame:
        """Convert OANDA candles to pandas DataFrame."""

        data = []
        for candle in candles:
            if candle.mid:
                data.append({
                    'timestamp': pd.to_datetime(candle.time),
                    'open': float(candle.mid.o),
                    'high': float(candle.mid.h),
                    'low': float(candle.mid.l),
                    'close': float(candle.mid.c),
                    'volume': int(candle.volume) if hasattr(candle, 'volume') else 0
                })

        df = pd.DataFrame(data)
        df.set_index('timestamp', inplace=True)
        return df

    def _calculate_trend_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate trend-following indicators."""

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # Moving averages
            sma_20 = talib.SMA(close, timeperiod=20)
            sma_50 = talib.SMA(close, timeperiod=50)
            ema_12 = talib.EMA(close, timeperiod=12)
            ema_26 = talib.EMA(close, timeperiod=26)

            # MACD
            macd, macd_signal, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

            # ADX (Average Directional Index)
            adx = talib.ADX(high, low, close, timeperiod=14)

            # Parabolic SAR
            sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)

            current_price = close[-1]

            indicators.update({
                'sma_20': sma_20[-1] if not np.isnan(sma_20[-1]) else 0,
                'sma_50': sma_50[-1] if not np.isnan(sma_50[-1]) else 0,
                'ema_12': ema_12[-1] if not np.isnan(ema_12[-1]) else 0,
                'ema_26': ema_26[-1] if not np.isnan(ema_26[-1]) else 0,
                'macd': macd[-1] if not np.isnan(macd[-1]) else 0,
                'macd_signal': macd_signal[-1] if not np.isnan(macd_signal[-1]) else 0,
                'macd_histogram': macd_hist[-1] if not np.isnan(macd_hist[-1]) else 0,
                'adx': adx[-1] if not np.isnan(adx[-1]) else 0,
                'sar': sar[-1] if not np.isnan(sar[-1]) else 0,
                'price_vs_sma20': (current_price / sma_20[-1] - 1) * 100 if not np.isnan(sma_20[-1]) else 0,
                'price_vs_sma50': (current_price / sma_50[-1] - 1) * 100 if not np.isnan(sma_50[-1]) else 0
            })

        except Exception as e:
            print(f"Error calculating trend indicators: {e}")

        return indicators

    def _calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate momentum indicators."""

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # RSI
            rsi = talib.RSI(close, timeperiod=14)

            # Stochastic
            slowk, slowd = talib.STOCH(high, low, close, fastk_period=5, slowk_period=3, slowd_period=3)

            # Williams %R
            willr = talib.WILLR(high, low, close, timeperiod=14)

            # Commodity Channel Index
            cci = talib.CCI(high, low, close, timeperiod=14)

            # Rate of Change
            roc = talib.ROC(close, timeperiod=10)

            indicators.update({
                'rsi': rsi[-1] if not np.isnan(rsi[-1]) else 50,
                'stoch_k': slowk[-1] if not np.isnan(slowk[-1]) else 50,
                'stoch_d': slowd[-1] if not np.isnan(slowd[-1]) else 50,
                'williams_r': willr[-1] if not np.isnan(willr[-1]) else -50,
                'cci': cci[-1] if not np.isnan(cci[-1]) else 0,
                'roc': roc[-1] if not np.isnan(roc[-1]) else 0
            })

        except Exception as e:
            print(f"Error calculating momentum indicators: {e}")

        return indicators

    def _calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate volatility indicators."""

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # Bollinger Bands
            bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2)

            # Average True Range
            atr = talib.ATR(high, low, close, timeperiod=14)

            current_price = close[-1]

            indicators.update({
                'bb_upper': bb_upper[-1] if not np.isnan(bb_upper[-1]) else 0,
                'bb_middle': bb_middle[-1] if not np.isnan(bb_middle[-1]) else 0,
                'bb_lower': bb_lower[-1] if not np.isnan(bb_lower[-1]) else 0,
                'bb_position': ((current_price - bb_lower[-1]) / (bb_upper[-1] - bb_lower[-1])) * 100
                              if not np.isnan(bb_upper[-1]) and not np.isnan(bb_lower[-1]) else 50,
                'atr': atr[-1] if not np.isnan(atr[-1]) else 0,
                'atr_percent': (atr[-1] / current_price) * 100 if not np.isnan(atr[-1]) and current_price > 0 else 0
            })

        except Exception as e:
            print(f"Error calculating volatility indicators: {e}")

        return indicators

    def _calculate_volume_indicators(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate volume-based indicators."""

        close = df['close'].values
        volume = df['volume'].values

        indicators = {}

        try:
            # On Balance Volume
            obv = talib.OBV(close, volume)

            # Volume Rate of Change
            volume_roc = talib.ROC(volume, timeperiod=10)

            indicators.update({
                'obv': obv[-1] if not np.isnan(obv[-1]) else 0,
                'volume_roc': volume_roc[-1] if not np.isnan(volume_roc[-1]) else 0,
                'avg_volume': np.mean(volume[-20:]) if len(volume) >= 20 else np.mean(volume),
                'current_volume': volume[-1] if len(volume) > 0 else 0
            })

        except Exception as e:
            print(f"Error calculating volume indicators: {e}")

        return indicators

    def _calculate_support_resistance(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate support and resistance levels."""

        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        indicators = {}

        try:
            # Pivot points (classic method)
            recent_high = np.max(high[-20:])
            recent_low = np.min(low[-20:])
            recent_close = close[-1]

            pivot = (recent_high + recent_low + recent_close) / 3

            # Support and resistance levels
            r1 = 2 * pivot - recent_low
            s1 = 2 * pivot - recent_high
            r2 = pivot + (recent_high - recent_low)
            s2 = pivot - (recent_high - recent_low)

            indicators.update({
                'pivot_point': pivot,
                'resistance_1': r1,
                'support_1': s1,
                'resistance_2': r2,
                'support_2': s2,
                'price_vs_pivot': ((recent_close / pivot) - 1) * 100 if pivot > 0 else 0
            })

        except Exception as e:
            print(f"Error calculating support/resistance: {e}")

        return indicators

class AdvancedTradingSignals:
    """Generate trading signals from multiple technical indicators."""

    def __init__(self, ta_provider: TechnicalAnalysisProvider):
        self.ta_provider = ta_provider

    async def generate_comprehensive_signal(self, instrument: str) -> Dict[str, any]:
        """Generate trading signal from multiple indicators."""

        # Get technical analysis
        analysis = await self.ta_provider.get_enhanced_analysis(instrument)

        if not analysis:
            return {'signal': 'NEUTRAL', 'strength': 0, 'reasons': []}

        # Analyze different aspects
        trend_signal = self._analyze_trend(analysis)
        momentum_signal = self._analyze_momentum(analysis)
        volatility_signal = self._analyze_volatility(analysis)

        # Combine signals
        signals = [trend_signal, momentum_signal, volatility_signal]
        signal_values = [s['value'] for s in signals]

        # Calculate weighted signal
        weights = [0.4, 0.4, 0.2]  # Trend and momentum more important
        combined_signal = sum(s * w for s, w in zip(signal_values, weights))

        # Determine final signal
        if combined_signal > 0.3:
            final_signal = 'BUY'
        elif combined_signal < -0.3:
            final_signal = 'SELL'
        else:
            final_signal = 'NEUTRAL'

        # Collect all reasons
        all_reasons = []
        for signal in signals:
            all_reasons.extend(signal['reasons'])

        return {
            'signal': final_signal,
            'strength': abs(combined_signal),
            'combined_score': combined_signal,
            'trend_component': trend_signal,
            'momentum_component': momentum_signal,
            'volatility_component': volatility_signal,
            'reasons': all_reasons,
            'raw_analysis': analysis
        }

    def _analyze_trend(self, analysis: Dict[str, float]) -> Dict[str, any]:
        """Analyze trend indicators."""

        signal_value = 0
        reasons = []

        # Price vs moving averages
        if analysis.get('price_vs_sma20', 0) > 2:
            signal_value += 0.3
            reasons.append("Price >2% above SMA20")
        elif analysis.get('price_vs_sma20', 0) < -2:
            signal_value -= 0.3
            reasons.append("Price >2% below SMA20")

        # MACD
        macd = analysis.get('macd', 0)
        macd_signal = analysis.get('macd_signal', 0)
        if macd > macd_signal and macd > 0:
            signal_value += 0.2
            reasons.append("MACD bullish crossover")
        elif macd < macd_signal and macd < 0:
            signal_value -= 0.2
            reasons.append("MACD bearish crossover")

        # ADX strength
        adx = analysis.get('adx', 0)
        if adx > 25:
            reasons.append(f"Strong trend (ADX: {adx:.1f})")
        elif adx < 15:
            signal_value *= 0.5  # Reduce signal in weak trends
            reasons.append(f"Weak trend (ADX: {adx:.1f})")

        return {
            'value': np.clip(signal_value, -1, 1),
            'reasons': reasons
        }

    def _analyze_momentum(self, analysis: Dict[str, float]) -> Dict[str, any]:
        """Analyze momentum indicators."""

        signal_value = 0
        reasons = []

        # RSI
        rsi = analysis.get('rsi', 50)
        if rsi > 70:
            signal_value -= 0.3
            reasons.append(f"RSI overbought ({rsi:.1f})")
        elif rsi < 30:
            signal_value += 0.3
            reasons.append(f"RSI oversold ({rsi:.1f})")
        elif 45 < rsi < 55:
            reasons.append("RSI neutral")

        # Stochastic
        stoch_k = analysis.get('stoch_k', 50)
        if stoch_k > 80:
            signal_value -= 0.2
            reasons.append("Stochastic overbought")
        elif stoch_k < 20:
            signal_value += 0.2
            reasons.append("Stochastic oversold")

        # CCI
        cci = analysis.get('cci', 0)
        if cci > 100:
            signal_value -= 0.1
            reasons.append("CCI overbought")
        elif cci < -100:
            signal_value += 0.1
            reasons.append("CCI oversold")

        return {
            'value': np.clip(signal_value, -1, 1),
            'reasons': reasons
        }

    def _analyze_volatility(self, analysis: Dict[str, float]) -> Dict[str, any]:
        """Analyze volatility indicators."""

        signal_value = 0
        reasons = []

        # Bollinger Bands position
        bb_position = analysis.get('bb_position', 50)
        if bb_position > 80:
            signal_value -= 0.2
            reasons.append("Near upper Bollinger Band")
        elif bb_position < 20:
            signal_value += 0.2
            reasons.append("Near lower Bollinger Band")

        # ATR analysis
        atr_percent = analysis.get('atr_percent', 0)
        if atr_percent > 2:
            reasons.append(f"High volatility (ATR: {atr_percent:.2f}%)")
        elif atr_percent < 0.5:
            reasons.append(f"Low volatility (ATR: {atr_percent:.2f}%)")

        return {
            'value': np.clip(signal_value, -1, 1),
            'reasons': reasons
        }

# Usage example
async def advanced_technical_analysis_example():
    """Example of advanced technical analysis integration."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as fivetwenty_client:
        ta_provider = TechnicalAnalysisProvider(fivetwenty_client)
        signal_generator = AdvancedTradingSignals(ta_provider)

        # Analyze multiple instruments
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]

        for instrument in instruments:
            print(f"\nAnalyzing {instrument}...")

            signal_data = await signal_generator.generate_comprehensive_signal(instrument)

            print(f"Signal: {signal_data['signal']} (Strength: {signal_data['strength']:.2f})")
            print(f"Combined Score: {signal_data['combined_score']:.2f}")

            print("Reasons:")
            for reason in signal_data['reasons']:
                print(f"  • {reason}")

        return signal_generator

# Example usage
# signal_generator = await advanced_technical_analysis_example()
```

## Advanced Signal Generation

### Multi-Timeframe Analysis

For more robust signals, analyze multiple timeframes:

```python
class MultiTimeframeAnalysis:
    """Analyze multiple timeframes for stronger signals."""

    def __init__(self, ta_provider: TechnicalAnalysisProvider) -> None:
        self.ta_provider = ta_provider
        self.timeframes = ["M5", "M15", "H1", "H4", "D"]
        self.timeframe_weights = {
            "M5": 0.1,
            "M15": 0.15,
            "H1": 0.25,
            "H4": 0.3,
            "D": 0.2
        }

    async def get_multi_timeframe_signal(self, instrument: str) -> Dict[str, any]:
        """Get signal from multiple timeframes."""

        timeframe_signals = {}

        for timeframe in self.timeframes:
            try:
                analysis = await self.ta_provider.get_enhanced_analysis(
                    instrument, timeframe=timeframe, periods=100
                )

                if analysis:
                    # Simple trend signal from price vs SMA
                    price_vs_sma = analysis.get('price_vs_sma20', 0)
                    rsi = analysis.get('rsi', 50)

                    # Combined signal
                    trend_signal = 1 if price_vs_sma > 1 else -1 if price_vs_sma < -1 else 0
                    momentum_signal = 1 if rsi < 30 else -1 if rsi > 70 else 0

                    timeframe_signals[timeframe] = {
                        'trend': trend_signal,
                        'momentum': momentum_signal,
                        'combined': (trend_signal + momentum_signal) / 2
                    }

            except Exception as e:
                print(f"Error analyzing {timeframe}: {e}")
                timeframe_signals[timeframe] = {
                    'trend': 0,
                    'momentum': 0,
                    'combined': 0
                }

        # Calculate weighted signal
        weighted_signal = 0
        total_weight = 0

        for timeframe, signals in timeframe_signals.items():
            weight = self.timeframe_weights.get(timeframe, 0)
            weighted_signal += signals['combined'] * weight
            total_weight += weight

        if total_weight > 0:
            final_signal = weighted_signal / total_weight
        else:
            final_signal = 0

        # Determine action
        if final_signal > 0.3:
            action = 'BUY'
        elif final_signal < -0.3:
            action = 'SELL'
        else:
            action = 'NEUTRAL'

        return {
            'action': action,
            'strength': abs(final_signal),
            'weighted_signal': final_signal,
            'timeframe_breakdown': timeframe_signals
        }
```

### Custom Indicator Development

Create custom indicators for specific strategies:

```python

class CustomIndicators:
    """Class docstring."""
    """Custom technical indicators for specific strategies."""

    @staticmethod
    def trend_strength_index(df: pd.DataFrame, period: int = 20) -> np.ndarray:
        """Custom trend strength indicator."""

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # Calculate price momentum
        price_change = np.diff(close)

        # Calculate volatility-adjusted momentum
        atr = talib.ATR(high, low, close, timeperiod=period)

        # Normalize momentum by ATR
        normalized_momentum = np.zeros(len(close))
        for i in range(period, len(close)):
            if atr[i] > 0:
                normalized_momentum[i] = price_change[i-1] / atr[i]

        # Smooth the indicator
        trend_strength = talib.EMA(normalized_momentum, timeperiod=period)

        return trend_strength

    @staticmethod
    def volatility_breakout_indicator(df: pd.DataFrame, period: int = 20) -> np.ndarray:
        """Detect volatility breakouts."""

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        # Calculate ATR
        atr = talib.ATR(high, low, close, timeperiod=period)

        # Calculate ATR percentile over lookback period
        breakout_signal = np.zeros(len(close))

        for i in range(period * 2, len(close)):
            current_atr = atr[i]
            historical_atr = atr[i-period:i]

            # Current ATR percentile
            percentile = np.percentile(historical_atr, 80)

            if current_atr > percentile:
                breakout_signal[i] = 1  # High volatility breakout
            elif current_atr < np.percentile(historical_atr, 20):
                breakout_signal[i] = -1  # Low volatility period

        return breakout_signal

    @staticmethod
    def mean_reversion_score(df: pd.DataFrame, period: int = 14) -> np.ndarray:
        """Calculate mean reversion probability."""

        close = df['close'].values

        # Calculate distance from moving average
        sma = talib.SMA(close, timeperiod=period)
        deviation = (close - sma) / sma * 100

        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = talib.BBANDS(close, timeperiod=period)
        bb_position = (close - bb_lower) / (bb_upper - bb_lower) * 100

        # Combine indicators for mean reversion score
        mean_reversion = np.zeros(len(close))

        for i in range(period, len(close)):
            # Strong mean reversion signals
            if bb_position[i] > 90:  # Near upper band
                mean_reversion[i] = -deviation[i] / 5  # Negative for sell signal
            elif bb_position[i] < 10:  # Near lower band
                mean_reversion[i] = -deviation[i] / 5  # Positive for buy signal

        return mean_reversion
```

## Trading System Integration

### Signal-Based Trading System

```python
class TechnicalSignalTradingSystem:
    """Complete trading system based on technical signals."""

    def __init__(self, fivetwenty_client: AsyncClient):
        self.fivetwenty_client = fivetwenty_client
        self.ta_provider = TechnicalAnalysisProvider(fivetwenty_client)
        self.signal_generator = AdvancedTradingSignals(self.ta_provider)
        self.multi_tf_analyzer = MultiTimeframeAnalysis(self.ta_provider)

    async def execute_signal_based_trade(self, account_id: str, instrument: str,
                                       base_units: int, min_signal_strength: float = 0.5):
        """Execute trades based on technical signals."""

        # Get single timeframe signal
        signal_data = await self.signal_generator.generate_comprehensive_signal(instrument)

        # Get multi-timeframe confirmation
        mtf_signal = await self.multi_tf_analyzer.get_multi_timeframe_signal(instrument)

        print(f"\n{instrument} Technical Analysis:")
        print(f"Primary Signal: {signal_data['signal']} (Strength: {signal_data['strength']:.2f})")
        print(f"Multi-TF Signal: {mtf_signal['action']} (Strength: {mtf_signal['strength']:.2f})")

        # Check signal alignment and strength
        primary_strong = signal_data["strength"] >= min_signal_strength
        mtf_strong = mtf_signal["strength"] >= 0.3
        signals_aligned = signal_data["signal"] == mtf_signal["action"]

        if not (primary_strong and mtf_strong and signals_aligned):
            print("Insufficient signal strength or alignment - no trade")
            return None

        # Calculate position size based on signal strength
        signal_multiplier = (signal_data["strength"] + mtf_signal["strength"]) / 2
        adjusted_units = int(base_units * signal_multiplier)

        # Apply signal direction
        if signal_data["signal"] == "SELL":
            adjusted_units = -adjusted_units

        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=adjusted_units,
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"Technical signal trade executed: {instrument} {adjusted_units} @ {fill.price}")

                return {
                    "trade_id": fill.trade_opened.trade_id if fill.trade_opened else None,
                    "signal": signal_data["signal"],
                    "strength": signal_data["strength"],
                    "units": adjusted_units,
                    "reasons": signal_data["reasons"],
                }

        except Exception as e:
            print(f"Trade execution error: {e}")
            return None
```

## Best Practices

### Indicator Validation

Always validate your indicators before live trading:

```python

class IndicatorValidator:
    """Class docstring."""
    """Validate technical indicators and signals."""

    @staticmethod
    def validate_indicator_values(indicators: Dict[str, float]) -> bool:
        """Check if indicator values are reasonable."""

        validations = [
            # RSI should be between 0 and 100
            0 <= indicators.get('rsi', 50) <= 100,

            # Stochastic should be between 0 and 100
            0 <= indicators.get('stoch_k', 50) <= 100,

            # Williams %R should be between -100 and 0
            -100 <= indicators.get('williams_r', -50) <= 0,

            # ATR should be positive
            indicators.get('atr', 0) >= 0,

            # Moving averages should be positive for forex
            indicators.get('sma_20', 1) > 0,
            indicators.get('ema_12', 1) > 0
        ]

        return all(validations)

    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict[str, bool]:
        """Check quality of price data."""

        return {
            'sufficient_data': len(df) >= 50,
            'no_missing_values': not df.isnull().any().any(),
            'realistic_prices': (df['high'] >= df['low']).all(),
            'consistent_ohlc': (
                (df['high'] >= df['open']).all() and
                (df['high'] >= df['close']).all() and
                (df['low'] <= df['open']).all() and
                (df['low'] <= df['close']).all()
            )
        }
```

### Performance Monitoring

Track the performance of your technical signals:

```python


from typing import Any
from datetime import datetime

class SignalPerformanceTracker:
    """Class docstring."""
    """Track performance of technical signals."""

    def __init__(self) -> None:
        self.signal_history = []

    def record_signal(self, instrument: str, signal_data: Dict, trade_result: Dict = None) -> Any:
        """Record a signal and its outcome."""

        record = {
            "timestamp": datetime.now(timezone.utc),
            "instrument": instrument,
            "signal": signal_data["signal"],
            "strength": signal_data["strength"],
            "reasons": signal_data["reasons"],
            "trade_executed": trade_result is not None,
            "trade_result": trade_result,
        }

        self.signal_history.append(record)

    def get_signal_accuracy(self, days_back: int = 30) -> Dict[str, float]:
        """Calculate signal accuracy over time period."""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_signals = [
            s for s in self.signal_history
            if s["timestamp"] > cutoff_date and s["trade_executed"]
        ]

        if not recent_signals:
            return {"accuracy": 0, "total_signals": 0}

        # This would need to be implemented based on your trade tracking
        # For demonstration, assume we track PnL in trade_result
        profitable_trades = sum(
            1 for s in recent_signals
            if s["trade_result"] and s["trade_result"].get("pnl", 0) > 0
        )

        return {
            "accuracy": profitable_trades / len(recent_signals) * 100,
            "total_signals": len(recent_signals),
            "profitable_trades": profitable_trades,
        }
```

## Troubleshooting

### Common Issues

1. **TA-Lib Installation**: TA-Lib can be challenging to install
   - Use conda: `conda install -c conda-forge ta-lib`
   - On Windows: Download precompiled wheels
   - Ensure you have the underlying TA-Lib C library

2. **Insufficient Data**: Some indicators need minimum periods
   - Always check data length before calculation
   - Handle NaN values gracefully
   - Use appropriate fallback values

3. **Performance Issues**: Technical analysis can be compute-intensive
   - Cache calculated indicators when possible
   - Use vectorized operations with NumPy
   - Consider async processing for multiple instruments

## Next Steps

- **[Social Sentiment Integration](social-sentiment.md)** - Add social media sentiment
- **[Unified Data Pipeline](unified-pipeline.md)** - Combine multiple data sources
- **[Financial News Integration](financial-news.md)** - Enhance with news analysis

---

## Related Guides

- [Economic Calendar Integration](economic-calendar.md)
- [Risk Management Tutorial](../../tutorials/risk-management.md)
- [Advanced Orders Guide](../../tutorials/advanced-orders/index.md)