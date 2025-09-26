# Social Sentiment Integration

**Problem**: You need to incorporate social media sentiment and market psychology into your trading decisions to gain additional market insights.

**Solution**: Integrate with social media APIs to analyze sentiment from Twitter, Reddit, and other platforms, focusing on central bank communications and currency-related discussions.

---

## Prerequisites

- FiveTwenty configured and working
- Understanding of sentiment analysis concepts
- Twitter API access (Bearer Token)
- Required libraries: `tweepy`, `vaderSentiment`, `numpy`
- Basic knowledge of social media data analysis

---

## Social Media Sentiment Analysis

Integrate social media sentiment data:

```python
from fivetwenty import AsyncClient, Environment

import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Optional
import asyncio
import numpy as np
from datetime import datetime, timedelta, timezone

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
            'JPY': ['#JPY', '#Yen', '#BoJ', '#Kuroda'],
            'CHF': ['#CHF', '#Franc', '#SNB'],
            'CAD': ['#CAD', '#BoC', '#Macklem'],
            'AUD': ['#AUD', '#RBA', '#Lowe']
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
                print(f"Error getting sentiment for {currency}: {e}")
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
            print(f"Twitter API error: {e}")
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

        print("Social Sentiment Summary:")
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
            print(f"{instrument}: Low social sentiment confidence - trading normally")
            units = base_units
        else:
            bias = sentiment_data['bias']
            confidence = sentiment_data['confidence']

            print(f"{instrument} social bias: {bias:.3f} (confidence: {confidence:.2f})")

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

                print(f"Social sentiment adjusted units: {units}")
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
                print(f"Social-sentiment trade: {instrument} {units} @ {fill.price}")

                return {
                    'trade_id': fill.trade_opened.trade_id if fill.trade_opened else None,
                    'sentiment_bias': sentiment_data['bias'],
                    'confidence': sentiment_data['confidence'],
                    'units': units
                }
            else:
                print(f"Order rejected: {instrument}")
                return None

        except Exception as e:
            print(f"Social sentiment trading error: {e}")
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

        print(f"Executed {len(trades)} social sentiment-informed trades")
        return trades

# Example usage
# trades = await social_sentiment_integration_example()
```

## Advanced Social Media Analysis

### Multi-Platform Sentiment Aggregation

Combine sentiment from multiple social platforms:

```python

"""Module docstring."""
class MultiPlatformSentimentProvider:
    """Class docstring."""
    """Aggregate sentiment from multiple social platforms."""

    def __init__(self, twitter_token: str, reddit_credentials: Dict = None) -> None:
        self.twitter_provider = SocialSentimentProvider(twitter_token)
        self.reddit_credentials = reddit_credentials

        # Platform weights for aggregation
        self.platform_weights = {
            "twitter": 0.6,
            "reddit": 0.4,
        }

    async def get_aggregated_sentiment(self, currencies: List[str], hours_back: int = 24) -> Dict[str, Dict]:
        """Get sentiment aggregated from multiple platforms."""

        # Get Twitter sentiment
        twitter_sentiment = await self.twitter_provider.get_social_sentiment(currencies, hours_back)

        # Get Reddit sentiment (if configured)
        reddit_sentiment = {}
        if self.reddit_credentials:
            reddit_sentiment = await self._get_reddit_sentiment(currencies, hours_back)

        # Aggregate sentiments
        aggregated_sentiment = {}

        for currency in currencies:
            twitter_data = twitter_sentiment.get(currency, {})
            reddit_data = reddit_sentiment.get(currency, {})

            # Weighted sentiment calculation
            twitter_weight = self.platform_weights["twitter"]
            reddit_weight = self.platform_weights["reddit"] if reddit_data else 0

            # Normalize weights if Reddit not available
            total_weight = twitter_weight + reddit_weight
            if total_weight > 0:
                twitter_weight /= total_weight
                reddit_weight /= total_weight

            # Calculate weighted sentiment
            weighted_sentiment = (
                twitter_data.get("sentiment", 0) * twitter_weight +
                reddit_data.get("sentiment", 0) * reddit_weight
            )

            # Combined confidence
            combined_confidence = (
                twitter_data.get("confidence", 0) * twitter_weight +
                reddit_data.get("confidence", 0) * reddit_weight
            )

            aggregated_sentiment[currency] = {
                "sentiment": weighted_sentiment,
                "confidence": combined_confidence,
                "sources": {
                    "twitter": twitter_data,
                    "reddit": reddit_data,
                },
                "total_mentions": (
                    twitter_data.get("tweet_count", 0) +
                    reddit_data.get("post_count", 0)
                ),
            }

        return aggregated_sentiment

    async def _get_reddit_sentiment(self, currencies: List[str], hours_back: int) -> Dict[str, Dict]:
        """Get sentiment from Reddit (placeholder for Reddit API integration)."""

        # This would integrate with Reddit API using PRAW
        # For now, return empty data
        return {currency: {} for currency in currencies}
```

