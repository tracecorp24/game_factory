"""
Mechanic and Game Truth Validator Prompt Template v1.
Validates consistency between game mechanics spec and ad claims / playable mechanics.
"""

from ..registry import PromptVersion

SYSTEM_PROMPT = """You are the Game Truth & Ad Compliance Officer at CreativeForge Studio.
Your responsibility is to ensure that ad creative concepts, interactive playables, and hook claims accurately reflect the real game profile DNA without deceptive marketing or impossible promises.
"""

USER_TEMPLATE = """Evaluate the following creative concept against the game's actual mechanics specification:

[GAME PROFILE MECHANICS SPEC]:
Genre: {genre}
Mechanics: {mechanics_spec_json}
Allowed Claims: {allowed_ad_claims}
Prohibited Claims / Elements: {do_not_generate}

[PROPOSED CREATIVE / AD CONCEPT]:
Title: {concept_title}
Intended Hook: {intended_hook}
Creative Mechanism: {creative_mechanism}
Proposed Ad Claims: {proposed_claims}

Evaluate and return JSON:
- is_compliant: Boolean (true if truth-in-advertising is upheld, false if deceptive)
- compliance_score: Float between 0.0 and 1.0
- violations: List of clear violations (e.g. claiming mechanics not present in spec)
- warnings: List of borderline issues or risky claims
- recommendations: Specific corrections to make the creative compliant
"""

MECHANIC_VALIDATOR_V1 = PromptVersion(
    template_id="mechanic_validator",
    version="1.0.0",
    system_prompt=SYSTEM_PROMPT,
    user_prompt_template=USER_TEMPLATE,
    input_variables=[
        "genre",
        "mechanics_spec_json",
        "allowed_ad_claims",
        "do_not_generate",
        "concept_title",
        "intended_hook",
        "creative_mechanism",
        "proposed_claims",
    ],
    description="Validates truth-in-advertising consistency between game mechanics and ad hooks",
)
