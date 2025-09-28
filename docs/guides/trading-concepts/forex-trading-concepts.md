# Forex Trading Concepts for FiveTwenty SDK

Understanding how forex market concepts map to FiveTwenty SDK models and operations.

## Currency Pairs and Instruments

### Instrument Representation

FiveTwenty uses OANDA's instrument naming convention:

```python
# Instrument format: BASE_QUOTE
instrument = "EUR_USD"  # Euro vs US Dollar
```

Key instrument categories:

- **Majors**: EUR_USD, GBP_USD, USD_JPY, USD_CHF, AUD_USD, USD_CAD, NZD_USD
- **Minors**: Cross-currency pairs like EUR_GBP, GBP_JPY
- **Exotics**: Emerging market currencies

## Positions vs Trades in the SDK

### Trade Objects

Individual order executions represented by `Trade` models:

```python
import asyncio
from typing import Any

from fivetwenty import AsyncClient


async def main() -> Any:
    """Example showing individual trades."""
    client = AsyncClient()
    account_id = "your-account-id"

    # Each order creates a separate trade
    trade1 = await client.orders.post_market_order(account_id, "EUR_USD", 10000)   # Buy 10k EUR
    trade2 = await client.orders.post_market_order(account_id, "EUR_USD", 15000)   # Buy 15k EUR
    trade3 = await client.orders.post_market_order(account_id, "EUR_USD", -5000)   # Sell 5k EUR

    # Results in 3 separate Trade objects
    trades = await client.trades.get_open_trades(account_id)  # Returns 3 trades


if __name__ == "__main__":
    asyncio.run(main())
```

**Trade Properties**:

- `id` - Unique trade identifier
- `initial_units` - Original trade size
- `current_units` - Current size (after partial closes)
- `price` - Entry price for this specific trade
- `unrealized_pl` - P/L for this individual trade

### Positions (Aggregated View)

A **position** is the net exposure for an instrument:

```python
from fivetwenty import AsyncClient


async def check_position() -> None:
    """Example showing position aggregation."""
    client = AsyncClient()
    account_id = "your-account-id"

    # After the trades above, you have:
    position = await client.positions.get_position(account_id, "EUR_USD")

    # Position shows NET exposure:
    # Long: 25,000 EUR (10k + 15k)
    # Short: 5,000 EUR
    # Net: 20,000 EUR long

    print(position.long.units)   # 25000
    print(position.short.units)  # -5000 (negative indicates short)
```

**Position Properties**:

- `instrument` - The currency pair
- `long` - Long side details (PositionSide)
- `short` - Short side details (PositionSide)
- `pl` - Total realized P/L for this instrument
- `unrealized_pl` - Current unrealized P/L

### Visual Example: Trades vs Positions

```text
TRADES (Individual Orders):                    POSITION (Net Exposure):

Trade 1: Buy 10,000 EUR @ 1.1234             ┌─────────────────────────┐
Trade 2: Buy 15,000 EUR @ 1.1245             │     EUR_USD Position    │
Trade 3: Sell 5,000 EUR @ 1.1250             │                         │
                                              │  Long Side:   25,000    │
┌─── Individual Trade Records ───┐            │  Short Side:  -5,000    │
│ Trade 1: +10,000 EUR @ 1.1234  │            │  Net:        +20,000    │
│ Trade 2: +15,000 EUR @ 1.1245  │            │                         │
│ Trade 3:  -5,000 EUR @ 1.1250  │            │  Unrealized P/L: $45.30 │
│                                 │            └─────────────────────────┘
│ Each tracked separately         │
│ for P/L and management         │
└─────────────────────────────────┘
```

### Why This Distinction Matters

**For Risk Management**:
<!-- fragment: Demo risk calculation with generic type parameters -->
```python
from typing import Any


def calculate_risk_exposure(trades: list, position: Any, stop_loss_distance: float) -> None:
    """Calculate individual and total risk exposure."""
    # Trades - individual risk exposure
    for trade in trades:
        individual_risk = trade.current_units * stop_loss_distance
        print(f"Trade {trade.id} risk: {individual_risk}")

    # Position - total instrument exposure
    total_exposure = abs(position.long.units) + abs(position.short.units)
    net_exposure = position.long.units + position.short.units  # short.units is negative
    print(f"Total exposure: {total_exposure}, Net: {net_exposure}")
```

