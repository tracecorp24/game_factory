"""Complete catalog of node definitions for CreativeForge v3.0."""

from __future__ import annotations

from typing import Dict, List, Optional
from .types import (
    ExecutorType,
    NodeCategory,
    NodeDefinition,
    PortDefinition,
    PortType,
    RetryPolicyConfig,
)


def _port(name: str, port_type: PortType, description: str = "", required: bool = True, allows_multiple: bool = False) -> PortDefinition:
    return PortDefinition(
        name=name,
        port_type=port_type,
        description=description,
        required=required,
        allows_multiple=allows_multiple,
    )


def _default_retry() -> RetryPolicyConfig:
    return RetryPolicyConfig(
        max_attempts=3,
        initial_interval_seconds=1.0,
        backoff_coefficient=2.0,
        maximum_interval_seconds=30.0,
    )


NODE_DEFINITIONS: Dict[str, NodeDefinition] = {
    # ------------------ MARKET ------------------
    "Source Fetch": NodeDefinition(
        node_type="Source Fetch",
        category=NodeCategory.MARKET,
        executor=ExecutorType.WORKER,
        description="Fetches raw ranking and store data from configured market sources",
        input_ports={"query": _port("query", PortType.SOURCE_QUERY, "Query parameters and filters")},
        output_ports={"snapshot": _port("snapshot", PortType.TREND_SNAPSHOT, "Raw collected snapshot")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["region", "period", "connector"],
    ),
    "Deduplicate": NodeDefinition(
        node_type="Deduplicate",
        category=NodeCategory.MARKET,
        executor=ExecutorType.WORKER,
        description="Deduplicates multiple trend snapshots by content SHA256 and time window",
        input_ports={"snapshots": _port("snapshots", PortType.TREND_SNAPSHOT_LIST, "Snapshots to deduplicate", allows_multiple=True)},
        output_ports={"snapshot": _port("snapshot", PortType.TREND_SNAPSHOT, "Clean deduplicated snapshot")},
        retry_policy=_default_retry(),
        timeout_seconds=60,
        ui_inspector_params=["similarity", "key"],
    ),
    "Genre Classifier": NodeDefinition(
        node_type="Genre Classifier",
        category=NodeCategory.MARKET,
        executor=ExecutorType.HYBRID,
        description="Classifies game titles and creatives into standard taxonomy genres",
        input_ports={"snapshot": _port("snapshot", PortType.TREND_SNAPSHOT, "Market snapshot")},
        output_ports={"genre_report": _port("genre_report", PortType.GENRE_REPORT, "Genre distribution and classifications")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["taxonomy", "threshold"],
    ),
    "Ad Pattern Extract": NodeDefinition(
        node_type="Ad Pattern Extract",
        category=NodeCategory.MARKET,
        executor=ExecutorType.HYBRID,
        description="Extracts visual, audio and narrative patterns from creative evidence",
        input_ports={"creative_evidence": _port("creative_evidence", PortType.CREATIVE_EVIDENCE_LIST, "Creative records", allows_multiple=True)},
        output_ports={"pattern_report": _port("pattern_report", PortType.PATTERN_REPORT, "Identified ad hook patterns")},
        retry_policy=_default_retry(),
        timeout_seconds=240,
        ui_inspector_params=["hook_tags", "batch"],
    ),
    "Trend Synthesis": NodeDefinition(
        node_type="Trend Synthesis",
        category=NodeCategory.MARKET,
        executor=ExecutorType.AGENT,
        description="Synthesizes genre data and creative patterns into an actionable Trend Report",
        input_ports={
            "genre_report": _port("genre_report", PortType.GENRE_REPORT, "Genre classification data"),
            "pattern_report": _port("pattern_report", PortType.PATTERN_REPORT, "Extracted ad patterns"),
        },
        output_ports={"trend_report": _port("trend_report", PortType.TREND_REPORT, "Synthesized trend report")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["model", "prompt_version"],
    ),

    # ------------------ PROFILE ------------------
    "Game Asset Import": NodeDefinition(
        node_type="Game Asset Import",
        category=NodeCategory.PROFILE,
        executor=ExecutorType.WORKER,
        description="Imports and validates official game art, sprites, and audio assets",
        input_ports={"files": _port("files", PortType.GAME_ASSETS, "Raw uploaded assets")},
        output_ports={"game_assets": _port("game_assets", PortType.GAME_ASSETS, "Cataloged game assets")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["rights", "format"],
    ),
    "Game DNA Extract": NodeDefinition(
        node_type="Game DNA Extract",
        category=NodeCategory.PROFILE,
        executor=ExecutorType.AGENT,
        description="Extracts visual style tokens, core mechanics, and brand constraints into draft profile",
        input_ports={"game_assets": _port("game_assets", PortType.GAME_ASSETS, "Game assets catalog")},
        output_ports={"draft": _port("draft", PortType.GAME_PROFILE_DRAFT, "Extracted profile draft")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["style_constraints"],
    ),
    "Human Confirm Mechanics": NodeDefinition(
        node_type="Human Confirm Mechanics",
        category=NodeCategory.PROFILE,
        executor=ExecutorType.HUMAN,
        description="Awaits manual human review and sign-off on extracted core game mechanics",
        can_pause=True,
        input_ports={"draft": _port("draft", PortType.GAME_PROFILE_DRAFT, "Draft to review")},
        output_ports={"game_profile_version": _port("game_profile_version", PortType.GAME_PROFILE_VERSION, "Frozen game profile version")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=86400,
        ui_inspector_params=["mandatory_checklist"],
    ),

    # ------------------ CONCEPT ------------------
    "Creative Brief": NodeDefinition(
        node_type="Creative Brief",
        category=NodeCategory.CONCEPT,
        executor=ExecutorType.FORM,
        description="Aggregates user campaign goals and brand profile into a formalized brief",
        input_ports={
            "user_brief": _port("user_brief", PortType.USER_BRIEF, "User inputs and campaign specs"),
            "game_profile": _port("game_profile", PortType.GAME_PROFILE_VERSION, "Approved brand/game profile"),
        },
        output_ports={"creative_brief": _port("creative_brief", PortType.CREATIVE_BRIEF, "Formalized creative brief")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=60,
        ui_inspector_params=["audience", "goals"],
    ),
    "Hypothesis Generate": NodeDefinition(
        node_type="Hypothesis Generate",
        category=NodeCategory.CONCEPT,
        executor=ExecutorType.AGENT,
        description="Generates grounded creative hypotheses combining market trends and Game DNA",
        input_ports={
            "trend_report": _port("trend_report", PortType.TREND_REPORT, "Evidence-based trend report"),
            "brief": _port("brief", PortType.CREATIVE_BRIEF, "Creative campaign brief"),
        },
        output_ports={"hypotheses": _port("hypotheses", PortType.CREATIVE_HYPOTHESIS_LIST, "Generated hypothesis list")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["count", "diversity"],
    ),
    "Hypothesis Rank": NodeDefinition(
        node_type="Hypothesis Rank",
        category=NodeCategory.CONCEPT,
        executor=ExecutorType.WORKER,
        description="Heuristic multi-factor ranking of hypotheses with calibrated rationale",
        input_ports={"hypotheses": _port("hypotheses", PortType.CREATIVE_HYPOTHESIS_LIST, "Unranked hypotheses")},
        output_ports={"ranked_concepts": _port("ranked_concepts", PortType.RANKED_CONCEPTS, "Scored and ranked concepts")},
        retry_policy=_default_retry(),
        timeout_seconds=60,
        ui_inspector_params=["weights", "exclusions"],
    ),
    "Concept Board Render": NodeDefinition(
        node_type="Concept Board Render",
        category=NodeCategory.CONCEPT,
        executor=ExecutorType.AGENT,
        description="Renders visual storyboard cards and hook mockups for top concepts",
        input_ports={"ranked_concepts": _port("ranked_concepts", PortType.RANKED_CONCEPTS, "Top ranked concepts")},
        output_ports={"concept_boards": _port("concept_boards", PortType.CONCEPT_BOARD_LIST, "Rendered visual boards")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["mockup_count", "model"],
    ),
    "User Select Board": NodeDefinition(
        node_type="User Select Board",
        category=NodeCategory.CONCEPT,
        executor=ExecutorType.HUMAN,
        description="Interactive checkpoint: User selects winning concept board to produce",
        can_pause=True,
        input_ports={"concept_boards": _port("concept_boards", PortType.CONCEPT_BOARD_LIST, "Candidate boards")},
        output_ports={"concept_spec": _port("concept_spec", PortType.CONCEPT_SPEC, "Selected concept specification")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=86400,
        ui_inspector_params=["selected_id", "reason"],
    ),

    # ------------------ PRODUCTION ------------------
    "Prompt Builder": NodeDefinition(
        node_type="Prompt Builder",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.AGENT,
        description="Translates concept spec into structured multi-shot asset prompt plan",
        input_ports={"concept_spec": _port("concept_spec", PortType.CONCEPT_SPEC, "Selected concept spec")},
        output_ports={"asset_plan": _port("asset_plan", PortType.ASSET_PLAN, "Asset generation plan")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["prompt_version", "model_version"],
    ),
    "Image Generator": NodeDefinition(
        node_type="Image Generator",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.PROVIDER_WORKER,
        description="Generates still frames, backgrounds, and character assets via ComfyUI or model API",
        input_ports={"asset_plan": _port("asset_plan", PortType.ASSET_PLAN, "Asset generation plan")},
        output_ports={"images": _port("images", PortType.IMAGE_ASSET_LIST, "Generated image assets")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["model", "resolution", "seed"],
    ),
    "Storyboard Planner": NodeDefinition(
        node_type="Storyboard Planner",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.AGENT,
        description="Plans second-by-second narrative timeline, hook frames, and CTA placement",
        input_ports={"concept_spec": _port("concept_spec", PortType.CONCEPT_SPEC, "Concept specification")},
        output_ports={"storyboard": _port("storyboard", PortType.STORYBOARD, "Detailed video storyboard")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["duration", "shots"],
    ),
    "Video Generator": NodeDefinition(
        node_type="Video Generator",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.MEDIA_WORKER,
        description="Generates generative video motion clips from storyboard prompts",
        input_ports={
            "storyboard": _port("storyboard", PortType.STORYBOARD, "Video storyboard"),
            "assets": _port("assets", PortType.IMAGE_ASSET_LIST, "Reference still assets"),
        },
        output_ports={"video_asset": _port("video_asset", PortType.VIDEO_ASSET, "Generated video asset")},
        retry_policy=_default_retry(),
        timeout_seconds=600,
        ui_inspector_params=["provider", "seconds"],
    ),
    "Remotion Render": NodeDefinition(
        node_type="Remotion Render",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.WORKER,
        description="Renders programmatic 9:16 vertical video composition using Remotion engine",
        input_ports={
            "storyboard": _port("storyboard", PortType.STORYBOARD, "Composition timeline"),
            "assets": _port("assets", PortType.IMAGE_ASSET_LIST, "Image and audio assets"),
        },
        output_ports={"video_asset": _port("video_asset", PortType.VIDEO_ASSET, "Rendered MP4 video")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["resolution", "fps"],
    ),
    "Playable Spec": NodeDefinition(
        node_type="Playable Spec",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.AGENT,
        description="Generates interactive HTML5 mini-game logic, winning condition, and rules spec",
        input_ports={
            "concept": _port("concept", PortType.CONCEPT_SPEC, "Target concept"),
            "game_dna": _port("game_dna", PortType.GAME_PROFILE_VERSION, "Game DNA mechanics rules"),
        },
        output_ports={"playable_spec": _port("playable_spec", PortType.PLAYABLE_SPEC, "Playable game spec")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["preset", "mechanics"],
    ),
    "Phaser Codegen": NodeDefinition(
        node_type="Phaser Codegen",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.AGENT,
        description="Generates Phaser 3 TypeScript source code and assets bundle for mini-game",
        input_ports={
            "playable_spec": _port("playable_spec", PortType.PLAYABLE_SPEC, "Game mechanics spec"),
            "assets": _port("assets", PortType.GAME_ASSETS, "Sprite sheet and textures"),
        },
        output_ports={"source_bundle": _port("source_bundle", PortType.SOURCE_BUNDLE, "TypeScript source bundle")},
        retry_policy=_default_retry(),
        timeout_seconds=300,
        ui_inspector_params=["template_version"],
    ),
    "Sandbox Build": NodeDefinition(
        node_type="Sandbox Build",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.WORKER,
        description="Compiles and bundles Phaser source in an isolated disposable sandbox",
        input_ports={"source_bundle": _port("source_bundle", PortType.SOURCE_BUNDLE, "Source code bundle")},
        output_ports={"playable_bundle": _port("playable_bundle", PortType.PLAYABLE_BUNDLE, "Compiled HTML5 bundle")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["cpu_limit", "memory_limit", "timeout"],
    ),
    "Browser QA": NodeDefinition(
        node_type="Browser QA",
        category=NodeCategory.PRODUCTION,
        executor=ExecutorType.WORKER,
        description="Runs Playwright headless browser QA tests checking for zero JS runtime errors",
        input_ports={"playable_bundle": _port("playable_bundle", PortType.PLAYABLE_BUNDLE, "HTML5 playable bundle")},
        output_ports={"evaluation_report": _port("evaluation_report", PortType.EVALUATION_REPORT, "Technical QA report")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["browsers", "viewports"],
    ),

    # ------------------ QUALITY ------------------
    "Schema Validate": NodeDefinition(
        node_type="Schema Validate",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.WORKER,
        description="Gate 1: Verifies artifact schema integrity and mandatory field contracts",
        input_ports={"artifact": _port("artifact", PortType.ANY, "Any produced artifact")},
        output_ports={"evaluation_report": _port("evaluation_report", PortType.EVALUATION_REPORT, "Schema verification report")},
        retry_policy=_default_retry(),
        timeout_seconds=60,
        ui_inspector_params=["schema_version"],
    ),
    "Visual QA": NodeDefinition(
        node_type="Visual QA",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.AGENT,
        description="Gate 4: Analyzes resolution, contrast, aspect ratio and CTA legibility",
        input_ports={
            "asset": _port("asset", PortType.ANY, "Image or video asset"),
            "brief": _port("brief", PortType.CREATIVE_BRIEF, "Original creative brief"),
        },
        output_ports={"evaluation_report": _port("evaluation_report", PortType.EVALUATION_REPORT, "Visual QA report")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["rubric_version"],
    ),
    "Mechanics QA": NodeDefinition(
        node_type="Mechanics QA",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.HYBRID,
        description="Gate 3: Game Truth check ensuring playable mechanics match game DNA claims",
        input_ports={
            "playable": _port("playable", PortType.PLAYABLE_BUNDLE, "Playable game bundle"),
            "game_dna": _port("game_dna", PortType.GAME_PROFILE_VERSION, "Truth mechanics spec"),
        },
        output_ports={"evaluation_report": _port("evaluation_report", PortType.EVALUATION_REPORT, "Mechanics truth report")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["rule_set"],
    ),
    "Similarity Risk": NodeDefinition(
        node_type="Similarity Risk",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.WORKER,
        description="Gate 5: Computes pHash and cosine similarity against reference corpus for IP/brand safety",
        input_ports={
            "asset": _port("asset", PortType.ANY, "Asset to check"),
            "corpus": _port("corpus", PortType.REFERENCE_CORPUS, "Reference corpus"),
        },
        output_ports={"risk_report": _port("risk_report", PortType.RISK_REPORT, "Similarity risk report")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["threshold"],
    ),
    "Quality Gate": NodeDefinition(
        node_type="Quality Gate",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.WORKER,
        description="Evaluates aggregated gate reports against pass/fail criteria",
        input_ports={"eval_reports": _port("eval_reports", PortType.EVALUATION_REPORT_LIST, "All QA reports", allows_multiple=True)},
        output_ports={"pass_fail": _port("pass_fail", PortType.PASS_FAIL_RESULT, "Consolidated gate verdict")},
        retry_policy=_default_retry(),
        timeout_seconds=60,
        ui_inspector_params=["gate_policy"],
    ),
    "Human Approval": NodeDefinition(
        node_type="Human Approval",
        category=NodeCategory.QUALITY,
        executor=ExecutorType.HUMAN,
        description="Gate 7: Final human sign-off checkpoint for critical or borderline creatives",
        can_pause=True,
        input_ports={
            "artifact": _port("artifact", PortType.ANY, "Artifact under review"),
            "qa": _port("qa", PortType.EVALUATION_REPORT, "QA test summary"),
        },
        output_ports={"approval_decision": _port("approval_decision", PortType.APPROVAL_DECISION, "Human approval decision")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=86400,
        ui_inspector_params=["required_reviewers"],
    ),

    # ------------------ CONTROL ------------------
    "Branch": NodeDefinition(
        node_type="Branch",
        category=NodeCategory.CONTROL,
        executor=ExecutorType.WORKER,
        description="Conditional branching based on evaluation or approval outcome",
        input_ports={"decision": _port("decision", PortType.APPROVAL_DECISION, "Decision signal")},
        output_ports={"selected_edge": _port("selected_edge", PortType.CONTROL_SIGNAL, "Branch control output")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=30,
        ui_inspector_params=["expression"],
    ),
    "Merge": NodeDefinition(
        node_type="Merge",
        category=NodeCategory.CONTROL,
        executor=ExecutorType.WORKER,
        description="Merges multiple concurrent branches into a unified execution path",
        input_ports={"inputs": _port("inputs", PortType.ANY, "Parallel branch outputs", allows_multiple=True)},
        output_ports={"output": _port("output", PortType.ANY, "Merged output")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=30,
        ui_inspector_params=["merge_strategy"],
    ),
    "Retry Policy": NodeDefinition(
        node_type="Retry Policy",
        category=NodeCategory.CONTROL,
        executor=ExecutorType.WORKER,
        description="Manages retry lifecycle and fallback routing when a node execution fails",
        input_ports={"failure": _port("failure", PortType.CONTROL_SIGNAL, "Failure notification")},
        output_ports={"control_signal": _port("control_signal", PortType.CONTROL_SIGNAL, "Retry directive")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=30,
        ui_inspector_params=["retries", "backoff"],
    ),
    "Budget Gate": NodeDefinition(
        node_type="Budget Gate",
        category=NodeCategory.CONTROL,
        executor=ExecutorType.WORKER,
        description="Checks pre-execution cost estimation against project budget limits",
        input_ports={"estimate": _port("estimate", PortType.COST_ESTIMATE, "Estimated step cost")},
        output_ports={"decision": _port("decision", PortType.APPROVAL_DECISION, "Budget permit decision")},
        retry_policy=RetryPolicyConfig(max_attempts=1),
        timeout_seconds=30,
        ui_inspector_params=["limits"],
    ),
    "Artifact Save": NodeDefinition(
        node_type="Artifact Save",
        category=NodeCategory.CONTROL,
        executor=ExecutorType.WORKER,
        description="Persists verified artifact to storage and registers lineage record in DB",
        input_ports={"output": _port("output", PortType.ANY, "Completed artifact")},
        output_ports={"artifact_ref": _port("artifact_ref", PortType.ARTIFACT_REF, "Storage reference & SHA256")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["retention", "tags"],
    ),

    # ------------------ EXPORT ------------------
    "Export": NodeDefinition(
        node_type="Export",
        category=NodeCategory.EXPORT,
        executor=ExecutorType.WORKER,
        description="Builds distribution packages (PNG/MP4/HTML/ZIP) and manifest for campaign export",
        input_ports={"approved_assets": _port("approved_assets", PortType.ANY, "Approved creatives", allows_multiple=True)},
        output_ports={"export_manifest": _port("export_manifest", PortType.EXPORT_MANIFEST, "Campaign export manifest")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["output_type"],
    ),

    # ------------------ EXPERIMENTS ------------------
    "Variant Factory": NodeDefinition(
        node_type="Variant Factory",
        category=NodeCategory.EXPERIMENTS,
        executor=ExecutorType.HYBRID,
        description="Generates single-variable A/B test variations (hook, CTA, color palette)",
        input_ports={"hypothesis": _port("hypothesis", PortType.CREATIVE_HYPOTHESIS_LIST, "Target hypothesis")},
        output_ports={"variants": _port("variants", PortType.EXPERIMENT_PLAN, "Generated variant plan")},
        retry_policy=_default_retry(),
        timeout_seconds=180,
        ui_inspector_params=["single_variable"],
    ),
    "Outcome Import": NodeDefinition(
        node_type="Outcome Import",
        category=NodeCategory.EXPERIMENTS,
        executor=ExecutorType.WORKER,
        description="Imports and validates actual ad network campaign metrics (CSV / API)",
        input_ports={"source_data": _port("source_data", PortType.DATASET, "Raw metric spreadsheet")},
        output_ports={"dataset": _port("dataset", PortType.DATASET, "Cleaned outcome dataset")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["mapping", "attribution"],
    ),
    "Experiment Analysis": NodeDefinition(
        node_type="Experiment Analysis",
        category=NodeCategory.EXPERIMENTS,
        executor=ExecutorType.WORKER,
        description="Calculates CPI, CTR, IPM, and Bayesian / Frequentist statistical confidence",
        input_ports={"outcomes": _port("outcomes", PortType.DATASET, "Normalized outcome dataset")},
        output_ports={"experiment_result": _port("experiment_result", PortType.EXPERIMENT_RESULT, "Statistical evaluation")},
        retry_policy=_default_retry(),
        timeout_seconds=120,
        ui_inspector_params=["confidence_settings"],
    ),
}


class NodeRegistry:
    """Registry providing lookup and validation services for workflow nodes."""

    @classmethod
    def get_node(cls, node_type: str) -> Optional[NodeDefinition]:
        return NODE_DEFINITIONS.get(node_type)

    @classmethod
    def list_nodes(cls) -> List[NodeDefinition]:
        return list(NODE_DEFINITIONS.values())

    @classmethod
    def get_by_category(cls, category: NodeCategory) -> List[NodeDefinition]:
        return [node for node in NODE_DEFINITIONS.values() if node.category == category]

    @classmethod
    def contains(cls, node_type: str) -> bool:
        return node_type in NODE_DEFINITIONS
