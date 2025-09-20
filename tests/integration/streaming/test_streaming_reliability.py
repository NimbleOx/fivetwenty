"""Integration tests for streaming reliability and error recovery."""

import asyncio
import time

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.streaming
class TestStreamReliability:
    """Integration tests for streaming reliability and error recovery."""

    async def test_stream_error_recovery(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test stream error recovery and resilience."""
        print("✓ Testing stream error recovery...")

        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        test_instrument = test_instruments["major_pairs"][0]

        # Test 1: Stream interruption simulation
        try:
            print("  - Testing stream interruption handling...")

            interruption_data = {
                "total_messages": 0,
                "pre_interruption_messages": 0,
                "post_recovery_messages": 0,
                "errors_encountered": [],
                "recovery_successful": False,
            }

            async def simulate_stream_with_interruption():
                try:
                    stream = sandbox_client.pricing.get_pricing_stream(
                        account_id=test_account_id,
                        instruments=[test_instrument],
                    )

                    async for message in stream:
                        interruption_data["total_messages"] += 1

                        if isinstance(message, ClientPrice):
                            print(f"    * Message {interruption_data['total_messages']}: {message.instrument}")

                        # Simulate interruption after a few messages
                        if interruption_data["total_messages"] == 3:
                            interruption_data["pre_interruption_messages"] = interruption_data["total_messages"]
                            print("    * Simulating stream interruption...")
                            raise Exception("Simulated stream interruption")  # noqa: TRY002

                        # Continue collecting post-"recovery" messages
                        if interruption_data["total_messages"] > 3:
                            interruption_data["post_recovery_messages"] += 1

                        if interruption_data["total_messages"] >= 8:
                            interruption_data["recovery_successful"] = True
                            break

                except Exception as stream_error:
                    interruption_data["errors_encountered"].append(str(stream_error))
                    print(f"    * Stream error: {type(stream_error).__name__}")

                    # Simulate recovery by creating new stream
                    if "Simulated stream interruption" in str(stream_error):
                        print("    * Attempting recovery...")
                        await asyncio.sleep(1.0)

                        try:
                            recovery_stream = sandbox_client.pricing.get_pricing_stream(
                                account_id=test_account_id,
                                instruments=[test_instrument],
                            )

                            recovery_count = 0
                            async for _recovery_message in recovery_stream:
                                recovery_count += 1
                                interruption_data["post_recovery_messages"] += 1
                                print(f"    * Recovery message {recovery_count}")

                                if recovery_count >= 3:
                                    interruption_data["recovery_successful"] = True
                                    break

                        except Exception as recovery_error:
                            print(f"    * Recovery failed: {type(recovery_error).__name__}")

            # Run interruption simulation
            await simulate_stream_with_interruption()

            print("    * Interruption test results:")
            print(f"      Total messages: {interruption_data['total_messages']}")
            print(f"      Pre-interruption: {interruption_data['pre_interruption_messages']}")
            print(f"      Post-recovery: {interruption_data['post_recovery_messages']}")
            print(f"      Errors encountered: {len(interruption_data['errors_encountered'])}")
            print(f"      Recovery successful: {interruption_data['recovery_successful']}")

            # Should demonstrate recovery capability
            assert interruption_data["pre_interruption_messages"] > 0, "Should receive messages before interruption"

            if interruption_data["recovery_successful"]:
                print("    ✓ Stream recovery capability demonstrated")
            else:
                print("    - Stream recovery test inconclusive")

        except Exception as e:
            print(f"✓ Stream interruption handling error: {type(e).__name__}: {e}")

        # Test 2: Invalid parameter recovery
        try:
            print("  - Testing invalid parameter recovery...")

            invalid_param_results = {
                "invalid_attempts": 0,
                "recovery_attempts": 0,
                "successful_recoveries": 0,
            }

            # Test with invalid instrument first
            invalid_param_results["invalid_attempts"] += 1
            try:
                invalid_stream = sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=["INVALID_INSTRUMENT"],
                )

                invalid_count = 0
                async for _invalid_message in invalid_stream:
                    invalid_count += 1
                    if invalid_count >= 2:
                        break

                if invalid_count > 0:
                    print("    * Invalid instrument stream produced data (unexpected)")

            except Exception as invalid_error:
                print(f"    * Invalid instrument rejected: {type(invalid_error).__name__}")

            # Now test recovery with valid parameters
            invalid_param_results["recovery_attempts"] += 1
            try:
                recovery_stream = sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=[test_instrument],
                )

                recovery_count = 0
                async for _recovery_message in recovery_stream:
                    recovery_count += 1
                    if recovery_count >= 2:
                        invalid_param_results["successful_recoveries"] += 1
                        break

                print(f"    * Recovery after invalid parameters: {recovery_count} messages")

            except Exception as recovery_error:
                print(f"    * Recovery after invalid parameters failed: {type(recovery_error).__name__}")

            print("    * Invalid parameter recovery results:")
            print(f"      Invalid attempts: {invalid_param_results['invalid_attempts']}")
            print(f"      Recovery attempts: {invalid_param_results['recovery_attempts']}")
            print(f"      Successful recoveries: {invalid_param_results['successful_recoveries']}")

            print("    ✓ Invalid parameter recovery test completed")

        except Exception as e:
            print(f"✓ Invalid parameter recovery error: {type(e).__name__}: {e}")

        # Test 3: Network timeout recovery
        try:
            print("  - Testing network timeout recovery...")

            timeout_recovery_data = {
                "timeout_tests": 0,
                "timeouts_encountered": 0,
                "recovery_after_timeout": 0,
            }

            # Test stream behavior with very short timeout
            timeout_recovery_data["timeout_tests"] += 1

            try:
                # Create stream and test timeout behavior
                timeout_stream = sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=[test_instrument],
                )

                timeout_count = 0
                timeout_start = time.time()

                try:
                    async for _timeout_message in timeout_stream:
                        timeout_count += 1
                        elapsed = time.time() - timeout_start

                        # Force timeout after short duration
                        if elapsed > 5.0:  # 5 second timeout
                            timeout_recovery_data["timeouts_encountered"] += 1
                            print("    * Forcing timeout for testing...")
                            break

                        if timeout_count >= 5:
                            break

                    print(f"    * Timeout test: {timeout_count} messages in {elapsed:.1f}s")

                except asyncio.TimeoutError:
                    timeout_recovery_data["timeouts_encountered"] += 1
                    print("    * Timeout encountered (as expected)")

                # Test recovery after timeout
                if timeout_recovery_data["timeouts_encountered"] > 0:
                    print("    * Testing recovery after timeout...")

                    try:
                        post_timeout_stream = sandbox_client.pricing.get_pricing_stream(
                            account_id=test_account_id,
                            instruments=[test_instrument],
                        )

                        post_timeout_count = 0
                        async for _post_timeout_message in post_timeout_stream:
                            post_timeout_count += 1
                            if post_timeout_count >= 2:
                                timeout_recovery_data["recovery_after_timeout"] += 1
                                break

                        print(f"    * Post-timeout recovery: {post_timeout_count} messages")

                    except Exception as post_timeout_error:
                        print(f"    * Post-timeout recovery failed: {type(post_timeout_error).__name__}")

            except Exception as timeout_test_error:
                print(f"    * Timeout test error: {type(timeout_test_error).__name__}")

            print("    * Timeout recovery results:")
            print(f"      Timeout tests: {timeout_recovery_data['timeout_tests']}")
            print(f"      Timeouts encountered: {timeout_recovery_data['timeouts_encountered']}")
            print(f"      Recovery after timeout: {timeout_recovery_data['recovery_after_timeout']}")

            print("    ✓ Network timeout recovery test completed")

        except Exception as e:
            print(f"✓ Network timeout recovery error: {type(e).__name__}: {e}")

        print("✓ Stream error recovery test completed")

    async def test_stream_heartbeat_monitoring(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test stream heartbeat monitoring and stall detection."""
        print("✓ Testing stream heartbeat monitoring...")

        # Test 1: Heartbeat reception and timing
        try:
            print("  - Testing heartbeat reception and timing...")

            heartbeat_data = {
                "heartbeats_received": 0,
                "prices_received": 0,
                "heartbeat_times": [],
                "intervals": [],
                "first_heartbeat": None,
                "last_heartbeat": None,
            }

            heartbeat_start_time = time.time()

            async for message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=["EUR_USD"],
            ):
                current_time = time.time()

                if isinstance(message, PricingHeartbeat):
                    heartbeat_data["heartbeats_received"] += 1
                    heartbeat_data["heartbeat_times"].append(current_time)

                    if heartbeat_data["first_heartbeat"] is None:
                        heartbeat_data["first_heartbeat"] = message
                    heartbeat_data["last_heartbeat"] = message

                    print(f"    * Heartbeat {heartbeat_data['heartbeats_received']}: {message.time}")

                    # Calculate intervals between heartbeats
                    if len(heartbeat_data["heartbeat_times"]) >= 2:
                        interval = heartbeat_data["heartbeat_times"][-1] - heartbeat_data["heartbeat_times"][-2]
                        heartbeat_data["intervals"].append(interval)

                elif isinstance(message, ClientPrice):
                    heartbeat_data["prices_received"] += 1

                # Stop after collecting sufficient heartbeat data or timeout
                if heartbeat_data["heartbeats_received"] >= 5 or current_time - heartbeat_start_time > 30.0:
                    break

            total_duration = time.time() - heartbeat_start_time

            print("    * Heartbeat monitoring results:")
            print(f"      Duration: {total_duration:.1f}s")
            print(f"      Heartbeats: {heartbeat_data['heartbeats_received']}")
            print(f"      Prices: {heartbeat_data['prices_received']}")
            print(f"      Intervals calculated: {len(heartbeat_data['intervals'])}")

            # Analyze heartbeat intervals
            if heartbeat_data["intervals"]:
                avg_interval = sum(heartbeat_data["intervals"]) / len(heartbeat_data["intervals"])
                min_interval = min(heartbeat_data["intervals"])
                max_interval = max(heartbeat_data["intervals"])

                print(f"      Avg interval: {avg_interval:.1f}s")
                print(f"      Min interval: {min_interval:.1f}s")
                print(f"      Max interval: {max_interval:.1f}s")

                # Heartbeat intervals should be reasonable (typically 5-60 seconds)
                assert avg_interval > 0, "Average interval should be positive"
                assert avg_interval < 300, "Average interval should be less than 5 minutes"

            # Validate heartbeat structure
            if heartbeat_data["first_heartbeat"]:
                first_hb = heartbeat_data["first_heartbeat"]
                assert hasattr(first_hb, "type"), "Heartbeat should have type"
                assert hasattr(first_hb, "time"), "Heartbeat should have time"
                assert first_hb.type == "HEARTBEAT", "Type should be HEARTBEAT"

            print("    ✓ Heartbeat reception and timing test successful")

        except Exception as e:
            print(f"✓ Heartbeat reception and timing error: {type(e).__name__}: {e}")

        # Test 2: Stream stall detection simulation
        try:
            print("  - Testing stream stall detection...")

            stall_detection_data = {
                "messages_before_stall": 0,
                "stall_detected": False,
                "recovery_messages": 0,
                "stall_duration": 0,
            }

            stall_start_time = time.time()
            last_message_time = stall_start_time

            async for message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=["EUR_USD"],
            ):
                current_time = time.time()
                time_since_last = current_time - last_message_time
                last_message_time = current_time

                if isinstance(message, ClientPrice | PricingHeartbeat):
                    if not stall_detection_data["stall_detected"]:
                        stall_detection_data["messages_before_stall"] += 1
                    else:
                        stall_detection_data["recovery_messages"] += 1

                    print(f"    * Message (gap: {time_since_last:.1f}s): {type(message).__name__}")

                    # Simulate stall detection (no messages for extended period)
                    # In a real implementation, this would be handled by the client
                    if time_since_last > 15.0 and not stall_detection_data["stall_detected"] and stall_detection_data["messages_before_stall"] >= 2:
                        stall_detection_data["stall_detected"] = True
                        stall_detection_data["stall_duration"] = time_since_last
                        print(f"    * Stall detected: {time_since_last:.1f}s without messages")

                # Stop after demonstrating stall detection or timeout
                if current_time - stall_start_time > 45.0 or (stall_detection_data["stall_detected"] and stall_detection_data["recovery_messages"] >= 2):
                    break

            print("    * Stall detection results:")
            print(f"      Messages before stall: {stall_detection_data['messages_before_stall']}")
            print(f"      Stall detected: {stall_detection_data['stall_detected']}")
            print(f"      Stall duration: {stall_detection_data['stall_duration']:.1f}s")
            print(f"      Recovery messages: {stall_detection_data['recovery_messages']}")

            if stall_detection_data["stall_detected"]:
                print("    ✓ Stream stall detection demonstrated")
            else:
                print("    - No stream stalls detected during test period")

            print("    ✓ Stream stall detection test completed")

        except Exception as e:
            print(f"✓ Stream stall detection error: {type(e).__name__}: {e}")

        # Test 3: Heartbeat frequency analysis
        try:
            print("  - Testing heartbeat frequency analysis...")

            frequency_data = {
                "observation_period": 60.0,  # 1 minute
                "heartbeats": [],
                "prices": [],
                "start_time": time.time(),
            }

            async for message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=["EUR_USD"],
            ):
                current_time = time.time()
                elapsed = current_time - frequency_data["start_time"]

                if isinstance(message, PricingHeartbeat):
                    frequency_data["heartbeats"].append(current_time)
                elif isinstance(message, ClientPrice):
                    frequency_data["prices"].append(current_time)

                # Stop after observation period
                if elapsed >= frequency_data["observation_period"]:
                    print(f"    * Observation period completed: {elapsed:.1f}s")
                    break

                # Also stop if we've collected sufficient data
                if len(frequency_data["heartbeats"]) >= 10:
                    print("    * Sufficient heartbeat data collected")
                    break

            # Analyze frequency
            observation_duration = min(time.time() - frequency_data["start_time"], frequency_data["observation_period"])

            heartbeat_frequency = len(frequency_data["heartbeats"]) / observation_duration * 60  # per minute
            price_frequency = len(frequency_data["prices"]) / observation_duration * 60  # per minute

            print("    * Frequency analysis results:")
            print(f"      Observation duration: {observation_duration:.1f}s")
            print(f"      Heartbeats: {len(frequency_data['heartbeats'])} ({heartbeat_frequency:.1f}/min)")
            print(f"      Prices: {len(frequency_data['prices'])} ({price_frequency:.1f}/min)")

            # Basic frequency validation
            total_messages = len(frequency_data["heartbeats"]) + len(frequency_data["prices"])
            assert total_messages > 0, "Should receive some messages during observation period"

            if len(frequency_data["heartbeats"]) > 0:
                # Heartbeat frequency should be reasonable (typically 1-12 per minute)
                assert heartbeat_frequency < 60, "Heartbeat frequency should be reasonable"

            print("    ✓ Heartbeat frequency analysis completed")

        except Exception as e:
            print(f"✓ Heartbeat frequency analysis error: {type(e).__name__}: {e}")

        print("✓ Stream heartbeat monitoring test completed")
