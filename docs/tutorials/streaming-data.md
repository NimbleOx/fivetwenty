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
Real-time bid/ask prices for instruments:

<!-- fragment: Demo comprehensive basic price streaming with detailed educational explanations -->
```python
from dotenv import load_dotenv
from typing import Any
from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice


async def demonstrate_comprehensive_basic_price_streaming() -> None:
    """Demonstrate comprehensive basic price streaming with detailed educational explanations."""
    print(f"Data Comprehensive Basic Price Streaming Tutorial")

    # Step 1: Environment configuration for streaming setup
    # Environment variables provide secure credential management
    print(f"\nConfig Environment Configuration:")
    print(f"   Folder Loading from .env file for secure credential management")
    print(f"   Lock Keeps sensitive tokens out of source code")
    print(f"   World Supports multiple environments (practice/live)")

    # Load environment variables from .env file
    load_dotenv()
    print(f"   Success Environment variables loaded successfully")

    # Step 2: Initialize AsyncClient for streaming operations
    # AsyncClient provides optimal performance for real-time data streaming
    print(f"\nStarting AsyncClient Initialization:")
    print(f"   Lightning Async architecture: Non-blocking I/O for optimal performance")
    print(f"   Link Persistent connections: Efficient streaming connections")
    print(f"   Processing Auto-reconnection: Built-in connection resilience")
    print(f"   Satellite Real-time data: Live market price updates")

    async with AsyncClient() as client:
        # Zero-config client automatically uses environment variables
        print(f"   Success Client initialized with zero-config setup")
        print(f"   Bank Account ID: {client.account_id}")
        print(f"   World Environment: {client.config.environment.value}")

        # Step 3: Configure streaming parameters for educational demonstration
        # Multiple instruments demonstrate real-world streaming scenarios
        streaming_instruments = ["EUR_USD", "GBP_USD"]
        print(f"\nAnalysis Streaming Configuration:")
        print(f"   Target Instruments: {', '.join(streaming_instruments)}")
        print(f"   Exchange EUR_USD: Most liquid major pair (tight spreads)")
        print(f"   Pound GBP_USD: Volatile major pair (good for demonstration)")
        print(f"   Data Data type: Real-time bid/ask prices with spreads")
        print(f"   Time Frequency: Live updates as market moves")

        # Step 4: Initialize streaming statistics for educational analysis
        # Tracking helps understand streaming performance and behavior
        streaming_stats = {
            "total_updates": 0,
            "eur_usd_updates": 0,
            "gbp_usd_updates": 0,
            "heartbeats_received": 0,
            "avg_spread_eur_usd": [],
            "avg_spread_gbp_usd": []
        }

        print(f"\nData Starting Real-Time Price Streaming...")
        print(f"   Processing Streaming mode: Continuous real-time updates")
        print(f"   Satellite Connection: Persistent HTTP streaming")
        print(f"   Lightning Processing: Asynchronous price handling")

        try:
            # Step 5: Enter price streaming loop with comprehensive processing
            # async for provides efficient iteration over streaming price data
            async for price_data in client.pricing.get_pricing_stream(
                account_id=client.account_id,
                instruments=streaming_instruments
            ):
                # Step 6: Process different message types from the stream
                # OANDA sends both price updates and heartbeat messages
                if hasattr(price_data, 'type'):
                    if price_data.type == "PRICE":
                        # Real price update processing
                        streaming_stats["total_updates"] += 1

                        # Extract bid and ask prices for analysis
                        bid_price = price_data.bids[0].price if price_data.bids else "N/A"
                        ask_price = price_data.asks[0].price if price_data.asks else "N/A"

                        # Calculate spread for market quality analysis
                        if price_data.bids and price_data.asks:
                            spread = ask_price - bid_price
                            spread_pips = spread * (10000 if "JPY" not in price_data.instrument else 100)

                            # Track spreads by instrument for educational analysis
                            if price_data.instrument == "EUR_USD":
                                streaming_stats["eur_usd_updates"] += 1
                                streaming_stats["avg_spread_eur_usd"].append(spread_pips)
                            elif price_data.instrument == "GBP_USD":
                                streaming_stats["gbp_usd_updates"] += 1
                                streaming_stats["avg_spread_gbp_usd"].append(spread_pips)

                            print(f"   Analysis {price_data.instrument}: {bid_price} / {ask_price} (spread: {spread_pips:.1f} pips)")
                        else:
                            print(f"   Analysis {price_data.instrument}: {bid_price} / {ask_price}")

                        # Process price data with educational context
                        await process_comprehensive_price_update(price_data, streaming_stats)

                    elif price_data.type == "HEARTBEAT":
                        # Heartbeat message for connection health monitoring
                        streaming_stats["heartbeats_received"] += 1
                        if streaming_stats["heartbeats_received"] % 10 == 0:
                            print(f"   Heart Connection healthy - heartbeat #{streaming_stats['heartbeats_received']}")

                # Step 7: Educational demonstration limit (prevent infinite streaming)
                if streaming_stats["total_updates"] >= 20:  # Stop after 20 updates for tutorial
                    print(f"\nRed Tutorial limit reached - stopping demonstration")
                    break

        except KeyboardInterrupt:
            print(f"\nStop Streaming stopped by user")
        except Exception as streaming_error:
            print(f"\nError Streaming error: {streaming_error}")
            print(f"Note This is normal - streaming connections can have temporary issues")

        # Step 8: Display comprehensive streaming statistics
        print(f"\nData Streaming Session Statistics:")
        print(f"   Analysis Total price updates: {streaming_stats['total_updates']}")
        print(f"   Exchange EUR_USD updates: {streaming_stats['eur_usd_updates']}")
        print(f"   Pound GBP_USD updates: {streaming_stats['gbp_usd_updates']}")
        print(f"   Heart Heartbeats: {streaming_stats['heartbeats_received']}")

        # Calculate average spreads for educational analysis
        if streaming_stats["avg_spread_eur_usd"]:
            avg_eur_spread = sum(streaming_stats["avg_spread_eur_usd"]) / len(streaming_stats["avg_spread_eur_usd"])
            print(f"   Data EUR_USD avg spread: {avg_eur_spread:.1f} pips")

        if streaming_stats["avg_spread_gbp_usd"]:
            avg_gbp_spread = sum(streaming_stats["avg_spread_gbp_usd"]) / len(streaming_stats["avg_spread_gbp_usd"])
            print(f"   Data GBP_USD avg spread: {avg_gbp_spread:.1f} pips")

        print(f"\nEducation Key Learning Points:")
        print(f"   Lightning Async streaming provides real-time market data")
        print(f"   Data Price updates include bid/ask/spread information")
        print(f"   Heart Heartbeats ensure connection health monitoring")
        print(f"   Processing Streaming handles multiple instruments simultaneously")
        print(f"   Analysis Market data quality varies by instrument and time")


async def process_comprehensive_price_update(price: ClientPrice, stats: dict) -> None:
    """Process incoming price data with comprehensive educational context."""
    # Step 9: Educational price processing with market context
    # This function demonstrates how to extract value from streaming price data

    # Extract price components for analysis
    instrument = price.instrument
    timestamp = price.time
    bid_price = price.bids[0].price if price.bids else None
    ask_price = price.asks[0].price if price.asks else None

    # Calculate mid price for strategy development
    if bid_price and ask_price:
        mid_price = (bid_price + ask_price) / 2
        spread = ask_price - bid_price

        # Educational market analysis
        # In real applications, this would trigger:
        # - Technical indicator calculations
        # - Trading signal generation
        # - Risk management checks
        # - Position management updates
        # - Market monitoring alerts

        # For tutorial purposes, demonstrate basic analysis
        update_number = stats["total_updates"]
        if update_number % 5 == 0:  # Log every 5th update for education
            print(f"      Search Analysis #{update_number}:")
            print(f"         Balance Mid price: {mid_price:.5f}")
            print(f"         Ruler Spread: {spread:.5f} ({spread*10000:.1f} pips)")
            print(f"         Time Timestamp: {timestamp}")
            print(f"         Target Use case: Signal generation, risk management, analysis")


# Educational demonstration execution
print(f"Data Starting Comprehensive Basic Price Streaming Tutorial")
try:
    import asyncio
    asyncio.run(demonstrate_comprehensive_basic_price_streaming())
except Exception as e:
    print(f"Error Tutorial error: {e}")
    print(f"Note Check environment configuration and network connectivity")
print(f"Success Basic price streaming tutorial complete")
print(f"Education Next: Explore connection management and error handling patterns")
```

