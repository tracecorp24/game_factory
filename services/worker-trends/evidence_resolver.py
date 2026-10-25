"""
Evidence Resolver and Confidence Calibration Engine.
Connects every trend signal to concrete observations with strict provenance.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .models import ConfidenceLevel, EvidenceRef, TrendObservation, TrendSignal


class EvidenceResolver:
    """
    Validates, links, and calculates statistical confidence for trend insights.
    Enforces the core rule: No trend signal without empirical evidence provenance.
    """

    def __init__(self, half_life_days: float = 14.0):
        self.half_life_days = half_life_days

    def calculate_recency_weight(self, observed_at_iso: str, reference_date: Optional[datetime] = None) -> float:
        """Calculates exponential decay based on observation age in days."""
        ref = reference_date or datetime.now(timezone.utc)
        try:
            # Handle ISO string with Z or offset
            dt_str = observed_at_iso.replace("Z", "+00:00")
            obs_dt = datetime.fromisoformat(dt_str)
            if obs_dt.tzinfo is None:
                obs_dt = obs_dt.replace(tzinfo=timezone.utc)
            delta_days = max(0.0, (ref - obs_dt).total_seconds() / 86400.0)
        except Exception:
            delta_days = 30.0

        # Exponential decay: e^(-lambda * t) where lambda = ln(2)/half_life
        decay_constant = math.log(2.0) / self.half_life_days
        return math.exp(-decay_constant * delta_days)

    def resolve_evidence_refs(
        self,
        observations: List[TrendObservation],
        snapshot_id: str,
    ) -> List[EvidenceRef]:
        """Convert raw observations into verified EvidenceRef objects."""
        refs: List[EvidenceRef] = []
        for obs in observations:
            evidence_url = obs.evidence_url or f"urn:source:{obs.source_id}:snapshot:{snapshot_id}:app:{obs.bundle_id or obs.app_name}"
            refs.append(
                EvidenceRef(
                    source_id=obs.source_id,
                    evidence_url=evidence_url,
                    observed_at=obs.observed_at,
                    raw_snapshot_id=snapshot_id,
                    rank=obs.rank,
                    observation_snippet=f"{obs.app_name} | {obs.genre or 'Unknown'} | Rank #{obs.rank or 'N/A'}",
                    confidence=ConfidenceLevel.MEDIUM if obs.evidence_url else ConfidenceLevel.LOW,
                )
            )
        return refs

    def calibrate_signal_confidence(
        self,
        evidence_refs: List[EvidenceRef],
        distinct_sources: int,
    ) -> tuple[ConfidenceLevel, float, float]:
        """
        Calibrates confidence level and score (0.0 to 1.0) based on:
        - Sample size (number of observations)
        - Source diversity (cross-validation across distinct sources)
        - Recency weight
        """
        if not evidence_refs:
            return ConfidenceLevel.LOW, 0.0, 999.0

        now = datetime.now(timezone.utc)
        recency_scores = [self.calculate_recency_weight(ref.observed_at, now) for ref in evidence_refs]
        avg_recency = sum(recency_scores) / len(recency_scores)

        # Average age in days
        earliest_recency = min(recency_scores)
        approx_days = -math.log(max(earliest_recency, 0.0001)) * (self.half_life_days / math.log(2.0))

        # Size factor: diminishing returns after 5 observations
        size_factor = min(1.0, len(evidence_refs) / 5.0)

        # Source diversity factor: bonus for multi-source confirmation
        source_factor = 1.0 if distinct_sources >= 2 else 0.75

        composite_score = round((0.4 * size_factor + 0.35 * avg_recency + 0.25 * source_factor), 3)
        composite_score = max(0.0, min(1.0, composite_score))

        if composite_score >= 0.75 and len(evidence_refs) >= 3:
            level = ConfidenceLevel.HIGH
        elif composite_score >= 0.45:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return level, composite_score, round(approx_days, 1)

    def build_trend_signal(
        self,
        genre: str,
        mechanic_pattern: str,
        hook_theme: str,
        description: str,
        observations: List[TrendObservation],
        snapshot_id: str,
        recommended_angles: Optional[List[str]] = None,
    ) -> TrendSignal:
        """Assembles a verified TrendSignal from empirical observations."""
        evidence_refs = self.resolve_evidence_refs(observations, snapshot_id)
        sources = {obs.source_id for obs in observations}
        level, score, recency_days = self.calibrate_signal_confidence(evidence_refs, len(sources))

        return TrendSignal(
            genre=genre,
            mechanic_pattern=mechanic_pattern,
            hook_theme=hook_theme,
            description=description,
            evidence_refs=evidence_refs,
            confidence=level,
            confidence_score=score,
            sample_size=len(observations),
            recency_days=recency_days,
            recommended_angles=recommended_angles or [],
        )
