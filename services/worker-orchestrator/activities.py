"""Temporal activities and mock executors for all CreativeForge pipeline nodes."""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

try:
    from temporalio import activity
except ImportError:
    # Fallback dummy decorator for standalone execution when temporalio is used without server
    class _ActivityMock:
        @staticmethod
        def defn(fn=None, name=None):
            def decorator(f):
                return f
            return decorator(fn) if fn else decorator
    activity = _ActivityMock()

logger = logging.getLogger("worker_orchestrator.activities")


class NodeActivityInput(BaseModel):
    """Input payload delivered to an activity execution."""
    run_id: str
    node_id: str
    node_type: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    current_attempt: int = 1
    simulate_failures: int = Field(default=0, description="Inject N failures before success")


class NodeActivityOutput(BaseModel):
    """Output response from an activity execution."""
    run_id: str
    node_id: str
    node_type: str
    status: str = "SUCCESS"
    attempt: int = 1
    outputs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    completed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ActivityExecutionError(Exception):
    """Raised when activity execution fails during a run attempt."""
    def __init__(self, message: str, attempt: int, can_retry: bool = True):
        super().__init__(message)
        self.attempt = attempt
        self.can_retry = can_retry


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def execute_node_logic(input_data: NodeActivityInput) -> Dict[str, Any]:
    """
    Deterministic domain executor for all node types in CreativeForge pipeline.
    Produces valid typed payloads compliant with Master Plan Section H.
    """
    nt = input_data.node_type
    run_id = input_data.run_id
    node_id = input_data.node_id

    # Simulated failure injection for retry testing
    if input_data.simulate_failures > 0 and input_data.current_attempt <= input_data.simulate_failures:
        raise ActivityExecutionError(
            f"Simulated transient error in node '{node_id}' ({nt}) on attempt {input_data.current_attempt}",
            attempt=input_data.current_attempt,
            can_retry=True,
        )

    # 1. Market Nodes
    if nt == "Source Fetch":
        snapshot_id = f"snap_{run_id}_{node_id[:6]}"
        return {
            "snapshot": {
                "source_id": "apple_charts_top_free",
                "snapshot_id": snapshot_id,
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "region": input_data.config.get("region", "US"),
                "records_count": 100,
                "raw_hash": _sha256(snapshot_id),
            }
        }
    elif nt == "Deduplicate":
        return {
            "snapshot": {
                "deduplicated": True,
                "records_retained": 85,
                "removed_duplicates": 15,
                "content_hash": _sha256(f"dedup_{run_id}"),
            }
        }
    elif nt == "Genre Classifier":
        return {
            "genre_report": {
                "top_genre": "Match-3 Puzzle",
                "confidence": 0.94,
                "tags": ["casual", "puzzle", "tile_match", "renovation"],
            }
        }
    elif nt == "Ad Pattern Extract":
        return {
            "pattern_report": {
                "hooks": ["satisfying_clear", "near_miss_dilemma", "puzzle_fail"],
                "pacing": "fast",
                "dominant_colors": ["vibrant_yellow", "royal_purple"],
            }
        }
    elif nt == "Trend Synthesis":
        return {
            "trend_report": {
                "signals": ["High engagement with ASMR clearing", "Character reaction hooks outperform"],
                "confidence": "high",
                "evidence_refs": ["https://appstore.apple.com/charts/top-free/us"],
                "limitations": "US region iOS data only",
            }
        }

    # 2. Profile Nodes
    elif nt == "Game Asset Import":
        return {
            "game_assets": {
                "sprites_count": 48,
                "audio_count": 6,
                "palette": ["#FFD700", "#FF4500", "#1E90FF", "#32CD32"],
                "brand_rights_verified": True,
            }
        }
    elif nt == "Game DNA Extract":
        return {
            "draft": {
                "mechanics": "Match-3 swap grid 8x8",
                "style_tokens": ["glossy", "cartoon", "playful"],
                "allowed_claims": ["Swap 3 tiles", "Unlock power-ups"],
                "do_not_generate": ["Misleading pin-pull mechanics", "Violent fails"],
            }
        }
    elif nt == "Human Confirm Mechanics":
        return {
            "game_profile_version": {
                "version_id": f"gp_{run_id}",
                "mechanics_confirmed": True,
                "frozen_at": datetime.now(timezone.utc).isoformat(),
            }
        }

    # 3. Concept Nodes
    elif nt == "Creative Brief":
        return {
            "creative_brief": {
                "target_audience": "Casual players 25-45",
                "primary_goal": "Lower CPI with authentic Match-3 hook",
                "duration_seconds": 15,
            }
        }
    elif nt == "Hypothesis Generate":
        return {
            "hypotheses": [
                {
                    "hypothesis_id": f"hyp_{run_id}_1",
                    "audience": "Match-3 enthusiasts",
                    "hook": "Satisfying 5-gem rainbow combo with tactile sound",
                    "expected_metric": "CTR > 4.2%",
                },
                {
                    "hypothesis_id": f"hyp_{run_id}_2",
                    "audience": "Casual solvers",
                    "hook": "1 move left critical decision puzzle",
                    "expected_metric": "IPM > 25",
                },
            ]
        }
    elif nt == "Hypothesis Rank":
        return {
            "ranked_concepts": {
                "ranking": [
                    {"hypothesis_id": f"hyp_{run_id}_1", "score": 0.88, "rank": 1},
                    {"hypothesis_id": f"hyp_{run_id}_2", "score": 0.81, "rank": 2},
                ]
            }
        }
    elif nt == "Concept Board Render":
        return {
            "concept_boards": [
                {
                    "board_id": f"board_{run_id}_1",
                    "preview_url": f"/artifacts/{run_id}/board_1.png",
                    "score": 0.88,
                }
            ]
        }
    elif nt == "User Select Board":
        return {
            "concept_spec": {
                "selected_board_id": f"board_{run_id}_1",
                "hook_concept": "Satisfying rainbow combo",
                "target_format": "9:16 vertical video & HTML5 playable",
            }
        }

    # 4. Production Nodes
    elif nt == "Prompt Builder":
        return {
            "asset_plan": {
                "visual_shots": ["0-3s: glowing tile grid", "3-10s: cascading matches", "10-15s: celebration & CTA"],
                "comfy_prompts": ["masterpiece, glossy gems, phaser game board, 8k resolution"],
            }
        }
    elif nt == "Image Generator":
        img_id = f"img_{run_id}_{node_id[:4]}"
        return {
            "images": [
                {
                    "artifact_id": img_id,
                    "storage_ref": f"s3://creativeforge-assets/{run_id}/frame_01.png",
                    "sha256": _sha256(img_id),
                    "resolution": "1080x1920",
                }
            ]
        }
    elif nt == "Storyboard Planner":
        return {
            "storyboard": {
                "total_duration": 15.0,
                "fps": 30,
                "scenes": ["Hook Scene", "Gameplay Simulation", "Endcard CTA"],
            }
        }
    elif nt == "Video Generator" or nt == "Remotion Render":
        vid_id = f"vid_{run_id}_{node_id[:4]}"
        return {
            "video_asset": {
                "artifact_id": vid_id,
                "storage_ref": f"s3://creativeforge-assets/{run_id}/creative_9x16.mp4",
                "sha256": _sha256(vid_id),
                "duration_seconds": 15.0,
                "codec": "h264",
            }
        }
    elif nt == "Playable Spec":
        return {
            "playable_spec": {
                "grid_size": [8, 8],
                "moves_limit": 5,
                "target_score": 1000,
                "winning_cta": "Play Full Game!",
            }
        }
    elif nt == "Phaser Codegen":
        return {
            "source_bundle": {
                "entrypoint": "src/game.ts",
                "files_count": 8,
                "bundle_hash": _sha256(f"phaser_{run_id}"),
            }
        }
    elif nt == "Sandbox Build":
        bundle_id = f"playable_{run_id}"
        return {
            "playable_bundle": {
                "artifact_id": bundle_id,
                "storage_ref": f"s3://creativeforge-assets/{run_id}/playable_bundle.zip",
                "sha256": _sha256(bundle_id),
                "entrypoint": "index.html",
                "size_bytes": 482100,
            }
        }
    elif nt == "Browser QA":
        return {
            "evaluation_report": {
                "gate": "TechnicalGate",
                "passed": True,
                "js_runtime_errors": 0,
                "first_interaction_delay_ms": 120,
            }
        }

    # 5. Quality & Control Nodes
    elif nt == "Schema Validate":
        return {
            "evaluation_report": {
                "gate": "SchemaGate",
                "passed": True,
                "schema_version": 1,
            }
        }
    elif nt == "Visual QA":
        return {
            "evaluation_report": {
                "gate": "VisualGate",
                "passed": True,
                "contrast_ratio": 4.8,
                "cta_legibility": "HIGH",
            }
        }
    elif nt == "Mechanics QA":
        return {
            "evaluation_report": {
                "gate": "GameTruthGate",
                "passed": True,
                "misleading_gameplay_score": 0.0,
            }
        }
    elif nt == "Similarity Risk":
        return {
            "risk_report": {
                "max_similarity": 0.22,
                "risk_level": "LOW",
                "flagged": False,
            }
        }
    elif nt == "Quality Gate":
        return {
            "pass_fail": {
                "verdict": "PASSED",
                "gates_checked": 6,
                "gates_passed": 6,
            }
        }
    elif nt == "Human Approval":
        return {
            "approval_decision": {
                "approved": True,
                "actor": "qa_lead",
                "comments": "High quality asset, ready for campaign delivery.",
            }
        }
    elif nt == "Budget Gate":
        return {
            "decision": {
                "approved": True,
                "budget_check": "WITHIN_LIMITS",
            }
        }
    elif nt == "Artifact Save":
        return {
            "artifact_ref": {
                "saved_ref": f"s3://creativeforge-ledger/{run_id}/{node_id}_artifact",
                "sha256": _sha256(f"{run_id}_{node_id}"),
            }
        }
    elif nt == "Export":
        return {
            "export_manifest": {
                "campaign_bundle": f"export_{run_id}.zip",
                "assets_included": ["video_9x16.mp4", "playable_bundle.zip", "preview.png"],
                "ready_for_ad_network": True,
            }
        }

    # Default fallback
    return {
        "result": f"Executed node '{node_id}' of type '{nt}' successfully.",
        "hash": _sha256(f"{run_id}_{node_id}"),
    }


@activity.defn(name="execute_node_activity")
async def execute_node_activity(input_data: NodeActivityInput) -> NodeActivityOutput:
    """
    Temporal Activity implementation that executes a node's domain logic.
    Handles exceptions, records attempt counts, and produces typed output.
    """
    logger.info(
        "Starting activity for node '%s' (type: %s, attempt: %d)",
        input_data.node_id,
        input_data.node_type,
        input_data.current_attempt,
    )

    outputs = execute_node_logic(input_data)

    return NodeActivityOutput(
        run_id=input_data.run_id,
        node_id=input_data.node_id,
        node_type=input_data.node_type,
        status="SUCCESS",
        attempt=input_data.current_attempt,
        outputs=outputs,
        metadata={
            "executed_by": "worker-orchestrator",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
