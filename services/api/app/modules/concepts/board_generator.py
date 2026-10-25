"""
Mockup Concept Board Generator.
Assembles interactive board cards with scene layout, hook frame spec, and ranking metrics.
"""

from __future__ import annotations

from typing import Optional
from .models import (
    ConceptBoard,
    CreativeHypothesis,
    HookFrameSpec,
    RankingEvaluation,
    SceneLayoutSpec,
)
from services.api.app.modules.game_dna.models import GameProfileVersion


class ConceptBoardGenerator:
    """
    Renders concept board cards containing game layout specifications,
    ad hook keyframe visuals, audio cues, and heuristic scores.
    """

    def generate_board(
        self,
        hypothesis: CreativeHypothesis,
        ranking: RankingEvaluation,
        profile_version: Optional[GameProfileVersion] = None,
    ) -> ConceptBoard:
        """Constructs an actionable ConceptBoard from a hypothesis and ranking evaluation."""
        genre_name = profile_version.genre.value if profile_version else hypothesis.genre

        # Tailor scene layout according to genre
        scene_layout = SceneLayoutSpec(
            layout_type="vertical_9_16",
            grid_placement="center_lower_half",
            character_placement=(
                "top_left_reaction_cam"
                if (profile_version and profile_version.character_refs)
                else "hidden"
            ),
            hud_spec={
                "top_bar": f"{genre_name} Score Star Meter | Level 42",
                "center_toast": "Dynamic combo multipliers (x2, x4, Mega Combo!)",
                "bottom_bar": "Interactive booster tray with pulsing highlights",
            },
            visual_effects=[
                "haptic_screen_shake_on_cascade",
                "particle_burst_custom_palette",
                "floating_golden_score_numbers",
            ],
        )

        hook_frame = HookFrameSpec(
            duration_seconds=3.0,
            headline_text=hypothesis.intended_hook,
            headline_style=(
                "Bold Impact typography, yellow fill with black stroke, "
                "bouncing downward entrance with subtle pulse"
            ),
            audio_cue="Satisfying tactile pop + tension buildup chord",
            interaction_cue="Glowing animated tutorial finger demonstrating first move",
        )

        return ConceptBoard(
            hypothesis=hypothesis,
            scene_layout=scene_layout,
            hook_frame=hook_frame,
            ranking=ranking,
            preview_asset_id=f"preview_{hypothesis.hypothesis_id[:8]}",
        )
