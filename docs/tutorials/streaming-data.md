# Real-time Streaming Data with FiveTwenty

Learn to implement real-time market data streaming, automated trading systems, and live data processing using the FiveTwenty SDK.

## Learning Objectives

By the end of this tutorial, you will:

- Understand FiveTwenty's streaming data capabilities
- Implement price streams and account monitoring
- Build automated trading systems with real-time data
- Handle connection management and error recovery
- Create production-ready streaming applications

## Prerequisites

- Completed [Basic Trading Tutorial](basic-trading/index.md)
- Understanding of async programming in Python
- FiveTwenty setup with streaming access

## Types of Streaming Data

FiveTwenty supports three main types of streaming data:

### Price Streams

Stream real-time bid/ask prices for currency pairs with live market data. Price streams provide tick-by-tick updates as the market moves, enabling real-time analysis and automated trading strategies.

<!-- filepath: example_basic_price_streaming.py -->
```python
# ==============================================================================
# BASIC REAL-TIME PRICE STREAMING
# ==============================================================================

# This example demonstrates fundamental price streaming from OANDA:
#
# KEY CONCEPTS:
# 1. Price Streaming - Receive live bid/ask prices as market moves
# 2. Async Iteration - Use async for to process streaming data efficiently
# 3. Type Filtering - Distinguish between price updates and heartbeats
# 4. Spread Calculation - Measure market liquidity through bid-ask spread
# 5. Multi-Instrument - Monitor multiple currency pairs simultaneously
#
# HOW IT WORKS:
# Connect to OANDA's streaming price endpoint and subscribe to EUR/USD and GBP/USD.
# The stream sends real-time price updates whenever the market moves, plus periodic
# heartbeats to confirm connection health. Use isinstance() to filter for actual
# ClientPrice objects (not heartbeats). Extract bid and ask prices from the price
# data, calculate spreads in pips, and track updates per instrument. The async for
# loop processes each message as it arrives without blocking.
#
# This code is fully executable and demonstrates basic price streaming fundamentals.

import asyncio
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice

load_dotenv()


async def main() -> None:
    """Execute basic price streaming demonstration."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # CONFIGURE STREAMING INSTRUMENTS
        # ==============================================================================

        instruments = ["EUR_USD", "GBP_USD"]
        print(f"Streaming prices for: {', '.join(instruments)}")
        print(f"Account: {client.account_id}")
        print("Press Ctrl+C to stop\n")

        # ==============================================================================
        # INITIALIZE STATISTICS TRACKING
        # ==============================================================================

        stats = {
            "total_updates": 0,
            "heartbeats": 0,
            "eur_usd_count": 0,
            "gbp_usd_count": 0,
        }

        # ==============================================================================
        # START PRICE STREAMING
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.pricing.get_pricing_stream()
        # ==============================================================================
        #
        # Stream real-time pricing updates for specified instruments
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instruments: List of instruments to stream (e.g., ["EUR_USD", "GBP_USD"])
        #
        # Returns: Async iterator of ClientPrice or PricingHeartbeat objects
        #
        # NOTE: Use isinstance(price_data, ClientPrice) to filter price updates
        #       Heartbeats indicate connection health but contain no price data
        #       Stream continues indefinitely until manually stopped

        try:
            async for price_data in client.pricing.get_pricing_stream(
                account_id=client.account_id, instruments=instruments
            ):
                # ==============================================================================
                # PROCESS DIFFERENT MESSAGE TYPES
                # ==============================================================================

                # Check if this is a real price update (not a heartbeat)
                if isinstance(price_data, ClientPrice):
                    # Type narrowed to ClientPrice - real price update received
                    stats["total_updates"] += 1

                    # ==============================================================================
                    # EXTRACT BID AND ASK PRICES
                    # ==============================================================================

                    # OANDA provides bids and asks as lists
                    # Use first element for best available price
                    bid = (
                        Decimal(str(price_data.bids[0].price))
                        if price_data.bids
                        else None
                    )
                    ask = (
                        Decimal(str(price_data.asks[0].price))
                        if price_data.asks
                        else None
                    )

                    if bid is None or ask is None:
                        continue

                    # ==============================================================================
                    # CALCULATE SPREAD IN PIPS
                    # ==============================================================================

                    # Spread = difference between ask and bid prices
                    # Convert to pips: multiply by 10,000 for most pairs (100 for JPY pairs)
                    spread = ask - bid
                    spread_pips = spread * Decimal("10000")

                    # Track instrument-specific updates
                    if price_data.instrument == "EUR_USD":
                        stats["eur_usd_count"] += 1
                    elif price_data.instrument == "GBP_USD":
                        stats["gbp_usd_count"] += 1

                    print(
                        f"{price_data.instrument}: {bid:.5f} / {ask:.5f} "
                        f"(spread: {spread_pips:.1f} pips)",
                        flush=True,
                    )

                else:
                    # Heartbeat message - connection health indicator
                    stats["heartbeats"] += 1
                    if stats["heartbeats"] % 10 == 0:
                        print(
                            f"Heartbeat #{stats['heartbeats']} - Connection healthy",
                            flush=True,
                        )

                # ==============================================================================
                # DEMONSTRATION LIMIT
                # ==============================================================================

                # Stop after 1 price update for demonstration purposes
                # Remove this limit for continuous streaming
                if stats["total_updates"] >= 1:
                    print("\nStopping demonstration (1 update received)")
                    break

        except KeyboardInterrupt:
            print("\nStreaming stopped by user")
        except Exception as e:
            print(f"\nStreaming error: {e}")

        # ==============================================================================
        # DISPLAY STREAMING SESSION STATISTICS
        # ==============================================================================

        print("\nStreaming Session Statistics:")
        print(f"  Total Updates: {stats['total_updates']}")
        print(f"  EUR/USD Updates: {stats['eur_usd_count']}")
        print(f"  GBP/USD Updates: {stats['gbp_usd_count']}")
        print(f"  Heartbeats: {stats['heartbeats']}")


if __name__ == "__main__":
    asyncio.run(main())
```

