"""
Trend intelligence, source registry, snapshots, and observation models.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import DateTime, Float, ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class SourceRegistry(Base, TimestampMixin):
    __tablename__ = "source_registry"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    source_type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # apple_charts, csv_upload, etc.
    access_policy: Mapped[str] = mapped_column(String(64), default="public_read", nullable=False)
    terms_checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sync_jobs = relationship("SourceSyncJob", back_populates="source", cascade="all, delete-orphan")
    snapshots = relationship("RawSnapshot", back_populates="source", cascade="all, delete-orphan")


class SourceSyncJob(Base, TimestampMixin):
    __tablename__ = "source_sync_jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(64), ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[str] = mapped_column(String(64), default="queued", nullable=False)  # queued, running, completed, failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    errors: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    source = relationship("SourceRegistry", back_populates="sync_jobs")

    __table_args__ = (
        Index("ix_sync_jobs_source_status", "source_id", "status", "created_at"),
    )


class RawSnapshot(Base, TimestampMixin):
    __tablename__ = "raw_snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    source_id: Mapped[str] = mapped_column(String(64), ForeignKey("source_registry.id", ondelete="CASCADE"), nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    object_ref: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(128), index=True, nullable=False)

    source = relationship("SourceRegistry", back_populates="snapshots")
    observations = relationship("TrendObservation", back_populates="snapshot", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_snapshots_source_time", "source_id", "observed_at"),
    )


class TrendObservation(Base, TimestampMixin):
    __tablename__ = "trend_observations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    snapshot_id: Mapped[str] = mapped_column(String(64), ForeignKey("raw_snapshots.id", ondelete="CASCADE"), nullable=False)
    game_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    genre: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    metric_type: Mapped[str] = mapped_column(String(64), nullable=False)  # rank, downloads, revenue, sentiment
    value: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    region: Mapped[str] = mapped_column(String(32), default="global", index=True, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, index=True, nullable=False)

    snapshot = relationship("RawSnapshot", back_populates="observations")

    __table_args__ = (
        Index("ix_trend_obs_region_genre_time", "region", "genre", "observed_at"),
    )


class TrendReport(Base, TimestampMixin):
    __tablename__ = "trend_reports"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    snapshot_ids: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    report_ref: Mapped[str] = mapped_column(String(1024), nullable=False)
    model_call_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    __table_args__ = (
        Index("ix_trend_reports_project_time", "project_id", "created_at"),
    )
