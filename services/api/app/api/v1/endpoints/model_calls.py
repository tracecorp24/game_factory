"""
Model Invocations and LLM Call Telemetry REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J & Module M09.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="", tags=["Model Calls"])

_MODEL_CALLS: Dict[str, Dict[str, Any]] = {
    "call_88_01": {
        "id": "call_88_01",
        "run_id": "run_demo_01",
        "attempt_id": "att_01",
        "provider": "openai",
        "model_requested": "gpt-4o",
        "model_resolved": "gpt-4o-2024-08-06",
        "provider_request_id": "chatcmpl-94812",
        "state": "completed",
        "tokens": {
            "input_tokens": 1420,
            "output_tokens": 580,
            "cached_tokens": 400,
            "usage_source": "provider_reported",
        },
        "cost": {
            "amount": 0.0185,
            "currency": "USD",
            "status": "actual",
        },
        "timing": {
            "started_at": "2026-10-25T11:00:05Z",
            "ended_at": "2026-10-25T11:00:07Z",
            "latency_ms": 2150,
        },
    }
}


@router.get("/runs/{run_id}/model-calls")
async def list_run_model_calls(run_id: str):
    """List all LLM and image/video model invocations for a run."""
    return [c for c in _MODEL_CALLS.values() if c.get("run_id") == run_id]


@router.get("/model-calls/{call_id}")
async def get_model_call(call_id: str):
    """Get full metadata, token usage, and cost for a single model call."""
    if call_id not in _MODEL_CALLS:
        raise HTTPException(status_code=404, detail="Model call not found")
    return _MODEL_CALLS[call_id]
