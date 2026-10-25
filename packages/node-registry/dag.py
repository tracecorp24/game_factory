"""DAG topological ordering and parallel execution staging engine."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Dict, List, Set
from .types import WorkflowEdge, WorkflowGraph, WorkflowNode
from .validator import CycleDetectedError, detect_cycles


def get_upstream_nodes(node_id: str, edges: List[WorkflowEdge]) -> Set[str]:
    """Returns all direct upstream dependency node IDs for the given node."""
    return {edge.source for edge in edges if edge.target == node_id}


def get_downstream_nodes(node_id: str, edges: List[WorkflowEdge]) -> Set[str]:
    """Returns all direct downstream dependent node IDs for the given node."""
    return {edge.target for edge in edges if edge.source == node_id}


def topological_sort(graph: WorkflowGraph) -> List[str]:
    """
    Computes a linear topological sort of node IDs using Kahn's algorithm.
    Throws CycleDetectedError if a cycle is present.
    """
    detect_cycles([node.id for node in graph.nodes], graph.edges)

    in_degree: Dict[str, int] = {node.id: 0 for node in graph.nodes}
    adj: Dict[str, List[str]] = defaultdict(list)

    for edge in graph.edges:
        adj[edge.source].append(edge.target)
        in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

    queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
    ordered: List[str] = []

    while queue:
        curr = queue.popleft()
        ordered.append(curr)

        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(ordered) != len(graph.nodes):
        raise CycleDetectedError(["Graph contains unresolved cycles"])

    return ordered


def get_execution_stages(graph: WorkflowGraph) -> List[List[str]]:
    """
    Partitions the DAG into parallel execution stages (layers).
    All nodes in stage[k] can be executed concurrently in parallel because
    their dependencies only lie in stage[0] ... stage[k-1].
    """
    detect_cycles([node.id for node in graph.nodes], graph.edges)

    # In-degree count per node
    in_degree: Dict[str, int] = {node.id: 0 for node in graph.nodes}
    adj: Dict[str, List[str]] = defaultdict(list)

    for edge in graph.edges:
        adj[edge.source].append(edge.target)
        in_degree[edge.target] = in_degree.get(edge.target, 0) + 1

    # Current frontier: nodes with in_degree == 0
    current_stage = [nid for nid, deg in in_degree.items() if deg == 0]
    stages: List[List[str]] = []
    processed_count = 0

    while current_stage:
        stages.append(sorted(current_stage))
        processed_count += len(current_stage)

        next_stage: List[str] = []
        for nid in current_stage:
            for neighbor in adj[nid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    next_stage.append(neighbor)

        current_stage = next_stage

    if processed_count != len(graph.nodes):
        raise CycleDetectedError(["Graph contains unresolved cycles in stage partitioning"])

    return stages
