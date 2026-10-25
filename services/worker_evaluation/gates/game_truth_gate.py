"""
Gate 3: GameTruthGate - Verifies that ad creative claims and mechanics align with Game DNA specifications.
Prevents deceptive/misleading gameplay claims and brand violations.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)


class GameTruthGate(BaseGate):
    """Gate 3: Game DNA & Truth in Advertising Gate."""

    gate_name: str = "game_truth_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False  # Can be configured per project; defaults to non-fatal ERROR

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        game_dna = context.game_dna or {}
        hypothesis = context.creative_hypothesis or {}
        artifact = context.artifact or {}

        # If no Game DNA is registered, pass with informational note
        if not game_dna:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.PASSED,
                severity=GateSeverity.INFO,
                score=4.0,
                message="No Game DNA constraints defined for this project; skipped deep constraint matching.",
                details={"game_dna_present": False},
            )

        # Extract text to analyze (ad claims, hooks, mechanism descriptions)
        text_corpus: List[str] = []
        if "intended_hook" in hypothesis:
            text_corpus.append(str(hypothesis["intended_hook"]))
        if "creative_mechanism" in hypothesis:
            text_corpus.append(str(hypothesis["creative_mechanism"]))
        if "ad_claims" in hypothesis and isinstance(hypothesis["ad_claims"], list):
            text_corpus.extend([str(c) for c in hypothesis["ad_claims"]])
        if "title" in artifact:
            text_corpus.append(str(artifact["title"]))

        media_meta = artifact.get("media_meta", {})
        if "hook_text" in media_meta:
            text_corpus.append(str(media_meta["hook_text"]))
        if "cta_text" in media_meta:
            text_corpus.append(str(media_meta["cta_text"]))

        combined_text = " ".join(text_corpus).lower()

        # 1. Check "do_not_generate" / negative brand constraints
        do_not_generate = [str(term).lower() for term in game_dna.get("do_not_generate", [])]
        brand_violations: List[str] = []
        for term in do_not_generate:
            if re.search(r"\b" + re.escape(term) + r"\b", combined_text):
                brand_violations.append(term)

        if brand_violations:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=0.5,
                failure_code="BRAND_CONSTRAINT_VIOLATION",
                message=f"Creative ad claim contains forbidden terms from 'do_not_generate': {brand_violations}",
                details={
                    "violating_terms": brand_violations,
                    "matched_text_sample": combined_text[:300],
                },
            )

        # 2. Check Mechanics Alignment (Misleading Gameplay Check)
        mechanics_spec = game_dna.get("mechanics_spec", {})
        core_genre = str(mechanics_spec.get("genre", "")).lower()
        allowed_mechanics = {str(m).lower() for m in mechanics_spec.get("allowed_mechanics", [])}
        disallowed_mechanics = {str(m).lower() for m in mechanics_spec.get("disallowed_mechanics", [])}

        # Check for explicitly disallowed mechanics claims
        found_disallowed_mechanics: List[str] = []
        for dis_m in disallowed_mechanics:
            if re.search(r"\b" + re.escape(dis_m) + r"\b", combined_text):
                found_disallowed_mechanics.append(dis_m)

        if found_disallowed_mechanics:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.FAILED,
                severity=GateSeverity.ERROR,
                score=1.0,
                failure_code="GAME_TRUTH_MISLEADING_MECHANIC",
                message=f"Creative advertises gameplay mechanics conflicting with Game DNA: {found_disallowed_mechanics}",
                details={
                    "disallowed_mechanics_found": found_disallowed_mechanics,
                    "core_genre": core_genre,
                },
            )

        # 3. Allowed claim verification (if whitelist exists)
        allowed_claims = game_dna.get("allowed_ad_claims", [])
        score = 5.0
        warnings = []
        if allowed_claims and not any(str(claim).lower() in combined_text for claim in allowed_claims):
            warnings.append("Ad creative does not incorporate any primary allowed brand claims.")
            score = 3.8

        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=score,
            message="Game truth verification passed: no misleading mechanics or brand violations detected.",
            details={
                "core_genre": core_genre,
                "verified_claims_count": len(text_corpus),
                "warnings": warnings,
            },
        )