### Account Streams

Monitor account changes and trade updates in real-time using OANDA's transaction stream. This provides instant notification of all account activity including order placements, fills, position changes, and account modifications.

<!-- filepath: example_transaction_streaming.py -->
```python
# ==============================================================================
# REAL-TIME ACCOUNT TRANSACTION STREAMING
# ==============================================================================

# This example demonstrates monitoring account activity with transaction streams:
#
# KEY CONCEPTS:
# 1. Transaction Streaming - Receive real-time notifications of all account changes
# 2. Transaction Types - Handle ORDER_FILL, MARKET_ORDER, LIMIT_ORDER, etc.
# 3. P&L Tracking - Calculate realized profits and losses from order fills
# 4. Type Safety - Use getattr() for safe attribute access on union types
# 5. Activity Monitoring - Track trading volume, fill counts, and transaction patterns
#
# HOW IT WORKS:
# Connect to OANDA's transaction stream to receive instant notifications whenever
# anything happens in your account: orders placed, orders filled, positions opened
# or closed, stop losses triggered, and more. The stream returns different transaction
# types as a union model. Extract the transaction type and use conditional logic to
# process each type appropriately. For ORDER_FILL transactions, calculate cumulative
# realized P&L. For other transactions, log the activity for audit trails.
#
# This code is fully executable and demonstrates account transaction monitoring.

import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


async def main() -> None:
    """Execute account transaction streaming demonstration."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # INITIALIZE TRANSACTION TRACKING
        # ==============================================================================

        stats: dict[str, Any] = {
            "total_transactions": 0,
            "order_fills": 0,
            "transaction_types": {},
            "realized_pl": Decimal("0"),
        }

        print(f"Monitoring transactions for account: {client.account_id}")
        print("Press Ctrl+C to stop\n")

        # ==============================================================================
        # START TRANSACTION STREAMING
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.transactions.get_transactions_stream()
        # ==============================================================================
        #
        # Stream real-time transaction events for an account
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #
        # Returns: Async iterator of Transaction union models
        #
        # NOTE: Use async for to iterate over streaming transactions
        #       Different transaction types (ORDER_FILL, MARKET_ORDER, etc.)
        #       Streams all account state changes in real-time

        try:
            async for transaction in client.transactions.get_transactions_stream(
                account_id=client.account_id
            ):
                stats["total_transactions"] += 1

                # Track transaction type
                tx_type = transaction.type
                if tx_type not in stats["transaction_types"]:
                    stats["transaction_types"][tx_type] = 0
                stats["transaction_types"][tx_type] += 1

                # Process ORDER_FILL transactions for P&L tracking
                if tx_type == "ORDER_FILL":
                    stats["order_fills"] += 1

                    # Track realized P&L if available
                    if hasattr(transaction, "pl") and transaction.pl:
                        pl = Decimal(str(transaction.pl))
                        stats["realized_pl"] += pl

                        # Get instrument and units with type safety
                        instrument = getattr(transaction, "instrument", "N/A")
                        units = getattr(transaction, "units", "N/A")
                        print(
                            f"ORDER_FILL: {instrument} "
                            f"units={units} P&L={pl:+.2f}"
                        )
                elif hasattr(transaction, "id"):
                    # Most transactions have an id attribute
                    print(f"Transaction: {tx_type} (ID: {transaction.id})")
                else:
                    # Heartbeat or other transaction without id
                    print(f"Transaction: {tx_type}")

                # Display stats every 5 transactions
                if stats["total_transactions"] % 5 == 0:
                    print(f"\nStats: {stats['total_transactions']} transactions, "
                          f"{stats['order_fills']} fills, "
                          f"P&L: {stats['realized_pl']:+.2f}\n")

                # Stop after 1 transactions for demonstration
                if stats["total_transactions"] >= 1:
                    print("\nStopping demonstration (1 transactions received)")
                    break

        except KeyboardInterrupt:
            print("\nStreaming stopped by user")
        except Exception as e:
            print(f"\nStreaming error: {e}")

        # ==============================================================================
        # DISPLAY FINAL STATISTICS
        # ==============================================================================

        print("\nTransaction Streaming Summary:")
        print(f"  Total Transactions: {stats['total_transactions']}")
        print(f"  Order Fills: {stats['order_fills']}")
        print(f"  Realized P&L: {stats['realized_pl']:+.2f}")
        print(f"  Transaction Types: {list(stats['transaction_types'].keys())}")


if __name__ == "__main__":
    asyncio.run(main())
```