### Account Streams
Monitor account changes and trade updates:

<!-- fragment: Demo comprehensive account transaction streaming with detailed monitoring -->
```python
from dotenv import load_dotenv
from typing import Dict, Any
from decimal import Decimal
from fivetwenty import AsyncClient


async def demonstrate_comprehensive_account_transaction_streaming() -> None:
    """Demonstrate comprehensive account transaction streaming with detailed monitoring."""
    print(f"Bank Comprehensive Account Transaction Streaming Tutorial")

    # Step 1: Environment setup for transaction streaming
    # Transaction streams monitor account state changes in real-time
    print(f"\nConfig Transaction Streaming Setup:")
    print(f"   Folder Environment configuration: Secure credential loading")
    print(f"   Bank Stream type: Account transaction monitoring")
    print(f"   Data Data scope: Order fills, account changes, position updates")
    print(f"   Lightning Processing: Real-time transaction event handling")

    # Load environment variables from .env file
    load_dotenv()
    print(f"   Success Environment loaded - ready for transaction monitoring")

    # Step 2: Initialize comprehensive transaction tracking
    # Tracking helps understand account activity and trading patterns
    transaction_tracker = {
        "total_transactions": 0,
        "order_fills": 0,
        "market_orders": 0,
        "limit_orders": 0,
        "stop_orders": 0,
        "account_changes": 0,
        "position_updates": 0,
        "transaction_types": {},
        "instruments_traded": set(),
        "total_volume": Decimal("0"),
        "realized_pl": Decimal("0")
    }

    print(f"\nData Transaction Tracking Initialized:")
    print(f"   Analysis Monitoring: All account transaction types")
    print(f"   Target Focus: Order fills, account changes, position updates")
    print(f"   List Metrics: Volume, P/L, instruments, transaction patterns")

    # Step 3: Initialize AsyncClient for transaction streaming
    async with AsyncClient() as client:
        print(f"\nStarting Transaction Stream Client Ready:")
        print(f"   Bank Account: {client.account_id}")
        print(f"   World Environment: {client.config.environment.value}")
        print(f"   Processing Stream type: Real-time transaction events")
        print(f"   Lightning Architecture: Async transaction processing")

        print(f"\nSatellite Starting Real-Time Transaction Monitoring...")
        print(f"   Processing Listening for: Order fills, account changes, position updates")
        print(f"   Time Frequency: Immediate notification on account activity")
        print(f"   Data Processing: Comprehensive transaction analysis")

        try:
            # Step 4: Enter transaction streaming loop
            # Transaction streams notify of all account state changes
            async for transaction in client.transactions.get_transactions_stream(
                account_id=client.account_id
            ):
                # Step 5: Comprehensive transaction processing and analysis
                transaction_tracker["total_transactions"] += 1

                # Extract transaction details for educational analysis
                transaction_type = transaction.type
                transaction_id = transaction.id
                transaction_time = getattr(transaction, 'time', 'N/A')

                print(f"\n Transaction #{transaction_tracker['total_transactions']}:")
                print(f"   Target Type: {transaction_type}")
                print(f"   ID ID: {transaction_id}")
                print(f"   Time Time: {transaction_time}")

                # Track transaction type frequency for pattern analysis
                if transaction_type not in transaction_tracker["transaction_types"]:
                    transaction_tracker["transaction_types"][transaction_type] = 0
                transaction_tracker["transaction_types"][transaction_type] += 1

                # Step 6: Handle different transaction types with educational context
                if transaction_type == "ORDER_FILL":
                    # Order fill: Most important transaction for trading analysis
                    transaction_tracker["order_fills"] += 1
                    print(f"   Analysis Processing ORDER_FILL transaction...")
                    await handle_comprehensive_order_fill(transaction, transaction_tracker)

                elif transaction_type == "MARKET_ORDER":
                    # Market order creation: Immediate execution order placed
                    transaction_tracker["market_orders"] += 1
                    print(f"   Starting Processing MARKET_ORDER transaction...")
                    await handle_comprehensive_market_order(transaction, transaction_tracker)

                elif transaction_type == "LIMIT_ORDER":
                    # Limit order creation: Pending order at specific price
                    transaction_tracker["limit_orders"] += 1
                    print(f"   Target Processing LIMIT_ORDER transaction...")
                    await handle_comprehensive_limit_order(transaction, transaction_tracker)

                elif transaction_type == "STOP_ORDER":
                    # Stop order: Risk management or breakout order
                    transaction_tracker["stop_orders"] += 1
                    print(f"   Stop Processing STOP_ORDER transaction...")
                    await handle_comprehensive_stop_order(transaction, transaction_tracker)

                elif transaction_type in ["DAILY_FINANCING", "MARGIN_CALL", "ACCOUNT_TRANSFER"]:
                    # Account-level changes: Important for account health monitoring
                    transaction_tracker["account_changes"] += 1
                    print(f"   Bank Processing account change transaction...")
                    await handle_comprehensive_account_change(transaction, transaction_tracker)

                else:
                    # Other transaction types: Educational logging for completeness
                    print(f"   Info Other transaction type: {transaction_type}")
                    print(f"      Notes Educational note: Monitor all types for complete picture")

                # Step 7: Display running transaction analysis
                if transaction_tracker["total_transactions"] % 5 == 0:
                    print(f"\nData Running Transaction Analysis:")
                    print(f"   Analysis Total transactions: {transaction_tracker['total_transactions']}")
                    print(f"   Target Order fills: {transaction_tracker['order_fills']}")
                    print(f"   Starting Market orders: {transaction_tracker['market_orders']}")
                    print(f"   Balance Total volume: {transaction_tracker['total_volume']}")
                    print(f"   Money Realized P/L: {transaction_tracker['realized_pl']}")

                # Educational demonstration limit
                if transaction_tracker["total_transactions"] >= 15:  # Limit for tutorial
                    print(f"\nRed Tutorial limit reached - stopping transaction monitoring")
                    break

        except KeyboardInterrupt:
            print(f"\nStop Transaction monitoring stopped by user")
        except Exception as streaming_error:
            print(f"\nError Transaction streaming error: {streaming_error}")
            print(f"Note Transaction streams may pause during low activity periods")

        # Step 8: Final transaction analysis summary
        print(f"\nData Transaction Monitoring Session Summary:")
        print(f"   Analysis Total transactions processed: {transaction_tracker['total_transactions']}")
        print(f"   Target Order fills: {transaction_tracker['order_fills']}")
        print(f"   Starting Market orders: {transaction_tracker['market_orders']}")
        print(f"   Bank Account changes: {transaction_tracker['account_changes']}")
        print(f"   Data Transaction types seen: {list(transaction_tracker['transaction_types'].keys())}")
        print(f"   Exchange Instruments traded: {len(transaction_tracker['instruments_traded'])}")

        print(f"\nEducation Transaction Streaming Key Learnings:")
        print(f"   Satellite Real-time notification of all account activity")
        print(f"   Target Order fills are most critical for trading systems")
        print(f"   Bank Account changes affect available margin and balance")
        print(f"   Data Transaction patterns reveal trading behavior")
        print(f"   Lightning Immediate processing enables rapid position management")


async def handle_comprehensive_order_fill(transaction: Any, tracker: Dict[str, Any]) -> None:
    """Handle order fill transactions with comprehensive educational analysis."""
    # Step 9: Order fill processing - most important transaction type
    print(f"      Target ORDER_FILL Analysis:")

    # Extract fill details for educational analysis
    if hasattr(transaction, 'instrument'):
        instrument = transaction.instrument
        tracker["instruments_traded"].add(instrument)
        print(f"         Exchange Instrument: {instrument}")

    if hasattr(transaction, 'units'):
        units = abs(int(transaction.units))
        tracker["total_volume"] += Decimal(str(units))
        print(f"         Data Units filled: {units:,}")

    if hasattr(transaction, 'price'):
        fill_price = transaction.price
        print(f"         Balance Fill price: {fill_price}")

    if hasattr(transaction, 'pl'):
        realized_pl = Decimal(str(transaction.pl))
        tracker["realized_pl"] += realized_pl
        print(f"         Money Realized P/L: {realized_pl}")

    print(f"         Education Educational note: Order fills update positions and realize P/L")


async def handle_comprehensive_market_order(transaction: Any, tracker: Dict[str, Any]) -> None:
    """Handle market order transactions with educational context."""
    # Step 10: Market order processing for immediate execution orders
    print(f"      Starting MARKET_ORDER Analysis:")

    if hasattr(transaction, 'instrument'):
        print(f"         Exchange Instrument: {transaction.instrument}")

    if hasattr(transaction, 'units'):
        units = transaction.units
        direction = "BUY" if int(units) > 0 else "SELL"
        print(f"         Analysis Direction: {direction} {abs(int(units)):,} units")

    print(f"         Education Educational note: Market orders execute immediately at best available price")


async def handle_comprehensive_limit_order(transaction: Any, tracker: Dict[str, Any]) -> None:
    """Handle limit order transactions with educational context."""
    # Step 11: Limit order processing for pending orders
    print(f"      Target LIMIT_ORDER Analysis:")

    if hasattr(transaction, 'instrument'):
        print(f"         Exchange Instrument: {transaction.instrument}")

    if hasattr(transaction, 'price'):
        print(f"         Balance Limit price: {transaction.price}")

    print(f"         Education Educational note: Limit orders wait for specific price levels")


async def handle_comprehensive_stop_order(transaction: Any, tracker: Dict[str, Any]) -> None:
    """Handle stop order transactions with educational context."""
    # Step 12: Stop order processing for risk management
    print(f"      Stop STOP_ORDER Analysis:")

    if hasattr(transaction, 'instrument'):
        print(f"         Exchange Instrument: {transaction.instrument}")

    if hasattr(transaction, 'price'):
        print(f"         Balance Stop price: {transaction.price}")

    print(f"         Education Educational note: Stop orders provide risk management and breakout trading")


async def handle_comprehensive_account_change(transaction: Any, tracker: Dict[str, Any]) -> None:
    """Handle account-level change transactions with educational context."""
    # Step 13: Account change processing for account health monitoring
    print(f"      Bank ACCOUNT_CHANGE Analysis:")
    print(f"         Data Type: {transaction.type}")
    print(f"         Education Educational note: Account changes affect margin and balance")


# Educational demonstration execution
print(f"Bank Starting Comprehensive Account Transaction Streaming Tutorial")
try:
    import asyncio
    asyncio.run(demonstrate_comprehensive_account_transaction_streaming())
except Exception as e:
    print(f"Error Tutorial error: {e}")
    print(f"Note Transaction streams require active trading to generate events")
print(f"Success Account transaction streaming tutorial complete")
print(f"Education Next: Learn about automated trading with streaming data integration")
```

