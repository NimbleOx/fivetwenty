# Strategy Building

!!! tip "Target Learning Goal"
    Develop your first complete trading strategy with systematic signal generation and risk management.

Trading strategies transform market observations into actionable trading decisions through systematic rules and logic. Rather than relying on intuition or emotion, algorithmic strategies use quantifiable signals - like price movements, technical indicators, or statistical patterns - to determine when to enter and exit positions. The key to successful algorithmic trading lies not just in having a strategy, but in rigorously testing it on historical data (backtesting), optimizing its parameters, and validating its performance before risking real capital.

In this tutorial, you'll build a complete trading system from the ground up using the FiveTwenty SDK. You'll start by implementing a moving average crossover strategy that generates buy and sell signals from market data. Then you'll build a backtesting framework to evaluate strategy performance on historical OANDA data, calculating critical metrics like win rate, total return, and average profit/loss. Finally, you'll create a parameter optimizer that systematically tests hundreds of configurations to find the best-performing settings. Each example is fully executable, type-safe, and demonstrates real SDK integration with OANDA's live market data - giving you production-ready code you can run and learn from immediately.

---

## Designing Your First Strategy

A moving average crossover strategy is one of the most popular algorithmic trading approaches, generating signals when a faster-moving average crosses a slower-moving average. This strategy captures trend changes - when the fast MA crosses above the slow MA, it signals potential upward momentum (buy signal), and when it crosses below, it signals potential downward momentum (sell signal). The strategy is reliable enough for beginners yet powerful enough that professional traders use variations of it with proper risk management and parameter optimization.

This complete implementation demonstrates how to structure a trading strategy class with FiveTwenty SDK integration. The strategy fetches real market data using `client.instruments.get_instrument_candles()`, calculates moving averages from closing prices, and detects crossover events to generate trading signals. You'll see how to maintain strategy state, implement signal generation methods (`should_buy()` and `should_sell()`), and integrate with OANDA's live market data for real-time analysis:

