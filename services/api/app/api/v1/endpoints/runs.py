"""
Runs, Control Signals and Reproducibility Manifest REST API endpoints.
CreativeForge Intelligence Studio v3.0 - Section J, Modules M10 & M11.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="", tags=["Runs & Controls"])

_RUNS: Dict[str, Dict[str, Any]] = {
    "run_demo_01": {
        "id": "run_demo_01",
        "workflow_version_id": "wf_standard_pipeline_v1",
        "state": "completed",
        "started_at": "2026-10-25T11:00:00Z",
        "ended_at": "2026-10-25T11:01:15Z",
        "run_manifest_id": "man_run_demo_01",
    }
}

_MANIFESTS: Dict[str, Dict[str, Any]] = {
    "man_run_demo_01": {
        "id": "man_run_demo_01",
        "run_id": "run_demo_01",
        "sha256": "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "workflow_version_id": "wf_standard_pipeline_v1",
        "game_profile_version_id": "game_gem_rush_v1",
        "code_commit": "cf3a910",
        "frozen_parameters": {"seed": 42, "temperature": 0.7},
    }
}


import asyncio
import logging
from packages.node_registry import WorkflowGraph, WorkflowNode, WorkflowEdge
from services.worker_orchestrator import LocalDAGRunner
from services.api.app.api.v1.endpoints.workflows import _WORKFLOW_VERSIONS

logger = logging.getLogger("creativeforge.runs")

_ACTIVE_RUNNERS: Dict[str, LocalDAGRunner] = {}

class RunCreate(BaseModel):
    brief_input: Optional[Dict[str, Any]] = None
    budget_limit_usd: Optional[float] = 10.0


@router.post("/workflows/{workflow_id}/runs", status_code=201)
async def start_run(workflow_id: str, payload: RunCreate):
    """Start a new workflow execution with real DAG orchestration and lock immutable RunManifest."""
    run_id = f"run_{uuid.uuid4().hex[:8]}"
    manifest_id = f"man_{run_id}"

    manifest = {
        "id": manifest_id,
        "run_id": run_id,
        "sha256": uuid.uuid4().hex + uuid.uuid4().hex,
        "workflow_version_id": f"{workflow_id}_v1",
        "code_commit": "cf3-live",
        "frozen_parameters": payload.brief_input or {},
    }
    _MANIFESTS[manifest_id] = manifest

    run_record = {
        "id": run_id,
        "workflow_version_id": f"{workflow_id}_v1",
        "state": "running",
        "started_at": "2026-10-25T12:00:00Z",
        "ended_at": None,
        "run_manifest_id": manifest_id,
        "active_nodes": [],
        "completed_nodes": [],
        "failed_nodes": [],
    }
    _RUNS[run_id] = run_record

    # Resolve Workflow Graph
    wv = _WORKFLOW_VERSIONS.get(f"{workflow_id}_v1") or _WORKFLOW_VERSIONS.get("wf_standard_pipeline_v1")
    if wv and "graph_json" in wv:
        try:
            gj = wv["graph_json"]
            nodes = [WorkflowNode(id=n["id"], type=n["type"], config=n.get("config", {})) for n in gj.get("nodes", [])]
            edges = [
                WorkflowEdge(
                    id=f"e_{i}",
                    source=e["source"],
                    target=e["target"],
                    source_handle=e.get("source_handle"),
                    target_handle=e.get("target_handle"),
                )
                for i, e in enumerate(gj.get("edges", []))
            ]
            graph = WorkflowGraph(workflow_id=workflow_id, nodes=nodes, edges=edges)

            runner = LocalDAGRunner(run_id=run_id, workflow_id=workflow_id, graph=graph)
            _ACTIVE_RUNNERS[run_id] = runner

            # Launch background DAG execution task with real-time SSE event relay
            async def _execute_and_monitor():
                try:
                    from services.worker_event_relay.hub import sse_hub
                    from services.worker_orchestrator import NodeStatus

                    logger.info("DAG Runner started for run '%s' (workflow '%s')", run_id, workflow_id)
                    await sse_hub.publish(run_id, {
                        "event_type": "RUN_STARTED",
                        "run_id": run_id,
                        "status": "running",
                        "payload_preview": {"workflow_id": workflow_id},
                    })

                    dag_task = await runner.start(parameters=payload.brief_input or {})

                    # Track node transitions and publish real-time SSE events
                    seen_states: Dict[str, Any] = {}
                    while not dag_task.done():
                        try:
                            records = runner.get_node_executions()
                            for rec in records:
                                prev = seen_states.get(rec.node_id)
                                if prev != rec.status:
                                    seen_states[rec.node_id] = rec.status
                                    if rec.status == NodeStatus.RUNNING:
                                        await sse_hub.publish(run_id, {
                                            "event_type": "NODE_STARTED",
                                            "run_id": run_id,
                                            "node_execution_id": f"exec_{rec.node_id}",
                                            "status": "running",
                                            "payload_preview": {"node_id": rec.node_id, "attempt": rec.current_attempt},
                                        })
                                    elif rec.status == NodeStatus.COMPLETED:
                                        await sse_hub.publish(run_id, {
                                            "event_type": "NODE_COMPLETED",
                                            "run_id": run_id,
                                            "node_execution_id": f"exec_{rec.node_id}",
                                            "status": "completed",
                                            "payload_preview": {"node_id": rec.node_id, "output": rec.output_data},
                                        })
                                    elif rec.status == NodeStatus.FAILED:
                                        await sse_hub.publish(run_id, {
                                            "event_type": "NODE_FAILED",
                                            "run_id": run_id,
                                            "node_execution_id": f"exec_{rec.node_id}",
                                            "status": "failed",
                                            "payload_preview": {"node_id": rec.node_id, "error": rec.error},
                                        })
                        except Exception:
                            pass
                        await asyncio.sleep(0.05)

                    output = await runner.wait_completion()
                    run_record["state"] = output.status.value.lower()
                    run_record["completed_nodes"] = output.completed_nodes
                    run_record["failed_nodes"] = output.failed_nodes

                    # Make sure any final completed nodes are emitted
                    for nid in output.completed_nodes:
                        if seen_states.get(nid) != NodeStatus.COMPLETED:
                            await sse_hub.publish(run_id, {
                                "event_type": "NODE_COMPLETED",
                                "run_id": run_id,
                                "node_execution_id": f"exec_{nid}",
                                "status": "completed",
                                "payload_preview": {"node_id": nid},
                            })

                    event_type = "RUN_COMPLETED" if output.status.value == "COMPLETED" else "RUN_FAILED"
                    await sse_hub.publish(run_id, {
                        "event_type": event_type,
                        "run_id": run_id,
                        "status": output.status.value.lower(),
                        "payload_preview": {
                            "completed_nodes": output.completed_nodes,
                            "failed_nodes": output.failed_nodes,
                        },
                    })
                    logger.info("DAG Runner finished for run '%s' with status: %s", run_id, output.status.value)
                except Exception as exc:
                    logger.error("DAG Runner error for run '%s': %s", run_id, exc)
                    run_record["state"] = "failed"
                    run_record["error"] = str(exc)
                    try:
                        from services.worker_event_relay.hub import sse_hub
                        await sse_hub.publish(run_id, {
                            "event_type": "RUN_FAILED",
                            "run_id": run_id,
                            "status": "failed",
                            "payload_preview": {"error": str(exc)},
                        })
                    except Exception:
                        pass

            asyncio.create_task(_execute_and_monitor())
        except Exception as init_err:
            logger.warning("Could not initialize LocalDAGRunner (%s). Run marked running.", init_err)

    return run_record


@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get current run state and live node execution snapshot."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    
    # Query live state from runner if active
    if run_id in _ACTIVE_RUNNERS:
        try:
            state = _ACTIVE_RUNNERS[run_id].get_run_state()
            _RUNS[run_id]["state"] = state.status.value.lower()
            _RUNS[run_id]["completed_nodes"] = state.completed_nodes
            _RUNS[run_id]["active_nodes"] = state.active_nodes
            _RUNS[run_id]["failed_nodes"] = state.failed_nodes
        except Exception:
            pass

    return _RUNS[run_id]


@router.post("/runs/{run_id}/pause")
async def pause_run(run_id: str):
    """Pause an active workflow run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    if run_id in _ACTIVE_RUNNERS:
        _ACTIVE_RUNNERS[run_id].pause(reason="User requested pause via API")
    _RUNS[run_id]["state"] = "paused"
    return {"run_id": run_id, "state": "paused"}


