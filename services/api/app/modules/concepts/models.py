"""
Creative Hypothesis, Ranking, and Concept Board Data Models (Pydantic v2).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator


class PrimaryMetric(str, Enum):
    CTR = "CTR"
    IPM = "IPM"
    CPI_REDUCTION = "CPI_reduction"


class CreativeHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: Optional[str] = None
    game_profile_version_id: str
    title: str
    audience: str
    genre: str
    intended_hook: str
    emotional_arc: str
    evidence_refs: List[str] = Field(default_factory=list)
    creative_mechanism: str
    primary_metric: PrimaryMetric = PrimaryMetric.IPM
    falsification_condition: str
    limitations: List[str] = Field(default_factory=list)
    novelty_rationale: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_hash: str = ""

    def calculate_hash(self) -> str:
        raw = f"{self.hypothesis_id}:{self.title}:{self.intended_hook}:{self.creative_mechanism}:{self.falsification_condition}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if not self.content_hash:
            self.content_hash = self.calculate_hash()


class RankingWeights(BaseModel):
    """
    Standard formula weights from Master Plan:
    Score = 0.25*evidence + 0.20*game_fit + 0.20*novelty + 0.15*feasibility + 0.10*hook_clarity + 0.10*cost_fit
    """
    evidence: float = Field(default=0.25, ge=0.0, le=1.0)
    game_fit: float = Field(default=0.20, ge=0.0, le=1.0)
    novelty: float = Field(default=0.20, ge=0.0, le=1.0)
    feasibility: float = Field(default=0.15, ge=0.0, le=1.0)
    hook_clarity: float = Field(default=0.10, ge=0.0, le=1.0)
    cost_fit: float = Field(default=0.10, ge=0.0, le=1.0)

    @field_validator("cost_fit")
    @classmethod
    def validate_sum_to_one(cls, v: float, info: Any) -> float:
        data = info.data
        total = round(
            data.get("evidence", 0.25)
            + data.get("game_fit", 0.20)
            + data.get("novelty", 0.20)
            + data.get("feasibility", 0.15)
            + data.get("hook_clarity", 0.10)
            + v,
            3,
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Ranking weights must sum to 1.0 (current sum: {total})")
        return v


class RankingDimensionScores(BaseModel):
    evidence: float = Field(ge=0.0, le=1.0)
    game_fit: float = Field(ge=0.0, le=1.0)
    novelty: float = Field(ge=0.0, le=1.0)
    feasibility: float = Field(ge=0.0, le=1.0)
    hook_clarity: float = Field(ge=0.0, le=1.0)
    cost_fit: float = Field(ge=0.0, le=1.0)


class RankingEvaluation(BaseModel):
    composite_score: float = Field(ge=0.0, le=1.0)
    dimension_scores: RankingDimensionScores
    weights_applied: RankingWeights
    is_calibrated: bool = False
    disclaimer: str = (
        "Heuristic scoring metric for ideation prioritization; "
        "not calibrated real-world CTR/performance probability."
    )
    primary_strength: str = ""
    primary_risk: str = ""
    rationale: str = ""


class SceneLayoutSpec(BaseModel):
    layout_type: str = "vertical_9_16"
    grid_placement: str = "center_lower_half"
    character_placement: str = "top_left_reaction_cam"
    hud_spec: Dict[str, Any] = Field(
        default_factory=lambda: {
            "top_bar": "Level progress, move counter, score star meter",
            "bottom_bar": "Interactive booster tray with pulsing highlights",
        }
    )
    visual_effects: List[str] = Field(
        default_factory=lambda: ["particle_sparkles_on_match", "screen_shake_on_combo", "floating_text_score"]
    )


class HookFrameSpec(BaseModel):
    duration_seconds: float = 3.0
    headline_text: str
    headline_style: str = "High-contrast yellow text, black border, bouncing entry"
    audio_cue: str = "Satisfying pop + dramatic attention chime"
    interaction_cue: str = "Pulsing animated tutorial finger guiding first swipe"


class ConceptBoard(BaseModel):
    board_id: str = Field(default_factory=lambda: str(uuid4()))
    concept_id: str = Field(default_factory=lambda: str(uuid4()))
    hypothesis: CreativeHypothesis
    scene_layout: SceneLayoutSpec = Field(default_factory=SceneLayoutSpec)
    hook_frame: HookFrameSpec
    ranking: RankingEvaluation
    preview_asset_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DecisionAction(str, Enum):
    SELECT = "select"
    REJECT = "reject"
    REGENERATE = "regenerate"


class ConceptDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid4()))
    concept_id: str
    board_id: str
    action: DecisionAction
    actor: str = "user"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reason: str
    workflow_override_params: Dict[str, Any] = Field(default_factory=dict)
    event_type: str = "CONCEPT_SELECTED"
