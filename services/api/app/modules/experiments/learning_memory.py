"""
Learning Memory Service.
Transforms empirical experiment outcomes into durable, reusable creative strategy rules.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    CausalityStatus,
    Experiment,
    ExperimentComparison,
    ExperimentMode,
    LearningInsight,
    VariantVariable,
)

logger = logging.getLogger(__name__)


class LearningMemoryService:
    """
    Stores and retrieves verified empirical insights.
    Strictly differentiates between causal findings (controlled single-variable A/B test)
    and unverified correlational trends.
    """

    def __init__(self) -> None:
        self._insights: Dict[str, LearningInsight] = {}

    def synthesize_insight_from_experiment(
        self,
        experiment: Experiment,
        genre: str = "Match-3",
    ) -> Optional[LearningInsight]:
        """
        Derives a LearningInsight from a completed experiment outcome.
        Enforces causality verification rules.
        """
        outcome = experiment.comparison_outcome
        if not outcome:
            return None

        # Determine causality status
        if not outcome.sample_size_reached:
            status = CausalityStatus.INCONCLUSIVE
            confidence = "low"
            prefix = "[Inconclusive — Insufficient Sample Size]"
        elif experiment.mode == ExperimentMode.OFFLINE:
            status = CausalityStatus.PROBABLE_TREND
            confidence = "low"
            prefix = "[Synthetic QA Simulation]"
        elif outcome.is_statistically_significant:
            status = CausalityStatus.VERIFIED_CAUSAL
            confidence = "high"
            prefix = "[Empirically Verified]"
        elif outcome.p_value is not None and outcome.p_value < 0.10:
            status = CausalityStatus.PROBABLE_TREND
            confidence = "medium"
            prefix = "[Probable Trend]"
        else:
            status = CausalityStatus.INCONCLUSIVE
            confidence = "low"
            prefix = "[Inconclusive]"

        # Format actionable rule
        var_name = experiment.isolated_variable.value.upper()
        if outcome.winning_variant_id:
            winning_desc = (
                "Test variant" if outcome.winning_variant_id == outcome.test_variant_id else "Control baseline"
            )
            rule = (
                f"{prefix} For {genre} creatives, optimizing {var_name}: {winning_desc} demonstrated "
                f"superior performance (Delta CTR: {outcome.delta_ctr or 0:+.4f}, Delta IPM: {outcome.delta_ipm or 0:+.2f})."
            )
        else:
            rule = f"{prefix} Tested {var_name} variation in {genre} yielded no statistically significant separation."

        insight = LearningInsight(
            insight_id=str(uuid4()),
            experiment_id=experiment.experiment_id,
            title=f"Insight: {experiment.name} ({var_name})",
            key_finding=outcome.rationale,
            actionable_rule=rule,
            causality_status=status,
            target_genres=[genre],
            confidence=confidence,
            supporting_metrics={
                "delta_ctr": outcome.delta_ctr,
                "delta_ipm": outcome.delta_ipm,
                "delta_cpi": outcome.delta_cpi,
                "p_value": outcome.p_value,
                "sample_size_reached": outcome.sample_size_reached,
                "mode": experiment.mode.value,
            },
        )

        self._insights[insight.insight_id] = insight
        logger.info(
            "Synthesized learning insight %s: status=%s, confidence=%s",
            insight.insight_id,
            insight.causality_status.value,
            insight.confidence,
        )
        return insight

    def list_insights(
        self,
        genre: Optional[str] = None,
        causality_status: Optional[CausalityStatus] = None,
    ) -> List[LearningInsight]:
        """Query insights filtered by genre or verified causality status."""
        results = list(self._insights.values())
        if genre:
            results = [ins for ins in results if any(g.lower() == genre.lower() for g in ins.target_genres)]
        if causality_status:
            results = [ins for ins in results if ins.causality_status == causality_status]
        return results

    def get_insight(self, insight_id: str) -> Optional[LearningInsight]:
        return self._insights.get(insight_id)
