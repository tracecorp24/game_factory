"""
Master Plan Section H - Typed Artifact Contracts for CreativeForge Intelligence Studio v3.0.
Every artifact has schema_version, content hashes, and structured domain types.
"""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import Field

from packages.contracts.common import BaseContractModel, generate_uuid, utc_now


ConfidenceLevel = Literal["low", "medium", "high"]


class TrendSnapshot(BaseContractModel):
    """M01 - Raw scraped/imported trend snapshot."""
    snapshot_id: str = Field(default_factory=generate_uuid)
    source_id: str = Field(...)
    observed_at: datetime = Field(default_factory=utc_now)
    region: str = Field(default="global")
    records: List[Dict[str, Any]] = Field(default_factory=list)
    raw_hash: str = Field(...)
    schema_version: int = Field(default=1)


class TrendReport(BaseContractModel):
    """M01 - Synthesized trend intelligence report with evidence linking."""
    report_id: str = Field(default_factory=generate_uuid)
    project_id: str = Field(...)
    signals: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    confidence: ConfidenceLevel = Field(default="medium")
    limitations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    schema_version: int = Field(default=1)


class GameProfileVersion(BaseContractModel):
    """M04 - Frozen game DNA profile version enforcing mechanics & brand truth."""
    profile_id: str = Field(...)
    version: int = Field(..., ge=1)
    mechanics: Dict[str, Any] = Field(..., description="Mechanics spec, grid rules, boosters, objectives")
    style: Dict[str, Any] = Field(..., description="Visual style tokens, color palette, lighting")
    assets: Dict[str, Any] = Field(default_factory=dict, description="Character refs, environment, UI symbols")
    constraints: Dict[str, Any] = Field(
        default_factory=dict,
        description="Brand constraints, do_not_generate rules, allowed_ad_claims"
    )
    approved_at: Optional[datetime] = Field(default=None)
    hash: str = Field(..., description="SHA256 of frozen profile spec")
    schema_version: int = Field(default=1)


class CreativeHypothesis(BaseContractModel):
    """M02 - Structured creative hypothesis for ad concept ideation."""
    hypothesis_id: str = Field(default_factory=generate_uuid)
    project_id: str = Field(...)
    audience: str = Field(...)
    genre: str = Field(...)
    intended_hook: str = Field(...)
    emotional_arc: str = Field(...)
    evidence_refs: List[str] = Field(default_factory=list)
    creative_mechanism: str = Field(...)
    primary_metric: str = Field(default="CTR")
    falsification_condition: str = Field(...)
    limitations: List[str] = Field(default_factory=list)
    novelty_rationale: str = Field(...)
    ranking_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    score_components: Dict[str, float] = Field(default_factory=dict)
    schema_version: int = Field(default=1)


class ConceptSpec(BaseContractModel):
    """M02 - Detailed creative specification for asset production."""
    concept_id: str = Field(default_factory=generate_uuid)
    hypothesis_id: str = Field(...)
    scene: Dict[str, Any] = Field(...)
    interaction: Dict[str, Any] = Field(...)
    style: Dict[str, Any] = Field(...)
    target_formats: List[str] = Field(default_factory=lambda: ["9:16", "1:1"])
    schema_version: int = Field(default=1)


class ConceptBoard(BaseContractModel):
    """M02 - Concept board presentation card with layout and score."""
    board_id: str = Field(default_factory=generate_uuid)
    concept_id: str = Field(...)
    preview_asset_id: Optional[str] = Field(default=None)
    score_components: Dict[str, float] = Field(default_factory=dict)
    layout: Dict[str, Any] = Field(default_factory=dict)
    schema_version: int = Field(default=1)


class ContextBundle(BaseContractModel):
    """M05 - Shared agent memory bundle and typed handoff."""
    bundle_id: str = Field(default_factory=generate_uuid)
    run_id: str = Field(...)
    ref_ids: List[str] = Field(default_factory=list)
    context_budget: int = Field(default=8000)
    used_tokens: int = Field(default=0)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    schema_version: int = Field(default=1)


class AssetPlan(BaseContractModel):
    """CORE - Generation plan defining shots, prompts, constraints."""
    plan_id: str = Field(default_factory=generate_uuid)
    shots: List[Dict[str, Any]] = Field(default_factory=list)
    prompts: Dict[str, str] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)
    model_policy: Dict[str, Any] = Field(default_factory=dict)
    schema_version: int = Field(default=1)


class ImageAsset(BaseContractModel):
    """CORE - Generated image asset reference and metadata."""
    asset_id: str = Field(default_factory=generate_uuid)
    object_ref: str = Field(...)
    sha256: str = Field(...)
    resolution: str = Field(default="1080x1920")
    aspect_ratio: str = Field(default="9:16")
    generation_call_id: Optional[str] = Field(default=None)
    schema_version: int = Field(default=1)


class VideoAsset(BaseContractModel):
    """CORE - Rendered Remotion / MP4 video asset reference."""
    asset_id: str = Field(default_factory=generate_uuid)
    object_ref: str = Field(...)
    sha256: str = Field(...)
    codec: str = Field(default="h264")
    duration: float = Field(..., gt=0.0)
    aspect_ratio: str = Field(default="9:16")
    generation_call_id: Optional[str] = Field(default=None)
    schema_version: int = Field(default=1)


class PlayableSpec(BaseContractModel):
    """CORE - Playable prototype parameter specification."""
    spec_id: str = Field(default_factory=generate_uuid)
    template: str = Field(default="match3")
    rules: Dict[str, Any] = Field(...)
    inputs: Dict[str, Any] = Field(default_factory=dict)
    winning_condition: Dict[str, Any] = Field(...)
    cta: Dict[str, Any] = Field(...)
    schema_version: int = Field(default=1)


class PlayableBundle(BaseContractModel):
    """CORE - Compiled Phaser.js / HTML5 playable package artifact."""
    bundle_id: str = Field(default_factory=generate_uuid)
    zip_object_ref: str = Field(...)
    sha256: str = Field(...)
    entrypoint: str = Field(default="index.html")
    build_report_id: Optional[str] = Field(default=None)
    schema_version: int = Field(default=1)


class EvaluationReport(BaseContractModel):
    """M07 - 7-Layer Quality Gate evaluation report."""
    report_id: str = Field(default_factory=generate_uuid)
    rubric_id: str = Field(...)
    gate_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    scores: Dict[str, float] = Field(default_factory=dict)
    overall_passed: bool = Field(...)
    judge_id: Optional[str] = Field(default=None)
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    schema_version: int = Field(default=1)


class ExperimentResult(BaseContractModel):
    """M03 - A/B experiment evaluation outcome."""
    result_id: str = Field(default_factory=generate_uuid)
    variant_ids: List[str] = Field(...)
    metric_values: Dict[str, Optional[float]] = Field(default_factory=dict)
    method: Literal["offline_rubric", "real_campaign"] = Field(...)
    uncertainty: Optional[Dict[str, float]] = Field(default=None)
    created_at: datetime = Field(default_factory=utc_now)
    schema_version: int = Field(default=1)