## Connection Management

### Basic Stream with Error Handling

<!-- fragment: Demo advanced streaming with comprehensive connection management and resilience -->
```python
import asyncio
import time
from typing import Optional, Dict, Any
from decimal import Decimal
from dotenv import load_dotenv

from fivetwenty import AsyncClient
from fivetwenty.exceptions import StreamStall
from fivetwenty.models import ClientPrice


class AdvancedStreamingManager:
    """Advanced streaming manager with comprehensive connection management and resilience."""

    def __init__(self, max_retries: int = 5, base_delay: float = 1.0) -> None:
        """Initialize advanced streaming manager with resilience parameters."""
        # Step 1: Initialize streaming resilience parameters
        # These parameters control how the system handles connection issues
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.retry_count = 0
        self.last_successful_data = time.time()
        self.connection_start_time = None
        self.total_reconnections = 0

        print(f"Config Advanced Streaming Manager Initialized:")
        print(f"   Processing Max retries: {max_retries}")
        print(f"   Time Base delay: {base_delay} seconds")
        print(f"   Security Resilience: Exponential backoff with connection monitoring")

        # Step 2: Initialize comprehensive streaming statistics
        # Statistics help monitor streaming health and performance
        self.streaming_stats = {
            "total_messages": 0,
            "price_updates": 0,
            "heartbeats": 0,
            "connection_uptime": 0,
            "reconnection_count": 0,
            "stall_events": 0,
            "error_events": 0,
            "data_gaps": 0,
            "avg_message_interval": [],
            "last_message_time": None
        }

    async def demonstrate_robust_streaming_with_resilience(self) -> None:
        """Demonstrate robust streaming with comprehensive resilience and error handling."""
        print(f"\nSecurity Advanced Robust Streaming Demonstration")

        # Step 3: Environment setup for resilient streaming
        print(f"\nConfig Resilient Streaming Configuration:")
        print(f"   Folder Environment: Secure credential management")
        print(f"   Security Resilience: Advanced error handling and recovery")
        print(f"   Data Monitoring: Comprehensive streaming health tracking")
        print(f"   Processing Recovery: Automatic reconnection with intelligent backoff")

        # Load environment variables from .env file
        load_dotenv()
        print(f"   Success Environment configured for resilient streaming")

        # Step 4: Initialize streaming session
        session_start_time = time.time()
        self.connection_start_time = session_start_time

        print(f"\nStarting Starting Resilient Streaming Session:")
        print(f"   Time Session start: {time.strftime('%H:%M:%S', time.localtime(session_start_time))}")
        print(f"   Target Target: EUR_USD price stream with resilience")
        print(f"   Processing Max retries: {self.max_retries}")
        print(f"   Lightning Architecture: Async with connection health monitoring")

        # Step 5: Resilient streaming loop with comprehensive error handling
        async with AsyncClient() as client:
            print(f"   Bank Account: {client.account_id}")
            print(f"   World Environment: {client.config.environment.value}")

            while self.retry_count < self.max_retries:
                try:
                    print(f"\nSatellite Establishing Streaming Connection (Attempt {self.retry_count + 1}/{self.max_retries})...")
                    connection_attempt_time = time.time()

                    # Step 6: Enter price streaming with comprehensive monitoring
                    async for price_data in client.pricing.get_pricing_stream(
                        account_id=client.account_id,
                        instruments=["EUR_USD"]
                    ):
                        # Step 7: Successful data reception - reset retry logic
                        if self.retry_count > 0:
                            print(f"   Success Connection restored after {self.retry_count} retries")
                            self.total_reconnections += 1
                            self.streaming_stats["reconnection_count"] += 1

                        self.retry_count = 0  # Reset on successful data
                        self.last_successful_data = time.time()

                        # Update connection uptime
                        self.streaming_stats["connection_uptime"] = time.time() - connection_attempt_time

                        # Step 8: Process streaming data with comprehensive analysis
                        await self.process_advanced_price_update(price_data)

                        # Educational demonstration limit
                        if self.streaming_stats["price_updates"] >= 15:
                            print(f"\nRed Tutorial limit reached - ending resilient streaming demo")
                            await self.display_streaming_health_report()
                            return

                except StreamStall as stall_error:
                    # Step 9: Handle stream stall with intelligent recovery
                    self.retry_count += 1
                    self.streaming_stats["stall_events"] += 1

                    print(f"\n⚠️ Stream Stall Detected:")
                    print(f"   Processing Retry attempt: {self.retry_count}/{self.max_retries}")
                    print(f"   Time Time since last data: {time.time() - self.last_successful_data:.1f} seconds")
                    print(f"   Security Recovery strategy: Exponential backoff")

                    if self.retry_count >= self.max_retries:
                        print(f"\nError Maximum retries ({self.max_retries}) exceeded")
                        print(f"Note Extended outage detected - may require manual intervention")
                        raise stall_error

                    # Step 10: Intelligent exponential backoff
                    backoff_delay = self.base_delay * (2 ** (self.retry_count - 1))
                    backoff_delay = min(backoff_delay, 60)  # Cap at 60 seconds

                    print(f"   Wait Waiting {backoff_delay:.1f} seconds before retry...")
                    print(f"   🔬 Backoff strategy: {self.base_delay} * 2^{self.retry_count-1} = {backoff_delay:.1f}s")
                    await asyncio.sleep(backoff_delay)

                    print(f"   Processing Attempting reconnection...")

                except Exception as unexpected_error:
                    # Step 11: Handle unexpected streaming errors
                    self.retry_count += 1
                    self.streaming_stats["error_events"] += 1

                    print(f"\nError Unexpected Streaming Error:")
                    print(f"   Search Error type: {type(unexpected_error).__name__}")
                    print(f"   Notes Error details: {str(unexpected_error)}")
                    print(f"   Processing Retry attempt: {self.retry_count}/{self.max_retries}")

                    if self.retry_count >= self.max_retries:
                        print(f"\nStop Maximum retries exceeded for unexpected error")
                        print(f"Note Check network connectivity and API status")
                        raise unexpected_error

                    # Shorter delay for unexpected errors
                    error_delay = min(5.0, self.base_delay * self.retry_count)
                    print(f"   Wait Waiting {error_delay:.1f} seconds before retry...")
                    await asyncio.sleep(error_delay)

            # Step 12: Maximum retries exceeded
            print(f"\nStop Resilient Streaming Failed:")
            print(f"   Error All retry attempts ({self.max_retries}) exhausted")
            print(f"   Time Total session time: {time.time() - session_start_time:.1f} seconds")
            print(f"   Data Final statistics: {self.streaming_stats}")

    async def process_advanced_price_update(self, price: ClientPrice) -> None:
        """Process price updates with advanced monitoring and analysis."""
        # Step 13: Advanced price processing with comprehensive monitoring
        current_time = time.time()
        self.streaming_stats["total_messages"] += 1

        if hasattr(price, 'type'):
            if price.type == "PRICE":
                self.streaming_stats["price_updates"] += 1

                # Calculate message intervals for performance monitoring
                if self.streaming_stats["last_message_time"]:
                    interval = current_time - self.streaming_stats["last_message_time"]
                    self.streaming_stats["avg_message_interval"].append(interval)

                self.streaming_stats["last_message_time"] = current_time

                # Extract price data for educational analysis
                bid_price = price.bids[0].price if price.bids else "N/A"
                ask_price = price.asks[0].price if price.asks else "N/A"

                update_number = self.streaming_stats["price_updates"]
                print(f"   Analysis Price Update #{update_number}: {bid_price}/{ask_price}")

                # Advanced monitoring every 5 updates
                if update_number % 5 == 0:
                    await self.display_advanced_streaming_metrics()

            elif price.type == "HEARTBEAT":
                self.streaming_stats["heartbeats"] += 1
                heartbeat_count = self.streaming_stats["heartbeats"]

                if heartbeat_count % 3 == 0:
                    print(f"   Heart Heartbeat #{heartbeat_count} - Connection healthy")

    async def display_advanced_streaming_metrics(self) -> None:
        """Display advanced streaming performance metrics."""
        # Step 14: Comprehensive streaming performance analysis
        print(f"\nData Advanced Streaming Metrics:")

        # Calculate average message interval
        if self.streaming_stats["avg_message_interval"]:
            avg_interval = sum(self.streaming_stats["avg_message_interval"]) / len(self.streaming_stats["avg_message_interval"])
            print(f"   Lightning Avg message interval: {avg_interval:.2f} seconds")
            print(f"   Analysis Message frequency: {1/avg_interval:.1f} messages/second")

        # Connection health metrics
        uptime = time.time() - self.connection_start_time if self.connection_start_time else 0
        print(f"   Time Connection uptime: {uptime:.1f} seconds")
        print(f"   Processing Reconnections: {self.streaming_stats['reconnection_count']}")
        print(f"   ⚠️ Stall events: {self.streaming_stats['stall_events']}")
        print(f"   Error Error events: {self.streaming_stats['error_events']}")

        # Data quality metrics
        total_messages = self.streaming_stats["total_messages"]
        heartbeat_ratio = (self.streaming_stats["heartbeats"] / total_messages * 100) if total_messages > 0 else 0
        print(f"   Heart Heartbeat ratio: {heartbeat_ratio:.1f}%")

    async def display_streaming_health_report(self) -> None:
        """Display comprehensive streaming health report."""
        # Step 15: Final streaming health and performance report
        print(f"\nList Streaming Health Report:")
        print(f"   Data Total messages: {self.streaming_stats['total_messages']}")
        print(f"   Analysis Price updates: {self.streaming_stats['price_updates']}")
        print(f"   Heart Heartbeats: {self.streaming_stats['heartbeats']}")
        print(f"   Processing Reconnections: {self.streaming_stats['reconnection_count']}")
        print(f"   ⚠️ Stall events: {self.streaming_stats['stall_events']}")
        print(f"   Error Error events: {self.streaming_stats['error_events']}")

        # Health assessment
        if self.streaming_stats["error_events"] == 0 and self.streaming_stats["stall_events"] == 0:
            health_status = "EXCELLENT"
        elif self.streaming_stats["error_events"] + self.streaming_stats["stall_events"] <= 2:
            health_status = "GOOD"
        else:
            health_status = "NEEDS_ATTENTION"

        print(f"   Target Overall health: {health_status}")


# Advanced streaming demonstration
async def demonstrate_advanced_streaming_resilience() -> None:
    """Demonstrate advanced streaming with comprehensive resilience features."""
    print(f"Security Advanced Streaming Resilience Tutorial")

    # Initialize advanced streaming manager
    streaming_manager = AdvancedStreamingManager(max_retries=3, base_delay=2.0)

    try:
        await streaming_manager.demonstrate_robust_streaming_with_resilience()
    except Exception as demo_error:
        print(f"\nError Advanced streaming demo error: {demo_error}")
        print(f"Note This demonstrates how resilient systems handle various failure modes")
        await streaming_manager.display_streaming_health_report()


# Educational demonstration execution
print(f"Security Starting Advanced Streaming Resilience Tutorial")
try:
    import asyncio
    asyncio.run(demonstrate_advanced_streaming_resilience())
except Exception as e:
    print(f"Error Tutorial error: {e}")
    print(f"Note Advanced streaming requires robust error handling for production use")
print(f"Success Advanced streaming resilience tutorial complete")
print(f"Education Next: Learn about stream monitoring and health detection")
```

