"""
ComfyUI Edge and Graph Connection Validator.

Ensures strict type compatibility between connected handles, enforces DAG acyclicity
(zero directed cycles), and verifies mandatory connection ports.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .introspection import ComfySchemaExtractor
from .types import (
    ComfyCycleError,
    ComfyMissingPortError,
    ComfyPortType,
    ComfyTypeMismatchError,
    ComfyValidationError,
    ReactFlowEdge,
    ReactFlowGraph,
    ReactFlowNode,
    ValidationResult,
)


def are_types_compatible(source_type: str, target_type: str) -> bool:
    """
    Checks if a source port type can be legally connected to a target port type.
    """
    src = source_type.strip().upper()
    tgt = target_type.strip().upper()

    # Wildcards / ANY
    if src in ("*", "ANY") or tgt in ("*", "ANY"):
        return True

    # Exact type match
    if src == tgt:
        return True

    # Image / Mask partial compatibility in certain nodes (opt-in)
    if (src == "IMAGE" and tgt == "MASK") or (src == "MASK" and tgt == "IMAGE"):
        return False  # ComfyUI requires explicit mask/image converter nodes

    return False


def validate_comfy_edge(
    source_node: Union[ReactFlowNode, Dict[str, Any], str],
    target_node: Union[ReactFlowNode, Dict[str, Any], str],
    source_handle: str,
    target_handle: str,
    schema_extractor: Optional[ComfySchemaExtractor] = None,
) -> bool:
    """
    Validates a single edge connection between two ComfyUI nodes.

    Raises:
        ComfyTypeMismatchError: If the source output type is incompatible with target input type.
    """
    if schema_extractor is None:
        schema_extractor = ComfySchemaExtractor()

    src_id, src_class, src_outputs = _extract_node_info(source_node)
    tgt_id, tgt_class, tgt_inputs = _extract_node_info(target_node)

    # Resolve source output type
    source_type = None
    output_idx = _parse_output_index(source_handle)
    if src_class:
        source_type = schema_extractor.get_output_type(src_class, output_idx)
    if not source_type and src_outputs:
        for out_def in src_outputs:
            if out_def.get("id") == source_handle:
                source_type = out_def.get("type")
                break
    if not source_type:
        source_type = ComfyPortType.ANY.value

    # Resolve target input type
    target_type = None
    input_name = _parse_input_name(target_handle)
    if tgt_class:
        target_type = schema_extractor.get_input_type(tgt_class, input_name)
    if not target_type and tgt_inputs:
        for in_def in tgt_inputs:
            if in_def.get("id") == target_handle or in_def.get("name") == input_name:
                target_type = in_def.get("type")
                break
    if not target_type:
        target_type = ComfyPortType.ANY.value

    if not are_types_compatible(source_type, target_type):
        raise ComfyTypeMismatchError(
            source_type=source_type,
            target_type=target_type,
            source_node=src_id,
            target_node=tgt_id,
            source_handle=source_handle,
            target_handle=target_handle,
        )

    return True


def detect_cycles(
    nodes: List[Union[ReactFlowNode, str]],
    edges: List[Union[ReactFlowEdge, Dict[str, Any]]],
) -> Optional[List[str]]:
    """
    Detects directed cycles using depth-first search with 3-state coloring.
    Returns the cycle path as a list of node IDs if found, or None if DAG is acyclic.
    """
    adj: Dict[str, List[str]] = {}
    for n in nodes:
        nid = n.id if isinstance(n, ReactFlowNode) else str(n)
        adj[nid] = []

    for e in edges:
        if isinstance(e, ReactFlowEdge):
            src, tgt = str(e.source), str(e.target)
        else:
            src, tgt = str(e.get("source")), str(e.get("target"))
        adj.setdefault(src, []).append(tgt)
        adj.setdefault(tgt, [])

    # 0 = unvisited, 1 = visiting (in stack), 2 = visited
    state: Dict[str, int] = {k: 0 for k in adj}
    parent: Dict[str, Optional[str]] = {k: None for k in adj}

    for start_node in adj:
        if state[start_node] != 0:
            continue

        stack = [(start_node, 0)]
        path: List[str] = []

        while stack:
            curr, neighbor_idx = stack[-1]

            if state[curr] == 0:
                state[curr] = 1
                path.append(curr)

            neighbors = adj.get(curr, [])
            if neighbor_idx < len(neighbors):
                neighbor = neighbors[neighbor_idx]
                stack[-1] = (curr, neighbor_idx + 1)

                if state[neighbor] == 1:
                    # Cycle detected!
                    cycle_start_idx = path.index(neighbor)
                    cycle = path[cycle_start_idx:] + [neighbor]
                    return cycle
                elif state[neighbor] == 0:
                    parent[neighbor] = curr
                    stack.append((neighbor, 0))
            else:
                state[curr] = 2
                path.pop()
                stack.pop()

    return None


def validate_workflow_graph(
    graph: Union[Dict[str, Any], ReactFlowGraph],
    schema_extractor: Optional[ComfySchemaExtractor] = None,
    check_required: bool = True,
) -> ValidationResult:
    """
    Validates a complete ComfyUI React Flow graph:
    1. Checks for cycles (raises ComfyCycleError if invalid).
    2. Checks every edge for type compatibility (raises ComfyTypeMismatchError).
    3. Verifies required connection inputs are satisfied.
    """
    if isinstance(graph, dict):
        rf_graph = ReactFlowGraph.model_validate(graph)
    elif isinstance(graph, ReactFlowGraph):
        rf_graph = graph
    else:
        raise ComfyValidationError("graph must be a dict or ReactFlowGraph")

    if schema_extractor is None:
        schema_extractor = ComfySchemaExtractor()

    errors: List[str] = []
    warnings: List[str] = []

    # 1. Cycle detection
    cycle = detect_cycles(rf_graph.nodes, rf_graph.edges)
    if cycle:
        raise ComfyCycleError(cycle)

    # 2. Build quick lookup for nodes
    node_map: Dict[str, ReactFlowNode] = {str(n.id): n for n in rf_graph.nodes}

    # 3. Edge type validations
    for edge in rf_graph.edges:
        src_node = node_map.get(str(edge.source))
        tgt_node = node_map.get(str(edge.target))
        if not src_node:
            errors.append(f"Edge '{edge.id}' references missing source node '{edge.source}'")
            continue
        if not tgt_node:
            errors.append(f"Edge '{edge.id}' references missing target node '{edge.target}'")
            continue

        validate_comfy_edge(
            source_node=src_node,
            target_node=tgt_node,
            source_handle=edge.sourceHandle,
            target_handle=edge.targetHandle,
            schema_extractor=schema_extractor,
        )

    # 4. Required port checks
    if check_required:
        # Build set of connected inputs per node: (target_node_id, input_name)
        connected_inputs: Set[Tuple[str, str]] = set()
        for edge in rf_graph.edges:
            input_name = _parse_input_name(edge.targetHandle)
            connected_inputs.add((str(edge.target), input_name))

        for node in rf_graph.nodes:
            class_type = node.data.class_type
            req_ports = schema_extractor.get_required_connection_inputs(class_type)
            for req_name, req_type in req_ports:
                if (str(node.id), req_name) not in connected_inputs:
                    raise ComfyMissingPortError(
                        node_id=str(node.id),
                        class_type=class_type,
                        input_name=req_name,
                        expected_type=req_type,
                    )

    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )


# -------------------------------------------------------------------------
# Internal Helpers
# -------------------------------------------------------------------------

def _parse_input_name(handle: str) -> str:
    if handle.startswith("input_"):
        return handle[6:]
    return handle


def _parse_output_index(handle: str) -> int:
    if handle.startswith("output_"):
        try:
            return int(handle[7:])
        except ValueError:
            return 0
    try:
        return int(handle)
    except ValueError:
        return 0


def _extract_node_info(
    node: Union[ReactFlowNode, Dict[str, Any], str]
) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
    if isinstance(node, ReactFlowNode):
        return (
            str(node.id),
            node.data.class_type,
            [h.model_dump() for h in (node.data.outputs if hasattr(node.data, "outputs") else [])],
        )
    if isinstance(node, dict):
        nid = str(node.get("id", ""))
        data = node.get("data", {})
        cls_type = data.get("class_type") or node.get("class_type")
        outputs = data.get("outputs", [])
        return (nid, cls_type, outputs)
    return (str(node), None, [])
