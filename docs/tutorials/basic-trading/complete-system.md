# Complete Trading System

!!! tip "Learning Goal"
    Build a production-ready automated trading system with full automation, risk management, and performance tracking.

---

## Complete Trading Strategy Implementation

Building a complete automated trading system requires orchestrating multiple components into a cohesive, production-ready workflow. This involves continuously monitoring market conditions, calculating technical indicators in real-time, managing open positions dynamically, and executing trades with proper risk management - all while handling errors gracefully and tracking performance metrics. A well-designed trading system operates autonomously within defined parameters, making decisions based on your strategy logic without requiring constant manual intervention.

This example demonstrates a full end-to-end trading loop that runs continuously for a specified duration. You'll see how to integrate price updates with `client.pricing.get_pricing()`, check existing positions using `client.trades.get_trades()`, execute trades with `client.orders.post_market_order()`, and implement proper error handling throughout. The code shows real-world patterns like sleep intervals to avoid API rate limits, exception handling for network issues, and performance tracking that provides visibility into your strategy's behavior.

Understanding this complete system architecture prepares you to build your own automated strategies with confidence. You'll learn how all the individual components from previous tutorials (market data, position management, order execution) work together in a production environment, and see best practices for structuring long-running trading applications:

<!-- fragment: Complete executable trading system with full strategy implementation -->
```python
import asyncio
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError
from fivetwenty.models import InstrumentName

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

# Load API credentials from .env file
# The AsyncClient automatically reads these environment variables:
#   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
#   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
#   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
load_dotenv()

# ==============================================================================
# COMPLETE AUTOMATED TRADING SYSTEM
# ==============================================================================

# This example demonstrates a production-ready automated trading system that
# combines all the concepts from previous tutorials into a complete workflow:
#
# KEY COMPONENTS:
# 1. Strategy Class - Moving Average Crossover with full state management
# 2. Price Updates - Continuous market data fetching from OANDA
# 3. Technical Indicators - Real-time moving average calculations
# 4. Position Management - Check existing trades before entering new ones
# 5. Trade Execution - Market orders with stop loss and take profit
# 6. Error Handling - Graceful recovery from API errors and rate limits
# 7. Performance Tracking - Monitor win rate, P&L, and trade statistics
#
# HOW IT WORKS:
# The system runs autonomously for a specified duration, checking market conditions
# every minute. When the fast MA crosses the slow MA, it generates signals and
# executes trades with proper risk management. All trades include protective
# stop loss and take profit orders to define maximum risk.
#
# This code is fully executable and runs a complete 5-minute trading session.


# ==============================================================================
# STRATEGY CLASS: MOVING AVERAGE CROSSOVER
# ==============================================================================


class SimpleMovingAverageCrossover:
    """
    A complete moving average crossover trading strategy.

    This strategy generates buy signals when a fast moving average crosses above
    a slow moving average, and sell signals when the fast MA crosses below the
    slow MA. This is a classic trend-following strategy that works in trending
    markets but can produce false signals in ranging markets.
    """

    def __init__(
        self,
        instrument: str = "EUR_USD",
        fast_ma_period: int = 10,
        slow_ma_period: int = 20,
        position_size: int = 1000,
        stop_loss_pips: int = 20,
        take_profit_pips: int = 30,
    ) -> None:
        """
        Initialize the strategy with trading parameters.

        Args:
            instrument: Currency pair to trade (e.g., "EUR_USD")
            fast_ma_period: Number of periods for fast moving average
            slow_ma_period: Number of periods for slow moving average
            position_size: Number of units to trade
            stop_loss_pips: Stop loss distance in pips
            take_profit_pips: Take profit distance in pips
        """
        self.instrument = instrument
        self.fast_ma_period = fast_ma_period
        self.slow_ma_period = slow_ma_period
        self.position_size = position_size
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips

        # Price history for calculating moving averages
        self.prices: list[Decimal] = []

        # Track previous MAs for crossover detection
        self.prev_fast_ma: Decimal | None = None
        self.prev_slow_ma: Decimal | None = None

        # Performance tracking
        self.strategy_stats: dict[str, int | Decimal] = {
            "total_trades": 0,
            "winning_trades": 0,
            "total_pnl": Decimal("0"),
        }

    async def update_prices(self, client: AsyncClient) -> bool:
        """Fetch latest price and add to price history."""
        try:
            # Get current pricing from OANDA
            response = await client.pricing.get_pricing(
                client.account_id, [self.instrument]
            )

            if response["prices"]:
                price_data = response["prices"][0]
                # Use mid-point between bid and ask for calculations
                bid = Decimal(price_data.bids[0].price)
                ask = Decimal(price_data.asks[0].price)
                mid_price = (bid + ask) / Decimal("2")

                self.prices.append(mid_price)

                # Keep only the most recent prices we need
                max_prices = self.slow_ma_period + 10
                if len(self.prices) > max_prices:
                    self.prices = self.prices[-max_prices:]

                return True

        except FiveTwentyError as e:
            print(f"   ERROR: Could not fetch prices: {e.message}")

        return False

    def calculate_moving_average(
        self, prices: list[Decimal], period: int
    ) -> Decimal | None:
        """Calculate simple moving average over the specified period."""
        if len(prices) < period:
            return None

        recent_prices = prices[-period:]
        return sum(recent_prices) / Decimal(str(period))

    def should_buy(self) -> bool:
        """Check for bullish crossover signal (fast MA crosses above slow MA)."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        if fast_ma is None or slow_ma is None:
            return False

        # Detect crossover: fast MA was below/equal and is now above slow MA
        if self.prev_fast_ma is not None and self.prev_slow_ma is not None:
            crossover = (
                self.prev_fast_ma <= self.prev_slow_ma and fast_ma > slow_ma
            )
            self.prev_fast_ma = fast_ma
            self.prev_slow_ma = slow_ma
            return crossover

        # Initialize previous values on first call
        self.prev_fast_ma = fast_ma
        self.prev_slow_ma = slow_ma
        return False

    def should_sell(self) -> bool:
        """Check for bearish crossover signal (fast MA crosses below slow MA)."""
        if len(self.prices) < self.slow_ma_period:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        if fast_ma is None or slow_ma is None:
            return False

        # Detect crossover: fast MA was above/equal and is now below slow MA
        if self.prev_fast_ma is not None and self.prev_slow_ma is not None:
            crossover = (
                self.prev_fast_ma >= self.prev_slow_ma and fast_ma < slow_ma
            )
            self.prev_fast_ma = fast_ma
            self.prev_slow_ma = slow_ma
            return crossover

        # Initialize previous values on first call
        self.prev_fast_ma = fast_ma
        self.prev_slow_ma = slow_ma
        return False


# ==============================================================================
# TRADE EXECUTION FUNCTION
# ==============================================================================


async def execute_strategy_trade(
    client: AsyncClient,
    strategy: SimpleMovingAverageCrossover,
    direction: str,
    current_price: Decimal,
) -> None:
    """Execute a trade with stop loss and take profit attached."""
    try:
        # Calculate position size (positive for buy, negative for sell)
        units = (
            strategy.position_size
            if direction == "BUY"
            else -strategy.position_size
        )

        # Calculate stop loss and take profit levels
        pip_value = Decimal("0.0001")

        if direction == "BUY":
            # Long: stop below entry, profit above entry
            stop_loss_price = current_price - (strategy.stop_loss_pips * pip_value)
            take_profit_price = current_price + (strategy.take_profit_pips * pip_value)
        else:
            # Short: stop above entry, profit below entry
            stop_loss_price = current_price + (strategy.stop_loss_pips * pip_value)
            take_profit_price = current_price - (strategy.take_profit_pips * pip_value)

        print(f"   Placing {direction} order...")
        print(f"      Entry: {current_price:.5f}")
        print(f"      Stop Loss: {stop_loss_price:.5f}")
        print(f"      Take Profit: {take_profit_price:.5f}")

        # ==============================================================================
        # SDK METHOD: client.orders.post_market_order()
        # ==============================================================================
        #
        # Place a market order with protective stop loss and take profit
        #
        # Parameters:
        #   - account_id: Your OANDA account ID (available as client.account_id)
        #   - instrument: Currency pair to trade (InstrumentName enum)
        #   - units: Position size (positive=buy, negative=sell)
        #   - stop_loss: Optional stop loss price (Decimal)
        #   - take_profit: Optional take profit price (Decimal)
        #
        # Returns: TypedDict with order fill details including transaction ID
        #
        # NOTE: The API now accepts Decimal prices directly for stop_loss and
        #       take_profit, simplifying the previous model-based approach

        await client.orders.post_market_order(
            account_id=client.account_id,
            instrument=InstrumentName(strategy.instrument),
            units=units,
            stop_loss=stop_loss_price,
            take_profit=take_profit_price,
        )

        # Update statistics (safely handle int type)
        total_trades = strategy.strategy_stats["total_trades"]
        assert isinstance(total_trades, int)
        strategy.strategy_stats["total_trades"] = total_trades + 1
        print(f"    {direction} ORDER EXECUTED SUCCESSFULLY")

    except FiveTwentyError as e:
        print(f"   ERROR: Trade execution failed: {e.message}")


# ==============================================================================
# MAIN TRADING LOOP
# ==============================================================================


async def run_complete_trading_strategy(
    strategy: SimpleMovingAverageCrossover, duration_minutes: int = 10
) -> None:
    """
    Run a complete automated trading strategy with continuous monitoring.

    This is the main loop that demonstrates:
    1. Continuous price updates using client.pricing.get_pricing()
    2. Technical indicator calculation (moving averages)
    3. Position checking with client.trades.get_trades()
    4. Automated trade execution with proper risk management
    5. Error handling and recovery patterns
    6. Performance tracking throughout the session
    """

    print("=" * 50)
    print("LAUNCHING AUTOMATED TRADING STRATEGY")
    print("=" * 50)
    print("Strategy: Moving Average Crossover")
    print(f"Instrument: {strategy.instrument}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Fast MA: {strategy.fast_ma_period} periods")
    print(f"Slow MA: {strategy.slow_ma_period} periods")
    print(f"Position Size: {strategy.position_size} units")
    print("=" * 50)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        start_time = datetime.now()

        # Main trading loop - runs until duration expires
        while (datetime.now() - start_time).seconds < duration_minutes * 60:
            try:
                print(f"\n{datetime.now().strftime('%H:%M:%S')} - Strategy Check")

                # ==============================================================================
                # STEP 1: UPDATE MARKET DATA
                # ==============================================================================

                # The SDK method: client.pricing.get_pricing()
                #
                # Parameters:
                #   - account_id: Your OANDA account ID (available as client.account_id)
                #   - instruments: List of instruments to get pricing for
                #
                # Returns: TypedDict with structure:
                #   {
                #       "prices": list[ClientPrice],  # Pydantic models with bids/asks
                #       "time": datetime
                #   }
                #
                # NOTE: Response is a TypedDict (use dictionary access: response["prices"])
                #       Each ClientPrice is a Pydantic model (use attribute access: price.bids)

                if not await strategy.update_prices(client):
                    print("   WARNING: Could not update prices, skipping this cycle")
                    await asyncio.sleep(60)
                    continue

                current_price = strategy.prices[-1]
                print(f"   Current Price: {current_price:.5f}")

                # ==============================================================================
                # STEP 2: CALCULATE INDICATORS
                # ==============================================================================

                if len(strategy.prices) >= strategy.slow_ma_period:
                    fast_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.fast_ma_period
                    )
                    slow_ma = strategy.calculate_moving_average(
                        strategy.prices, strategy.slow_ma_period
                    )
                    if fast_ma and slow_ma:
                        print(f"   Fast MA: {fast_ma:.5f}")
                        print(f"   Slow MA: {slow_ma:.5f}")
                else:
                    print(
                        f"   Collecting data... ({len(strategy.prices)}/{strategy.slow_ma_period} candles)"
                    )

                # ==============================================================================
                # STEP 3: CHECK CURRENT POSITION
                # ==============================================================================

                # The SDK method: client.trades.get_trades()
                #
                # Returns: TypedDict with structure:
                #   {
                #       "trades": list[Trade],        # List of Pydantic Trade models
                #       "lastTransactionID": str
                #   }
                #
                # Each Trade model contains:
                #   - trade.id: str - Unique trade identifier
                #   - trade.instrument: str - Currency pair
                #   - trade.current_units: str - Position size

                response = await client.trades.get_trades(client.account_id)
                trades = response["trades"]

                # Filter for our instrument
                open_trades = [
                    t for t in trades if t.instrument == strategy.instrument
                ]
                has_position = len(open_trades) > 0

                print(f"   Current Position: {'YES' if has_position else 'NONE'}")

                # ==============================================================================
                # STEP 4: EXECUTE STRATEGY LOGIC
                # ==============================================================================

                if not has_position:
                    # Look for entry signals
                    if strategy.should_buy():
                        print("    BUY SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "BUY", current_price
                        )
                    elif strategy.should_sell():
                        print("    SELL SIGNAL DETECTED!")
                        await execute_strategy_trade(
                            client, strategy, "SELL", current_price
                        )
                    else:
                        print("   No signal - waiting...")
                else:
                    print("   Managing existing position...")
                    # In production, you might implement:
                    # - Trailing stop loss adjustments
                    # - Partial profit taking
                    # - Position scaling

                # ==============================================================================
                # STEP 5: DISPLAY STATISTICS
                # ==============================================================================

                stats = strategy.strategy_stats
                print(
                    f"   Stats: {stats['total_trades']} trades, "
                    f"${stats['total_pnl']:+.2f} P&L"
                )

                # Wait before next check (avoid API rate limits)
                await asyncio.sleep(60)

            except Exception as e:
                print(f"   ERROR: {e}")
                print("   Continuing after error recovery...")
                await asyncio.sleep(60)

        # Strategy completion
        print("\n" + "=" * 50)
        print("STRATEGY COMPLETED")
        print("=" * 50)
        print(f"Session ended at: {datetime.now().strftime('%H:%M:%S')}")
        print_strategy_performance(strategy)


# ==============================================================================
# PERFORMANCE REPORTING
# ==============================================================================


def print_strategy_performance(strategy: SimpleMovingAverageCrossover) -> None:
    """
    Display comprehensive strategy performance metrics.

    Shows total trades, win rate, and P&L along with strategy parameters
    for post-session analysis.
    """
    print("\nFINAL STRATEGY PERFORMANCE")
    print("=" * 50)

    stats = strategy.strategy_stats
    total_trades = stats["total_trades"]
    winning_trades = stats["winning_trades"]
    total_pnl = stats["total_pnl"]

    assert isinstance(total_trades, int)
    assert isinstance(winning_trades, int)
    assert isinstance(total_pnl, Decimal)

    print(f"Total Trades: {total_trades}")

    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
        print(f"Winning Trades: {winning_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${total_pnl:+.2f}")

        if total_pnl > 0:
            print("\n Profitable strategy session")
        elif total_pnl < 0:
            print("\n⚠ Loss detected - review strategy parameters")
        else:
            print("\n= Breakeven performance")
    else:
        print("No trades executed during this session")

    print("\nStrategy Parameters:")
    print(f"   Instrument: {strategy.instrument}")
    print(f"   Position Size: {strategy.position_size} units")
    print(f"   Stop Loss: {strategy.stop_loss_pips} pips")
    print(f"   Take Profit: {strategy.take_profit_pips} pips")
    print(f"   Fast MA: {strategy.fast_ma_period} periods")
    print(f"   Slow MA: {strategy.slow_ma_period} periods")


# ==============================================================================
# EXECUTION
# ==============================================================================

if __name__ == "__main__":
    # Create strategy instance with parameters
    strategy = SimpleMovingAverageCrossover(
        instrument="EUR_USD",
        fast_ma_period=10,
        slow_ma_period=20,
        position_size=1000,
        stop_loss_pips=20,
        take_profit_pips=30,
    )

    # Run the strategy for 5 minutes (use longer duration in production)
    # Note: This will attempt to trade on your OANDA practice account
    asyncio.run(run_complete_trading_strategy(strategy, duration_minutes=5))
```

