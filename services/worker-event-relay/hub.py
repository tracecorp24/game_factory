"""
SSE Event Broadcasting Hub and Replay Manager.
Maintains client subscriptions per run_id, handles catch-up replay via Last-Event-ID / since_seq,
and formats SSE wire responses conforming to Master Plan Section J.
CreativeForge Intelligence Studio v3.0 - Module M06 / M11.
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, List, Optional, Set

logger = logging.getLogger("worker_event_relay.hub")


class SSEHub:
    """In-memory event broadcaster and SSE stream manager per run_id."""

    def __init__(self):
        # run_id -> Set of asyncio.Queue instances (one per connected SSE client)
        self._subscribers: Dict[str, Set[asyncio.Queue[Dict[str, Any]]]] = {}
        # run_id -> List of recorded event dicts (sorted by run_seq)
        self._event_store: Dict[str, List[Dict[str, Any]]] = {}
        self._lock = asyncio.Lock()

    def record_event(self, run_id: str, event: Dict[str, Any]) -> None:
        """Store event in the historical buffer for catch-up replay."""
        if run_id not in self._event_store:
            self._event_store[run_id] = []
        
        # Ensure run_seq exists
        if "run_seq" not in event:
            event["run_seq"] = len(self._event_store[run_id]) + 1
        
        self._event_store[run_id].append(event)
        # Keep sorted by run_seq
        self._event_store[run_id].sort(key=lambda x: x.get("run_seq", 0))

    def get_historical_events(self, run_id: str, since_seq: int = 0) -> List[Dict[str, Any]]:
        """Retrieve historical events with run_seq > since_seq."""
        events = self._event_store.get(run_id, [])
        return [evt for evt in events if evt.get("run_seq", 0) > since_seq]

    async def publish(self, run_id: str, event: Dict[str, Any]) -> int:
        """Publish an event to all active SSE subscribers for this run_id."""
        self.record_event(run_id, event)
        subscribers = self._subscribers.get(run_id, set())
        delivered = 0

        for queue in list(subscribers):
            try:
                queue.put_nowait(event)
                delivered += 1
            except asyncio.QueueFull:
                logger.warning(f"Subscriber queue full for run {run_id}; dropping slow client message.")
            except Exception as exc:
                logger.error(f"Error publishing to subscriber: {exc}")

        return delivered

    def format_sse_message(self, run_id: str, event: Dict[str, Any]) -> str:
        """
        Format event conforming to strict SSE wire format:
        id: <run_id>:<run_seq>
        event: <event_type>
        data: <json_string>

        """
        run_seq = event.get("run_seq", 0)
        event_type = event.get("event_type", "MESSAGE")
        
        # Data payload can be whole event or inner payload
        payload = event.get("payload_preview") or event
        data_json = json.dumps(payload, default=str)

        return f"id: {run_id}:{run_seq}\nevent: {event_type}\ndata: {data_json}\n\n"

    def parse_last_event_id(self, last_event_id: Optional[str]) -> Optional[int]:
        """Parse run_seq out of 'run_id:seq' or numeric string."""
        if not last_event_id:
            return None
        try:
            if ":" in last_event_id:
                parts = last_event_id.split(":")
                return int(parts[-1])
            return int(last_event_id)
        except (ValueError, TypeError):
            return None

    async def stream_run_events(
        self,
        run_id: str,
        since_seq: Optional[int] = None,
        last_event_id: Optional[str] = None,
        keepalive_interval: float = 15.0,
    ) -> AsyncGenerator[str, None]:
        """
        Stream events for a run as an AsyncGenerator yielding SSE wire-formatted strings.
        Supports replay from since_seq or Last-Event-ID header.
        """
        # Determine starting sequence
        effective_since = 0
        parsed_id_seq = self.parse_last_event_id(last_event_id)
        if since_seq is not None:
            effective_since = since_seq
        elif parsed_id_seq is not None:
            effective_since = parsed_id_seq

        # 1. Catch-up Replay: stream missed historical events in order
        history = self.get_historical_events(run_id, since_seq=effective_since)
        for past_event in history:
            yield self.format_sse_message(run_id, past_event)

        # 2. Register real-time subscriber queue
        queue: asyncio.Queue[Dict[str, Any]] = asyncio.Queue(maxsize=500)
        async with self._lock:
            if run_id not in self._subscribers:
                self._subscribers[run_id] = set()
            self._subscribers[run_id].add(queue)

        try:
            while True:
                try:
                    # Wait for next event or send ping keepalive
                    event = await asyncio.wait_for(queue.get(), timeout=keepalive_interval)
                    yield self.format_sse_message(run_id, event)
                except asyncio.TimeoutError:
                    # Send standard SSE keepalive comment
                    yield f": ping {datetime.now(timezone.utc).isoformat()}\n\n"
        finally:
            # Unregister on disconnect
            async with self._lock:
                if run_id in self._subscribers and queue in self._subscribers[run_id]:
                    self._subscribers[run_id].remove(queue)
                    if not self._subscribers[run_id]:
                        del self._subscribers[run_id]


# Global singleton SSE hub
sse_hub = SSEHub()