## Automated Trading with Streaming Data

### Signal Generation from Price Streams

Build automated trading systems that generate buy/sell signals from real-time price data. This example demonstrates calculating moving averages from streaming prices and executing market orders when signals trigger. The system uses a rolling window of prices to compute a 10-period moving average, then places orders with stop-loss protection when the current price crosses above the average by a threshold percentage. This pattern forms the foundation of many algorithmic trading strategies.

<!-- filepath: example_price_analysis_trading.py -->
```python
# ==============================================================================
# AUTOMATED TRADING WITH STREAMING PRICE ANALYSIS
# ==============================================================================

# This example demonstrates algorithmic trading with real-time price streams:
#
# KEY CONCEPTS:
# 1. Moving Average Signals - Calculate MA from streaming prices for trend detection
# 2. Real-time Analysis - Process price data as it arrives, not on fixed intervals
# 3. Automated Execution - Place orders automatically when signals trigger
# 4. Risk Management - Attach stop losses to every trade for protection
# 5. Type Safety - Use Decimal for financial calculations, avoid float precision issues
#
# HOW IT WORKS:
# Connect to OANDA's streaming price API and receive tick-by-tick EUR/USD prices.
# Calculate a rolling 10-period moving average using a deque for efficient windowing.
# Generate buy signals when current price exceeds the MA by 0.1%, indicating upward
# momentum. Execute market orders with automatic 50-pip stop losses. The system
# processes each price update in real-time and acts immediately on signals.
#
# This code is fully executable and demonstrates streaming-based algorithmic trading.

import asyncio
from collections import deque
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, InstrumentName

load_dotenv()


class MovingAverageSignal:
    """Calculate moving average signals from streaming price data."""

    def __init__(self, window_size: int = 20):
        """Initialize moving average calculator.

        Args:
            window_size: Number of prices to include in moving average
        """
        self.window_size = window_size
        self.prices: deque[Decimal] = deque(maxlen=window_size)

    def add_price(self, price: Decimal) -> Decimal | None:
        """Add price and return moving average if window is full.

        Args:
            price: Mid-market price to add to window

        Returns:
            Moving average if window is full, None otherwise
        """
        self.prices.append(price)

        if len(self.prices) == self.window_size:
            return sum(self.prices, Decimal("0")) / Decimal(len(self.prices))
        return None


async def main() -> None:
    """Execute automated trading system with streaming price analysis."""

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # INITIALIZE TRADING SYSTEM
        # ==============================================================================

        signal = MovingAverageSignal(window_size=10)
        print("Automated Trading System")
        print(f"Moving Average Window: {signal.window_size} periods")
        print("Signal Threshold: Price > MA * 1.001 (0.1% above MA)\n")

        # ==============================================================================
        # STREAM REAL-TIME PRICES AND GENERATE SIGNALS
        # ==============================================================================

        # ==============================================================================
        # SDK METHOD: client.pricing.get_pricing_stream()
        # ==============================================================================
        #
        # Stream real-time pricing updates for specified instruments
        #
        # Parameters:
        #   - account_id: Your OANDA account ID
        #   - instruments: List of instruments to stream
        #
        # Returns: Async iterator of ClientPrice or PricingHeartbeat objects
        #
        # NOTE: Use async for to iterate over streaming price updates
        #       Check isinstance(price_data, ClientPrice) to filter real prices
        #       Heartbeats indicate connection health but contain no price data

        price_count = 0
        async for price_data in client.pricing.get_pricing_stream(
            account_id=client.account_id, instruments=["EUR_USD"]
        ):
            # Filter for price updates (ignore heartbeats)
            if not isinstance(price_data, ClientPrice):
                continue

            price_count += 1
            # Safety limit for demonstration
            if price_count > 5:
                print("\nStopping demonstration (5 prices processed)")
                break

            # ==============================================================================
            # CALCULATE MID-MARKET PRICE
            # ==============================================================================

            # Extract bid/ask prices from streaming data
            # OANDA provides bids and asks as lists (use first element for best price)
            bid_price = (
                Decimal(str(price_data.bids[0].price)) if price_data.bids else None
            )
            ask_price = (
                Decimal(str(price_data.asks[0].price)) if price_data.asks else None
            )

            if bid_price is None or ask_price is None:
                continue

            # Calculate mid-market price (average of bid and ask)
            mid_price = (bid_price + ask_price) / Decimal("2")

            # ==============================================================================
            # UPDATE MOVING AVERAGE AND CHECK FOR SIGNAL
            # ==============================================================================

            ma = signal.add_price(mid_price)

            if ma is None:
                # Still filling moving average window
                print(
                    f"Building MA window: {len(signal.prices)}/{signal.window_size} prices"
                )
                continue

            # Check for buy signal: price crosses above MA by threshold
            threshold = ma * Decimal("1.001")  # 0.1% above moving average

            if mid_price > threshold:
                print("\nBUY SIGNAL DETECTED")
                print(f"  Mid Price: {mid_price:.5f}")
                print(f"  Moving Average: {ma:.5f}")
                print(f"  Threshold: {threshold:.5f}")

                # ==============================================================================
                # EXECUTE MARKET ORDER WITH STOP LOSS
                # ==============================================================================

                # ==============================================================================
                # SDK METHOD: client.orders.post_market_order()
                # ==============================================================================
                #
                # Place a market order with stop-loss protection
                #
                # Parameters:
                #   - account_id: Your OANDA account ID
                #   - instrument: Currency pair to trade (InstrumentName enum)
                #   - units: Position size (positive=buy, negative=sell)
                #   - stop_loss: Stop loss price (Decimal)
                #
                # Returns: OrderResponse TypedDict with trade execution details
                #
                # NOTE: Stop loss is attached automatically when order fills
                #       OrderResponse is TypedDict (use dictionary access)

                # Calculate stop loss 50 pips below entry
                stop_loss_price = mid_price - Decimal("0.0050")

                order_response = await client.orders.post_market_order(
                    account_id=client.account_id,
                    instrument=InstrumentName("EUR_USD"),
                    units=1000,
                    stop_loss=stop_loss_price,
                )

                # OrderResponse is TypedDict, orderFillTransaction is Pydantic model
                fill_tx = order_response["orderFillTransaction"]
                print(f"  Order Executed: {fill_tx.id}")
                print(f"  Stop Loss: {stop_loss_price:.5f}")
                print(
                    "  Stopping demonstration (order placed successfully)\n", flush=True
                )
                break

            else:
                # No signal - display current status
                print(
                    f"EUR/USD: {mid_price:.5f} | MA: {ma:.5f} | No signal", flush=True
                )


if __name__ == "__main__":
    asyncio.run(main())
```