---

## Enhanced Strategy with Advanced Features

Production trading strategies go beyond technical indicators. Volatility filters prevent trading during choppy, unpredictable market conditions, and dynamic position sizing adjusts your exposure based on current volatility and account risk parameters. Spread monitoring keeps you out of trades when execution costs are high, and daily trade limits prevent over-trading that erodes profits through transaction costs and emotional decisions.

This enhanced strategy demonstrates how to build trading logic that adapts to changing market conditions. You'll use `client.pricing.get_pricing()` to monitor bid-ask spreads in real time, implement volatility-based position sizing, and create market condition filters that keep the strategy out of unfavorable environments.

The example is a foundation; real-world implementations would expand it with multi-timeframe analysis, correlation filters across instruments, economic calendar integration, or machine learning-based signal optimization:

<!-- fragment: Enhanced strategy with market condition filtering and dynamic position sizing -->
```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

# Load API credentials from .env file
# The AsyncClient automatically reads these environment variables:
#   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
#   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
#   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
load_dotenv()

# ==============================================================================
# ENHANCED STRATEGY WITH MARKET CONDITION FILTERING
# ==============================================================================

# This example demonstrates advanced trading features beyond basic automation:
#
# KEY CONCEPTS COVERED:
# 1. Market Condition Analysis - Check spread width before trading
# 2. Dynamic Position Sizing - Adjust position size based on volatility
# 3. Risk-Based Limits - Never exceed account risk parameters
# 4. Real-time SDK Integration - Use live account and pricing data
#
# WHAT'S DIFFERENT FROM BASIC STRATEGY:
# - Analyzes market conditions to determine if trading is appropriate
# - Calculates position sizes dynamically based on current volatility
# - Demonstrates account balance integration for risk management
# - Shows how to build protective filters into your strategy
#
# This code is fully executable and demonstrates real SDK methods in action.


# ==============================================================================
# ENHANCED TRADING STRATEGY CLASS
# ==============================================================================


class EnhancedTradingStrategy:
    """
    Enhanced trading strategy with advanced market condition filtering.

    This strategy extends basic trading with:
    - Spread monitoring to avoid trading during wide spreads
    - Dynamic position sizing based on volatility
    - Market condition analysis before trade execution
    - Risk-based position limits
    """

    def __init__(self, instrument: str = "EUR_USD") -> None:
        """Initialize enhanced strategy with risk management parameters."""
        self.instrument = instrument
        self.position_size = 1000
        self.max_risk_per_trade = 0.02  # 2% risk per trade
        self.stop_loss_pips = 20
        self.take_profit_pips = 30

        # Enhanced features
        self.max_daily_trades = 5
        self.daily_trade_count = 0
        self.trend_filter_enabled = True
        self.volatility_filter_enabled = True

    async def check_market_conditions(self, client: AsyncClient) -> dict[str, str | bool]:
        """
        Analyze market conditions to determine if trading is appropriate.

        Checks spread width and determines if market conditions are suitable
        for trade execution based on current bid-ask spread.

        Returns:
            Dictionary with market condition indicators and tradeable status
        """
        conditions: dict[str, str | bool] = {
            "trend": "neutral",
            "volatility": "normal",
            "spread": "normal",
            "tradeable": True,
        }

        try:
            # ==============================================================================
            # SDK METHOD: client.pricing.get_pricing()
            # ==============================================================================
            #
            # Get current market pricing to analyze spread conditions
            #
            # Parameters:
            #   - account_id: Your OANDA account ID (available as client.account_id)
            #   - instruments: List of instruments to get pricing for
            #
            # Returns: TypedDict with structure:
            #   {
            #       "prices": list[ClientPrice],  # Pydantic models
            #       "time": datetime
            #   }
            #
            # NOTE: Response is TypedDict (use dictionary access: response["prices"])

            response = await client.pricing.get_pricing(
                client.account_id,
                [self.instrument],
            )

            if response["prices"]:
                price_data = response["prices"][0]
                # Calculate spread from bid-ask prices
                bid = Decimal(price_data.bids[0].price)
                ask = Decimal(price_data.asks[0].price)
                spread = ask - bid

                # Check if spread is too wide (more than 5 pips)
                if spread > Decimal("0.0005"):  # 5 pips
                    conditions["spread"] = "wide"
                    conditions["tradeable"] = False

                # In production, you would also analyze:
                # - Volatility measurement (ATR, standard deviation)
                # - Trend strength (ADX, moving average slopes)
                # - Economic calendar events
                # - Multi-timeframe confirmation

        except Exception:
            # If we can't get market conditions, don't trade
            conditions["tradeable"] = False

        return conditions

    def calculate_dynamic_position_size(
        self, account_balance: Decimal, volatility: Decimal
    ) -> int:
        """
        Calculate position size based on account balance and market volatility.

        Adjusts position size dynamically:
        - Reduces size in high volatility to limit risk
        - Increases size in low volatility to maximize opportunity
        - Never exceeds risk limits or maximum position cap
        """
        # Start with base position size
        base_size = self.position_size

        # ==============================================================================
        # VOLATILITY-BASED POSITION SIZING
        # ==============================================================================
        # Adjust position size based on current market volatility
        # High volatility = smaller positions to control risk
        # Low volatility = larger positions to capitalize on stable conditions

        if volatility > Decimal("0.002"):  # High volatility threshold (20 pips)
            base_size = int(base_size * Decimal("0.5"))  # Reduce to 50%
        elif volatility < Decimal("0.001"):  # Low volatility (10 pips)
            base_size = int(base_size * Decimal("1.2"))  # Increase to 120%

        # Calculate maximum size based on account risk limits
        # Risk 2% of account per trade with 20 pip stop loss
        max_size_by_risk = int(account_balance * Decimal(str(self.max_risk_per_trade)) / 20)

        # Return the smallest of: volatility-adjusted size, risk limit, or hard cap
        return min(base_size, max_size_by_risk, 2000)  # Cap at 2000 units


# ==============================================================================
# DEMONSTRATION MAIN FUNCTION
# ==============================================================================


async def main() -> None:
    """Demonstrate enhanced strategy features with real SDK integration."""

    print("=" * 60)
    print("ENHANCED TRADING STRATEGY - MARKET CONDITION ANALYSIS")
    print("=" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:

        # Create enhanced strategy instance
        strategy = EnhancedTradingStrategy(instrument="EUR_USD")

        print(f"\nAnalyzing market conditions for {strategy.instrument}...")

        # ==============================================================================
        # STEP 1: CHECK MARKET CONDITIONS
        # ==============================================================================

        conditions = await strategy.check_market_conditions(client)

        print("\nMarket Condition Analysis:")
        print(f"  Trend: {conditions['trend']}")
        print(f"  Volatility: {conditions['volatility']}")
        print(f"  Spread: {conditions['spread']}")
        print(f"  Tradeable: {'YES ' if conditions['tradeable'] else 'NO ✗'}")

        if not conditions["tradeable"]:
            print("\n⚠ Market conditions not suitable for trading")
            print("  Reason: Spread too wide (>5 pips)")
            print("  Action: Wait for better conditions")
        else:
            print("\n Market conditions acceptable for trading")

        # ==============================================================================
        # STEP 2: DEMONSTRATE DYNAMIC POSITION SIZING
        # ==============================================================================

        print("\n" + "=" * 60)
        print("DYNAMIC POSITION SIZING EXAMPLES")
        print("=" * 60)

        # Get account balance for position sizing calculations
        account_response = await client.accounts.get_account_summary(client.account_id)
        account_balance = Decimal(account_response["account"].balance)

        print(f"\nAccount Balance: ${account_balance}")
        print(f"Max Risk Per Trade: {strategy.max_risk_per_trade * 100}%")

        # Test different volatility scenarios
        scenarios = [
            (Decimal("0.0005"), "Very Low Volatility (5 pips)"),
            (Decimal("0.0010"), "Low Volatility (10 pips)"),
            (Decimal("0.0015"), "Normal Volatility (15 pips)"),
            (Decimal("0.0025"), "High Volatility (25 pips)"),
        ]

        print("\nPosition Sizing by Volatility:")
        for volatility, description in scenarios:
            position_size = strategy.calculate_dynamic_position_size(
                account_balance, volatility
            )
            print(f"  {description:30s}  {position_size:5d} units")

        # ==============================================================================
        # ENHANCEMENT IDEAS FOR PRODUCTION
        # ==============================================================================

        print("\n" + "=" * 60)
        print("PRODUCTION ENHANCEMENT IDEAS")
        print("=" * 60)
        print("\nTo make this strategy production-ready, consider adding:")
        print("  • Volatility filters using ATR (Average True Range)")
        print("  • Time-of-day filters to avoid low liquidity periods")
        print("  • Economic calendar integration to avoid news events")
        print("  • Multi-timeframe trend confirmation")
        print("  • Correlation analysis across currency pairs")
        print("  • Machine learning for adaptive parameter optimization")
        print("  • Real-time drawdown monitoring and circuit breakers")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
```

