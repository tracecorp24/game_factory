from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class VideoShot(BaseModel):
    shot_id: str
    start_sec: float
    end_sec: float
    name: str = "Scene"
    headline: str
    subtext: str
    visual_type: str = "gameplay"
    accent_color: str = "#3B82F6"
    asset_refs: List[str] = Field(default_factory=list)

class Storyboard(BaseModel):
    storyboard_id: str = Field(default_factory=lambda: f"sb_{uuid.uuid4().hex[:10]}")
    title: str = "CreativeForge Mobile Ad Storyboard"
    duration_seconds: float = 15.0
    fps: int = 30
    aspect_ratio: str = "9:16"
    width: int = 720
    height: int = 1280
    shots: List[VideoShot] = Field(default_factory=list)
    audio_track: Optional[str] = None
    target_cta_url: Optional[str] = "https://example.com/play"

class VideoProbeReport(BaseModel):
    valid: bool
    duration_seconds: float
    fps: float
    width: int
    height: int
    codec: str
    bitrate_kbps: Optional[int] = None
    issues: List[str] = Field(default_factory=list)

class VideoAsset(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"art_vid_{uuid.uuid4().hex[:12]}")
    run_id: str
    storyboard_id: str
    storage_ref: str
    preview_url: str
    sha256: str
    bytes: int
    duration_seconds: float
    fps: int
    resolution: str
    codec: str
    aspect_ratio: str = "9:16"
    generation_call_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    parent_ids: List[str] = Field(default_factory=list)