**For P/L Tracking**:
<!-- fragment: Demo P/L analysis with generic type parameters -->
```python
from typing import Any


def analyze_pnl(trades: list, position: Any) -> None:
    """Analyze P/L at different levels."""
    # Trade-level P/L (useful for strategy analysis)
    trade_performance = [(t.id, t.unrealized_pl) for t in trades]
    print(f"Individual trade P/L: {trade_performance}")

    # Position-level P/L (useful for risk management)
    total_instrument_pl = position.unrealized_pl
    print(f"Total instrument P/L: {total_instrument_pl}")
```

---

## Order Types and Market Mechanics

### Market Orders

Execute immediately at current market price:

```python
import asyncio
from fivetwenty import AsyncClient


async def place_market_order() -> None:
    """Place a market order example."""
    # Setup example variables
    client = AsyncClient()
    account_id = "your-account-id"

    # Market order - executes now
    order = await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=10000  # Buy 10,000 EUR
    )

    # Usually fills immediately
    if order.order_fill_transaction:
        fill_price = order.order_fill_transaction.price
        print(f"Filled at {fill_price}")

if __name__ == "__main__":
    asyncio.run(place_market_order())
```

**Use Cases**:
- When you want immediate execution
- High liquidity instruments
- Small position sizes relative to market depth

### Limit Orders

Execute only at specified price or better:

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_limit_order() -> None:
    """Place a limit order example."""
    # Setup example variables
    client = AsyncClient()
    account_id = "your-account-id"

    # Current EUR_USD price: 1.1050
    # Place buy limit at 1.1000 (below market)
    limit_order = await client.orders.post_limit_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=10000,
        price=Decimal("1.1000")  # Will only buy at 1.1000 or lower
    )
    print(f"Limit order placed: {limit_order}")

if __name__ == "__main__":
    asyncio.run(place_limit_order())
```

**Market Scenarios**:

- **Buy Limit Below Market**: Wait for price to drop to your level
- **Sell Limit Above Market**: Wait for price to rise to your level
- **No Fill Risk**: Order may never execute if price doesn't reach your level

### Stop Orders

Triggered when market reaches specified price:

```python
import asyncio
from decimal import Decimal
from fivetwenty import AsyncClient


async def place_stop_order() -> None:
    """Place a stop order example."""
    # Setup example variables
    client = AsyncClient()
    account_id = "your-account-id"

    # Current EUR_USD: 1.1050
    # Stop buy at 1.1100 (above market) - breakout strategy
    stop_order = await client.orders.post_stop_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=10000,
        price=Decimal("1.1100")  # Buy if price breaks above 1.1100
    )
    print(f"Stop order placed: {stop_order}")

if __name__ == "__main__":
    asyncio.run(place_stop_order())
```


**Common Strategies**:

- **Stop Buy Above Market**: Momentum/breakout trading
- **Stop Sell Below Market**: Trend following on breaks
- **Becomes Market Order**: When triggered, executes at current market price

---

## Margin and Leverage

### How Forex Margin Works

Unlike stocks, forex trading uses **leverage** - you can control large positions with small amounts:
```text
                    Leverage & Margin Example
                        (30:1 Leverage)

┌─────────────────────────┐     ┌──────────────────────────┐
│     Your Account        │     │    Your Position         │
│                         │────▶│                          │
│  Balance:   $10,000     │     │  Size: $300,000 EUR_USD  │
│  Used:      $3,333      │     │                          │
│  Available: $6,667      │     │  Margin Required: 3.33%  │
│                         │     │  = $300,000 × 0.0333     │
│  Risk: If position      │     │  = $10,000 ÷ 30          │
│  moves 333 pips         │     │  = $3,333                │
│  against you = 100%     │     │                          │
│  account loss           │     │  Control: 30× your money │
└─────────────────────────┘     └──────────────────────────┘

⚠️  Higher leverage = Higher risk & reward
```

```python
from decimal import Decimal
from fivetwenty import AsyncClient

# Setup example variables
client = AsyncClient()
account_id = "your-account-id"

async def main() -> None:
    """Check your account margin situation."""
    account = await client.accounts.get_account(account_id)

    print(f"Balance: {account.balance}")              # Your actual money
    print(f"Margin Used: {account.margin_used}")     # Tied up in positions
    print(f"Margin Available: {account.margin_available}")  # Available for new trades

    # Margin calculation example:
    # Position: 100,000 EUR_USD
    # Margin Rate: 3.33% (30:1 leverage)
    # Required Margin: 100,000 * Decimal("0.0333") = 3,330 USD

if __name__ == "__main__":
    asyncio.run(main())

```

**Key Concepts**:

- **Leverage**: Allows you to trade larger positions than your account balance
- **Margin Used**: Capital reserved for open positions
- **Free Margin**: Available for new positions
- **Margin Call**: When margin used approaches account balance

### SDK Margin Information

```python
from decimal import Decimal
from fivetwenty import AsyncClient

