"""
Experimentation and Learning Loop Models (Pydantic v2).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class ExperimentMode(str, Enum):
    OFFLINE = "offline"  # Synthetic QA, rubric scoring, internal simulated tests
    REAL_CAMPAIGN = "real_campaign"  # Empirical live ad network CSV or API metrics


class VariantVariable(str, Enum):
    HOOK = "hook"  # 0-3s visual or headline
    CTA = "cta"  # Endcard button text and animation
    COLOR_PALETTE = "color_palette"  # Color scheme and background contrast
    CHARACTER = "character"  # Hero mascot appearance or absence
    MECHANIC_TWIST = "mechanic_twist"  # Minor puzzle mechanic nuance


class ExperimentStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class CausalityStatus(str, Enum):
    VERIFIED_CAUSAL = "verified_causal"  # Controlled single-variable A/B test with statistical significance
    PROBABLE_TREND = "probable_trend"  # Strong correlation but potential confounding factors
    INCONCLUSIVE = "inconclusive"  # Sample size too small or p-value >= 0.05


class MetricValues(BaseModel):
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    installs: int = Field(default=0, ge=0)
    spend: float = Field(default=0.0, ge=0.0)
    ctr: Optional[float] = None  # clicks / impressions
    ipm: Optional[float] = None  # (installs / impressions) * 1000
    cpi: Optional[float] = None  # spend / installs
    calculated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class Variant(BaseModel):
    variant_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    is_control: bool = False
    variable_type: Optional[VariantVariable] = None
    variable_description: str = ""
    concept_id: Optional[str] = None
    artifact_ref: Optional[str] = None
    metrics: MetricValues = Field(default_factory=MetricValues)


class ExperimentComparison(BaseModel):
    control_variant_id: str
    test_variant_id: str
    control_metrics: MetricValues
    test_metrics: MetricValues
    delta_ctr: Optional[float] = None
    delta_ipm: Optional[float] = None
    delta_cpi: Optional[float] = None
    p_value: Optional[float] = None
    is_statistically_significant: bool = False
    sample_size_reached: bool = False
    winning_variant_id: Optional[str] = None
    rationale: str = ""


class Experiment(BaseModel):
    experiment_id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    name: str
    hypothesis_id: str
    mode: ExperimentMode = ExperimentMode.REAL_CAMPAIGN
    isolated_variable: VariantVariable
    status: ExperimentStatus = ExperimentStatus.DRAFT
    variants: List[Variant] = Field(default_factory=list)
    min_sample_size: int = Field(default=1000, ge=100)
    significance_threshold: float = Field(default=0.05, gt=0.0, lt=0.5)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    comparison_outcome: Optional[ExperimentComparison] = None
    notes: str = ""

    @property
    def mode_badge(self) -> str:
        return "[VERIFIED REAL CAMPAIGN]" if self.mode == ExperimentMode.REAL_CAMPAIGN else "[SYNTHETIC / OFFLINE QA]"


class LearningInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: str(uuid4()))
    experiment_id: str
    title: str
    key_finding: str
    actionable_rule: str
    causality_status: CausalityStatus
    target_genres: List[str] = Field(default_factory=list)
    confidence: str = "medium"  # low, medium, high
    supporting_metrics: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
