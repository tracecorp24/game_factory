"""
Runs, Control Signals and Reproducibility Manifest REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J, Modules M10 & M11.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Runs & Controls"])

_RUNS: Dict[str, Dict[str, Any]] = {
    "run_demo_01": {
        "id": "run_demo_01",
        "workflow_version_id": "wf_standard_pipeline_v1",
        "state": "completed",
        "started_at": "2026-10-25T11:00:00Z",
        "ended_at": "2026-10-25T11:01:15Z",
        "run_manifest_id": "man_run_demo_01",
    }
}

_MANIFESTS: Dict[str, Dict[str, Any]] = {
    "man_run_demo_01": {
        "id": "man_run_demo_01",
        "run_id": "run_demo_01",
        "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "workflow_version_id": "wf_standard_pipeline_v1",
        "game_profile_version_id": "game_gem_rush_v1",
        "code_commit": "cf3a910",
        "frozen_parameters": {"seed": 42, "temperature": 0.7},
    }
}


class RunCreate(BaseModel):
    brief_input: Optional[Dict[str, Any]] = None
    budget_limit_usd: Optional[float] = 10.0


@router.post("/workflows/{workflow_id}/runs", status_code=201)
async def start_run(workflow_id: str, payload: RunCreate):
    """Start a new workflow execution and lock immutable RunManifest."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    manifest_id = f"man_{run_id}"

    manifest = {
        "id": manifest_id,
        "run_id": run_id,
        "sha256": uuid.uuid4().hex + uuid.uuid4().hex,
        "workflow_version_id": f"{workflow_id}_v1",
        "code_commit": "git-head",
        "frozen_parameters": payload.brief_input or {},
    }
    _MANIFESTS[manifest_id] = manifest

    run_record = {
        "id": run_id,
        "workflow_version_id": f"{workflow_id}_v1",
        "state": "running",
        "started_at": "2026-10-25T12:00:00Z",
        "ended_at": None,
        "run_manifest_id": manifest_id,
    }
    _RUNS[run_id] = run_record
    return run_record


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get current run state and metadata."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    return _RUNS[run_id]


@router.post("/runs/{run_id}/pause")
async def pause_run(run_id: str):
    """Pause an active workflow run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    _RUNS[run_id]["state"] = "paused"
    return {"run_id": run_id, "state": "paused"}


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str):
    """Resume a paused workflow run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    _RUNS[run_id]["state"] = "running"
    return {"run_id": run_id, "state": "running"}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    """Cancel an active or paused run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    _RUNS[run_id]["state"] = "cancelled"
    return {"run_id": run_id, "state": "cancelled"}


@router.post("/runs/{run_id}/rerun")
async def rerun_run(run_id: str):
    """Idempotent rerun / retry failed node executions."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    _RUNS[run_id]["state"] = "running"
    return {"run_id": run_id, "state": "running", "action": "rerun_initiated"}


@router.get("/runs/{run_id}/manifest")
async def get_run_manifest(run_id: str):
    """Get frozen reproducibility manifest for this run."""
    run = _RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    manifest_id = run.get("run_manifest_id")
    if manifest_id not in _MANIFESTS:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return _MANIFESTS[manifest_id]


@router.get("/runs/{run_id}/export")
async def export_run_bundle(run_id: str):
    """Export complete reproducible bundle for the run."""
    run = _RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run": run,
        "manifest": _MANIFESTS.get(run.get("run_manifest_id")),
        "exported_at": "2026-10-25T12:00:00Z",
    }
