"""
Unit and integration tests for the 7-Layer Quality Gate Pipeline.
Validates acceptance criteria: broken playable fails TechnicalGate and halts pipeline.
CreativeForge Intelligence Studio v3.0 - Module M07.
"""

import pytest
from services.worker_evaluation.gates.base import (
    GateExecutionContext,
    GateSeverity,
    GateStatus,
)
from services.worker_evaluation.gates.schema_gate import SchemaGate
from services.worker_evaluation.gates.technical_gate import TechnicalGate
from services.worker_evaluation.gates.game_truth_gate import GameTruthGate
from services.worker_evaluation.gates.visual_gate import VisualGate
from services.worker_evaluation.gates.similarity_gate import SimilarityGate
from services.worker_evaluation.gates.llm_judge_gate import LLMJudgeGate
from services.worker_evaluation.gates.human_review_gate import HumanReviewGate
from services.worker_evaluation.models import OverallVerdict
from services.worker_evaluation.pipeline import QualityGatePipeline


@pytest.mark.asyncio
async def test_schema_gate_validation():
    gate = SchemaGate()

    # Invalid: missing required fields
    bad_context = GateExecutionContext(artifact={"title": "incomplete"})
    res = await gate.evaluate(bad_context)
    assert res.status == GateStatus.FAILED
    assert res.severity == GateSeverity.FATAL
    assert res.failure_code == "SCHEMA_MISSING_REQUIRED_FIELD"

    # Valid image artifact
    good_context = GateExecutionContext(
        artifact={
            "artifact_id": "art_01",
            "run_id": "run_01",
            "type": "image",
            "storage_ref": "s3://bucket/image.png",
            "sha256": "a" * 64,
            "bytes": 50000,
            "media_meta": {"width": 1080, "height": 1920, "format": "png"},
        }
    )
    res_good = await gate.evaluate(good_context)
    assert res_good.status == GateStatus.PASSED
    assert res_good.score == 5.0


@pytest.mark.asyncio
async def test_technical_gate_broken_playable_fails_fatal():
    """
    CRITICAL ACCEPTANCE CRITERION:
    A broken playable with runtime JS errors must fail TechnicalGate and halt the pipeline.
    """
    gate = TechnicalGate()

    # Playable with console JS error
    context = GateExecutionContext(
        artifact={
            "artifact_id": "art_play_01",
            "run_id": "run_01",
            "type": "playable_zip",
            "storage_ref": "s3://bucket/playable.zip",
            "sha256": "b" * 64,
            "bytes": 1024 * 1024,
            "media_meta": {"entrypoint": "index.html"},
        },
        playwright_report={
            "page_load_ms": 1200,
            "js_errors": ["Uncaught TypeError: Cannot read properties of undefined (reading 'swapTiles')"],
            "http_errors": [],
            "interaction_passed": False,
        },
    )

    res = await gate.evaluate(context)
    assert res.status == GateStatus.FAILED
    assert res.severity == GateSeverity.FATAL
    assert res.is_blocking is True
    assert res.failure_code == "PLAYWRIGHT_JS_ERROR"
    assert "runtime JavaScript errors" in res.message


@pytest.mark.asyncio
async def test_pipeline_halts_on_fatal_technical_gate():
    """Verify that when TechnicalGate fails, subsequent gates are not executed."""
    pipeline = QualityGatePipeline()

    context = GateExecutionContext(
        artifact={
            "artifact_id": "art_play_01",
            "run_id": "run_01",
            "type": "playable_zip",
            "storage_ref": "s3://bucket/playable.zip",
            "sha256": "c" * 64,
            "bytes": 1024 * 500,
            "media_meta": {"entrypoint": "index.html"},
        },
        playwright_report={
            "page_load_ms": 900,
            "js_errors": ["ReferenceError: Phaser is not defined"],
            "http_errors": [],
            "interaction_passed": False,
        },
    )

    report = await pipeline.run(context)
    assert report.overall_verdict == OverallVerdict.FAILED
    assert report.blocking_failure is not None
    assert "technical_gate" in report.blocking_failure
    # Schema passed, Technical failed, and execution halted (so total gates executed == 2)
    assert len(report.gate_results) == 2
    assert report.gate_results[0].gate_name == "schema_gate"
    assert report.gate_results[1].gate_name == "technical_gate"
    assert report.gate_results[1].status == GateStatus.FAILED


