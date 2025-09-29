# Order Strategies & Combinations

Learn to combine FiveTwenty's order types effectively for common trading scenarios.

## Learning Objectives

By the end of this tutorial, you will:

- Scale into and out of positions using multiple order layers
- Implement advanced stop management techniques
- Build conditional order logic and position reversal strategies
- Combine multiple order types for complete trading strategies


## Multiple Position Management

### Scaling Into Positions

Build positions with multiple entries:

<!-- fragment: Demo scaling into positions with argument type mismatches and call argument issues -->
```python
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scale_into_position():
    """Demonstrate scaling into positions using multiple entry points for reduced average cost."""

    # Step 1: Initialize client using environment-based authentication
    # Zero-config approach reads OANDA credentials from environment variables
    async with AsyncClient() as client:
        orders = []  # Track all scaling orders for management

        # Step 2: Place first entry order at conservative level
        # First entry uses smaller size to test market direction
        order1 = await client.orders.post_limit_order(
            account_id=client.account_id,     # Account for order execution
            instrument="EUR_USD",             # Major currency pair with good liquidity
            units=5000,                       # Conservative initial position size
            price=Decimal("1.0850"),          # First entry level (higher price)
            time_in_force="GTC",              # Good Till Cancelled - stays active
            stop_loss_on_fill={               # Automatic risk protection on fill
                "price": "1.0800",            # Stop loss 50 pips below entry
                "time_in_force": "GTC"        # Stop remains active until triggered
            }
        )
        orders.append(order1)
        print(f"   Analysis First entry: {order1.units} units at {order1.price}")

        # Step 3: Place second entry order at more aggressive level
        # Second entry uses larger size as confidence in direction increases
        order2 = await client.orders.post_limit_order(
            account_id=client.account_id,     # Same account for position building
            instrument="EUR_USD",             # Same instrument for cumulative position
            units=10000,                      # Larger size for better average price
            price=Decimal("1.0825"),          # Lower entry price (better value)
            time_in_force="GTC",              # Long-term active order
            stop_loss_on_fill={               # Consistent risk management
                "price": "1.0800",            # Same stop level for both entries
                "time_in_force": "GTC"        # Persistent protection
            }
        )
        orders.append(order2)
        print(f"   Analysis Second entry: {order2.units} units at {order2.price}")

        # Step 4: Provide scaling strategy summary
        total_units = 5000 + 10000  # Combined position if both fill
        average_price = ((5000 * Decimal("1.0850")) + (10000 * Decimal("1.0825"))) / total_units
        print(f"\nTarget Scaling Strategy Summary:")
        print(f"   Total Position (if both fill): {total_units} units")
        print(f"   Average Entry Price: {average_price:.5f}")
        print(f"   Risk Management: Stop loss at 1.0800 for all entries")

        return orders
```

### Scaling Out of Positions

Take partial profits at multiple levels:

<!-- fragment: Demo scaling out with return type annotations and argument type issues -->
```python
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scale_out_of_position():
    """Demonstrate scaling out of positions using multiple profit-taking levels for optimized exits."""

    # Step 1: Initialize client for profit-taking order management
    # Scaling out allows capturing profits while maintaining market exposure
    async with AsyncClient() as client:
        print(f"Target Implementing Scaling Exit Strategy:")

        # Step 2: Place first profit-taking order at conservative target
        # First exit secures partial profits at reasonable target level
        profit1 = await client.orders.post_limit_order(
            account_id=client.account_id,     # Account for profit realization
            instrument="EUR_USD",             # Same instrument as original position
            units=-5000,                      # Negative units = sell (close partial position)
            price=Decimal("1.0925"),          # First profit target (75 pips from 1.0850)
            time_in_force="GTC"               # Persistent until market reaches target
        )
        print(f"   Balance First profit target: Sell {abs(profit1.units)} units at {profit1.price}")

        # Step 3: Place second profit-taking order at extended target
        # Second exit captures additional profits if trend continues
        profit2 = await client.orders.post_limit_order(
            account_id=client.account_id,     # Same account for consistent management
            instrument="EUR_USD",             # Maintaining instrument consistency
            units=-5000,                      # Close remaining position
            price=Decimal("1.0975"),          # Extended target (125 pips from 1.0850)
            time_in_force="GTC"               # Long-term profit capture
        )
        print(f"   Balance Second profit target: Sell {abs(profit2.units)} units at {profit2.price}")

        # Step 4: Display scaling exit strategy analysis
        print(f"\nData Scaling Exit Analysis:")
        print(f"   Conservative Target: {profit1.price} (early profit protection)")
        print(f"   Extended Target: {profit2.price} (trend continuation capture)")
        print(f"   Strategy Benefit: Balances profit security with upside potential")

        return [profit1, profit2]
```

## Advanced Stop Management


### Stop Loss Modification

Update stop levels as trades move in your favor:

