"""
Creative hypotheses, concept boards, and human decision capture models.
"""
from typing import Any, Dict, Optional
from sqlalchemy import Float, ForeignKey, Index, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid


class CreativeHypothesis(Base, TimestampMixin):
    __tablename__ = "creative_hypotheses"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    report_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("trend_reports.id", ondelete="SET NULL"), nullable=True)
    spec_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    rank_version: Mapped[str] = mapped_column(String(64), default="v1", nullable=False)
    ranking_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    boards = relationship("ConceptBoard", back_populates="hypothesis", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_hypotheses_project_time", "project_id", "created_at"),
    )


class ConceptBoard(Base, TimestampMixin):
    __tablename__ = "concept_boards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    hypothesis_id: Mapped[str] = mapped_column(String(64), ForeignKey("creative_hypotheses.id", ondelete="CASCADE"), nullable=False)
    board_artifact_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    score_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    hypothesis = relationship("CreativeHypothesis", back_populates="boards")
    decisions = relationship("ConceptDecision", back_populates="board", cascade="all, delete-orphan")


class ConceptDecision(Base, TimestampMixin):
    __tablename__ = "concept_decisions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    concept_id: Mapped[str] = mapped_column(String(64), ForeignKey("concept_boards.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decision: Mapped[str] = mapped_column(String(64), nullable=False)  # select, reject, regenerate
    reason: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)

    board = relationship("ConceptBoard", back_populates="decisions")

    __table_args__ = (
        Index("ix_concept_decisions_concept_time", "concept_id", "created_at"),
    )
