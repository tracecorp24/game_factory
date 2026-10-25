"""
Events and Real-Time SSE Stream REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J, Modules M06 & M11.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from services.worker_event_relay.hub import sse_hub

router = APIRouter(prefix="", tags=["Events & Real-Time Stream"])


class EventPublishRequest(BaseModel):
    event_type: str = Field(..., examples=["NODE_STARTED"])
    run_seq: Optional[int] = None
    node_execution_id: Optional[str] = None
    attempt_id: Optional[str] = None
    status: Optional[str] = "running"
    payload_preview: Dict[str, Any] = Field(default_factory=dict)


@router.get("/runs/{run_id}/events")
async def get_run_events(
    run_id: str,
    since_seq: int = Query(default=0, ge=0, description="Return events strictly greater than this sequence number"),
):
    """Query historical events for a run with monotonic sequence filtering."""
    events = sse_hub.get_historical_events(run_id, since_seq=since_seq)
    return {"run_id": run_id, "since_seq": since_seq, "count": len(events), "events": events}


@router.post("/runs/{run_id}/events", status_code=201)
async def publish_event(run_id: str, payload: EventPublishRequest):
    """Publish an event to the run's SSE stream and persistent store."""
    event_dict = payload.model_dump()
    event_dict["run_id"] = run_id
    if not event_dict.get("payload_preview"):
        event_dict["payload_preview"] = {
            "node_execution_id": payload.node_execution_id,
            "status": payload.status,
        }
    await sse_hub.publish(run_id, event_dict)
    return {"run_id": run_id, "status": "event_published", "event_type": payload.event_type}


@router.get("/runs/{run_id}/events/stream")
async def stream_run_events(
    run_id: str,
    request: Request,
    since_seq: Optional[int] = Query(default=None, description="Sequence number to replay missed events from"),
    last_event_id: Optional[str] = Header(default=None, alias="Last-Event-ID"),
):
    """
    Live Server-Sent Events (SSE) stream for real-time Agent Observatory & Workflow updates.
    Conforms to Master Plan Section J wire format:
    id: <run_id>:<run_seq>
    event: <event_type>
    data: <json_string>

    Supports seamless reconnection without event loss via 'Last-Event-ID' header or 'since_seq' query parameter.
    """
    generator = sse_hub.stream_run_events(
        run_id=run_id,
        since_seq=since_seq,
        last_event_id=last_event_id,
        keepalive_interval=10.0,
    )

    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
