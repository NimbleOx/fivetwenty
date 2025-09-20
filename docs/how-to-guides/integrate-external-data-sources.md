# How to Integrate with External Data Sources

**Problem**: You need to combine FiveTwenty trading capabilities with external data sources for enhanced market analysis and decision-making.

**Solution**: Implement data integration patterns to combine OANDA price data with economic calendars, news feeds, technical indicators, and alternative data sources.

---

## Prerequisites

- FiveTwenty configured and working
- Understanding of async programming patterns
- API access to external data providers (where applicable)
- Basic knowledge of data processing and analysis
- Database or storage system for data persistence

---

## Economic Calendar Integration

### News and Economic Events

Integrate economic calendar data to avoid trading during high-impact events:

```python
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass
from fivetwenty import AsyncClient, Environment

@dataclass
class EconomicEvent:
    """Economic calendar event data."""

    time: datetime
    currency: str
    event: str
    impact: str  # LOW, MEDIUM, HIGH
    forecast: Optional[str] = None
    previous: Optional[str] = None
    actual: Optional[str] = None

class EconomicCalendarProvider:
    """Integration with economic calendar APIs."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.forexfactory.com/calendar"  # Example endpoint

    async def get_events(self, start_date: datetime, end_date: datetime,
                        currencies: List[str] = None) -> List[EconomicEvent]:
        """Fetch economic events from calendar API."""

        params = {
            'from': start_date.strftime('%Y%m%d'),
            'to': end_date.strftime('%Y%m%d'),
            'importance': 'high',  # Only high-impact events
            'api_key': self.api_key
        }

        if currencies:
            params['currencies'] = ','.join(currencies)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_events(data)
                    else:
                        print(f"❌ Calendar API error: {response.status}")
                        return []

            except Exception as e:
                print(f"❌ Calendar request failed: {e}")
                return []

    def _parse_events(self, data: Dict) -> List[EconomicEvent]:
        """Parse API response into EconomicEvent objects."""

        events = []

        for item in data.get('events', []):
            try:
                event_time = datetime.fromisoformat(item['datetime'])

                event = EconomicEvent(
                    time=event_time,
                    currency=item.get('currency', ''),
                    event=item.get('title', ''),
                    impact=item.get('importance', 'MEDIUM').upper(),
                    forecast=item.get('forecast'),
                    previous=item.get('previous'),
                    actual=item.get('actual')
                )

                events.append(event)

            except Exception as e:
                print(f"⚠️ Failed to parse event: {e}")
                continue

        return events

class TradingWithEconomicData:
    """Trading system integrated with economic calendar."""

    def __init__(self, fivetwenty_client: AsyncClient, calendar: EconomicCalendarProvider):
        self.fivetwenty_client = fivetwenty_client
        self.calendar = calendar
        self.trading_blackout_periods = []

    async def update_economic_events(self):
        """Update economic events and create trading blackout periods."""

        # Get events for next 7 days
        start_date = datetime.now(timezone.utc)
        end_date = start_date + timedelta(days=7)

        events = await self.calendar.get_events(
            start_date, end_date,
            currencies=['USD', 'EUR', 'GBP', 'JPY']
        )

        print(f"📅 Loaded {len(events)} economic events")

        # Create blackout periods around high-impact events
        self.trading_blackout_periods = []

        for event in events:
            if event.impact == 'HIGH':
                # 30 minutes before and after high-impact events
                blackout_start = event.time - timedelta(minutes=30)
                blackout_end = event.time + timedelta(minutes=30)

                self.trading_blackout_periods.append({
                    'start': blackout_start,
                    'end': blackout_end,
                    'event': event.event,
                    'currency': event.currency
                })

        print(f"🚫 Created {len(self.trading_blackout_periods)} blackout periods")

    def is_trading_allowed(self, instrument: str) -> bool:
        """Check if trading is allowed for instrument given economic events."""

        now = datetime.now(timezone.utc)

        # Check if current time falls in any blackout period
        for blackout in self.trading_blackout_periods:
            if blackout['start'] <= now <= blackout['end']:
                # Check if this event affects the trading instrument
                if blackout['currency'] in instrument:
                    print(f"🚫 Trading blocked: {blackout['event']} affects {instrument}")
                    return False

        return True

    async def safe_place_order(self, account_id: str, instrument: str, units: int):
        """Place order only if no economic events conflict."""

        if not self.is_trading_allowed(instrument):
            print(f"⏳ Order delayed due to economic event: {instrument}")
            return None

        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units
            )

            if response.order_fill_transaction:
                print(f"✅ Order placed: {instrument} {units} units")
                return response.order_fill_transaction
            else:
                print(f"❌ Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"❌ Order error: {e}")
            return None

# Usage example
async def economic_data_integration_example():
    """Example of trading with economic calendar integration."""

    # Initialize components
    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as fivetwenty_client:
        calendar = EconomicCalendarProvider(api_key = 'your-api-key-here')
        trading_system = TradingWithEconomicData(fivetwenty_client, calendar)

        # Update economic events
        await trading_system.update_economic_events()

        # Attempt to place trades
        account_id = "101-001-1234567-001"

        # This will check economic calendar before trading
        await trading_system.safe_place_order(account_id, "EUR_USD", 10000)
        await trading_system.safe_place_order(account_id, "GBP_USD", 5000)

        return trading_system

# Example usage
# trading_system = await economic_data_integration_example()
```

