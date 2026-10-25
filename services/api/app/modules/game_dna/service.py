"""
Game Profile Application Service.
Provides lifecycle management, immutable version freezing, and compliance validation.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .models import (
    GameProfileVersion,
    MechanicGenre,
    MechanicValidationResult,
    MechanicsSpecType,
)
from .presets import create_match3_preset, create_merge_preset, create_sorting_preset
from .style_analyzer import StyleAnalyzer, StyleSuggestionResult
from .mechanic_validator import MechanicValidator


class GameProfileService:
    """
    Manages Game DNA Profiles and immutable frozen versions.
    Enforces the fundamental architectural rule:
    Once a GameProfileVersion is frozen or used in a run, it is strictly immutable.
    Any updates generate a new monotonic version ID.
    """

    def __init__(
        self,
        style_analyzer: Optional[StyleAnalyzer] = None,
        mechanic_validator: Optional[MechanicValidator] = None,
    ):
        self.style_analyzer = style_analyzer or StyleAnalyzer()
        self.mechanic_validator = mechanic_validator or MechanicValidator()
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._versions: Dict[str, GameProfileVersion] = {}

    def create_profile_from_preset(
        self,
        project_id: str,
        genre: MechanicGenre,
        name: str,
    ) -> GameProfileVersion:
        """Create a new game profile seeded with an official genre preset."""
        profile_id = str(uuid4())
        if genre == MechanicGenre.MATCH_3:
            version = create_match3_preset(profile_id=profile_id, name=name)
        elif genre == MechanicGenre.MERGE:
            version = create_merge_preset(profile_id=profile_id, name=name)
        elif genre == MechanicGenre.SORTING:
            version = create_sorting_preset(profile_id=profile_id, name=name)
        else:
            raise ValueError(f"No preset available for genre {genre}")

        self._versions[version.version_id] = version
        self._profiles[profile_id] = {
            "profile_id": profile_id,
            "project_id": project_id,
            "name": name,
            "active_version_id": version.version_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return version

    def register_custom_profile(
        self,
        project_id: str,
        name: str,
        genre: MechanicGenre,
        mechanics_spec: MechanicsSpecType,
        style_tokens: Optional[List[str]] = None,
        do_not_generate: Optional[List[str]] = None,
        allowed_ad_claims: Optional[List[str]] = None,
    ) -> GameProfileVersion:
        """Register a new custom GameProfile."""
        profile_id = str(uuid4())
        version = GameProfileVersion(
            profile_id=profile_id,
            version_number=1,
            name=name,
            genre=genre,
            mechanics_spec=mechanics_spec,
            style_tokens=style_tokens or [],
            do_not_generate=do_not_generate or [],
            allowed_ad_claims=allowed_ad_claims or [],
        )
        self._versions[version.version_id] = version
        self._profiles[profile_id] = {
            "profile_id": profile_id,
            "project_id": project_id,
            "name": name,
            "active_version_id": version.version_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        return version

    def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        return self._profiles.get(profile_id)

    def get_active_version(self, profile_id: str) -> Optional[GameProfileVersion]:
        profile = self._profiles.get(profile_id)
        if not profile:
            return None
        active_id = profile["active_version_id"]
        return self._versions.get(active_id)

    def get_version(self, version_id: str) -> Optional[GameProfileVersion]:
        return self._versions.get(version_id)

    def list_versions_for_profile(self, profile_id: str) -> List[GameProfileVersion]:
        return [v for v in self._versions.values() if v.profile_id == profile_id]

    def freeze_version(self, version_id: str) -> GameProfileVersion:
        """
        Permanently freezes a GameProfileVersion.
        Frozen versions can never be modified. Subsequent changes will fork a new version.
        """
        version = self._versions.get(version_id)
        if not version:
            raise KeyError(f"Version '{version_id}' not found.")

        frozen = version.freeze()
        self._versions[version_id] = frozen
        return frozen

    def update_profile_create_new_version(
        self,
        profile_id: str,
        updates: Dict[str, Any],
    ) -> GameProfileVersion:
        """
        Implements copy-on-write versioning.
        If current active version is frozen, automatically increments version_number
        and forks a new GameProfileVersion.
        """
        current_version = self.get_active_version(profile_id)
        if not current_version:
            raise KeyError(f"Profile '{profile_id}' has no active version.")

        # Ensure current version is frozen before forking
        if not current_version.is_frozen:
            current_version.freeze()

        # Build new version
        new_ver_num = current_version.version_number + 1
        data = current_version.model_dump()
        data["version_id"] = str(uuid4())
        data["parent_version_id"] = current_version.version_id
        data["version_number"] = new_ver_num
        data["is_frozen"] = False
        data["frozen_at"] = None
        data["created_at"] = datetime.now(timezone.utc).isoformat()
        data["content_hash"] = ""

        # Apply updates
        for key, value in updates.items():
            if key in data and key not in ["version_id", "profile_id", "version_number", "created_at"]:
                data[key] = value

        new_version = GameProfileVersion(**data)
        self._versions[new_version.version_id] = new_version
        self._profiles[profile_id]["active_version_id"] = new_version.version_id

        return new_version

    def diff_versions(self, version_id_a: str, version_id_b: str) -> Dict[str, Any]:
        """Compute structural differences between two profile versions."""
        ver_a = self._versions.get(version_id_a)
        ver_b = self._versions.get(version_id_b)
        if not ver_a or not ver_b:
            raise KeyError("One or both profile versions not found.")

        diffs = {
            "version_a": f"v{ver_a.version_number} ({ver_a.version_id})",
            "version_b": f"v{ver_b.version_number} ({ver_b.version_id})",
            "changes": {},
        }

        fields_to_compare = [
            "style_tokens",
            "do_not_generate",
            "allowed_ad_claims",
            "palette",
            "brand_constraints",
        ]
        for field in fields_to_compare:
            val_a = getattr(ver_a, field)
            val_b = getattr(ver_b, field)
            if val_a != val_b:
                diffs["changes"][field] = {
                    "from": val_a.model_dump() if hasattr(val_a, "model_dump") else val_a,
                    "to": val_b.model_dump() if hasattr(val_b, "model_dump") else val_b,
                }

        return diffs

    def validate_creative_against_profile(
        self,
        version_id: str,
        concept_title: str,
        intended_hook: str,
        creative_mechanism: str,
        proposed_claims: Optional[List[str]] = None,
    ) -> MechanicValidationResult:
        """Validate proposed creative against specific Game Profile Version."""
        version = self._versions.get(version_id)
        if not version:
            raise KeyError(f"Game profile version '{version_id}' not found.")
        return self.mechanic_validator.validate_creative(
            profile_version=version,
            concept_title=concept_title,
            intended_hook=intended_hook,
            creative_mechanism=creative_mechanism,
            proposed_claims=proposed_claims,
        )

    def extract_style_suggestions(
        self,
        game_name: str,
        asset_description: str,
        reference_notes: Optional[str] = None,
    ) -> StyleSuggestionResult:
        """Extract recommended style tokens and palette from visual notes."""
        return self.style_analyzer.analyze_design_notes(
            game_name=game_name,
            asset_description=asset_description,
            reference_notes=reference_notes,
        )
