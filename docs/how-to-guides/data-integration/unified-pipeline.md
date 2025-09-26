# Unified Data Pipeline

**Problem**: You need to combine multiple external data sources (economic calendar, news, technical indicators, social sentiment) into a cohesive system for comprehensive market analysis.

**Solution**: Build a unified data pipeline that orchestrates all external data sources, combines their signals, and provides comprehensive market context for trading decisions.

---

## Prerequisites

- FiveTwenty configured and working
- All individual data integration guides implemented:
  - [Economic Calendar Integration](economic-calendar.md)
  - [Financial News Integration](financial-news.md)
  - [Technical Indicators Integration](technical-indicators.md)
  - [Social Sentiment Integration](social-sentiment.md)
- Understanding of data pipeline architecture
- Async programming knowledge for coordinating multiple data sources

---

## Unified Data Pipeline Architecture

Combine all external data sources into a unified system:

```python
from fivetwenty import AsyncClient, Environment

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import numpy as np

@dataclass
class MarketContext:
    """Unified market context from all data sources."""

    timestamp: datetime
    instrument: str

    # OANDA price data
    current_price: Decimal
    spread: Decimal

    # Technical analysis
    technical_signal: str  # BUY, SELL, NEUTRAL
    technical_strength: Decimal
    technical_reasons: List[str]

    # Economic calendar
    upcoming_events: List[str]
    trading_allowed: bool

    # News sentiment
    news_sentiment: Decimal
    news_confidence: Decimal
    news_count: int

    # Social sentiment
    social_bias: Decimal
    social_confidence: Decimal

    # Combined analysis
    final_signal: str
    signal_strength: Decimal
    risk_level: str

class UnifiedTradingSystem:
    """Unified trading system combining all external data sources."""

    def __init__(self, fivetwenty_client: AsyncClient, config: Dict[str, str]):
        self.fivetwenty_client = fivetwenty_client

        # Initialize all data providers
        self.economic_calendar = EconomicCalendarProvider(config.get('calendar_api_key'))
        self.news_provider = NewsProvider(config.get('news_api_key'))
        self.ta_provider = TechnicalAnalysisProvider(fivetwenty_client)
        self.social_provider = SocialSentimentProvider(config.get('twitter_token'))

        # Initialize individual systems
        self.economic_system = EconomicAwareTradingSystem(fivetwenty_client, self.economic_calendar)
        self.news_system = NewsSentimentTrading(fivetwenty_client, self.news_provider)
        self.signal_generator = AdvancedTradingSignals(self.ta_provider)
        self.social_system = SocialTradingSystem(fivetwenty_client, self.social_provider)

        # Data cache
        self.market_context_cache = {}

    async def initialize_all_data_sources(self):
        """Initialize all external data sources."""

        print("Initializing unified data pipeline...")

        # Initialize all systems concurrently
        initialization_tasks = [
            self.economic_system.update_economic_events(),
            self.news_system.update_news_sentiment(),
            self.social_system.update_social_sentiment()
        ]

        await asyncio.gather(*initialization_tasks, return_exceptions=True)
        print("All data sources initialized")

    async def get_unified_market_context(self, instrument: str) -> MarketContext:
        """Get comprehensive market context for an instrument."""

        print(f"Building unified market context for {instrument}...")

        # Get current OANDA price
        prices = await self.fivetwenty_client.pricing.get_pricing("101-001-1234567-001", [instrument])
        current_price_data = prices[0]

        current_price = Decimal(str(current_price_data.asks[0].price))
        spread = Decimal(str(current_price_data.asks[0].price)) - Decimal(str(current_price_data.bids[0].price))

        # Get all analysis data concurrently
        analysis_tasks = [
            self.signal_generator.generate_comprehensive_signal(instrument),
            asyncio.create_task(self._get_economic_context(instrument)),
            asyncio.create_task(self._get_news_context(instrument)),
            asyncio.create_task(self._get_social_context(instrument))
        ]

        results = await asyncio.gather(*analysis_tasks, return_exceptions=True)

        # Parse results
        technical_analysis = results[0] if not isinstance(results[0], Exception) else {}
        economic_context = results[1] if not isinstance(results[1], Exception) else {}
        news_context = results[2] if not isinstance(results[2], Exception) else {}
        social_context = results[3] if not isinstance(results[3], Exception) else {}

        # Create unified market context
        context = MarketContext(
            timestamp=datetime.now(),
            instrument=instrument,
            current_price=current_price,
            spread=spread,

            # Technical analysis
            technical_signal=technical_analysis.get('signal', 'NEUTRAL'),
            technical_strength=Decimal(str(technical_analysis.get('strength', 0))),
            technical_reasons=technical_analysis.get('reasons', []),

            # Economic calendar
            upcoming_events=economic_context.get('upcoming_events', []),
            trading_allowed=economic_context.get('trading_allowed', True),

            # News sentiment
            news_sentiment=Decimal(str(news_context.get('sentiment', 0))),
            news_confidence=Decimal(str(news_context.get('confidence', 0))),
            news_count=news_context.get('news_count', 0),

            # Social sentiment
            social_bias=Decimal(str(social_context.get('bias', 0))),
            social_confidence=Decimal(str(social_context.get('confidence', 0))),

            # Combined analysis (calculated below)
            final_signal='NEUTRAL',
            signal_strength=Decimal('0'),
            risk_level='MEDIUM'
        )

        # Calculate combined signal
        context.final_signal, context.signal_strength, context.risk_level = self._calculate_combined_signal(context)

        # Cache the context
        self.market_context_cache[instrument] = context

        return context

    async def _get_economic_context(self, instrument: str) -> Dict:
        """Get economic context for instrument."""

        upcoming_events = []
        trading_allowed, conflicting_event = await self.economic_system.is_safe_to_trade(instrument)

        # Get relevant upcoming events
        currencies = instrument.split('_')
        for currency in currencies:
            events = await self.economic_system.get_upcoming_events(instrument, hours_ahead=24)
            for event in events:
                time_until = (event.time - datetime.now(timezone.utc)).total_seconds() / 3600
                upcoming_events.append(f"{event.event} in {time_until:.1f}h")

        return {
            'upcoming_events': upcoming_events,
            'trading_allowed': trading_allowed
        }

    async def _get_news_context(self, instrument: str) -> Dict:
        """Get news sentiment context for instrument."""

        sentiment_data = self.news_system.get_instrument_sentiment(instrument)

        return {
            'sentiment': sentiment_data.get('sentiment', 0),
            'confidence': sentiment_data.get('confidence', 0),
            'news_count': sentiment_data.get('news_count', 0)
        }

    async def _get_social_context(self, instrument: str) -> Dict:
        """Get social sentiment context for instrument."""

        sentiment_data = self.social_system.get_pair_sentiment_bias(instrument)

        return {
            'bias': sentiment_data.get('bias', 0),
            'confidence': sentiment_data.get('confidence', 0)
        }

    def _calculate_combined_signal(self, context: MarketContext) -> tuple[str, float, str]:
        """Calculate combined trading signal from all data sources."""

        # Weight different signal sources
        weights = {
            'technical': 0.4,
            'news': 0.25,
            'social': 0.2,
            'economic': 0.15
        }

        # Convert signals to numerical values
        technical_value = self._signal_to_value(context.technical_signal) * context.technical_strength
        news_value = context.news_sentiment * context.news_confidence
        social_value = context.social_bias * context.social_confidence
        economic_value = -1 if not context.trading_allowed else 0  # Penalty for blackout periods

        # Calculate weighted signal
        combined_signal = (
            technical_value * weights['technical'] +
            news_value * weights['news'] +
            social_value * weights['social'] +
            economic_value * weights['economic']
        )

        # Determine final signal
        if combined_signal > 0.3:
            final_signal = 'BUY'
        elif combined_signal < -0.3:
            final_signal = 'SELL'
        else:
            final_signal = 'NEUTRAL'

        signal_strength = abs(combined_signal)

        # Calculate risk level
        risk_factors = 0
        if not context.trading_allowed:
            risk_factors += 2
        if context.spread > 0.0005:  # High spread
            risk_factors += 1
        if context.technical_strength < 0.3:  # Weak technical signal
            risk_factors += 1
        if context.news_count > 5:  # High news activity
            risk_factors += 1

        if risk_factors >= 3:
            risk_level = 'HIGH'
        elif risk_factors >= 2:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'

        return final_signal, signal_strength, risk_level

    def _signal_to_value(self, signal: str) -> float:
        """Convert signal string to numerical value."""

        signal_map = {
            'BUY': 1.0,
            'SELL': -1.0,
            'NEUTRAL': 0.0
        }
        return signal_map.get(signal, 0.0)

    async def execute_unified_trading_decision(self, account_id: str, instrument: str,
                                            base_units: int) -> Optional[Dict]:
        """Execute trading decision based on unified analysis."""

        # Get comprehensive market context
        context = await self.get_unified_market_context(instrument)

        # Print analysis summary
        print(f"\nUnified Analysis for {instrument}:")
        print(f"   Current Price: {context.current_price}")
        print(f"   Technical: {context.technical_signal} ({context.technical_strength:.2f})")
        print(f"   News Sentiment: {context.news_sentiment:.3f} ({context.news_count} articles)")
        print(f"   Social Bias: {context.social_bias:.3f}")
        print(f"   Trading Allowed: {context.trading_allowed}")
        print(f"   Final Signal: {context.final_signal} (Strength: {context.signal_strength:.2f})")
        print(f"   Risk Level: {context.risk_level}")

        # Risk-based position sizing
        risk_multipliers = {'LOW': 1.0, 'MEDIUM': 0.7, 'HIGH': 0.3}
        risk_multiplier = risk_multipliers.get(context.risk_level, 0.5)

        # Signal-based position sizing
        signal_multiplier = context.signal_strength

        # Calculate final position size
        if context.final_signal == 'NEUTRAL' or not context.trading_allowed:
            print(f"No trading signal or trading blocked - skipping {instrument}")
            return None

        final_units = int(base_units * risk_multiplier * signal_multiplier)

        if context.final_signal == 'SELL':
            final_units = -final_units

        print(f"Calculated position size: {final_units} units (Risk: {risk_multiplier:.1f}x, Signal: {signal_multiplier:.2f}x)")

        # Execute trade
        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=final_units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"Unified trade executed: {instrument} {final_units} @ {fill.price}")

                # Log detailed context
                context_dict = asdict(context)
                context_dict['timestamp'] = context_dict['timestamp'].isoformat()

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'units': final_units,
                    'fill_price': Decimal(str(fill.price)),
                    'market_context': context_dict
                }
            else:
                print(f"Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"Unified trading error: {e}")
            return None

    def export_market_context(self, filepath: str):
        """Export current market context to file."""

        export_data = {}
        for instrument, context in self.market_context_cache.items():
            context_dict = asdict(context)
            context_dict['timestamp'] = context_dict['timestamp'].isoformat()
            export_data[instrument] = context_dict

        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Market context exported to {filepath}")

# Complete usage example
async def unified_trading_system_example():
    """Example of complete unified trading system."""

    # Configuration
    config = {
        'calendar_api_key': 'your-calendar-key',
        'news_api_key': 'your-news-key',
        'twitter_token': 'your-twitter-token'
    }

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as fivetwenty_client:
        # Initialize unified system
        unified_system = UnifiedTradingSystem(fivetwenty_client, config)

        # Initialize all data sources
        await unified_system.initialize_all_data_sources()

        # Execute unified trading decisions
        account_id = "101-001-1234567-001"
        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]

        trades = []
        for instrument in instruments:
            result = await unified_system.execute_unified_trading_decision(
                account_id, instrument, base_units=10000
            )
            if result:
                trades.append(result)

        # Export market context for analysis
        unified_system.export_market_context("market_context_export.json")

        print(f"\nUnified Trading Summary:")
        print(f"   Executed {len(trades)} trades based on comprehensive analysis")
        print(f"   Market context exported for {len(unified_system.market_context_cache)} instruments")

        return trades

# Example usage
# trades = await unified_trading_system_example()
```

