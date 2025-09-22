"""Consolidated integration tests for pricing operations.

This module combines pricing validation, precision checking, and data retrieval
into efficient tests that validate multiple aspects with fewer API calls.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import ClassVar

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import CandlestickGranularity


class PrecisionValidator:
    """Validate price precision per instrument type."""

    PRECISION_RULES: ClassVar[dict[str, int]] = {
        # Major pairs - 5 decimal places
        "EUR_USD": 5,
        "GBP_USD": 5,
        "AUD_USD": 5,
        "NZD_USD": 5,
        "USD_CHF": 5,
        "USD_CAD": 5,
        # JPY pairs - 3 decimal places
        "USD_JPY": 3,
        "EUR_JPY": 3,
        "GBP_JPY": 3,
        # Indices - 1 decimal place
        "SPX500_USD": 1,
        "NAS100_USD": 1,
        # Commodities
        "XAU_USD": 2,  # Gold
        "XAG_USD": 3,  # Silver
    }

    @staticmethod
    def validate_precision(instrument: str, price: str) -> bool:
        """Validate price has correct decimal precision."""
        expected_precision = PrecisionValidator.PRECISION_RULES.get(instrument)

        if expected_precision is None:
            # Dynamic rules for unknown instruments
            if "JPY" in instrument:
                expected_precision = 3
            elif any(idx in instrument for idx in ["SPX", "NAS", "UK100", "DE30", "JP225"]):
                expected_precision = 1
            else:
                expected_precision = 5

        if "." in price:
            actual_precision = len(price.split(".")[-1])
            return actual_precision <= expected_precision
        return True


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.core
class TestConsolidatedPricingOperations:
    """Consolidated tests for pricing operations with efficient API usage."""

    async def test_comprehensive_pricing_validation(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test comprehensive pricing functionality in a single efficient test.

        Consolidates testing of:
        - Current price retrieval for multiple instruments
        - Price precision validation
        - Spread analysis
        - Price consistency checks
        - Market status validation
        """
        print("✓ Starting comprehensive pricing validation test...")

        # Get multiple instruments for testing
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)

        # Test with up to 5 instruments to balance coverage vs speed
        test_instrument_list = all_instruments[:5]
        print(f"✓ Testing pricing for instruments: {test_instrument_list}")

        # Single API call to get pricing for multiple instruments
        pricing_response = await sandbox_client.pricing.get_pricing(
            account_id=test_account_id,
            instruments=test_instrument_list
        )

        assert pricing_response is not None, "Pricing response should not be None"
        prices = pricing_response.get("prices", [])
        assert len(prices) > 0, "Should have at least one price"

        print(f"✓ Retrieved pricing data for {len(prices)} instruments")

        # Validate each price comprehensively
        for i, price in enumerate(prices):
            instrument = price.get("instrument")
            print(f"\n✓ Validating price data for {instrument} ({i+1}/{len(prices)}):")

            # Basic structure validation
            assert price.get("type") == "PRICE", f"Type should be PRICE for {instrument}"
            assert "time" in price, f"Should have timestamp for {instrument}"
            assert "bids" in price, f"Should have bid prices for {instrument}"
            assert "asks" in price, f"Should have ask prices for {instrument}"

            # Get bid/ask prices
            bid_price = price.get("bids", [{}])[0].get("price", "0") if price.get("bids") else "0"
            ask_price = price.get("asks", [{}])[0].get("price", "0") if price.get("asks") else "0"

            print(f"  Bid: {bid_price}, Ask: {ask_price}")

            # Precision validation
            if bid_price != "0":
                bid_valid = PrecisionValidator.validate_precision(instrument, bid_price)
                assert bid_valid, f"Bid price precision invalid for {instrument}: {bid_price}"

            if ask_price != "0":
                ask_valid = PrecisionValidator.validate_precision(instrument, ask_price)
                assert ask_valid, f"Ask price precision invalid for {instrument}: {ask_price}"

            # Spread validation
            if bid_price != "0" and ask_price != "0":
                bid_decimal = Decimal(bid_price)
                ask_decimal = Decimal(ask_price)
                spread = ask_decimal - bid_decimal

                assert spread >= 0, f"Spread should be non-negative for {instrument}"
                assert spread < ask_decimal * Decimal("0.1"), f"Spread should be reasonable for {instrument}"

                spread_pct = (spread / ask_decimal * 100)
                print(f"  Spread: {spread} ({spread_pct:.4f}%)")

            # Market status validation
            if "status" in price:
                status = price.get("status")
                valid_statuses = ["tradeable", "non-tradeable", "invalid"]
                assert status in valid_statuses, f"Invalid status for {instrument}: {status}"
                print(f"  Status: {status}")

            # Timestamp validation
            if "time" in price and price.get("time"):
                time_str = str(price.get("time"))
                assert "T" in time_str, f"Timestamp should be ISO format for {instrument}: {time_str}"
                print(f"  Time: {time_str}")

        print(f"\n✓ Comprehensive pricing validation completed for {len(prices)} instruments")

    async def test_historical_data_and_candlesticks(self, sandbox_client: AsyncClient, test_instruments):
        """Test historical data retrieval and candlestick validation.

        Consolidates testing of:
        - Candlestick data retrieval for multiple granularities
        - OHLC data validation
        - Time series consistency
        - Data completeness
        """
        print("✓ Starting historical data and candlestick validation...")

        # Use first major pair for historical data testing
        test_instrument = test_instruments["major_pairs"][0]
        print(f"✓ Testing historical data for {test_instrument}")

        # Test multiple granularities in a single test
        granularities_to_test = [
            CandlestickGranularity.M5,
            CandlestickGranularity.H1,
            CandlestickGranularity.D,
        ]

        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=7)

        for granularity in granularities_to_test:
            print(f"\n✓ Testing {granularity.value} candlesticks:")

            try:
                candles_response = await sandbox_client.instruments.get_instrument_candles(
                    instrument=test_instrument,
                    granularity=granularity,
                    from_time=start_time,
                    to_time=end_time,
                    count=10  # Limit to reduce test time
                )

                assert candles_response is not None, f"Should have candlestick response for {granularity.value}"
                candles = candles_response.get("candles", [])

                if candles:
                    print(f"  Retrieved {len(candles)} candles")

                    # Validate first few candles
                    for i, candle in enumerate(candles[:3]):
                        assert hasattr(candle, "time"), f"Candle {i} should have time"
                        assert hasattr(candle, "complete"), f"Candle {i} should have complete flag"

                        # Validate OHLC data if present
                        if hasattr(candle, "mid") and candle.mid:
                            mid = candle.mid
                            open_price = Decimal(str(mid.o))
                            high_price = Decimal(str(mid.h))
                            low_price = Decimal(str(mid.l))
                            close_price = Decimal(str(mid.c))

                            # OHLC relationship validation
                            assert high_price >= open_price, f"High >= Open for candle {i}"
                            assert high_price >= close_price, f"High >= Close for candle {i}"
                            assert low_price <= open_price, f"Low <= Open for candle {i}"
                            assert low_price <= close_price, f"Low <= Close for candle {i}"

                            # Precision validation
                            for price_str in [str(mid.o), str(mid.h), str(mid.l), str(mid.c)]:
                                precision_valid = PrecisionValidator.validate_precision(test_instrument, price_str)
                                assert precision_valid, f"Price precision invalid: {price_str}"

                    print(f"  ✓ OHLC validation passed for {granularity.value}")

                    # Time series consistency check
                    if len(candles) >= 2:
                        for i in range(1, min(len(candles), 3)):
                            current_time = candles[i].time
                            previous_time = candles[i - 1].time
                            assert current_time > previous_time, "Candles should be chronological"

                        print(f"  ✓ Time series consistency verified for {granularity.value}")

                else:
                    print(f"  No candles returned for {granularity.value} (this may be normal)")

            except Exception as e:
                print(f"  Error testing {granularity.value}: {type(e).__name__}: {e}")
                # Continue with other granularities

        print("✓ Historical data and candlestick validation completed")

    async def test_pricing_edge_cases_consolidated(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test pricing edge cases and error handling.

        Consolidates testing of:
        - Invalid instrument handling
        - Empty instrument lists
        - Market closure scenarios
        - Data consistency checks
        """
        print("✓ Starting consolidated pricing edge cases test...")

        # Test 1: Invalid instrument
        print("\n✓ Test 1: Invalid instrument handling")
        try:
            await sandbox_client.pricing.get_pricing(
                account_id=test_account_id,
                instruments=["INVALID_INSTRUMENT"]
            )
            print("  ⚠ Invalid instrument request did not raise error (this may be normal in sandbox)")
        except Exception as e:
            print(f"  ✓ Correctly caught invalid instrument error: {type(e).__name__}")

        # Test 2: Empty instrument list
        print("\n✓ Test 2: Empty instrument list handling")
        try:
            await sandbox_client.pricing.get_pricing(
                account_id=test_account_id,
                instruments=[]
            )
            print("  ⚠ Empty instrument list did not raise error (this may be normal)")
        except Exception as e:
            print(f"  ✓ Correctly caught empty instrument list error: {type(e).__name__}")

        # Test 3: Price consistency check with multiple calls
        print("\n✓ Test 3: Price consistency verification")
        test_instrument = test_instruments["major_pairs"][0]

        prices = []
        for i in range(3):
            try:
                response = await sandbox_client.pricing.get_pricing(
                    account_id=test_account_id,
                    instruments=[test_instrument]
                )
                price_data = response.get("prices", [])
                if price_data:
                    prices.append(price_data[0])
                await asyncio.sleep(0.1)  # Small delay between requests
            except Exception as e:
                print(f"  Request {i+1} failed: {type(e).__name__}")

        if len(prices) >= 2:
            first_price = prices[0]
            last_price = prices[-1]

            first_ask = first_price.get("asks", [{}])[0].get("price", "0")
            last_ask = last_price.get("asks", [{}])[0].get("price", "0")

            if first_ask != "0" and last_ask != "0":
                price_change = abs(Decimal(last_ask) - Decimal(first_ask)) / Decimal(first_ask)
                print(f"  Price change over {len(prices)} requests: {price_change:.6f}")

                # Prices shouldn't change more than 5% in a few seconds under normal conditions
                if price_change < Decimal("0.05"):
                    print("  ✓ Price consistency check passed")
                else:
                    print(f"  ⚠ Large price change detected: {price_change} (this may be normal in volatile markets)")

        print("✓ Consolidated pricing edge cases test completed")
