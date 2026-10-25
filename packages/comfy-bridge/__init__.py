"""
CreativeForge Intelligence Studio v3.0 — ComfyUI Bridge Package.

Provides loss-less bidirectional transpilation between standard ComfyUI API JSON
and React Flow (@xyflow/react) graph formats, strict type and acyclicity validation,
and node introspection.
"""

from .introspection import (
    BUILTIN_SCHEMAS,
    COMFY_CONNECTION_PORT_TYPES,
    ComfySchemaExtractor,
)
from .transpiler import (
    comfy_to_react_flow,
    react_flow_to_comfy,
)
from .types import (
    DEFAULT_PORT_COLOR,
    PORT_COLORS,
    ComfyBridgeError,
    ComfyCycleError,
    ComfyMissingPortError,
    ComfyPortType,
    ComfySchemaError,
    ComfyTypeMismatchError,
    ComfyValidationError,
    HandleDefinition,
    NodeSchema,
    Position,
    ReactFlowEdge,
    ReactFlowGraph,
    ReactFlowNode,
    ReactFlowNodeData,
    ValidationResult,
    get_port_color,
)
from .validator import (
    are_types_compatible,
    detect_cycles,
    validate_comfy_edge,
    validate_workflow_graph,
)

__all__ = [
    # Transpiler
    "comfy_to_react_flow",
    "react_flow_to_comfy",
    # Introspection
    "ComfySchemaExtractor",
    "BUILTIN_SCHEMAS",
    "COMFY_CONNECTION_PORT_TYPES",
    # Validator
    "validate_comfy_edge",
    "validate_workflow_graph",
    "detect_cycles",
    "are_types_compatible",
    # Types & Models
    "ComfyPortType",
    "PORT_COLORS",
    "DEFAULT_PORT_COLOR",
    "get_port_color",
    "HandleDefinition",
    "Position",
    "ReactFlowNodeData",
    "ReactFlowNode",
    "ReactFlowEdge",
    "ReactFlowGraph",
    "NodeSchema",
    "ValidationResult",
    # Errors
    "ComfyBridgeError",
    "ComfyTypeMismatchError",
    "ComfyCycleError",
    "ComfyMissingPortError",
    "ComfyValidationError",
    "ComfySchemaError",
]
