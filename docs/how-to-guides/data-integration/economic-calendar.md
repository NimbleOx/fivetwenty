# Economic Calendar Integration

**Problem**: You need to avoid trading during high-impact economic events that can cause significant market volatility.

**Solution**: Integrate economic calendar data to automatically pause trading or adjust position sizes around major economic releases.

---

## Prerequisites

- FiveTwenty configured and working
- Understanding of async programming patterns
- Access to economic calendar API (ForexFactory, Economic Calendar API, etc.)
- Basic knowledge of economic events and their market impact

---

## News and Economic Events

Integrate economic calendar data to avoid trading during high-impact events:

```python
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
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

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = "https://api.forexfactory.com/v1"

    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        impact_filter: List[str] = None
    ) -> List[EconomicEvent]:
        """Fetch economic events for date range."""
        if impact_filter is None:
            impact_filter = ["HIGH", "MEDIUM"]

        params = {
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "impact": ",".join(impact_filter)
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/calendar",
                params=params,
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                data = await response.json()

                events = []
                for event_data in data.get("events", []):
                    event = EconomicEvent(
                        time=datetime.fromisoformat(event_data["date"]),
                        currency=event_data["currency"],
                        event=event_data["title"],
                        impact=event_data["impact"],
                        forecast=event_data.get("forecast"),
                        previous=event_data.get("previous"),
                        actual=event_data.get("actual")
                    )
                    events.append(event)

                return events

class EconomicAwareTradingSystem:
    """Trading system that considers economic events."""

    def __init__(self, client: AsyncClient, calendar: EconomicCalendarProvider) -> None:
        self.client = client
        self.calendar = calendar
        self.event_blackout_minutes = {
            "HIGH": 60,    # 1 hour before/after high impact
            "MEDIUM": 30,  # 30 minutes before/after medium impact
            "LOW": 0       # No blackout for low impact
        }

    async def is_safe_to_trade(
        self,
        currency_pair: str,
        check_time: datetime = None
    ) -> tuple[bool, Optional[EconomicEvent]]:
        """Check if it's safe to trade based on economic calendar."""
        if check_time is None:
            check_time = datetime.now(timezone.utc)

        # Get events for today
        start_date = check_time.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=1)

        events = await self.calendar.get_events(start_date, end_date)

        # Extract currencies from pair (e.g., "EUR_USD" -> ["EUR", "USD"])
        currencies = currency_pair.split("_")

        for event in events:
            if event.currency in currencies:
                blackout_minutes = self.event_blackout_minutes.get(event.impact, 0)

                if blackout_minutes > 0:
                    event_start = event.time - timedelta(minutes=blackout_minutes)
                    event_end = event.time + timedelta(minutes=blackout_minutes)

                    if event_start <= check_time <= event_end:
                        return False, event

        return True, None

    async def place_order_with_economic_check(self, account_id: str, instrument: str, units: int, order_type: str = "MARKET") -> Any:
        """Place order only if no conflicting economic events."""
        safe_to_trade, conflicting_event = await self.is_safe_to_trade(instrument)

        if not safe_to_trade:
            raise ValueError(
                f"Trading blocked due to {conflicting_event.impact} impact event: "
                f"{conflicting_event.event} at {conflicting_event.time}"
            )

        # Proceed with order placement
        if order_type == "MARKET":
            response = await self.client.orders.post_market_order(
                account_id=account_id,
                instrument=instrument,
                units=units
            )
        else:
            # Handle other order types
            pass

        return response

    async def get_upcoming_events(
        self,
        currency_pair: str,
        hours_ahead: int = 24
    ) -> List[EconomicEvent]:
        """Get upcoming economic events for a currency pair."""
        now = datetime.now(timezone.utc)
        end_time = now + timedelta(hours=hours_ahead)

        events = await self.calendar.get_events(now, end_time)
        currencies = currency_pair.split("_")

        return [
            event for event in events
            if event.currency in currencies and event.time > now
        ]

async def economic_data_integration_example():
    """Complete example of economic data integration."""

    # Initialize components
    client = AsyncClient(
        token="your-oanda-token",
        environment=Environment.PRACTICE
    )

    calendar = EconomicCalendarProvider("your-calendar-api-key")
    trading_system = EconomicAwareTradingSystem(client, calendar)

    account_id = "your-account-id"

    try:
        # Check upcoming events
        upcoming = await trading_system.get_upcoming_events("EUR_USD", hours_ahead=8)
        print(f"Upcoming EUR/USD events in next 8 hours: {len(upcoming)}")

        for event in upcoming:
            print(f"  {event.time}: {event.event} ({event.impact})")

        # Attempt to place a trade (with economic check)
        try:
            response = await trading_system.place_order_with_economic_check(
                account_id=account_id,
                instrument="EUR_USD",
                units=1000
            )
            print(f"Order placed successfully: {response.order.id}")

        except ValueError as e:
            print(f"Order blocked: {e}")

    finally:
        await client.close()

    return trading_system

# Usage example
# trading_system = await economic_data_integration_example()
```