---

## Financial News Integration

### Real-Time News Analysis

Integrate with news APIs for sentiment analysis:

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

import re
from textblob import TextBlob
from typing import List, Dict, Tuple
import asyncio
import aiohttp

@dataclass
class NewsItem:
    """Financial news item."""

    timestamp: datetime
    title: str
    content: str
    source: str
    instruments_mentioned: List[str]
    sentiment_score: float
    relevance_score: float

class NewsProvider:
    """Integration with financial news APIs."""

    def __init__(self, api_key: str, provider: str = "newsapi"):
        self.api_key = api_key
        self.provider = provider

        # Currency-related keywords
        self.currency_keywords = {
            'USD': ['dollar', 'usd', 'federal reserve', 'fed', 'jerome powell'],
            'EUR': ['euro', 'eur', 'ecb', 'european central bank', 'lagarde'],
            'GBP': ['pound', 'gbp', 'sterling', 'bank of england', 'boe'],
            'JPY': ['yen', 'jpy', 'bank of japan', 'boj', 'kuroda'],
            'CHF': ['franc', 'chf', 'swiss national bank', 'snb'],
            'CAD': ['cad', 'canadian dollar', 'bank of canada', 'boc'],
            'AUD': ['aud', 'australian dollar', 'reserve bank', 'rba']
        }

    async def get_financial_news(self, hours_back: int = 24) -> List[NewsItem]:
        """Fetch recent financial news."""

        if self.provider == "newsapi":
            return await self._fetch_newsapi_data(hours_back)
        elif self.provider == "alpha_vantage":
            return await self._fetch_alpha_vantage_news(hours_back)
        else:
            print(f"❌ Unknown news provider: {self.provider}")
            return []

    async def _fetch_newsapi_data(self, hours_back: int) -> List[NewsItem]:
        """Fetch from NewsAPI."""

        from_date = (datetime.now() - timedelta(hours=hours_back)).isoformat()

        url = "https://newsapi.org/v2/everything"
        params = {
            'q': 'forex OR currency OR "central bank" OR "interest rates"',
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date,
            'apiKey': self.api_key
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_newsapi_response(data)
                    else:
                        print(f"❌ NewsAPI error: {response.status}")
                        return []

            except Exception as e:
                print(f"❌ News request failed: {e}")
                return []

    def _parse_newsapi_response(self, data: Dict) -> List[NewsItem]:
        """Parse NewsAPI response."""

        news_items = []

        for article in data.get('articles', []):
            try:
                # Parse timestamp
                published_at = datetime.fromisoformat(
                    article['publishedAt'].replace('Z', '+00:00')
                )

                # Combine title and description for analysis
                content = f"{article['title']} {article.get('description', '')}"

                # Analyze sentiment
                sentiment_score = self._analyze_sentiment(content)

                # Find relevant instruments
                instruments = self._find_relevant_instruments(content)

                # Calculate relevance score
                relevance_score = self._calculate_relevance(content, instruments)

                news_item = NewsItem(
                    timestamp=published_at,
                    title=article['title'],
                    content=content,
                    source=article.get('source', {}).get('name', 'Unknown'),
                    instruments_mentioned=instruments,
                    sentiment_score=sentiment_score,
                    relevance_score=relevance_score
                )

                news_items.append(news_item)

            except Exception as e:
                print(f"⚠️ Failed to parse article: {e}")
                continue

        return news_items

    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment using TextBlob."""

        try:
            blob = TextBlob(text)
            # Return polarity (-1 to 1, where -1 is negative, 1 is positive)
            return blob.sentiment.polarity
        except Exception:
            return 0.0  # Neutral if analysis fails

    def _find_relevant_instruments(self, text: str) -> List[str]:
        """Find currency pairs mentioned in text."""

        text_lower = text.lower()
        mentioned_currencies = []

        # Find mentioned currencies
        for currency, keywords in self.currency_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    mentioned_currencies.append(currency)
                    break

        # Generate instrument pairs
        instruments = []

        # If multiple currencies mentioned, create pairs
        if len(mentioned_currencies) >= 2:
            for i, curr1 in enumerate(mentioned_currencies):
                for curr2 in mentioned_currencies[i+1:]:
                    instruments.extend([f"{curr1}_{curr2}", f"{curr2}_{curr1}"])

        # If only one currency, pair with USD
        elif len(mentioned_currencies) == 1:
            currency = mentioned_currencies[0]
            if currency != 'USD':
                instruments.extend([f"{currency}_USD", f"USD_{currency}"])

        return list(set(instruments))  # Remove duplicates

    def _calculate_relevance(self, text: str, instruments: List[str]) -> float:
        """Calculate relevance score (0-1)."""

        relevance_keywords = [
            'central bank', 'interest rate', 'monetary policy',
            'inflation', 'gdp', 'employment', 'trade war',
            'economic data', 'fed', 'ecb', 'boe', 'boj'
        ]

        text_lower = text.lower()
        keyword_count = sum(1 for keyword in relevance_keywords if keyword in text_lower)

        # Base relevance on keyword matches and instrument mentions
        base_score = min(keyword_count * Decimal("0.2"), Decimal("1.0"))
        instrument_bonus = min(len(instruments) * 0.1, 0.3)

        return min(base_score + instrument_bonus, 1.0)

class NewsSentimentTrading:
    """Trading system that incorporates news sentiment."""

    def __init__(self, fivetwenty_client: AsyncClient, news_provider: NewsProvider):
        self.fivetwenty_client = fivetwenty_client
        self.news_provider = news_provider
        self.news_cache = []
        self.sentiment_threshold = 0.3  # Minimum sentiment for trading

    async def update_news_sentiment(self):
        """Update news sentiment analysis."""

        news_items = await self.news_provider.get_financial_news(hours_back=6)

        # Filter for high relevance news
        relevant_news = [
            news for news in news_items
            if news.relevance_score > 0.5 and abs(news.sentiment_score) > 0.2
        ]

        self.news_cache = relevant_news
        print(f"📰 Loaded {len(relevant_news)} relevant news items")

        # Log significant sentiment
        for news in relevant_news:
            if abs(news.sentiment_score) > 0.5:
                sentiment = "POSITIVE" if news.sentiment_score > 0 else "NEGATIVE"
                print(f"📈 {sentiment} news: {news.title[:50]}... (Score: {news.sentiment_score:.2f})")

    def get_instrument_sentiment(self, instrument: str) -> Dict[str, float]:
        """Get aggregated sentiment for an instrument."""

        relevant_news = [
            news for news in self.news_cache
            if instrument in news.instruments_mentioned
        ]

        if not relevant_news:
            return {'sentiment': 0.0, 'confidence': 0.0, 'news_count': 0}

        # Weight sentiment by relevance and recency
        weighted_sentiment = 0.0
        total_weight = 0.0

        now = datetime.now(timezone.utc)

        for news in relevant_news:
            # Recency weight (decay over 24 hours)
            hours_old = (now - news.timestamp).total_seconds() / 3600
            recency_weight = max(0.1, 1.0 - (hours_old / 24))

            # Combined weight
            weight = news.relevance_score * recency_weight

            weighted_sentiment += news.sentiment_score * weight
            total_weight += weight

        if total_weight > 0:
            avg_sentiment = weighted_sentiment / total_weight
            confidence = min(total_weight / len(relevant_news), 1.0)
        else:
            avg_sentiment = 0.0
            confidence = 0.0

        return {
            'sentiment': avg_sentiment,
            'confidence': confidence,
            'news_count': len(relevant_news)
        }

    async def sentiment_informed_trading(self, account_id: str, instrument: str,
                                       base_units: int) -> Optional[Dict]:
        """Place trades informed by news sentiment."""

        sentiment_data = self.get_instrument_sentiment(instrument)

        if sentiment_data['news_count'] == 0:
            print(f"📰 No news sentiment for {instrument} - trading normally")
            units = base_units
        else:
            sentiment = sentiment_data['sentiment']
            confidence = sentiment_data['confidence']

            print(f"📊 {instrument} sentiment: {sentiment:.2f} (confidence: {confidence:.2f})")

            # Adjust position size based on sentiment and confidence
            if confidence < 0.3:
                print(f"⚠️ Low confidence news - reducing position size")
                units = int(base_units * Decimal("0.5"))
            elif abs(sentiment) > self.sentiment_threshold:
                # Strong sentiment - adjust direction and size
                sentiment_multiplier = 1.0 + (confidence * abs(sentiment))
                units = int(base_units * sentiment_multiplier)

                # Reverse direction if sentiment is negative
                if sentiment < 0:
                    units = -units

                print(f"📈 Strong sentiment detected - adjusted units: {units}")
            else:
                units = base_units

        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Sentiment-informed trade: {instrument} {units} @ {fill.price}")

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'sentiment_score': sentiment_data['sentiment'],
                    'confidence': sentiment_data['confidence'],
                    'units': units
                }
            else:
                print(f"❌ Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"❌ Trading error: {e}")
            return None

# Usage example
async def news_sentiment_trading_example():
    """Example of trading with news sentiment analysis."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as fivetwenty_client:
        news_provider = NewsProvider(api_key="your-newsapi-key")
        trading_system = NewsSentimentTrading(fivetwenty_client, news_provider)

        # Update news sentiment
        await trading_system.update_news_sentiment()

        # Make sentiment-informed trades
        account_id = "101-001-1234567-001"

        trades = []
        for instrument in ["EUR_USD", "GBP_USD", "USD_JPY"]:
            result = await trading_system.sentiment_informed_trading(
                account_id, instrument, base_units=10000
            )
            if result:
                trades.append(result)

        print(f"📊 Placed {len(trades)} sentiment-informed trades")
        return trades

# Example usage
# trades = await news_sentiment_trading_example()
```

---

## Technical Analysis Integration

### External Technical Indicators

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
        candles_response = await self.fivetwenty_client.instruments.candles(
            instrument=instrument,
            count=periods,
            granularity=timeframe
        )

        # Convert to pandas DataFrame
        df = self._candles_to_dataframe(candles_response.candles)

        if len(df) < 50:
            print(f"⚠️ Insufficient data for analysis: {len(df)} candles")
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
            print(f"⚠️ Error calculating trend indicators: {e}")

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
            print(f"⚠️ Error calculating momentum indicators: {e}")

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
            print(f"⚠️ Error calculating volatility indicators: {e}")

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
            print(f"⚠️ Error calculating volume indicators: {e}")

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
            print(f"⚠️ Error calculating support/resistance: {e}")

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
            print(f"\n📊 Analyzing {instrument}...")

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

---

## Alternative Data Sources

### Social Sentiment Integration

Integrate social media sentiment data:

```python
from fivetwenty import AsyncClient, Environment

import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict
import asyncio

class SocialSentimentProvider:
    """Social media sentiment analysis for forex."""

    def __init__(self, twitter_bearer_token: str):
        self.twitter_client = tweepy.Client(bearer_token=twitter_bearer_token)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Forex-related Twitter accounts to monitor
        self.forex_accounts = [
            'federalreserve', 'ecb', 'bankofengland',
            'bankofcanada', 'rba_gov', 'boj_en'
        ]

        # Currency-related hashtags and keywords
        self.currency_keywords = {
            'USD': ['#USD', '#Dollar', '#Fed', '#FOMC'],
            'EUR': ['#EUR', '#Euro', '#ECB', '#Lagarde'],
            'GBP': ['#GBP', '#Pound', '#Sterling', '#BoE'],
            'JPY': ['#JPY', '#Yen', '#BoJ', '#Kuroda']
        }

    async def get_social_sentiment(self, currencies: List[str], hours_back: int = 24) -> Dict[str, Dict]:
        """Get aggregated social sentiment for currencies."""

        sentiment_data = {}

        for currency in currencies:
            try:
                # Get tweets for currency
                tweets = await self._fetch_currency_tweets(currency, hours_back)

                if tweets:
                    # Analyze sentiment
                    sentiment_scores = [self._analyze_tweet_sentiment(tweet) for tweet in tweets]

                    # Aggregate sentiment
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)

                    # Calculate confidence based on volume and consistency
                    sentiment_std = np.std(sentiment_scores) if len(sentiment_scores) > 1 else 0
                    volume_factor = min(len(tweets) / 100, 1.0)  # Normalize to max 100 tweets
                    consistency_factor = max(0.1, 1.0 - sentiment_std)
                    confidence = volume_factor * consistency_factor

                    sentiment_data[currency] = {
                        'sentiment': avg_sentiment,
                        'confidence': confidence,
                        'tweet_count': len(tweets),
                        'sample_tweets': tweets[:3]  # Store sample tweets
                    }

                else:
                    sentiment_data[currency] = {
                        'sentiment': 0.0,
                        'confidence': 0.0,
                        'tweet_count': 0,
                        'sample_tweets': []
                    }

            except Exception as e:
                print(f"❌ Error getting sentiment for {currency}: {e}")
                sentiment_data[currency] = {
                    'sentiment': 0.0,
                    'confidence': 0.0,
                    'tweet_count': 0,
                    'sample_tweets': []
                }

        return sentiment_data

    async def _fetch_currency_tweets(self, currency: str, hours_back: int) -> List[str]:
        """Fetch recent tweets related to a currency."""

        keywords = self.currency_keywords.get(currency, [])
        if not keywords:
            return []

        # Create search query
        query = ' OR '.join(keywords) + ' -is:retweet lang:en'

        try:
            # Search recent tweets
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=query,
                max_results=100
            ).flatten(limit=200)

            # Extract tweet text
            tweet_texts = []
            for tweet in tweets:
                if tweet.created_at and tweet.text:
                    # Check if tweet is within time window
                    tweet_age = (datetime.now(timezone.utc) - tweet.created_at).total_seconds() / 3600
                    if tweet_age <= hours_back:
                        tweet_texts.append(tweet.text)

            return tweet_texts

        except Exception as e:
            print(f"❌ Twitter API error: {e}")
            return []

    def _analyze_tweet_sentiment(self, tweet_text: str) -> float:
        """Analyze sentiment of a single tweet."""

        try:
            # Use VADER sentiment analyzer
            scores = self.sentiment_analyzer.polarity_scores(tweet_text)

            # Return compound score (-1 to 1)
            return scores['compound']

        except Exception:
            return 0.0  # Neutral if analysis fails