### Stream Monitoring

Monitor stream health and implement reconnection logic:

<!-- fragment: Demo latency measurement streaming -->
```python
import time

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

async def process_price_update(price):
    """Process incoming price data."""
    pass

class StreamMonitor:
    def __init__(self, stall_timeout: float = 30.0):
        self.stall_timeout = stall_timeout
        self.last_heartbeat = time.time()

    def on_data_received(self):
        """Call when data is received."""
        self.last_heartbeat = time.time()

    def is_stalled(self) -> bool:
        """Check if stream appears stalled."""
        return (time.time() - self.last_heartbeat) > self.stall_timeout

async def monitored_stream():
    monitor = StreamMonitor(stall_timeout=30.0)

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        ):
            monitor.on_data_received()

            if monitor.is_stalled():
                print("Stream appears stalled, reconnecting...")
                break

            await process_price_update(price)
```

## Automated Trading with Streaming Data

### Signal Generation from Price Streams

<!-- fragment: Demo price analysis with deque and Decimal types -->
```python
from collections import deque
from decimal import Decimal

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

class MovingAverageSignal:
    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self.prices = deque(maxlen=window_size)

    def add_price(self, price: Decimal) -> Decimal | None:
        """Add price and return moving average if window is full."""
        self.prices.append(price)

        if len(self.prices) == self.window_size:
            return sum(self.prices) / len(self.prices)
        return None

async def automated_trading_system():
    signal = MovingAverageSignal(window_size=10)

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        async for price in client.pricing.get_pricing_stream(
            account_id=client.account_id,
            instruments=["EUR_USD"]
        ):
            # Calculate signal
            mid_price = (Decimal(price.bids[0].price) + Decimal(price.asks[0].price)) / 2
            ma = signal.add_price(mid_price)

            if ma and mid_price > ma * Decimal("1.001"):  # Price 0.1% above MA
                # Buy signal
                await client.orders.post_market_order(
                    account_id=client.account_id,
                    instrument="EUR_USD",
                    units=1000,
                    stop_loss_on_fill={
                        "price": str(mid_price - Decimal("0.0050")),
                        "time_in_force": "GTC"
                    }
                )
                print(f"Buy signal executed at {mid_price}")
```