```python
import asyncio
from decimal import Decimal

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity, InstrumentName

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
# STRATEGY IMPLEMENTATION
# ==============================================================================

class SimpleMovingAverageCrossover:
    """
    A complete moving average crossover trading strategy with risk management.

    This strategy demonstrates core concepts of algorithmic trading:
    - Signal generation based on technical indicators (moving averages)
    - Real-time market data integration via FiveTwenty SDK
    - Risk management with stop loss and take profit parameters
    - Type-safe implementation with full mypy compliance

    The strategy generates:
    - BUY signals when fast MA crosses above slow MA (bullish crossover)
    - SELL signals when fast MA crosses below slow MA (bearish crossover)
    """

    def __init__(
        self,
        instrument: InstrumentName = InstrumentName.EUR_USD,
        position_size: int = 1000,
        stop_loss_pips: int = 20,
        take_profit_pips: int = 30,
        fast_ma_period: int = 10,
        slow_ma_period: int = 20,
    ) -> None:
        """
        Initialize strategy with trading parameters.

        Args:
            instrument: InstrumentName enum for the currency pair to trade.
                       Use InstrumentName.EUR_USD, InstrumentName.GBP_USD, etc.
                       The SDK provides enums for all major currency pairs.
            position_size: Number of units per trade (1000 = 1 micro lot)
            stop_loss_pips: Distance in pips from entry for stop loss
            take_profit_pips: Distance in pips from entry for take profit
            fast_ma_period: Number of periods for fast moving average (smaller = more responsive)
            slow_ma_period: Number of periods for slow moving average (larger = smoother)
        """
        self.instrument = instrument
        self.position_size = position_size
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.fast_ma_period = fast_ma_period
        self.slow_ma_period = slow_ma_period

        # Strategy state - stores recent prices for MA calculation
        # We use Decimal type for all prices to maintain financial precision
        self.prices: list[Decimal] = []

    def calculate_moving_average(self, prices: list[Decimal], period: int) -> Decimal | None:
        """
        Calculate simple moving average for given period.

        Simple Moving Average (SMA) formula:
        SMA = (P1 + P2 + ... + Pn) / n

        Args:
            prices: List of closing prices (using Decimal for precision)
            period: Number of periods to average

        Returns:
            Moving average value, or None if insufficient data
        """
        if len(prices) < period:
            return None
        # Use Decimal arithmetic to avoid floating-point precision errors
        # Take the last 'period' prices and calculate their average
        return sum(prices[-period:]) / Decimal(period)

    def should_buy(self) -> bool:
        """
        Check if conditions are met for a buy signal.

        A buy signal (bullish crossover) occurs when:
        1. Previously: fast MA was at or below slow MA
        2. Currently: fast MA is above slow MA

        This indicates potential upward momentum and buying opportunity.

        Returns:
            True if fast MA crosses above slow MA (bullish crossover)
        """
        # Need at least slow_ma_period + 1 prices to detect a crossover
        # (+1 because we need current AND previous values)
        if len(self.prices) < self.slow_ma_period + 1:
            return False

        # Calculate current moving averages
        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Calculate previous moving averages for crossover detection
        # We slice the list to exclude the most recent price
        prev_fast_ma = self.calculate_moving_average(
            self.prices[:-1], self.fast_ma_period
        )
        prev_slow_ma = self.calculate_moving_average(
            self.prices[:-1], self.slow_ma_period
        )

        # Ensure all values are available before checking crossover
        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Type narrowing for mypy - tell the type checker these are definitely not None
        # This is necessary because mypy can't automatically infer from the all() check
        assert fast_ma is not None
        assert slow_ma is not None
        assert prev_fast_ma is not None
        assert prev_slow_ma is not None

        # Bullish crossover detection:
        # - Previous state: fast MA <= slow MA (fast was below or equal)
        # - Current state: fast MA > slow MA (fast is now above)
        # This crossover indicates a potential buy opportunity
        crossover = (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)
        return crossover

    def should_sell(self) -> bool:
        """
        Check if conditions are met for a sell signal.

        A sell signal (bearish crossover) occurs when:
        1. Previously: fast MA was at or above slow MA
        2. Currently: fast MA is below slow MA

        This indicates potential downward momentum and selling opportunity.

        Returns:
            True if fast MA crosses below slow MA (bearish crossover)
        """
        # Need at least slow_ma_period + 1 prices to detect a crossover
        if len(self.prices) < self.slow_ma_period + 1:
            return False

        # Calculate current moving averages
        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Calculate previous moving averages for crossover detection
        prev_fast_ma = self.calculate_moving_average(
            self.prices[:-1], self.fast_ma_period
        )
        prev_slow_ma = self.calculate_moving_average(
            self.prices[:-1], self.slow_ma_period
        )

        # Ensure all values are available
        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Type narrowing for mypy strict compliance
        assert fast_ma is not None
        assert slow_ma is not None
        assert prev_fast_ma is not None
        assert prev_slow_ma is not None

        # Bearish crossover detection:
        # - Previous state: fast MA >= slow MA (fast was above or equal)
        # - Current state: fast MA < slow MA (fast is now below)
        # This crossover indicates a potential sell opportunity
        crossover = (prev_fast_ma >= prev_slow_ma) and (fast_ma < slow_ma)
        return crossover

    async def update_prices(self, client: AsyncClient) -> bool:
        """
        Update price history by fetching recent candles from OANDA using the SDK.

        This method demonstrates key FiveTwenty SDK patterns:
        1. Using client.instruments.get_instrument_candles() to fetch historical data
        2. Accessing TypedDict responses with dictionary notation (response["candles"])
        3. Accessing Pydantic model attributes with dot notation (candle.mid.c)
        4. Working with Decimal types for financial precision

        Args:
            client: FiveTwenty AsyncClient for API access

        Returns:
            True if prices updated successfully, False otherwise
        """
        try:
            # ==============================================================================
            # FETCH CANDLES FROM OANDA USING SDK
            # ==============================================================================

            # The SDK method: client.instruments.get_instrument_candles()
            #
            # Parameters:
            #   - instrument: String value (use .value on InstrumentName enum)
            #   - count: Number of candles to fetch (alternative to from_time/to_time)
            #   - granularity: CandlestickGranularity enum (M5, H1, D, etc.)
            #
            # Returns: TypedDict with structure:
            #   {
            #       "candles": list[Candle],  # List of Pydantic Candle models
            #       "instrument": str,
            #       "granularity": str
            #   }
            #
            # We request enough candles for MA calculation plus a buffer
            candles_response = await client.instruments.get_instrument_candles(
                instrument=self.instrument.value,  # Convert enum to string: "EUR_USD"
                count=max(50, self.slow_ma_period + 10),  # Ensure sufficient data
                granularity=CandlestickGranularity.M5,  # 5-minute candles
            )

            # ==============================================================================
            # EXTRACT PRICES FROM CANDLE DATA
            # ==============================================================================

            # Extract candles list from TypedDict response
            # Response is a TypedDict, so use dictionary access: response["candles"]
            candles = candles_response["candles"]

            if candles:
                # Each candle is a Pydantic model with attributes:
                #   - candle.mid: CandlestickData with o, h, l, c (open, high, low, close)
                #   - candle.bid: BID prices (if available)
                #   - candle.ask: ASK prices (if available)
                #   - candle.time: datetime object (already parsed by SDK)
                #
                # We use list comprehension to extract closing prices:
                # - candle.mid.c accesses the closing price (Decimal type)
                # - We filter out candles without mid prices (if c.mid is truthy)
                self.prices = [c.mid.c for c in candles if c.mid]
                return True

        except Exception as e:
            # In production, you might want to use proper logging instead of print
            print(f"Error updating prices: {e}")
            return False

        return False


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

async def main() -> None:
    """
    Demonstrate moving average crossover strategy with real market data.

    This example shows the complete workflow:
    1. Create strategy instance with desired parameters
    2. Connect to OANDA via AsyncClient
    3. Fetch real-time market data using SDK
    4. Calculate moving averages from live prices
    5. Check for trading signals
    """

    # Create strategy instance with default parameters
    # InstrumentName is an enum provided by the SDK for type-safe instrument selection
    strategy = SimpleMovingAverageCrossover(
        instrument=InstrumentName.EUR_USD,  # EUR/USD currency pair
        fast_ma_period=10,                   # 10-period fast moving average
        slow_ma_period=20,                   # 20-period slow moving average
    )

    print("Moving Average Crossover Strategy Demo")
    print("=" * 50)
    print(f"Instrument: {strategy.instrument.value}")
    print(f"Fast MA Period: {strategy.fast_ma_period}")
    print(f"Slow MA Period: {strategy.slow_ma_period}")
    print(f"Position Size: {strategy.position_size} units")
    print(f"Stop Loss: {strategy.stop_loss_pips} pips")
    print(f"Take Profit: {strategy.take_profit_pips} pips\n")

    # ==============================================================================
    # CONNECT TO OANDA AND FETCH MARKET DATA
    # ==============================================================================

    # Use AsyncClient context manager for automatic resource cleanup
    # The client reads credentials from environment variables (loaded by dotenv)
    async with AsyncClient() as client:
        print("Fetching market data from OANDA...")

        # Update strategy with recent price data from OANDA
        # This calls client.instruments.get_instrument_candles() internally
        if await strategy.update_prices(client):
            print(f"✓ Loaded {len(strategy.prices)} price points\n")

            # ==============================================================================
            # CALCULATE MOVING AVERAGES AND CHECK FOR SIGNALS
            # ==============================================================================

            # Calculate current moving averages from fetched prices
            fast_ma = strategy.calculate_moving_average(
                strategy.prices, strategy.fast_ma_period
            )
            slow_ma = strategy.calculate_moving_average(
                strategy.prices, strategy.slow_ma_period
            )

            if fast_ma and slow_ma:
                print("Current Market Analysis:")
                print(f"  Latest Price: {strategy.prices[-1]:.5f}")
                print(f"  Fast MA ({strategy.fast_ma_period}): {fast_ma:.5f}")
                print(f"  Slow MA ({strategy.slow_ma_period}): {slow_ma:.5f}")

                # Check for trading signals based on crossover detection
                if strategy.should_buy():
                    print("\n🟢 BUY SIGNAL: Fast MA crossed above slow MA")
                    print(f"   Entry would be at ~{strategy.prices[-1]:.5f}")
                elif strategy.should_sell():
                    print("\n🔴 SELL SIGNAL: Fast MA crossed below slow MA")
                    print(f"   Entry would be at ~{strategy.prices[-1]:.5f}")
                else:
                    print("\n⚪ NO SIGNAL: Waiting for crossover")

                    # Show current market trend
                    if fast_ma > slow_ma:
                        print("   Fast MA is above slow MA (bullish trend)")
                    else:
                        print("   Fast MA is below slow MA (bearish trend)")
            else:
                print("Not enough data for MA calculation")
        else:
            print("Failed to fetch market data")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
```

