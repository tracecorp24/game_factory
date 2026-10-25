"""
Node executions, attempts, model invocations, token usage, cost entries, and tool calls.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class NodeExecution(Base, TimestampMixin):
    __tablename__ = "node_executions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    node_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    node_version: Mapped[str] = mapped_column(String(32), default="v1", nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="created", nullable=False)  # pending, running, completed, failed, skipped
    timings_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    attempts = relationship("Attempt", back_populates="node_execution", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_node_exec_run_node", "run_id", "node_id"),
    )


class Attempt(Base, TimestampMixin):
    __tablename__ = "attempts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    node_execution_id: Mapped[str] = mapped_column(String(64), ForeignKey("node_executions.id", ondelete="CASCADE"), nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="running", nullable=False)  # running, succeeded, failed, retried
    error_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    backoff_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    node_execution = relationship("NodeExecution", back_populates="attempts")
    model_invocations = relationship("ModelInvocation", back_populates="attempt", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="attempt", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("node_execution_id", "attempt_no", name="uq_attempt_node_no"),
    )


class AgentSession(Base, TimestampMixin):
    __tablename__ = "agent_sessions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    agent_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    node_execution_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("node_executions.id", ondelete="SET NULL"), nullable=True)
    context_bundle_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class ModelInvocation(Base, TimestampMixin):
    __tablename__ = "model_invocations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(String(64), ForeignKey("attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model_requested: Mapped[str] = mapped_column(String(128), nullable=False)
    model_resolved: Mapped[str] = mapped_column(String(128), nullable=False)
    provider_request_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    state: Mapped[str] = mapped_column(String(64), default="started", nullable=False)  # started, completed, failed
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    attempt = relationship("Attempt", back_populates="model_invocations")
    usage_records = relationship("UsageRecord", back_populates="invocation", cascade="all, delete-orphan")
    cost_entries = relationship("CostEntry", back_populates="invocation", cascade="all, delete-orphan")


class UsageRecord(Base, TimestampMixin):
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    invocation_id: Mapped[str] = mapped_column(String(64), ForeignKey("model_invocations.id", ondelete="CASCADE"), index=True, nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cached_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reasoning_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="provider_reported", nullable=False)  # provider_reported, estimated, invoice_reconciled, missing
    modality_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    invocation = relationship("ModelInvocation", back_populates="usage_records")


class PriceCatalogVersion(Base, TimestampMixin):
    __tablename__ = "price_catalog_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    provider: Mapped[str] = mapped_column(String(64), nullable=False)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unit_prices_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        Index("ix_price_cat_provider_model", "provider", "model", "effective_from"),
    )


class CostEntry(Base, TimestampMixin):
    __tablename__ = "cost_entries"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    invocation_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("model_invocations.id", ondelete="SET NULL"), nullable=True)
    usage_record_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("usage_records.id", ondelete="SET NULL"), nullable=True)
    price_version_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("price_catalog_versions.id", ondelete="SET NULL"), nullable=True)
    amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD", nullable=False)
    cost_kind: Mapped[str] = mapped_column(String(64), nullable=False)  # llm_token, image_generation, video_generation, compute_second
    status: Mapped[str] = mapped_column(String(64), default="actual", nullable=False)  # estimated, actual, reconciled

    invocation = relationship("ModelInvocation", back_populates="cost_entries")

    __table_args__ = (
        Index("ix_cost_entries_kind_status", "cost_kind", "status", "created_at"),
    )


class ToolCall(Base, TimestampMixin):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    attempt_id: Mapped[str] = mapped_column(String(64), ForeignKey("attempts.id", ondelete="CASCADE"), index=True, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    args_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    result_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    status: Mapped[str] = mapped_column(String(64), default="completed", nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    attempt = relationship("Attempt", back_populates="tool_calls")