---

## Performance Monitoring Dashboard

You need continuous performance monitoring to understand how your strategy behaves in live market conditions. Real-time metrics like win rate, profit per hour, and trades per hour show when your strategy is performing as expected and when market conditions have changed. A monitoring dashboard gives you immediate visibility into your strategy's health, so you can decide when to let it run, when to pause for analysis, and when to shut it down to prevent further losses.

This monitoring system demonstrates how to track and display the performance indicators professional traders use to evaluate a strategy. The `StrategyMonitor` class calculates runtime statistics, win rates, profitability metrics, and efficiency measures that show both whether you're making money and how hard your capital is working. Use these metrics to compare strategies, tune parameters, and weigh trade frequency against profitability.

Monitoring matters as much as the trading logic itself. Without it, you can't distinguish normal strategy drawdowns from fundamental strategy failures. The patterns shown here can be extended with equity curve tracking, drawdown analysis, Sharpe ratio calculation, and real-time alerting for abnormal behavior:

<!-- fragment: Complete performance monitoring with SDK integration and real account data -->
```python
import asyncio
from datetime import datetime
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError

# ==============================================================================
# ENVIRONMENT SETUP
# ==============================================================================

# Load API credentials from .env file
# The AsyncClient automatically reads these environment variables:
#   - FIVETWENTY_OANDA_TOKEN: Your OANDA API token
#   - FIVETWENTY_OANDA_ACCOUNT: Your OANDA account ID
#   - FIVETWENTY_OANDA_ENVIRONMENT: "practice" or "live" (defaults to practice)
load_dotenv()

# ==============================================================================
# PERFORMANCE MONITORING DASHBOARD
# ==============================================================================

# This example demonstrates real-time performance monitoring for trading strategies:
#
# KEY FEATURES:
# 1. Runtime Metrics - Track how long the strategy has been running
# 2. Trade Statistics - Count total trades and winning trades
# 3. Win Rate Calculation - Measure strategy effectiveness percentage
# 4. Profitability Tracking - Monitor total P&L and P&L per hour
# 5. Efficiency Metrics - Calculate trades per hour
# 6. Status Indicators - Automatic alerts for performance thresholds
#
# WHY MONITORING MATTERS:
# Without proper monitoring, you can't distinguish between normal strategy
# drawdowns and fundamental strategy failures. Real-time visibility into
# performance metrics allows you to make informed decisions about when to
# continue trading versus when to pause for analysis or adjustment.
#
# This code is fully executable and demonstrates monitoring integration with
# a simple strategy. In production, you would add equity curve tracking,
# drawdown analysis, Sharpe ratio calculation, and real-time alerting.


# ==============================================================================
# SIMPLE STRATEGY FOR DEMONSTRATION
# ==============================================================================


class SimpleStrategy:
    """
    A minimal strategy class for demonstrating the performance monitor.

    In a real system, this would be your complete trading strategy (like the
    SimpleMovingAverageCrossover from the previous example). For monitoring
    demonstration purposes, we keep it simple.
    """

    def __init__(self, instrument: str = "EUR_USD") -> None:
        """Initialize strategy with basic tracking."""
        self.instrument = instrument

        # Performance tracking - same structure as complete trading system
        self.strategy_stats: dict[str, int | Decimal] = {
            "total_trades": 0,
            "winning_trades": 0,
            "total_pnl": Decimal("0"),
        }

    def simulate_trade_result(self, profit: Decimal) -> None:
        """Simulate a trade result for demonstration purposes."""
        # Update total trades count
        total_trades = self.strategy_stats["total_trades"]
        assert isinstance(total_trades, int)
        self.strategy_stats["total_trades"] = total_trades + 1

        # Update P&L
        current_pnl = self.strategy_stats["total_pnl"]
        assert isinstance(current_pnl, Decimal)
        self.strategy_stats["total_pnl"] = current_pnl + profit

        # Update winning trades if profitable
        if profit > 0:
            winning_trades = self.strategy_stats["winning_trades"]
            assert isinstance(winning_trades, int)
            self.strategy_stats["winning_trades"] = winning_trades + 1


# ==============================================================================
# STRATEGY PERFORMANCE MONITOR
# ==============================================================================


class StrategyMonitor:
    """
    Real-time performance monitoring for trading strategies.

    This monitor tracks key performance indicators (KPIs) that professional
    traders use to evaluate strategy effectiveness:
    - Win rate: Percentage of profitable trades
    - P&L per hour: Capital efficiency metric
    - Trades per hour: Activity level indicator
    - Status indicators: Automatic performance alerts

    Usage:
        monitor = StrategyMonitor(strategy)
        monitor.print_performance_dashboard()  # Display current metrics
    """

    # ==============================================================================
    # PERFORMANCE THRESHOLDS (CONFIGURABLE)
    # ==============================================================================

    # These thresholds determine when the monitor raises alerts about
    # strategy performance. Adjust these based on your risk tolerance:

    MAX_ACCEPTABLE_LOSS = Decimal("100")  # Dollar loss before review needed
    MIN_WIN_RATE_WARNING = 40.0  # Win rate percentage below which to warn
    MIN_TRADES_FOR_STATS = 5  # Minimum trades before calculating win rate

    def __init__(self, strategy: SimpleStrategy) -> None:
        """
        Initialize the monitor with a strategy to track.

        Args:
            strategy: Strategy instance with strategy_stats dictionary
        """
        self.strategy = strategy
        self.start_time = datetime.now()

    def update_performance_metrics(self) -> dict[str, float | int | Decimal]:
        """
        Calculate comprehensive performance metrics.

        Returns:
            Dictionary with runtime metrics, trade statistics, and efficiency measures
        """
        # Calculate runtime in hours
        current_time = datetime.now()
        runtime_seconds = (current_time - self.start_time).total_seconds()
        runtime_hours = runtime_seconds / 3600

        # Get current strategy statistics
        stats = self.strategy.strategy_stats
        total_trades = stats["total_trades"]
        winning_trades = stats["winning_trades"]
        total_pnl = stats["total_pnl"]

        assert isinstance(total_trades, int)
        assert isinstance(winning_trades, int)
        assert isinstance(total_pnl, Decimal)

        # ==============================================================================
        # METRIC CALCULATIONS
        # ==============================================================================

        # Win Rate: Percentage of trades that were profitable
        # Use max() to avoid division by zero on first call
        win_rate = (winning_trades / max(total_trades, 1)) * 100

        # Trades Per Hour: Measures strategy activity level
        # Higher values indicate more frequent trading
        trades_per_hour = total_trades / max(runtime_hours, 0.01)

        # P&L Per Hour: Capital efficiency metric
        # Shows how effectively capital is being deployed
        pnl_per_hour = total_pnl / Decimal(str(max(runtime_hours, 0.01)))

        return {
            "runtime_hours": runtime_hours,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "total_pnl": total_pnl,
            "win_rate": win_rate,
            "trades_per_hour": trades_per_hour,
            "pnl_per_hour": pnl_per_hour,
        }

    def get_performance_status(
        self, metrics: dict[str, float | int | Decimal]
    ) -> str:
        """
        Determine current performance status based on metrics.

        Args:
            metrics: Dictionary of performance metrics

        Returns:
            Status string: "PROFITABLE", "REVIEW NEEDED", or "MONITORING"
        """
        total_pnl = metrics["total_pnl"]
        win_rate = metrics["win_rate"]
        total_trades = metrics["total_trades"]

        assert isinstance(total_pnl, Decimal)
        assert isinstance(win_rate, (int, float))
        assert isinstance(total_trades, int)

        # Status determination logic:
        # 1. Profitable: Overall P&L is positive
        # 2. Review needed: Loss exceeds threshold OR win rate too low
        # 3. Monitoring: Normal operation within acceptable parameters

        if total_pnl > 0:
            return "PROFITABLE "
        elif total_pnl < -self.MAX_ACCEPTABLE_LOSS:
            return "REVIEW NEEDED ⚠"
        elif (
            total_trades >= self.MIN_TRADES_FOR_STATS
            and win_rate < self.MIN_WIN_RATE_WARNING
        ):
            return "LOW WIN RATE ⚠"
        else:
            return "MONITORING"

    def print_performance_dashboard(self) -> None:
        """Display comprehensive real-time performance dashboard."""
        metrics = self.update_performance_metrics()

        # Extract values with type safety
        runtime_hours = metrics["runtime_hours"]
        total_trades = metrics["total_trades"]
        win_rate = metrics["win_rate"]
        total_pnl = metrics["total_pnl"]
        trades_per_hour = metrics["trades_per_hour"]
        pnl_per_hour = metrics["pnl_per_hour"]

        assert isinstance(runtime_hours, (int, float))
        assert isinstance(total_trades, int)
        assert isinstance(win_rate, (int, float))
        assert isinstance(total_pnl, Decimal)
        assert isinstance(trades_per_hour, (int, float))
        assert isinstance(pnl_per_hour, Decimal)

        print("\nSTRATEGY PERFORMANCE DASHBOARD")
        print("=" * 40)
        print(f"Runtime: {runtime_hours:.1f} hours")
        print(f"Total Trades: {total_trades}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Total P&L: ${total_pnl:+.2f}")
        print(f"Trades/Hour: {trades_per_hour:.1f}")
        print(f"P&L/Hour: ${pnl_per_hour:+.2f}")

        # Display performance status
        status = self.get_performance_status(metrics)
        print(f"Status: {status}")


# ==============================================================================
# DEMONSTRATION WITH SDK INTEGRATION
# ==============================================================================


async def main() -> None:
    """Demonstrate performance monitoring with simulated and real SDK data."""

    print("=" * 60)
    print("PERFORMANCE MONITORING DASHBOARD DEMONSTRATION")
    print("=" * 60)

    # ==============================================================================
    # PART 1: DEMONSTRATE MONITORING WITH SIMULATED TRADES
    # ==============================================================================

    print("\nPart 1: Monitoring with Simulated Trades")
    print("-" * 60)

    # Create a simple strategy for demonstration
    strategy = SimpleStrategy(instrument="EUR_USD")

    # Create monitor instance
    monitor = StrategyMonitor(strategy)

    # Simulate some trades to show how monitoring works
    print("\nSimulating trading activity...")

    # Simulate 10 trades with realistic P&L values
    simulated_results = [
        Decimal("15.50"),  # Win
        Decimal("-20.00"),  # Loss
        Decimal("22.30"),  # Win
        Decimal("18.75"),  # Win
        Decimal("-20.00"),  # Loss
        Decimal("25.00"),  # Win
        Decimal("-20.00"),  # Loss
        Decimal("19.25"),  # Win
        Decimal("21.50"),  # Win
        Decimal("-20.00"),  # Loss
    ]

    for i, pnl in enumerate(simulated_results, 1):
        strategy.simulate_trade_result(pnl)
        print(f"  Trade {i}: ${pnl:+.2f}")

    # Display the performance dashboard
    print("\nPerformance After Simulated Trades:")
    monitor.print_performance_dashboard()

    # ==============================================================================
    # PART 2: DEMONSTRATE SDK INTEGRATION FOR REAL MONITORING
    # ==============================================================================

    print("\n" + "=" * 60)
    print("Part 2: Integration with Real OANDA Account Data")
    print("-" * 60)

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        try:
            # ==============================================================================
            # SDK METHOD: client.accounts.get_account_summary()
            # ==============================================================================
            #
            # Get account summary including P&L information
            #
            # Parameters:
            #   - account_id: Your OANDA account ID (available as client.account_id)
            #
            # Returns: TypedDict with structure:
            #   {
            #       "account": AccountSummary,  # Pydantic model
            #       "lastTransactionID": str
            #   }
            #
            # NOTE: AccountSummary contains unrealized_pl, realized_pl, balance fields

            account_response = await client.accounts.get_account_summary(
                client.account_id
            )
            account = account_response["account"]

            print("\nReal Account Performance Metrics:")
            print(f"  Account Balance: ${Decimal(account.balance)}")
            print(f"  Unrealized P&L: ${Decimal(account.unrealized_pl):+.2f}")

            # ==============================================================================
            # SDK METHOD: client.trades.get_trades()
            # ==============================================================================
            #
            # Get all open trades to count active positions
            #
            # Returns: TypedDict with structure:
            #   {
            #       "trades": list[Trade],
            #       "lastTransactionID": str
            #   }

            trades_response = await client.trades.get_trades(client.account_id)
            trades = trades_response["trades"]

            print(f"  Open Positions: {len(trades)}")

            # Show real-time data integration
            if trades:
                print("\n  Open Trade Details:")
                for trade in trades[:3]:  # Show first 3 trades
                    print(f"    {trade.instrument}: {trade.current_units} units")
                    print(f"      Entry: {trade.price}")
                    print(f"      Current P&L: ${Decimal(trade.unrealized_pl):+.2f}")
            else:
                print("  No open trades currently")

        except FiveTwentyError as e:
            print(f"\n  ERROR: Could not fetch account data: {e.message}")
            print("  Note: Ensure your .env file contains valid OANDA credentials")

    # ==============================================================================
    # PRODUCTION MONITORING ENHANCEMENTS
    # ==============================================================================

    print("\n" + "=" * 60)
    print("PRODUCTION MONITORING ENHANCEMENTS")
    print("=" * 60)
    print("\nTo build production-grade monitoring, consider adding:")
    print("  • Equity curve tracking - Plot account balance over time")
    print("  • Maximum drawdown analysis - Track largest peak-to-trough decline")
    print("  • Sharpe ratio calculation - Risk-adjusted return metric")
    print("  • Trade duration statistics - Analyze holding period distribution")
    print("  • Real-time alerting - Email/SMS when thresholds breached")
    print("  • Daily/weekly performance reports - Automated performance summaries")
    print("  • Correlation monitoring - Track performance vs market conditions")
    print("  • Database persistence - Store metrics for historical analysis")


if __name__ == "__main__":
    # Run the demonstration
    asyncio.run(main())
```

