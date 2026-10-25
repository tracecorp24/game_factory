"""
Execution Attempts and Retry History REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J & Module M11.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter

router = APIRouter(prefix="", tags=["Attempts & Retries"])

_ATTEMPTS: Dict[str, Dict[str, Any]] = {
    "att_01": {
        "id": "att_01",
        "run_id": "run_demo_01",
        "node_execution_id": "ne_video_render",
        "attempt_no": 1,
        "state": "completed",
        "error_code": None,
        "backoff_ms": 0,
        "started_at": "2026-10-25T11:00:10Z",
        "ended_at": "2026-10-25T11:00:15Z",
    }
}


@router.get("/runs/{run_id}/attempts")
async def list_run_attempts(run_id: str):
    """List execution attempts and retry backoffs for all nodes in a run."""
    return [a for a in _ATTEMPTS.values() if a.get("run_id") == run_id]
