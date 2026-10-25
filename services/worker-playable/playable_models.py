from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class PlayableSpec(BaseModel):
    spec_id: str = Field(default_factory=lambda: f"spec_{uuid.uuid4().hex[:10]}")
    title: str = "Kingdom Match-3 Rescue"
    hook_text: str = "Match 3 to break the curse!"
    cta_text: str = "PLAY NOW - FREE DOWNLOAD"
    cta_url: str = "https://apps.apple.com/app/example"
    target_score: int = 600
    max_moves: int = 8
    points_per_match: int = 100
    grid_rows: int = 8
    grid_cols: int = 8
    colors: List[str] = Field(default_factory=lambda: [
        "#EF4444", "#3B82F6", "#10B981", "#F59E0B", "#8B5CF6"
    ])
    background_color: str = "#0F172A"
    accent_color: str = "#38BDF8"
    template_name: str = "match3"
    custom_assets: Dict[str, str] = Field(default_factory=dict)

class BrowserTestReport(BaseModel):
    status: str  # "passed" | "failed"
    load_time_ms: float
    js_errors: List[str] = Field(default_factory=list)
    http_errors: List[str] = Field(default_factory=list)
    canvas_initialized: bool = True
    interactions_completed: int = 0
    screenshot_path: Optional[str] = None
    tested_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: Dict[str, Any] = Field(default_factory=dict)

class PlayableBundle(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"art_play_{uuid.uuid4().hex[:12]}")
    run_id: str
    spec_id: str
    storage_ref: str
    entrypoint: str = "index.html"
    sha256: str
    bytes: int
    preview_url: str
    zip_storage_ref: Optional[str] = None
    build_report: Dict[str, Any] = Field(default_factory=dict)
    test_report: Optional[BrowserTestReport] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    parent_ids: List[str] = Field(default_factory=list)
