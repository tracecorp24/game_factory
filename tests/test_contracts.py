"""
Unit tests for Pydantic v2 core contracts, taxonomy, and integrity hashes.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
from pydantic import ValidationError

from packages.contracts.common import generate_uuid, utc_now, compute_sha256
from packages.contracts.events import EventEnvelope, EventType
from packages.contracts.records import (
    TokenUsageRecord,
    CostEntryRecord,
    ArtifactRecord,
    RunManifestRecord,
)
from packages.contracts.artifacts import (
    TrendSnapshot,
    TrendReport,
    GameProfileVersion,
    CreativeHypothesis,
    ConceptSpec,
    ConceptBoard,
    ContextBundle,
    AssetPlan,
    ImageAsset,
    VideoAsset,
    PlayableSpec,
    PlayableBundle,
    EvaluationReport,
    ExperimentResult,
)


def test_event_envelope_creation_and_integrity():
    event = EventEnvelope.create(
        event_type=EventType.MODEL_CALL_FINISHED,
        project_id="proj_1",
        campaign_id="camp_1",
        request_id="req_1",
        run_id="run_1",
        run_seq=1,
        payload_preview={"model": "gpt-4o", "tokens": 150},
    )

    assert event.event_type == EventType.MODEL_CALL_FINISHED
    assert event.run_seq == 1
    assert event.verify_integrity() is True

    # Tampering test: altering payload must fail integrity verification
    event.payload_preview["tokens"] = 999
    assert event.verify_integrity() is False


def test_invalid_event_type_raises_validation_error():
    with pytest.raises(ValidationError):
        EventEnvelope(
            event_id=generate_uuid(),
            event_type="INVALID_NON_EXISTENT_EVENT_TYPE",  # Must fail taxonomy enum check
            project_id="proj_1",
            campaign_id="camp_1",
            request_id="req_1",
            run_id="run_1",
            run_seq=1,
            integrity_hash="sha256:dummy",
        )


def test_token_usage_record_no_double_counting():
    record = TokenUsageRecord(
        input_tokens=1000,
        output_tokens=200,
        cached_input_tokens=400,
        usage_source="provider_reported",
    )
    # Total tokens auto-calculated as input + output
    assert record.total_tokens == 1200
    assert record.cached_input_tokens == 400


def test_token_usage_negative_tokens_rejected():
    with pytest.raises(ValidationError):
        TokenUsageRecord(
            input_tokens=-5,
            output_tokens=100,
            usage_source="provider_reported",
        )


def test_cost_entry_record():
    cost = CostEntryRecord(
        amount=0.015,
        currency="USD",
        cost_kind="llm_token",
        status="actual",
    )
    assert cost.amount == 0.015
    assert cost.cost_kind == "llm_token"

    with pytest.raises(ValidationError):
        CostEntryRecord(
            amount=-1.0,  # Negative cost not allowed
            cost_kind="llm_token",
            status="actual",
        )


def test_artifact_record():
    art = ArtifactRecord(
        run_id="run_101",
        type="image",
        storage_ref="s3://bucket/test.png",
        sha256="sha256:abcd1234",
        bytes=10240,
        media_meta={"width": 1080, "height": 1920},
    )
    assert art.type == "image"
    assert art.bytes == 10240


def test_run_manifest_record_freeze_and_hash():
    manifest = RunManifestRecord.create_manifest(
        run_id="run_42",
        workflow_version_id="wfv_1",
        game_profile_version_id="gpv_1",
        prompt_versions={"ideation": "v1.2"},
        model_versions={"ideation": "claude-3-5-sonnet"},
        code_commit="git_commit_abcdef",
    )
    assert manifest.run_id == "run_42"
    assert manifest.sha256.startswith("sha256:")
    assert manifest.prompt_versions["ideation"] == "v1.2"


def test_typed_artifacts_contracts():
    hypothesis = CreativeHypothesis(
        project_id="proj_1",
        audience="casual gamers",
        genre="match3",
        intended_hook="Princess in peril",
        emotional_arc="urgency to relief",
        creative_mechanism="swipe to drop rope",
        falsification_condition="CTR < 1.5%",
        limitations=["2D assets only"],
        novelty_rationale="Physics puzzle fusion with match-3",
        ranking_score=0.88,
    )
    assert hypothesis.ranking_score == 0.88

    eval_report = EvaluationReport(
        rubric_id="rubric_v3",
        overall_passed=True,
        scores={"game_truth": 1.0, "technical": 1.0, "llm_judge": 4.8},
    )
    assert eval_report.overall_passed is True


def test_observatory_demo_events_fixture_validity():
    fixture_path = Path("packages/test-fixtures/observatory-demo-events.jsonl")
    assert fixture_path.exists(), "observatory-demo-events.jsonl must exist"

    lines = fixture_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 10, "Demo scenario must have exactly 10 steps"

    previous_seq = 0
    for line in lines:
        data = json.loads(line)
        event = EventEnvelope.model_validate(data)
        assert event.run_id == "run_88"
        assert event.run_seq == previous_seq + 1
        assert event.verify_integrity() is True
        previous_seq = event.run_seq
