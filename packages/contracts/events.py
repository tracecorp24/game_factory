"""
Event envelope and taxonomy definitions for CreativeForge Intelligence Studio v3.0.
"""
from datetime import datetime
from enum import Enum
import hashlib
import json
from typing import Any, Dict, Literal, Optional
from pydantic import Field, field_validator

from packages.contracts.common import BaseContractModel, generate_uuid, utc_now


class EventType(str, Enum):
    """Exhaustive Event Taxonomy from Master Plan Section M11 and Section 3.1."""
    # Request & Approvals
    REQUEST_RECEIVED = "REQUEST_RECEIVED"
    BRIEF_VERSION_CREATED = "BRIEF_VERSION_CREATED"
    USER_INPUT_CHANGED = "USER_INPUT_CHANGED"
    CONCEPT_SELECTED = "CONCEPT_SELECTED"
    CONCEPT_REJECTED = "CONCEPT_REJECTED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    APPROVAL_DENIED = "APPROVAL_DENIED"

    # Trend Intelligence
    SOURCE_SYNC_QUEUED = "SOURCE_SYNC_QUEUED"
    SOURCE_SYNC_STARTED = "SOURCE_SYNC_STARTED"
    SOURCE_FETCHED = "SOURCE_FETCHED"
    SOURCE_FETCH_FAILED = "SOURCE_FETCH_FAILED"
    TREND_SNAPSHOT_CREATED = "TREND_SNAPSHOT_CREATED"
    TREND_REPORT_CREATED = "TREND_REPORT_CREATED"

    # Workflow & Run Lifecycle
    WORKFLOW_VERSION_CREATED = "WORKFLOW_VERSION_CREATED"
    RUN_CREATED = "RUN_CREATED"
    RUN_QUEUED = "RUN_QUEUED"
    RUN_STARTED = "RUN_STARTED"
    RUN_PAUSED = "RUN_PAUSED"
    RUN_RESUMED = "RUN_RESUMED"
    RUN_CANCELLED = "RUN_CANCELLED"
    RUN_COMPLETED = "RUN_COMPLETED"
    RUN_FAILED = "RUN_FAILED"

    # Agent & Node Execution
    TASK_DISPATCHED = "TASK_DISPATCHED"
    AGENT_STARTED = "AGENT_STARTED"
    AGENT_FINISHED = "AGENT_FINISHED"
    NODE_STARTED = "NODE_STARTED"
    NODE_FINISHED = "NODE_FINISHED"
    NODE_FAILED = "NODE_FAILED"
    ATTEMPT_STARTED = "ATTEMPT_STARTED"
    ATTEMPT_FAILED = "ATTEMPT_FAILED"
    RETRY_SCHEDULED = "RETRY_SCHEDULED"
    RETRY_EXHAUSTED = "RETRY_EXHAUSTED"

    # Model Invocations & Gateway
    MODEL_ROUTE_SELECTED = "MODEL_ROUTE_SELECTED"
    MODEL_CALL_STARTED = "MODEL_CALL_STARTED"
    MODEL_CALL_FINISHED = "MODEL_CALL_FINISHED"
    MODEL_CALL_FAILED = "MODEL_CALL_FAILED"
    MODEL_USAGE_RECORDED = "MODEL_USAGE_RECORDED"
    MODEL_USAGE_CORRECTED = "MODEL_USAGE_CORRECTED"
    MODEL_FALLBACK_USED = "MODEL_FALLBACK_USED"

    # Tool Calls & Artifacts
    TOOL_CALL_STARTED = "TOOL_CALL_STARTED"
    TOOL_CALL_FINISHED = "TOOL_CALL_FINISHED"
    TOOL_CALL_FAILED = "TOOL_CALL_FAILED"
    ARTIFACT_CREATED = "ARTIFACT_CREATED"
    ARTIFACT_VALIDATED = "ARTIFACT_VALIDATED"
    ARTIFACT_REVISED = "ARTIFACT_REVISED"
    ARTIFACT_EXPORTED = "ARTIFACT_EXPORTED"
    ARTIFACT_DELETION_REQUESTED = "ARTIFACT_DELETION_REQUESTED"

    # QA, Cost & Governance
    EVALUATION_CREATED = "EVALUATION_CREATED"
    QUALITY_GATE_PASSED = "QUALITY_GATE_PASSED"
    QUALITY_GATE_FAILED = "QUALITY_GATE_FAILED"
    COST_ESTIMATED = "COST_ESTIMATED"
    COST_COMMITTED = "COST_COMMITTED"
    COST_RECONCILED = "COST_RECONCILED"
    BUDGET_ALERTED = "BUDGET_ALERTED"
    BUDGET_BLOCKED = "BUDGET_BLOCKED"
    POLICY_VIOLATION_BLOCKED = "POLICY_VIOLATION_BLOCKED"
    SETTINGS_CHANGED = "SETTINGS_CHANGED"
    DATA_REDACTED = "DATA_REDACTED"

    # ComfyUI Live Telemetry & Streaming
    COMFY_STEP_PROGRESS = "COMFY_STEP_PROGRESS"
    COMFY_PREVIEW_FRAME = "COMFY_PREVIEW_FRAME"


RedactionLevel = Literal["metadata_only", "sanitized", "full_content"]
ActorType = Literal["user", "agent", "worker", "system"]