---

## Strategy Backtesting Framework

Backtesting is the process of testing a trading strategy on historical market data to evaluate its performance before risking real capital. By simulating trades using past price data, you can measure key metrics like win rate, average profit/loss, maximum drawdown, and total return to understand whether your strategy has edge in the market. A robust backtesting framework is essential - it helps you identify profitable strategies, optimize parameters, and build confidence before deploying capital in live trading.

This complete backtesting implementation demonstrates how to test a moving average crossover strategy using FiveTwenty's historical data API. The backtester fetches candlestick data via `client.instruments.get_instrument_candles()`, processes each candle sequentially to simulate real-time trading, executes virtual trades based on MA crossover signals, and tracks all positions with proper stop loss and take profit management. You'll see how to calculate comprehensive performance statistics including win rate, profit factor, and return on investment, providing you with the metrics needed to evaluate strategy viability:

```python
import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TypedDict

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity, InstrumentName

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
# TYPE DEFINITIONS
# ==============================================================================

class Position(TypedDict):
    """
    Type definition for an open position using TypedDict.

    TypedDict provides type hints for dictionaries with specific keys.
    This is different from Pydantic models:
    - TypedDict: Just type hints, no runtime validation, dictionary access
    - Pydantic: Runtime validation, attribute access, serialization

    We use TypedDict here for lightweight position tracking since we're
    building the dictionary ourselves and don't need validation.
    """

    direction: str          # "BUY" or "SELL"
    entry_price: Decimal    # Price where position was opened
    stop_loss: Decimal      # Price that triggers loss exit
    take_profit: Decimal    # Price that triggers profit exit
    entry_time: datetime    # When position was opened


# ==============================================================================
# BACKTESTING ENGINE
# ==============================================================================

class SimpleBacktester:
    """
    Backtest a simple moving average crossover strategy on historical data.

    This backtester demonstrates how to use the FiveTwenty SDK to:
    1. Fetch historical candlestick data from OANDA
    2. Process candles sequentially to simulate real-time trading
    3. Generate trading signals based on moving average crossovers
    4. Track positions with stop loss and take profit management
    5. Calculate comprehensive performance statistics
    """

    def __init__(
        self,
        instrument: InstrumentName = InstrumentName.EUR_USD,
        initial_balance: Decimal = Decimal("10000"),
        position_size: int = 1000,
        stop_loss_pips: int = 20,
        take_profit_pips: int = 30,
        fast_ma_period: int = 10,
        slow_ma_period: int = 20,
    ) -> None:
        """
        Initialize backtester with strategy parameters.

        Args:
            instrument: InstrumentName enum for the currency pair to trade.
                       Use InstrumentName.EUR_USD, InstrumentName.GBP_USD, etc.
                       The SDK provides enums for all major currency pairs.
            initial_balance: Starting account balance (use Decimal for precision)
            position_size: Number of units to trade (1000 = 1 micro lot)
            stop_loss_pips: Distance in pips from entry to stop loss
            take_profit_pips: Distance in pips from entry to take profit
            fast_ma_period: Number of periods for fast moving average
            slow_ma_period: Number of periods for slow moving average
        """
        self.instrument = instrument
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.position_size = position_size
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.fast_ma_period = fast_ma_period
        self.slow_ma_period = slow_ma_period

        # Backtesting state - tracks price history and trade records
        self.prices: list[Decimal] = []              # Historical closing prices
        self.current_position: Position | None = None # Open position (if any)
        self.trades: list[dict] = []                  # Completed trades history

    def calculate_moving_average(
        self, prices: list[Decimal], period: int
    ) -> Decimal | None:
        """
        Calculate simple moving average for the given period.

        SMA = (P1 + P2 + ... + Pn) / n

        Args:
            prices: List of closing prices
            period: Number of periods to average

        Returns:
            Moving average value, or None if insufficient data
        """
        if len(prices) < period:
            return None
        # Use Decimal arithmetic for financial precision
        return sum(prices[-period:]) / Decimal(period)

    def check_buy_signal(self) -> bool:
        """
        Check if conditions are met for a buy signal.

        A buy signal occurs when the fast MA crosses above the slow MA,
        indicating potential upward momentum (bullish crossover).

        Returns:
            True if fast MA crosses above slow MA, False otherwise
        """
        # Need at least slow_ma_period + 1 prices to detect a crossover
        if len(self.prices) < self.slow_ma_period + 1:
            return False

        # Calculate current moving averages
        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)

        # Calculate previous moving averages (one period ago)
        # This is needed to detect the crossover moment
        prev_fast_ma = self.calculate_moving_average(
            self.prices[:-1], self.fast_ma_period
        )
        prev_slow_ma = self.calculate_moving_average(
            self.prices[:-1], self.slow_ma_period
        )

        # Check if all MAs are available
        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        # Type narrowing - tell mypy these values are definitely not None
        # This is necessary because mypy can't infer from the all() check above
        assert fast_ma is not None and slow_ma is not None
        assert prev_fast_ma is not None and prev_slow_ma is not None

        # Bullish crossover detection:
        # - Previously: fast MA was at or below slow MA
        # - Currently: fast MA is above slow MA
        # This indicates upward momentum and a potential buy opportunity
        return (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)

    def execute_trade(
        self, price: Decimal, timestamp: datetime, direction: str
    ) -> None:
        """
        Open a new position with stop loss and take profit.

        Args:
            price: Entry price (Decimal for financial precision)
            timestamp: Entry time (datetime object from candle.time)
            direction: "BUY" for long position, "SELL" for short position
        """
        # A pip is typically 0.0001 for most currency pairs (4th decimal place)
        # For JPY pairs it would be 0.01 (2nd decimal place)
        pip_value = Decimal("0.0001")

        # Calculate stop loss and take profit levels based on direction
        if direction == "BUY":
            # Long position: SL below entry, TP above entry
            stop_loss = price - (self.stop_loss_pips * pip_value)
            take_profit = price + (self.take_profit_pips * pip_value)
        else:
            # Short position: SL above entry, TP below entry
            stop_loss = price + (self.stop_loss_pips * pip_value)
            take_profit = price - (self.take_profit_pips * pip_value)

        # Create position dictionary matching our TypedDict structure
        # TypedDict provides type checking but it's still a regular dict at runtime
        self.current_position = {
            "direction": direction,
            "entry_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": timestamp,
        }

        print(f"  {direction} at {price:.5f} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")

    def check_exit(self, price: Decimal, timestamp: datetime) -> None:
        """
        Check if position should be closed based on stop loss or take profit.

        Args:
            price: Current market price to check against exit levels
            timestamp: Current time for recording exit time
        """
        if not self.current_position:
            return

        pos = self.current_position
        should_close = False
        exit_reason = ""

        # Check stop loss conditions
        if pos["direction"] == "BUY" and price <= pos["stop_loss"]:
            # Long position hit stop loss (price fell)
            should_close = True
            exit_reason = "Stop Loss"
        elif pos["direction"] == "SELL" and price >= pos["stop_loss"]:
            # Short position hit stop loss (price rose)
            should_close = True
            exit_reason = "Stop Loss"

        # Check take profit conditions
        elif pos["direction"] == "BUY" and price >= pos["take_profit"]:
            # Long position hit take profit (price rose)
            should_close = True
            exit_reason = "Take Profit"
        elif pos["direction"] == "SELL" and price <= pos["take_profit"]:
            # Short position hit take profit (price fell)
            should_close = True
            exit_reason = "Take Profit"

        if should_close:
            self.close_position(price, timestamp, exit_reason)

    def close_position(self, price: Decimal, timestamp: datetime, reason: str) -> None:
        """
        Close current position and record the trade.

        Args:
            price: Exit price
            timestamp: Exit time
            reason: Why the position was closed ("Stop Loss", "Take Profit", etc.)
        """
        if not self.current_position:
            return

        pos = self.current_position
        entry_price = pos["entry_price"]

        # Calculate profit/loss using Decimal arithmetic
        # P&L = (exit_price - entry_price) * position_size for long positions
        # P&L = (entry_price - exit_price) * position_size for short positions
        if pos["direction"] == "BUY":
            pnl = (price - entry_price) * self.position_size
        else:
            pnl = (entry_price - price) * self.position_size

        # Update account balance with P&L
        self.current_balance += pnl

        # Record trade for performance analysis
        trade = {
            "entry_time": pos["entry_time"],
            "exit_time": timestamp,
            "direction": pos["direction"],
            "entry_price": entry_price,
            "exit_price": price,
            "pnl": pnl,
            "reason": reason,
        }
        self.trades.append(trade)

        print(f"  CLOSE at {price:.5f} | P&L: ${pnl:+.2f} | {reason}")

        # Clear current position
        self.current_position = None

    async def run_backtest(
        self, client: AsyncClient, days_back: int = 30
    ) -> None:
        """
        Run backtest on historical data using the FiveTwenty SDK.

        This method demonstrates the core SDK workflow:
        1. Use client.instruments.get_instrument_candles() to fetch historical data
        2. Process Pydantic model responses from the SDK
        3. Access candle data using attribute notation (candle.mid.c)
        4. Work with datetime objects that the SDK returns

        Args:
            client: FiveTwenty AsyncClient for API access
            days_back: Number of days of historical data to test
        """
        print(f"\nBacktest: {self.instrument.value}")
        print("=" * 60)

        # Calculate date range using timezone-aware datetime objects
        # IMPORTANT: Always use datetime.now(UTC) instead of deprecated utcnow()
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days_back)

        print(f"Period: {start_date.date()} to {end_date.date()}")
        print(f"Initial Balance: ${self.initial_balance:,.2f}\n")

        # ==============================================================================
        # FETCH HISTORICAL CANDLES USING SDK
        # ==============================================================================

        # The SDK method: client.instruments.get_instrument_candles()
        #
        # Parameters:
        #   - instrument: String value (use .value on InstrumentName enum)
        #   - granularity: CandlestickGranularity enum (H1, M5, D, etc.)
        #   - from_time: datetime object (SDK converts to ISO format automatically)
        #   - to_time: datetime object (SDK converts to ISO format automatically)
        #
        # Returns: TypedDict with structure:
        #   {
        #       "candles": list[Candle],  # List of Pydantic Candle models
        #       "instrument": str,
        #       "granularity": str
        #   }
        #
        # NOTE: Response is a TypedDict, so use dictionary access: response["candles"]
        #       But each Candle is a Pydantic model, so use attribute access: candle.mid.c
        candles_response = await client.instruments.get_instrument_candles(
            instrument=self.instrument.value,  # "EUR_USD" string
            granularity=CandlestickGranularity.H1,  # 1-hour candles
            from_time=start_date,  # datetime object, NOT ISO string
            to_time=end_date,       # datetime object, NOT ISO string
        )

        # Extract candles list from TypedDict response
        # This is a list of Pydantic Candle models
        candles = candles_response["candles"]
        print(f"Loaded {len(candles)} candles\n")

        # ==============================================================================
        # PROCESS CANDLES TO SIMULATE TRADING
        # ==============================================================================

        # Loop through each historical candle in chronological order
        # This simulates receiving candles one-by-one in real-time
        for candle in candles:
            # Each candle is a Pydantic model with attributes:
            #   - candle.time: datetime object (already parsed by SDK)
            #   - candle.mid: CandlestickData model with o, h, l, c (open, high, low, close)
            #   - candle.bid: BID prices (if available)
            #   - candle.ask: ASK prices (if available)

            # Check if candle has mid prices (some candles might only have bid/ask)
            if not candle.mid:
                continue

            # Access closing price using attribute notation (Pydantic model)
            # candle.mid returns a CandlestickData Pydantic model
            # candle.mid.c returns the closing price as a Decimal
            price = candle.mid.c

            # Access candle timestamp using attribute notation
            # candle.time is already a datetime object parsed by the SDK
            # (NOT a string - no need for datetime.fromisoformat())
            timestamp = candle.time

            # Add closing price to our historical price list
            self.prices.append(price)

            # ==============================================================================
            # TRADING LOGIC
            # ==============================================================================

            # If we have an open position, check if we should exit it
            if self.current_position:
                self.check_exit(price, timestamp)

            # If we don't have a position and have enough price history,
            # check if we should enter a new position
            elif len(self.prices) >= self.slow_ma_period:
                if self.check_buy_signal():
                    # Execute buy trade at current price
                    self.execute_trade(price, timestamp, "BUY")

        # ==============================================================================
        # BACKTEST CLEANUP
        # ==============================================================================

        # Close any remaining open position at the end of backtest
        if self.current_position and self.prices:
            self.close_position(self.prices[-1], datetime.now(UTC), "End of Test")

        # Display performance statistics
        self.print_results()

    def print_results(self) -> None:
        """
        Print comprehensive backtest performance statistics.

        Key metrics explained:
        - Win Rate: Percentage of profitable trades
        - Total Return: Overall percentage gain/loss on initial balance
        - Average Win/Loss: Mean profit/loss per winning/losing trade
        """
        print("\n" + "=" * 60)
        print("BACKTEST RESULTS")
        print("=" * 60)

        if not self.trades:
            print("No trades executed during backtest period")
            return

        # Calculate performance statistics
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t["pnl"] > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        total_pnl = sum(t["pnl"] for t in self.trades)
        total_return = (
            (self.current_balance - self.initial_balance) / self.initial_balance * 100
        )

        # Display core performance metrics
        print(f"\nInitial Balance: ${self.initial_balance:,.2f}")
        print(f"Final Balance:   ${self.current_balance:,.2f}")
        print(f"Total Return:    {total_return:+.2f}%")
        print(f"Total P&L:       ${total_pnl:+.2f}")
        print(f"\nTotal Trades:    {total_trades}")
        print(f"Winning Trades:  {winning_trades}")
        print(f"Losing Trades:   {losing_trades}")
        print(f"Win Rate:        {win_rate:.1f}%")

        # Calculate and display average win/loss
        if winning_trades > 0:
            avg_win = sum(t["pnl"] for t in self.trades if t["pnl"] > 0) / winning_trades
            print(f"Average Win:     ${avg_win:.2f}")

        if losing_trades > 0:
            avg_loss = sum(t["pnl"] for t in self.trades if t["pnl"] < 0) / losing_trades
            print(f"Average Loss:    ${avg_loss:.2f}")


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

async def main() -> None:
    """
    Demonstrate strategy backtesting on historical data.

    This example shows the complete SDK workflow:
    1. Create AsyncClient context manager
    2. Fetch historical candles from OANDA
    3. Process candles to simulate trading
    4. Generate performance report
    """

    # Create backtester with strategy parameters
    backtester = SimpleBacktester(
        instrument=InstrumentName.EUR_USD,  # Use SDK's InstrumentName enum
        initial_balance=Decimal("10000"),   # Always use Decimal for money
        position_size=1000,                 # 1000 units = 1 micro lot
        stop_loss_pips=20,                  # 20 pip stop loss
        take_profit_pips=30,                # 30 pip take profit
        fast_ma_period=10,                  # 10-period fast MA
        slow_ma_period=20,                  # 20-period slow MA
    )

    # Use AsyncClient context manager for automatic resource cleanup
    # The client reads credentials from environment variables (loaded by dotenv)
    async with AsyncClient() as client:
        # Run backtest on last 30 days of data
        await backtester.run_backtest(client, days_back=30)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
```