---


## What You've Learned

Success **Complete System Development**: Building production-ready automated trading systems with continuous market monitoring, technical indicator calculation, position management, and automated trade execution using `client.pricing.get_pricing()`, `client.trades.get_trades()`, and `client.orders.post_market_order()`

Success **Advanced Strategy Features**: Market condition analysis with spread monitoring, dynamic position sizing based on volatility and account balance, and risk-based trade limits using real-time data from `client.accounts.get_account_summary()`

Success **Performance Monitoring**: Real-time tracking with KPI dashboards, win rate calculations, profitability metrics (P&L per hour), efficiency measures (trades per hour), and automatic status alerts for performance thresholds

Success **SDK Integration Patterns**: Proper AsyncClient context manager usage, TypedDict response handling with dictionary access, Pydantic model field access with attributes, Decimal type for financial precision, InstrumentName enum for type-safe instruments, and FiveTwentyError exception handling

!!! success "Trading System Complete"
    You've built a complete automated trading system, from concept to production deployment. You can now integrate real-time OANDA data, execute trades with risk management, and monitor performance with a dashboard.

---

## Next Steps

### What You've Accomplished

You've completed the FiveTwenty trading tutorial series. You now have:

Success **Level 1 - Foundation Knowledge**
- Deep understanding of forex concepts, pips, spreads, and order types
- Ability to analyze currency pair pricing and market dynamics