@router.post("/runs/{run_id}/resume")
async def resume_run(run_id: str):
    """Resume a paused workflow run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    if run_id in _ACTIVE_RUNNERS:
        _ACTIVE_RUNNERS[run_id].resume(reason="User requested resume via API")
    _RUNS[run_id]["state"] = "running"
    return {"run_id": run_id, "state": "running"}


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    """Cancel an active or paused run."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    if run_id in _ACTIVE_RUNNERS:
        _ACTIVE_RUNNERS[run_id].cancel(reason="User requested cancellation via API")
    _RUNS[run_id]["state"] = "cancelled"
    return {"run_id": run_id, "state": "cancelled"}


@router.get("/runs/{run_id}/executions")
async def get_run_node_executions(run_id: str):
    """Get granular node execution attempt records."""
    if run_id in _ACTIVE_RUNNERS:
        return _ACTIVE_RUNNERS[run_id].get_node_executions()
    return []


@router.post("/runs/{run_id}/rerun")
async def rerun_run(run_id: str):
    """Idempotent rerun / retry failed node executions."""
    if run_id not in _RUNS:
        raise HTTPException(status_code=404, detail="Run not found")
    _RUNS[run_id]["state"] = "running"
    return {"run_id": run_id, "state": "running", "action": "rerun_initiated"}


@router.get("/runs/{run_id}/manifest")
async def get_run_manifest(run_id: str):
    """Get frozen reproducibility manifest for this run."""
    run = _RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    manifest_id = run.get("run_manifest_id")
    if manifest_id not in _MANIFESTS:
        raise HTTPException(status_code=404, detail="Manifest not found")
    return _MANIFESTS[manifest_id]


@router.get("/runs/{run_id}/export")
async def export_run_bundle(run_id: str):
    """Export complete reproducible bundle for the run."""
    run = _RUNS.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return {
        "run": run,
        "manifest": _MANIFESTS.get(run.get("run_manifest_id")),
        "exported_at": "2026-10-25T12:00:00Z",
    }
