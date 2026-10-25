"""
Workflow definitions, versions, execution requests, runs, and frozen manifests.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class Workflow(Base, TimestampMixin):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active_version_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    versions = relationship("WorkflowVersion", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowVersion(Base, TimestampMixin):
    __tablename__ = "workflow_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    workflow_id: Mapped[str] = mapped_column(String(64), ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    graph_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False)

    workflow = relationship("Workflow", back_populates="versions")
    runs = relationship("Run", back_populates="workflow_version")

    __table_args__ = (
        UniqueConstraint("workflow_id", "version", name="uq_workflow_version"),
    )


class Request(Base, TimestampMixin):
    __tablename__ = "requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    campaign_id: Mapped[str] = mapped_column(String(64), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    original_text_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    normalized_brief_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    runs = relationship("Run", back_populates="request")

    __table_args__ = (
        Index("ix_requests_campaign_time", "campaign_id", "created_at"),
    )


class Run(Base, TimestampMixin):
    __tablename__ = "runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    request_id: Mapped[str] = mapped_column(String(64), ForeignKey("requests.id", ondelete="CASCADE"), nullable=False)
    workflow_version_id: Mapped[str] = mapped_column(String(64), ForeignKey("workflow_versions.id", ondelete="RESTRICT"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="created", index=True, nullable=False)  # created, queued, running, paused, completed, failed, cancelled
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    run_manifest_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    request = relationship("Request", back_populates="runs")
    workflow_version = relationship("WorkflowVersion", back_populates="runs")
    manifest = relationship("RunManifest", back_populates="run", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_runs_project_state_time", "project_id", "state", "created_at"),
    )


class RunManifest(Base, TimestampMixin):
    __tablename__ = "run_manifests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), unique=True, nullable=False)
    json_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False)
    code_commit: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    manifest_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    run = relationship("Run", back_populates="manifest")
