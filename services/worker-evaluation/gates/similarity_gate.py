"""
Gate 5: SimilarityGate - Perceptual hash and vector cosine similarity scanner against reference corpus.
Flags intellectual property risks, excessive visual similarity, and near-duplicate assets.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple
from services.worker_evaluation.gates.base import (
    BaseGate,
    GateExecutionContext,
    GateResult,
    GateSeverity,
    GateStatus,
)


def hamming_distance(hex1: str, hex2: str) -> int:
    """Calculate the Hamming distance between two hex-encoded perceptual hashes."""
    try:
        val1 = int(hex1, 16)
        val2 = int(hex2, 16)
        xor_val = val1 ^ val2
        return bin(xor_val).count("1")
    except (ValueError, TypeError):
        return 64


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Compute cosine similarity between two float vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = math.sqrt(sum(a * a for a in vec1))
    norm_b = math.sqrt(sum(b * b for b in vec2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)


class SimilarityGate(BaseGate):
    """Gate 5: Perceptual Hash and Embedding Similarity Gate."""

    gate_name: str = "similarity_gate"
    gate_version: str = "1.0.0"
    is_fatal: bool = False

    async def evaluate(self, context: GateExecutionContext) -> GateResult:
        artifact = context.artifact or {}
        media_meta = artifact.get("media_meta", {})
        corpus = context.corpus_references or []
        options = context.options or {}

        similarity_threshold = options.get("similarity_threshold", 0.85)
        strict_mode = options.get("strict_similarity", False)

        current_phash = media_meta.get("phash") or media_meta.get("dhash")
        current_embedding = media_meta.get("embedding")  # Optional vector

        if not corpus:
            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=GateStatus.PASSED,
                severity=GateSeverity.INFO,
                score=5.0,
                message="No corpus reference set provided; perceptual similarity check skipped.",
                details={"corpus_size": 0},
            )

        highest_similarity = 0.0
        closest_match: Optional[Dict[str, Any]] = None
        match_type = "none"

        for ref in corpus:
            ref_id = ref.get("id") or ref.get("asset_id") or "unknown_ref"
            ref_phash = ref.get("phash") or ref.get("dhash")
            ref_embedding = ref.get("embedding")

            # 1. Check Perceptual Hash if both available
            if current_phash and ref_phash:
                dist = hamming_distance(str(current_phash), str(ref_phash))
                # 64-bit hash: similarity = 1 - (dist / 64)
                phash_sim = max(0.0, 1.0 - (dist / 64.0))
                if phash_sim > highest_similarity:
                    highest_similarity = phash_sim
                    match_type = "phash"
                    closest_match = {
                        "reference_id": ref_id,
                        "reference_name": ref.get("name", "unnamed"),
                        "hamming_distance": dist,
                        "similarity": round(phash_sim, 4),
                        "provenance": ref.get("provenance", "external_catalog"),
                    }

            # 2. Check Embedding Cosine Similarity if both available
            if current_embedding and ref_embedding and isinstance(current_embedding, list) and isinstance(ref_embedding, list):
                cos_sim = cosine_similarity(current_embedding, ref_embedding)
                if cos_sim > highest_similarity:
                    highest_similarity = cos_sim
                    match_type = "embedding_cosine"
                    closest_match = {
                        "reference_id": ref_id,
                        "reference_name": ref.get("name", "unnamed"),
                        "similarity": round(cos_sim, 4),
                        "provenance": ref.get("provenance", "external_catalog"),
                    }

        # Determine gate status
        if highest_similarity >= similarity_threshold:
            # Score scales down as similarity approaches 1.0
            score = max(0.0, (1.0 - highest_similarity) * 5.0)
            status = GateStatus.FAILED if strict_mode else GateStatus.WARNING
            severity = GateSeverity.ERROR if strict_mode else GateSeverity.WARNING
            failure_code = "EXACT_DUPLICATE_DETECTED" if highest_similarity >= 0.98 else "SIMILARITY_THRESHOLD_EXCEEDED"

            return GateResult(
                gate_name=self.gate_name,
                gate_version=self.gate_version,
                status=status,
                severity=severity,
                score=round(score, 2),
                failure_code=failure_code,
                message=(
                    f"High similarity detected ({highest_similarity:.1%}) against reference "
                    f"'{closest_match.get('reference_name')}' exceeding threshold ({similarity_threshold:.1%})."
                ),
                details={
                    "highest_similarity": round(highest_similarity, 4),
                    "threshold": similarity_threshold,
                    "match_type": match_type,
                    "closest_match": closest_match,
                    "strict_mode": strict_mode,
                },
            )

        # Clean pass
        score = 5.0 - (highest_similarity * 1.5)
        return GateResult(
            gate_name=self.gate_name,
            gate_version=self.gate_version,
            status=GateStatus.PASSED,
            severity=GateSeverity.INFO,
            score=round(score, 2),
            message=f"Similarity scan passed. Highest similarity was {highest_similarity:.1%} (below threshold {similarity_threshold:.1%}).",
            details={
                "highest_similarity": round(highest_similarity, 4),
                "threshold": similarity_threshold,
                "corpus_size": len(corpus),
            },
        )
