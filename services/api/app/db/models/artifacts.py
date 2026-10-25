"""
Artifacts storage metadata, lineage graph, quality gate results, evaluations, and human reviews.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class Artifact(Base, TimestampMixin):
    __tablename__ = "artifacts"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), index=True, nullable=False)  # image, video, playable_zip, concept_board, evaluation_report, manifest
    storage_ref: Mapped[str] = mapped_column(String(1024), nullable=False)
    sha256: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    media_meta: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    state: Mapped[str] = mapped_column(String(64), default="created", nullable=False)  # created, validated, approved, rejected, archived

    quality_gate_results = relationship("QualityGateResult", back_populates="artifact", cascade="all, delete-orphan")
    evaluations = relationship("Evaluation", back_populates="artifact", cascade="all, delete-orphan")
    human_reviews = relationship("HumanReview", back_populates="artifact", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_artifacts_run_type", "run_id", "type"),
    )


class ArtifactLineage(Base):
    """
    Composite PK Directed Acyclic Graph connecting parent and derived child artifacts.
    """
    __tablename__ = "artifact_lineage"

    parent_artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="CASCADE"), primary_key=True)
    child_artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="CASCADE"), primary_key=True)
    relation_type: Mapped[str] = mapped_column(String(64), primary_key=True, default="derived_from")  # derived_from, storyboard_frame, evaluation_of, etc.

    parent = relationship("Artifact", foreign_keys=[parent_artifact_id])
    child = relationship("Artifact", foreign_keys=[child_artifact_id])


class QualityGateResult(Base, TimestampMixin):
    __tablename__ = "quality_gate_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="CASCADE"), index=True, nullable=False)
    rubric_version_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    gate_type: Mapped[str] = mapped_column(String(64), nullable=False)  # schema, technical, game_truth, visual, similarity, llm_judge, human_review
    state: Mapped[str] = mapped_column(String(64), default="passed", nullable=False)  # passed, failed, warning, skipped
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    details_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    artifact = relationship("Artifact", back_populates="quality_gate_results")

    __table_args__ = (
        Index("ix_gate_results_artifact_gate", "artifact_id", "gate_type"),
    )


class Evaluation(Base, TimestampMixin):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    target_artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False)
    rubric_version: Mapped[str] = mapped_column(String(64), default="v1", nullable=False)
    report_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    judge_invocation_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("model_invocations.id", ondelete="SET NULL"), nullable=True)
    overall_passed: Mapped[bool] = mapped_column(default=True, nullable=False)
    score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    artifact = relationship("Artifact", back_populates="evaluations")


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    artifact_id: Mapped[str] = mapped_column(String(64), ForeignKey("artifacts.id", ondelete="CASCADE"), index=True, nullable=False)
    reviewer_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision: Mapped[str] = mapped_column(String(64), nullable=False)  # approved, rejected, requested_changes
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    artifact = relationship("Artifact", back_populates="human_reviews")

    __table_args__ = (
        Index("ix_human_reviews_artifact_time", "artifact_id", "reviewed_at"),
    )
