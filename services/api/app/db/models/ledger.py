"""
Transactional Execution Ledger, Append-Only Run Events, and Transactional Outbox.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class RunEvent(Base):
    """
    Append-only event ledger table.
    Enforces strict uniqueness on (run_id, run_seq) and immutable historical record.
    """
    __tablename__ = "run_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    run_seq: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    schema_version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    campaign_id: Mapped[str] = mapped_column(String(64), nullable=False)
    request_id: Mapped[str] = mapped_column(String(64), nullable=False)

    workflow_version_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    node_execution_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    attempt_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    agent_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    trace_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    span_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    actor_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    actor_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    correlation_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    causation_event_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    payload_preview: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    payload_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    redaction_level: Mapped[str] = mapped_column(String(32), default="metadata_only", nullable=False)
    integrity_hash: Mapped[str] = mapped_column(String(128), nullable=False)

    __table_args__ = (
        UniqueConstraint("run_id", "run_seq", name="uq_run_events_run_id_seq"),
        Index("ix_run_events_time_type", "occurred_at", "event_type"),
    )


class OutboxEvent(Base, TimestampMixin):
    """
    Transactional outbox table for atomic event publication and reliable SSE delivery.
    """
    __tablename__ = "outbox_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    event_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    run_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    dispatched_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        # Partial-like index for finding undispatched events quickly
        Index("ix_outbox_undispatched", "dispatched_at", "created_at"),
    )


class AuditEvent(Base, TimestampMixin):
    """
    System audit ledger for governance, policy checks, and security actions.
    """
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    actor_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    redacted_diff_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_audit_events_entity", "entity_type", "entity_id", "created_at"),
        Index("ix_audit_events_actor_time", "actor_id", "created_at"),
    )
