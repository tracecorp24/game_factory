"""
Game DNA Preset Factories for Match-3, Merge, and Sorting.
"""

from __future__ import annotations

from .models import (
    BrandConstraints,
    CharacterRef,
    ColorPalette,
    GameProfileVersion,
    Match3Spec,
    MechanicGenre,
    MergeSpec,
    SortingSpec,
)


def create_match3_preset(profile_id: str, name: str = "Royal Gems Match-3") -> GameProfileVersion:
    """Pre-configured profile for standard 8x8 cascade Match-3 mobile game."""
    return GameProfileVersion(
        profile_id=profile_id,
        version_number=1,
        name=name,
        genre=MechanicGenre.MATCH_3,
        mechanics_spec=Match3Spec(
            grid_width=8,
            grid_height=8,
            tile_types=["ruby_red", "sapphire_blue", "emerald_green", "topaz_yellow", "amethyst_purple"],
            move_limit=25,
            target_score=1500,
            special_combos=["4_in_a_row_rocket", "T_shape_bomb", "5_in_a_row_rainbow_gem"],
            booster_mechanics=["royal_hammer", "color_swap", "row_clear_lightning"],
            has_physics_drop=True,
        ),
        style_tokens=[
            "3d_casual_isometric",
            "glossy_juicy_gems",
            "vibrant_saturation",
            "gold_trimmed_hud",
            "smooth_satisfying_pops",
            "chibi_royal_mascot",
        ],
        palette=ColorPalette(
            primary="#FF3366",
            secondary="#4A148C",
            accent="#FFD700",
            background="#0D1B2A",
            surface="#1B263B",
            contrast_ratio=5.2,
            mood="Royal, Luxurious & Highly Satisfying",
        ),
        character_refs=[
            CharacterRef(
                name="King Reginald",
                role="Crown Mascot",
                visual_traits=["cheerful king", "cartoon crown", "red royal robe", "expressive facial reactions"],
            )
        ],
        brand_constraints=BrandConstraints(
            visual_tone="Polished, playful, regal casual elegance",
            prohibited_elements=[
                "depicting king in actual distress/gory harm",
                "false rescue pin-pull gameplay",
                "fake close buttons",
            ],
            required_disclaimers=[],
        ),
        do_not_generate=[
            "violence",
            "gore",
            "gloom",
            "pin_pulling_puzzles",
            "misleading_tower_defense_bait",
        ],
        allowed_ad_claims=[
            "Can you beat level 50?",
            "The most satisfying Match-3 of 2026!",
            "Chain reaction blast mania!",
            "Play free instantly!",
        ],
    )


def create_merge_preset(profile_id: str, name: str = "Garden Estate Merge-2") -> GameProfileVersion:
    """Pre-configured profile for standard 7x9 Merge-2 puzzle game."""
    return GameProfileVersion(
        profile_id=profile_id,
        version_number=1,
        name=name,
        genre=MechanicGenre.MERGE,
        mechanics_spec=MergeSpec(
            grid_width=7,
            grid_height=9,
            merge_depth=10,
            generator_items=["seed_planter", "gardening_shed", "flower_pot"],
            energy_cost_per_spawn=1,
            cooldown_seconds=45,
            has_board_evolution=True,
        ),
        style_tokens=[
            "warm_cozy_casual",
            "pastel_garden_tones",
            "cottagecore_aesthetic",
            "detailed_handcrafted_icons",
            "satisfying_merge_sparkles",
        ],
        palette=ColorPalette(
            primary="#4CAF50",
            secondary="#FF9800",
            accent="#8BC34A",
            background="#F1F8E9",
            surface="#FFFFFF",
            contrast_ratio=4.8,
            mood="Cozy, Relaxing, Cottagecore",
        ),
        character_refs=[
            CharacterRef(
                name="Daisy the Florist",
                role="Estate Renovator",
                visual_traits=["young woman", "green apron", "gardening sunhat", "warm smile"],
            )
        ],
        brand_constraints=BrandConstraints(
            visual_tone="Gentle, rewarding, uplifting renovation story",
            prohibited_elements=["cheating spouse drama bait", "freezing mother in snow bait"],
            required_disclaimers=[],
        ),
        do_not_generate=["melodrama_bait", "freezing_cabin_scams", "hyper_aggressive_violence"],
        allowed_ad_claims=[
            "Restore the forgotten garden!",
            "Merge, discover, and renovate!",
            "Relaxing merge puzzle fun!",
        ],
    )


def create_sorting_preset(profile_id: str, name: str = "Liquid Color Sort") -> GameProfileVersion:
    """Pre-configured profile for Water / Tube Sorting puzzle game."""
    return GameProfileVersion(
        profile_id=profile_id,
        version_number=1,
        name=name,
        genre=MechanicGenre.SORTING,
        mechanics_spec=SortingSpec(
            tube_count=5,
            tube_capacity=4,
            color_count=4,
            win_condition="Pour colored liquid until each glass contains only one color",
        ),
        style_tokens=[
            "asmr_minimalist",
            "smooth_liquid_shaders",
            "glass_refraction_effects",
            "calming_haptic_feedback",
            "clean_dark_ui",
        ],
        palette=ColorPalette(
            primary="#00E5FF",
            secondary="#FF007F",
            accent="#00FF66",
            background="#121212",
            surface="#1E1E1E",
            contrast_ratio=6.0,
            mood="ASMR, Crisp, Focused Logic",
        ),
        character_refs=[],
        brand_constraints=BrandConstraints(
            visual_tone="Minimalist, satisfying, intellectual brain training",
            prohibited_elements=["jarring screams", "deceptive mini-games"],
        ),
        do_not_generate=["unpleasant_liquids", "loud_distortions", "irrelevant_shooter_bait"],
        allowed_ad_claims=[
            "Can your brain sort this in 3 moves?",
            "Oddly satisfying ASMR puzzle",
            "IQ test for puzzle lovers",
        ],
    )
