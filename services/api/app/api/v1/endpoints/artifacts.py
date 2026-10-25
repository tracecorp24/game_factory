"""
Artifacts, Lineage, Quality Gate Evaluation and Human Review REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J & Module M07.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.api.app.modules.evaluations.schemas import (
    EvaluateArtifactRequest,
    HumanReviewSubmission,
)
from services.api.app.modules.evaluations.service import evaluation_service

router = APIRouter(prefix="", tags=["Artifacts & QA Evaluation"])

_ARTIFACTS: Dict[str, Dict[str, Any]] = {
    "art_sample_001": {
        "id": "art_sample_001",
        "run_id": "run_demo_01",
        "type": "image",
        "storage_ref": "data/storage/art_sample_001.png",
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "bytes": 524288,
        "media_meta": {
            "width": 1080,
            "height": 1920,
            "format": "PNG",
            "cta_text": "Play Now",
            "contrast_ratio": 5.4,
        },
        "state": "approved",
    }
}

_LINEAGE: Dict[str, List[Dict[str, Any]]] = {
    "art_sample_001": [
        {"parent_artifact_id": "cpt_gem_combo_01", "relation_type": "derived_from"}
    ]
}


class PreviewTicketResponse(BaseModel):
    artifact_id: str
    preview_url: str
    expires_at: str
    ticket_token: str


@router.get("/runs/{run_id}/artifacts")
async def list_run_artifacts(run_id: str):
    """List all generated creative artifacts for a run."""
    return [a for a in _ARTIFACTS.values() if a.get("run_id") == run_id]


@router.get("/artifacts/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get artifact details, checksum, and media metadata."""
    if artifact_id not in _ARTIFACTS:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return _ARTIFACTS[artifact_id]


@router.get("/artifacts/{artifact_id}/lineage")
async def get_artifact_lineage(artifact_id: str):
    """Get the DAG lineage and parent artifacts for this creative asset."""
    if artifact_id not in _ARTIFACTS:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return {
        "artifact_id": artifact_id,
        "lineage": _LINEAGE.get(artifact_id, []),
    }


@router.post("/artifacts/{artifact_id}/preview-ticket", response_model=PreviewTicketResponse)
async def generate_preview_ticket(artifact_id: str):
    """Generate a time-limited secure preview URL for private artifact rendering."""
    if artifact_id not in _ARTIFACTS:
        raise HTTPException(status_code=404, detail="Artifact not found")
    ticket = uuid.uuid4().hex
    return PreviewTicketResponse(
        artifact_id=artifact_id,
        preview_url=f"/preview/{artifact_id}?ticket={ticket}",
        expires_at="2026-10-25T14:00:00Z",
        ticket_token=ticket,
    )


@router.post("/artifacts/{artifact_id}/evaluate")
async def evaluate_artifact_endpoint(artifact_id: str, payload: EvaluateArtifactRequest):
    """Trigger the 7-Layer Quality Gate pipeline on an artifact."""
    if payload.artifact_id != artifact_id:
        payload.artifact_id = artifact_id
    report = await evaluation_service.evaluate_artifact(payload)
    return report


@router.post("/artifacts/{artifact_id}/review")
async def review_artifact_endpoint(artifact_id: str, payload: HumanReviewSubmission):
    """Submit human review decision (approved or rejected with mandatory reason)."""
    if payload.artifact_id != artifact_id:
        payload.artifact_id = artifact_id
    result = await evaluation_service.record_human_review(payload)
    if artifact_id in _ARTIFACTS:
        _ARTIFACTS[artifact_id]["state"] = payload.decision.lower()
    return result


@router.get("/quality/gates")
async def list_quality_gates():
    """List the 7 Quality Gates and standard rubrics."""
    return {
        "gates": [
            {"name": "schema_gate", "order": 1, "fatal": True, "description": "Schema, required fields and SHA256 integrity."},
            {"name": "technical_gate", "order": 2, "fatal": True, "description": "Playwright zero runtime JS error policy and size bounds."},
            {"name": "game_truth_gate", "order": 3, "fatal": False, "description": "Mechanics alignment and misleading ad claim prevention."},
            {"name": "visual_gate", "order": 4, "fatal": False, "description": "Aspect ratio (9:16), resolution, contrast and CTA readability."},
            {"name": "similarity_gate", "order": 5, "fatal": False, "description": "Perceptual hash and cosine embedding similarity checks."},
            {"name": "llm_judge_gate", "order": 6, "fatal": False, "description": "Rubric-based 0-5 scored evaluation with golden references."},
            {"name": "human_review_gate", "order": 7, "fatal": False, "description": "Human-in-the-loop sign-off for ambiguous/critical assets."},
        ],
        "rubrics": evaluation_service.get_all_rubrics(),
    }


@router.get("/quality/pending-reviews")
async def list_pending_reviews():
    """List artifacts awaiting human QA decision."""
    return evaluation_service.get_pending_reviews()
