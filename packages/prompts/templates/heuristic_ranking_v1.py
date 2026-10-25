"""
Heuristic Ranking Rationale Prompt Template v1.
Generates structured justification for concept ranking scores.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are an algorithmic creative strategist.
Explain heuristic ranking scores computed across 6 dimensions:
Score = 0.25*evidence + 0.20*game_fit + 0.20*novelty + 0.15*feasibility + 0.10*hook_clarity + 0.10*cost_fit.
Note: Always remind that this is a calibrated heuristic for ideation prioritization, NOT a guaranteed CTR or performance prediction.
"""

USER_TEMPLATE = """Explain the ranking evaluation for concept '{concept_title}':

[DIMENSION SCORES (0.0 to 1.0)]:
- Evidence Grounding (0.25): {evidence_score}
- Game DNA Fit (0.20): {game_fit_score}
- Novelty vs Category (0.20): {novelty_score}
- Technical Feasibility (0.15): {feasibility_score}
- Hook Clarity (0.10): {hook_clarity_score}
- Production Cost Fit (0.10): {cost_fit_score}
- Total Composite Score: {composite_score}

Provide JSON:
- primary_strength: Key advantage of this concept
- primary_risk: Chief operational or creative risk
- optimization_tips: 2-3 concrete tips to increase score
- ranking_summary: 2-sentence executive summary
"""

HEURISTIC_RANKING_V1 = PromptVersion(
    template_id="heuristic_ranking",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=[
        "concept_title",
        "evidence_score",
        "game_fit_score",
        "novelty_score",
        "feasibility_score",
        "hook_clarity_score",
        "cost_fit_score",
        "composite_score",
    ],
    description="Explains composite heuristic ranking scores across 6 standardized dimensions",
)
