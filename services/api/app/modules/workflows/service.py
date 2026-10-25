"""Workflow Execution Service Layer for managing runs, signals, and queries."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

from packages.node_registry import (
    NodeRegistry,
    WorkflowGraph,
    validate_graph,
)
from services.worker_orchestrator import (
    LocalDAGRunner,
    NodeExecutionRecord,
    RunStateQueryResult,
    WorkflowStatus,
)
from .manifest import RunManifest, RunManifestBuilder


class WorkflowExecutionService:
    """
    Manages workflow version lifecycle, starts runs, dispatches signals,
    and returns durable run queries and frozen manifests.
    """

    def __init__(self) -> None:
        # In-memory storage for active local runners and manifests
        self._active_runners: Dict[str, LocalDAGRunner] = {}
        self._manifests: Dict[str, RunManifest] = {}
        self._graphs: Dict[str, WorkflowGraph] = {}

    def register_graph(self, graph: WorkflowGraph) -> None:
        """Validates and registers a workflow graph template."""
        validate_graph(graph, check_required_ports=False)
        self._graphs[graph.workflow_id] = graph

    def get_graph(self, workflow_id: str) -> Optional[WorkflowGraph]:
        return self._graphs.get(workflow_id)

    async def start_run(
        self,
        workflow_id: str,
        project_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        campaign_id: Optional[str] = None,
        simulate_failures: Optional[Dict[str, int]] = None,
    ) -> RunManifest:
        """
        Validates the graph, freezes an immutable RunManifest, and initiates execution.
        """
        graph = self._graphs.get(workflow_id)
        if not graph:
            raise ValueError(f"Workflow '{workflow_id}' not found. Register graph first.")

        # Validate DAG
        validate_graph(graph, check_required_ports=False)

        run_id = f"run_{uuid.uuid4().hex[:12]}"
        manifest_id = f"man_{uuid.uuid4().hex[:12]}"

        # Map node registry versions
        node_versions = {
            node.type: (NodeRegistry.get_node(node.type).version if NodeRegistry.get_node(node.type) else "1.0.0")
            for node in graph.nodes
        }

        # Build frozen manifest
        manifest = RunManifestBuilder.create_manifest(
            manifest_id=manifest_id,
            run_id=run_id,
            project_id=project_id,
            campaign_id=campaign_id,
            workflow_id=workflow_id,
            workflow_version=graph.version,
            graph_data=graph.model_dump(),
            node_registry_versions=node_versions,
            parameters=parameters or {},
        )

        self._manifests[run_id] = manifest

        # Initialize runner
        runner = LocalDAGRunner(run_id=run_id, workflow_id=workflow_id, graph=graph)
        self._active_runners[run_id] = runner

        # Launch execution
        await runner.start(simulate_failures=simulate_failures, parameters=parameters)

        return manifest

    def pause_run(self, run_id: str, reason: str = "Operator paused run") -> None:
        """Sends PauseSignal to active run."""
        runner = self._get_runner(run_id)
        runner.pause(reason=reason)

    def resume_run(self, run_id: str, reason: str = "Operator resumed run") -> None:
        """Sends ResumeSignal to paused run."""
        runner = self._get_runner(run_id)
        runner.resume(reason=reason)

    def cancel_run(self, run_id: str, reason: str = "Operator cancelled run") -> None:
        """Sends CancelSignal to terminate run."""
        runner = self._get_runner(run_id)
        runner.cancel(reason=reason)

    def submit_human_approval(
        self,
        run_id: str,
        node_id: str,
        approved: bool = True,
        reason: str = "Approved",
        selected_id: Optional[str] = None,
    ) -> None:
        """Delivers human decision to a waiting checkpoint node."""
        runner = self._get_runner(run_id)
        runner.approve_human_node(
            node_id=node_id,
            approved=approved,
            reason=reason,
            selected_id=selected_id,
        )

    def get_run_state(self, run_id: str) -> RunStateQueryResult:
        """Queries the real-time execution snapshot for a run."""
        runner = self._get_runner(run_id)
        return runner.get_run_state()

    def get_node_executions(self, run_id: str) -> List[NodeExecutionRecord]:
        """Queries node execution records and attempt histories."""
        runner = self._get_runner(run_id)
        return runner.get_node_executions()

    def get_manifest(self, run_id: str) -> Optional[RunManifest]:
        """Retrieves the frozen immutable RunManifest."""
        return self._manifests.get(run_id)

    def _get_runner(self, run_id: str) -> LocalDAGRunner:
        runner = self._active_runners.get(run_id)
        if not runner:
            raise KeyError(f"Active runner for run '{run_id}' not found.")
        return runner
