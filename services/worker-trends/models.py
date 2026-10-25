"""
Trend Intelligence and Evidence Data Models (Pydantic v2).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


class CollectionMethod(str, Enum):
    OFFICIAL_FEED = "official_feed"
    AUTHORIZED_API = "authorized_api"
    MANUAL_IMPORT = "manual_import"
    CSV_UPLOAD = "csv_upload"
    SIMULATED_MOCK = "simulated_mock"


class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SourceStatus(str, Enum):
    ACTIVE = "active"
    REQUIRES_AUTH = "requires_auth"
    MANUAL_IMPORT_REQUIRED = "manual_import_required"
    DISABLED = "disabled"


class EvidenceRef(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    evidence_url: str
    observed_at: str
    raw_snapshot_id: str
    rank: Optional[int] = None
    observation_snippet: str = ""
    license_note: str = "Authorized public or user-provided data"
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM


class TrendObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    app_name: str
    bundle_id: Optional[str] = None
    developer: Optional[str] = None
    rank: Optional[int] = None
    category: Optional[str] = None
    genre: Optional[str] = None
    mechanic_tags: List[str] = Field(default_factory=list)
    creative_tags: List[str] = Field(default_factory=list)
    hook_text: Optional[str] = None
    evidence_url: str = ""
    observed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    region: str = "US"
    platform: str = "iOS"
    metrics: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RawSnapshot(BaseModel):
    snapshot_id: str = Field(default_factory=lambda: str(uuid4()))
    source_id: str
    collection_method: CollectionMethod
    region: str = "US"
    platform: str = "iOS"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    raw_hash: str = ""
    record_count: int = 0
    records: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def calculate_hash(self) -> str:
        data_str = f"{self.source_id}:{self.region}:{self.platform}:{len(self.records)}:{repr(self.records)}"
        return hashlib.sha256(data_str.encode("utf-8")).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if not self.raw_hash:
            self.raw_hash = self.calculate_hash()
        if not self.record_count:
            self.record_count = len(self.records)


class TrendSignal(BaseModel):
    signal_id: str = Field(default_factory=lambda: str(uuid4()))
    genre: str
    mechanic_pattern: str
    hook_theme: str
    description: str
    evidence_refs: List[EvidenceRef] = Field(default_factory=list)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    sample_size: int = 0
    recency_days: float = 0.0
    recommended_angles: List[str] = Field(default_factory=list)


class TrendReport(BaseModel):
    report_id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    signals: List[TrendSignal] = Field(default_factory=list)
    total_snapshots_analyzed: int = 0
    total_observations: int = 0
    source_distribution: Dict[str, int] = Field(default_factory=dict)
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    limitations: List[str] = Field(default_factory=list)
    missingness_note: Optional[str] = None
