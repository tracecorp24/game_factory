"""
Game DNA profiles, frozen immutable versions, and asset rights.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.api.app.db.base import Base, TimestampMixin, generate_uuid


class GameProfile(Base, TimestampMixin):
    __tablename__ = "game_profiles"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active_version_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)

    versions = relationship("GameProfileVersion", back_populates="profile", cascade="all, delete-orphan")


class GameProfileVersion(Base, TimestampMixin):
    __tablename__ = "game_profile_versions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    profile_id: Mapped[str] = mapped_column(String(64), ForeignKey("game_profiles.id", ondelete="CASCADE"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    spec_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    hash: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    profile = relationship("GameProfile", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("profile_id", "version", name="uq_game_profile_version"),
    )


class AssetRight(Base, TimestampMixin):
    __tablename__ = "asset_rights"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    asset_id: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    license_kind: Mapped[str] = mapped_column(String(128), default="proprietary", nullable=False)
    evidence_ref: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