### Order Management with Real-time Updates

<!-- fragment: Demo position monitoring with async task coordination -->
```python
import asyncio

from dotenv import load_dotenv

from fivetwenty import AsyncClient

# Load environment variables from .env file
load_dotenv()

class PositionManager:
    def __init__(self):
        self.open_positions = {}
        self.pending_orders = {}

    async def handle_transaction(self, transaction):
        """Handle incoming transaction stream data."""
        if transaction.type == "ORDER_FILL":
            await self.update_position(transaction)
        elif transaction.type == "ORDER_CREATE":
            self.pending_orders[transaction.order_id] = transaction
        elif transaction.type == "ORDER_CANCEL":
            self.pending_orders.pop(transaction.order_id, None)

    async def update_position(self, fill_transaction):
        """Update position tracking on fill."""
        instrument = fill_transaction.instrument
        units = int(fill_transaction.units)

        if instrument not in self.open_positions:
            self.open_positions[instrument] = 0

        self.open_positions[instrument] += units
        print(f"Position updated: {instrument} = {self.open_positions[instrument]}")

async def managed_trading_system():
    position_manager = PositionManager()

    # Zero-config - automatically uses environment variables
    async with AsyncClient() as client:
        # Monitor both prices and transactions
        price_task = asyncio.create_task(monitor_prices(client, position_manager))
        transaction_task = asyncio.create_task(monitor_transactions(client, position_manager))

        await asyncio.gather(price_task, transaction_task)

async def monitor_prices(client, position_manager):
    """Monitor price streams."""
    async for price in client.pricing.get_pricing_stream(
        account_id=client.account_id,
        instruments=["EUR_USD"]
    ):
        # Price-based logic here
        pass

async def monitor_transactions(client, position_manager):
    """Monitor transaction streams."""
    async for transaction in client.transactions.get_transactions_stream(
        account_id=client.account_id
    ):
        await position_manager.handle_transaction(transaction)
```


