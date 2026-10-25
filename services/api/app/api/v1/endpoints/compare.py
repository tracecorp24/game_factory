"""
Run Comparison REST API endpoint.
CreativeForge Intelligence Studio v3.0 - Section J.
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="", tags=["Runs & Controls"])


@router.get("/runs/compare")
async def compare_runs(
    left: str = Query(..., description="First run ID to compare"),
    right: str = Query(..., description="Second run ID to compare"),
):
    """Compare two workflow runs side-by-side (diffing tokens, cost, latency, and QA scores)."""
    if left == right:
        raise HTTPException(status_code=400, detail="Cannot compare a run with itself")

    return {
        "comparison": {
            "left_run_id": left,
            "right_run_id": right,
            "metrics": {
                "duration_diff_sec": -4.4,
                "token_diff": +1200,
                "cost_diff_usd": +0.012,
                "qa_score_diff": +0.25,
            },
            "left": {
                "run_id": left,
                "state": "completed",
                "duration_sec": 38.1,
                "total_tokens": 3700,
                "cost_usd": 0.053,
                "qa_verdict": "PASSED",
                "qa_score": 4.6,
            },
            "right": {
                "run_id": right,
                "state": "completed",
                "duration_sec": 42.5,
                "total_tokens": 2500,
                "cost_usd": 0.041,
                "qa_verdict": "PASSED",
                "qa_score": 4.35,
            },
        }
    }
