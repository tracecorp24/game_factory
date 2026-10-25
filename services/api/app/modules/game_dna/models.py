"""
Game DNA and Brand Consistency Models (Pydantic v2).
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4
from pydantic import BaseModel, Field


class MechanicGenre(str, Enum):
    MATCH_3 = "Match-3"
    MERGE = "Merge"
    SORTING = "Sorting"
    CUSTOM = "Custom"


class Match3Spec(BaseModel):
    genre: MechanicGenre = MechanicGenre.MATCH_3
    grid_width: int = Field(default=8, ge=3, le=16)
    grid_height: int = Field(default=8, ge=3, le=16)
    tile_types: List[str] = Field(default_factory=lambda: ["red_gem", "blue_gem", "green_gem", "yellow_gem", "purple_gem"])
    move_limit: int = Field(default=25, ge=1)
    target_score: int = Field(default=1000, ge=1)
    special_combos: List[str] = Field(
        default_factory=lambda: ["4_in_a_row_rocket", "T_shape_bomb", "5_in_a_row_rainbow_blast"]
    )
    booster_mechanics: List[str] = Field(default_factory=lambda: ["hammer", "color_bomb", "swap_free"])
    has_physics_drop: bool = True


class MergeSpec(BaseModel):
    genre: MechanicGenre = MechanicGenre.MERGE
    grid_width: int = Field(default=7, ge=3, le=14)
    grid_height: int = Field(default=9, ge=3, le=14)
    merge_depth: int = Field(default=10, ge=2)
    generator_items: List[str] = Field(default_factory=lambda: ["seed_bag", "toolbox", "cleaning_cart"])
    energy_cost_per_spawn: int = Field(default=1, ge=1)
    cooldown_seconds: int = Field(default=60, ge=0)
    has_board_evolution: bool = True


class SortingSpec(BaseModel):
    genre: MechanicGenre = MechanicGenre.SORTING
    tube_count: int = Field(default=5, ge=2, le=20)
    tube_capacity: int = Field(default=4, ge=2, le=10)
    color_count: int = Field(default=4, ge=2, le=15)
    win_condition: str = "All tubes contain homogeneous colors or are empty"


class CustomMechanicsSpec(BaseModel):
    genre: MechanicGenre = MechanicGenre.CUSTOM
    description: str = "Custom game mechanics"
    parameters: Dict[str, Any] = Field(default_factory=dict)


MechanicsSpecType = Union[Match3Spec, MergeSpec, SortingSpec, CustomMechanicsSpec]


class ColorPalette(BaseModel):
    primary: str = "#FF4081"
    secondary: str = "#7C4DFF"
    accent: str = "#FFD700"
    background: str = "#1A1A2E"
    surface: str = "#16213E"
    contrast_ratio: float = 4.5
    mood: str = "Vibrant & Playful"


class CharacterRef(BaseModel):
    character_id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    role: str = "Hero / Mascot"
    visual_traits: List[str] = Field(default_factory=list)
    asset_url: Optional[str] = None
    expression_presets: List[str] = Field(default_factory=lambda: ["happy", "surprised", "frustrated", "triumphant"])


class BrandConstraints(BaseModel):
    visual_tone: str = "High-energy, satisfying, polished casual 3D"
    typography_font: str = "Rounded Bold Sans-Serif"
    prohibited_elements: List[str] = Field(
        default_factory=lambda: ["fake_os_dialogs", "fake_interactive_x_close", "excessive_gore", "misleading_genre_bait"]
    )
    required_disclaimers: List[str] = Field(default_factory=list)


class AssetRights(BaseModel):
    license_type: str = "Proprietary Original IP"
    rights_holder: str = "Game Studio Inc."
    commercial_allowed: bool = True
    notes: str = "All characters and audio cleared for digital ad distribution."


class GameProfileVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid4()))
    profile_id: str
    version_number: int = 1
    parent_version_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    frozen_at: Optional[str] = None
    is_frozen: bool = False
    name: str
    genre: MechanicGenre
    mechanics_spec: MechanicsSpecType
    style_tokens: List[str] = Field(default_factory=list)
    palette: ColorPalette = Field(default_factory=ColorPalette)
    character_refs: List[CharacterRef] = Field(default_factory=list)
    brand_constraints: BrandConstraints = Field(default_factory=BrandConstraints)
    do_not_generate: List[str] = Field(
        default_factory=lambda: ["violence", "depressing_scenarios", "impossible_gameplay_scams", "misleading_core_loop"]
    )
    allowed_ad_claims: List[str] = Field(
        default_factory=lambda: [
            "Can you beat level 20?",
            "Satisfying chain reactions!",
            "Brain puzzle mastery",
            "Play now for free!",
        ]
    )
    asset_rights: AssetRights = Field(default_factory=AssetRights)
    content_hash: str = ""

    def calculate_hash(self) -> str:
        raw = f"{self.profile_id}:{self.version_number}:{self.genre}:{self.mechanics_spec.model_dump_json()}:{self.style_tokens}:{self.do_not_generate}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if not self.content_hash:
            self.content_hash = self.calculate_hash()

    def freeze(self) -> GameProfileVersion:
        """Mark this version as permanently frozen and immutable."""
        if self.is_frozen:
            return self
        self.is_frozen = True
        self.frozen_at = datetime.now(timezone.utc).isoformat()
        self.content_hash = self.calculate_hash()
        return self


class MechanicValidationResult(BaseModel):
    is_compliant: bool
    compliance_score: float = Field(default=1.0, ge=0.0, le=1.0)
    violations: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
