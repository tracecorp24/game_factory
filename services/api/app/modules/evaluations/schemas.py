"""
Pydantic schemas for the Evaluations API module.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from services.worker_evaluation.gates.base import GateResult, GateStatus, GateSeverity
from services.worker_evaluation.models import OverallVerdict, EvaluationReport


class EvaluateArtifactRequest(BaseModel):
    """Request payload to initiate a 7-Gate evaluation on an artifact."""
    artifact_id: str
    run_id: str
    target_type: str = Field(default="image", description="image, video, playable_zip, concept_board")
    storage_ref: Optional[str] = None
    media_meta: Dict[str, Any] = Field(default_factory=dict)
    game_dna: Optional[Dict[str, Any]] = None
    creative_hypothesis: Optional[Dict[str, Any]] = None
    playwright_report: Optional[Dict[str, Any]] = None
    rubric_id: Optional[str] = "rubric_mobile_ad_v3"
    options: Dict[str, Any] = Field(default_factory=dict)


class HumanReviewSubmission(BaseModel):
    """Payload when human reviewer submits an approval or rejection."""
    artifact_id: str
    reviewer_id: str
    decision: str = Field(description="'approved' or 'rejected'")
    reason: str = Field(description="Detailed reason or feedback for decision")
    rubric_feedback: Optional[Dict[str, float]] = None


class RubricCriterionSchema(BaseModel):
    id: str
    name: str
    weight: float
    description: str


class RubricDefinitionSchema(BaseModel):
    rubric_id: str
    name: str
    version: str
    target_types: List[str]
    pass_threshold: float = 3.0
    criteria: List[RubricCriterionSchema]
    golden_prompt_id: Optional[str] = None
