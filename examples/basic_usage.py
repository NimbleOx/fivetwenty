#!/usr/bin/env python3
"""
Basic usage example for OANDA SDK.

Before running, set your OANDA token:
    export OANDA_TOKEN="your-token-here"

Then run:
    python examples/basic_usage.py
"""

import asyncio
import os
from decimal import Decimal

from oanda import AsyncClient, Environment, OandaError


async def main():
    """Demonstrate basic SDK usage."""
    token = os.getenv("OANDA_TOKEN")
    if not token:
        print("Please set OANDA_TOKEN environment variable")
        return
    
    async with AsyncClient(token=token, environment=Environment.PRACTICE) as client:
        try:
            print("🏦 Getting accounts...")
            accounts = await client.accounts.list()
            
            if not accounts:
                print("❌ No accounts found")
                return
            
            account = accounts[0]
            print(f"✅ Using account: {account.id}")
            
            # Get account details
            print("\n📊 Account details...")
            details = await client.accounts.get(account.id)
            print(f"   Currency: {details.currency}")
            print(f"   Balance: {details.balance}")
            print(f"   Open trades: {details.open_trade_count}")
            
            # Get instruments
            print("\n🎯 Available instruments...")
            instruments = await client.accounts.instruments(
                account.id, 
                instruments=["EUR_USD", "GBP_USD", "USD_JPY"]
            )
            
            for instrument in instruments[:3]:  # Show first 3
                print(f"   {instrument.display_name}: {instrument.margin_rate} margin")
            
            # Get current prices
            print("\n💰 Current prices...")
            pricing = await client.pricing.get(
                account.id,
                ["EUR_USD", "GBP_USD"]
            )
            
            for price in pricing.get("prices", []):
                instrument = price["instrument"]
                closeout_bid = price["closeoutBid"]
                closeout_ask = price["closeoutAsk"]
                spread = float(closeout_ask) - float(closeout_bid)
                print(f"   {instrument}: {closeout_bid}/{closeout_ask} (spread: {spread:.5f})")
            
            # Create a small test order (demo only!)
            print("\n📝 Creating test order...")
            try:
                order = await client.orders.create_market(
                    account_id=account.id,
                    instrument="EUR_USD",
                    units=100,  # Very small order
                    stop_loss=Decimal("1.0000"),  # Far away stop loss
                    idempotency_key=f"test-{account.id[:8]}",
                )
                print(f"✅ Order created: {order.last_transaction_id}")
                
            except OandaError as e:
                if "INSUFFICIENT_MARGIN" in str(e):
                    print("ℹ️  Insufficient margin for test order (this is normal)")
                else:
                    print(f"❌ Order failed: {e}")
            
            # Stream prices for a few seconds
            print("\n📡 Streaming prices for 10 seconds...")
            import time
            end_time = time.time() + 10
            count = 0
            
            async for event in client.pricing.stream(account.id, ["EUR_USD"]):
                if hasattr(event, 'instrument'):  # Price update
                    spread = event.spread
                    print(f"   {event.instrument}: {event.closeout_bid}/{event.closeout_ask} (spread: {spread:.5f})")
                    count += 1
                elif hasattr(event, 'time'):  # Heartbeat
                    print(f"   💓 Heartbeat at {event.time}")
                
                if time.time() > end_time or count >= 5:
                    break
            
            print("\n✅ Demo complete!")
            
        except OandaError as e:
            print(f"❌ API Error: {e}")
            if e.request_id:
                print(f"   Request ID: {e.request_id}")
        
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())