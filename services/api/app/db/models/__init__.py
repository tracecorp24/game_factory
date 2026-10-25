"""
CreativeForge Intelligence Studio v3.0 Database Models.
All 46 relational tables and metadata definitions.
"""
from services.api.app.db.base import Base
from services.api.app.db.models.organizations import (
    Organization,
    User,
    Membership,
    Workspace,
    Project,
    Campaign,
)
from services.api.app.db.models.intelligence import (
    SourceRegistry,
    SourceSyncJob,
    RawSnapshot,
    TrendObservation,
    TrendReport,
)
from services.api.app.db.models.game_dna import (
    GameProfile,
    GameProfileVersion,
    AssetRight,
)
from services.api.app.db.models.concepts import (
    CreativeHypothesis,
    ConceptBoard,
    ConceptDecision,
)
from services.api.app.db.models.workflows import (
    Workflow,
    WorkflowVersion,
    Request,
    Run,
    RunManifest,
)
from services.api.app.db.models.ledger import (
    RunEvent,
    OutboxEvent,
    AuditEvent,
)
from services.api.app.db.models.executions import (
    NodeExecution,
    Attempt,
    AgentSession,
    ModelInvocation,
    UsageRecord,
    PriceCatalogVersion,
    CostEntry,
    ToolCall,
)
from services.api.app.db.models.artifacts import (
    Artifact,
    ArtifactLineage,
    QualityGateResult,
    Evaluation,
    HumanReview,
)
from services.api.app.db.models.experiments import (
    Experiment,
    ExperimentVariant,
    ExperimentOutcome,
)
from services.api.app.db.models.prompts_and_policies import (
    PromptTemplate,
    PromptVersion,
    ModelPolicy,
    ContextBundle,
)
from services.api.app.db.models.analytics import (
    AnalyticsRollupHourly,
)
from services.api.app.db.models.comfy import (
    ComfyPreset,
    ComfyPresetVersion,
    ComfyModelCatalog,
)

__all__ = [
    "Base",
    # Organizations
    "Organization",
    "User",
    "Membership",
    "Workspace",
    "Project",
    "Campaign",
    # Intelligence
    "SourceRegistry",
    "SourceSyncJob",
    "RawSnapshot",
    "TrendObservation",
    "TrendReport",
    # Game DNA
    "GameProfile",
    "GameProfileVersion",
    "AssetRight",
    # Concepts
    "CreativeHypothesis",
    "ConceptBoard",
    "ConceptDecision",
    # Workflows
    "Workflow",
    "WorkflowVersion",
    "Request",
    "Run",
    "RunManifest",
    # Ledger
    "RunEvent",
    "OutboxEvent",
    "AuditEvent",
    # Executions
    "NodeExecution",
    "Attempt",
    "AgentSession",
    "ModelInvocation",
    "UsageRecord",
    "PriceCatalogVersion",
    "CostEntry",
    "ToolCall",
    # Artifacts
    "Artifact",
    "ArtifactLineage",
    "QualityGateResult",
    "Evaluation",
    "HumanReview",
    # Experiments
    "Experiment",
    "ExperimentVariant",
    "ExperimentOutcome",
    # Prompts & Policies
    "PromptTemplate",
    "PromptVersion",
    "ModelPolicy",
    "ContextBundle",
    # Analytics
    "AnalyticsRollupHourly",
    # ComfyUI Deep Hybrid (Agent H3)
    "ComfyPreset",
    "ComfyPresetVersion",
    "ComfyModelCatalog",
]