class SocialTradingSystem:
    """Trading system incorporating social sentiment."""

    def __init__(self, fivetwenty_client: AsyncClient, social_provider: SocialSentimentProvider):
        self.fivetwenty_client = fivetwenty_client
        self.social_provider = social_provider
        self.sentiment_cache = {}

    async def update_social_sentiment(self):
        """Update social sentiment for major currencies."""

        currencies = ['USD', 'EUR', 'GBP', 'JPY']
        self.sentiment_cache = await self.social_provider.get_social_sentiment(currencies)

        print("📱 Social Sentiment Summary:")
        for currency, data in self.sentiment_cache.items():
            sentiment_label = "POSITIVE" if data['sentiment'] > 0.1 else "NEGATIVE" if data['sentiment'] < -0.1 else "NEUTRAL"
            print(f"  {currency}: {sentiment_label} ({data['sentiment']:.3f}, {data['tweet_count']} tweets)")

    def get_pair_sentiment_bias(self, instrument: str) -> Dict[str, float]:
        """Get sentiment bias for a currency pair."""

        # Extract currencies from instrument (e.g., EUR_USD -> EUR, USD)
        currencies = instrument.split('_')
        if len(currencies) != 2:
            return {'bias': 0.0, 'confidence': 0.0}

        base_currency, quote_currency = currencies

        # Get sentiment for each currency
        base_sentiment = self.sentiment_cache.get(base_currency, {})
        quote_sentiment = self.sentiment_cache.get(quote_currency, {})

        # Calculate bias (positive = favor base currency)
        base_score = base_sentiment.get('sentiment', 0.0)
        quote_score = quote_sentiment.get('sentiment', 0.0)

        # Sentiment bias: positive base sentiment or negative quote sentiment = buy bias
        sentiment_bias = base_score - quote_score

        # Confidence based on both currencies having data
        base_conf = base_sentiment.get('confidence', 0.0)
        quote_conf = quote_sentiment.get('confidence', 0.0)
        combined_confidence = (base_conf + quote_conf) / 2

        return {
            'bias': sentiment_bias,
            'confidence': combined_confidence,
            'base_sentiment': base_score,
            'quote_sentiment': quote_score,
            'base_tweets': base_sentiment.get('tweet_count', 0),
            'quote_tweets': quote_sentiment.get('tweet_count', 0)
        }

    async def social_sentiment_trade(self, account_id: str, instrument: str,
                                   base_units: int, min_confidence: float = 0.3) -> Optional[Dict]:
        """Execute trade with social sentiment bias."""

        sentiment_data = self.get_pair_sentiment_bias(instrument)

        if sentiment_data['confidence'] < min_confidence:
            print(f"📱 {instrument}: Low social sentiment confidence - trading normally")
            units = base_units
        else:
            bias = sentiment_data['bias']
            confidence = sentiment_data['confidence']

            print(f"📱 {instrument} social bias: {bias:.3f} (confidence: {confidence:.2f})")

            # Adjust position based on sentiment bias
            if abs(bias) > 0.2:  # Significant bias threshold
                bias_multiplier = 1.0 + (confidence * abs(bias) * 2)
                units = int(base_units * bias_multiplier)

                # Apply bias direction
                if bias > 0:
                    # Positive bias = buy base currency
                    units = abs(units)
                else:
                    # Negative bias = sell base currency
                    units = -abs(units)

                print(f"📈 Social sentiment adjusted units: {units}")
            else:
                units = base_units

        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Social-sentiment trade: {instrument} {units} @ {fill.price}")

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'sentiment_bias': sentiment_data['bias'],
                    'confidence': sentiment_data['confidence'],
                    'units': units
                }
            else:
                print(f"❌ Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"❌ Social sentiment trading error: {e}")
            return None

# Usage example
async def social_sentiment_integration_example():
    """Example of social sentiment integration."""

    async with AsyncClient(token="your-token", environment=Environment.PRACTICE) as fivetwenty_client:
        social_provider = SocialSentimentProvider(twitter_bearer_token="your-twitter-token")
        social_system = SocialTradingSystem(fivetwenty_client, social_provider)

        # Update social sentiment
        await social_system.update_social_sentiment()

        # Execute social sentiment-informed trades
        account_id = "101-001-1234567-001"

        instruments = ["EUR_USD", "GBP_USD", "USD_JPY"]
        trades = []

        for instrument in instruments:
            result = await social_system.social_sentiment_trade(
                account_id, instrument, base_units=8000, min_confidence=0.2
            )
            if result:
                trades.append(result)

        print(f"📱 Executed {len(trades)} social sentiment-informed trades")
        return trades

# Example usage
# trades = await social_sentiment_integration_example()
```

---

## Data Pipeline Integration

### Unified Data Pipeline

Combine all external data sources into a unified system:

```python
from fivetwenty import AsyncClient, Environment

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime, timedelta

@dataclass
class MarketContext:
    """Unified market context from all data sources."""

    timestamp: datetime
    instrument: str

    # OANDA price data
    current_price: float
    spread: float

    # Technical analysis
    technical_signal: str  # BUY, SELL, NEUTRAL
    technical_strength: float
    technical_reasons: List[str]

    # Economic calendar
    upcoming_events: List[str]
    trading_allowed: bool

    # News sentiment
    news_sentiment: float
    news_confidence: float
    news_count: int

    # Social sentiment
    social_bias: float
    social_confidence: float

    # Combined analysis
    final_signal: str
    signal_strength: float
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
        self.economic_system = TradingWithEconomicData(fivetwenty_client, self.economic_calendar)
        self.news_system = NewsSentimentTrading(fivetwenty_client, self.news_provider)
        self.signal_generator = AdvancedTradingSignals(self.ta_provider)
        self.social_system = SocialTradingSystem(fivetwenty_client, self.social_provider)

        # Data cache
        self.market_context_cache = {}

    async def initialize_all_data_sources(self):
        """Initialize all external data sources."""

        print("🔄 Initializing unified data pipeline...")

        # Initialize all systems concurrently
        initialization_tasks = [
            self.economic_system.update_economic_events(),
            self.news_system.update_news_sentiment(),
            self.social_system.update_social_sentiment()
        ]

        await asyncio.gather(*initialization_tasks, return_exceptions=True)
        print("✅ All data sources initialized")

    async def get_unified_market_context(self, instrument: str) -> MarketContext:
        """Get comprehensive market context for an instrument."""

        print(f"📊 Building unified market context for {instrument}...")

        # Get current OANDA price
        prices = await self.fivetwenty_client.pricing.get("101-001-1234567-001", [instrument])
        current_price_data = prices[0]

        current_price = float(current_price_data.asks[0].price)
        spread = float(current_price_data.asks[0].price) - float(current_price_data.bids[0].price)

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
            technical_strength=technical_analysis.get('strength', 0),
            technical_reasons=technical_analysis.get('reasons', []),

            # Economic calendar
            upcoming_events=economic_context.get('upcoming_events', []),
            trading_allowed=economic_context.get('trading_allowed', True),

            # News sentiment
            news_sentiment=news_context.get('sentiment', 0),
            news_confidence=news_context.get('confidence', 0),
            news_count=news_context.get('news_count', 0),

            # Social sentiment
            social_bias=social_context.get('bias', 0),
            social_confidence=social_context.get('confidence', 0),

            # Combined analysis (calculated below)
            final_signal='NEUTRAL',
            signal_strength=0,
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
        trading_allowed = self.economic_system.is_trading_allowed(instrument)

        # Get relevant upcoming events
        for blackout in self.economic_system.trading_blackout_periods:
            if blackout['currency'] in instrument:
                time_until = (blackout['start'] - datetime.now(timezone.utc)).total_seconds() / 3600
                if 0 < time_until < 24:  # Next 24 hours
                    upcoming_events.append(f"{blackout['event']} in {time_until:.1f}h")

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
        print(f"\n📊 Unified Analysis for {instrument}:")
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
            print(f"❌ No trading signal or trading blocked - skipping {instrument}")
            return None

        final_units = int(base_units * risk_multiplier * signal_multiplier)

        if context.final_signal == 'SELL':
            final_units = -final_units

        print(f"🎯 Calculated position size: {final_units} units (Risk: {risk_multiplier:.1f}x, Signal: {signal_multiplier:.2f}x)")

        # Execute trade
        try:
            response = await self.fivetwenty_client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=final_units
            )

            if response.order_fill_transaction:
                fill = response.order_fill_transaction
                print(f"✅ Unified trade executed: {instrument} {final_units} @ {fill.price}")

                # Log detailed context
                context_dict = asdict(context)
                context_dict['timestamp'] = context_dict['timestamp'].isoformat()

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'units': final_units,
                    'fill_price': float(fill.price),
                    'market_context': context_dict
                }
            else:
                print(f"❌ Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"❌ Unified trading error: {e}")
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

        print(f"📄 Market context exported to {filepath}")

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

        print(f"\n🎯 Unified Trading Summary:")
        print(f"   Executed {len(trades)} trades based on comprehensive analysis")
        print(f"   Market context exported for {len(unified_system.market_context_cache)} instruments")

        return trades

# Example usage
# trades = await unified_trading_system_example()
```

**Task Complete**: External data integration guide provides comprehensive patterns for combining FiveTwenty with economic calendars, news sentiment, technical analysis, social media data, and unified data pipelines for enhanced trading decisions.