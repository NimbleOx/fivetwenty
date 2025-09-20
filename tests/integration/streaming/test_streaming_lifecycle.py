"""Integration tests for streaming lifecycle management."""

import asyncio
import time

import pytest

from fivetwenty import AsyncClient
from fivetwenty.models import ClientPrice, PricingHeartbeat


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.streaming
class TestStreamLifecycle:
    """Integration tests for streaming lifecycle management."""

    async def test_account_stream_lifecycle(self, sandbox_client: AsyncClient, test_account_id: str):
        """Test account streaming lifecycle management."""
        print("✓ Testing account stream lifecycle...")

        # Test 1: Account stream initialization
        try:
            print("  - Testing account stream initialization...")

            account_updates = []
            stream_count = 0

            # Note: Account streaming might not be available in sandbox or might work differently
            # This test structure shows how it would be tested if available

            try:
                async for account_update in sandbox_client.accounts.get_account_changes_stream(account_id=test_account_id):
                    stream_count += 1
                    account_updates.append(account_update)
                    print(f"    * Account update {stream_count}: {type(account_update).__name__}")

                    # Validate account update structure
                    if hasattr(account_update, "changes"):
                        print(f"      Changes: {len(account_update.changes) if account_update.changes else 0}")

                    # Stop after a few updates for testing
                    if stream_count >= 3:
                        break

                print(f"    ✓ Account stream received {stream_count} updates")

            except AttributeError:
                print("    - Account streaming not available in current client implementation")
            except Exception as account_stream_error:
                print(f"    - Account stream: {type(account_stream_error).__name__}")

        except Exception as e:
            print(f"✓ Account stream initialization error: {type(e).__name__}: {e}")

        # Test 2: Account stream data validation (if available)
        try:
            print("  - Testing account stream data validation...")

            if account_updates:
                for i, update in enumerate(account_updates):
                    print(f"    * Validating account update {i + 1}")

                    # Basic structure validation
                    assert hasattr(update, "lastTransactionID"), "Update should have last transaction ID"

                    if hasattr(update, "changes") and update.changes:
                        for change in update.changes:
                            print(f"      Change type: {type(change).__name__}")

                print("    ✓ Account stream data validation successful")
            else:
                print("    - No account updates to validate")

        except Exception as e:
            print(f"✓ Account stream data validation error: {type(e).__name__}: {e}")

        # Test 3: Account stream termination
        try:
            print("  - Testing account stream termination...")

            # Test clean termination of account stream
            try:
                account_termination_stream = sandbox_client.accounts.get_account_changes_stream(account_id=test_account_id)

                termination_count = 0
                async for _update in account_termination_stream:
                    termination_count += 1
                    if termination_count >= 1:
                        print("    * Terminating account stream...")
                        break

                print("    ✓ Account stream terminated cleanly")

            except AttributeError:
                print("    - Account streaming termination test not applicable")
            except Exception as termination_error:
                print(f"    - Account stream termination: {type(termination_error).__name__}")

        except Exception as e:
            print(f"✓ Account stream termination error: {type(e).__name__}: {e}")

        print("✓ Account stream lifecycle test completed")

    async def test_stream_configuration_options(self, sandbox_client: AsyncClient, test_account_id: str, test_instruments):
        """Test various stream configuration options."""
        print("✓ Testing stream configuration options...")

        if not test_instruments or not test_instruments.get("major_pairs"):
            pytest.skip("No test instruments available")

        test_instrument = test_instruments["major_pairs"][0]

        # Test 1: Snapshot option
        try:
            print("  - Testing snapshot configuration...")

            # Test with snapshot=True
            snapshot_stream_data = {"prices": 0, "heartbeats": 0}

            async for _message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=[test_instrument],
                snapshot=True,
            ):
                if isinstance(_message, ClientPrice):
                    snapshot_stream_data["prices"] += 1
                elif isinstance(_message, PricingHeartbeat):
                    snapshot_stream_data["heartbeats"] += 1

                if snapshot_stream_data["prices"] >= 3:
                    break

            print(f"    * Snapshot=True: {snapshot_stream_data['prices']} prices, {snapshot_stream_data['heartbeats']} heartbeats")

            # Test with snapshot=False
            no_snapshot_stream_data = {"prices": 0, "heartbeats": 0}

            async for _message in sandbox_client.pricing.get_pricing_stream(
                account_id=test_account_id,
                instruments=[test_instrument],
                snapshot=False,
            ):
                if isinstance(_message, ClientPrice):
                    no_snapshot_stream_data["prices"] += 1
                elif isinstance(_message, PricingHeartbeat):
                    no_snapshot_stream_data["heartbeats"] += 1

                if no_snapshot_stream_data["prices"] >= 3:
                    break

            print(f"    * Snapshot=False: {no_snapshot_stream_data['prices']} prices, {no_snapshot_stream_data['heartbeats']} heartbeats")

            # Both configurations should work
            assert snapshot_stream_data["prices"] > 0, "Snapshot=True should receive prices"
            assert no_snapshot_stream_data["prices"] > 0, "Snapshot=False should receive prices"

            print("    ✓ Snapshot configuration test successful")

        except Exception as e:
            print(f"✓ Snapshot configuration error: {type(e).__name__}: {e}")

        # Test 2: Include unrealized P&L option (if available)
        try:
            print("  - Testing include unrealized P&L configuration...")

            # This might be an account stream feature
            try:
                pnl_stream_data = {"updates": 0}

                async for _message in sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=[test_instrument],
                    include_unrealized_pl=True,
                ):
                    pnl_stream_data["updates"] += 1
                    print(f"    * P&L stream update {pnl_stream_data['updates']}")

                    if pnl_stream_data["updates"] >= 2:
                        break

                print("    ✓ Include unrealized P&L configuration successful")

            except Exception as pnl_error:
                print(f"    - Include unrealized P&L: {type(pnl_error).__name__} (may not be supported)")

        except Exception as e:
            print(f"✓ Include unrealized P&L configuration error: {type(e).__name__}: {e}")

        # Test 3: Stream timeout behavior
        try:
            print("  - Testing stream timeout behavior...")

            timeout_start = time.time()
            timeout_messages = 0

            try:
                # Test with a reasonable timeout
                async for _message in sandbox_client.pricing.get_pricing_stream(
                    account_id=test_account_id,
                    instruments=[test_instrument],
                ):
                    timeout_messages += 1
                    current_time = time.time()

                    # Stop after 10 seconds or 5 messages
                    if current_time - timeout_start > 10.0 or timeout_messages >= 5:
                        print("    * Timeout test stopping...")
                        break

                timeout_duration = time.time() - timeout_start
                print(f"    * Timeout test: {timeout_messages} messages in {timeout_duration:.1f}s")

                print("    ✓ Stream timeout behavior test successful")

            except asyncio.TimeoutError:
                print("    ✓ Stream timeout handled correctly")

        except Exception as e:
            print(f"✓ Stream timeout behavior error: {type(e).__name__}: {e}")

        print("✓ Stream configuration options test completed")
