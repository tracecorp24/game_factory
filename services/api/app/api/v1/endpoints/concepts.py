"""
Creative Concepts, Hypotheses and User Decisions REST API endpoints.
Connected directly to ConceptService, IdeationAgent, and ConceptRankingEngine.
CreativeForge Intelligence Studio v3.0 - Section J & Module M02.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.api.app.modules.concepts.service import ConceptService
from services.api.app.modules.concepts.models import DecisionAction
from services.api.app.modules.game_dna.service import GameProfileService
from services.api.app.modules.game_dna.models import MechanicGenre
from services.worker_trends.models import TrendReport, TrendSignal

router = APIRouter(prefix="", tags=["Concepts & Hypotheses"])

# Shared singleton service instance
concept_service = ConceptService()
game_profile_service = GameProfileService()

# Seed default baseline profile for immediate generation
_default_profile = game_profile_service.create_profile_from_preset(
    project_id="proj_default",
    genre=MechanicGenre.MATCH_3,
    name="Gem Rush",
)
game_profile_service.freeze_version(_default_profile.version_id)

_CONCEPTS_LEGACY_CACHE: Dict[str, Dict[str, Any]] = {
    "cpt_gem_combo_01": {
        "id": "cpt_gem_combo_01",
        "project_id": "proj_gem_rush",
        "title": "Chain Reaction Cascade",
        "intended_hook": "Can you trigger a 5-gem rainbow blast?",
        "emotional_arc": "Curiosity -> Anticipation -> Joyful Blast",
        "creative_mechanism": "Cascading Match-3 with explosive combo particle feedback",
        "heuristic_score": 0.88,
        "score_breakdown": {
            "evidence": 0.90,
            "game_fit": 0.95,
            "novelty": 0.80,
            "feasibility": 0.90,
            "hook_clarity": 0.85,
            "cost_fit": 0.85,
        },
        "state": "pending",
    }
}


class ConceptGenerateRequest(BaseModel):
    game_profile_version_id: Optional[str] = None
    target_count: int = Field(default=3, ge=1, le=8)
    audience_segment: Optional[str] = "Puzzle Enthusiasts"


class ConceptDecisionRequest(BaseModel):
    user_id: str = "usr_lead_creative"
    decision: str = Field(..., description="'select', 'reject', or 'regenerate'")
    reason: str = Field(..., description="Actionable justification for this decision")


@router.post("/projects/{project_id}/concepts/generate", status_code=201)
async def generate_concepts(project_id: str, payload: ConceptGenerateRequest):
    """Generate 3 to 8 creative hypotheses and concept mockup boards."""
    # Resolve Game Profile
    profile = None
    if payload.game_profile_version_id:
        profile = game_profile_service.get_version(payload.game_profile_version_id)
    if not profile:
        profile = _default_profile

    # Synthetic or empty trend report
    trend_report = TrendReport(signals=[])

    # Generate and rank concept boards
    boards = await concept_service.generate_and_rank_concepts_async(
        trend_report=trend_report,
        profile_version=profile,
        count=payload.target_count,
        target_audience=payload.audience_segment,
    )

    generated = []
    for b in boards:
        c_dict = {
            "id": b.concept_id,
            "board_id": b.board_id,
            "project_id": project_id,
            "title": b.hypothesis.title,
            "intended_hook": b.hook_frame.headline_text,
            "emotional_arc": b.hypothesis.emotional_arc,
            "creative_mechanism": b.hypothesis.creative_mechanism,
            "heuristic_score": b.ranking.composite_score,
            "score_breakdown": b.ranking.dimension_scores.model_dump(),
            "is_calibrated": b.ranking.is_calibrated,
            "disclaimer": b.ranking.disclaimer,
            "state": "pending",
            "scene_layout": b.scene_layout.model_dump(),
            "falsification_condition": b.hypothesis.falsification_condition,
            "primary_metric": b.hypothesis.primary_metric.value,
        }
        _CONCEPTS_LEGACY_CACHE[b.concept_id] = c_dict
        generated.append(c_dict)

    return {"project_id": project_id, "concepts": generated}


@router.get("/projects/{project_id}/concepts")
async def list_concepts(project_id: str):
    """List generated concepts for a project."""
    return [c for c in _CONCEPTS_LEGACY_CACHE.values() if c.get("project_id") == project_id]


@router.post("/concepts/{concept_id}/decision")
async def record_concept_decision(concept_id: str, payload: ConceptDecisionRequest):
    """Record a user decision (select, reject, regenerate) with rationale."""
    if not payload.reason or not payload.reason.strip():
        raise HTTPException(status_code=400, detail="Decision requires a mandatory justification reason.")

    # Convert to enum
    action_map = {
        "select": DecisionAction.SELECT,
        "reject": DecisionAction.REJECT,
        "regenerate": DecisionAction.REGENERATE,
    }
    action = action_map.get(payload.decision.lower())
    if not action:
        raise HTTPException(status_code=400, detail=f"Invalid decision '{payload.decision}'. Must be select, reject, or regenerate.")

    try:
        # If in ConceptService store
        board = concept_service.get_board(concept_id)
        if board:
            dec = concept_service.record_user_decision(
                concept_id=concept_id,
                action=action,
                reason=payload.reason,
                actor=payload.user_id,
            )
            return {
                "concept_id": concept_id,
                "status": "decision_recorded",
                "decision": dec.action.value,
                "reason": dec.reason,
                "event_type": dec.event_type,
            }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    # Backward compatibility with legacy cache
    if concept_id in _CONCEPTS_LEGACY_CACHE:
        concept = _CONCEPTS_LEGACY_CACHE[concept_id]
        concept["state"] = payload.decision
        concept["decision_record"] = {
            "user_id": payload.user_id,
            "decision": payload.decision,
            "reason": payload.reason,
            "decided_at": "2026-10-25T12:00:00Z",
        }
        return {
            "concept_id": concept_id,
            "status": "decision_recorded",
            "decision": payload.decision,
            "reason": payload.reason,
        }

    raise HTTPException(status_code=404, detail="Concept not found")
