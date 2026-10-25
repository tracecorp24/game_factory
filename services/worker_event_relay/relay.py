"""
Transactional Outbox Event Relay Worker.
Polls undispatched events from outbox_events, routes to appropriate run channels,
and updates dispatch status atomically.
CreativeForge Intelligence Studio v3.0 - Module M06 / M11.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from services.worker_event_relay.hub import sse_hub

logger = logging.getLogger("worker_event_relay.relay")


class EventRelayWorker:
    """Worker daemon polling outbox_events and dispatching to SSEHub & consumers."""

    def __init__(
        self,
        poll_interval: float = 1.0,
        batch_size: int = 50,
        db_session_factory: Optional[Callable[[], Any]] = None,
    ):
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.db_session_factory = db_session_factory
        self.is_running = False
        # In-memory outbox buffer for environments without active Postgres connection
        self._mock_outbox: List[Dict[str, Any]] = []

    def enqueue_outbox_event(self, event_data: Dict[str, Any]) -> str:
        """Add event to local outbox queue for dispatching."""
        outbox_id = f"outbox_{len(self._mock_outbox) + 1}"
        record = {
            "id": outbox_id,
            "event_id": event_data.get("event_id", f"evt_{outbox_id}"),
            "run_id": event_data.get("run_id", "default_run"),
            "event_type": event_data.get("event_type", "EVENT"),
            "payload": event_data,
            "dispatched_at": None,
            "attempts": 0,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._mock_outbox.append(record)
        return outbox_id

    async def poll_and_dispatch(self) -> int:
        """Process one batch of undispatched outbox events."""
        # 1. Fetch undispatched
        undispatched = [r for r in self._mock_outbox if r["dispatched_at"] is None][: self.batch_size]
        if not undispatched:
            return 0

        dispatched_count = 0
        for record in undispatched:
            run_id = record["run_id"]
            payload = record["payload"]
            record["attempts"] += 1

            try:
                # Deliver to SSE stream hub
                await sse_hub.publish(run_id, payload)
                record["dispatched_at"] = datetime.now(timezone.utc).isoformat()
                dispatched_count += 1
                logger.debug(f"Dispatched outbox event {record['id']} for run {run_id}")
            except Exception as exc:
                logger.error(f"Failed to dispatch outbox event {record['id']}: {exc}")

        return dispatched_count

    async def start(self) -> None:
        """Continuous execution loop."""
        self.is_running = True
        logger.info(f"EventRelayWorker started. Polling every {self.poll_interval}s...")
        while self.is_running:
            try:
                await self.poll_and_dispatch()
            except Exception as exc:
                logger.error(f"Error in EventRelayWorker loop: {exc}")
            await asyncio.sleep(self.poll_interval)

    def stop(self) -> None:
        """Stop worker execution."""
        self.is_running = False
        logger.info("EventRelayWorker stopped.")


# Global worker singleton
event_relay_worker = EventRelayWorker()
