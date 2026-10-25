"""Graph and edge validation engine for CreativeForge Node Registry."""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple
from .catalog import NodeRegistry
from .types import (
    NodeDefinition,
    PortDefinition,
    PortType,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
)


class NodeRegistryError(Exception):
    """Base error for node registry operations."""
    pass


class NodeNotFoundError(NodeRegistryError):
    """Raised when a referenced node type is not registered in the catalog."""
    pass


class PortNotFoundError(NodeRegistryError):
    """Raised when an edge references a non-existent port handle."""
    pass


class TypeMismatchError(NodeRegistryError):
    """Raised when source and target ports have incompatible types."""
    pass


class CycleDetectedError(NodeRegistryError):
    """Raised when a graph contains one or more directed cycles."""
    def __init__(self, cycle_path: List[str]):
        self.cycle_path = cycle_path
        super().__init__(f"Cycle detected in workflow graph: {' -> '.join(cycle_path)}")


class MissingRequiredPortError(NodeRegistryError):
    """Raised when a required input port is left unconnected."""
    pass


def are_port_types_compatible(source_type: PortType, target_type: PortType) -> bool:
    """Evaluates type compatibility between an output and input port."""
    if source_type == PortType.ANY or target_type == PortType.ANY:
        return True

    if source_type == target_type:
        return True

    # Array / element compatibility rules
    if source_type == PortType.TREND_SNAPSHOT and target_type == PortType.TREND_SNAPSHOT_LIST:
        return True
    if source_type == PortType.TREND_SNAPSHOT_LIST and target_type == PortType.TREND_SNAPSHOT:
        return True
    if source_type in (PortType.TREND_SNAPSHOT, PortType.TREND_SNAPSHOT_LIST) and target_type == PortType.CREATIVE_EVIDENCE_LIST:
        return True
    if source_type == PortType.EVALUATION_REPORT and target_type == PortType.EVALUATION_REPORT_LIST:
        return True
    if source_type == PortType.CREATIVE_HYPOTHESIS_LIST and target_type == PortType.EXPERIMENT_PLAN:
        return True
    if source_type == PortType.APPROVAL_DECISION and target_type == PortType.CONTROL_SIGNAL:
        return True
    if source_type == PortType.PASS_FAIL_RESULT and target_type == PortType.CONTROL_SIGNAL:
        return True

    return False


def validate_edge(
    source_node_type: str,
    target_node_type: str,
    source_handle: Optional[str] = None,
    target_handle: Optional[str] = None,
) -> Tuple[PortDefinition, PortDefinition]:
    """
    Validates the connection between two nodes by inspecting port contracts.
    
    Returns the resolved (source_port, target_port) definitions on success,
    or raises TypeMismatchError / PortNotFoundError / NodeNotFoundError.
    """
    source_def = NodeRegistry.get_node(source_node_type)
    if not source_def:
        raise NodeNotFoundError(f"Source node type '{source_node_type}' not found in registry.")

    target_def = NodeRegistry.get_node(target_node_type)
    if not target_def:
        raise NodeNotFoundError(f"Target node type '{target_node_type}' not found in registry.")

    # Resolve source output port
    if source_handle:
        if source_handle not in source_def.output_ports:
            raise PortNotFoundError(
                f"Source node '{source_node_type}' has no output port named '{source_handle}'. "
                f"Available: {list(source_def.output_ports.keys())}"
            )
        src_port = source_def.output_ports[source_handle]
    else:
        # Default to single output port if only one exists
        if len(source_def.output_ports) == 1:
            src_port = next(iter(source_def.output_ports.values()))
        else:
            raise PortNotFoundError(
                f"Source node '{source_node_type}' has multiple output ports: {list(source_def.output_ports.keys())}. "
                f"Explicit 'source_handle' must be provided."
            )

    # Resolve target input port
    if target_handle:
        if target_handle not in target_def.input_ports:
            raise PortNotFoundError(
                f"Target node '{target_node_type}' has no input port named '{target_handle}'. "
                f"Available: {list(target_def.input_ports.keys())}"
            )
        tgt_port = target_def.input_ports[target_handle]
    else:
        # Default to single input port if only one exists
        if len(target_def.input_ports) == 1:
            tgt_port = next(iter(target_def.input_ports.values()))
        else:
            raise PortNotFoundError(
                f"Target node '{target_node_type}' has multiple input ports: {list(target_def.input_ports.keys())}. "
                f"Explicit 'target_handle' must be provided."
            )

    # Verify type compatibility
    if not are_port_types_compatible(src_port.port_type, tgt_port.port_type):
        raise TypeMismatchError(
            f"Type mismatch: Output port '{src_port.name}' ({src_port.port_type.value}) of node '{source_node_type}' "
            f"cannot be connected to input port '{tgt_port.name}' ({tgt_port.port_type.value}) of node '{target_node_type}'."
        )

    return src_port, tgt_port


