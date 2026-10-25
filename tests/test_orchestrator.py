"""Tests for Workflow Orchestrator, Temporal Lifecycle, Signals, Queries & Retries."""

import asyncio
import pytest
from packages.node_registry import WorkflowEdge, WorkflowGraph, WorkflowNode
from services.worker_orchestrator import (
    LocalDAGRunner,
    NodeStatus,
    WorkflowStatus,
)


@pytest.fixture
def sample_pipeline_graph() -> WorkflowGraph:
    """Fixture providing a standard 4-node pipeline graph."""
    return WorkflowGraph(
        workflow_id="test_wf_pipeline",
        nodes=[
            WorkflowNode(id="node_fetch", type="Source Fetch"),
            WorkflowNode(id="node_genre", type="Genre Classifier"),
            WorkflowNode(id="node_pattern", type="Ad Pattern Extract"),
            WorkflowNode(id="node_synthesis", type="Trend Synthesis"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="node_fetch", target="node_genre", source_handle="snapshot", target_handle="snapshot"),
            WorkflowEdge(id="e2", source="node_fetch", target="node_pattern", source_handle="snapshot", target_handle="creative_evidence"),
            WorkflowEdge(id="e3", source="node_genre", target="node_synthesis", source_handle="genre_report", target_handle="genre_report"),
            WorkflowEdge(id="e4", source="node_pattern", target="node_synthesis", source_handle="pattern_report", target_handle="pattern_report"),
        ],
    )


@pytest.mark.asyncio
async def test_workflow_end_to_end_execution(sample_pipeline_graph):
    """Verifies complete deterministic execution of multi-stage DAG."""
    runner = LocalDAGRunner(
        run_id="run_e2e_01",
        workflow_id="test_wf_pipeline",
        graph=sample_pipeline_graph,
    )

    await runner.start()
    output = await runner.wait_completion()

    assert output.status == WorkflowStatus.COMPLETED
    assert set(output.completed_nodes) == {"node_fetch", "node_genre", "node_pattern", "node_synthesis"}
    assert len(output.failed_nodes) == 0
    assert "node_synthesis" in output.node_outputs
    assert "trend_report" in output.node_outputs["node_synthesis"]


@pytest.mark.asyncio
async def test_workflow_pause_and_resume(sample_pipeline_graph):
    """Verifies that PauseSignal suspends workflow and ResumeSignal continues it."""
    runner = LocalDAGRunner(
        run_id="run_pause_01",
        workflow_id="test_wf_pipeline",
        graph=sample_pipeline_graph,
    )

    # Pause before starting
    runner.pause(reason="Testing initial pause")
    await runner.start()

    await asyncio.sleep(0.1)
    state = runner.get_run_state()
    assert state.is_paused is True
    assert state.status == WorkflowStatus.PAUSED

    # Resume
    runner.resume(reason="Testing resume")
    output = await runner.wait_completion()

    assert output.status == WorkflowStatus.COMPLETED
    assert set(output.completed_nodes) == {"node_fetch", "node_genre", "node_pattern", "node_synthesis"}


@pytest.mark.asyncio
async def test_workflow_cancel_signal(sample_pipeline_graph):
    """Verifies that CancelSignal immediately aborts active and pending nodes."""
    runner = LocalDAGRunner(
        run_id="run_cancel_01",
        workflow_id="test_wf_pipeline",
        graph=sample_pipeline_graph,
    )

    runner.pause()
    await runner.start()

    # Cancel while paused
    runner.cancel(reason="Aborted by user test")
    output = await runner.wait_completion()

    assert output.status == WorkflowStatus.CANCELLED
    state = runner.get_run_state()
    assert state.is_cancelled is True


@pytest.mark.asyncio
async def test_workflow_human_approval_checkpoint():
    """Verifies that human executor nodes wait for HumanApprovalSignal."""
    human_graph = WorkflowGraph(
        workflow_id="wf_human_test",
        nodes=[
            WorkflowNode(id="n_brief", type="Creative Brief"),
            WorkflowNode(id="n_approval", type="Human Approval"),
        ],
        edges=[
            WorkflowEdge(id="e1", source="n_brief", target="n_approval", source_handle="creative_brief", target_handle="artifact"),
        ],
    )

    runner = LocalDAGRunner(
        run_id="run_human_01",
        workflow_id="wf_human_test",
        graph=human_graph,
    )

    await runner.start()
    await asyncio.sleep(0.1)

    # Check that human approval node is waiting
    node_records = {r.node_id: r for r in runner.get_node_executions()}
    assert node_records["n_approval"].status == NodeStatus.WAITING_APPROVAL

    # Deliver human approval
    runner.approve_human_node(
        node_id="n_approval",
        approved=True,
        reason="Visuals look amazing, approved for production",
    )

    output = await runner.wait_completion()
    assert output.status == WorkflowStatus.COMPLETED
    assert "n_approval" in output.completed_nodes


@pytest.mark.asyncio
async def test_workflow_retry_lifecycle_and_backoff(sample_pipeline_graph):
    """
    Verifies that transient activity failures increment attempt count and succeed
    if attempts <= max_attempts.
    """
    runner = LocalDAGRunner(
        run_id="run_retry_success",
        workflow_id="test_wf_pipeline",
        graph=sample_pipeline_graph,
    )

    # Inject 2 transient failures for node_fetch (max_attempts = 3)
    await runner.start(simulate_failures={"node_fetch": 2})
    output = await runner.wait_completion()

    assert output.status == WorkflowStatus.COMPLETED
    node_records = {r.node_id: r for r in runner.get_node_executions()}
    assert node_records["node_fetch"].attempt_count == 3
    assert node_records["node_fetch"].status == NodeStatus.COMPLETED


@pytest.mark.asyncio
async def test_workflow_retry_exhausted_failure(sample_pipeline_graph):
    """
    Verifies that when failures exceed max_attempts, the node and workflow fail gracefully.
    """
    runner = LocalDAGRunner(
        run_id="run_retry_exhausted",
        workflow_id="test_wf_pipeline",
        graph=sample_pipeline_graph,
    )

    # Inject 5 failures for node_fetch (max_attempts = 3)
    await runner.start(simulate_failures={"node_fetch": 5})
    output = await runner.wait_completion()

    assert output.status == WorkflowStatus.FAILED
    assert "node_fetch" in output.failed_nodes
    node_records = {r.node_id: r for r in runner.get_node_executions()}
    assert node_records["node_fetch"].status == NodeStatus.FAILED
    assert node_records["node_fetch"].attempt_count == 3
