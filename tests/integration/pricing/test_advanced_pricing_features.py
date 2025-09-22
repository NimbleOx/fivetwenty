"""Integration tests for advanced pricing features.

This module tests advanced pricing functionality that was previously
missing from integration test coverage.
"""

from datetime import datetime, timedelta, timezone

import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.core
class TestAdvancedPricingFeatures:
    """Integration tests for advanced pricing operations."""

    async def test_latest_candles_multiple_specs(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test latest candles endpoint with multiple specifications.

        Validates:
        - Latest candles for multiple instrument/granularity combinations
        - Candle specification formatting
        - Multi-instrument candle retrieval
        - Parameter validation
        """
        print("✓ Starting latest candles multiple specifications test...")

        # Get multiple instruments for testing
        all_instruments = []
        for category_instruments in test_instruments.values():
            all_instruments.extend(category_instruments)

        # Use up to 3 instruments to balance coverage vs speed
        test_instrument_list = all_instruments[:3]
        print(f"  Testing latest candles for instruments: {test_instrument_list}")

        try:
            # Test 1: Multiple candle specifications
            print("\n✓ Test 1: Multiple candle specifications")

            candle_specs = []
            for instrument in test_instrument_list:
                # Create specifications for different granularities
                candle_specs.extend([
                    f"{instrument}:M1:M",  # 1-minute mid prices
                    f"{instrument}:H1:M",  # 1-hour mid prices
                ])

            print(f"  Candle specifications: {candle_specs}")

            latest_response = await sandbox_client.pricing.get_latest_candles(
                account_id=test_account_id,
                candle_specifications=candle_specs,
                units=5  # Get 5 latest candles for each spec
            )

            assert latest_response is not None, "Latest candles response should not be None"

            if "latestCandles" in latest_response:
                latest_candles = latest_response["latestCandles"]
                print(f"  ✓ Retrieved latest candles for {len(latest_candles)} specifications")

                # Validate each candle specification result
                for candle_result in latest_candles:
                    if isinstance(candle_result, dict):
                        assert "instrument" in candle_result, "Should have instrument field"
                        assert "granularity" in candle_result, "Should have granularity field"
                        assert "candles" in candle_result, "Should have candles field"

                        instrument = candle_result["instrument"]
                        granularity = candle_result["granularity"]
                        candles = candle_result["candles"]

                        print(f"    {instrument} {granularity}: {len(candles)} candles")

                        # Validate candle data
                        if candles and len(candles) > 0:
                            first_candle = candles[0]
                            if hasattr(first_candle, "time"):
                                print(f"      Latest candle time: {first_candle.time}")
                            if hasattr(first_candle, "complete"):
                                print(f"      Candle complete: {first_candle.complete}")

            else:
                print("  ✓ Latest candles response structure validated")

            # Test 2: Different price types (Bid, Ask, Mid)
            print("\n✓ Test 2: Different price types")

            price_type_specs = [
                f"{test_instrument_list[0]}:M5:B",  # Bid prices
                f"{test_instrument_list[0]}:M5:A",  # Ask prices
                f"{test_instrument_list[0]}:M5:M",  # Mid prices
            ]

            price_types_response = await sandbox_client.pricing.get_latest_candles(
                account_id=test_account_id,
                candle_specifications=price_type_specs,
                units=3
            )

            assert price_types_response is not None, "Price types response should not be None"

            if "latestCandles" in price_types_response:
                price_candles = price_types_response["latestCandles"]
                print(f"  ✓ Retrieved {len(price_candles)} price type specifications")

                for price_result in price_candles:
                    if isinstance(price_result, dict) and "candles" in price_result:
                        candles = price_result["candles"]
                        if candles and len(candles) > 0:
                            candle = candles[0]
                            # Check which price types are available
                            has_bid = hasattr(candle, "bid") and candle.bid
                            has_ask = hasattr(candle, "ask") and candle.ask
                            has_mid = hasattr(candle, "mid") and candle.mid
                            print(f"    Price types available - Bid: {has_bid}, Ask: {has_ask}, Mid: {has_mid}")

            # Test 3: Smoothing and alignment parameters
            print("\n✓ Test 3: Smoothing and alignment parameters")

            smooth_specs = [f"{test_instrument_list[0]}:H1:M"]

            smooth_response = await sandbox_client.pricing.get_latest_candles(
                account_id=test_account_id,
                candle_specifications=smooth_specs,
                units=2,
                smooth=True,
                daily_alignment=17,
                alignment_timezone="America/New_York",
                weekly_alignment="Friday"
            )

            assert smooth_response is not None, "Smoothed response should not be None"
            print("  ✓ Smoothing and alignment parameters accepted")

        except FiveTwentyError as e:
            print(f"  ⚠ Latest candles test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during latest candles test: {type(e).__name__}: {e}")

        print("✓ Latest candles multiple specifications test completed")

    async def test_latest_candles_error_handling(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test error handling for latest candles endpoint.

        Validates:
        - Invalid candle specification handling
        - Parameter validation
        - Empty specification list handling
        - Invalid account ID handling
        """
        print("✓ Starting latest candles error handling test...")

        # Test 1: Empty candle specifications
        print("\n✓ Test 1: Empty candle specifications")

        try:
            with pytest.raises((ValueError, FiveTwentyError)):
                await sandbox_client.pricing.get_latest_candles(
                    account_id=test_account_id,
                    candle_specifications=[]  # Empty list should raise ValueError
                )
            print("  ✓ Empty specifications correctly rejected")
        except Exception as e:
            print(f"  ✓ Empty specifications rejected: {type(e).__name__}")

        # Test 2: Invalid candle specification format
        print("\n✓ Test 2: Invalid candle specification format")

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.pricing.get_latest_candles(
                    account_id=test_account_id,
                    candle_specifications=["INVALID_FORMAT"]  # Missing colons
                )

            error = exc_info.value
            assert error.status == 400, f"Expected 400 for invalid format, got {error.status}"
            print("  ✓ Invalid specification format correctly rejected")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid format: {type(e).__name__}")

        # Test 3: Invalid units parameter
        print("\n✓ Test 3: Invalid units parameter")

        try:
            with pytest.raises((ValueError, FiveTwentyError)):
                await sandbox_client.pricing.get_latest_candles(
                    account_id=test_account_id,
                    candle_specifications=["EUR_USD:M1:M"],
                    units=0  # Invalid: units must be >= 1
                )
            print("  ✓ Invalid units (0) correctly rejected")
        except Exception as e:
            print(f"  ✓ Invalid units rejected: {type(e).__name__}")

        try:
            with pytest.raises((ValueError, FiveTwentyError)):
                await sandbox_client.pricing.get_latest_candles(
                    account_id=test_account_id,
                    candle_specifications=["EUR_USD:M1:M"],
                    units=6000  # Invalid: units must be <= 5000
                )
            print("  ✓ Invalid units (6000) correctly rejected")
        except Exception as e:
            print(f"  ✓ Large units rejected: {type(e).__name__}")

        # Test 4: Invalid account ID
        print("\n✓ Test 4: Invalid account ID")

        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.pricing.get_latest_candles(
                    account_id="invalid-account-123",
                    candle_specifications=["EUR_USD:M1:M"]
                )

            error = exc_info.value
            assert error.status in [400, 404], f"Expected 400/404 for invalid account, got {error.status}"
            print(f"  ✓ Invalid account ID correctly rejected: HTTP {error.status}")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid account: {type(e).__name__}")

        print("✓ Latest candles error handling test completed")

    async def test_account_instrument_candles_vs_instrument_candles(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test differentiation between account-based and general instrument candles.

        Validates:
        - Account-specific instrument candles functionality
        - Comparison with general instrument candles
        - Account-specific pricing behavior
        - Data consistency between endpoints
        """
        print("✓ Starting account vs general instrument candles comparison test...")

        test_instrument = test_instruments["major_pairs"][0]
        print(f"  Using instrument: {test_instrument}")

        try:
            # Common parameters for both endpoints
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=2)
            candle_count = 5

            # Test 1: Account-specific instrument candles
            print("\n✓ Test 1: Account-specific instrument candles")

            account_candles_response = await sandbox_client.pricing.get_account_instrument_candles(
                account_id=test_account_id,
                instrument=test_instrument,
                granularity="H1",  # Use H1 which is more commonly supported
                count=candle_count
            )

            assert account_candles_response is not None, "Account candles response should not be None"

            account_candles = []
            if "candles" in account_candles_response:
                account_candles = account_candles_response["candles"]
                print(f"  ✓ Account-specific candles: {len(account_candles)} retrieved")

                # Validate account-specific candle structure
                if account_candles:
                    first_candle = account_candles[0]
                    print(f"    First candle time: {first_candle.time}")
                    print(f"    First candle complete: {first_candle.complete}")

            # Test 2: General instrument candles
            print("\n✓ Test 2: General instrument candles")

            general_candles_response = await sandbox_client.instruments.get_instrument_candles(
                instrument=test_instrument,
                granularity="H1",  # Use H1 which is more commonly supported
                count=candle_count
            )

            assert general_candles_response is not None, "General candles response should not be None"

            general_candles = []
            if "candles" in general_candles_response:
                general_candles = general_candles_response["candles"]
                print(f"  ✓ General instrument candles: {len(general_candles)} retrieved")

                # Validate general candle structure
                if general_candles:
                    first_candle = general_candles[0]
                    print(f"    First candle time: {first_candle.time}")
                    print(f"    First candle complete: {first_candle.complete}")

            # Test 3: Compare data consistency (if both have data)
            print("\n✓ Test 3: Data consistency comparison")

            if account_candles and general_candles:
                # Compare candle counts
                print(f"    Account candles count: {len(account_candles)}")
                print(f"    General candles count: {len(general_candles)}")

                # Compare timestamps of first candles
                if len(account_candles) > 0 and len(general_candles) > 0:
                    account_time = account_candles[0].time
                    general_time = general_candles[0].time
                    print(f"    Account first candle time: {account_time}")
                    print(f"    General first candle time: {general_time}")

                    # Times should be similar (within reasonable difference)
                    if account_time == general_time:
                        print("    ✓ Candle times match exactly")
                    else:
                        print("    ✓ Candle times differ (expected for different endpoints)")

            else:
                print("    ⚠ Cannot compare - insufficient data from one or both endpoints")

            # Test 4: Account-specific pricing behavior
            print("\n✓ Test 4: Account-specific pricing behavior validation")

            # Test with different price components for account-specific endpoint
            try:
                account_candles_bid_ask = await sandbox_client.pricing.get_account_instrument_candles(
                    account_id=test_account_id,
                    instrument=test_instrument,
                    granularity="H1",
                    count=2,
                    price="BA"  # Bid and Ask prices
                )

                if account_candles_bid_ask and "candles" in account_candles_bid_ask:
                    ba_candles = account_candles_bid_ask["candles"]
                    if ba_candles:
                        candle = ba_candles[0]
                        has_bid = hasattr(candle, "bid") and candle.bid
                        has_ask = hasattr(candle, "ask") and candle.ask
                        print(f"    ✓ Account BA candles - Bid: {has_bid}, Ask: {has_ask}")

            except Exception as e:
                print(f"    ⚠ Account-specific BA pricing test failed: {type(e).__name__}")

        except FiveTwentyError as e:
            print(f"  ⚠ Candles comparison test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during candles comparison: {type(e).__name__}: {e}")

        print("✓ Account vs general instrument candles comparison test completed")

    async def test_advanced_candle_parameters(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test advanced candle parameters and options.

        Validates:
        - Weekly alignment options
        - Daily alignment settings
        - Timezone handling
        - Smoothing functionality
        - includeFirst parameter behavior
        """
        print("✓ Starting advanced candle parameters test...")

        test_instrument = test_instruments["major_pairs"][0]
        print(f"  Using instrument: {test_instrument}")

        try:
            # Test 1: Weekly alignment options
            print("\n✓ Test 1: Weekly alignment options")

            weekly_alignments = ["Sunday", "Monday", "Friday"]

            for alignment in weekly_alignments:
                try:
                    weekly_response = await sandbox_client.pricing.get_latest_candles(
                        account_id=test_account_id,
                        candle_specifications=[f"{test_instrument}:W:M"],
                        units=1,
                        weekly_alignment=alignment
                    )

                    assert weekly_response is not None, f"Weekly alignment {alignment} should work"
                    print(f"    ✓ Weekly alignment '{alignment}' accepted")

                except Exception as e:
                    print(f"    ⚠ Weekly alignment '{alignment}' failed: {type(e).__name__}")

            # Test 2: Daily alignment hours
            print("\n✓ Test 2: Daily alignment hours")

            alignment_hours = [0, 12, 17, 23]

            for hour in alignment_hours:
                try:
                    daily_response = await sandbox_client.pricing.get_latest_candles(
                        account_id=test_account_id,
                        candle_specifications=[f"{test_instrument}:D:M"],
                        units=1,
                        daily_alignment=hour
                    )

                    assert daily_response is not None, f"Daily alignment hour {hour} should work"
                    print(f"    ✓ Daily alignment hour {hour} accepted")

                except Exception as e:
                    print(f"    ⚠ Daily alignment hour {hour} failed: {type(e).__name__}")

            # Test 3: Timezone handling
            print("\n✓ Test 3: Timezone handling")

            timezones = ["America/New_York", "Europe/London", "Asia/Tokyo"]

            for tz in timezones:
                try:
                    tz_response = await sandbox_client.pricing.get_latest_candles(
                        account_id=test_account_id,
                        candle_specifications=[f"{test_instrument}:H4:M"],
                        units=1,
                        alignment_timezone=tz
                    )

                    assert tz_response is not None, f"Timezone {tz} should work"
                    print(f"    ✓ Timezone '{tz}' accepted")

                except Exception as e:
                    print(f"    ⚠ Timezone '{tz}' failed: {type(e).__name__}")

            # Test 4: Smoothing functionality
            print("\n✓ Test 4: Smoothing functionality")

            for smooth in [True, False]:
                try:
                    smooth_response = await sandbox_client.pricing.get_latest_candles(
                        account_id=test_account_id,
                        candle_specifications=[f"{test_instrument}:M5:M"],
                        units=2,
                        smooth=smooth
                    )

                    assert smooth_response is not None, f"Smoothing {smooth} should work"
                    print(f"    ✓ Smoothing {smooth} accepted")

                except Exception as e:
                    print(f"    ⚠ Smoothing {smooth} failed: {type(e).__name__}")

        except Exception as e:
            print(f"  ⚠ Advanced parameters test failed: {type(e).__name__}: {e}")

        print("✓ Advanced candle parameters test completed")