def detect_cycles(node_ids: List[str], edges: List[WorkflowEdge]) -> None:
    """
    Performs Depth-First Search cycle detection on the graph edges.
    Raises CycleDetectedError if any directed cycle is discovered.
    """
    adj: Dict[str, List[str]] = {nid: [] for nid in node_ids}
    for edge in edges:
        if edge.source in adj:
            adj[edge.source].append(edge.target)

    # State: 0 = unvisited, 1 = visiting (in recursion stack), 2 = visited
    state: Dict[str, int] = {nid: 0 for nid in node_ids}
    current_path: List[str] = []

    def dfs(node: str) -> None:
        state[node] = 1
        current_path.append(node)

        for neighbor in adj.get(node, []):
            if neighbor not in state:
                continue
            if state[neighbor] == 1:
                # Cycle found! Extract the cycle path
                cycle_start_idx = current_path.index(neighbor)
                cycle = current_path[cycle_start_idx:] + [neighbor]
                raise CycleDetectedError(cycle)
            elif state[neighbor] == 0:
                dfs(neighbor)

        current_path.pop()
        state[node] = 2

    for nid in node_ids:
        if state[nid] == 0:
            dfs(nid)


def validate_graph(graph: WorkflowGraph, check_required_ports: bool = True) -> None:
    """
    Validates an entire WorkflowGraph:
    1. All node types exist in NodeRegistry.
    2. The graph is acyclic (DAG) - verified before edge port checks.
    3. All edges connect existing nodes and have type-compatible ports.
    4. Optional: All required input ports are connected.
    """
    node_map: Dict[str, WorkflowNode] = {node.id: node for node in graph.nodes}

    # 1. Check all nodes exist in registry
    for node in graph.nodes:
        if not NodeRegistry.contains(node.type):
            raise NodeNotFoundError(f"Node '{node.id}' specifies unknown type '{node.type}'.")

    # 2. Cycle detection (must detect cyclic graphs regardless of edge port configuration)
    detect_cycles([node.id for node in graph.nodes], graph.edges)

    # 3. Check edges and port compatibility
    connected_inputs: Dict[str, Set[str]] = {node.id: set() for node in graph.nodes}

    for edge in graph.edges:
        if edge.source not in node_map:
            raise NodeNotFoundError(f"Edge '{edge.id}' references non-existent source node '{edge.source}'.")
        if edge.target not in node_map:
            raise NodeNotFoundError(f"Edge '{edge.id}' references non-existent target node '{edge.target}'.")

        src_node = node_map[edge.source]
        tgt_node = node_map[edge.target]

        src_port, tgt_port = validate_edge(
            source_node_type=src_node.type,
            target_node_type=tgt_node.type,
            source_handle=edge.source_handle,
            target_handle=edge.target_handle,
        )

        connected_inputs[edge.target].add(tgt_port.name)

    # 4. Required ports validation
    if check_required_ports:
        for node in graph.nodes:
            node_def = NodeRegistry.get_node(node.type)
            if not node_def:
                continue
            for port_name, port_def in node_def.input_ports.items():
                if port_def.required and port_name not in connected_inputs[node.id]:
                    raise MissingRequiredPortError(
                        f"Node '{node.id}' (type '{node.type}') is missing required connection on input port '{port_name}'."
                    )
