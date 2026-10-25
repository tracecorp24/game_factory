"""
Experimentation Application Service.
Provides lifecycle orchestration for A/B testing, metric calculation, and learning synthesis.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    Experiment,
    ExperimentComparison,
    ExperimentMode,
    ExperimentStatus,
    LearningInsight,
    MetricValues,
    VariantVariable,
)
from .planner import ExperimentPlanner
from .metrics import MetricCalculator
from .learning_memory import LearningMemoryService
from services.api.app.modules.concepts.models import ConceptBoard


class ExperimentService:
    """
    Coordinates creation, outcome tracking, statistical evaluation,
    and long-term learning memory for creative A/B experiments.
    """

    def __init__(
        self,
        planner: Optional[ExperimentPlanner] = None,
        memory: Optional[LearningMemoryService] = None,
    ):
        self.planner = planner or ExperimentPlanner()
        self.memory = memory or LearningMemoryService()
        self._experiments: Dict[str, Experiment] = {}

    def create_experiment(
        self,
        project_id: str,
        name: str,
        control_board: ConceptBoard,
        variable_type: VariantVariable,
        test_variation_description: str,
        mode: ExperimentMode = ExperimentMode.REAL_CAMPAIGN,
        min_sample_size: int = 1000,
        significance_threshold: float = 0.05,
    ) -> Experiment:
        exp = self.planner.create_single_variable_experiment(
            project_id=project_id,
            name=name,
            control_board=control_board,
            variable_type=variable_type,
            test_variation_description=test_variation_description,
            mode=mode,
            min_sample_size=min_sample_size,
            significance_threshold=significance_threshold,
        )
        self._experiments[exp.experiment_id] = exp
        return exp

    def get_experiment(self, experiment_id: str) -> Optional[Experiment]:
        return self._experiments.get(experiment_id)

    def list_experiments(self, project_id: Optional[str] = None) -> List[Experiment]:
        if project_id:
            return [e for e in self._experiments.values() if e.project_id == project_id]
        return list(self._experiments.values())

    def record_variant_metrics(
        self,
        experiment_id: str,
        variant_id: str,
        impressions: int,
        clicks: int,
        installs: int,
        spend: float,
    ) -> MetricValues:
        """Record raw telemetry and compute zero-division safe metrics."""
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Experiment '{experiment_id}' not found.")

        target_variant = None
        for v in exp.variants:
            if v.variant_id == variant_id:
                target_variant = v
                break

        if not target_variant:
            raise KeyError(f"Variant '{variant_id}' not found in experiment '{experiment_id}'.")

        metrics = MetricCalculator.calculate_metrics(
            impressions=impressions,
            clicks=clicks,
            installs=installs,
            spend=spend,
        )
        target_variant.metrics = metrics
        return metrics

    def evaluate_experiment_results(
        self,
        experiment_id: str,
        genre_context: str = "Match-3",
    ) -> tuple[ExperimentComparison, Optional[LearningInsight]]:
        """
        Runs statistical comparison between control and test variants,
        updates experiment status, and creates a durable LearningInsight.
        """
        exp = self._experiments.get(experiment_id)
        if not exp:
            raise KeyError(f"Experiment '{experiment_id}' not found.")

        if len(exp.variants) < 2:
            raise ValueError("Experiment requires at least 2 variants for comparison.")

        control = exp.variants[0]
        test = exp.variants[1]

        comparison = MetricCalculator.compare_variants(
            control_id=control.variant_id,
            test_id=test.variant_id,
            control_metrics=control.metrics,
            test_metrics=test.metrics,
            min_sample_size=exp.min_sample_size,
            significance_threshold=exp.significance_threshold,
        )

        exp.comparison_outcome = comparison
        exp.status = ExperimentStatus.COMPLETED

        # Synthesize into durable learning memory
        insight = self.memory.synthesize_insight_from_experiment(
            experiment=exp,
            genre=genre_context,
        )

        return comparison, insight
