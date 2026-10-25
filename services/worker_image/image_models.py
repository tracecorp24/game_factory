from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

class ImageAssetRequest(BaseModel):
    concept_id: str
    prompt: str
    negative_prompt: Optional[str] = "ugly, distorted, blurry, low quality, watermark, text error"
    width: int = 1024
    height: int = 1024
    aspect_ratio: str = "1:1"  # "1:1", "9:16", "16:9"
    style_tokens: List[str] = Field(default_factory=list)
    seed: Optional[int] = None
    headline: Optional[str] = "Save the Kingdom!"
    hook_text: Optional[str] = "Can you solve this puzzle?"
    call_to_action: Optional[str] = "Play Now"
    provider_preference: Optional[str] = "mock"  # "mock" | "comfyui"

class ImageMetadata(BaseModel):
    width: int
    height: int
    aspect_ratio: str
    format: str = "png"
    channels: int = 4
    has_alpha: bool = True
    color_palette: List[str] = Field(default_factory=list)

class ImageAsset(BaseModel):
    artifact_id: str = Field(default_factory=lambda: f"art_img_{uuid.uuid4().hex[:12]}")
    run_id: str
    concept_id: str
    storage_ref: str
    preview_url: str
    sha256: str
    bytes: int
    metadata: ImageMetadata
    generation_call_id: str
    provider: str
    seed: Optional[int] = None
    prompt_used: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    parent_ids: List[str] = Field(default_factory=list)
