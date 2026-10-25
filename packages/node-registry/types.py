"""Typed definitions and contracts for CreativeForge Node Registry."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class NodeCategory(str, Enum):
    MARKET = "Market"
    PROFILE = "Profile"
    CONCEPT = "Concept"
    PRODUCTION = "Production"
    QUALITY = "Quality"
    CONTROL = "Control"
    EXPORT = "Export"
    EXPERIMENTS = "Experiments"


class ExecutorType(str, Enum):
    WORKER = "worker"
    AGENT = "agent"
    HUMAN = "human"
    HYBRID = "hybrid"
    FORM = "form"
    PROVIDER_WORKER = "provider_worker"
    MEDIA_WORKER = "media_worker"


class PortType(str, Enum):
    SOURCE_QUERY = "SourceQuery"
    TREND_SNAPSHOT = "TrendSnapshot"
    TREND_SNAPSHOT_LIST = "TrendSnapshot[]"
    TREND_REPORT = "TrendReport"
    GENRE_REPORT = "GenreReport"
    PATTERN_REPORT = "PatternReport"
    CREATIVE_EVIDENCE_LIST = "CreativeEvidence[]"
    GAME_ASSETS = "GameAssets"
    GAME_PROFILE_DRAFT = "GameProfileDraft"
    GAME_PROFILE_VERSION = "GameProfileVersion"
    USER_BRIEF = "UserBrief"
    CREATIVE_BRIEF = "CreativeBrief"
    CREATIVE_HYPOTHESIS_LIST = "CreativeHypothesis[]"
    RANKED_CONCEPTS = "RankedConcepts"
    CONCEPT_SPEC = "ConceptSpec"
    CONCEPT_BOARD_LIST = "ConceptBoard[]"
    APPROVAL_DECISION = "ApprovalDecision"
    ASSET_PLAN = "AssetPlan"
    IMAGE_ASSET_LIST = "ImageAsset[]"
    STORYBOARD = "Storyboard"
    VIDEO_ASSET = "VideoAsset"
    PLAYABLE_SPEC = "PlayableSpec"
    SOURCE_BUNDLE = "SourceBundle"
    PLAYABLE_BUNDLE = "PlayableBundle"
    EVALUATION_REPORT = "EvaluationReport"
    EVALUATION_REPORT_LIST = "EvaluationReport[]"
    EXPERIMENT_PLAN = "ExperimentPlan"
    EXPERIMENT_RESULT = "ExperimentResult"
    EXPORT_MANIFEST = "ExportManifest"
    RISK_REPORT = "RiskReport"
    PASS_FAIL_RESULT = "PassFailResult"
    CONTROL_SIGNAL = "ControlSignal"
    COST_ESTIMATE = "CostEstimate"
    ARTIFACT_REF = "ArtifactRef"
    REFERENCE_CORPUS = "ReferenceCorpus"
    DATASET = "Dataset"
    ANY = "Any"


class PortDefinition(BaseModel):
    """Specification of a single input or output port of a node."""
    model_config = ConfigDict(frozen=True)

    name: str = Field(..., description="Unique port name on this node")
    port_type: PortType = Field(..., description="Expected data contract type")
    description: str = Field(default="", description="Port documentation")
    required: bool = Field(default=True, description="Whether this port must be connected")
    allows_multiple: bool = Field(default=False, description="Whether port accepts incoming array or fan-in")


class RetryPolicyConfig(BaseModel):
    """Execution retry policy for durable workflow activities."""
    model_config = ConfigDict(frozen=True)

    max_attempts: int = Field(default=3, ge=1, description="Max execution attempts before failing")
    initial_interval_seconds: float = Field(default=1.0, ge=0.1, description="Initial retry delay in seconds")
    backoff_coefficient: float = Field(default=2.0, ge=1.0, description="Multiplier for backoff")
    maximum_interval_seconds: float = Field(default=60.0, ge=1.0, description="Max delay between retries")


class NodeDefinition(BaseModel):
    """Complete specification of an executable node in the registry."""
    model_config = ConfigDict(frozen=True)

    node_type: str = Field(..., description="Canonical node name")
    category: NodeCategory = Field(..., description="Observatory / Studio category")
    version: str = Field(default="1.0.0", description="Node definition semantic version")
    executor: ExecutorType = Field(..., description="Entity executing this node")
    input_ports: Dict[str, PortDefinition] = Field(default_factory=dict)
    output_ports: Dict[str, PortDefinition] = Field(default_factory=dict)
    retry_policy: RetryPolicyConfig = Field(default_factory=RetryPolicyConfig)
    timeout_seconds: int = Field(default=300, ge=1, description="Execution timeout in seconds")
    can_pause: bool = Field(default=False, description="Whether node pauses workflow (e.g. human approval)")
    description: str = Field(default="", description="Node purpose summary")
    ui_inspector_params: List[str] = Field(default_factory=list, description="Config keys exposed in UI inspector")


class WorkflowEdge(BaseModel):
    """Connection between two nodes in a workflow DAG."""
    id: str = Field(..., description="Edge identifier")
    source: str = Field(..., description="Source node id")
    target: str = Field(..., description="Target node id")
    source_handle: Optional[str] = Field(default=None, description="Output port name on source node")
    target_handle: Optional[str] = Field(default=None, description="Input port name on target node")


class WorkflowNode(BaseModel):
    """A node instance placed in a React Flow graph canvas."""
    id: str = Field(..., description="Node instance identifier in graph")
    type: str = Field(..., description="Registry node_type name")
    data: Dict[str, Any] = Field(default_factory=dict, description="Instance configuration parameters")
    position: Dict[str, float] = Field(default_factory=lambda: {"x": 0.0, "y": 0.0})


class WorkflowGraph(BaseModel):
    """Complete workflow graph definition."""
    workflow_id: str
    version: str = "1.0.0"
    nodes: List[WorkflowNode] = Field(default_factory=list)
    edges: List[WorkflowEdge] = Field(default_factory=list)
