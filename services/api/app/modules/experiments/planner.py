"""
Experiment Planner.
Designs rigorous single-variable A/B test experiments with strict offline vs real-campaign isolation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    Experiment,
    ExperimentMode,
    ExperimentStatus,
    Variant,
    VariantVariable,
)
from services.api.app.modules.concepts.models import ConceptBoard

logger = logging.getLogger(__name__)


class ExperimentPlannerError(Exception):
    """Raised when experiment plan formulation violates scientific validity."""
    pass


class ExperimentPlanner:
    """
    Constructs scientifically valid A/B test plans.
    Enforces the single-variable isolation principle:
    Only ONE creative element (Hook, CTA, Color Palette, Character, or Mechanic)
    may vary between control and test variants.
    """

    SUPPORTED_HOOK_VARIATIONS = [
        ("Loss Aversion / Frustration", "97% of players cannot beat this!"),
        ("Oddly Satisfying ASMR", "Turn sound ON for maximum gem pops!"),
        ("Urgent Rescue Dilemma", "Hurry! 3 seconds to save the royal crown!"),
        ("Casual Relaxing", "Unwind with the ultimate satisfying puzzle."),
    ]

    SUPPORTED_CTA_VARIATIONS = [
        ("Play Now", "Hemen Oyna / Play Now Free"),
        ("Challenge", "Can you beat Level 10?"),
        ("Install Direct", "Get Free on App Store"),
    ]

    def create_single_variable_experiment(
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
        """
        Derives an A/B test with exactly one isolated variable changed in the test variant.
        """
        if not test_variation_description or not test_variation_description.strip():
            raise ExperimentPlannerError("Test variant variation description cannot be empty.")

        # Control Variant (Baseline)
        control_variant = Variant(
            variant_id=str(uuid4()),
            name=f"Control ({control_board.hypothesis.title})",
            is_control=True,
            variable_type=None,
            variable_description="Original baseline concept",
            concept_id=control_board.concept_id,
        )

        # Test Variant (Isolated single-variable difference)
        test_variant = Variant(
            variant_id=str(uuid4()),
            name=f"Test Variant [{variable_type.value.upper()}]",
            is_control=False,
            variable_type=variable_type,
            variable_description=test_variation_description.strip(),
            concept_id=control_board.concept_id,
        )

        experiment = Experiment(
            project_id=project_id,
            name=name,
            hypothesis_id=control_board.hypothesis.hypothesis_id,
            mode=mode,
            isolated_variable=variable_type,
            status=ExperimentStatus.DRAFT,
            variants=[control_variant, test_variant],
            min_sample_size=min_sample_size,
            significance_threshold=significance_threshold,
            notes=f"Single-variable test isolating '{variable_type.value}'. Mode: {mode.value}.",
        )

        logger.info(
            "Created %s experiment '%s' (ID: %s) isolating variable: %s",
            experiment.mode_badge,
            name,
            experiment.experiment_id,
            variable_type.value,
        )
        return experiment

    def derive_hook_variants(
        self,
        project_id: str,
        control_board: ConceptBoard,
        mode: ExperimentMode = ExperimentMode.REAL_CAMPAIGN,
    ) -> Experiment:
        """Convenience method to derive an A/B test testing alternate opening 3-second hooks."""
        current_hook = control_board.hook_frame.headline_text
        alt_hook = "Can you beat Level 50 in 3 moves? Tap to prove it!"
        for name, hook in self.SUPPORTED_HOOK_VARIATIONS:
            if hook != current_hook:
                alt_hook = hook
                break

        return self.create_single_variable_experiment(
            project_id=project_id,
            name=f"{control_board.hypothesis.title} — Hook A/B Test",
            control_board=control_board,
            variable_type=VariantVariable.HOOK,
            test_variation_description=f"Altered 0-3s hook to: '{alt_hook}'",
            mode=mode,
        )
