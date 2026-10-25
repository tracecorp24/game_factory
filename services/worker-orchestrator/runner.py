"""Deterministic local runner for executing workflows and testing signals/queries."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

from packages.node_registry import WorkflowGraph
from .signals import (
    CancelSignalInput,
    HumanApprovalSignalInput,
    NodeExecutionRecord,
    PauseSignalInput,
    ResumeSignalInput,
    RunStateQueryResult,
    WorkflowStatus,
)
from .workflow import CreativePipelineWorkflow, WorkflowInput, WorkflowOutput


class LocalDAGRunner:
    """
    Local in-process executor that executes CreativePipelineWorkflow instances.
    Provides immediate signal delivery and query capabilities for automated tests
    and standalone executions.
    """

    def __init__(self, run_id: str, workflow_id: str, graph: WorkflowGraph) -> None:
        self.run_id = run_id
        self.workflow_id = workflow_id
        self.graph = graph
        self.workflow = CreativePipelineWorkflow()
        self._task: Optional[asyncio.Task] = None
        self._output: Optional[WorkflowOutput] = None

    async def start(
        self,
        simulate_failures: Optional[Dict[str, int]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> asyncio.Task:
        """Starts workflow execution in a background task."""
        input_data = WorkflowInput(
            run_id=self.run_id,
            workflow_id=self.workflow_id,
            graph=self.graph,
            simulate_failures=simulate_failures or {},
            parameters=parameters or {},
        )
        self._task = asyncio.create_task(self.workflow.run(input_data))
        return self._task

    async def wait_completion(self) -> WorkflowOutput:
        """Awaits completion of the workflow execution task."""
        if not self._task:
            raise RuntimeError("Workflow has not been started yet.")
        self._output = await self._task
        return self._output

    def pause(self, reason: str = "Local runner pause") -> None:
        """Sends PauseSignal to the active workflow."""
        self.workflow.pause_workflow(PauseSignalInput(reason=reason))

    def resume(self, reason: str = "Local runner resume") -> None:
        """Sends ResumeSignal to the paused workflow."""
        self.workflow.resume_workflow(ResumeSignalInput(reason=reason))

    def cancel(self, reason: str = "Local runner cancel") -> None:
        """Sends CancelSignal to terminate the workflow."""
        self.workflow.cancel_workflow(CancelSignalInput(reason=reason))

    def approve_human_node(
        self,
        node_id: str,
        approved: bool = True,
        reason: str = "Approved in test",
        selected_id: Optional[str] = None,
    ) -> None:
        """Sends HumanApprovalSignal to resolve a pending human checkpoint node."""
        self.workflow.human_approval(
            HumanApprovalSignalInput(
                node_id=node_id,
                approved=approved,
                reason=reason,
                selected_id=selected_id,
            )
        )

    def get_run_state(self) -> RunStateQueryResult:
        """Queries the workflow's real-time execution snapshot."""
        return self.workflow.get_run_state()

    def get_node_executions(self) -> List[NodeExecutionRecord]:
        """Queries the current status and attempt records of all nodes."""
        return self.workflow.get_current_node_executions()
