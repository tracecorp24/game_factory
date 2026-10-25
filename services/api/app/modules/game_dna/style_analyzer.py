"""
Style and Visual Asset Analyzer.
Extracts style tokens, palettes, and brand guidelines from visual assets and design notes.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from .models import ColorPalette


class StyleSuggestionResult(BaseModel):
    style_tokens: List[str] = Field(default_factory=list)
    palette: ColorPalette = Field(default_factory=ColorPalette)
    mood_keywords: List[str] = Field(default_factory=list)
    recommended_negative_prompts: List[str] = Field(default_factory=list)
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    rationale: str = ""


class StyleAnalyzer:
    """
    Analyzes visual design text, color swatches, and asset descriptors
    to produce standardized Game DNA style tokens and constraints.
    """

    STYLE_VOCABULARY = {
        "3d_casual_isometric": ["isometric", "3d", "angle", "perspective", "blocky 3d"],
        "glossy_juicy_textures": ["glossy", "juicy", "candy", "shiny", "sparkling", "gems", "polished"],
        "vibrant_saturation": ["vibrant", "bright", "saturated", "colorful", "high saturation"],
        "pastel_soft_tones": ["pastel", "soft", "gentle", "watercolor", "muted", "cozy"],
        "cel_shaded_toon": ["cel shaded", "anime", "toon", "cartoon line", "comic"],
        "asmr_minimalist": ["asmr", "minimal", "clean", "smooth", "satisfying", "liquid", "zen"],
        "hyper_realistic_pbr": ["realistic", "pbr", "gritty", "photoreal", "hdr"],
    }

    HEX_REGEX = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")

    def analyze_design_notes(
        self,
        game_name: str,
        asset_description: str,
        reference_notes: Optional[str] = None,
    ) -> StyleSuggestionResult:
        """
        Extracts visual tokens and colors deterministically from design notes.
        """
        combined = f"{game_name} {asset_description} {reference_notes or ''}".lower()

        # Extract tokens
        detected_tokens: List[str] = []
        for token, triggers in self.STYLE_VOCABULARY.items():
            if any(trig in combined for trig in triggers):
                detected_tokens.append(token)

        if not detected_tokens:
            detected_tokens = ["3d_casual_isometric", "glossy_juicy_textures", "vibrant_saturation"]

        # Extract hex colors if mentioned
        hex_matches = self.HEX_REGEX.findall(asset_description + " " + (reference_notes or ""))
        if len(hex_matches) >= 3:
            palette = ColorPalette(
                primary=hex_matches[0],
                secondary=hex_matches[1],
                accent=hex_matches[2],
                background=hex_matches[3] if len(hex_matches) > 3 else "#1A1A2E",
                surface="#16213E",
                mood="Extracted from brand guidelines",
            )
        else:
            palette = ColorPalette()

        # Mood keywords
        moods = []
        if "cozy" in combined or "relax" in combined:
            moods.append("Cozy & Relaxing")
        if "juicy" in combined or "satisfying" in combined:
            moods.append("Satisfying & Juicy")
        if "luxurious" in combined or "royal" in combined:
            moods.append("Luxurious Regal")
        if not moods:
            moods.append("Playful Casual")

        # Negative prompts
        negative_prompts = [
            "lowres",
            "blurry",
            "photorealistic_uncanny",
            "dark_gritty_horror",
            "deformed_anatomy",
            "unauthorized_watermarks",
        ]

        return StyleSuggestionResult(
            style_tokens=detected_tokens,
            palette=palette,
            mood_keywords=moods,
            recommended_negative_prompts=negative_prompts,
            confidence=0.85 if hex_matches else 0.70,
            rationale=f"Identified {len(detected_tokens)} visual tokens from asset descriptors.",
        )
