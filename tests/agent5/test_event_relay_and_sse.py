"""
Unit and integration tests for Transactional Outbox Event Relay and Live SSE Streaming.
Validates acceptance criteria: since_seq=5 connection streams events from 6 onwards in monotonic order.
CreativeForge Intelligence Studio v3.0 - Modules M06 & M11.
"""

import asyncio
import json
import pytest
from services.worker_event_relay.hub import SSEHub
from services.worker_event_relay.relay import EventRelayWorker


@pytest.mark.asyncio
async def test_sse_wire_format():
    hub = SSEHub()
    sample_event = {
        "event_id": "evt_42",
        "run_id": "run_88",
        "run_seq": 42,
        "event_type": "MODEL_CALL_FINISHED",
        "payload_preview": {
            "node_execution_id": "ne_video_2",
            "attempt_id": "att_video_2",
            "status": "completed",
            "latency_ms": 2780,
        },
    }

    wire_msg = hub.format_sse_message("run_88", sample_event)
    assert wire_msg.startswith("id: run_88:42\n")
    assert "event: MODEL_CALL_FINISHED\n" in wire_msg
    assert "data: {" in wire_msg
    assert wire_msg.endswith("\n\n")


@pytest.mark.asyncio
async def test_sse_catchup_replay_since_seq():
    """
    CRITICAL ACCEPTANCE CRITERION:
    When connecting with since_seq=5, historical events must stream starting from sequence 6 in order.
    """
    hub = SSEHub()
    run_id = "run_catchup_test"

    # Pre-populate 10 historical events
    for seq in range(1, 11):
        hub.record_event(
            run_id,
            {
                "event_id": f"evt_{seq}",
                "run_id": run_id,
                "run_seq": seq,
                "event_type": "NODE_PROGRESS",
                "payload_preview": {"step": seq},
            },
        )

    # Stream with since_seq=5
    received_seqs = []
    generator = hub.stream_run_events(run_id=run_id, since_seq=5)

    # Pull the 5 catch-up events (6, 7, 8, 9, 10)
    for _ in range(5):
        wire_msg = await anext(generator)
        lines = wire_msg.strip().split("\n")
        id_line = lines[0]  # "id: run_catchup_test:6"
        seq = int(id_line.split(":")[-1])
        received_seqs.append(seq)

    # Verify exact sequence
    assert received_seqs == [6, 7, 8, 9, 10], f"Expected [6, 7, 8, 9, 10], got {received_seqs}"


@pytest.mark.asyncio
async def test_sse_last_event_id_header():
    """Verify that Last-Event-ID header 'run_88:3' resumes stream from sequence 4."""
    hub = SSEHub()
    run_id = "run_header_test"

    for seq in range(1, 6):
        hub.record_event(
            run_id,
            {"event_id": f"evt_{seq}", "run_id": run_id, "run_seq": seq, "event_type": "EVENT"},
        )

    generator = hub.stream_run_events(run_id=run_id, last_event_id="run_header_test:3")

    first_msg = await anext(generator)
    assert "id: run_header_test:4\n" in first_msg

    second_msg = await anext(generator)
    assert "id: run_header_test:5\n" in second_msg


@pytest.mark.asyncio
async def test_event_relay_worker_outbox_dispatch():
    relay = EventRelayWorker()
    event_payload = {
        "event_id": "evt_outbox_01",
        "run_id": "run_relay_test",
        "run_seq": 1,
        "event_type": "RUN_STARTED",
        "payload_preview": {"status": "started"},
    }

    outbox_id = relay.enqueue_outbox_event(event_payload)
    assert len(relay._mock_outbox) == 1
    assert relay._mock_outbox[0]["dispatched_at"] is None

    # Process outbox batch
    dispatched = await relay.poll_and_dispatch()
    assert dispatched == 1
    assert relay._mock_outbox[0]["dispatched_at"] is not None
    assert relay._mock_outbox[0]["attempts"] == 1

    # Second poll should find nothing undispatched
    second_dispatched = await relay.poll_and_dispatch()
    assert second_dispatched == 0
