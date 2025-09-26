# Financial News Integration

**Problem**: You need to integrate real-time financial news and sentiment analysis to make more informed trading decisions.

**Solution**: Implement news providers that fetch financial news from multiple sources, analyze sentiment, and adjust trading strategies based on market-moving events.

---

## Prerequisites

- FiveTwenty configured and working
- Understanding of async programming patterns
- Access to news API (NewsAPI, Alpha Vantage, etc.)
- Basic knowledge of sentiment analysis concepts
- TextBlob or similar NLP library for sentiment analysis

---

## Real-Time News Analysis

Integrate with news APIs for sentiment analysis:

```python
from decimal import Decimal
from fivetwenty import AsyncClient, Environment

import re
from textblob import TextBlob
from typing import List, Dict, Tuple, Optional
import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass


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

    def __init__(self, api_key: str, provider: str = "newsapi") -> None:
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
            print(f"Unknown news provider: {self.provider}")
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
                        print(f"NewsAPI error: {response.status}")
                        return []

            except Exception as e:
                print(f"News request failed: {e}")
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
                print(f"Failed to parse article: {e}")
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

    def __init__(self, fivetwenty_client: AsyncClient, news_provider: NewsProvider) -> None:
        self.fivetwenty_client = fivetwenty_client
        self.news_provider = news_provider
        self.news_cache = []
        self.sentiment_threshold = 0.3  # Minimum sentiment for trading

    async def update_news_sentiment(self) -> Any:
        """Update news sentiment analysis."""

        news_items = await self.news_provider.get_financial_news(hours_back=6)

        # Filter for high relevance news
        relevant_news = [
            news for news in news_items
            if news.relevance_score > 0.5 and abs(news.sentiment_score) > 0.2
        ]

        self.news_cache = relevant_news
        print(f"Loaded {len(relevant_news)} relevant news items")

        # Log significant sentiment
        for news in relevant_news:
            if abs(news.sentiment_score) > 0.5:
                sentiment = "POSITIVE" if news.sentiment_score > 0 else "NEGATIVE"
                print(f"{sentiment} news: {news.title[:50]}... (Score: {news.sentiment_score:.2f})")

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
            print(f"No news sentiment for {instrument} - trading normally")
            units = base_units
        else:
            sentiment = sentiment_data['sentiment']
            confidence = sentiment_data['confidence']

            print(f"{instrument} sentiment: {sentiment:.2f} (confidence: {confidence:.2f})")

            # Adjust position size based on sentiment and confidence
            if confidence < 0.3:
                print(f"Low confidence news - reducing position size")
                units = int(base_units * Decimal("0.5"))
            elif abs(sentiment) > self.sentiment_threshold:
                # Strong sentiment - adjust direction and size
                sentiment_multiplier = 1.0 + (confidence * abs(sentiment))
                units = int(base_units * sentiment_multiplier)

                # Reverse direction if sentiment is negative
                if sentiment < 0:
                    units = -units

                print(f"Strong sentiment detected - adjusted units: {units}")
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
                print(f"Sentiment-informed trade: {instrument} {units} @ {fill.price}")

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'sentiment_score': sentiment_data['sentiment'],
                    'confidence': sentiment_data['confidence'],
                    'units': units
                }
            else:
                print(f"Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"Trading error: {e}")
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

        print(f"Placed {len(trades)} sentiment-informed trades")
        return trades

# Example usage
# trades = await news_sentiment_trading_example()
```

## Advanced News Integration

### Multi-Source News Aggregation

For production systems, combine multiple news sources:

```python
class MultiSourceNewsProvider:
    """Aggregate news from multiple sources."""

    def __init__(self, news_apis: Dict[str, str]) -> None:
        self.providers = {}

        for provider_name, api_key in news_apis.items():
            self.providers[provider_name] = NewsProvider(api_key, provider_name)

    async def get_aggregated_news(self, hours_back: int = 24) -> List[NewsItem]:
        """Get news from all configured providers."""

        all_news = []

        tasks = []
        for provider in self.providers.values():
            tasks.append(provider.get_financial_news(hours_back))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_news.extend(result)
            else:
                print(f"Provider error: {result}")

        # Remove duplicates based on title similarity
        return self._deduplicate_news(all_news)

    def _deduplicate_news(self, news_items: List[NewsItem]) -> List[NewsItem]:
        """Remove duplicate news items."""

        unique_news = []
        seen_titles = set()

        for news in sorted(news_items, key=lambda x: x.timestamp, reverse=True):
            # Simple deduplication based on title similarity
            title_lower = news.title.lower()
            is_duplicate = any(
                self._title_similarity(title_lower, seen_title) > 0.8
                for seen_title in seen_titles
            )

            if not is_duplicate:
                unique_news.append(news)
                seen_titles.add(title_lower)

        return unique_news

    def _title_similarity(self, title1: str, title2: str) -> float:
        """Calculate title similarity (simple word overlap)."""

        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return 0.0

        overlap = len(words1.intersection(words2))
        total = len(words1.union(words2))

        return overlap / total if total > 0 else 0.0
```

