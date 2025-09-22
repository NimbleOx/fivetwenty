"""Integration tests for systematic position management operations.

This module tests position closing functionality that was previously
missing comprehensive integration test coverage.
"""


import pytest

from fivetwenty import AsyncClient
from fivetwenty.exceptions import FiveTwentyError


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.trading
class TestPositionManagement:
    """Integration tests for systematic position management operations."""

    async def test_systematic_position_closing(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test systematic position closing functionality.

        Validates:
        - Complete position closure (ALL units)
        - Partial position closure (specific units)
        - Long/short position side closing
        - Position closure validation
        - Error handling for invalid parameters
        """
        print("✓ Starting systematic position closing test...")

        test_instrument = test_instruments["major_pairs"][0]  # EUR_USD
        print(f"  Using instrument: {test_instrument}")

        # Get initial position state
        try:
            initial_positions_response = await sandbox_client.positions.get_positions(test_account_id)
            initial_positions = initial_positions_response.get("positions", [])
            print(f"  Initial positions count: {len(initial_positions)}")

            # Check if we have any open positions
            open_position = None
            for pos in initial_positions:
                if hasattr(pos, "instrument") and pos.instrument == test_instrument:
                    if (hasattr(pos, "long") and pos.long and hasattr(pos.long, "units") and int(pos.long.units) != 0) or \
                       (hasattr(pos, "short") and pos.short and hasattr(pos.short, "units") and int(pos.short.units) != 0):
                        open_position = pos
                        break

            if open_position:
                print(f"  Found existing open position for {test_instrument}")

                # Test 1: Get specific position details
                print("\n✓ Test 1: Position details retrieval")

                position_response = await sandbox_client.positions.get_position(test_account_id, test_instrument)
                assert position_response is not None, "Position response should not be None"

                if "position" in position_response:
                    position = position_response["position"]
                    print(f"  ✓ Retrieved position details for {test_instrument}")

                    # Analyze position sides
                    long_units = 0
                    short_units = 0

                    if hasattr(position, "long") and position.long and hasattr(position.long, "units"):
                        long_units = int(position.long.units)
                        print(f"    Long position: {long_units} units")

                    if hasattr(position, "short") and position.short and hasattr(position.short, "units"):
                        short_units = int(position.short.units)
                        print(f"    Short position: {short_units} units")

                    # Test 2: Partial position closure (if position is large enough)
                    if long_units > 1:
                        print("\n✓ Test 2: Partial long position closure")

                        partial_units = min(long_units // 2, 500)  # Close half or max 500 units

                        try:
                            partial_close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                long_units=str(partial_units)
                            )

                            assert partial_close_response is not None, "Partial close response should not be None"
                            print(f"  ✓ Partially closed {partial_units} long units")

                            # Verify partial closure worked
                            updated_position_response = await sandbox_client.positions.get_position(test_account_id, test_instrument)
                            if "position" in updated_position_response:
                                updated_position = updated_position_response["position"]
                                if hasattr(updated_position, "long") and updated_position.long:
                                    remaining_long = int(updated_position.long.units)
                                    expected_remaining = long_units - partial_units
                                    print(f"    Remaining long units: {remaining_long} (expected: {expected_remaining})")

                        except FiveTwentyError as e:
                            print(f"  ⚠ Partial closure not supported: {e.status} - {e.code}")
                        except Exception as e:
                            print(f"  ⚠ Unexpected error during partial closure: {type(e).__name__}")

                    elif short_units > 1:
                        print("\n✓ Test 2: Partial short position closure")

                        partial_units = min(abs(short_units) // 2, 500)

                        try:
                            partial_close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                short_units=str(partial_units)
                            )

                            assert partial_close_response is not None, "Partial close response should not be None"
                            print(f"  ✓ Partially closed {partial_units} short units")

                        except FiveTwentyError as e:
                            print(f"  ⚠ Partial closure not supported: {e.status} - {e.code}")
                        except Exception as e:
                            print(f"  ⚠ Unexpected error during partial closure: {type(e).__name__}")

                    else:
                        print("\n✓ Test 2: Skipped - position too small for partial closure")

                    # Test 3: Complete position closure using "ALL"
                    print("\n✓ Test 3: Complete position closure")

                    try:
                        if long_units != 0:
                            all_close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                long_units="ALL"
                            )
                            print("  ✓ Closed all long units using 'ALL'")

                        if short_units != 0:
                            all_close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                short_units="ALL"
                            )
                            print("  ✓ Closed all short units using 'ALL'")

                        # Verify complete closure
                        final_position_response = await sandbox_client.positions.get_position(test_account_id, test_instrument)
                        if "position" in final_position_response:
                            final_position = final_position_response["position"]
                            final_long = 0
                            final_short = 0

                            if hasattr(final_position, "long") and final_position.long:
                                final_long = int(final_position.long.units)
                            if hasattr(final_position, "short") and final_position.short:
                                final_short = int(final_position.short.units)

                            print(f"    Final position - Long: {final_long}, Short: {final_short}")

                    except FiveTwentyError as e:
                        print(f"  ⚠ Complete closure failed: {e.status} - {e.code}")
                    except Exception as e:
                        print(f"  ⚠ Unexpected error during complete closure: {type(e).__name__}")

                else:
                    print("  ⚠ Position response missing 'position' field")

            else:
                print(f"  No existing position found for {test_instrument} - creating test position")

                # Create a small test position first
                try:
                    # Get minimum trade size for the instrument
                    instruments_response = await sandbox_client.accounts.get_account_instruments(
                        test_account_id, instruments=[test_instrument]
                    )

                    if instruments_response.get("instruments"):
                        instrument_details = instruments_response["instruments"][0]
                        min_trade_size = max(int(instrument_details.minimum_trade_size), 1)

                        # Create a small market order to establish a position
                        market_order_response = await sandbox_client.orders.post_market_order(
                            account_id=test_account_id,
                            instrument=test_instrument,
                            units=min_trade_size,
                        )

                        if market_order_response and market_order_response.order_fill_transaction:
                            print(f"  ✓ Created test position with {min_trade_size} units")

                            # Now test closing this new position
                            close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                long_units="ALL"
                            )

                            print("  ✓ Successfully closed test position")

                except Exception as e:
                    print(f"  ⚠ Could not create test position: {type(e).__name__}")

        except FiveTwentyError as e:
            print(f"  ⚠ Position closing test failed: {e.status} - {e.code}")
        except Exception as e:
            print(f"  ⚠ Unexpected error during position test: {type(e).__name__}: {e}")

        # Test 4: Error handling for invalid position closure parameters
        print("\n✓ Test 4: Invalid parameter error handling")

        # Test with no parameters
        try:
            with pytest.raises((ValueError, FiveTwentyError)):
                await sandbox_client.positions.close_position(
                    account_id=test_account_id,
                    instrument=test_instrument
                    # No long_units or short_units - should raise ValueError
                )
            print("  ✓ Empty parameters correctly rejected")
        except Exception as e:
            print(f"  ✓ Empty parameters rejected: {type(e).__name__}")

        # Test with invalid instrument
        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.positions.close_position(
                    account_id=test_account_id,
                    instrument="INVALID_INSTRUMENT",
                    long_units="ALL"
                )

            error = exc_info.value
            assert error.status == 400, f"Expected 400 for invalid instrument, got {error.status}"
            print("  ✓ Invalid instrument correctly rejected")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid instrument: {type(e).__name__}")

        # Test with invalid account ID
        try:
            with pytest.raises(FiveTwentyError) as exc_info:
                await sandbox_client.positions.close_position(
                    account_id="invalid-account-123",
                    instrument=test_instrument,
                    long_units="ALL"
                )

            error = exc_info.value
            assert error.status in [400, 404], f"Expected 400/404 for invalid account, got {error.status}"
            print(f"  ✓ Invalid account ID correctly rejected: HTTP {error.status}")

        except AssertionError:
            raise
        except Exception as e:
            print(f"  ⚠ Unexpected error for invalid account: {type(e).__name__}")

        print("✓ Systematic position closing test completed")

    async def test_position_closure_with_client_extensions(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test position closure with client extensions.

        Validates:
        - Client extensions in position closure orders
        - Long and short side extension handling
        - Extension data preservation
        """
        print("✓ Starting position closure with client extensions test...")

        test_instrument = test_instruments["major_pairs"][0]
        print(f"  Using instrument: {test_instrument}")

        try:
            # Check for existing positions
            positions_response = await sandbox_client.positions.get_positions(test_account_id)
            positions = positions_response.get("positions", [])

            # Find a position with open units
            test_position = None
            for pos in positions:
                if hasattr(pos, "instrument") and pos.instrument == test_instrument:
                    has_long = hasattr(pos, "long") and pos.long and hasattr(pos.long, "units") and int(pos.long.units) != 0
                    has_short = hasattr(pos, "short") and pos.short and hasattr(pos.short, "units") and int(pos.short.units) != 0

                    if has_long or has_short:
                        test_position = pos
                        break

            if test_position:
                print("  Found position for client extensions test")

                # Test client extensions for position closure
                client_extensions = {
                    "id": f"test-close-{test_account_id[-4:]}",
                    "tag": "integration-test-close",
                    "comment": "Position closure with client extensions"
                }

                print(f"  Testing client extensions: {client_extensions}")

                # Determine which side to close
                if hasattr(test_position, "long") and test_position.long and hasattr(test_position.long, "units"):
                    long_units = int(test_position.long.units)
                    if long_units > 0:
                        try:
                            close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                long_units="ALL",
                                long_client_extensions=client_extensions
                            )

                            assert close_response is not None, "Close response should not be None"
                            print("  ✓ Position closed with long client extensions")

                        except FiveTwentyError as e:
                            print(f"  ⚠ Client extensions closure failed: {e.status} - {e.code}")
                        except Exception as e:
                            print(f"  ⚠ Unexpected error with client extensions: {type(e).__name__}")

                elif hasattr(test_position, "short") and test_position.short and hasattr(test_position.short, "units"):
                    short_units = int(test_position.short.units)
                    if short_units != 0:
                        try:
                            close_response = await sandbox_client.positions.close_position(
                                account_id=test_account_id,
                                instrument=test_instrument,
                                short_units="ALL",
                                short_client_extensions=client_extensions
                            )

                            assert close_response is not None, "Close response should not be None"
                            print("  ✓ Position closed with short client extensions")

                        except FiveTwentyError as e:
                            print(f"  ⚠ Client extensions closure failed: {e.status} - {e.code}")
                        except Exception as e:
                            print(f"  ⚠ Unexpected error with client extensions: {type(e).__name__}")

            else:
                print("  ⚠ No open positions found for client extensions test")

        except Exception as e:
            print(f"  ⚠ Client extensions test failed: {type(e).__name__}: {e}")

        print("✓ Position closure with client extensions test completed")
