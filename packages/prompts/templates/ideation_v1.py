"""
Creative Hypothesis Ideation Prompt Template v1.
Generates structured creative hypotheses grounded in trend signals and game DNA.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are the Principal Creative Strategist at CreativeForge Intelligence Studio v3.0.
Your mission is to formulate structured, high-performing mobile game creative hypotheses grounded strictly in empirical trend evidence and game profile DNA.

Principles:
1. Every hypothesis must be anchored to concrete trend observations (with source links & dates).
2. Creative mechanisms must be strictly compatible with the game's core loop, mechanics spec, and brand constraints.
3. Respect all negative constraints ('do_not_generate').
4. Formulate testable falsification conditions and expected primary metrics.
5. Return strictly valid JSON adhering to the CreativeHypothesis schema.
"""

USER_TEMPLATE = """Generate {num_concepts} distinct creative hypotheses for the following campaign:

[GAME PROFILE DNA]
Name: {game_name}
Genre: {genre}
Core Mechanics: {mechanics_summary}
Style Tokens: {style_tokens}
Brand Constraints: {brand_constraints}
Forbidden Elements (Do Not Generate): {do_not_generate}
Allowed Ad Claims: {allowed_ad_claims}

[TREND INTELLIGENCE & EVIDENCE]
Trend Signals:
{trend_signals_json}

[AUDIENCE & CAMPAIGN CONTEXT]
Target Audience: {target_audience}
Optimization Goal: {optimization_goal}

For each hypothesis, include:
- title: Concise concept title
- audience: Precise gamer archetype and motivation
- genre: Sub-genre alignment
- intended_hook: The critical 0-3 second hook description and visual action
- emotional_arc: Emotional journey (e.g. Frustration -> Tension -> Satisfying Mastery)
- evidence_refs: List of IDs from the provided trend signals supporting this direction
- creative_mechanism: Interactive or visual mechanic highlighted in the ad
- primary_metric: CTR, IPM, or CPI_reduction
- falsification_condition: Specific condition under which this concept should be considered failed
- limitations: Known production risks, audience fatigue, or brand limitations
- novelty_rationale: Why this creative is meaningfully novel in the category
"""

IDEATION_V1 = PromptVersion(
    template_id="ideation",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=[
        "num_concepts",
        "game_name",
        "genre",
        "mechanics_summary",
        "style_tokens",
        "brand_constraints",
        "do_not_generate",
        "allowed_ad_claims",
        "trend_signals_json",
        "target_audience",
        "optimization_goal",
    ],
    description="Generates grounded creative hypotheses from Trend Intelligence and Game DNA",
)