### Real-Time Social Media Monitoring

Implement real-time monitoring of social media sentiment:

```python
class RealTimeSocialMonitor:
    """Real-time social media sentiment monitoring."""

    def __init__(self, social_provider: SocialSentimentProvider):
        self.social_provider = social_provider
        self.monitoring = False
        self.sentiment_history = {}
        self.alert_callbacks = []

    async def start_monitoring(self, currencies: List[str], check_interval_minutes: int = 10):
        """Start real-time sentiment monitoring."""

        self.monitoring = True

        while self.monitoring:
            try:
                # Get current sentiment
                current_sentiment = await self.social_provider.get_social_sentiment(
                    currencies, hours_back=1
                )

                # Check for significant changes
                for currency, data in current_sentiment.items():
                    await self._check_sentiment_changes(currency, data)

                # Store current sentiment
                timestamp = datetime.now(timezone.utc)
                for currency, data in current_sentiment.items():
                    if currency not in self.sentiment_history:
                        self.sentiment_history[currency] = []

                    self.sentiment_history[currency].append({
                        'timestamp': timestamp,
                        'sentiment': data['sentiment'],
                        'confidence': data['confidence'],
                        'tweet_count': data['tweet_count']
                    })

                    # Keep only last 24 hours of data
                    cutoff_time = timestamp - timedelta(hours=24)
                    self.sentiment_history[currency] = [
                        entry for entry in self.sentiment_history[currency]
                        if entry['timestamp'] > cutoff_time
                    ]

                await asyncio.sleep(check_interval_minutes * 60)

            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute

    async def _check_sentiment_changes(self, currency: str, current_data: Dict):
        """Check for significant sentiment changes."""

        if currency not in self.sentiment_history or not self.sentiment_history[currency]:
            return

        # Get recent sentiment history
        recent_entries = self.sentiment_history[currency][-5:]  # Last 5 measurements
        if len(recent_entries) < 2:
            return

        # Calculate sentiment trend
        recent_sentiments = [entry['sentiment'] for entry in recent_entries]
        current_sentiment = current_data['sentiment']

        # Check for sudden sentiment shift
        avg_recent = sum(recent_sentiments) / len(recent_sentiments)
        sentiment_change = abs(current_sentiment - avg_recent)

        # Alert if significant change detected
        if sentiment_change > 0.3 and current_data['confidence'] > 0.5:
            alert_data = {
                'currency': currency,
                'current_sentiment': current_sentiment,
                'previous_avg': avg_recent,
                'change': sentiment_change,
                'confidence': current_data['confidence'],
                'tweet_count': current_data['tweet_count'],
                'direction': 'POSITIVE' if current_sentiment > avg_recent else 'NEGATIVE'
            }

            await self._trigger_sentiment_alert(alert_data)

    async def _trigger_sentiment_alert(self, alert_data: Dict):
        """Trigger sentiment change alerts."""

        print(f"SENTIMENT ALERT: {alert_data['currency']} sentiment shifted {alert_data['direction']}")
        print(f"  Change: {alert_data['change']:.3f} (confidence: {alert_data['confidence']:.2f})")

        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                print(f"Alert callback error: {e}")

    def add_alert_callback(self, callback):
        """Add callback for sentiment alerts."""
        self.alert_callbacks.append(callback)

    def stop_monitoring(self):
        """Stop sentiment monitoring."""
        self.monitoring = False

    def get_sentiment_trend(self, currency: str, hours_back: int = 6) -> Dict:
        """Get sentiment trend analysis for a currency."""

        if currency not in self.sentiment_history:
            return {'trend': 'UNKNOWN', 'confidence': 0}

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        relevant_entries = [
            entry for entry in self.sentiment_history[currency]
            if entry['timestamp'] > cutoff_time
        ]

        if len(relevant_entries) < 3:
            return {'trend': 'INSUFFICIENT_DATA', 'confidence': 0}

        # Calculate trend direction
        sentiments = [entry['sentiment'] for entry in relevant_entries]

        # Simple linear trend
        x = list(range(len(sentiments)))
        slope = np.polyfit(x, sentiments, 1)[0] if len(sentiments) > 1 else 0

        if slope > 0.05:
            trend = 'IMPROVING'
        elif slope < -0.05:
            trend = 'DECLINING'
        else:
            trend = 'STABLE'

        # Confidence based on data volume and consistency
        avg_confidence = sum(entry['confidence'] for entry in relevant_entries) / len(relevant_entries)

        return {
            'trend': trend,
            'slope': slope,
            'confidence': avg_confidence,
            'data_points': len(relevant_entries),
            'time_span_hours': hours_back
        }
```

