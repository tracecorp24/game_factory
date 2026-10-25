"""Temporal Durable Workflow for CreativeForge Creative Pipeline."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from packages.node_registry import (
    ExecutorType,
    NodeRegistry,
    WorkflowGraph,
    get_execution_stages,
    validate_graph,
)

from .signals import (
    CancelSignalInput,
    HumanApprovalSignalInput,
    NodeExecutionRecord,
    NodeStatus,
    PauseSignalInput,
    ResumeSignalInput,
    RunStateQueryResult,
    WorkflowStatus,
)

try:
    from temporalio import workflow
    from temporalio.common import RetryPolicy
except ImportError:
    class _WorkflowMock:
        @staticmethod
        def defn(fn=None, name=None):
            def decorator(f):
                return f
            return decorator(fn) if fn else decorator

        @staticmethod
        def run(fn):
            return fn

        @staticmethod
        def signal(fn=None, name=None):
            def decorator(f):
                return f
            return decorator(fn) if fn else decorator

        @staticmethod
        def query(fn=None, name=None):
            def decorator(f):
                return f
            return decorator(fn) if fn else decorator

    workflow = _WorkflowMock()
    RetryPolicy = dict

logger = logging.getLogger("worker_orchestrator.workflow")


def is_in_temporal_workflow() -> bool:
    """Checks whether execution is currently inside an active Temporal workflow event loop."""
    try:
        from temporalio import workflow as t_wf
        return hasattr(t_wf, "in_workflow") and t_wf.in_workflow()
    except Exception:
        return False


async def durable_wait_condition(predicate) -> None:
    """
    Waits until predicate() is True.
    Uses temporalio.workflow.wait_condition when running inside a Temporal workflow,
    or asyncio polling loop in standalone runner.
    """
    if is_in_temporal_workflow():
        from temporalio import workflow as t_wf
        await t_wf.wait_condition(predicate)
    else:
        while not predicate():
            await asyncio.sleep(0.02)


class WorkflowInput(BaseModel):
    """Input parameters to start a CreativePipelineWorkflow execution."""
    run_id: str
    workflow_id: str
    graph: WorkflowGraph
    simulate_failures: Dict[str, int] = Field(default_factory=dict, description="node_id -> failure count")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowOutput(BaseModel):
    """Final output result of a CreativePipelineWorkflow execution."""
    run_id: str
    workflow_id: str
    status: WorkflowStatus
    completed_nodes: List[str]
    failed_nodes: List[str]
    node_outputs: Dict[str, Any]
    error: Optional[str] = None
    started_at: str
    completed_at: str


@workflow.defn(name="CreativePipelineWorkflow")
class CreativePipelineWorkflow:
    """
    Temporal Durable Workflow that orchestrates CreativeForge DAG execution.
    Features:
    - Topological parallel stage execution
    - Pause / Resume durable signals
    - Cancellation signal
    - Human-in-the-loop approval pause & signal resolution
    - Dynamic query state inspection
    - Exponential backoff attempt lifecycle
    """

    def __init__(self) -> None:
        self._run_id: str = ""
        self._workflow_id: str = ""
        self._status: WorkflowStatus = WorkflowStatus.PENDING
        self._is_paused: bool = False
        self._is_cancelled: bool = False
        self._cancel_reason: Optional[str] = None
        self._error: Optional[str] = None

        self._current_stage_idx: int = 0
        self._total_stages: int = 0

        self._node_executions: Dict[str, NodeExecutionRecord] = {}
        self._node_outputs: Dict[str, Any] = {}
        self._human_approvals: Dict[str, HumanApprovalSignalInput] = {}

        self._started_at: str = ""
        self._completed_at: Optional[str] = None

    # ------------------ SIGNALS ------------------

    @workflow.signal(name="PauseSignal")
    def pause_workflow(self, input_data: PauseSignalInput) -> None:
        """Pauses workflow execution safely before the next stage or node."""
        if self._status in (WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED):
            return
        self._is_paused = True
        self._status = WorkflowStatus.PAUSED

    @workflow.signal(name="ResumeSignal")
    def resume_workflow(self, input_data: ResumeSignalInput) -> None:
        """Resumes a paused workflow."""
        if self._is_cancelled:
            return
        self._is_paused = False
        if self._status == WorkflowStatus.PAUSED:
            self._status = WorkflowStatus.RUNNING

    @workflow.signal(name="CancelSignal")
    def cancel_workflow(self, input_data: CancelSignalInput) -> None:
        """Cancels an active or paused workflow immediately."""
        self._is_cancelled = True
        self._cancel_reason = input_data.reason
        self._status = WorkflowStatus.CANCELLED

    @workflow.signal(name="HumanApprovalSignal")
    def human_approval(self, input_data: HumanApprovalSignalInput) -> None:
        """Delivers a human review decision to unblock a waiting approval node."""
        self._human_approvals[input_data.node_id] = input_data

    # ------------------ QUERIES ------------------

    @workflow.query(name="GetRunStateQuery")
    def get_run_state(self) -> RunStateQueryResult:
        """Returns the real-time execution snapshot of this workflow run."""
        completed = [nid for nid, r in self._node_executions.items() if r.status == NodeStatus.COMPLETED]
        failed = [nid for nid, r in self._node_executions.items() if r.status == NodeStatus.FAILED]
        active = [nid for nid, r in self._node_executions.items() if r.status in (NodeStatus.RUNNING, NodeStatus.WAITING_APPROVAL)]

        return RunStateQueryResult(
            run_id=self._run_id,
            workflow_id=self._workflow_id,
            status=self._status,
            current_stage=self._current_stage_idx,
            total_stages=self._total_stages,
            completed_nodes=completed,
            failed_nodes=failed,
            active_nodes=active,
            is_paused=self._is_paused,
            is_cancelled=self._is_cancelled,
            error=self._error or self._cancel_reason,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )

    @workflow.query(name="GetCurrentNodeExecutionsQuery")
    def get_current_node_executions(self) -> List[NodeExecutionRecord]:
        """Returns the detailed status and attempt records of all workflow nodes."""
        return list(self._node_executions.values())

    # ------------------ MAIN WORKFLOW RUN ------------------

    @workflow.run
    async def run(self, input_data: WorkflowInput) -> WorkflowOutput:
        """Main durable execution loop for the creative pipeline."""
        self._run_id = input_data.run_id
        self._workflow_id = input_data.workflow_id
        if self._is_paused:
            self._status = WorkflowStatus.PAUSED
        else:
            self._status = WorkflowStatus.RUNNING
        self._started_at = datetime.now(timezone.utc).isoformat()

        # Validate DAG
        try:
            validate_graph(input_data.graph, check_required_ports=False)
            stages = get_execution_stages(input_data.graph)
        except Exception as exc:
            self._status = WorkflowStatus.FAILED
            self._error = f"DAG validation error: {str(exc)}"
            return self._build_output()

        self._total_stages = len(stages)
        node_lookup = {node.id: node for node in input_data.graph.nodes}

        # Initialize node records
        for node in input_data.graph.nodes:
            node_def = NodeRegistry.get_node(node.type)
            max_att = node_def.retry_policy.max_attempts if node_def else 3
            self._node_executions[node.id] = NodeExecutionRecord(
                node_id=node.id,
                node_type=node.type,
                status=NodeStatus.PENDING,
                attempt_count=0,
                max_attempts=max_att,
            )

        # Execute topological stages sequentially; nodes within each stage run in parallel
        for stage_idx, stage_nodes in enumerate(stages):
            self._current_stage_idx = stage_idx + 1

            # Check pause state before starting stage
            if self._is_paused:
                await durable_wait_condition(lambda: not self._is_paused or self._is_cancelled)

            if self._is_cancelled:
                break

            # Execute all nodes in the current stage concurrently
            stage_coros = [
                self._execute_single_node(
                    node_id=nid,
                    node_instance=node_lookup[nid],
                    simulate_failures=input_data.simulate_failures.get(nid, 0),
                    run_id=input_data.run_id,
                )
                for nid in stage_nodes
            ]

            results = await asyncio.gather(*stage_coros, return_exceptions=True)

            # Check for stage failures
            stage_failed = False
            for nid, res in zip(stage_nodes, results):
                if isinstance(res, Exception):
                    stage_failed = True
                    self._error = f"Node '{nid}' failed: {str(res)}"
                    self._node_executions[nid].status = NodeStatus.FAILED
                    self._node_executions[nid].error = str(res)
                elif not res:
                    stage_failed = True

            if stage_failed or self._is_cancelled:
                break

        # Terminal status resolution
        if self._is_cancelled:
            self._status = WorkflowStatus.CANCELLED
            for nid, rec in self._node_executions.items():
                if rec.status in (NodeStatus.PENDING, NodeStatus.QUEUED, NodeStatus.WAITING_APPROVAL):
                    rec.status = NodeStatus.SKIPPED
        elif any(r.status == NodeStatus.FAILED for r in self._node_executions.values()):
            self._status = WorkflowStatus.FAILED
        else:
            self._status = WorkflowStatus.COMPLETED

        self._completed_at = datetime.now(timezone.utc).isoformat()
        return self._build_output()

    async def _execute_single_node(
        self,
        node_id: str,
        node_instance: Any,
        simulate_failures: int,
        run_id: str,
    ) -> bool:
        """Executes a single node, managing pauses, human approval, and retry attempts."""
        from .activities import NodeActivityInput, execute_node_activity

        rec = self._node_executions[node_id]
        node_def = NodeRegistry.get_node(node_instance.type)
        rec.status = NodeStatus.RUNNING
        rec.started_at = datetime.now(timezone.utc).isoformat()

        # Handle Human checkpoint node
        is_human = (node_def and node_def.executor == ExecutorType.HUMAN) or (node_def and node_def.can_pause)
        if is_human:
            rec.status = NodeStatus.WAITING_APPROVAL
            await durable_wait_condition(lambda: node_id in self._human_approvals or self._is_cancelled)

            if self._is_cancelled:
                rec.status = NodeStatus.SKIPPED
                return False

            approval = self._human_approvals[node_id]
            if not approval.approved:
                rec.status = NodeStatus.FAILED
                rec.error = f"Rejected by reviewer ({approval.reason})"
                return False

            rec.output_data = {"approval": approval.model_dump()}
            self._node_outputs[node_id] = rec.output_data
            rec.status = NodeStatus.COMPLETED
            rec.completed_at = datetime.now(timezone.utc).isoformat()
            return True

        # Activity execution with retry attempt loop
        max_attempts = rec.max_attempts
        backoff_sec = node_def.retry_policy.initial_interval_seconds if node_def else 0.05
        backoff_coeff = node_def.retry_policy.backoff_coefficient if node_def else 2.0
        max_backoff = node_def.retry_policy.maximum_interval_seconds if node_def else 1.0

        for attempt in range(1, max_attempts + 1):
            rec.attempt_count = attempt

            if self._is_cancelled:
                rec.status = NodeStatus.SKIPPED
                return False

            try:
                act_input = NodeActivityInput(
                    run_id=run_id,
                    node_id=node_id,
                    node_type=node_instance.type,
                    inputs=self._gather_node_inputs(node_id),
                    config=node_instance.data,
                    current_attempt=attempt,
                    simulate_failures=simulate_failures,
                )

                if is_in_temporal_workflow():
                    from temporalio import workflow as t_wf
                    act_output = await t_wf.execute_activity(
                        execute_node_activity,
                        act_input,
                        start_to_close_timeout=timedelta(seconds=node_def.timeout_seconds if node_def else 300),
                    )
                else:
                    act_output = await execute_node_activity(act_input)

                rec.status = NodeStatus.COMPLETED
                rec.completed_at = datetime.now(timezone.utc).isoformat()
                rec.output_data = act_output.outputs
                self._node_outputs[node_id] = act_output.outputs
                return True

            except Exception as err:
                rec.error = str(err)
                if attempt < max_attempts:
                    # Exponential backoff sleep before next attempt (short in tests)
                    sleep_time = min(backoff_sec, max_backoff)
                    await asyncio.sleep(min(sleep_time, 0.1))
                    backoff_sec *= backoff_coeff
                else:
                    rec.status = NodeStatus.FAILED
                    rec.completed_at = datetime.now(timezone.utc).isoformat()
                    return False

        return False

    def _gather_node_inputs(self, node_id: str) -> Dict[str, Any]:
        """Collects outputs produced by upstream completed nodes."""
        return {nid: out for nid, out in self._node_outputs.items()}

    def _build_output(self) -> WorkflowOutput:
        """Constructs the standard workflow output object."""
        completed = [nid for nid, r in self._node_executions.items() if r.status == NodeStatus.COMPLETED]
        failed = [nid for nid, r in self._node_executions.items() if r.status == NodeStatus.FAILED]

        return WorkflowOutput(
            run_id=self._run_id,
            workflow_id=self._workflow_id,
            status=self._status,
            completed_nodes=completed,
            failed_nodes=failed,
            node_outputs=self._node_outputs,
            error=self._error or self._cancel_reason,
            started_at=self._started_at,
            completed_at=self._completed_at or datetime.now(timezone.utc).isoformat(),
        )