### Order Management with Real-time Updates

Demonstrate running price and transaction streams concurrently for unified market and account monitoring. This pattern enables real-time position tracking and coordinated data analysis across multiple streaming endpoints.

<!-- filepath: example_concurrent_stream_monitoring.py -->
```python
# ==============================================================================
# CONCURRENT STREAM MONITORING WITH POSITION TRACKING
# ==============================================================================

# This example demonstrates concurrent monitoring of multiple streaming APIs:
#
# KEY CONCEPTS:
# 1. Concurrent Streaming - Run price and transaction streams simultaneously
# 2. Task Coordination - Use asyncio.gather() to manage multiple async tasks
# 3. Shared State - Track positions across both streams with PositionManager
# 4. Transaction Processing - Handle different transaction types (FILL, CREATE, CANCEL)
# 5. Type Safety - Use getattr() for safe attribute access on union types
#
# HOW IT WORKS:
# Launch two concurrent async tasks: one monitoring EUR/USD price stream, another
# monitoring account transaction stream. Both tasks run simultaneously using
# asyncio.create_task() and are coordinated with asyncio.gather(). The shared
# PositionManager tracks position changes from order fills in real-time. When
# transactions arrive, the system identifies the type and updates position state
# accordingly. This pattern enables unified monitoring of market data and account
# activity in a single application.
#
# This code is fully executable and demonstrates concurrent streaming patterns.

import asyncio
from decimal import Decimal
from typing import Any

from dotenv import load_dotenv

from fivetwenty import AsyncClient

load_dotenv()


class PositionManager:
    """Track open positions and pending orders from transaction stream."""

    def __init__(self) -> None:
        """Initialize position manager with empty tracking dictionaries."""
        self.open_positions: dict[str, int] = {}
        self.pending_orders: dict[str, str] = {}
        self.transaction_count = 0

    async def handle_transaction(self, transaction: Any) -> None:
        """Handle incoming transaction stream data.

        Args:
            transaction: Transaction union type from stream
        """
        self.transaction_count += 1

        # Check transaction type and handle accordingly
        # Transaction types: ORDER_FILL, ORDER_CREATE, ORDER_CANCEL, etc.
        tx_type = getattr(transaction, "type", None)

        if tx_type == "ORDER_FILL":
            await self.update_position(transaction)
        elif tx_type == "ORDER_CREATE":
            order_id = getattr(transaction, "order_id", None)
            if order_id:
                self.pending_orders[order_id] = tx_type
                print(f"Order created: {order_id}")
        elif tx_type == "ORDER_CANCEL":
            order_id = getattr(transaction, "order_id", None)
            if order_id:
                self.pending_orders.pop(order_id, None)
                print(f"Order cancelled: {order_id}")

    async def update_position(self, fill_transaction: Any) -> None:
        """Update position tracking on order fill.

        Args:
            fill_transaction: OrderFillTransaction from stream
        """
        # Safe attribute access for union types
        instrument = getattr(fill_transaction, "instrument", "UNKNOWN")
        units_decimal = getattr(fill_transaction, "units", Decimal("0"))
        units = int(units_decimal)

        if instrument not in self.open_positions:
            self.open_positions[instrument] = 0

        self.open_positions[instrument] += units
        print(
            f"Position updated: {instrument} = {self.open_positions[instrument]} units"
        )


async def monitor_prices(
    client: AsyncClient, _position_manager: PositionManager
) -> None:
    """Monitor price streams for EUR/USD.

    Args:
        client: AsyncClient instance for API access
        _position_manager: Shared position manager (unused in this simplified example)
    """
    print("Price monitoring task started")

    # ==============================================================================
    # SDK METHOD: client.pricing.get_pricing_stream()
    # ==============================================================================
    #
    # Stream real-time pricing updates for specified instruments
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #   - instruments: List of instruments to stream
    #
    # Returns: Async iterator of ClientPrice or PricingHeartbeat objects
    #
    # NOTE: This runs concurrently with transaction monitoring
    #       Can coordinate with position_manager for unified state

    price_count = 0

    async for _price_data in client.pricing.get_pricing_stream(
        account_id=client.account_id, instruments=["EUR_USD"]
    ):
        price_count += 1

        # Price-based logic would go here
        # For demonstration, just count prices received
        if price_count % 10 == 0:
            print(f"  Received {price_count} price updates")

        # Stop after 1 price updates for demonstration
        if price_count >= 1:
            print("Price monitoring complete")
            break


async def monitor_transactions(
    client: AsyncClient, position_manager: PositionManager
) -> None:
    """Monitor transaction streams for account activity.

    Args:
        client: AsyncClient instance for API access
        position_manager: Shared position manager for state tracking
    """
    print("Transaction monitoring task started")

    # ==============================================================================
    # SDK METHOD: client.transactions.get_transactions_stream()
    # ==============================================================================
    #
    # Stream real-time transaction events for an account
    #
    # Parameters:
    #   - account_id: Your OANDA account ID
    #
    # Returns: Async iterator of Transaction union models
    #
    # NOTE: Different transaction types (ORDER_FILL, ORDER_CREATE, etc.)
    #       Runs concurrently with price monitoring for real-time coordination

    async for transaction in client.transactions.get_transactions_stream(
        account_id=client.account_id
    ):
        await position_manager.handle_transaction(transaction)

        # Stop after 1 transactions for demonstration
        if position_manager.transaction_count >= 1:
            print("Transaction monitoring complete")
            break


async def main() -> None:
    """Execute concurrent price and transaction stream monitoring."""

    print("=" * 60)
    print("CONCURRENT STREAM MONITORING DEMONSTRATION")
    print("=" * 60)
    print()

    # ==============================================================================
    # CONNECT TO OANDA
    # ==============================================================================

    # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
    # Context manager ensures proper cleanup of HTTP connections
    async with AsyncClient() as client:
        # ==============================================================================
        # INITIALIZE POSITION MANAGER
        # ==============================================================================

        position_manager = PositionManager()

        print(f"Account: {client.account_id}")
        print("Starting concurrent monitoring of:")
        print("  - Price stream (EUR/USD)")
        print("  - Transaction stream (all account activity)")
        print()

        # ==============================================================================
        # RUN CONCURRENT STREAMING TASKS
        # ==============================================================================

        # Create concurrent tasks for price and transaction monitoring
        # asyncio.create_task() schedules coroutines for concurrent execution
        # asyncio.gather() waits for all tasks to complete
        price_task = asyncio.create_task(monitor_prices(client, position_manager))
        transaction_task = asyncio.create_task(
            monitor_transactions(client, position_manager)
        )

        # Wait for both tasks to complete
        # If either task raises an exception, gather() will propagate it
        try:
            await asyncio.gather(price_task, transaction_task)
        except Exception as e:
            print(f"\nError during monitoring: {e}")

        # ==============================================================================
        # DISPLAY FINAL STATISTICS
        # ==============================================================================

        print("\n" + "=" * 60)
        print("MONITORING SUMMARY")
        print("=" * 60)
        print(f"Transactions Processed: {position_manager.transaction_count}")
        print(f"Open Positions: {len(position_manager.open_positions)}")
        print(f"Pending Orders: {len(position_manager.pending_orders)}")

        if position_manager.open_positions:
            print("\nPosition Details:")
            for instrument, units in position_manager.open_positions.items():
                print(f"  {instrument}: {units:+,} units")


if __name__ == "__main__":
    asyncio.run(main())
```