<!-- fragment: Demo stop loss modification with function return type annotations -->
```python
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def update_stop_loss(trade_id: str, new_stop_price: Decimal):
    """Update stop loss levels for active trades to lock in profits or adjust risk."""

    # Step 1: Initialize client for trade management operations
    # Stop loss updates enable dynamic risk management as trades develop
    async with AsyncClient() as client:
        print(f"Security Updating Stop Loss Protection:")
        print(f"   Trade ID: {trade_id}")
        print(f"   New Stop Level: {new_stop_price}")

        # Step 2: Execute stop loss modification for specified trade
        # Trade-specific updates allow individual position risk management
        response = await client.trades.put_trade_orders(
            account_id=client.account_id,     # Account containing the trade
            trade_id=trade_id,                # Specific trade to modify
            stop_loss={                       # New stop loss configuration
                "price": str(new_stop_price), # Updated trigger price
                "time_in_force": "GTC"        # Persistent until triggered
            }
        )

        # Step 3: Confirm successful stop loss update
        print(f"Success Stop loss successfully updated to: {new_stop_price}")
        print(f"Secure Trade {trade_id} now protected at new level")
        print(f"Note Use this to trail stops or tighten risk management")

        return response
```

## Order Coordination Patterns

### If-Then Order Logic

Simulate conditional orders with monitoring:

<!-- fragment: Demo conditional logic with attribute access and argument type patterns -->
```python
import asyncio
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def conditional_order_logic():
    """Implement conditional order logic using price monitoring for breakout strategies."""

    # Step 1: Initialize client for conditional order monitoring
    # Conditional logic enables automated responses to market conditions
    async with AsyncClient() as client:
        # Step 2: Define breakout condition parameters
        target_price = Decimal("1.0875")  # Breakout level to monitor
        print(f"Search Monitoring for breakout above {target_price}")
        print(f"Data Starting conditional order monitoring...")

        # Step 3: Continuous price monitoring loop
        # Real-time monitoring enables immediate response to market conditions
        while True:
            # Step 4: Retrieve current market pricing for condition evaluation
            pricing = await client.pricing.get_pricing(
                account_id=client.account_id,     # Account context for pricing
                instruments=["EUR_USD"]           # Target instrument for monitoring
            )

            # Step 5: Extract current price for condition checking
            current_price = Decimal(pricing.prices[0].mid.o)  # Mid price for fairness
            print(f"Time Current price: {current_price} (target: {target_price})")

            # Step 6: Evaluate breakout condition
            # Price crossing above target indicates potential upward momentum
            if current_price >= target_price:
                # Step 7: Execute breakout order when condition is satisfied
                print(f"Starting BREAKOUT DETECTED! Price hit {current_price}")
                order = await client.orders.post_market_order(
                    account_id=client.account_id,     # Execute on monitored account
                    instrument="EUR_USD",             # Same instrument as monitoring
                    units=10000,                      # Full position size for breakout
                    stop_loss_on_fill={               # Immediate risk protection
                        "price": "1.0825",            # Stop below breakout level
                        "time_in_force": "GTC"        # Persistent protection
                    }
                )

                print(f"Success Breakout order executed: {order.units} units")
                print(f"Security Stop loss protection active at 1.0825")
                return order

            # Step 8: Wait before next price check to avoid excessive API calls
            print(f"   Wait Condition not met, checking again in 10 seconds...")
            await asyncio.sleep(10)  # 10-second monitoring interval
```

### Position Reversal Strategy

Close existing position and open opposite position:

<!-- fragment: Demo position reversal with undefined names and missing return statements -->
```python
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def position_reversal():
    """Demonstrate position reversal strategy for trend change scenarios."""

    # Step 1: Initialize client for position reversal operations
    # Position reversal enables quick response to changing market conditions
    async with AsyncClient() as client:
        print(f"Processing Executing Position Reversal Strategy")

        # Step 2: Retrieve current positions for reversal analysis
        # Position data determines reversal size and direction
        positions = await client.positions.get_positions(account_id=client.account_id)

        # Step 3: Analyze positions for reversal opportunities
        for position in positions.positions:
            if position.instrument == "EUR_USD" and position.long.units != "0":
                # Step 4: Calculate reversal order size
                # Reversal requires closing existing position and opening opposite position
                close_size = int(position.long.units)    # Current long position size
                new_position_size = close_size * 2       # Double size for full reversal

                print(f"Data Reversal Analysis:")
                print(f"   Current Position: {close_size} units LONG")
                print(f"   Reversal Order: {new_position_size} units SHORT")
                print(f"   Net Result: {new_position_size//2} units SHORT")

                # Step 5: Execute reversal order with market order
                # Negative units close long and open short in single transaction
                order = await client.orders.post_market_order(
                    account_id=client.account_id,     # Account for reversal
                    instrument="EUR_USD",             # Same instrument as existing position
                    units=-new_position_size,         # Negative for short position
                    stop_loss_on_fill={               # Risk protection for new direction
                        "price": "1.0925",            # Stop above current price (short protection)
                        "time_in_force": "GTC"        # Persistent risk management
                    }
                )

                print(f"\nSuccess Position Reversal Executed:")
                print(f"   Closed: {close_size} units LONG")
                print(f"   Opened: {new_position_size//2} units SHORT")
                print(f"   Stop Loss: 1.0925 (protecting short position)")
                return order

        # Step 6: Handle case where no reversible positions exist
        print(f"Info No EUR_USD long positions found for reversal")
        return None
```

