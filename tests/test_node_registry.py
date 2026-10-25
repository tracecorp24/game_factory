"""Tests for Node Registry, Port Contracts, Edge Validation, and DAG Engine."""

import pytest
from packages.node_registry import (
    CycleDetectedError,
    NodeNotFoundError,
    NodeRegistry,
    PortNotFoundError,
    PortType,
    TypeMismatchError,
    WorkflowEdge,
    WorkflowGraph,
    WorkflowNode,
    get_execution_stages,
    topological_sort,
    validate_edge,
    validate_graph,
)


def test_node_catalog_contains_all_nodes():
    """Verifies that all required nodes across all 8 categories exist in the registry."""
    nodes = NodeRegistry.list_nodes()
    assert len(nodes) >= 33, f"Expected at least 33 nodes, got {len(nodes)}"

    expected_nodes = [
        "Source Fetch",
        "Deduplicate",
        "Genre Classifier",
        "Ad Pattern Extract",
        "Trend Synthesis",
        "Game Asset Import",
        "Game DNA Extract",
        "Human Confirm Mechanics",
        "Creative Brief",
        "Hypothesis Generate",
        "Hypothesis Rank",
        "Concept Board Render",
        "User Select Board",
        "Prompt Builder",
        "Image Generator",
        "Storyboard Planner",
        "Video Generator",
        "Remotion Render",
        "Playable Spec",
        "Phaser Codegen",
        "Sandbox Build",
        "Browser QA",
        "Schema Validate",
        "Visual QA",
        "Mechanics QA",
        "Similarity Risk",
        "Quality Gate",
        "Human Approval",
        "Branch",
        "Merge",
        "Retry Policy",
        "Budget Gate",
        "Artifact Save",
        "Export",
        "Variant Factory",
        "Outcome Import",
        "Experiment Analysis",
    ]

    for node_name in expected_nodes:
        assert NodeRegistry.contains(node_name), f"Node '{node_name}' missing from catalog"
        node_def = NodeRegistry.get_node(node_name)
        assert node_def is not None
        assert node_def.node_type == node_name
        assert len(node_def.output_ports) > 0 or node_def.category.value == "Export"


def test_validate_edge_success():
    """Tests valid connections between compatible ports."""
    # 1. Concept Board Render -> User Select Board
    src_port, tgt_port = validate_edge(
        source_node_type="Concept Board Render",
        target_node_type="User Select Board",
        source_handle="concept_boards",
        target_handle="concept_boards",
    )
    assert src_port.port_type == PortType.CONCEPT_BOARD_LIST
    assert tgt_port.port_type == PortType.CONCEPT_BOARD_LIST

    # 2. User Select Board -> Prompt Builder
    src_port, tgt_port = validate_edge(
        source_node_type="User Select Board",
        target_node_type="Prompt Builder",
    )
    assert src_port.port_type == PortType.CONCEPT_SPEC
    assert tgt_port.port_type == PortType.CONCEPT_SPEC

    # 3. Prompt Builder -> Image Generator
    src_port, tgt_port = validate_edge(
        source_node_type="Prompt Builder",
        target_node_type="Image Generator",
    )
    assert src_port.port_type == PortType.ASSET_PLAN
    assert tgt_port.port_type == PortType.ASSET_PLAN


def test_validate_edge_type_mismatch_error():
    """Verifies that an edge with incompatible types raises a clear TypeMismatchError."""
    with pytest.raises(TypeMismatchError) as exc_info:
        validate_edge(
            source_node_type="Image Generator",
            target_node_type="Source Fetch",
            source_handle="images",
            target_handle="query",
        )
    err_msg = str(exc_info.value)
    assert "Type mismatch" in err_msg
    assert "ImageAsset[]" in err_msg
    assert "SourceQuery" in err_msg
    assert "Image Generator" in err_msg
    assert "Source Fetch" in err_msg


def test_validate_edge_non_existent_node():
    """Verifies error on unknown node."""
    with pytest.raises(NodeNotFoundError):
        validate_edge("NonExistentNode", "Source Fetch")


def test_validate_edge_non_existent_port():
    """Verifies error on unknown port handle."""
    with pytest.raises(PortNotFoundError):
        validate_edge(
            source_node_type="Source Fetch",
            target_node_type="Deduplicate",
            source_handle="invalid_port_name",
        )


def test_cycle_detection_in_graph():
    """Verifies that directed cycles in a workflow graph raise CycleDetectedError."""
    cyclic_graph = WorkflowGraph(
        workflow_id="wf_cycle",
        nodes=[
            WorkflowNode(id="n1", type="Source Fetch"),
            WorkflowNode(id="n2", type="Deduplicate"),
            WorkflowNode(id="n3", type="Genre Classifier"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="n1", target="n2", source_handle="snapshot", target_handle="snapshots"),
            WorkflowEdge(id="e2", source="n2", target="n3", source_handle="snapshot", target_handle="snapshot"),
            WorkflowEdge(id="e3", source="n3", target="n1"),  # Creates cycle: n1 -> n2 -> n3 -> n1
        ],
    )

    with pytest.raises(CycleDetectedError) as exc_info:
        validate_graph(cyclic_graph, check_required_ports=False)

    assert "Cycle detected" in str(exc_info.value)


def test_topological_sort_and_parallel_stages():
    r"""
    Tests DAG ordering and parallel execution staging on a diamond graph:
         n1 (Source Fetch)
        /  \
      n2    n3 (Two parallel branches)
        \  /
         n4 (Merge)
    """
    diamond_graph = WorkflowGraph(
        workflow_id="wf_diamond",
        nodes=[
            WorkflowNode(id="n1", type="Source Fetch"),
            WorkflowNode(id="n2", type="Genre Classifier"),
            WorkflowNode(id="n3", type="Ad Pattern Extract"),
            WorkflowNode(id="n4", type="Trend Synthesis"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="n1", target="n2", source_handle="snapshot", target_handle="snapshot"),
            WorkflowEdge(id="e2", source="n1", target="n3", source_handle="snapshot", target_handle="creative_evidence"),
            WorkflowEdge(id="e3", source="n2", target="n4", source_handle="genre_report", target_handle="genre_report"),
            WorkflowEdge(id="e4", source="n3", target="n4", source_handle="pattern_report", target_handle="pattern_report"),
        ],
    )

    # 1. Topological Sort
    sorted_nodes = topological_sort(diamond_graph)
    assert sorted_nodes[0] == "n1"
    assert sorted_nodes[-1] == "n4"
    assert set(sorted_nodes[1:3]) == {"n2", "n3"}

    # 2. Parallel Stages Partition
    stages = get_execution_stages(diamond_graph)
    assert len(stages) == 3
    assert stages[0] == ["n1"]              # Stage 1: Root
    assert sorted(stages[1]) == ["n2", "n3"]  # Stage 2: Parallel branch execution!
    assert stages[2] == ["n4"]              # Stage 3: Aggregation sink