## Complete Example

Here's a complete streaming trading system:

<!-- fragment: Demo production-ready streaming system with logging -->
```python
import asyncio
import logging
import os
from collections import deque
from decimal import Decimal

from fivetwenty import AsyncClient, Environment
from fivetwenty.exceptions import StreamStall

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingTradingSystem:
    def __init__(self, token: str, account_id: str):
        self.token = token
        self.account_id = account_id
        self.prices = deque(maxlen=100)  # Keep last 100 prices
        self.positions = {}

    async def run(self):
        """Main trading system loop."""
        while True:
            try:
                async with AsyncClient(
                    token=self.token,
                    environment=Environment.PRACTICE
                ) as client:
                    logger.info("Starting streaming trading system")

                    # Create concurrent tasks for price and transaction monitoring
                    tasks = [
                        asyncio.create_task(self.monitor_prices(client)),
                        asyncio.create_task(self.monitor_transactions(client))
                    ]

                    await asyncio.gather(*tasks)

            except StreamStall:
                logger.warning("Stream stalled, reconnecting in 5 seconds...")
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"System error: {e}")
                await asyncio.sleep(10)

    async def monitor_prices(self, client):
        """Monitor price streams and generate trading signals."""
        async for price in client.pricing.get_pricing_stream(
            account_id=self.account_id,
            instruments=["EUR_USD"]
        ):
            try:
                await self.process_price(client, price)
            except Exception as e:
                logger.error(f"Price processing error: {e}")

    async def monitor_transactions(self, client):
        """Monitor transaction streams for position updates."""
        async for transaction in client.transactions.get_transactions_stream(
            account_id=self.account_id
        ):
            try:
                await self.process_transaction(transaction)
            except Exception as e:
                logger.error(f"Transaction processing error: {e}")

    async def process_price(self, client, price):
        """Process incoming price data and generate signals."""
        mid_price = (Decimal(price.bids[0].price) + Decimal(price.asks[0].price)) / 2
        self.prices.append(mid_price)

        # Simple moving average signal
        if len(self.prices) >= 20:
            ma20 = sum(list(self.prices)[-20:]) / 20

            # Buy signal: price crosses above MA
            if mid_price > ma20 * Decimal("1.001"):
                await self.place_buy_order(client, price.instrument, mid_price)

    async def place_buy_order(self, client, instrument: str, price: Decimal):
        """Place a buy order with stop loss."""
        try:
            order = await client.orders.post_market_order(
                account_id=self.account_id,
                instrument=instrument,
                units=1000,
                stop_loss_on_fill={
                    "price": str(price - Decimal("0.0050")),
                    "time_in_force": "GTC"
                }
            )
            logger.info(f"Buy order placed: {order.order_fill_transaction.id}")
        except Exception as e:
            logger.error(f"Order placement failed: {e}")

    async def process_transaction(self, transaction):
        """Process transaction updates."""
        if transaction.type == "ORDER_FILL":
            logger.info(f"Order filled: {transaction.id}")
            # Update position tracking

# Run the system
async def main():
    token = os.getenv("OANDA_TOKEN")
    account_id = "101-001-0000000-001"

    system = StreamingTradingSystem(token, account_id)
    await system.run()

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