## Complete Strategy Example

Here's a complete breakout strategy using multiple order types:

<!-- fragment: Demo complete scaling strategy with comprehensive argument and type issues -->
```python
import asyncio
from decimal import Decimal
from dotenv import load_dotenv
from fivetwenty import AsyncClient
# Setup
# Load environment variables from .env file
load_dotenv()

async def scaling_strategy_example():
    """Complete scaling strategy demonstrating systematic entry and exit using order combinations."""

    # Step 1: Initialize client for comprehensive scaling strategy
    # Scaling strategies balance risk and opportunity through systematic position building
    async with AsyncClient() as client:
        print(f"Target COMPREHENSIVE SCALING STRATEGY")
        print(f"=" * 40)

        # Step 2: Define scaling parameters for systematic approach
        base_size = 5000  # Base unit size for scaling calculations
        entry_prices = [Decimal("1.0850"), Decimal("1.0825"), Decimal("1.0800")]  # Descending entry levels
        exit_prices = [Decimal("1.0925"), Decimal("1.0950"), Decimal("1.0975")]   # Ascending exit levels

        scaling_orders = []  # Track all orders for strategy management

        # Step 3: Implement scaling entry strategy
        print(f"\nAnalysis SCALING INTO POSITION:")
        for i, price in enumerate(entry_prices):
            # Step 4: Calculate progressive position sizing
            # Larger sizes at better prices improve average entry cost
            position_size = base_size * (i + 1)  # Increasing size: 5k, 10k, 15k
            stop_price = price - Decimal("0.0050")  # 50 pip stop for each entry

            # Step 5: Place scaling entry order with risk protection
            order = await client.orders.post_limit_order(
                account_id=client.account_id,     # Account for strategy execution
                instrument="EUR_USD",             # Major pair for reliable execution
                units=position_size,              # Progressive sizing
                price=price,                      # Entry level for this scale
                time_in_force="GTC",              # Persistent until filled
                stop_loss_on_fill={               # Automatic risk management
                    "price": str(stop_price),     # Individual stop for this entry
                    "time_in_force": "GTC"        # Persistent protection
                }
            )
            scaling_orders.append(order)
            print(f"   Entry {i+1}: {position_size:,} units at {price} (stop: {stop_price})")

        # Step 6: Calculate total potential position and average price
        total_units = sum(base_size * (i + 1) for i in range(len(entry_prices)))  # 30,000 units total
        weighted_avg = sum(entry_prices[i] * base_size * (i + 1) for i in range(len(entry_prices))) / total_units
        print(f"   Data Total Position (if all fill): {total_units:,} units")
        print(f"   Data Weighted Average Price: {weighted_avg:.5f}")

        # Step 7: Implement scaling exit strategy
        print(f"\nBalance SCALING OUT OF POSITION:")
        for i, price in enumerate(exit_prices):
            # Step 8: Place systematic profit-taking orders
            # Equal exit sizes provide balanced profit realization
            order = await client.orders.post_limit_order(
                account_id=client.account_id,     # Same account for consistency
                instrument="EUR_USD",             # Same instrument
                units=-base_size,                 # Consistent partial exit size
                price=price,                      # Progressive profit targets
                time_in_force="GTC"               # Persistent profit capture
            )
            scaling_orders.append(order)
            pips_from_avg = (price - weighted_avg) * 10000
            print(f"   Exit {i+1}: {base_size:,} units at {price} ({pips_from_avg:.0f} pips profit)")

        # Step 9: Display strategy summary and risk analysis
        print(f"\nList STRATEGY SUMMARY:")
        print(f"   Entry Orders: {len(entry_prices)} levels ({entry_prices[0]} to {entry_prices[-1]})")
        print(f"   Exit Orders: {len(exit_prices)} levels ({exit_prices[0]} to {exit_prices[-1]})")
        print(f"   Risk Management: 50-pip stops on all entries")
        print(f"   Total Orders: {len(scaling_orders)} orders placed")
        print(f"   Strategy Type: Systematic scaling with progressive sizing")

        return scaling_orders

# Step 10: Execute the comprehensive scaling strategy demonstration
if __name__ == "__main__":
    print(f"Starting Starting comprehensive scaling strategy demonstration...")
    asyncio.run(scaling_strategy_example())
    print(f"Success Scaling strategy demonstration completed")
```

## Key Takeaways

1. **Use OANDA's built-in combinations** - `stop_loss_on_fill` and `take_profit_on_fill`
2. **Keep strategies simple** - Focus on proven order type combinations
3. **Monitor order fills** - Build logic around order state changes
4. **Plan your exits** - Always include protective stops

## Next Steps

- Review [Best Practices](../../guides/understanding/best-practices.md) for robust order handling
- Check [Best Practices](../../guides/understanding/best-practices.md) for production deployment

FiveTwenty provides powerful order combinations through OANDA's proven order types - use these building blocks rather than complex custom strategies.