## Advanced Pipeline Features

### Real-Time Data Orchestration

Coordinate real-time updates from all data sources:

```python
from datetime import datetime


class RealTimeDataOrchestrator:
    """Orchestrate real-time updates from multiple data sources."""

    def __init__(self, unified_system: UnifiedTradingSystem) -> None:
        self.unified_system = unified_system
        self.monitoring = False
        self.update_intervals = {
            'pricing': 30,      # 30 seconds
            'technical': 300,   # 5 minutes
            'news': 600,        # 10 minutes
            'social': 900,      # 15 minutes
            'economic': 3600    # 1 hour
        }
        self.last_updates = {}

    async def start_orchestration(self) -> Any:
        """Start coordinated real-time data updates."""

        self.monitoring = True
        print("Starting real-time data orchestration...")

        # Initialize last update times
        now = datetime.now(timezone.utc)
        for source in self.update_intervals:
            self.last_updates[source] = now

        while self.monitoring:
            try:
                current_time = datetime.now(timezone.utc)
                update_tasks = []

                # Check which sources need updates
                for source, interval in self.update_intervals.items():
                    if (current_time - self.last_updates[source]).total_seconds() >= interval:
                        task = self._create_update_task(source)
                        if task:
                            update_tasks.append(task)
                            self.last_updates[source] = current_time

                # Execute updates concurrently
                if update_tasks:
                    await asyncio.gather(*update_tasks, return_exceptions=True)

                # Sleep until next check
                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                print(f"Orchestration error: {e}")
                await asyncio.sleep(60)

    def _create_update_task(self, source: str) -> Any:
        """Create update task for a specific data source."""

        if source == 'news':
            return self.unified_system.news_system.update_news_sentiment()
        elif source == 'social':
            return self.unified_system.social_system.update_social_sentiment()
        elif source == 'economic':
            return self.unified_system.economic_system.update_economic_events()
        # Technical indicators are calculated on-demand
        # Pricing is fetched on-demand

        return None

    def stop_orchestration(self) -> Any:
        """Stop real-time orchestration."""
        self.monitoring = False
        print("Real-time data orchestration stopped")
```

