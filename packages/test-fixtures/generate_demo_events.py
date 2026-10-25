"""
Generates synthetic observatory-demo-events.jsonl for run_88 adhering to Master Plan Section I3.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

# Ensure workspace packages are importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from packages.contracts.events import EventEnvelope, EventType


def generate_run_88_events() -> list[EventEnvelope]:
    project_id = "proj_royal_match3"
    campaign_id = "camp_autumn_rescue_2026"
    request_id = "req_7"
    run_id = "run_88"
    wf_version_id = "wfv_4"
    profile_version_id = "gpv_2"

    events: list[EventEnvelope] = []
    seq = 1

    # 1. 14:00:00 - REQUEST_RECEIVED
    t1 = datetime(2026, 10, 25, 14, 0, 0, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.REQUEST_RECEIVED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            occurred_at=t1,
            actor_type="user",
            actor_id="user_marketing_lead",
            payload_preview={
                "brief_prompt": "Match-3 rescue concept featuring royal rescue hook",
                "game_profile_version": profile_version_id,
                "target_duration_sec": 15,
            },
        )
    )
    seq += 1

    # 2. 14:00:01 - RUN_STARTED (Workflow & Game DNA frozen)
    t2 = datetime(2026, 10, 25, 14, 0, 1, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.RUN_STARTED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            occurred_at=t2,
            actor_type="system",
            actor_id="workflow_orchestrator",
            payload_preview={
                "frozen_manifest_sha256": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "workflow_version": wf_version_id,
                "game_profile_version": profile_version_id,
                "budget_limit_usd": 15.0,
            },
        )
    )
    seq += 1

    # 3. 14:00:03 - AGENT_STARTED (concept-agent)
    t3 = datetime(2026, 10, 25, 14, 0, 3, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.AGENT_STARTED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_ideation_01",
            agent_id="concept_agent",
            occurred_at=t3,
            actor_type="agent",
            actor_id="concept_agent",
            payload_preview={
                "agent_role": "Concept Ideation & Hypothesis Generator",
                "context_bundle_id": "cb_88_01",
                "max_hypotheses": 4,
            },
        )
    )
    seq += 1

    # 4. 14:00:04 - MODEL_CALL_FINISHED (1200 input, 250 output tokens)
    t4 = datetime(2026, 10, 25, 14, 0, 4, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.MODEL_CALL_FINISHED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_ideation_01",
            attempt_id="att_ideation_01",
            agent_id="concept_agent",
            occurred_at=t4,
            actor_type="worker",
            actor_id="model_gateway",
            payload_preview={
                "provider": "anthropic",
                "model": "claude-3-5-sonnet",
                "input_tokens": 1200,
                "output_tokens": 250,
                "cached_tokens": 400,
                "usage_source": "provider_reported",
                "cost_usd": 0.00735,
            },
        )
    )
    seq += 1

    # 5. 14:00:06 - ARTIFACT_CREATED (artifact_a: mockup image 1)
    t5 = datetime(2026, 10, 25, 14, 0, 6, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.ARTIFACT_CREATED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_mockup_01",
            agent_id="image_worker",
            occurred_at=t5,
            actor_type="worker",
            actor_id="comfyui_adapter",
            payload_preview={
                "artifact_id": "art_img_88a",
                "type": "image",
                "storage_ref": "s3://creativeforge/run_88/mockup_a.png",
                "sha256": "sha256:7b52009b64fd0a2a49e6d8a939753077792b0554",
                "resolution": "1080x1920",
                "bytes": 1450200,
            },
        )
    )
    seq += 1

    # 6. 14:00:07 - ARTIFACT_CREATED (artifact_b: mockup image 2)
    t6 = datetime(2026, 10, 25, 14, 0, 7, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.ARTIFACT_CREATED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_mockup_01",
            agent_id="image_worker",
            occurred_at=t6,
            actor_type="worker",
            actor_id="comfyui_adapter",
            payload_preview={
                "artifact_id": "art_img_88b",
                "type": "image",
                "storage_ref": "s3://creativeforge/run_88/mockup_b.png",
                "sha256": "sha256:9f86d081884c7d659a2feaa0c55ad015a3bf4f1b",
                "resolution": "1080x1920",
                "bytes": 1520100,
            },
        )
    )
    seq += 1

    # 7. 14:00:15 - ATTEMPT_FAILED (video node attempt #1 timeout)
    t7 = datetime(2026, 10, 25, 14, 0, 15, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.ATTEMPT_FAILED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_video_01",
            attempt_id="att_video_88_1",
            agent_id="video_worker",
            occurred_at=t7,
            actor_type="worker",
            actor_id="temporal_activity_worker",
            payload_preview={
                "attempt_no": 1,
                "error_code": "PROVIDER_TIMEOUT",
                "error_message": "Primary video render service exceeded 30s timeout threshold",
                "backoff_ms": 3000,
                "retry_eligible": True,
            },
        )
    )
    seq += 1

    # 8. 14:00:18 - MODEL_FALLBACK_USED (attempt #2 with secondary model)
    t8 = datetime(2026, 10, 25, 14, 0, 18, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.MODEL_FALLBACK_USED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_video_01",
            attempt_id="att_video_88_2",
            agent_id="video_worker",
            occurred_at=t8,
            actor_type="worker",
            actor_id="model_gateway",
            payload_preview={
                "attempt_no": 2,
                "primary_model": "video-gen-v1-hd",
                "fallback_model": "video-gen-v1-fast",
                "fallback_reason": "failover_on_primary_timeout",
            },
        )
    )
    seq += 1

    # 9. 14:00:28 - ARTIFACT_CREATED (Video asset with lineage to image_a and image_b)
    t9 = datetime(2026, 10, 25, 14, 0, 28, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.ARTIFACT_CREATED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_video_01",
            attempt_id="att_video_88_2",
            agent_id="video_worker",
            occurred_at=t9,
            actor_type="worker",
            actor_id="remotion_renderer",
            payload_preview={
                "artifact_id": "art_vid_88_final",
                "type": "video",
                "storage_ref": "s3://creativeforge/run_88/rescue_hook_9x16.mp4",
                "sha256": "sha256:5d41402abc4b2a76b9719d911017c592",
                "duration_sec": 14.8,
                "aspect_ratio": "9:16",
                "bytes": 8420100,
                "parent_artifacts": ["art_img_88a", "art_img_88b"],
            },
        )
    )
    seq += 1

    # 10. 14:00:34 - QUALITY_GATE_PASSED & APPROVAL_REQUESTED
    t10 = datetime(2026, 10, 25, 14, 0, 34, tzinfo=timezone.utc)
    events.append(
        EventEnvelope.create(
            event_type=EventType.APPROVAL_REQUESTED,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=seq,
            workflow_version_id=wf_version_id,
            node_execution_id="node_qa_01",
            agent_id="qa_evaluator",
            occurred_at=t10,
            actor_type="system",
            actor_id="quality_gate_pipeline",
            payload_preview={
                "technical_gate": "PASSED",
                "game_truth_gate": "PASSED",
                "visual_contrast_gate": "PASSED",
                "originality_gate": "WARNING_SIMILARITY_0.71",
                "llm_judge_score": 4.5,
                "requires_human_approval": True,
                "approval_ticket_id": "appr_ticket_88",
            },
        )
    )

    return events


def main() -> None:
    events = generate_run_88_events()
    output_dir = Path("packages/test-fixtures")
    output_dir.mkdir(parents=True, exist_ok=True)
    target_file = output_dir / "observatory-demo-events.jsonl"

    with open(target_file, "w", encoding="utf-8") as f:
        for ev in events:
            # Export as valid JSON string per line
            line = ev.model_dump_json()
            f.write(line + "\n")

    print(f"Successfully generated {len(events)} events in {target_file}")


if __name__ == "__main__":
    main()
