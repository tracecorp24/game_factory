"""
Learning Synthesis Prompt Template v1.
Synthesizes A/B test results and performance outcomes into durable learning memory.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are a Lead Growth & Experimentation Scientist at CreativeForge Studio.
Your role is to synthesize empirical A/B test outcomes into actionable, durable learning insights.
Distinguish strictly between statistical correlation and validated causal relationships.
Never assume correlation implies causation without a controlled single-variable experiment.
"""

USER_TEMPLATE = """Synthesize findings from the following experiment:

[EXPERIMENT INFO]:
ID: {experiment_id}
Name: {experiment_name}
Hypothesis Tested: {hypothesis_text}
Isolated Variable: {variable_type} (e.g. HOOK, CTA, COLOR_PALETTE)
Test Mode: {test_mode} (offline vs real_campaign)

[VARIANTS & OUTCOMES]:
Control (Variant A): {variant_a_summary}
Test (Variant B): {variant_b_summary}
Metric Differences:
- Delta CTR: {delta_ctr}
- Delta IPM: {delta_ipm}
- Delta CPI: {delta_cpi}
- Statistical Significance (p-value): {p_value}

Provide JSON:
- key_finding: Clear 1-sentence finding
- causality_status: "verified_causal" | "probable_trend" | "inconclusive"
- actionable_rule: Concrete rule for future ideation (e.g. "For Match-3, 3s frustration hook improves IPM by 18%")
- target_genres: Genres where this rule likely applies
- confidence: "low" | "medium" | "high"
"""

LEARNING_SYNTHESIS_V1 = PromptVersion(
    template_id="learning_synthesis",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=[
        "experiment_id",
        "experiment_name",
        "hypothesis_text",
        "variable_type",
        "test_mode",
        "variant_a_summary",
        "variant_b_summary",
        "delta_ctr",
        "delta_ipm",
        "delta_cpi",
        "p_value",
    ],
    description="Synthesizes A/B test outcomes into reusable learning rules with strict causal distinction",
)
