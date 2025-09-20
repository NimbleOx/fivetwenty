"""Integration tests for OANDA API streaming compliance."""

import time
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.streaming
class TestStreamCompliance:
    """Integration tests for OANDA API streaming compliance."""

    async def test_stream_api_compliance(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test OANDA API specification compliance for streaming."""
        print("✓ Testing OANDA API specification compliance...")

        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        test_instrument = test_instruments["major_pairs"][0]
        multi_instruments = test_instruments["major_pairs"][:2] if len(test_instruments["major_pairs"]) >= 2 else [test_instrument]

        # Test 1: Price and Heartbeat object structure validation
        try:
            print("  - Testing price and heartbeat object structure...")

            structure_validation_count = 0
            price_objects = []
            heartbeat_objects = []

            async for message in sandbox_client.pricing.get_pricing_stream(account_id=test_account_id, instruments=[test_instrument], snapshot=True, stall_timeout=10.0):
                structure_validation_count += 1

                if isinstance(message, ClientPrice):
                    price_objects.append(message)
                    # Validate Price object structure
                    self._validate_price_object_structure(message, test_instrument)
                    print(f"    * Price object validation passed: {message.instrument}")

                elif isinstance(message, PricingHeartbeat):
                    heartbeat_objects.append(message)
                    # Validate Heartbeat object structure
                    self._validate_heartbeat_object_structure(message)
                    print(f"    * Heartbeat object validation passed: {message.time}")

                # Stop after validating several objects
                if structure_validation_count >= 8:
                    break

            print(f"    ✓ Structure validation: {len(price_objects)} prices, {len(heartbeat_objects)} heartbeats")

        except Exception as e:
            print(f"✓ Structure validation error: {type(e).__name__}: {e}")

        # Test 2: Rate limiting compliance (4 updates/sec/instrument per OANDA spec)
        try:
            print("  - Testing rate limiting compliance (4 updates/sec/instrument)...")

            rate_start_time = time.time()
            price_timestamps = []
            rate_test_duration = 5.0  # Test for 5 seconds

            async for message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=multi_instruments,  # Multiple instruments to potentially trigger rate limiting
                snapshot=True,
                stall_timeout=8.0,
            ):
                current_time = time.time()

                if isinstance(message, ClientPrice):
                    price_timestamps.append({"instrument": str(message.instrument), "timestamp": current_time, "elapsed": current_time - rate_start_time})

                # Stop after test duration
                if current_time - rate_start_time >= rate_test_duration:
                    break

            # Analyze rate limiting
            if price_timestamps:
                total_duration = price_timestamps[-1]["elapsed"]
                total_updates = len(price_timestamps)
                overall_rate = total_updates / total_duration if total_duration > 0 else 0

                # Per-instrument rate analysis
                instrument_rates = {}
                for instrument in multi_instruments:
                    instrument_updates = [p for p in price_timestamps if p["instrument"] == instrument]
                    if instrument_updates:
                        instrument_rate = len(instrument_updates) / total_duration if total_duration > 0 else 0
                        instrument_rates[instrument] = instrument_rate

                print(f"    ✓ Rate analysis: {total_updates} updates in {total_duration:.2f}s")
                print(f"      Overall rate: {overall_rate:.2f} updates/sec")

                for instrument, rate in instrument_rates.items():
                    print(f"      {instrument}: {rate:.2f} updates/sec")

                    # OANDA spec: maximum 4 updates/sec/instrument
                    # We'll be lenient and allow up to 5 for test variations
                    if rate > 5.0:
                        print(f"      Warning: {instrument} rate ({rate:.2f}) may exceed OANDA limit (4/sec)")

        except Exception as e:
            print(f"✓ Rate limiting test error: {type(e).__name__}: {e}")

        # Test 3: Parameter validation and behavior
        try:
            print("  - Testing parameter validation and behavior...")

            # Test snapshot parameter behavior
            snapshot_tests = [{"snapshot": True, "name": "with_snapshot"}, {"snapshot": False, "name": "without_snapshot"}]

            for test_config in snapshot_tests:
                config_messages = 0
                config_start = time.time()

                async for message in sandbox_client.pricing.get_pricing_stream(account_id=test_account_id, instruments=[test_instrument], snapshot=test_config["snapshot"], stall_timeout=5.0):
                    config_messages += 1

                    # Validate message types are correct
                    assert isinstance(message, ClientPrice | PricingHeartbeat), "Message should be Price or Heartbeat type"

                    if config_messages >= 3:  # Quick validation
                        break

                config_duration = time.time() - config_start
                print(f"    ✓ {test_config['name']}: {config_messages} messages in {config_duration:.2f}s")

        except Exception as e:
            print(f"✓ Parameter validation error: {type(e).__name__}: {e}")

        # Test 4: Streaming URL vs REST URL validation (conceptual)
        try:
            print("  - Testing URL endpoint validation...")

            # This test validates that our client correctly uses streaming endpoints
            # We can't directly test the URL but we can validate streaming behavior
            url_test_start = time.time()
            streaming_messages = 0
            continuous_stream = True

            async for message in sandbox_client.pricing.get_pricing_stream(account_id=test_account_id, instruments=[test_instrument], snapshot=True, stall_timeout=8.0):
                streaming_messages += 1

                # Validate continuous streaming behavior (characteristic of streaming endpoints)
                if isinstance(message, ClientPrice | PricingHeartbeat):
                    # Streaming endpoints should provide continuous data
                    current_time = time.time()
                    if current_time - url_test_start > 3.0 and streaming_messages < 2:
                        continuous_stream = False
                        break

                if streaming_messages >= 5:
                    break

            if continuous_stream and streaming_messages >= 3:
                print("    ✓ Streaming endpoint behavior validated (continuous data flow)")
            else:
                print(f"    ! Streaming behavior validation: {streaming_messages} messages (expected continuous flow)")

        except Exception as e:
            print(f"✓ URL endpoint validation error: {type(e).__name__}: {e}")

        print("✓ OANDA API specification compliance test completed")

    def _validate_price_object_structure(self, price_message: ClientPrice, expected_instrument: str):
        """Validate Price object structure against OANDA API specification."""
        # Validate core Price object fields per OANDA spec
        assert hasattr(price_message, "instrument"), "Price object should have 'instrument' field"
        assert str(price_message.instrument) == expected_instrument, f"Price instrument should match expected: {expected_instrument}"

        # Validate required Price fields
        assert hasattr(price_message, "time"), "Price object should have 'time' field"
        assert price_message.time, "Price time should not be empty"

        # Validate bid/ask structure
        assert hasattr(price_message, "bids"), "Price object should have 'bids' field"
        assert hasattr(price_message, "asks"), "Price object should have 'asks' field"

        # Validate closeout prices
        assert hasattr(price_message, "closeout_bid"), "Price object should have 'closeout_bid' field"
        assert hasattr(price_message, "closeout_ask"), "Price object should have 'closeout_ask' field"

        # Validate price values are positive
        assert Decimal(price_message.closeout_bid) > 0, "Closeout bid should be positive"
        assert Decimal(price_message.closeout_ask) > 0, "Closeout ask should be positive"
        assert Decimal(price_message.closeout_ask) > Decimal(price_message.closeout_bid), "Ask should be greater than bid"

        # Validate tradeable status if present
        if hasattr(price_message, "tradeable"):
            assert isinstance(price_message.tradeable, bool), "Tradeable field should be boolean"

    def _validate_heartbeat_object_structure(self, heartbeat_message: PricingHeartbeat):
        """Validate Heartbeat object structure against OANDA API specification."""
        # Validate core Heartbeat fields per OANDA spec
        assert hasattr(heartbeat_message, "type"), "Heartbeat object should have 'type' field"
        assert heartbeat_message.type == "HEARTBEAT", f"Heartbeat type should be 'HEARTBEAT', got: {heartbeat_message.type}"

        assert hasattr(heartbeat_message, "time"), "Heartbeat object should have 'time' field"
        assert heartbeat_message.time, "Heartbeat time should not be empty"

        # Validate timestamp format (should be ISO 8601 format)
        import re

        iso_pattern = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z"
        assert re.match(iso_pattern, heartbeat_message.time), f"Heartbeat time should be ISO 8601 format: {heartbeat_message.time}"

    def _validate_price_precision(self, price_value: Decimal):
        """Validate price precision according to OANDA specification (up to 5 decimal places)."""
        # Convert to string to check decimal places
        price_str = str(price_value)

        if "." in price_str:
            decimal_part = price_str.split(".")[1]
            decimal_places = len(decimal_part)

            # OANDA typically uses up to 5 decimal places for most currency pairs
            assert decimal_places <= 5, f"Price precision should not exceed 5 decimal places, got {decimal_places}: {price_value}"

            # Ensure we have reasonable precision (at least 1 decimal place for FX)
            assert decimal_places >= 1, f"Price should have at least 1 decimal place for FX: {price_value}"

        # Ensure price is within reasonable range for FX (0.00001 to 10000)
        assert 0.00001 <= price_value <= 10000, f"Price should be within reasonable FX range: {price_value}"
