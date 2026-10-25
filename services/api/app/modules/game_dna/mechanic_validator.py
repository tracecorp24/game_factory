"""
Mechanic and Game Truth Validator.
Enforces truth-in-advertising consistency between Game DNA and creative concepts.
"""

from __future__ import annotations

from typing import List, Optional
from .models import GameProfileVersion, MechanicGenre, MechanicValidationResult


class MechanicValidator:
    """
    Evaluates proposed creative concepts and ad claims against Game Profile DNA.
    Prevents deceptive bait marketing and ensures brand compliance.
    """

    KNOWN_BAIT_PATTERNS = {
        "pin_pull": ["pull the pin", "pin pull", "remove pin to save"],
        "tower_math": ["tower math", "hero climb tower", "multiply numbers runner"],
        "freezing_cabin": ["freezing cabin", "match match to keep warm", "mother in cold"],
        "fake_open_world": ["open world", "drive cars", "survival crafting"],
    }

    def validate_creative(
        self,
        profile_version: GameProfileVersion,
        concept_title: str,
        intended_hook: str,
        creative_mechanism: str,
        proposed_claims: Optional[List[str]] = None,
    ) -> MechanicValidationResult:
        """
        Validates that the concept's hooks, mechanics, and claims are compatible
        with the game profile's real genre and do not violate constraints.
        """
        violations: List[str] = []
        warnings: List[str] = []
        recommendations: List[str] = []

        combined_text = f"{concept_title} {intended_hook} {creative_mechanism} {' '.join(proposed_claims or [])}".lower()

        # 1. Check prohibited negative elements (do_not_generate)
        for forbidden in profile_version.do_not_generate:
            f_norm = forbidden.replace("_", " ").lower()
            if f_norm in combined_text:
                violations.append(
                    f"Violates negative constraint 'do_not_generate': found prohibited motif '{forbidden}'."
                )

        # 2. Check bait mini-games incompatible with genre
        if profile_version.genre == MechanicGenre.MATCH_3:
            for bait_type, triggers in self.KNOWN_BAIT_PATTERNS.items():
                for trig in triggers:
                    if trig in combined_text:
                        violations.append(
                            f"Deceptive gameplay flag: Match-3 profile cannot use '{bait_type}' mechanics ({trig}) "
                            f"as primary advertising hook without actual game mode support."
                        )

        # 3. Check allowed ad claims whitelist
        if proposed_claims:
            allowed_lower = [c.lower() for c in profile_version.allowed_ad_claims]
            for claim in proposed_claims:
                claim_lower = claim.lower()
                # Check for extreme or deceptive superlative claims
                if any(kw in claim_lower for kw in ["win $1000", "real money", "cash out instantly"]):
                    violations.append(f"Deceptive financial promise in claim: '{claim}'.")
                elif not any(allowed in claim_lower or claim_lower in allowed for allowed in allowed_lower):
                    warnings.append(
                        f"Claim '{claim}' is not in approved allowed_ad_claims whitelist. Requires human brand review."
                    )

        # 4. Compute score
        if violations:
            score = max(0.0, 1.0 - (len(violations) * 0.4) - (len(warnings) * 0.1))
            is_compliant = False
            recommendations.append("Align the ad hook directly with real core gameplay mechanics (e.g. gem cascades).")
            recommendations.append("Remove deceptive bait triggers and unapproved claims.")
        elif warnings:
            score = max(0.6, 1.0 - (len(warnings) * 0.1))
            is_compliant = True
            recommendations.append("Obtain brand manager clearance for claims outside the preset whitelist.")
        else:
            score = 1.0
            is_compliant = True

        return MechanicValidationResult(
            is_compliant=is_compliant,
            compliance_score=round(score, 2),
            violations=violations,
            warnings=warnings,
            recommendations=recommendations,
        )