## Advanced Economic Integration

### Real-Time Event Monitoring

For production systems, implement real-time monitoring:

```python
class RealTimeEconomicMonitor:
    """Real-time economic event monitoring."""

    def __init__(self, trading_system: EconomicAwareTradingSystem) -> None:
        self.trading_system = trading_system
        self.active_positions = {}
        self.monitoring = False

    async def start_monitoring(self) -> Any:
        """Start real-time economic event monitoring."""
        self.monitoring = True

        while self.monitoring:
            try:
                # Check for imminent events every 5 minutes
                await self._check_imminent_events()
                await asyncio.sleep(300)  # 5 minutes

            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(60)  # Retry in 1 minute

    async def _check_imminent_events(self) -> Any:
        """Check for events in the next hour."""
        for instrument in self.active_positions:
            events = await self.trading_system.get_upcoming_events(
                instrument, hours_ahead=1,
            )

            high_impact_events = [
                event for event in events
                if event.impact == "HIGH"
            ]

            if high_impact_events:
                await self._handle_imminent_event(instrument, high_impact_events[0])

    async def _handle_imminent_event(self, instrument: str, event: EconomicEvent) -> Any:
        """Handle imminent high-impact economic event."""
        print(f"High-impact event approaching for {instrument}: {event.event}")

        # Option 1: Close all positions
        # await self._close_positions(instrument)

        # Option 2: Reduce position sizes
        # await self._reduce_position_sizes(instrument, reduction_factor=0.5)

        # Option 3: Tighten stop losses
        # await self._tighten_stop_losses(instrument, tighter_percentage=0.5)

    def stop_monitoring(self) -> Any:
        """Stop monitoring."""
        self.monitoring = False
```

## Best Practices

### Event Impact Classification

```python

EVENT_IMPACT_RULES = {
    # Central Bank Events (Highest Impact)
    "interest_rate_decision": "HIGH",
    "monetary_policy": "HIGH",
    "fomc_statement": "HIGH",

    # Employment Data (High Impact)
    "nonfarm_payrolls": "HIGH",
    "unemployment_rate": "HIGH",
    "employment_change": "MEDIUM",

    # Inflation Data (High Impact)
    "cpi": "HIGH",
    "ppi": "MEDIUM",
    "inflation_rate": "HIGH",

    # GDP and Growth (Medium to High Impact)
    "gdp": "HIGH",
    "retail_sales": "MEDIUM",
    "manufacturing_pmi": "MEDIUM",

    # Default for unknown events
    "default": "LOW",
}

def classify_event_impact(event_title: str) -> str:
    """Classify event impact based on title."""
    title_lower = event_title.lower()

    for key, impact in EVENT_IMPACT_RULES.items():
        if key in title_lower:
            return impact

    return EVENT_IMPACT_RULES["default"]
```

### Position Sizing During Events

```python

def calculate_event_adjusted_position_size(
    base_size: int,
    event_impact: str,
    time_to_event_minutes: int,
) -> int:
    """Adjust position size based on upcoming events."""

    if event_impact == "HIGH":
        if time_to_event_minutes <= 60:
            return 0  # No trading within 1 hour
        elif time_to_event_minutes <= 240:
            return int(base_size * 0.3)  # 30% size within 4 hours

    elif event_impact == "MEDIUM":
        if time_to_event_minutes <= 30:
            return int(base_size * 0.5)  # 50% size within 30 minutes

    return base_size  # Normal size for LOW impact or distant events
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Economic calendar APIs often have rate limits
   - Cache event data locally
   - Use webhooks when available
   - Implement exponential backoff

2. **Timezone Handling**: Economic events use various timezones
   - Always convert to UTC for consistency
   - Account for daylight saving time changes

3. **Data Quality**: Economic data can be delayed or revised
   - Implement data validation
   - Have fallback mechanisms
   - Log data quality issues

## Next Steps

- **[Financial News Integration](financial-news.md)** - Add real-time news sentiment analysis
- **[Unified Data Pipeline](unified-pipeline.md)** - Combine multiple data sources
- **[Technical Indicators Integration](technical-indicators.md)** - Enhance with technical analysis

---

## Related Guides

- [Risk Management Tutorial](../../tutorials/risk-management.md)
- [Advanced Orders Guide](../../tutorials/advanced-orders/index.md)
- [Production Deployment](../production-deployment/index.md)