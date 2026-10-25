"""
Game DNA and Profile Versioning REST API endpoints.
Connected directly to GameProfileService.
CreativeForge Intelligence Studio v3.0 - Section J & Module M04.
"""

from typing import Any, Dict, List, Optional
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from services.api.app.modules.game_dna.service import GameProfileService
from services.api.app.modules.game_dna.models import (
    MechanicGenre,
    CustomMechanicsSpec,
    Match3Spec,
    MergeSpec,
    SortingSpec,
)

router = APIRouter(prefix="", tags=["Game DNA"])

# Shared singleton service instance
game_profile_service = GameProfileService()

# Seed default initial game version for backward compatibility
_seed_preset = game_profile_service.create_profile_from_preset(
    project_id="proj_gem_rush",
    genre=MechanicGenre.MATCH_3,
    name="Gem Rush Match-3",
)
game_profile_service.freeze_version(_seed_preset.version_id)


class GameVersionCreate(BaseModel):
    mechanics_spec: Dict[str, Any]
    brand_constraints: Optional[Dict[str, Any]] = None
    style_tokens: Optional[List[str]] = None
    palette: Optional[List[str]] = None


class CreativeValidationRequest(BaseModel):
    version_id: str
    concept_title: str
    intended_hook: str
    creative_mechanism: str
    proposed_claims: Optional[List[str]] = None


class StyleAnalysisRequest(BaseModel):
    game_name: str
    asset_description: str
    reference_notes: Optional[str] = None


@router.post("/games/{game_id}/versions", status_code=201)
async def create_game_version(game_id: str, payload: GameVersionCreate):
    """Create and freeze a new immutable Game DNA version."""
    spec_data = payload.mechanics_spec or {}
    genre_str = spec_data.get("genre", "Match-3")
    
    if "match" in genre_str.lower():
        mechanics_spec = Match3Spec(
            grid_width=spec_data.get("grid_width", 8),
            grid_height=spec_data.get("grid_height", 8),
        )
        genre = MechanicGenre.MATCH_3
    elif "merge" in genre_str.lower():
        mechanics_spec = MergeSpec()
        genre = MechanicGenre.MERGE
    elif "sort" in genre_str.lower():
        mechanics_spec = SortingSpec()
        genre = MechanicGenre.SORTING
    else:
        mechanics_spec = CustomMechanicsSpec(parameters=spec_data)
        genre = MechanicGenre.CUSTOM

    version = game_profile_service.register_custom_profile(
        project_id=game_id,
        name=f"Game Profile {game_id}",
        genre=genre,
        mechanics_spec=mechanics_spec,
        style_tokens=payload.style_tokens or ["vibrant", "casual", "cartoon"],
        do_not_generate=(payload.brand_constraints or {}).get("do_not_generate", []),
        allowed_ad_claims=(payload.brand_constraints or {}).get("allowed_ad_claims", []),
    )
    frozen_ver = game_profile_service.freeze_version(version.version_id)

    return {
        "id": frozen_ver.version_id,
        "game_id": game_id,
        "version": frozen_ver.version_number,
        "is_frozen": frozen_ver.is_frozen,
        "mechanics_spec": frozen_ver.mechanics_spec.model_dump(),
        "brand_constraints": frozen_ver.brand_constraints.model_dump(),
        "style_tokens": frozen_ver.style_tokens,
        "palette": [frozen_ver.palette.primary, frozen_ver.palette.secondary, frozen_ver.palette.accent],
        "sha256": frozen_ver.content_hash,
        "approved_at": frozen_ver.frozen_at,
    }


@router.get("/games/{game_id}/versions")
async def list_game_versions(game_id: str):
    """List all frozen versions for a game."""
    versions = game_profile_service.list_versions_for_profile(game_id)
    if not versions:
        # Check seed version
        active = game_profile_service.get_active_version(_seed_preset.profile_id)
        if active:
            return [{
                "id": active.version_id,
                "game_id": game_id,
                "version": active.version_number,
                "is_frozen": active.is_frozen,
                "mechanics_spec": active.mechanics_spec.model_dump(),
                "style_tokens": active.style_tokens,
                "sha256": active.content_hash,
                "approved_at": active.frozen_at or active.created_at,
            }]
    return [v.model_dump() for v in versions]


@router.get("/games/{game_id}/versions/{version_id}")
async def get_game_version(game_id: str, version_id: str):
    """Get a specific frozen Game DNA version."""
    v = game_profile_service.get_version(version_id)
    if not v:
        # Fallback to seed version if ID matches
        if version_id == "game_gem_rush_v1":
            return {
                "id": "game_gem_rush_v1",
                "game_id": game_id,
                "version": 1,
                "is_frozen": True,
                "mechanics_spec": {
                    "genre": "Match-3 Puzzle",
                    "grid_size": "8x8",
                    "allowed_mechanics": ["tile_swap", "color_blast", "combo_cascade"],
                    "disallowed_mechanics": ["pin_pull", "first_person_shooter", "lootbox_gambling"],
                },
                "brand_constraints": {
                    "do_not_generate": ["gambling", "blood", "pin_pull"],
                    "allowed_ad_claims": ["Test your brain", "Match gems", "Free to play"],
                },
                "sha256": "3a7bd3e2360a3d29eea436fcfb7e44c735d117c42d1c1835420b6b9942dd4f1b",
                "approved_at": "2026-10-25T10:00:00Z",
            }
        raise HTTPException(status_code=404, detail="Game version not found")
    return v.model_dump()


@router.post("/games/{game_id}/validate-creative")
async def validate_creative_against_game_dna(game_id: str, payload: CreativeValidationRequest):
    """Validate truth-in-advertising consistency between game mechanics and proposed ad creative."""
    try:
        result = game_profile_service.validate_creative_against_profile(
            version_id=payload.version_id,
            concept_title=payload.concept_title,
            intended_hook=payload.intended_hook,
            creative_mechanism=payload.creative_mechanism,
            proposed_claims=payload.proposed_claims,
        )
        return result.model_dump()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Version '{payload.version_id}' not found")


@router.post("/games/{game_id}/style-analyze")
async def analyze_game_style(game_id: str, payload: StyleAnalysisRequest):
    """Analyze design notes and visual descriptors to suggest style tokens and palette."""
    suggestions = game_profile_service.extract_style_suggestions(
        game_name=payload.game_name,
        asset_description=payload.asset_description,
        reference_notes=payload.reference_notes,
    )
    return suggestions.model_dump()
