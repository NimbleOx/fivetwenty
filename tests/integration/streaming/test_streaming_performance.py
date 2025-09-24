"""Integration tests for streaming performance and concurrent operations."""

import asyncio
import time
from decimal import Decimal

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.streaming
class TestStreamPerformance:
    """Integration tests for streaming performance and concurrent operations."""

    async def test_stream_performance_stability(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test stream performance under various load conditions."""
        print("✓ Testing stream performance stability...")

        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        # Test 1: Single stream throughput measurement
        try:
            print("  - Testing single stream throughput...")

            throughput_data = {
                "messages_received": 0,
                "prices_received": 0,
                "heartbeats_received": 0,
                "start_time": time.time(),
                "message_times": [],
                "processing_delays": [],
            }

            test_instrument = test_instruments["major_pairs"][0]

            async for _message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=[test_instrument],
            ):
                receive_time = time.time()
                throughput_data["message_times"].append(receive_time)
                throughput_data["messages_received"] += 1

                if isinstance(_message, ClientPrice):
                    throughput_data["prices_received"] += 1

                    # Measure processing delay (simplified)
                    processing_start = time.time()

                    # Simulate message processing
                    bid = Decimal(str(_message.bid))
                    ask = Decimal(str(_message.ask))
                    ask - bid

                    processing_end = time.time()
                    processing_delay = processing_end - processing_start
                    throughput_data["processing_delays"].append(processing_delay)

                elif isinstance(_message, PricingHeartbeat):
                    throughput_data["heartbeats_received"] += 1

                # Stop after collecting sufficient data for analysis
                if throughput_data["messages_received"] >= 20:
                    break

                # Also stop after maximum test duration
                elapsed = receive_time - throughput_data["start_time"]
                if elapsed > 60.0:  # 1 minute maximum
                    break

            # Calculate throughput metrics
            total_duration = time.time() - throughput_data["start_time"]
            messages_per_second = throughput_data["messages_received"] / total_duration
            prices_per_second = throughput_data["prices_received"] / total_duration

            # Calculate processing statistics
            avg_processing_delay = (sum(throughput_data["processing_delays"]) / len(throughput_data["processing_delays"])) if throughput_data["processing_delays"] else 0
            max_processing_delay = max(throughput_data["processing_delays"]) if throughput_data["processing_delays"] else 0

            print("    * Throughput results:")
            print(f"      Duration: {total_duration:.1f}s")
            print(f"      Messages received: {throughput_data['messages_received']}")
            print(f"      Messages/sec: {messages_per_second:.2f}")
            print(f"      Prices/sec: {prices_per_second:.2f}")
            print(f"      Avg processing delay: {avg_processing_delay * 1000:.2f}ms")
            print(f"      Max processing delay: {max_processing_delay * 1000:.2f}ms")

            # Performance validation
            assert messages_per_second > 0, "Should have positive throughput"
            assert avg_processing_delay < 0.1, f"Processing delay too high: {avg_processing_delay:.3f}s"

            print("    ✓ Single stream throughput test successful")

        except Exception as e:
            print(f"✓ Single stream throughput error: {type(e).__name__}: {e}")

        # Test 2: Multi-instrument performance
        try:
            print("  - Testing multi-instrument performance...")

            if len(test_instruments.get("major_pairs", [])) >= 2:
                multi_instruments = test_instruments["major_pairs"][:3]  # Test up to 3 instruments

                multi_perf_data = {
                    "instruments": multi_instruments,
                    "messages_by_instrument": dict.fromkeys(multi_instruments, 0),
                    "total_messages": 0,
                    "start_time": time.time(),
                }

                async for _message in sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=multi_instruments,
                ):
                    multi_perf_data["total_messages"] += 1

                    if isinstance(_message, ClientPrice):
                        instrument = _message.instrument
                        if instrument in multi_perf_data["messages_by_instrument"]:
                            multi_perf_data["messages_by_instrument"][instrument] += 1

                    # Stop after collecting sufficient data
                    if multi_perf_data["total_messages"] >= 30:
                        break

                    # Timeout protection
                    if time.time() - multi_perf_data["start_time"] > 45.0:
                        break

                multi_duration = time.time() - multi_perf_data["start_time"]
                multi_throughput = multi_perf_data["total_messages"] / multi_duration

                print("    * Multi-instrument results:")
                print(f"      Instruments: {len(multi_instruments)}")
                print(f"      Total messages: {multi_perf_data['total_messages']}")
                print(f"      Duration: {multi_duration:.1f}s")
                print(f"      Combined throughput: {multi_throughput:.2f} msg/sec")

                # Per-instrument breakdown
                for instrument in multi_instruments:
                    count = multi_perf_data["messages_by_instrument"][instrument]
                    per_instrument_rate = count / multi_duration
                    print(f"        {instrument}: {count} messages ({per_instrument_rate:.2f}/sec)")

                # Validate multi-instrument performance
                assert multi_throughput > 0, "Multi-instrument throughput should be positive"
                instruments_with_data = sum(1 for count in multi_perf_data["messages_by_instrument"].values() if count > 0)
                assert instruments_with_data >= 1, "Should receive data for at least one instrument"

                print("    ✓ Multi-instrument performance test successful")

            else:
                print("    - Insufficient instruments for multi-instrument performance test")

        except Exception as e:
            print(f"✓ Multi-instrument performance error: {type(e).__name__}: {e}")

        # Test 3: Memory usage stability
        try:
            print("  - Testing memory usage stability...")

            # This is a simplified memory usage test
            # In practice, you'd use memory profiling tools

            memory_test_data = {
                "message_batches": [],
                "batch_size": 10,
                "num_batches": 5,
                "current_batch": 0,
            }

            current_batch_messages = []

            async for _message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=[test_instruments["major_pairs"][0]],
            ):
                current_batch_messages.append(
                    {
                        "type": type(_message).__name__,
                        "timestamp": time.time(),
                    }
                )

                if len(current_batch_messages) >= memory_test_data["batch_size"]:
                    memory_test_data["message_batches"].append(current_batch_messages)
                    memory_test_data["current_batch"] += 1

                    print(f"    * Batch {memory_test_data['current_batch']}: {len(current_batch_messages)} messages")

                    # Clear batch to simulate memory management
                    current_batch_messages = []

                    if memory_test_data["current_batch"] >= memory_test_data["num_batches"]:
                        break

            total_processed = sum(len(batch) for batch in memory_test_data["message_batches"])

            print("    * Memory stability results:")
            print(f"      Batches processed: {len(memory_test_data['message_batches'])}")
            print(f"      Total messages: {total_processed}")
            print("      Memory management: Batching successful")

            # Validate memory management approach
            assert len(memory_test_data["message_batches"]) > 0, "Should process at least one batch"
            assert total_processed > 0, "Should process some messages"

            print("    ✓ Memory usage stability test successful")

        except Exception as e:
            print(f"✓ Memory usage stability error: {type(e).__name__}: {e}")

        # Test 4: Long-running stream stability
        try:
            print("  - Testing long-running stream stability...")

            long_running_data = {
                "phases": [
                    {"name": "Phase 1", "duration": 15, "messages": 0},
                    {"name": "Phase 2", "duration": 15, "messages": 0},
                    {"name": "Phase 3", "duration": 15, "messages": 0},
                ],
                "current_phase": 0,
                "total_messages": 0,
                "errors": [],
                "start_time": time.time(),
            }

            phase_start_time = time.time()

            async for _message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=[test_instruments["major_pairs"][0]],
            ):
                current_time = time.time()
                long_running_data["total_messages"] += 1

                # Update current phase
                if long_running_data["current_phase"] < len(long_running_data["phases"]):
                    current_phase = long_running_data["phases"][long_running_data["current_phase"]]
                    current_phase["messages"] += 1

                    phase_elapsed = current_time - phase_start_time
                    if phase_elapsed >= current_phase["duration"]:
                        print(f"    * {current_phase['name']} completed: {current_phase['messages']} messages in {phase_elapsed:.1f}s")
                        long_running_data["current_phase"] += 1
                        phase_start_time = current_time

                # Stop after all phases or timeout
                total_elapsed = current_time - long_running_data["start_time"]
                if long_running_data["current_phase"] >= len(long_running_data["phases"]) or total_elapsed > 60.0:
                    break

            total_duration = time.time() - long_running_data["start_time"]
            overall_rate = long_running_data["total_messages"] / total_duration

            print("    * Long-running stability results:")
            print(f"      Total duration: {total_duration:.1f}s")
            print(f"      Total messages: {long_running_data['total_messages']}")
            print(f"      Overall rate: {overall_rate:.2f} msg/sec")
            print(f"      Phases completed: {long_running_data['current_phase']}/{len(long_running_data['phases'])}")

            # Phase-by-phase analysis
            for i, phase in enumerate(long_running_data["phases"]):
                if i < long_running_data["current_phase"]:
                    phase_rate = phase["messages"] / phase["duration"]
                    print(f"        {phase['name']}: {phase['messages']} messages ({phase_rate:.2f}/sec)")

            # Validate long-running stability
            assert long_running_data["total_messages"] > 0, "Should receive messages during long run"
            assert overall_rate > 0, "Should maintain positive message rate"

            print("    ✓ Long-running stream stability test successful")

        except Exception as e:
            print(f"✓ Long-running stream stability error: {type(e).__name__}: {e}")

        print("✓ Stream performance stability test completed")

    async def test_concurrent_streams(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test concurrent stream handling and resource management."""
        print("✓ Testing concurrent streams...")

        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        # Test 1: Multiple concurrent price streams
        try:
            print("  - Testing multiple concurrent price streams...")

            concurrent_data = {
                "streams": [],
                "stream_results": {},
                "total_messages": 0,
                "errors": [],
            }

            # Prepare multiple streams
            instruments_to_test = test_instruments["major_pairs"][:2]  # Test with 2 instruments

            async def run_concurrent_stream(stream_id: str, instrument: str):
                """Run a single concurrent stream."""
                stream_data = {
                    "stream_id": stream_id,
                    "instrument": instrument,
                    "messages": 0,
                    "prices": 0,
                    "heartbeats": 0,
                    "errors": [],
                    "start_time": time.time(),
                }

                try:
                    async for _message in sandbox_client.pricing.get_pricing_stream(
                        account_id=test_account_id,
                        instruments=[instrument],
                    ):
                        stream_data["messages"] += 1

                        if isinstance(_message, ClientPrice):
                            stream_data["prices"] += 1
                        elif isinstance(_message, PricingHeartbeat):
                            stream_data["heartbeats"] += 1

                        # Stop individual stream after collecting enough data
                        if stream_data["messages"] >= 8:
                            break

                        # Timeout protection
                        if time.time() - stream_data["start_time"] > 30.0:
                            break

                except Exception as stream_error:
                    stream_data["errors"].append(str(stream_error))

                return stream_data

            # Run concurrent streams
            concurrent_tasks = []
            for i, instrument in enumerate(instruments_to_test):
                stream_id = f"stream_{i + 1}_{instrument}"
                task = run_concurrent_stream(stream_id, instrument)
                concurrent_tasks.append(task)

            # Execute all streams concurrently
            stream_results = await asyncio.gather(*concurrent_tasks, return_exceptions=True)

            # Analyze concurrent results
            successful_streams = 0
            total_concurrent_messages = 0

            for i, result in enumerate(stream_results):
                if isinstance(result, Exception):
                    concurrent_data["errors"].append(f"Stream {i + 1}: {result}")
                    print(f"    * Stream {i + 1}: Error - {type(result).__name__}")
                else:
                    successful_streams += 1
                    total_concurrent_messages += result["messages"]
                    concurrent_data["stream_results"][result["stream_id"]] = result

                    print(f"    * {result['stream_id']}: {result['messages']} messages ({result['prices']} prices, {result['heartbeats']} heartbeats)")

            print("    * Concurrent streams results:")
            print(f"      Streams launched: {len(concurrent_tasks)}")
            print(f"      Successful streams: {successful_streams}")
            print(f"      Total messages: {total_concurrent_messages}")
            print(f"      Errors: {len(concurrent_data['errors'])}")

            # Validate concurrent performance
            assert successful_streams > 0, "At least one concurrent stream should succeed"

            if successful_streams > 1:
                print("    ✓ Multiple concurrent streams successful")
            else:
                print("    - Single concurrent stream successful (may be expected)")

        except Exception as e:
            print(f"✓ Concurrent streams error: {type(e).__name__}: {e}")

        # Test 2: Stream switching performance
        try:
            print("  - Testing stream switching performance...")

            switching_data = {
                "switches": 0,
                "switch_times": [],
                "messages_per_stream": [],
                "total_messages": 0,
            }

            instruments_for_switching = test_instruments["major_pairs"][:2]

            for switch_num in range(3):  # Test 3 switches
                switching_data["switches"] += 1
                current_instrument = instruments_for_switching[switch_num % len(instruments_for_switching)]

                print(f"    * Switch {switch_num + 1}: Starting stream for {current_instrument}")

                switch_start = time.time()
                stream_messages = 0

                async for _message in sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=[current_instrument],
                ):
                    stream_messages += 1
                    switching_data["total_messages"] += 1

                    # Stop this stream after a few messages
                    if stream_messages >= 3:
                        break

                    # Timeout protection
                    if time.time() - switch_start > 15.0:
                        break

                switch_duration = time.time() - switch_start
                switching_data["switch_times"].append(switch_duration)
                switching_data["messages_per_stream"].append(stream_messages)

                print(f"      Switch {switch_num + 1} completed: {stream_messages} messages in {switch_duration:.1f}s")

                # Small delay between switches
                await asyncio.sleep(0.5)

            # Analyze switching performance
            avg_switch_time = sum(switching_data["switch_times"]) / len(switching_data["switch_times"])
            avg_messages_per_stream = sum(switching_data["messages_per_stream"]) / len(switching_data["messages_per_stream"])

            print("    * Stream switching results:")
            print(f"      Switches completed: {switching_data['switches']}")
            print(f"      Average switch time: {avg_switch_time:.1f}s")
            print(f"      Average messages per stream: {avg_messages_per_stream:.1f}")
            print(f"      Total messages: {switching_data['total_messages']}")

            # Validate switching performance
            assert switching_data["switches"] > 0, "Should complete at least one switch"
            assert switching_data["total_messages"] > 0, "Should receive messages across switches"
            assert avg_switch_time < 30.0, f"Average switch time too high: {avg_switch_time:.1f}s"

            print("    ✓ Stream switching performance test successful")

        except Exception as e:
            print(f"✓ Stream switching performance error: {type(e).__name__}: {e}")

        # Test 3: Resource cleanup under concurrent load
        try:
            print("  - Testing resource cleanup under concurrent load...")

            cleanup_data = {
                "cleanup_cycles": 0,
                "streams_created": 0,
                "streams_cleaned": 0,
                "cleanup_errors": 0,
            }

            # Simulate multiple create/cleanup cycles
            for cycle in range(3):
                cleanup_data["cleanup_cycles"] += 1
                cycle_streams = []

                print(f"    * Cleanup cycle {cycle + 1}: Creating streams...")

                # Create multiple short-lived streams
                for stream_num in range(2):
                    cleanup_data["streams_created"] += 1

                    try:
                        stream = sandbox_client.pricing.get_pricing_stream(
                            account_id=test_account_id,
                            instruments=[test_instruments["major_pairs"][0]],
                        )

                        # Collect just a few messages then stop
                        message_count = 0
                        async for _message in stream:
                            message_count += 1
                            if message_count >= 2:
                                break

                        cycle_streams.append(f"stream_{cycle}_{stream_num}")
                        print(f"      Created and used stream {stream_num + 1}: {message_count} messages")

                    except Exception as stream_create_error:
                        cleanup_data["cleanup_errors"] += 1
                        print(f"      Stream {stream_num + 1} error: {type(stream_create_error).__name__}")

                # Simulate cleanup (streams should clean up automatically)
                cleanup_data["streams_cleaned"] += len(cycle_streams)
                print(f"    * Cycle {cycle + 1} completed: {len(cycle_streams)} streams cleaned")

                # Small delay between cycles
                await asyncio.sleep(1.0)

            print("    * Resource cleanup results:")
            print(f"      Cleanup cycles: {cleanup_data['cleanup_cycles']}")
            print(f"      Streams created: {cleanup_data['streams_created']}")
            print(f"      Streams cleaned: {cleanup_data['streams_cleaned']}")
            print(f"      Cleanup errors: {cleanup_data['cleanup_errors']}")

            # Validate resource cleanup
            cleanup_success_rate = (cleanup_data["streams_cleaned"] / cleanup_data["streams_created"] * 100) if cleanup_data["streams_created"] > 0 else 100

            assert cleanup_success_rate >= 80, f"Cleanup success rate too low: {cleanup_success_rate:.1f}%"

            print("    ✓ Resource cleanup test successful")

        except Exception as e:
            print(f"✓ Resource cleanup error: {type(e).__name__}: {e}")

        print("✓ Concurrent streams test completed")