### Data Quality Monitoring

Monitor the quality and freshness of all data sources:

```python
class DataQualityMonitor:
    """Monitor data quality across all sources."""

    def __init__(self, unified_system: UnifiedTradingSystem):
        self.unified_system = unified_system
        self.quality_metrics = {}

    async def assess_data_quality(self) -> Dict[str, Dict]:
        """Assess quality of all data sources."""

        quality_report = {}

        # Economic data quality
        quality_report['economic'] = await self._assess_economic_quality()

        # News data quality
        quality_report['news'] = await self._assess_news_quality()

        # Social data quality
        quality_report['social'] = await self._assess_social_quality()

        # Technical data quality
        quality_report['technical'] = await self._assess_technical_quality()

        # Overall quality score
        source_scores = [metrics.get('score', 0) for metrics in quality_report.values()]
        overall_score = sum(source_scores) / len(source_scores) if source_scores else 0

        quality_report['overall'] = {
            'score': overall_score,
            'status': 'GOOD' if overall_score > 0.8 else 'WARNING' if overall_score > 0.5 else 'POOR'
        }

        self.quality_metrics = quality_report
        return quality_report

    async def _assess_economic_quality(self) -> Dict:
        """Assess economic calendar data quality."""

        try:
            # Check if we have recent event data
            events_count = len(self.unified_system.economic_system.trading_blackout_periods)

            # Check data freshness (assume update within last 24 hours is fresh)
            now = datetime.now(timezone.utc)
            recent_events = [
                event for event in self.unified_system.economic_system.trading_blackout_periods
                if abs((event['start'] - now).total_seconds()) < 86400  # 24 hours
            ]

            freshness_score = min(len(recent_events) / max(1, events_count), 1.0)
            coverage_score = min(events_count / 10, 1.0)  # Expect ~10 events per update

            overall_score = (freshness_score + coverage_score) / 2

            return {
                'score': overall_score,
                'events_count': events_count,
                'recent_events': len(recent_events),
                'status': 'GOOD' if overall_score > 0.7 else 'WARNING' if overall_score > 0.4 else 'POOR'
            }

        except Exception as e:
            return {'score': 0, 'error': str(e), 'status': 'ERROR'}

    async def _assess_news_quality(self) -> Dict:
        """Assess news data quality."""

        try:
            news_cache = getattr(self.unified_system.news_system, 'news_cache', [])

            if not news_cache:
                return {'score': 0, 'status': 'NO_DATA'}

            # Check data freshness
            now = datetime.now(timezone.utc)
            fresh_news = [
                news for news in news_cache
                if (now - news.timestamp).total_seconds() < 3600  # 1 hour
            ]

            freshness_score = len(fresh_news) / max(1, len(news_cache))

            # Check relevance quality
            high_relevance = [news for news in news_cache if news.relevance_score > 0.5]
            relevance_score = len(high_relevance) / max(1, len(news_cache))

            overall_score = (freshness_score + relevance_score) / 2

            return {
                'score': overall_score,
                'total_news': len(news_cache),
                'fresh_news': len(fresh_news),
                'high_relevance': len(high_relevance),
                'status': 'GOOD' if overall_score > 0.6 else 'WARNING' if overall_score > 0.3 else 'POOR'
            }

        except Exception as e:
            return {'score': 0, 'error': str(e), 'status': 'ERROR'}

    async def _assess_social_quality(self) -> Dict:
        """Assess social sentiment data quality."""

        try:
            sentiment_cache = getattr(self.unified_system.social_system, 'sentiment_cache', {})

            if not sentiment_cache:
                return {'score': 0, 'status': 'NO_DATA'}

            # Check data coverage
            major_currencies = ['USD', 'EUR', 'GBP', 'JPY']
            covered_currencies = [curr for curr in major_currencies if curr in sentiment_cache]
            coverage_score = len(covered_currencies) / len(major_currencies)

            # Check data volume
            total_tweets = sum(data.get('tweet_count', 0) for data in sentiment_cache.values())
            volume_score = min(total_tweets / 50, 1.0)  # Expect ~50 tweets across currencies

            overall_score = (coverage_score + volume_score) / 2

            return {
                'score': overall_score,
                'covered_currencies': len(covered_currencies),
                'total_tweets': total_tweets,
                'status': 'GOOD' if overall_score > 0.6 else 'WARNING' if overall_score > 0.3 else 'POOR'
            }

        except Exception as e:
            return {'score': 0, 'error': str(e), 'status': 'ERROR'}

    async def _assess_technical_quality(self) -> Dict:
        """Assess technical analysis data quality."""

        try:
            # Test technical analysis on a sample instrument
            test_analysis = await self.unified_system.ta_provider.get_enhanced_analysis(
                "EUR_USD", periods=50
            )

            if not test_analysis:
                return {'score': 0, 'status': 'NO_DATA'}

            # Check completeness of indicators
            expected_indicators = ['rsi', 'macd', 'sma_20', 'bb_upper', 'atr']
            present_indicators = [ind for ind in expected_indicators if ind in test_analysis]
            completeness_score = len(present_indicators) / len(expected_indicators)

            # Check for reasonable values
            validity_checks = [
                0 <= test_analysis.get('rsi', 50) <= 100,
                test_analysis.get('atr', 0) >= 0,
                test_analysis.get('sma_20', 1) > 0
            ]
            validity_score = sum(validity_checks) / len(validity_checks)

            overall_score = (completeness_score + validity_score) / 2

            return {
                'score': overall_score,
                'indicators_present': len(present_indicators),
                'indicators_expected': len(expected_indicators),
                'status': 'GOOD' if overall_score > 0.8 else 'WARNING' if overall_score > 0.5 else 'POOR'
            }

        except Exception as e:
            return {'score': 0, 'error': str(e), 'status': 'ERROR'}

    def get_quality_summary(self) -> str:
        """Get human-readable quality summary."""

        if not self.quality_metrics:
            return "Data quality not assessed yet"

        summary = "Data Quality Report:\n"
        for source, metrics in self.quality_metrics.items():
            status = metrics.get('status', 'UNKNOWN')
            score = metrics.get('score', 0)
            summary += f"  {source.title()}: {status} (Score: {score:.2f})\n"

        return summary
```