## Complete Example

Build a production-ready streaming trading system with automatic reconnection, error handling, and Python logging. This comprehensive example integrates all concepts from this tutorial into a robust, continuously-running system suitable for real-world deployment.

<!-- filepath: example_production_streaming_system.py -->
```python
# ==============================================================================
# PRODUCTION-READY STREAMING TRADING SYSTEM
# ==============================================================================

# This example demonstrates a production-grade streaming system with resilience:
#
# KEY CONCEPTS:
# 1. Automatic Reconnection - Handle StreamStall exceptions and reconnect seamlessly
# 2. Error Isolation - Catch and log errors without crashing the entire system
# 3. Concurrent Monitoring - Run price and transaction streams simultaneously
# 4. Production Logging - Use Python logging for debugging and monitoring
# 5. Demo Mode - Safe testing mode that prevents live order execution
#
# HOW IT WORKS:
# This is a complete trading system that runs continuously, monitoring EUR/USD prices
# and account transactions concurrently. When streams stall or errors occur, the
# system automatically waits and reconnects. All operations are logged with timestamps
# and severity levels. Price data feeds a 20-period moving average signal generator.
# When signals trigger, the system can execute orders with stop losses (disabled in
# demo mode). The reconnection loop ensures 24/7 operation with graceful error recovery.
#
# This code is fully executable and demonstrates production streaming architecture.

import asyncio
import logging
from collections import deque
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall
from fivetwenty.models import ClientPrice, InstrumentName

load_dotenv()

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Setup logging for production monitoring
# Use INFO level for normal operation, DEBUG for troubleshooting
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class StreamingTradingSystem:
    """Production-ready streaming trading system with error handling and reconnection."""

    def __init__(self) -> None:
        """Initialize trading system."""
        self.prices: deque[Decimal] = deque(maxlen=100)  # Keep last 100 prices
        self.positions: dict[str, int] = {}
        self.demo_mode = True  # Set False for continuous operation

    async def run(self) -> None:
        """Main trading system loop with automatic reconnection."""
        reconnect_count = 0

        # ==============================================================================
        # RECONNECTION LOOP
        # ==============================================================================

        # Production systems should run continuously and reconnect on errors
        # This loop handles StreamStall exceptions and other failures
        while True:
            try:
                # ==============================================================================
                # CONNECT TO OANDA
                # ==============================================================================

                # AsyncClient automatically reads FIVETWENTY_OANDA_* environment variables
                # Context manager ensures proper cleanup of HTTP connections
                async with AsyncClient() as client:
                    logger.info("Starting streaming trading system")
                    logger.info(f"Account: {client.account_id}")
                    logger.info(f"Environment: {client.config.environment.value}")

                    # ==============================================================================
                    # CREATE CONCURRENT MONITORING TASKS
                    # ==============================================================================

                    # Run price and transaction monitoring concurrently
                    # asyncio.gather() returns when all tasks complete or one raises
                    tasks = [
                        asyncio.create_task(self.monitor_prices(client)),
                        asyncio.create_task(self.monitor_transactions(client)),
                    ]

                    await asyncio.gather(*tasks)

                    # If demo mode, exit after tasks complete
                    if self.demo_mode:
                        logger.info("Demo mode complete")
                        break

            except StreamStall:
                # ==============================================================================
                # HANDLE STREAM STALL WITH RECONNECTION
                # ==============================================================================

                # StreamStall indicates no data received within timeout
                # Production systems should wait and reconnect
                reconnect_count += 1
                logger.warning(
                    f"Stream stalled (attempt {reconnect_count}), reconnecting in 5 seconds..."
                )
                await asyncio.sleep(5)

            except KeyboardInterrupt:
                logger.info("Shutdown requested by user")
                break

            except Exception as e:
                # ==============================================================================
                # HANDLE UNEXPECTED ERRORS
                # ==============================================================================

                # Log unexpected errors and attempt reconnection
                # Increase delay for persistent errors
                reconnect_count += 1
                logger.error(f"System error: {e}", exc_info=True)
                logger.info(f"Reconnecting in 10 seconds (attempt {reconnect_count})...")
                await asyncio.sleep(10)

    async def monitor_prices(self, client: AsyncClient) -> None:
        """Monitor price streams and generate trading signals.

        Args:
            client: AsyncClient instance for API access
        """
        logger.info("Price monitoring started")
        price_count = 0

        try:
            # ==============================================================================
            # SDK METHOD: client.pricing.get_pricing_stream()
            # ==============================================================================
            #
            # Stream real-time pricing updates for specified instruments
            #
            # Parameters:
            #   - account_id: Your OANDA account ID
            #   - instruments: List of instruments to stream
            #
            # Returns: Async iterator of ClientPrice or PricingHeartbeat objects
            #
            # NOTE: Runs indefinitely until error or manual stop
            #       Filter heartbeats with isinstance(price_data, ClientPrice)

            async for price_data in client.pricing.get_pricing_stream(
                account_id=client.account_id, instruments=["EUR_USD"]
            ):
                # Filter for actual price updates (ignore heartbeats)
                if not isinstance(price_data, ClientPrice):
                    continue

                price_count += 1

                try:
                    await self.process_price(client, price_data)
                except Exception as e:
                    logger.error(f"Price processing error: {e}", exc_info=True)

                # Demo mode: stop after 1 price
                if self.demo_mode and price_count >= 1:
                    logger.info("Price monitoring complete (demo limit reached)")
                    break

        except Exception as e:
            logger.error(f"Price monitoring error: {e}", exc_info=True)
            raise

    async def monitor_transactions(self, client: AsyncClient) -> None:
        """Monitor transaction streams for position updates.

        Args:
            client: AsyncClient instance for API access
        """
        logger.info("Transaction monitoring started")
        transaction_count = 0

        try:
            # ==============================================================================
            # SDK METHOD: client.transactions.get_transactions_stream()
            # ==============================================================================
            #
            # Stream real-time transaction events for an account
            #
            # Parameters:
            #   - account_id: Your OANDA account ID
            #
            # Returns: Async iterator of Transaction union models
            #
            # NOTE: Streams all account activity (orders, fills, modifications)
            #       Runs indefinitely until error or manual stop

            async for transaction in client.transactions.get_transactions_stream(
                account_id=client.account_id
            ):
                transaction_count += 1

                try:
                    await self.process_transaction(transaction)
                except Exception as e:
                    logger.error(f"Transaction processing error: {e}", exc_info=True)

                # Demo mode: stop after 1 transaction
                if self.demo_mode and transaction_count >= 1:
                    logger.info("Transaction monitoring complete (demo limit reached)")
                    break

        except Exception as e:
            logger.error(f"Transaction monitoring error: {e}", exc_info=True)
            raise

    async def process_price(self, client: AsyncClient, price_data: ClientPrice) -> None:
        """Process incoming price data and generate trading signals.

        Args:
            client: AsyncClient instance for order placement
            price_data: ClientPrice model with bid/ask data
        """
        # ==============================================================================
        # CALCULATE MID-MARKET PRICE
        # ==============================================================================

        # Extract best bid and ask prices
        if not price_data.bids or not price_data.asks:
            return

        bid = Decimal(str(price_data.bids[0].price))
        ask = Decimal(str(price_data.asks[0].price))
        mid_price = (bid + ask) / Decimal("2")

        self.prices.append(mid_price)

        # ==============================================================================
        # GENERATE TRADING SIGNAL
        # ==============================================================================

        # Simple moving average signal (20-period MA)
        if len(self.prices) >= 20:
            # Calculate 20-period moving average
            recent_prices = list(self.prices)[-20:]
            ma20 = sum(recent_prices, Decimal("0")) / Decimal("20")

            # Buy signal: price crosses above MA by 0.1%
            threshold = ma20 * Decimal("1.001")

            if mid_price > threshold:
                logger.info(
                    f"Buy signal: EUR/USD {mid_price:.5f} > MA {ma20:.5f} + 0.1%"
                )

                # In demo mode, log signal without placing order
                if self.demo_mode:
                    logger.info("  (Demo mode: order not placed)")
                else:
                    await self.place_buy_order(client, price_data.instrument, mid_price)

    async def place_buy_order(
        self, client: AsyncClient, instrument: InstrumentName, price: Decimal
    ) -> None:
        """Place a buy order with stop loss protection.

        Args:
            client: AsyncClient instance for order placement
            instrument: Instrument to trade
            price: Current mid-market price for stop loss calculation
        """
        try:
            # ==============================================================================
            # SDK METHOD: client.orders.post_market_order()
            # ==============================================================================
            #
            # Place a market order with stop-loss protection
            #
            # Parameters:
            #   - account_id: Your OANDA account ID
            #   - instrument: Currency pair to trade (InstrumentName enum)
            #   - units: Position size (positive=buy, negative=sell)
            #   - stop_loss: Stop loss price (Decimal)
            #
            # Returns: OrderResponse TypedDict with trade execution details
            #
            # NOTE: Stop loss is attached automatically when order fills

            # Calculate stop loss 50 pips below entry
            stop_loss_price = price - Decimal("0.0050")

            order_response = await client.orders.post_market_order(
                account_id=client.account_id,
                instrument=instrument,
                units=1000,
                stop_loss=stop_loss_price,
            )

            # Extract transaction ID from response
            fill_tx = order_response["orderFillTransaction"]
            logger.info(f"Buy order placed: {fill_tx.id}")
            logger.info(f"  Entry: {price:.5f}")
            logger.info(f"  Stop Loss: {stop_loss_price:.5f}")

        except Exception as e:
            logger.error(f"Order placement failed: {e}", exc_info=True)

    async def process_transaction(self, transaction: object) -> None:
        """Process transaction updates and track positions.

        Args:
            transaction: Transaction union model from stream
        """
        # Safe attribute access for union types
        tx_type = getattr(transaction, "type", None)
        tx_id = getattr(transaction, "id", "unknown")

        if tx_type == "ORDER_FILL":
            # ==============================================================================
            # UPDATE POSITION TRACKING
            # ==============================================================================

            instrument = getattr(transaction, "instrument", "UNKNOWN")
            units_decimal = getattr(transaction, "units", Decimal("0"))
            units = int(units_decimal)

            if instrument not in self.positions:
                self.positions[instrument] = 0

            self.positions[instrument] += units

            logger.info(f"Order filled: {tx_id}")
            logger.info(
                f"  Position: {instrument} = {self.positions[instrument]} units"
            )


async def main() -> None:
    """Execute production-ready streaming trading system."""

    # ==============================================================================
    # START TRADING SYSTEM
    # ==============================================================================

    logger.info("=" * 60)
    logger.info("PRODUCTION-READY STREAMING TRADING SYSTEM")
    logger.info("=" * 60)

    system = StreamingTradingSystem()
    await system.run()

    logger.info("System shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
```

## Key Takeaways

1. **Use async/await** - Essential for efficient streaming data handling
2. **Implement reconnection logic** - Streams can disconnect, plan for recovery
3. **Monitor stream health** - Detect stalls and connection issues
4. **Handle errors gracefully** - Don't let processing errors stop the stream
5. **Use proper logging** - Essential for debugging production systems
6. **Test thoroughly** - Start with practice environment, validate with live data

## Next Steps

- Review [Best Practices](../guides/understanding/best-practices.md) for production deployment
- Explore [Advanced Order Types](advanced-orders/index.md) for sophisticated strategies
- Check [Performance Optimization](../guides/optimization/index.md) for performance tuning

FiveTwenty provides robust streaming capabilities for real-time trading applications - focus on building reliable, maintainable systems that handle the inherent challenges of live market data.