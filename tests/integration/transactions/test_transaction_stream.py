"""Integration tests for the live transaction stream endpoint."""

import asyncio

import pytest

from fivetwenty import AsyncClient
from fivetwenty.endpoints.transactions import TransactionUnion
from fivetwenty.exceptions import StreamStall
from fivetwenty.models import TransactionHeartbeat

# Heartbeats arrive roughly every 5 seconds, even when markets are closed;
# 20 seconds gives ample room for connection setup plus several heartbeats.
STREAM_TIME_BUDGET_SECONDS = 20.0


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.streaming
class TestTransactionStream:
    """Integration tests for streaming live transaction events."""

    async def test_transaction_stream_delivers_heartbeat(self, sandbox_client_no_cleanup: AsyncClient, test_account_id: str):
        """Test connecting to the transaction stream and receiving a heartbeat.

        Validates:
        - Stream connects and yields events via async iteration
        - At least one TransactionHeartbeat arrives within the time budget
        - Heartbeat parses into the TransactionHeartbeat model
        - Any real transaction events parse into TransactionUnion models
        """
        print("✓ Starting transaction stream heartbeat test...")

        events = []

        async def collect_until_heartbeat() -> None:
            async for event in sandbox_client_no_cleanup.transactions.get_transactions_stream(test_account_id):
                events.append(event)
                print(f"  * Stream event {len(events)}: {type(event).__name__}")
                if isinstance(event, TransactionHeartbeat):
                    return

        try:
            await asyncio.wait_for(collect_until_heartbeat(), timeout=STREAM_TIME_BUDGET_SECONDS)
        except StreamStall as exc:
            pytest.fail(f"Transaction stream stalled before delivering a heartbeat: {exc}")
        except asyncio.TimeoutError:
            pytest.fail(f"No TransactionHeartbeat received within {STREAM_TIME_BUDGET_SECONDS}s (received {len(events)} events)")

        heartbeats = [event for event in events if isinstance(event, TransactionHeartbeat)]
        assert heartbeats, "Expected at least one TransactionHeartbeat from the stream"

        heartbeat = heartbeats[-1]
        assert heartbeat.type == "HEARTBEAT"
        assert heartbeat.time is not None
        assert heartbeat.last_transaction_id is not None
        print(f"  ✓ Heartbeat validated: time={heartbeat.time}, lastTransactionID={heartbeat.last_transaction_id}")

        # Any non-heartbeat events (real transactions) must parse into TransactionUnion models
        for event in events:
            if not isinstance(event, TransactionHeartbeat):
                assert isinstance(event, TransactionUnion), f"Unexpected stream event type: {type(event).__name__}"
                print(f"  ✓ Real transaction event validated: {type(event).__name__}")

        print("✓ Transaction stream heartbeat test completed")