### Pipeline Performance Monitoring

Monitor the performance and efficiency of the data pipeline:

```python


from typing import Any
from datetime import datetime

class PipelinePerformanceMonitor:
    """Class docstring."""
    """Monitor performance of the unified data pipeline."""

    def __init__(self) -> None:
        self.performance_metrics = {}
        self.operation_times = {}

    async def time_operation(self, operation_name: str, operation_func, *args, **kwargs) -> Any:
        """Time an operation and record performance metrics."""

        start_time = datetime.now()

        try:
            result = await operation_func(*args, **kwargs)
            success = True
            error = None

        except Exception as e:
            result = None
            success = False
            error = str(e)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Record metrics
        if operation_name not in self.operation_times:
            self.operation_times[operation_name] = []

        self.operation_times[operation_name].append({
            'duration': duration,
            'success': success,
            'error': error,
            'timestamp': start_time
        })

        # Keep only last 100 operations per type
        self.operation_times[operation_name] = self.operation_times[operation_name][-100:]

        return result

    def get_performance_summary(self) -> Dict[str, Dict]:
        """Get performance summary for all operations."""

        summary = {}

        for operation, times in self.operation_times.items():
            if not times:
                continue

            durations = [t['duration'] for t in times if t['success']]
            successes = [t['success'] for t in times]

            if durations:
                summary[operation] = {
                    'avg_duration': sum(durations) / len(durations),
                    'min_duration': min(durations),
                    'max_duration': max(durations),
                    'success_rate': sum(successes) / len(successes),
                    'total_operations': len(times),
                    'recent_errors': [
                        t['error'] for t in times[-10:]
                        if not t['success'] and t['error']
                    ]
                }

        return summary

    def identify_bottlenecks(self) -> List[str]:
        """Identify performance bottlenecks."""

        summary = self.get_performance_summary()
        bottlenecks = []

        for operation, metrics in summary.items():
            # Slow operations (>5 seconds average)
            if metrics['avg_duration'] > 5.0:
                bottlenecks.append(f"{operation}: Slow average duration ({metrics['avg_duration']:.2f}s)")

            # Low success rate (<90%)
            if metrics['success_rate'] < 0.9:
                bottlenecks.append(f"{operation}: Low success rate ({metrics['success_rate']:.1%})")

            # High variability
            if metrics['max_duration'] > metrics['avg_duration'] * 3:
                bottlenecks.append(f"{operation}: High duration variability")

        return bottlenecks
```

