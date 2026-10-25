"""
Analytics materialized rollups and reporting tables.
"""
from datetime import datetime
from typing import Any, Dict
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from services.api.app.db.base import Base, TimestampMixin, generate_uuid, utc_now


class AnalyticsRollupHourly(Base, TimestampMixin):
    __tablename__ = "analytics_rollups_hourly"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(64), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    hour: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    dimensions_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    aggregate_json: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    watermark_seq: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (
        Index("ix_analytics_rollups_proj_hour", "project_id", "hour"),
    )