### Central Bank Communication Analysis

Focus on central bank communications for high-impact sentiment:

```python
class CentralBankSentimentAnalyzer:
    """Specialized analysis of central bank communications."""

    def __init__(self, twitter_token: str):
        self.twitter_client = tweepy.Client(bearer_token=twitter_token)
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Central bank accounts and their currencies
        self.central_banks = {
            "federalreserve": "USD",
            "ecb": "EUR",
            "bankofengland": "GBP",
            "boj_en": "JPY",
            "bankofcanada": "CAD",
            "rba_gov": "AUD",
            "snb_ch": "CHF",
        }

        # High-impact keywords
        self.policy_keywords = [
            "interest rate", "monetary policy", "inflation target",
            "quantitative easing", "tightening", "dovish", "hawkish",
            "stimulus", "tapering", "forward guidance",
        ]

    async def analyze_central_bank_communications(self, hours_back: int = 48) -> Dict[str, Dict]:
        """Analyze recent central bank communications."""

        bank_analysis = {}

        for bank_handle, currency in self.central_banks.items():
            try:
                # Get recent tweets from central bank
                tweets = await self._fetch_bank_tweets(bank_handle, hours_back)

                if tweets:
                    # Analyze each tweet
                    tweet_analyses = []
                    for tweet in tweets:
                        analysis = self._analyze_bank_tweet(tweet)
                        if analysis["policy_relevance"] > 0.5:  # Only policy-relevant tweets
                            tweet_analyses.append(analysis)

                    if tweet_analyses:
                        # Aggregate analysis
                        avg_sentiment = sum(t["sentiment"] for t in tweet_analyses) / len(tweet_analyses)
                        avg_hawkishness = sum(t["hawkish_score"] for t in tweet_analyses) / len(tweet_analyses)

                        bank_analysis[currency] = {
                            "sentiment": avg_sentiment,
                            "hawkish_score": avg_hawkishness,
                            "policy_tweets_count": len(tweet_analyses),
                            "total_tweets": len(tweets),
                            "recent_tweets": [t["text"] for t in tweet_analyses[:3]],
                        }

            except Exception as e:
                print(f"Error analyzing {bank_handle}: {e}")

        return bank_analysis

    async def _fetch_bank_tweets(self, username: str, hours_back: int) -> List[Dict]:
        """Fetch recent tweets from a central bank."""

        try:
            # Get user tweets
            tweets = tweepy.Paginator(
                self.twitter_client.get_users_tweets,
                username=username,
                max_results=100,
                tweet_fields=["created_at", "public_metrics"],
            ).flatten(limit=50)

            # Filter by time
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
            recent_tweets = []

            for tweet in tweets:
                if tweet.created_at and tweet.created_at > cutoff_time:
                    recent_tweets.append({
                        "text": tweet.text,
                        "created_at": tweet.created_at,
                        "metrics": tweet.public_metrics,
                    })

            return recent_tweets

        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")
            return []

    def _analyze_bank_tweet(self, tweet_data: Dict) -> Dict:
        """Analyze a single central bank tweet."""

        text = tweet_data["text"].lower()

        # Calculate basic sentiment
        sentiment_scores = self.sentiment_analyzer.polarity_scores(tweet_data["text"])
        sentiment = sentiment_scores["compound"]

        # Calculate policy relevance
        policy_relevance = sum(1 for keyword in self.policy_keywords if keyword in text) / len(self.policy_keywords)

        # Calculate hawkish/dovish bias
        hawkish_terms = ["tightening", "hawkish", "raise rates", "combat inflation", "reduce stimulus"]
        dovish_terms = ["easing", "dovish", "lower rates", "support economy", "increase stimulus"]

        hawkish_count = sum(1 for term in hawkish_terms if term in text)
        dovish_count = sum(1 for term in dovish_terms if term in text)

        # Hawkish score: positive = hawkish, negative = dovish
        total_policy_terms = hawkish_count + dovish_count
        if total_policy_terms > 0:
            hawkish_score = (hawkish_count - dovish_count) / total_policy_terms
        else:
            hawkish_score = 0

        return {
            "text": tweet_data["text"],
            "sentiment": sentiment,
            "hawkish_score": hawkish_score,
            "policy_relevance": policy_relevance,
            "created_at": tweet_data["created_at"],
            "engagement": tweet_data.get("metrics", {}).get("like_count", 0),
        }
```