## Best Practices

### Configuration Management

Centralize configuration for all data sources:

```python
class DataSourceConfig:
    """Centralized configuration for all data sources."""

    def __init__(self, config_file: str = None) -> None:
        self.config = self._load_config(config_file) if config_file else {}

    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file."""
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}

    def get_api_keys(self) -> Dict[str, str]:
        """Get all API keys."""
        return {
            "economic_calendar": self.config.get("economic_calendar_api_key"),
            "news_api": self.config.get("news_api_key"),
            "twitter_bearer": self.config.get("twitter_bearer_token"),
            "oanda_token": self.config.get("oanda_token"),
        }

    def get_update_intervals(self) -> Dict[str, int]:
        """Get update intervals for each data source."""
        return self.config.get("update_intervals", {
            "economic": 3600,   # 1 hour
            "news": 600,        # 10 minutes
            "social": 900,      # 15 minutes
            "technical": 300,    # 5 minutes
        })

    def get_risk_settings(self) -> Dict[str, float]:
        """Get risk management settings."""
        return self.config.get("risk_settings", {
            "max_position_size": 100000,
            "risk_multipliers": {"LOW": 1.0, "MEDIUM": 0.7, "HIGH": 0.3},
            "min_signal_strength": 0.3,
        })
```

### Error Handling and Resilience

