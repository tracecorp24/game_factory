"""
CreativeForge Intelligence Studio v3.0 Core Contracts Package.
"""
from packages.contracts.common import (
    BaseContractModel,
    generate_uuid,
    utc_now,
    compute_sha256,
)
from packages.contracts.events import (
    EventType,
    EventEnvelope,
    RedactionLevel,
    ActorType,
)
from packages.contracts.records import (
    TokenUsageRecord,
    CostEntryRecord,
    ArtifactRecord,
    RunManifestRecord,
    UsageSource,
    CostKind,
    CostStatus,
    ArtifactType,
)
from packages.contracts.artifacts import (
    ConfidenceLevel,
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
from packages.contracts.comfy_contracts import (
    ComfyVariableSpec,
    ComfyModelCatalogItem,
    ComfyExecutionProgressEvent,
    ComfyPresetRecord,
    ComfyPresetCreate,
    ComfyPresetUpdate,
    ComfyTestRunRequest,
    ComfyTestRunResponse,
    validate_comfy_workflow_json,
)

__all__ = [
    # Common
    "BaseContractModel",
    "generate_uuid",
    "utc_now",
    "compute_sha256",
    # Events
    "EventType",
    "EventEnvelope",
    "RedactionLevel",
    "ActorType",
    # Records
    "TokenUsageRecord",
    "CostEntryRecord",
    "ArtifactRecord",
    "RunManifestRecord",
    "UsageSource",
    "CostKind",
    "CostStatus",
    "ArtifactType",
    # Artifacts
    "ConfidenceLevel",
    "TrendSnapshot",
    "TrendReport",
    "GameProfileVersion",
    "CreativeHypothesis",
    "ConceptSpec",
    "ConceptBoard",
    "ContextBundle",
    "AssetPlan",
    "ImageAsset",
    "VideoAsset",
    "PlayableSpec",
    "PlayableBundle",
    "EvaluationReport",
    "ExperimentResult",
    # ComfyUI Deep Hybrid Contracts (Agent H3)
    "ComfyVariableSpec",
    "ComfyModelCatalogItem",
    "ComfyExecutionProgressEvent",
    "ComfyPresetRecord",
    "ComfyPresetCreate",
    "ComfyPresetUpdate",
    "ComfyTestRunRequest",
    "ComfyTestRunResponse",
    "validate_comfy_workflow_json",
]
