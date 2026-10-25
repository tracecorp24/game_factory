"""
SQLAlchemy 2.0 Database Models for ComfyUI Presets, Versions, and Model Catalog.
CreativeForge Intelligence Studio v3.0 - Agent H3.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class ComfyPreset(Base, TimestampMixin):
    """Registered ComfyUI visual pipeline preset."""
    __tablename__ = "comfy_presets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    description: Mapped[str] = mapped_column(String(1024), default="", nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    active_version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    versions = relationship(
        "ComfyPresetVersion",
        back_populates="preset",
        cascade="all, delete-orphan",
        order_by="ComfyPresetVersion.created_at.desc()",
        lazy="selectin",
    )


class ComfyPresetVersion(Base, TimestampMixin):
    """Immutable versioned snapshot of a ComfyUI pipeline preset."""
    __tablename__ = "comfy_preset_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    preset_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("comfy_presets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    workflow_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    exposed_variables: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    checksum: Mapped[str] = mapped_column(String(128), nullable=False)

    preset = relationship("ComfyPreset", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("preset_id", "version", name="uq_comfy_preset_version"),
    )


class ComfyModelCatalog(Base, TimestampMixin):
    """Diffusion checkpoints, LoRAs, ControlNets, VAEs, and Upscalers catalog."""
    __tablename__ = "comfy_models"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    filename: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    model_type: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    sha256: Mapped[str] = mapped_column(String(128), nullable=False)
    is_downloaded: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    size_bytes: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)
    vram_requirement_mb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    local_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