Implement robust error handling for production use:

```python
from decimal import Decimal
from datetime import datetime


class ResilientDataPipeline:
    """Resilient wrapper for unified trading system."""

    def __init__(self, unified_system: UnifiedTradingSystem) -> None:
        self.unified_system = unified_system
        self.fallback_modes = {
            "economic": True,   # Can trade without economic data
            "news": True,       # Can trade without news
            "social": True,     # Can trade without social sentiment
            "technical": False,  # Cannot trade without technical analysis
        }

    async def get_resilient_market_context(self, instrument: str) -> MarketContext:
        """Get market context with fallback for failed data sources."""

        try:
            return await self.unified_system.get_unified_market_context(instrument)

        except Exception as e:
            print(f"Error getting full market context: {e}")

            # Try with fallback mode
            return await self._get_fallback_context(instrument)

    async def _get_fallback_context(self, instrument: str) -> MarketContext:
        """Get market context using only available data sources."""

        # Start with minimal context
        prices = await self.unified_system.fivetwenty_client.pricing.get_pricing(
            "101-001-1234567-001", [instrument],
        )
        current_price_data = prices[0]

        context = MarketContext(
            timestamp=datetime.now(),
            instrument=instrument,
            current_price=Decimal(str(current_price_data.asks[0].price)),
            spread=Decimal(str(current_price_data.asks[0].price)) - Decimal(str(current_price_data.bids[0].price)),
            technical_signal="NEUTRAL",
            technical_strength=0,
            technical_reasons=[],
            upcoming_events=[],
            trading_allowed=True,
            news_sentiment=0,
            news_confidence=0,
            news_count=0,
            social_bias=0,
            social_confidence=0,
            final_signal="NEUTRAL",
            signal_strength=0,
            risk_level="HIGH",  # High risk due to missing data
        )

        # Try to get technical analysis (critical)
        try:
            technical = await self.unified_system.signal_generator.generate_comprehensive_signal(instrument)
            context.technical_signal = technical.get("signal", "NEUTRAL")
            context.technical_strength = technical.get("strength", 0)
            context.technical_reasons = technical.get("reasons", [])

            # If we have technical analysis, we can trade
            if context.technical_strength > 0.3:
                context.final_signal = context.technical_signal
                context.signal_strength = context.technical_strength * 0.7  # Reduced confidence
                context.risk_level = "MEDIUM"

        except Exception as e:
            print(f"Technical analysis failed: {e}")
            context.risk_level = "HIGH"

        return context
```

## Troubleshooting

### Common Pipeline Issues

1. **Data Source Synchronization**: Different update frequencies can cause inconsistencies
   - Implement proper caching strategies
   - Use timestamps to validate data freshness
   - Consider data staleness in signal calculations

2. **API Rate Limiting**: Multiple APIs with different rate limits
   - Implement intelligent rate limiting
   - Use exponential backoff for failed requests
   - Consider API key rotation strategies

3. **Performance Optimization**: Multiple concurrent API calls can be slow
   - Use async/await properly for concurrent operations
   - Implement connection pooling where possible
   - Cache expensive calculations

## Next Steps

With the unified data pipeline complete, you can:

- **Scale to More Instruments**: Apply the pipeline to additional currency pairs
- **Add Custom Data Sources**: Integrate proprietary or additional data feeds
- **Implement Machine Learning**: Use the comprehensive market context for ML models
- **Build Trading Strategies**: Create sophisticated strategies using all available data

---

## Related Guides

- [Economic Calendar Integration](economic-calendar.md)
- [Financial News Integration](financial-news.md)
- [Technical Indicators Integration](technical-indicators.md)
- [Social Sentiment Integration](social-sentiment.md)
- [Risk Management Tutorial](../../tutorials/risk-management/index.md)