class EventEnvelope(BaseContractModel):
    """
    Standard immutable event envelope stored in run_events and transactional outbox.
    All runtime telemetry and audit streams conform strictly to this model.
    """
    event_id: str = Field(default_factory=generate_uuid, description="Unique event UUID")
    event_type: EventType = Field(..., description="Taxonomy event type")
    schema_version: int = Field(default=1, description="Event schema version")
    occurred_at: datetime = Field(default_factory=utc_now, description="UTC event occurrence timestamp")
    recorded_at: datetime = Field(default_factory=utc_now, description="UTC storage recording timestamp")

    # Scoping IDs
    project_id: str = Field(..., description="Project identifier")
    campaign_id: str = Field(..., description="Campaign identifier")
    request_id: str = Field(..., description="Initial user request identifier")
    run_id: str = Field(..., description="Run execution identifier")
    run_seq: int = Field(..., ge=1, description="Monotonically increasing sequence number per run_id")

    # Execution lineage IDs (Optional)
    workflow_version_id: Optional[str] = Field(default=None, description="Frozen workflow version ID")
    node_execution_id: Optional[str] = Field(default=None, description="Logical node execution ID")
    attempt_id: Optional[str] = Field(default=None, description="Execution attempt ID")
    agent_id: Optional[str] = Field(default=None, description="Assigned agent ID")

    # Distributed Tracing
    trace_id: Optional[str] = Field(default=None, description="OpenTelemetry / W3C Trace ID")
    span_id: Optional[str] = Field(default=None, description="OpenTelemetry Span ID")

    # Actor information
    actor_type: Optional[str] = Field(default=None, description="Actor type: user, agent, worker, system")
    actor_id: Optional[str] = Field(default=None, description="Actor ID identifier")

    # Causality & Correlation
    correlation_id: Optional[str] = Field(default=None, description="Correlation identifier across distributed calls")
    causation_event_id: Optional[str] = Field(default=None, description="Event ID that directly triggered this event")

    # Payload & Privacy
    payload_preview: Dict[str, Any] = Field(default_factory=dict, description="Safe metadata-only or sanitized preview")
    payload_ref: Optional[str] = Field(default=None, description="Object storage URI to full encrypted payload")
    redaction_level: RedactionLevel = Field(default="metadata_only", description="Data privacy redaction level")

    # Cryptographic integrity
    integrity_hash: str = Field(..., description="SHA256 integrity hash of this event")

    @classmethod
    def calculate_hash(
        cls,
        event_id: str,
        event_type: str,
        run_id: str,
        run_seq: int,
        occurred_at: datetime,
        payload_preview: Dict[str, Any],
        payload_ref: Optional[str] = None,
    ) -> str:
        """Deterministically calculate SHA256 integrity hash for an event."""
        norm_time = occurred_at.isoformat()
        norm_payload = json.dumps(payload_preview, sort_keys=True, default=str)
        raw_repr = f"{event_id}|{event_type}|{run_id}|{run_seq}|{norm_time}|{norm_payload}|{payload_ref or ''}"
        return f"sha256:{hashlib.sha256(raw_repr.encode('utf-8')).hexdigest()}"

    @classmethod
    def create(
        cls,
        event_type: EventType,
        project_id: str,
        campaign_id: str,
        request_id: str,
        run_id: str,
        run_seq: int,
        payload_preview: Optional[Dict[str, Any]] = None,
        payload_ref: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        event_id: Optional[str] = None,
        redaction_level: RedactionLevel = "metadata_only",
        workflow_version_id: Optional[str] = None,
        node_execution_id: Optional[str] = None,
        attempt_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        actor_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        causation_event_id: Optional[str] = None,
    ) -> "EventEnvelope":
        """Factory helper to construct an EventEnvelope with auto-computed integrity hash."""
        eid = event_id or generate_uuid()
        occ_at = occurred_at or utc_now()
        rec_at = utc_now()
        preview = payload_preview or {}
        itype = event_type.value if isinstance(event_type, EventType) else str(event_type)
        ihash = cls.calculate_hash(
            event_id=eid,
            event_type=itype,
            run_id=run_id,
            run_seq=run_seq,
            occurred_at=occ_at,
            payload_preview=preview,
            payload_ref=payload_ref,
        )

        return cls(
            event_id=eid,
            event_type=event_type,
            schema_version=1,
            occurred_at=occ_at,
            recorded_at=rec_at,
            project_id=project_id,
            campaign_id=campaign_id,
            request_id=request_id,
            run_id=run_id,
            run_seq=run_seq,
            workflow_version_id=workflow_version_id,
            node_execution_id=node_execution_id,
            attempt_id=attempt_id,
            agent_id=agent_id,
            trace_id=trace_id,
            span_id=span_id,
            actor_type=actor_type,
            actor_id=actor_id,
            correlation_id=correlation_id,
            causation_event_id=causation_event_id,
            payload_preview=preview,
            payload_ref=payload_ref,
            redaction_level=redaction_level,
            integrity_hash=ihash,
        )

    def verify_integrity(self) -> bool:
        """Verify that current integrity_hash matches calculated hash."""
        expected = self.calculate_hash(
            event_id=self.event_id,
            event_type=self.event_type.value if isinstance(self.event_type, EventType) else str(self.event_type),
            run_id=self.run_id,
            run_seq=self.run_seq,
            occurred_at=self.occurred_at,
            payload_preview=self.payload_preview,
            payload_ref=self.payload_ref,
        )
        return self.integrity_hash == expected