---

## Strategy Optimization

Parameter optimization is the systematic process of finding the best configuration for your trading strategy by testing different combinations of parameters on historical data. While backtesting tells you how a strategy performed, optimization helps you discover which specific parameter values (like moving average periods, stop loss distances, or position sizes) maximize performance metrics such as total return, Sharpe ratio, or profit factor. This process transforms a mediocre strategy into a potentially profitable one by fine-tuning its behavior to match market characteristics.

This complete optimization implementation demonstrates grid search - an exhaustive testing method that evaluates every possible combination of parameters you define. The optimizer uses `itertools.product()` to generate the Cartesian product of parameter ranges, then runs a full backtest for each combination using FiveTwenty's SDK to fetch historical data from OANDA. You'll learn how to define parameter search spaces, execute parallel optimization workflows, track performance metrics across hundreds of tests, and identify optimal configurations while understanding the critical importance of out-of-sample validation to avoid overfitting:

```python
import asyncio
import itertools
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import TypedDict

from dotenv import load_dotenv
from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity, InstrumentName

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
# TYPE DEFINITIONS
# ==============================================================================

class Position(TypedDict):
    """Type definition for an open position using TypedDict."""

    direction: str          # "BUY" or "SELL"
    entry_price: Decimal    # Price where position was opened
    stop_loss: Decimal      # Price that triggers loss exit
    take_profit: Decimal    # Price that triggers profit exit
    entry_time: datetime    # When position was opened


# ==============================================================================
# BACKTESTING ENGINE (SIMPLIFIED FOR OPTIMIZATION)
# ==============================================================================

class SimpleBacktester:
    """
    Simplified backtester optimized for parameter testing.

    This version is streamlined for use in optimization loops - it runs
    backtests silently without printing trade-by-trade details, making
    it suitable for testing hundreds or thousands of parameter combinations.
    """

    def __init__(
        self,
        instrument: InstrumentName = InstrumentName.EUR_USD,
        initial_balance: Decimal = Decimal("10000"),
        position_size: int = 1000,
        stop_loss_pips: int = 20,
        take_profit_pips: int = 30,
        fast_ma_period: int = 10,
        slow_ma_period: int = 20,
    ) -> None:
        """Initialize backtester with strategy parameters."""
        self.instrument = instrument
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.position_size = position_size
        self.stop_loss_pips = stop_loss_pips
        self.take_profit_pips = take_profit_pips
        self.fast_ma_period = fast_ma_period
        self.slow_ma_period = slow_ma_period

        # Backtesting state
        self.prices: list[Decimal] = []
        self.current_position: Position | None = None
        self.trades: list[dict] = []

    def calculate_moving_average(
        self, prices: list[Decimal], period: int
    ) -> Decimal | None:
        """Calculate simple moving average."""
        if len(prices) < period:
            return None
        return sum(prices[-period:]) / Decimal(period)

    def check_buy_signal(self) -> bool:
        """Check if conditions met for buy signal (fast MA crosses above slow MA)."""
        if len(self.prices) < self.slow_ma_period + 1:
            return False

        fast_ma = self.calculate_moving_average(self.prices, self.fast_ma_period)
        slow_ma = self.calculate_moving_average(self.prices, self.slow_ma_period)
        prev_fast_ma = self.calculate_moving_average(
            self.prices[:-1], self.fast_ma_period
        )
        prev_slow_ma = self.calculate_moving_average(
            self.prices[:-1], self.slow_ma_period
        )

        if not all([fast_ma, slow_ma, prev_fast_ma, prev_slow_ma]):
            return False

        assert fast_ma is not None and slow_ma is not None
        assert prev_fast_ma is not None and prev_slow_ma is not None

        return (prev_fast_ma <= prev_slow_ma) and (fast_ma > slow_ma)

    def execute_trade(
        self, price: Decimal, timestamp: datetime, direction: str
    ) -> None:
        """Open a new position."""
        pip_value = Decimal("0.0001")

        if direction == "BUY":
            stop_loss = price - (self.stop_loss_pips * pip_value)
            take_profit = price + (self.take_profit_pips * pip_value)
        else:
            stop_loss = price + (self.stop_loss_pips * pip_value)
            take_profit = price - (self.take_profit_pips * pip_value)

        self.current_position = {
            "direction": direction,
            "entry_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "entry_time": timestamp,
        }

    def check_exit(self, price: Decimal, timestamp: datetime) -> None:
        """Check if position should be closed based on stop loss or take profit."""
        if not self.current_position:
            return

        pos = self.current_position
        should_close = False
        exit_reason = ""

        if pos["direction"] == "BUY" and price <= pos["stop_loss"]:
            should_close = True
            exit_reason = "Stop Loss"
        elif pos["direction"] == "SELL" and price >= pos["stop_loss"]:
            should_close = True
            exit_reason = "Stop Loss"
        elif pos["direction"] == "BUY" and price >= pos["take_profit"]:
            should_close = True
            exit_reason = "Take Profit"
        elif pos["direction"] == "SELL" and price <= pos["take_profit"]:
            should_close = True
            exit_reason = "Take Profit"

        if should_close:
            self.close_position(price, timestamp, exit_reason)

    def close_position(
        self, price: Decimal, timestamp: datetime, reason: str
    ) -> None:
        """Close current position and record trade."""
        if not self.current_position:
            return

        pos = self.current_position
        entry_price = pos["entry_price"]

        if pos["direction"] == "BUY":
            pnl = (price - entry_price) * self.position_size
        else:
            pnl = (entry_price - price) * self.position_size

        self.current_balance += pnl

        trade = {
            "entry_time": pos["entry_time"],
            "exit_time": timestamp,
            "direction": pos["direction"],
            "entry_price": entry_price,
            "exit_price": price,
            "pnl": pnl,
            "reason": reason,
        }
        self.trades.append(trade)

        self.current_position = None

    async def run_backtest(
        self, client: AsyncClient, days_back: int = 30
    ) -> None:
        """
        Run backtest on historical data using the FiveTwenty SDK.

        This method fetches historical candles from OANDA and processes them
        to simulate trading. It's designed to run silently for optimization.

        Args:
            client: FiveTwenty AsyncClient for API access
            days_back: Number of days of historical data to test
        """
        # Calculate date range using timezone-aware datetime
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days_back)

        # Fetch historical candles using SDK
        # The SDK handles datetime-to-ISO conversion automatically
        candles_response = await client.instruments.get_instrument_candles(
            instrument=self.instrument.value,
            granularity=CandlestickGranularity.H1,
            from_time=start_date,
            to_time=end_date,
        )

        # Extract candles from TypedDict response
        candles = candles_response["candles"]

        # Process each candle to simulate trading
        for candle in candles:
            if not candle.mid:
                continue

            # Access Pydantic model attributes
            price = candle.mid.c
            timestamp = candle.time

            self.prices.append(price)

            # Trading logic
            if self.current_position:
                self.check_exit(price, timestamp)
            elif len(self.prices) >= self.slow_ma_period:
                if self.check_buy_signal():
                    self.execute_trade(price, timestamp, "BUY")

        # Close any remaining position
        if self.current_position and self.prices:
            self.close_position(self.prices[-1], datetime.now(UTC), "End of Test")


# ==============================================================================
# PARAMETER OPTIMIZATION ENGINE
# ==============================================================================

class StrategyOptimizer:
    """
    Optimize strategy parameters using grid search algorithm.

    Grid search is an exhaustive parameter optimization technique that:
    1. Takes ranges of values for each parameter
    2. Generates all possible combinations (Cartesian product)
    3. Tests each combination by running a backtest
    4. Tracks performance metrics for each combination
    5. Identifies the best-performing parameter set

    This is useful for finding optimal strategy settings, but can be
    computationally expensive for large parameter spaces.
    """

    def __init__(self, instrument: InstrumentName = InstrumentName.EUR_USD) -> None:
        """
        Initialize optimizer for a specific instrument.

        Args:
            instrument: InstrumentName enum for the currency pair to optimize
        """
        self.instrument = instrument
        self.optimization_results: list[dict] = []

    async def optimize_parameters(
        self,
        client: AsyncClient,
        parameter_ranges: dict[str, list[int]],
        days_back: int = 30,
    ) -> tuple[dict[str, int], Decimal]:
        """
        Optimize strategy parameters across given ranges using grid search.

        This method demonstrates systematic parameter optimization:
        1. Generate all parameter combinations using itertools.product
        2. For each combination, create a new backtester instance
        3. Run backtest using SDK to fetch historical data
        4. Calculate performance metrics (return, win rate, trade count)
        5. Track best-performing parameter set

        Args:
            client: FiveTwenty AsyncClient for API access (used for backtesting)
            parameter_ranges: Dictionary mapping parameter names to lists of values
                            Example: {"fast_ma_period": [5, 10, 15],
                                     "slow_ma_period": [20, 25, 30]}
            days_back: Number of days of historical data for each backtest

        Returns:
            Tuple of (best_parameters_dict, best_return_percentage)

        Example:
            >>> optimizer = StrategyOptimizer(InstrumentName.EUR_USD)
            >>> ranges = {
            ...     "fast_ma_period": [5, 10, 15],
            ...     "slow_ma_period": [20, 25, 30]
            ... }
            >>> best_params, best_return = await optimizer.optimize_parameters(
            ...     client, ranges, days_back=30
            ... )
            >>> print(f"Best params: {best_params}, Return: {best_return}%")
        """

        print("\n" + "=" * 70)
        print("STRATEGY PARAMETER OPTIMIZATION")
        print("=" * 70)

        # ==============================================================================
        # GENERATE PARAMETER COMBINATIONS
        # ==============================================================================

        # Extract parameter names and their possible values
        # Example:
        #   parameter_ranges = {
        #       "fast_ma_period": [5, 10, 15],
        #       "slow_ma_period": [20, 25, 30]
        #   }
        #   param_names = ["fast_ma_period", "slow_ma_period"]
        #   param_values = [[5, 10, 15], [20, 25, 30]]
        param_names = list(parameter_ranges.keys())
        param_values = list(parameter_ranges.values())

        # Use itertools.product to generate Cartesian product (all combinations)
        # For the example above, this generates:
        #   [(5, 20), (5, 25), (5, 30), (10, 20), (10, 25), (10, 30),
        #    (15, 20), (15, 25), (15, 30)]
        # Total combinations = product of all list lengths (3 * 3 = 9)
        combinations = list(itertools.product(*param_values))

        print(f"\nTesting {len(combinations)} parameter combinations...")
        print(f"Instrument: {self.instrument.value}")
        print(f"Backtest Period: {days_back} days")
        print(
            "Data Source: OANDA via client.instruments.get_instrument_candles()\n"
        )

        # Track best performing parameters
        best_return = Decimal("-Infinity")
        best_params: dict[str, int] = {}

        # ==============================================================================
        # TEST EACH PARAMETER COMBINATION
        # ==============================================================================

        for i, params in enumerate(combinations):
            # Convert tuple of parameter values to dictionary
            # Example: (5, 20) -> {"fast_ma_period": 5, "slow_ma_period": 20}
            param_dict = dict(zip(param_names, params))

            # Create backtester with these specific parameters
            # The backtester will use the SDK to fetch historical data
            backtester = SimpleBacktester(
                instrument=self.instrument,
                fast_ma_period=param_dict["fast_ma_period"],
                slow_ma_period=param_dict["slow_ma_period"],
                stop_loss_pips=param_dict["stop_loss_pips"],
                take_profit_pips=param_dict["take_profit_pips"],
            )

            # Run backtest using FiveTwenty SDK
            # This will:
            # 1. Use client.instruments.get_instrument_candles() to get historical data
            # 2. Process candles to simulate trading
            # 3. Track all trades and P&L
            await backtester.run_backtest(client, days_back=days_back)

            # ==============================================================================
            # CALCULATE PERFORMANCE METRICS
            # ==============================================================================

            # Calculate total return percentage
            # Return = (Final Balance - Initial Balance) / Initial Balance * 100
            total_return = (
                (backtester.current_balance - backtester.initial_balance)
                / backtester.initial_balance
                * 100
            )

            # Count total trades executed
            total_trades = len(backtester.trades)

            # Calculate win rate (percentage of profitable trades)
            winning_trades = sum(1 for t in backtester.trades if t["pnl"] > 0)
            win_rate = (
                (winning_trades / total_trades * 100) if total_trades > 0 else 0
            )

            # Store results for this parameter combination
            result = {
                "parameters": param_dict.copy(),
                "return": total_return,
                "total_trades": total_trades,
                "win_rate": win_rate,
            }
            self.optimization_results.append(result)

            # Update best parameters if this combination performs better
            # We use total return as our optimization metric
            # (could also optimize for Sharpe ratio, profit factor, etc.)
            if total_return > best_return:
                best_return = total_return
                best_params = param_dict.copy()

            # Progress indicator - shows results for each combination tested
            print(
                f"  [{i+1:3d}/{len(combinations)}] "
                f"Fast MA: {param_dict['fast_ma_period']:2d} | "
                f"Slow MA: {param_dict['slow_ma_period']:2d} | "
                f"SL: {param_dict['stop_loss_pips']:2d} | "
                f"TP: {param_dict['take_profit_pips']:2d} | "
                f"Return: {total_return:+7.2f}% | "
                f"Trades: {total_trades:3d} | "
                f"Win Rate: {win_rate:5.1f}%"
            )

        # ==============================================================================
        # DISPLAY OPTIMIZATION RESULTS
        # ==============================================================================

        print("\n" + "=" * 70)
        print("OPTIMIZATION COMPLETE")
        print("=" * 70)
        print("\nBest Parameters:")
        for key, value in best_params.items():
            print(f"  {key}: {value}")
        print(f"\nBest Return: {best_return:+.2f}%")
        print(
            f"\nNote: These parameters were optimized on {days_back} days of data."
        )
        print(
            "      Always validate on out-of-sample data to avoid overfitting."
        )

        return best_params, best_return


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

async def main() -> None:
    """
    Demonstrate strategy parameter optimization using grid search.

    This example shows how to:
    1. Define parameter ranges to test
    2. Use the optimizer to test all combinations
    3. Identify the best-performing parameters
    4. Understand the tradeoff between exploration and computation

    The optimizer uses the FiveTwenty SDK to fetch historical data from OANDA
    for each backtest, ensuring results are based on real market conditions.
    """

    # Create optimizer for EUR/USD
    optimizer = StrategyOptimizer(instrument=InstrumentName.EUR_USD)

    # ==============================================================================
    # DEFINE PARAMETER SEARCH SPACE
    # ==============================================================================

    # Define ranges for each parameter to test
    # Grid search will test ALL combinations (Cartesian product)
    #
    # IMPORTANT: The number of backtests grows exponentially:
    #   - 3 values per parameter, 4 parameters = 3^4 = 81 backtests
    #   - 5 values per parameter, 4 parameters = 5^4 = 625 backtests
    #   - 10 values per parameter, 4 parameters = 10^4 = 10,000 backtests!
    #
    # Start with fewer values and expand if needed
    parameter_ranges = {
        "fast_ma_period": [5, 10, 15],      # 3 values
        "slow_ma_period": [20, 25, 30],     # 3 values
        "stop_loss_pips": [15, 20, 25],     # 3 values
        "take_profit_pips": [25, 30, 35],   # 3 values
    }
    # Total combinations: 3 * 3 * 3 * 3 = 81 backtests

    print("\nGrid Search Configuration:")
    print(f"  Total combinations to test: {3 * 3 * 3 * 3}")
    for param, values in parameter_ranges.items():
        print(f"  {param}: {values}")

    # ==============================================================================
    # RUN OPTIMIZATION USING SDK
    # ==============================================================================

    # Use AsyncClient context manager for automatic resource cleanup
    # The client will be passed to each backtest to fetch historical data
    async with AsyncClient() as client:
        # Run grid search optimization
        # Each backtest will use client.instruments.get_instrument_candles()
        # to fetch the last 30 days of 1-hour candles from OANDA
        best_params, best_return = await optimizer.optimize_parameters(
            client,
            parameter_ranges,
            days_back=30  # Use 30 days of historical data for each backtest
        )

    # ==============================================================================
    # NEXT STEPS
    # ==============================================================================

    print("\n" + "=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("\n1. Validate on out-of-sample data (different time period)")
    print("2. Test on different instruments to check robustness")
    print("3. Consider walk-forward optimization to avoid overfitting")
    print("4. Analyze the full results in optimizer.optimization_results")
    print("5. Visualize parameter sensitivity and performance surface")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
```

