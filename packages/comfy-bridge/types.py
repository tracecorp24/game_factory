"""
ComfyUI and React Flow Type Definitions, Port Standards, and Color Palette.

Defines port types, color schemes, Pydantic v2 graph representations,
and error hierarchies for ComfyUI and React Flow bidirectional integration.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ComfyPortType(str, Enum):
    """Core ComfyUI data types used across node ports and widgets."""
    MODEL = "MODEL"
    CLIP = "CLIP"
    VAE = "VAE"
    CONDITIONING = "CONDITIONING"
    LATENT = "LATENT"
    IMAGE = "IMAGE"
    MASK = "MASK"
    CONTROL_NET = "CONTROL_NET"
    
    # Primitive parameter types
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    COMBO = "COMBO"
    
    # Generic / wildcard
    ANY = "*"


# Standardized color palette for port types in React Flow
PORT_COLORS: Dict[str, str] = {
    ComfyPortType.MODEL.value: "#b197fc",        # Açık Mor
    ComfyPortType.CLIP.value: "#ffd43b",         # Sarı
    ComfyPortType.VAE.value: "#ff6b6b",          # Kırmızı
    ComfyPortType.CONDITIONING.value: "#ffa94d", # Turuncu
    ComfyPortType.LATENT.value: "#da77f2",       # Mor
    ComfyPortType.IMAGE.value: "#4dabf7",        # Mavi
    ComfyPortType.MASK.value: "#ced4da",         # Gri
    ComfyPortType.CONTROL_NET.value: "#51cf66",  # Yeşil
    
    # Additional / scalar types
    ComfyPortType.INT.value: "#74c0fc",
    ComfyPortType.FLOAT.value: "#66d9e8",
    ComfyPortType.STRING.value: "#b197fc",
    ComfyPortType.BOOLEAN.value: "#69db7c",
    ComfyPortType.COMBO.value: "#fcc419",
    ComfyPortType.ANY.value: "#868e96",
}

DEFAULT_PORT_COLOR = "#868e96"


def get_port_color(port_type: str) -> str:
    """Returns the hex color code for a given ComfyUI port type."""
    normalized = port_type.strip().upper()
    return PORT_COLORS.get(normalized, DEFAULT_PORT_COLOR)


# -------------------------------------------------------------------------
# Exception Hierarchy
# -------------------------------------------------------------------------

class ComfyBridgeError(Exception):
    """Base exception for all ComfyUI bridge operations."""
    pass


class ComfyTypeMismatchError(ComfyBridgeError):
    """Raised when connecting incompatible port types."""
    def __init__(
        self,
        source_type: str,
        target_type: str,
        source_node: str,
        target_node: str,
        source_handle: str,
        target_handle: str,
        message: Optional[str] = None,
    ):
        self.source_type = source_type
        self.target_type = target_type
        self.source_node = source_node
        self.target_node = target_node
        self.source_handle = source_handle
        self.target_handle = target_handle
        default_msg = (
            f"Type mismatch: Cannot connect '{source_type}' from node '{source_node}' "
            f"({source_handle}) to '{target_type}' on node '{target_node}' ({target_handle})"
        )
        super().__init__(message or default_msg)


class ComfyCycleError(ComfyBridgeError):
    """Raised when a directed cycle is detected in the workflow graph."""
    def __init__(self, cycle_path: List[str]):
        self.cycle_path = cycle_path
        super().__init__(f"Cycle detected in ComfyUI graph: {' -> '.join(cycle_path)}")


class ComfyMissingPortError(ComfyBridgeError):
    """Raised when a required ComfyUI port or input is unconnected."""
    def __init__(self, node_id: str, class_type: str, input_name: str, expected_type: str):
        self.node_id = node_id
        self.class_type = class_type
        self.input_name = input_name
        self.expected_type = expected_type
        super().__init__(
            f"Missing required input '{input_name}' ({expected_type}) on node '{node_id}' ({class_type})"
        )


class ComfyValidationError(ComfyBridgeError):
    """Raised when a ComfyUI workflow fails structural validation."""
    pass


class ComfySchemaError(ComfyBridgeError):
    """Raised when ComfyUI object_info introspection schema is malformed or missing."""
    pass


# -------------------------------------------------------------------------
# Graph Data Contracts (Pydantic v2)
# -------------------------------------------------------------------------

class Position(BaseModel):
    """2D Position for React Flow canvas."""
    model_config = ConfigDict(extra="ignore")
    x: float
    y: float


class HandleDefinition(BaseModel):
    """Specification of an input or output port handle in React Flow."""
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    type: str
    color: Optional[str] = None
    is_connected: bool = False
    description: Optional[str] = None


class ReactFlowNodeData(BaseModel):
    """Payload data embedded in each React Flow node."""
    model_config = ConfigDict(extra="ignore")
    id: str
    label: str
    class_type: str
    category: Optional[str] = "ComfyUI"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    inputs: List[HandleDefinition] = Field(default_factory=list)
    outputs: List[HandleDefinition] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class ReactFlowNode(BaseModel):
    """Single node object compatible with @xyflow/react format."""
    model_config = ConfigDict(extra="ignore")
    id: str
    type: str = "comfyNode"
    position: Position
    data: ReactFlowNodeData
    width: Optional[float] = None
    height: Optional[float] = None


class ReactFlowEdge(BaseModel):
    """Single directed edge compatible with @xyflow/react format."""
    model_config = ConfigDict(extra="ignore")
    id: str
    source: str
    target: str
    sourceHandle: str
    targetHandle: str
    type: Optional[str] = "default"
    animated: Optional[bool] = False
    data: Dict[str, Any] = Field(default_factory=dict)


class ReactFlowGraph(BaseModel):
    """Complete React Flow canvas state."""
    model_config = ConfigDict(extra="ignore")
    nodes: List[ReactFlowNode] = Field(default_factory=list)
    edges: List[ReactFlowEdge] = Field(default_factory=list)
    viewport: Optional[Dict[str, float]] = None


class NodeSchema(BaseModel):
    """Introspected schema for a ComfyUI node class."""
    model_config = ConfigDict(extra="ignore")
    class_type: str
    category: str = "general"
    display_name: Optional[str] = None
    description: Optional[str] = None
    required_inputs: Dict[str, Any] = Field(default_factory=dict)
    optional_inputs: Dict[str, Any] = Field(default_factory=dict)
    output_types: List[str] = Field(default_factory=list)
    output_names: List[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result of workflow graph validation."""
    model_config = ConfigDict(extra="ignore")
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
