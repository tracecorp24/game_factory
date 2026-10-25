"""
A/B Experimentation, variants, and empirical outcome metrics models.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    campaign_id: Mapped[str] = mapped_column(String(64), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    hypothesis_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("creative_hypotheses.id", ondelete="SET NULL"), nullable=True)
    mode: Mapped[str] = mapped_column(String(64), default="offline", nullable=False)  # offline, real_campaign
    outcome_source: Mapped[str] = mapped_column(String(128), default="qa_rubric", nullable=False)

    variants = relationship("ExperimentVariant", back_populates="experiment", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_experiments_campaign_mode", "campaign_id", "mode"),
    )


class ExperimentVariant(Base, TimestampMixin):
    __tablename__ = "experiment_variants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    experiment_id: Mapped[str] = mapped_column(String(64), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    artifact_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="SET NULL"), nullable=True)
    variant_controls_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    experiment = relationship("Experiment", back_populates="variants")
    outcomes = relationship("ExperimentOutcome", back_populates="variant", cascade="all, delete-orphan")


class ExperimentOutcome(Base, TimestampMixin):
    __tablename__ = "experiment_outcomes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    variant_id: Mapped[str] = mapped_column(String(64), ForeignKey("experiment_variants.id", ondelete="CASCADE"), nullable=False)
    observations_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)  # impressions, clicks, installs, spend, ctr, cpi
    window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    window_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    variant = relationship("ExperimentVariant", back_populates="outcomes")

    __table_args__ = (
        Index("ix_experiment_outcomes_variant_window", "variant_id", "window_start"),
    )
