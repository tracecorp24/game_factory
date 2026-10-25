"""Signals, queries, and execution state contracts for worker-orchestrator."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class NodeStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class PauseSignalInput(BaseModel):
    """Input payload for pausing an active workflow."""
    reason: str = Field(default="User paused workflow", description="Reason for pause")
    requested_by: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ResumeSignalInput(BaseModel):
    """Input payload for resuming a paused workflow."""
    reason: str = Field(default="User resumed workflow", description="Reason for resume")
    requested_by: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CancelSignalInput(BaseModel):
    """Input payload for cancelling an active workflow."""
    reason: str = Field(default="User cancelled workflow", description="Reason for cancellation")
    requested_by: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class HumanApprovalSignalInput(BaseModel):
    """Input payload when a human approves or rejects a checkpoint node."""
    node_id: str = Field(..., description="ID of the human approval node")
    approved: bool = Field(..., description="True if approved, False if rejected")
    reason: str = Field(default="", description="Reviewer feedback or rationale")
    selected_id: Optional[str] = Field(default=None, description="Selected concept or variant ID if applicable")
    reviewer: Optional[str] = Field(default="human_operator")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class NodeExecutionRecord(BaseModel):
    """Execution state and attempt history for a specific node in the workflow."""
    node_id: str
    node_type: str
    status: NodeStatus = NodeStatus.PENDING
    attempt_count: int = 0
    max_attempts: int = 3
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
    output_data: Dict[str, Any] = Field(default_factory=dict)


class RunStateQueryResult(BaseModel):
    """Snapshot response returned by GetRunStateQuery."""
    run_id: str
    workflow_id: str
    status: WorkflowStatus
    current_stage: int = 0
    total_stages: int = 0
    completed_nodes: List[str] = Field(default_factory=list)
    failed_nodes: List[str] = Field(default_factory=list)
    active_nodes: List[str] = Field(default_factory=list)
    is_paused: bool = False
    is_cancelled: bool = False
    error: Optional[str] = None
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
