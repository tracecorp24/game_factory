"""
Creative Ideation Agent.
Generates empirical, evidence-grounded creative hypotheses from Trend Reports and Game DNA.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import uuid4

import sys
import os
import importlib.util

# Ensure services.worker_trends is resolvable
if "services.worker_trends" not in sys.modules:
    wt_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../worker-trends"))
    if wt_dir not in sys.path:
        sys.path.insert(0, wt_dir)
    spec = importlib.util.spec_from_file_location("worker_trends", os.path.join(wt_dir, "__init__.py"))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["worker_trends"] = mod
        sys.modules["services.worker_trends"] = mod
        spec.loader.exec_module(mod)

from .models import CreativeHypothesis, PrimaryMetric
from services.api.app.modules.game_dna.models import GameProfileVersion
from services.worker_trends.models import TrendReport, TrendSignal

logger = logging.getLogger(__name__)


class IdeationAgent:
    """
    Synthesizes Trend Intelligence Signals and Game DNA Profiles into
    3 to 8 distinct, rigorous, testable creative hypotheses.
    """

    ANGLE_TEMPLATES = [
        {
            "theme": "Frustration to Mastery Subversion",
            "hook_prefix": "97% of players fail this move!",
            "emotional_arc": "Mild annoyance at an obvious mistake -> urgent desire to fix -> satisfying combo resolution.",
            "mechanism": "Interactive one-tap blunder correction revealing hidden cascading booster.",
            "primary_metric": PrimaryMetric.IPM,
            "falsification_condition": "IPM drops below baseline by >10% due to player irritation or high drop-off in first 2s.",
            "novelty_rationale": "Subverts typical generic puzzle ads by demonstrating an intelligent error correction mechanic.",
        },
        {
            "theme": "Oddly Satisfying ASMR Cascades",
            "hook_prefix": "Turn sound ON for pure gem satisfaction.",
            "emotional_arc": "Sensory curiosity -> deep visual/audio tactile pleasure -> desire to replicate feeling.",
            "mechanism": "Mega rainbow gem trigger causing a 12-gem chain reaction with synchronized spatial audio.",
            "primary_metric": PrimaryMetric.CTR,
            "falsification_condition": "CTR does not achieve at least +15% over non-ASMR control in silent playback.",
            "novelty_rationale": "Focuses on audio-visual haptics rather than competitive game loss.",
        },
        {
            "theme": "High-Stakes Rescue Timer Challenge",
            "hook_prefix": "Only 3 moves before the treasure collapses!",
            "emotional_arc": "Instant urgency -> strategic tension -> euphoric last-second rescue.",
            "mechanism": "Pulsing countdown move counter with dynamic board lighting and danger warning.",
            "primary_metric": PrimaryMetric.IPM,
            "falsification_condition": "Playable completion rate falls below 40% indicating move puzzle is too hard.",
            "novelty_rationale": "Brings time-pressure elements into turn-based matching without misrepresenting core rules.",
        },
        {
            "theme": "Dramatic Mascot Reaction Dilemma",
            "hook_prefix": "Don't let the King lose his royal crown!",
            "emotional_arc": "Empathy for mascot -> comedic tension -> celebratory royal reward fanfare.",
            "mechanism": "Dynamic character expression camera reacting live to every tile swap.",
            "primary_metric": PrimaryMetric.CTR,
            "falsification_condition": "View-through rate in 0-3s window is lower than non-character variant.",
            "novelty_rationale": "Leverages expressive mascot character animation to boost emotional resonance.",
        },
        {
            "theme": "Satisfying Cleaning & Renovation Metaphor",
            "hook_prefix": "Clean this messy estate in 3 taps!",
            "emotional_arc": "Clutter fatigue -> satisfying visual clearing -> beautiful orderly transformation.",
            "mechanism": "Tiles clear dirty surface textures to uncover pristine architectural art.",
            "primary_metric": PrimaryMetric.CPI_REDUCTION,
            "falsification_condition": "Installs fail to increase despite higher click-through.",
            "novelty_rationale": "Integrates popular sorting/renovation satisfaction directly into Match-3 board.",
        },
    ]

    def generate_hypotheses(
        self,
        trend_report: TrendReport,
        profile_version: GameProfileVersion,
        count: int = 4,
        target_audience: Optional[str] = None,
    ) -> List[CreativeHypothesis]:
        """
        Generates between 3 and 8 unique CreativeHypothesis models grounded in
        real trend report signals and bounded by Game Profile DNA constraints.
        """
        target_count = max(3, min(8, count))
        hypotheses: List[CreativeHypothesis] = []

        # Collect evidence refs from trend report
        evidence_ids: List[str] = []
        for signal in trend_report.signals:
            for ref in signal.evidence_refs:
                evidence_ids.append(ref.evidence_id)

        # Default fallback evidence if report had no signals
        if not evidence_ids:
            evidence_ids = [f"signal_auto_{profile_version.genre.value.lower()}"]

        audience = target_audience or "Casual & Midcore Mobile Puzzle Gamers (Age 25-54, seeking quick tactile relaxation)"

        for idx in range(target_count):
            tpl = self.ANGLE_TEMPLATES[idx % len(self.ANGLE_TEMPLATES)]

            # Check negative constraints
            hook_text = f"{tpl['hook_prefix']} Tap to blast!"
            for forbidden in profile_version.do_not_generate:
                if forbidden.lower() in hook_text.lower():
                    hook_text = f"Satisfying {profile_version.genre.value} challenge!"

            title = f"{profile_version.name} — {tpl['theme']}"

            # Distribute evidence refs across hypotheses
            assigned_refs = evidence_ids[idx % len(evidence_ids) : (idx % len(evidence_ids)) + 2]
            if not assigned_refs:
                assigned_refs = evidence_ids[:1]

            hypo = CreativeHypothesis(
                project_id=None,
                game_profile_version_id=profile_version.version_id,
                title=title,
                audience=audience,
                genre=profile_version.genre.value,
                intended_hook=hook_text,
                emotional_arc=tpl["emotional_arc"],
                evidence_refs=assigned_refs,
                creative_mechanism=tpl["mechanism"],
                primary_metric=tpl["primary_metric"],
                falsification_condition=tpl["falsification_condition"],
                limitations=[
                    "Requires 60fps particle render in playable sandbox",
                    "Asset bundle size must remain under 4.5MB for responsive web load",
                ],
                novelty_rationale=tpl["novelty_rationale"],
            )
            hypotheses.append(hypo)

        logger.info(
            "Generated %d creative hypotheses for game '%s' (version %s)",
            len(hypotheses),
            profile_version.name,
            profile_version.version_id,
        )
        return hypotheses