Success **Level 2 - Technical Proficiency**
- Skill connecting to OANDA API safely and securely
- Understanding of account management and margin concepts

Success **Level 3 - Trading Execution**
- Practical experience placing, monitoring, and closing trades
- Knowledge of position management and risk assessment

Success **Level 4 - System Development**
- Ability to build complete automated trading strategies
- Understanding of strategy design, backtesting, and optimization

### Ready for Advanced Learning?

**For Strategy Development:**
- Explore [Risk Management Fundamentals](../risk-management.md)
- Study [Advanced Order Types](../advanced-orders/index.md)
- Learn [Performance Optimization](../../guides/optimization/index.md)

**For Production Trading:**
- Set up [Live Trading Safely](../../guides/practical-solutions/setup-live-trading.md)

### Safety Reminders

!!! warning "Before Live Trading"
    1. **Practice extensively** with paper trading first
    2. **Start small** - use minimum position sizes initially
    3. **Never risk** more than you can afford to lose
    4. **Always use stop losses** and proper risk management
    5. **Keep learning** - markets constantly evolve

---

The technical skills are in place. Run your system on a practice account until its behavior holds no surprises, then follow the [live trading setup guide](../../guides/practical-solutions/setup-live-trading.md) when you're ready.

---

## Related Resources

- [Account Management](../account-management.md) - Advanced analysis techniques
- [Streaming Data](../streaming-data.md) - Real-time data processing
- [API Reference](../../api-reference/index.md) - Complete technical documentation