## Best Practices

### Data Quality and Filtering

Ensure high-quality social media data:

```python

"""Module docstring."""
class SocialDataFilter:
    """Class docstring."""
    """Filter and validate social media data quality."""

    @staticmethod
    def filter_high_quality_tweets(tweets: List[str], min_length: int = 20) -> List[str]:
        """Filter tweets for quality."""

        filtered_tweets = []

        for tweet in tweets:
            # Remove retweets and mentions-heavy tweets
            if tweet.startswith('RT @') or tweet.count('@') > 3:
                continue

            # Remove very short tweets
            if len(tweet) < min_length:
                continue

            # Remove tweets with excessive emojis or special characters
            emoji_ratio = sum(1 for char in tweet if ord(char) > 127) / len(tweet)
            if emoji_ratio > 0.3:
                continue

            # Remove tweets with excessive hashtags
            hashtag_ratio = tweet.count('#') / len(tweet.split())
            if hashtag_ratio > 0.5:
                continue

            filtered_tweets.append(tweet)

        return filtered_tweets

    @staticmethod
    def detect_bot_accounts(tweet_data: Dict) -> bool:
        """Detect potential bot accounts."""

        metrics = tweet_data.get('metrics', {})

        # High follower-to-following ratio might indicate bot
        followers = metrics.get('followers_count', 0)
        following = metrics.get('following_count', 1)

        if followers > 0 and following > 0:
            ratio = followers / following
            if ratio > 100:  # Suspiciously high ratio
                return True

        # Very high tweet frequency might indicate bot
        tweet_count = metrics.get('tweet_count', 0)
        account_age_days = metrics.get('account_age_days', 1)

        tweets_per_day = tweet_count / account_age_days
        if tweets_per_day > 50:  # Suspiciously high frequency
            return True

        return False
```

### Sentiment Validation

Validate sentiment analysis results:

```python

"""Module docstring."""
class SentimentValidator:
    """Class docstring."""
    """Validate and improve sentiment analysis accuracy."""

    def __init__(self) -> None:
        self.financial_positive_terms = [
            "bullish", "optimistic", "strong", "growth", "recovery",
            "positive", "confident", "robust", "healthy", "improving",
        ]

        self.financial_negative_terms = [
            "bearish", "pessimistic", "weak", "decline", "recession",
            "negative", "concerned", "fragile", "deteriorating", "crisis",
        ]

    def enhance_financial_sentiment(self, text: str, base_sentiment: float) -> float:
        """Enhance sentiment with financial context."""

        text_lower = text.lower()

        # Count financial sentiment terms
        positive_count = sum(1 for term in self.financial_positive_terms if term in text_lower)
        negative_count = sum(1 for term in self.financial_negative_terms if term in text_lower)

        # Adjust sentiment based on financial terms
        financial_adjustment = (positive_count - negative_count) * 0.1

        # Apply adjustment but keep within bounds
        enhanced_sentiment = max(-1.0, min(1.0, base_sentiment + financial_adjustment))

        return enhanced_sentiment

    def validate_sentiment_consistency(self, sentiments: List[float], confidence_threshold: float = 0.3) -> bool:
        """Check if sentiment measurements are consistent."""

        if len(sentiments) < 3:
            return False

        # Calculate standard deviation
        std_dev = np.std(sentiments)

        # High standard deviation indicates inconsistent sentiment
        return std_dev < confidence_threshold
```

## Troubleshooting

### Common Issues

1. **Twitter API Rate Limits**: Twitter API has strict rate limits
   - Implement proper rate limiting and backoff
   - Use multiple API keys if available
   - Cache results appropriately

2. **Sentiment Analysis Accuracy**: Social media text can be noisy
   - Filter low-quality content
   - Use domain-specific sentiment analysis
   - Combine multiple sentiment engines

3. **Data Volume vs. Quality**: Balance between data volume and quality
   - Focus on authoritative sources
   - Filter bot accounts and spam
   - Weight recent data more heavily

## Next Steps

- **[Unified Data Pipeline](unified-pipeline.md)** - Combine with other data sources
- **[Financial News Integration](financial-news.md)** - Enhance with news analysis
- **[Technical Indicators Integration](technical-indicators.md)** - Add technical analysis

---

## Related Guides

- [Economic Calendar Integration](economic-calendar.md)
- [Risk Management Tutorial](../../tutorials/risk-management/index.md)
- [Production Deployment](../production-deployment/index.md)