@pytest.mark.asyncio
async def test_game_truth_gate_brand_violation():
    gate = GameTruthGate()

    context = GateExecutionContext(
        artifact={"type": "image", "title": "Play Real Money Roulette!"},
        game_dna={
            "mechanics_spec": {"genre": "Match-3 Puzzle", "disallowed_mechanics": ["pin_pull"]},
            "do_not_generate": ["gambling", "real money", "blood"],
        },
        creative_hypothesis={
            "intended_hook": "Win real money by spinning the wheel!",
            "creative_mechanism": "Casino roulette",
        },
    )

    res = await gate.evaluate(context)
    assert res.status == GateStatus.FAILED
    assert res.failure_code == "BRAND_CONSTRAINT_VIOLATION"


@pytest.mark.asyncio
async def test_visual_gate_aspect_ratio_and_resolution():
    gate = VisualGate()

    # Horizontal 16:9 image when 9:16 vertical is expected
    bad_aspect_context = GateExecutionContext(
        artifact={
            "type": "image",
            "media_meta": {"width": 1920, "height": 1080, "format": "png"},
        },
        options={"target_aspect_ratio": "9:16"},
    )
    res = await gate.evaluate(bad_aspect_context)
    assert res.status == GateStatus.FAILED
    assert res.failure_code == "VISUAL_INVALID_ASPECT_RATIO"

    # Good 9:16 vertical
    good_context = GateExecutionContext(
        artifact={
            "type": "image",
            "media_meta": {"width": 1080, "height": 1920, "format": "png", "contrast_ratio": 5.0},
        },
        options={"target_aspect_ratio": "9:16"},
    )
    res_good = await gate.evaluate(good_context)
    assert res_good.status == GateStatus.PASSED


@pytest.mark.asyncio
async def test_similarity_gate_warning_and_strict():
    gate = SimilarityGate()

    # Perceptual hash near duplicate
    context = GateExecutionContext(
        artifact={"type": "image", "media_meta": {"phash": "ffffffff00000000"}},
        corpus_references=[
            {"id": "ref_competitor_ad", "name": "Competitor Gem Ad", "phash": "ffffffff00000001"}
        ],
        options={"similarity_threshold": 0.85, "strict_similarity": False},
    )
    res = await gate.evaluate(context)
    assert res.status == GateStatus.WARNING
    assert res.failure_code == "EXACT_DUPLICATE_DETECTED" or res.failure_code == "SIMILARITY_THRESHOLD_EXCEEDED"

    # Strict mode turns warning into failure
    context.options["strict_similarity"] = True
    res_strict = await gate.evaluate(context)
    assert res_strict.status == GateStatus.FAILED


@pytest.mark.asyncio
async def test_llm_judge_gate_scoring():
    gate = LLMJudgeGate()

    context = GateExecutionContext(
        artifact={
            "type": "image",
            "media_meta": {"width": 1080, "height": 1920, "cta_text": "Play Now", "format": "png"},
        },
        creative_hypothesis={
            "intended_hook": "Match three gems to defeat the dragon!",
            "creative_mechanism": "Cascading blast mechanic",
            "novelty_rationale": "Introduces dynamic elemental chain reactions.",
        },
    )

    res = await gate.evaluate(context)
    assert res.status == GateStatus.PASSED
    assert res.score >= 3.0
    assert "overall_rubric_score" in res.details
    assert "criteria_scores" in res.details


@pytest.mark.asyncio
async def test_human_review_gate():
    gate = HumanReviewGate()

    # Queues for review when required
    context = GateExecutionContext(
        artifact={"artifact_id": "art_ambiguous_01", "run_id": "run_01"},
        options={"require_human_approval": True},
    )
    res = await gate.evaluate(context)
    assert res.status == GateStatus.PENDING_REVIEW
    assert res.failure_code == "AWAITING_HUMAN_DECISION"

    # Approves when human decision is recorded
    context.human_decision = {
        "decision": "approved",
        "reviewer_id": "usr_art_director",
        "reason": "Vibrant colors and excellent hook pacing.",
    }
    res_appr = await gate.evaluate(context)
    assert res_appr.status == GateStatus.PASSED
    assert res_appr.score == 5.0
