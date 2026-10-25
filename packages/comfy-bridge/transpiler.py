"""
Bidirectional Transpiler between ComfyUI API JSON and React Flow Graph Structures.

Translates ComfyUI workflow JSON into React Flow (@xyflow/react) visual nodes & edges
with Sugiyama/DAG hierarchical layout, and transpiles React Flow graphs back into
strictly valid ComfyUI /prompt API specifications.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from .introspection import ComfySchemaExtractor
from .types import (
    ComfyBridgeError,
    ComfyMissingPortError,
    HandleDefinition,
    Position,
    ReactFlowEdge,
    ReactFlowGraph,
    ReactFlowNode,
    ReactFlowNodeData,
    get_port_color,
)


def comfy_to_react_flow(
    comfy_json: Union[Dict[str, Any], str, Path],
    schema_extractor: Optional[ComfySchemaExtractor] = None,
    horizontal_spacing: float = 380.0,
    vertical_spacing: float = 260.0,
) -> ReactFlowGraph:
    """
    Converts a ComfyUI API prompt JSON dictionary into a React Flow visual graph.

    - Resolves links (`["node_id", output_idx]`) into React Flow directed edges.
    - Isolates scalar parameters (steps, cfg, seed, text, etc.) into `data.parameters`.
    - Generates colored input & output handles according to ComfyUI port standards.
    - Automatically calculates non-overlapping hierarchical coordinates (DAG rank).
    """
    if isinstance(comfy_json, (str, Path)):
        p = Path(comfy_json)
        if p.is_file():
            with open(p, "r", encoding="utf-8") as f:
                prompt_dict = json.load(f)
        else:
            prompt_dict = json.loads(str(comfy_json))
    elif isinstance(comfy_json, dict):
        # Support both wrapped {"prompt": {...}} and raw ComfyUI prompt dicts
        if "prompt" in comfy_json and isinstance(comfy_json["prompt"], dict):
            prompt_dict = comfy_json["prompt"]
        else:
            prompt_dict = comfy_json
    else:
        raise ComfyBridgeError("comfy_json must be a dict, json string, or Path")

    if schema_extractor is None:
        schema_extractor = ComfySchemaExtractor()

    # Step 1: Pre-scan edges and node references
    edges: List[ReactFlowEdge] = []
    # node_id -> list of incoming source node_ids
    in_dependencies: Dict[str, Set[str]] = {str(nid): set() for nid in prompt_dict.keys()}
    # node_id -> set of used output indices
    observed_outputs: Dict[str, Set[int]] = {str(nid): set() for nid in prompt_dict.keys()}

    for target_id, node_spec in prompt_dict.items():
        if not isinstance(node_spec, dict):
            continue
        target_id_str = str(target_id)
        inputs = node_spec.get("inputs", {})
        if not isinstance(inputs, dict):
            continue

        for input_name, input_val in inputs.items():
            if _is_comfy_link(input_val):
                source_id_str = str(input_val[0])
                output_idx = int(input_val[1])
                in_dependencies[target_id_str].add(source_id_str)
                observed_outputs.setdefault(source_id_str, set()).add(output_idx)

                edge_id = f"e_{source_id_str}_{output_idx}_{target_id_str}_{input_name}"
                edges.append(
                    ReactFlowEdge(
                        id=edge_id,
                        source=source_id_str,
                        target=target_id_str,
                        sourceHandle=f"output_{output_idx}",
                        targetHandle=f"input_{input_name}",
                        animated=False,
                        data={
                            "input_name": input_name,
                            "output_index": output_idx,
                        },
                    )
                )

    # Step 2: Compute hierarchical DAG positions (topological ranking)
    positions = _compute_hierarchical_layout(
        node_ids=list(prompt_dict.keys()),
        in_deps=in_dependencies,
        horizontal_spacing=horizontal_spacing,
        vertical_spacing=vertical_spacing,
    )

    # Step 3: Construct ReactFlowNode instances
    nodes: List[ReactFlowNode] = []
    for node_id, node_spec in prompt_dict.items():
        if not isinstance(node_spec, dict):
            continue
        node_id_str = str(node_id)
        class_type = node_spec.get("class_type", "UnknownNode")
        raw_inputs = node_spec.get("inputs", {})
        meta = node_spec.get("_meta", {})
        label = meta.get("title", class_type)

        schema = schema_extractor.get_node_schema(class_type)

        parameters: Dict[str, Any] = {}
        connected_input_names: Set[str] = set()

        for k, v in raw_inputs.items():
            if _is_comfy_link(v):
                connected_input_names.add(k)
            else:
                parameters[k] = v

        # Build Input Handles
        input_handles: List[HandleDefinition] = []
        if schema:
            # Add required inputs
            for req_name, req_spec in schema.required_inputs.items():
                inp_type = schema_extractor.get_input_type(class_type, req_name) or "ANY"
                is_connected = req_name in connected_input_names
                input_handles.append(
                    HandleDefinition(
                        id=f"input_{req_name}",
                        name=req_name,
                        type=inp_type,
                        color=get_port_color(inp_type),
                        is_connected=is_connected,
                        description="Required input",
                    )
                )
            # Add optional inputs
            for opt_name, opt_spec in schema.optional_inputs.items():
                inp_type = schema_extractor.get_input_type(class_type, opt_name) or "ANY"
                is_connected = opt_name in connected_input_names
                input_handles.append(
                    HandleDefinition(
                        id=f"input_{opt_name}",
                        name=opt_name,
                        type=inp_type,
                        color=get_port_color(inp_type),
                        is_connected=is_connected,
                        description="Optional input",
                    )
                )
        else:
            # Fallback if no schema is known: infer from raw inputs
            for inp_name in raw_inputs.keys():
                is_conn = inp_name in connected_input_names
                inp_type = "ANY"
                input_handles.append(
                    HandleDefinition(
                        id=f"input_{inp_name}",
                        name=inp_name,
                        type=inp_type,
                        color=get_port_color(inp_type),
                        is_connected=is_conn,
                    )
                )

        # Build Output Handles
        output_handles: List[HandleDefinition] = []
        if schema and schema.output_types:
            for idx, out_type in enumerate(schema.output_types):
                out_name = schema_extractor.get_output_name(class_type, idx) or out_type
                output_handles.append(
                    HandleDefinition(
                        id=f"output_{idx}",
                        name=out_name,
                        type=out_type,
                        color=get_port_color(out_type),
                        is_connected=idx in observed_outputs.get(node_id_str, set()),
                    )
                )
        else:
            # Fallback: based on observed outputs
            used_indices = sorted(list(observed_outputs.get(node_id_str, set())))
            if not used_indices:
                used_indices = [0]
            for idx in used_indices:
                output_handles.append(
                    HandleDefinition(
                        id=f"output_{idx}",
                        name=f"output_{idx}",
                        type="ANY",
                        color=get_port_color("ANY"),
                        is_connected=True,
                    )
                )

        node_data = ReactFlowNodeData(
            id=node_id_str,
            label=label,
            class_type=class_type,
            category=schema.category if schema else "ComfyUI",
            parameters=parameters,
            inputs=input_handles,
            outputs=output_handles,
            meta=meta,
        )

        pos = positions.get(node_id_str, Position(x=0.0, y=0.0))
        nodes.append(
            ReactFlowNode(
                id=node_id_str,
                type="comfyNode",
                position=pos,
                data=node_data,
            )
        )

    # Sort nodes by ID for deterministic order
    nodes.sort(key=lambda n: (int(n.id) if n.id.isdigit() else n.id))

    return ReactFlowGraph(
        nodes=nodes,
        edges=edges,
    )


def react_flow_to_comfy(
    react_flow_graph: Union[Dict[str, Any], ReactFlowGraph],
    schema_extractor: Optional[ComfySchemaExtractor] = None,
    validate_required: bool = True,
) -> Dict[str, Any]:
    """
    Converts a React Flow graph back into the standard ComfyUI API /prompt format.

    - Restores `inputs` dict by merging scalar parameters and incoming edge links.
    - Validates missing required connection inputs (raises `ComfyMissingPortError`).
    - Produces an exact JSON dictionary ready to POST to `/prompt`.
    """
    if isinstance(react_flow_graph, dict):
        graph = ReactFlowGraph.model_validate(react_flow_graph)
    elif isinstance(react_flow_graph, ReactFlowGraph):
        graph = react_flow_graph
    else:
        raise ComfyBridgeError("react_flow_graph must be a dict or ReactFlowGraph")

    if schema_extractor is None:
        schema_extractor = ComfySchemaExtractor()

    comfy_dict: Dict[str, Any] = {}

    # Initialize nodes with parameters
    for node in graph.nodes:
        node_id_str = str(node.id)
        class_type = node.data.class_type
        # Deepcopy/clone parameters to avoid mutating node.data
        inputs: Dict[str, Any] = dict(node.data.parameters)

        comfy_dict[node_id_str] = {
            "class_type": class_type,
            "inputs": inputs,
        }
        if node.data.meta:
            comfy_dict[node_id_str]["_meta"] = dict(node.data.meta)

    # Map edges to input links: [source_id, output_index]
    for edge in graph.edges:
        target_id_str = str(edge.target)
        source_id_str = str(edge.source)

        if target_id_str not in comfy_dict:
            continue

        input_name = _parse_input_name_from_handle(edge.targetHandle)
        output_idx = _parse_output_index_from_handle(edge.sourceHandle)

        comfy_dict[target_id_str]["inputs"][input_name] = [source_id_str, output_idx]

    # Validate required ports if requested
    if validate_required:
        for node_id_str, spec in comfy_dict.items():
            class_type = spec["class_type"]
            current_inputs = spec["inputs"]

            req_connections = schema_extractor.get_required_connection_inputs(class_type)
            for req_name, req_type in req_connections:
                if req_name not in current_inputs:
                    raise ComfyMissingPortError(
                        node_id=node_id_str,
                        class_type=class_type,
                        input_name=req_name,
                        expected_type=req_type,
                    )

    return comfy_dict


# -------------------------------------------------------------------------
# Layout and Helper Utilities
# -------------------------------------------------------------------------

def _is_comfy_link(val: Any) -> bool:
    """Checks if a value is a ComfyUI link: [source_node_id, output_index]."""
    if isinstance(val, (list, tuple)) and len(val) == 2:
        return isinstance(val[0], (str, int)) and isinstance(val[1], int)
    return False


def _parse_input_name_from_handle(handle: str) -> str:
    """Extracts input name from a handle ID like 'input_model' -> 'model'."""
    if handle.startswith("input_"):
        return handle[6:]
    return handle


def _parse_output_index_from_handle(handle: str) -> int:
    """Extracts output index from handle ID like 'output_0' -> 0."""
    if handle.startswith("output_"):
        try:
            return int(handle[7:])
        except ValueError:
            return 0
    try:
        return int(handle)
    except ValueError:
        return 0


def _compute_hierarchical_layout(
    node_ids: List[Any],
    in_deps: Dict[str, Set[str]],
    horizontal_spacing: float = 380.0,
    vertical_spacing: float = 260.0,
) -> Dict[str, Position]:
    """
    Computes a clean, column-based hierarchical layout (Sugiyama-style DAG ranking).
    Roots (0 in-degree) are at layer 0 (x=50.0). Subsequent dependent nodes are placed
    in successive layers. Nodes within the same layer are vertically separated.
    """
    str_node_ids = [str(nid) for nid in node_ids]

    # Compute topological layers using dynamic programming / memoization
    memo_layer: Dict[str, int] = {}
    visiting: Set[str] = set()

    def get_layer(nid: str) -> int:
        if nid in memo_layer:
            return memo_layer[nid]
        if nid in visiting:
            # Cycle detected during layout; break cycle gracefully
            return 0
        visiting.add(nid)
        parents = in_deps.get(nid, set())
        if not parents:
            res = 0
        else:
            res = max((get_layer(p) + 1 for p in parents if p in in_deps), default=0)
        visiting.remove(nid)
        memo_layer[nid] = res
        return res

    layers: Dict[int, List[str]] = {}
    for nid in str_node_ids:
        layer_idx = get_layer(nid)
        layers.setdefault(layer_idx, []).append(nid)

    positions: Dict[str, Position] = {}
    base_x = 60.0
    base_y = 60.0

    for layer_idx in sorted(layers.keys()):
        layer_nodes = layers[layer_idx]
        # Sort layer nodes for visual stability
        layer_nodes.sort(key=lambda x: (int(x) if x.isdigit() else x))
        for row_idx, nid in enumerate(layer_nodes):
            x = base_x + (layer_idx * horizontal_spacing)
            y = base_y + (row_idx * vertical_spacing)
            positions[nid] = Position(x=round(x, 2), y=round(y, 2))

    return positions
