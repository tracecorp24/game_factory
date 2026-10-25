"""
Standard Rubric Catalog for CreativeForge Evaluations.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from typing import Dict, List
from services.api.app.modules.evaluations.schemas import (
    RubricCriterionSchema,
    RubricDefinitionSchema,
)

STANDARD_RUBRICS: Dict[str, RubricDefinitionSchema] = {
    "rubric_mobile_ad_v3": RubricDefinitionSchema(
        rubric_id="rubric_mobile_ad_v3",
        name="Mobile Video & Image Ad Rubric v3.0",
        version="v3.0",
        target_types=["image", "video"],
        pass_threshold=3.0,
        golden_prompt_id="ref_golden_puzzle_hook_01",
        criteria=[
            RubricCriterionSchema(
                id="hook_clarity",
                name="Hook Clarity & Attention Grab",
                weight=0.30,
                description="Does the 0-3s opening immediately capture interest with crisp contrast and narrative pull?",
            ),
            RubricCriterionSchema(
                id="gameplay_authenticity",
                name="Gameplay Authenticity & Flow",
                weight=0.25,
                description="Does the ad demonstrate true, satisfying game mechanics without misleading illusions?",
            ),
            RubricCriterionSchema(
                id="visual_audio_polish",
                name="Visual & Polish Quality",
                weight=0.20,
                description="High resolution, consistent typography, smooth framing and appealing colors.",
            ),
            RubricCriterionSchema(
                id="brand_and_cta_strength",
                name="Brand Identity & CTA Prominence",
                weight=0.15,
                description="Clear logo/game title recognition and unmistakable 'Play Now / Download' CTA endcard.",
            ),
            RubricCriterionSchema(
                id="novelty_and_differentiation",
                name="Creative Novelty & Differentiation",
                weight=0.10,
                description="Breaks category fatigue and avoids overused tropes while retaining high conversion power.",
            ),
        ],
    ),
    "rubric_playable_v3": RubricDefinitionSchema(
        rubric_id="rubric_playable_v3",
        name="Playable Mini-Game Technical & Engagement Rubric v3.0",
        version="v3.0",
        target_types=["playable_zip"],
        pass_threshold=3.2,
        golden_prompt_id="ref_golden_playable_match3_01",
        criteria=[
            RubricCriterionSchema(
                id="interaction_responsiveness",
                name="Touch / Swipe Responsiveness",
                weight=0.35,
                description="Immediate zero-lag tactile feedback when player interacts with pieces on grid.",
            ),
            RubricCriterionSchema(
                id="mechanics_clarity",
                name="Mechanics Clarity & Onboarding",
                weight=0.25,
                description="Player instantly understands the goal (e.g. match 3 gems) without reading lengthy instructions.",
            ),
            RubricCriterionSchema(
                id="reward_and_juice",
                name="Feedback Loops ('Juice') & Particle Effects",
                weight=0.20,
                description="Satisfying match explosions, combo counters, and dynamic audio-visual reinforcement.",
            ),
            RubricCriterionSchema(
                id="endcard_transition",
                name="Seamless Transition to Store CTA",
                weight=0.20,
                description="Winning or move limit reached leads smoothly to store CTA without getting stuck.",
            ),
        ],
    ),
    "rubric_concept_v3": RubricDefinitionSchema(
        rubric_id="rubric_concept_v3",
        name="Creative Hypothesis & Concept Board Evaluation Rubric v3.0",
        version="v3.0",
        target_types=["concept_board"],
        pass_threshold=3.0,
        golden_prompt_id="ref_golden_concept_board_01",
        criteria=[
            RubricCriterionSchema(
                id="evidence_grounding",
                name="Evidence & Trend Grounding",
                weight=0.30,
                description="Concept is directly supported by empirical store data or market signals.",
            ),
            RubricCriterionSchema(
                id="brand_compatibility",
                name="Brand & Game DNA Compatibility",
                weight=0.25,
                description="Fits game IP, character tone, and mechanic boundaries cleanly.",
            ),
            RubricCriterionSchema(
                id="production_feasibility",
                name="Production & Asset Feasibility",
                weight=0.25,
                description="Can be produced within pipeline generation budgets and asset limitations.",
            ),
            RubricCriterionSchema(
                id="falsifiability",
                name="Clear Falsification & Primary Metric",
                weight=0.20,
                description="Specifies exact hypothesis falsification conditions and expected metric lift.",
            ),
        ],
    ),
}