### Real-Time News Monitoring

Implement continuous news monitoring:

```python
from datetime import datetime


class RealTimeNewsMonitor:
    """Monitor news in real-time with alerts."""

    def __init__(self, news_provider: NewsProvider) -> None:
        self.news_provider = news_provider
        self.monitoring = False
        self.alert_callbacks = []
        self.last_check = datetime.now(timezone.utc)

    async def start_monitoring(self, check_interval_minutes: int = 5) -> Any:
        """Start real-time news monitoring."""

        self.monitoring = True

        while self.monitoring:
            try:
                await self._check_breaking_news()
                await asyncio.sleep(check_interval_minutes * 60)

            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute

    async def _check_breaking_news(self) -> Any:
        """Check for breaking news since last check."""

        now = datetime.now(timezone.utc)
        hours_back = max(1, (now - self.last_check).total_seconds() / 3600)

        news_items = await self.news_provider.get_financial_news(hours_back=hours_back)

        # Filter for breaking news
        breaking_news = [
            news for news in news_items
            if news.timestamp > self.last_check and
               news.relevance_score > 0.7 and
               abs(news.sentiment_score) > 0.4
        ]

        if breaking_news:
            for news in breaking_news:
                await self._trigger_alerts(news)

        self.last_check = now

    async def _trigger_alerts(self, news: NewsItem) -> Any:
        """Trigger alerts for breaking news."""

        alert_data = {
            "timestamp": news.timestamp,
            "title": news.title,
            "sentiment": news.sentiment_score,
            "relevance": news.relevance_score,
            "instruments": news.instruments_mentioned,
        }

        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                # Expected output: f"Alert callback error: {e}"
                pass

    def add_alert_callback(self, callback: Any) -> Any:
        """Add callback for news alerts."""
        self.alert_callbacks.append(callback)

    def stop_monitoring(self) -> Any:
        """Stop news monitoring."""
        self.monitoring = False
```

## Best Practices

### Sentiment Analysis Enhancement

```python

class EnhancedSentimentAnalyzer:
    """Class docstring."""
    """Enhanced sentiment analysis with financial context."""

    def __init__(self) -> None:
        self.financial_keywords = {
            "positive": [
                "bullish", "surge", "rally", "gains", "optimistic",
                "breakthrough", "strong", "outperform", "beat expectations",
            ],
            "negative": [
                "bearish", "plunge", "crash", "losses", "pessimistic",
                "concerns", "weak", "underperform", "miss expectations",
            ],
        }

    def analyze_financial_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment with financial context."""

        # Basic TextBlob sentiment
        blob = TextBlob(text)
        base_sentiment = blob.sentiment.polarity

        # Financial keyword adjustment
        text_lower = text.lower()

        positive_count = sum(1 for word in self.financial_keywords["positive"]
                           if word in text_lower)
        negative_count = sum(1 for word in self.financial_keywords["negative"]
                           if word in text_lower)

        # Adjust sentiment based on financial keywords
        keyword_adjustment = (positive_count - negative_count) * 0.1

        final_sentiment = max(-1.0, min(1.0, base_sentiment + keyword_adjustment))

        return {
            "sentiment": final_sentiment,
            "base_sentiment": base_sentiment,
            "keyword_adjustment": keyword_adjustment,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count,
        }
```

### Position Sizing with News Impact

```python

def calculate_news_adjusted_position_size(
    base_size: int,
    sentiment_score: float,
    confidence: float,
    news_count: int
) -> int:
    """Adjust position size based on news sentiment."""

    # No news adjustment
    if news_count == 0:
        return base_size

    # Low confidence - reduce size
    if confidence < 0.3:
        return int(base_size * 0.5)

    # High confidence sentiment - amplify
    if confidence > 0.7 and abs(sentiment_score) > 0.5:
        multiplier = 1.0 + (confidence * abs(sentiment_score) * 0.5)
        adjusted_size = int(base_size * multiplier)

        # Reverse direction for negative sentiment
        if sentiment_score < 0:
            adjusted_size = -adjusted_size

        return adjusted_size

    return base_size
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: News APIs often have strict rate limits
   - Implement caching with appropriate TTL
   - Use multiple API keys if available
   - Add exponential backoff for failed requests

2. **Sentiment Accuracy**: Basic sentiment analysis can be inaccurate
   - Combine multiple sentiment analysis libraries
   - Train custom models on financial text
   - Use human validation for critical decisions

3. **News Relevance**: Not all financial news affects forex markets
   - Implement sophisticated relevance scoring
   - Focus on central bank communications
   - Filter by news source credibility

## Next Steps

- **[Technical Indicators Integration](technical-indicators.md)** - Enhance with technical analysis
- **[Social Sentiment Integration](social-sentiment.md)** - Add social media sentiment
- **[Unified Data Pipeline](unified-pipeline.md)** - Combine multiple data sources

---

## Related Guides

- [Economic Calendar Integration](economic-calendar.md)
- [Risk Management Tutorial](../../tutorials/risk-management/index.md)
- [Production Deployment](../production-deployment/index.md)