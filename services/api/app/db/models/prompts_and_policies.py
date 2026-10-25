"""
Prompt templates, versioning, routing policies, and agent context bundles.
"""
from typing import Any, Dict, Optional
from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid


class PromptTemplate(Base, TimestampMixin):
    __tablename__ = "prompt_templates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    task_kind: Mapped[str] = mapped_column(String(64), nullable=False)  # hypothesis, image_gen, judge, etc.

    versions = relationship("PromptVersion", back_populates="template", cascade="all, delete-orphan")


class PromptVersion(Base, TimestampMixin):
    __tablename__ = "prompt_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    template_id: Mapped[str] = mapped_column(String(64), ForeignKey("prompt_templates.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    object_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False)
    template_body: Mapped[str] = mapped_column(Text, nullable=False)

    template = relationship("PromptTemplate", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("template_id", "version", name="uq_prompt_template_version"),
    )


class ModelPolicy(Base, TimestampMixin):
    __tablename__ = "model_policies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    rules_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    __table_args__ = (
        UniqueConstraint("project_id", "version", name="uq_model_policy_project_version"),
    )


class ContextBundle(Base, TimestampMixin):
    __tablename__ = "context_bundles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    run_id: Mapped[str] = mapped_column(String(64), ForeignKey("runs.id", ondelete="CASCADE"), index=True, nullable=False)
    refs_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    token_budget: Mapped[int] = mapped_column(Integer, default=8000, nullable=False)
    selected_token_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