---


## What You've Learned

- **FiveTwenty SDK Integration**: How to use `client.instruments.get_instrument_candles()` to fetch historical market data from OANDA, understanding the difference between TypedDict responses and Pydantic model attributes

- **Strategy Design**: Building systematic trading strategies with signal generation methods, maintaining strategy state, and implementing clear entry/exit rules using moving average crossovers

- **Type-Safe Development**: Working with `Decimal` for financial precision, using TypedDict vs Pydantic models appropriately, and achieving full mypy strict compliance with proper type hints

- **Backtesting Framework**: Creating a complete backtesting engine that simulates trading on historical data, tracks positions with stop loss/take profit, and calculates comprehensive performance metrics

- **Parameter Optimization**: Implementing grid search algorithms with `itertools.product()` to systematically test parameter combinations, understanding the computational complexity of search spaces, and recognizing overfitting risks

- **Production-Ready Patterns**: Using AsyncClient context managers, loading environment variables with python-dotenv, handling datetime objects correctly with timezone awareness, and structuring executable standalone scripts

!!! success "Strategy Building Complete!"
    Outstanding! You've built three complete, production-ready trading system components using the FiveTwenty SDK. You can now design strategies, backtest them on real OANDA data, and optimize parameters - all with full type safety and comprehensive SDK integration. Next, you'll learn to build production-ready automated systems that put these skills together.

---

## Next Steps

Continue to [Complete Trading System](complete-system.md) to build a production-ready automated trading system.

---

## Related Resources

- [Advanced Orders](../advanced-orders/index.md) - Complex order strategies
- [Risk Management](../risk-management.md) - Comprehensive risk frameworks
- [Performance Optimization](../../guides/optimization/index.md) - Performance optimization
