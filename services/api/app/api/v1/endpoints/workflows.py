"""
Workflows and Versioning REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Workflows"])

_WORKFLOWS: Dict[str, Dict[str, Any]] = {
    "wf_standard_pipeline": {
        "id": "wf_standard_pipeline",
        "project_id": "proj_gem_rush",
        "name": "Standard Mobile Ad Generation & QA Pipeline",
        "active_version_id": "wf_standard_pipeline_v1",
        "versions": ["wf_standard_pipeline_v1"],
    }
}

_WORKFLOW_VERSIONS: Dict[str, Dict[str, Any]] = {
    "wf_standard_pipeline_v1": {
        "id": "wf_standard_pipeline_v1",
        "workflow_id": "wf_standard_pipeline",
        "version": 1,
        "is_published": True,
        "graph_json": {
            "nodes": [
                {"id": "node_fetch", "type": "Source Fetch"},
                {"id": "node_genre", "type": "Genre Classifier"},
                {"id": "node_pattern", "type": "Ad Pattern Extract"},
                {"id": "node_synthesis", "type": "Trend Synthesis"},
            ],
            "edges": [
                {"source": "node_fetch", "target": "node_genre", "source_handle": "snapshot", "target_handle": "snapshot"},
                {"source": "node_fetch", "target": "node_pattern", "source_handle": "snapshot", "target_handle": "creative_evidence"},
                {"source": "node_genre", "target": "node_synthesis", "source_handle": "genre_report", "target_handle": "genre_report"},
                {"source": "node_pattern", "target": "node_synthesis", "source_handle": "pattern_report", "target_handle": "pattern_report"},
            ],
        },
        "sha256": "8a329fa5a932bce26fec918da294c79c5cbb702e53ef711b6ff7b7f14b62fef9",
        "published_at": "2026-10-25T10:00:00Z",
    }
}


class WorkflowCreate(BaseModel):
    project_id: str
    name: str


class WorkflowDraftUpdate(BaseModel):
    graph_json: Dict[str, Any]


@router.post("/workflows", status_code=201)
async def create_workflow(payload: WorkflowCreate):
    """Create a new workflow container."""
    wid = f"wf_{uuid.uuid4().hex[:8]}"
    wf = {
        "id": wid,
        "project_id": payload.project_id,
        "name": payload.name,
        "active_version_id": None,
        "versions": [],
    }
    _WORKFLOWS[wid] = wf
    return wf


@router.get("/workflows")
async def list_workflows(project_id: Optional[str] = None):
    """List workflows, optionally filtered by project."""
    if project_id:
        return [w for w in _WORKFLOWS.values() if w.get("project_id") == project_id]
    return list(_WORKFLOWS.values())


@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow metadata and published versions."""
    if workflow_id not in _WORKFLOWS:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _WORKFLOWS[workflow_id]


@router.put("/workflows/{workflow_id}/draft")
async def update_workflow_draft(workflow_id: str, payload: WorkflowDraftUpdate):
    """Update draft DAG graph of the workflow."""
    if workflow_id not in _WORKFLOWS:
        raise HTTPException(status_code=404, detail="Workflow not found")
    _WORKFLOWS[workflow_id]["draft_graph"] = payload.graph_json
    return {"workflow_id": workflow_id, "status": "draft_updated"}


@router.post("/workflows/{workflow_id}/publish")
async def publish_workflow(workflow_id: str):
    """Freeze draft DAG into an immutable, versioned workflow specification."""
    if workflow_id not in _WORKFLOWS:
        raise HTTPException(status_code=404, detail="Workflow not found")

    wf = _WORKFLOWS[workflow_id]
    next_ver = len(wf.get("versions", [])) + 1
    vid = f"{workflow_id}_v{next_ver}"

    graph = wf.get("draft_graph", {"nodes": [], "edges": []})
    version_record = {
        "id": vid,
        "workflow_id": workflow_id,
        "version": next_ver,
        "is_published": True,
        "graph_json": graph,
        "sha256": uuid.uuid4().hex + uuid.uuid4().hex,
        "published_at": "2026-10-25T12:00:00Z",
    }
    _WORKFLOW_VERSIONS[vid] = version_record
    wf["active_version_id"] = vid
    wf.setdefault("versions", []).append(vid)
    return version_record
