#!/usr/bin/env python3
"""
Sync usage example for FiveTwenty.

Before running, set your FiveTwenty token:
    export FIVETWENTY_OANDA_TOKEN="your-token-here"

Then run:
    python examples/sync_usage.py
"""

import os

from fivetwenty import Client, Environment, FiveTwentyError


def main() -> None:
    """Demonstrate sync SDK usage."""
    token = os.getenv("FIVETWENTY_OANDA_TOKEN")
    if not token:
        print("Please set FIVETWENTY_OANDA_TOKEN environment variable")
        return

    with Client(token=token, environment=Environment.PRACTICE) as client:
        try:
            print("🏦 Getting accounts...")
            accounts = client.accounts.list()

            if not accounts:
                print("❌ No accounts found")
                return

            account = accounts[0]
            print(f"✅ Using account: {account.id}")

            # Get account details
            print("\n📊 Account summary...")
            details = client.accounts.summary(account.id)
            print(f"   Balance: {details.balance} {details.currency}")
            print(f"   Unrealized P&L: {details.unrealized_pl}")

            # Get current pricing
            print("\n💰 Getting current prices...")
            pricing = client.pricing.get(account.id, ["EUR_USD"])

            for price in pricing.get("prices", []):
                bid = price["closeoutBid"]
                ask = price["closeoutAsk"]
                spread = float(ask) - float(bid)
                print(f"   EUR_USD: {bid}/{ask} (spread: {spread:.5f})")

            # Stream prices for a bit (blocking iterator)
            print("\n📡 Streaming 5 price updates...")
            count = 0

            for event in client.pricing.stream_iter(account.id, ["EUR_USD"]):
                if hasattr(event, "instrument"):  # Price update
                    # Type narrowing - we know it's a ClientPrice if it has 'instrument'
                    if hasattr(event, "closeout_bid") and hasattr(event, "closeout_ask"):
                        print(f"   {event.instrument}: {event.closeout_bid}/{event.closeout_ask}")
                    count += 1

                    if count >= 5:
                        break  # Stop after 5 price updates

            print("\n✅ Sync demo complete!")

        except FiveTwentyError as e:
            print(f"❌ API Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