# Setup example variables
client = AsyncClient()
account_id = "your-account-id"

async def main() -> None:
    """Check account margin levels."""
    # Account-level margin
    account = await client.accounts.get_account(account_id)
    margin_utilization = Decimal(account.margin_used) / Decimal(account.balance)

    # Position-level margin
    positions = await client.positions.get_open_positions(account_id)
    for position in positions:
        print(f"{position.instrument}: {position.margin_used} margin used")

    # Individual trade margin
    trades = await client.trades.get_open_trades(account_id)
    for trade in trades:
        print(f"Trade {trade.id}: {trade.margin_used} margin")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Profit and Loss Calculations

### Unrealized vs. Realized P/L

**Unrealized P/L**: Potential profit/loss on open positions
**Realized P/L**: Actual profit/loss from closed trades

```python
async def check_pnl() -> None:
    """Check unrealized and realized P/L."""
    client = AsyncClient()
    account_id = "your-account-id"

    # Unrealized P/L (paper profits/losses)
    account = await client.accounts.get_account(account_id)
    current_unrealized = account.unrealized_pl  # All open positions

    # Individual position unrealized P/L
    position = await client.positions.get_position(account_id, "EUR_USD")
    eur_usd_unrealized = position.unrealized_pl

    # Realized P/L tracking
    for trade in await client.trades.get_open_trades(account_id):
        print(f"Trade {trade.id}: Realized P/L = {trade.realized_pl}")
```

### P/L Calculation Example

```python
import asyncio


async def main():
    # You bought 10,000 EUR_USD at 1.1000
    # Current price: 1.1050
    # P/L = (Current Price - Entry Price) × Position Size
    # P/L = (1.1050 - 1.1000) × 10,000 = 50 USD profit

    # The SDK calculates this automatically:
    client = AsyncClient()
    account_id = "your-account-id"
    trade_id = "123"

    trade = await client.trades.get_trade(account_id, trade_id)
    print(f"Unrealized P/L: {trade.unrealized_pl}")  # Shows 50.00

if __name__ == "__main__":
    asyncio.run(main())
```

### Currency Conversion in P/L

When your account currency differs from the quote currency:

```python
async def check_currency_conversion() -> None:
    """Check currency conversion in P/L."""
    client = AsyncClient()
    account_id = "your-account-id"

    # Account in USD, trading GBP_JPY
    # P/L is calculated in JPY (quote currency)
    # Then converted to USD (account currency)

    position = await client.positions.get_position(account_id, "GBP_JPY")
    # position.unrealized_pl is already in USD (your account currency)

    # The SDK handles conversion automatically using current exchange rates
```

---

## Market Data and Pricing

### Bid-Ask Spreads

Forex markets have two prices:

```text
                Market Depth & Pricing

        SELL ORDERS (Asks)                 BUY ORDERS (Bids)
    Price    |    Volume              Price    |    Volume
    ---------|----------              ---------|----------
    1.1055   |   100K  ← ASK          1.1049   |   150K  ← BID
    1.1054   |   200K    (You pay     1.1048   |   100K    (You receive
    1.1053   |   150K     higher)     1.1047   |   200K     lower)
    1.1052   |   300K                 1.1046   |   250K

            ↕ SPREAD ↕
         (1.1055 - 1.1049 = 0.0006 = 0.6 pips)

Trading Cost: You immediately lose the spread when opening a position
```

```python
async def check_spread() -> None:
    """Check bid-ask spread."""
    client = AsyncClient()
    account_id = "your-account-id"

    prices = await client.pricing.get_pricing(account_id, ["EUR_USD"])
    eur_usd_price = prices.prices[0]

    bid_price = eur_usd_price.bids[0].price      # Price you can SELL at
    ask_price = eur_usd_price.asks[0].price      # Price you can BUY at
    spread = ask_price - bid_price               # Market maker profit

    # Trading implications:
    # - Buying: You pay the ask price (higher)
    # - Selling: You receive the bid price (lower)
    # - Position starts with negative P/L equal to spread
```

### Market Depth (Order Book)

See available liquidity at different price levels:

```python
async def check_order_book() -> None:
    """Check order book depth."""
    client = AsyncClient()
    account_id = "your-account-id"

    # Get candle data as a proxy for market depth analysis
    candles = await client.instruments.get_instrument_candles(
        instrument="EUR_USD",
        count=1
    )

    print(f"Current candle data: {candles.candles[0]}")
    # Note: OANDA API doesn't provide order book data directly
    # This is a simplified example for educational purposes
```


**Market Depth Insights**:

- **Liquidity**: How much volume available at each price
- **Support/Resistance**: Large orders may act as price barriers
- **Slippage Risk**: Low liquidity = potential price impact

---

## Risk Management Concepts

### Position Sizing

Never risk more than a small percentage of your account:
```python
from decimal import Decimal

async def calculate_position_size() -> None:
    """Calculate position size based on risk."""
    client = AsyncClient()
    account_id = "your-account-id"

    # The 2% rule: Never risk more than 2% on a single trade
    account = await client.accounts.get_account(account_id)
    account_balance = Decimal(account.balance)
    max_risk = account_balance * Decimal("0.02")  # 2% of account

    # Calculate position size based on stop loss
    stop_loss_pips = 50  # Stop loss 50 pips away
    pip_value = Decimal("1.0")      # For EUR_USD, 1 pip = $1 per 10k units

    # Position size = Max Risk / (Stop Loss Pips × Pip Value)
    position_size = int(max_risk / (stop_loss_pips * pip_value))

    # Place order with calculated size
    # Note: StopLossDetails needs to be properly imported and constructed
    await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=position_size
    )
```

### Correlation Risk

Be aware of correlated positions:

```python
async def check_correlation_risk() -> None:
    """Check correlation risk across positions."""
    client = AsyncClient()
    account_id = "your-account-id"

    # EUR_USD and GBP_USD often move together
    # Having large positions in both = concentration risk

    eur_position = await client.positions.get_position(account_id, "EUR_USD")
    gbp_position = await client.positions.get_position(account_id, "GBP_USD")

    # Calculate total USD exposure
    eur_net = int(eur_position.long.units) + int(eur_position.short.units)
    gbp_net = int(gbp_position.long.units) + int(gbp_position.short.units)

    # Both positive = both long USD (correlated risk)
    # Opposite signs = hedged positions
    print(f"EUR net: {eur_net}, GBP net: {gbp_net}")
```

### Drawdown Management

Track account performance:

```python
from decimal import Decimal

async def monitor_drawdown() -> None:
    """Monitor account drawdown."""
    client = AsyncClient()
    account_id = "your-account-id"
    peak_equity = Decimal("10000")  # Example peak equity

    # Monitor account equity (balance + unrealized P/L)
    account = await client.accounts.get_account(account_id)
    current_equity = Decimal(str(account.balance)) + Decimal(str(account.unrealized_pl))

    # Compare to account high-water mark
    if current_equity < peak_equity * Decimal("0.95"):  # 5% drawdown
        print("⚠️ Significant drawdown detected")
        # Consider reducing position sizes or stopping trading
```

---

## Market Sessions and Timing

### Global Forex Sessions

Forex markets trade 24/5, but activity varies:

<!-- fragment: Demo market session with magic numbers and control flow patterns -->
```python
from datetime import datetime, timezone


def get_market_session(dt: datetime) -> str:
    """Determine current forex market session."""
    utc_hour = dt.replace(tzinfo=timezone.utc).hour

    if 0 <= utc_hour < 7:
        return "Sydney/Tokyo"    # Asian session
    elif 7 <= utc_hour < 15:
        return "London"          # European session
    elif 15 <= utc_hour < 22:
        return "New York"        # US session
    else:
        return "Sydney"          # Asian session starts

# Check current session
current_session = get_market_session(datetime.now())
print(f"Current session: {current_session}")

# Trading implications:
# - London/NY overlap (12-17 UTC): Highest volume
# - Asian session: Lower volatility, different currency focus
# - Fridays 22 UTC - Sunday 22 UTC: Markets closed
```

### Economic Calendar Impact

Major news events affect volatility:

<!-- fragment: Demo news adjustment with assignment type patterns -->
```python
def adjust_for_news() -> None:
    """Adjust trading parameters for news events."""
    major_news_expected = True  # Example - would come from economic calendar
    stop_loss_distance = 50  # Example stop loss distance
    position_size = 10000  # Example position size

    # Before major economic releases, consider:
    # - Reducing position sizes
    # - Widening stop losses
    # - Avoiding new positions

    # Check if major news expected (external data needed)
    # Then adjust trading parameters:
    if major_news_expected:
        stop_loss_distance *= 1.5  # Wider stops
        position_size //= 2         # Smaller positions

    print(f"Adjusted stop loss: {stop_loss_distance}")
    print(f"Adjusted position size: {position_size}")
```

---

## Advanced Concepts

### Carry Trades

Profit from interest rate differentials:

```python
# High-yield currency vs. low-yield currency
# Example: AUD (higher rates) vs JPY (lower rates)

# Long AUD_JPY position earns:
# - Capital appreciation if AUD rises vs JPY
# - Interest rate differential (swap/rollover)

async def check_carry_trade() -> None:
    """Check carry trade financing."""
    client = AsyncClient()
    account_id = "your-account-id"

    # Get instrument information (financing rates would be in instrument details)
    # Note: This is a simplified example - actual financing data structure may differ
    try:
        # Get current candles as proxy for instrument data
        candles = await client.instruments.get_instrument_candles(
            instrument="AUD_JPY",
            count=1
        )
        print(f"AUD_JPY candle data: {candles.candles[0]}")
        # Financing rates would typically be in account/instrument details
    except Exception as e:
        print(f"Error getting instrument data: {e}")
```

### Currency Hedging

Protect against currency risk:

```python
# If you have EUR exposure from business
# but trade with USD account, you have currency risk

async def hedge_currency_exposure() -> None:
    """Hedge currency exposure."""
    client = AsyncClient()
    account_id = "your-account-id"
    business_eur_exposure = 100000  # Example EUR exposure from business

    # If you have EUR exposure from business
    # but trade with USD account, you have currency risk

    # Natural hedge: Go short EUR_USD to offset EUR exposure
    hedge_position = -business_eur_exposure  # Opposite position

    await client.orders.post_market_order(
        account_id=account_id,
        instrument="EUR_USD",
        units=hedge_position  # Negative = short EUR
    )
```

---

## SDK-Specific Considerations

### Decimal Precision

The SDK uses `Decimal` for financial accuracy:
```python
from decimal import ROUND_HALF_UP, Decimal

# Proper forex price handling
price = Decimal("1.10505")  # 5-decimal precision for most pairs
rounded_price = price.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

# JPY pairs use 3-decimal precision
jpy_price = Decimal("110.505")
jpy_rounded = jpy_price.quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
```

### Streaming Data Usage

Real-time price feeds for active trading:

```python
import asyncio


async def main() -> None:
    """Main streaming example."""
    client = AsyncClient()
    account_id = "your-account-id"
    instruments = ["EUR_USD", "GBP_USD"]

    async def price_monitor() -> None:
        """Monitor real-time prices for trading signals."""

        async for price_data in client.pricing.get_pricing_stream(account_id, instruments):
            if hasattr(price_data, 'type') and price_data.type == "PRICE":
                # price_data is ClientPrice object
                current_bid = price_data.bids[0].price
                current_ask = price_data.asks[0].price

                # Your trading logic here would go here
                print(f"Price update: {current_bid}/{current_ask}")

            elif hasattr(price_data, 'type') and price_data.type == "HEARTBEAT":
                # Keep-alive signal - connection is healthy
                pass

    await price_monitor()

if __name__ == "__main__":
    asyncio.run(main())
```

### Error Handling in Trading Context

```python
async def handle_trading_errors() -> None:
    """Handle trading errors properly."""
    import asyncio
    import logging
    from decimal import Decimal
    from fivetwenty.exceptions import VeeTwentyError

    client = AsyncClient()
    account_id = "your-account-id"
    logger = logging.getLogger(__name__)

    def calculate_affordable_size(balance: str) -> int:
        """Calculate affordable position size."""
        return int(Decimal(balance) * Decimal('0.01'))  # 1% of balance

    try:
        order = await client.orders.post_market_order(
            account_id=account_id,
            instrument="EUR_USD",
            units=10000
        )
    except VeeTwentyError as e:
        if "INSUFFICIENT_MARGIN" in str(e):
            # Reduce position size and retry
            account = await client.accounts.get_account(account_id)
            smaller_size = calculate_affordable_size(account.balance)
            order = await client.orders.post_market_order(
                account_id=account_id,
                instrument="EUR_USD",
                units=smaller_size
            )
        elif "MARKET_HALTED" in str(e):
            # Wait and retry later
            await asyncio.sleep(60)
            # Implement retry logic
        else:
            # Log error and alert
            logger.error(f"Unexpected trading error: {e}")
```

---

## Conclusion

Understanding these forex concepts in the context of the FiveTwenty helps you:

1. **Structure Your Code**: Know when to use trades vs. positions
2. **Manage Risk**: Implement proper position sizing and margin monitoring
3. **Handle Market Realities**: Account for spreads, slippage, and market sessions
4. **Build Robust Systems**: Proper error handling for trading scenarios
5. **Optimize Performance**: Use appropriate order types and timing

The SDK abstracts away much complexity, but understanding the underlying forex mechanics helps you build more effective and safer trading applications.

Remember: Forex trading involves substantial risk. Always test thoroughly in the practice environment before using real money.