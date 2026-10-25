"""
Experiments and Learning Loop REST API endpoints.
Connected directly to ExperimentService and MetricCalculator.
CreativeForge Intelligence Studio v3.0 - Section J & Module M03.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.api.app.modules.experiments.service import ExperimentService
from services.api.app.modules.experiments.models import (
    ExperimentMode,
    VariantVariable,
)
from services.api.app.modules.experiments.metrics import MetricCalculator
from services.api.app.modules.concepts.models import (
    ConceptBoard,
    CreativeHypothesis,
    HookFrameSpec,
    RankingDimensionScores,
    RankingEvaluation,
    RankingWeights,
)

router = APIRouter(prefix="", tags=["Experiments & Learning"])

# Shared singleton service instance
experiment_service = ExperimentService()

_EXPERIMENTS_LEGACY_CACHE: Dict[str, Dict[str, Any]] = {
    "exp_ab_hook_01": {
        "id": "exp_ab_hook_01",
        "campaign_id": "cmp_fall_promo",
        "name": "Hook A/B Test: Mystery vs Urgency",
        "mode": "offline",
        "variants": [
            {"id": "var_a", "intended_hook": "Mystery gem mystery", "artifact_id": "art_sample_001"},
            {"id": "var_b", "intended_hook": "Urgency 30-sec rush", "artifact_id": "art_sample_002"},
        ],
        "created_at": "2026-10-25T11:00:00Z",
    }
}


class ExperimentCreate(BaseModel):
    campaign_id: str
    name: str
    mode: str = Field(default="offline", description="'offline' (synthetic QA) or 'real_campaign'")
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    isolated_variable: Optional[str] = "hook"


class OutcomeMetricsImport(BaseModel):
    variant_id: str
    impressions: int = Field(ge=0)
    clicks: int = Field(ge=0)
    installs: int = Field(ge=0)
    spend: float = Field(ge=0.0)


@router.post("/experiments", status_code=201)
async def create_experiment(payload: ExperimentCreate):
    """Create a new A/B creative experiment plan."""
    eid = f"exp_{uuid.uuid4().hex[:8]}"
    mode_enum = ExperimentMode.REAL_CAMPAIGN if payload.mode.lower() == "real_campaign" else ExperimentMode.OFFLINE

    record = {
        "id": eid,
        "campaign_id": payload.campaign_id,
        "name": payload.name,
        "mode": payload.mode,
        "mode_badge": "[VERIFIED REAL CAMPAIGN]" if mode_enum == ExperimentMode.REAL_CAMPAIGN else "[SYNTHETIC / OFFLINE QA]",
        "variants": payload.variants,
        "created_at": "2026-10-25T12:00:00Z",
    }
    _EXPERIMENTS_LEGACY_CACHE[eid] = record
    return record


@router.get("/experiments")
async def list_experiments(campaign_id: Optional[str] = None):
    """List experiments, optionally filtered by campaign."""
    if campaign_id:
        return [e for e in _EXPERIMENTS_LEGACY_CACHE.values() if e.get("campaign_id") == campaign_id]
    return list(_EXPERIMENTS_LEGACY_CACHE.values())


@router.post("/experiments/{experiment_id}/outcomes/import")
async def import_outcome_metrics(experiment_id: str, payload: OutcomeMetricsImport):
    """
    Import outcome performance metrics with strict zero-division safety:
    CTR = clicks / impressions (null if impressions == 0)
    CPI = spend / installs (null if installs == 0)
    IPM = (installs / impressions) * 1000 (null if impressions == 0)
    """
    if experiment_id not in _EXPERIMENTS_LEGACY_CACHE and experiment_id not in experiment_service._experiments:
        raise HTTPException(status_code=404, detail="Experiment not found")

    metrics = MetricCalculator.calculate_metrics(
        impressions=payload.impressions,
        clicks=payload.clicks,
        installs=payload.installs,
        spend=payload.spend,
    )

    result = {
        "experiment_id": experiment_id,
        "variant_id": payload.variant_id,
        "raw_counts": {
            "impressions": payload.impressions,
            "clicks": payload.clicks,
            "installs": payload.installs,
            "spend": payload.spend,
        },
        "computed_metrics": {
            "ctr": metrics.ctr,
            "cpi": metrics.cpi,
            "ipm": metrics.ipm,
        },
        "imported_at": "2026-10-25T12:00:00Z",
    }
    return result


@router.post("/experiments/{experiment_id}/evaluate")
async def evaluate_experiment(experiment_id: str, genre_context: str = "Match-3"):
    """Evaluate statistical significance between variants and synthesize durable learning insight."""
    if experiment_id in experiment_service._experiments:
        comparison, insight = experiment_service.evaluate_experiment_results(
            experiment_id=experiment_id,
            genre_context=genre_context,
        )
        return {
            "experiment_id": experiment_id,
            "comparison": comparison.model_dump(),
            "insight": insight.model_dump() if insight else None,
        }
    raise HTTPException(status_code=404, detail="Experiment not found in active experiment engine.")
