"""
Unit and integration tests for Game DNA module.
"""

import unittest
from services.api.app.modules.game_dna import (
    GameProfileService,
    MechanicGenre,
    StyleAnalyzer,
    MechanicValidator,
)


class TestGameDNA(unittest.TestCase):

    def setUp(self):
        self.service = GameProfileService()

    def test_preset_creation(self):
        v_m3 = self.service.create_profile_from_preset("p1", MechanicGenre.MATCH_3, "Royal Saga")
        self.assertEqual(v_m3.genre, MechanicGenre.MATCH_3)
        self.assertEqual(v_m3.version_number, 1)
        self.assertFalse(v_m3.is_frozen)
        self.assertIn("3d_casual_isometric", v_m3.style_tokens)

        v_merge = self.service.create_profile_from_preset("p1", MechanicGenre.MERGE, "Mansion Merge")
        self.assertEqual(v_merge.genre, MechanicGenre.MERGE)

        v_sort = self.service.create_profile_from_preset("p1", MechanicGenre.SORTING, "Water Sort")
        self.assertEqual(v_sort.genre, MechanicGenre.SORTING)

    def test_version_freezing_and_immutability(self):
        v = self.service.create_profile_from_preset("p1", MechanicGenre.MATCH_3, "Match Castle")
        orig_id = v.version_id

        # Freeze version
        frozen_v = self.service.freeze_version(orig_id)
        self.assertTrue(frozen_v.is_frozen)
        self.assertIsNotNone(frozen_v.frozen_at)
        orig_hash = frozen_v.content_hash

        # Update profile -> must produce a new version and preserve old version
        new_v = self.service.update_profile_create_new_version(
            profile_id=frozen_v.profile_id,
            updates={"style_tokens": ["neon_cyber_gems", "futuristic_hologram"]},
        )
        self.assertEqual(new_v.version_number, 2)
        self.assertEqual(new_v.parent_version_id, orig_id)
        self.assertNotEqual(new_v.version_id, orig_id)

        # Verify old version remains unchanged
        old_v = self.service.get_version(orig_id)
        self.assertTrue(old_v.is_frozen)
        self.assertEqual(old_v.content_hash, orig_hash)
        self.assertIn("3d_casual_isometric", old_v.style_tokens)
        self.assertNotIn("neon_cyber_gems", old_v.style_tokens)

    def test_diff_versions(self):
        v1 = self.service.create_profile_from_preset("p1", MechanicGenre.MATCH_3, "Gems Diff")
        self.service.freeze_version(v1.version_id)
        v2 = self.service.update_profile_create_new_version(
            profile_id=v1.profile_id,
            updates={"style_tokens": ["updated_art_style"]},
        )
        diff = self.service.diff_versions(v1.version_id, v2.version_id)
        self.assertIn("style_tokens", diff["changes"])

    def test_style_analyzer(self):
        analyzer = StyleAnalyzer()
        res = analyzer.analyze_design_notes(
            game_name="Candy Splash",
            asset_description="Glossy juicy candy gems with bright vibrant saturation and sparkling particle pops. Primary #FF0055, secondary #00CCFF, accent #FFFF00.",
        )
        self.assertIn("glossy_juicy_textures", res.style_tokens)
        self.assertIn("vibrant_saturation", res.style_tokens)
        self.assertEqual(res.palette.primary, "#FF0055")
        self.assertEqual(res.palette.secondary, "#00CCFF")

    def test_mechanic_validator_truth_in_advertising(self):
        v = self.service.create_profile_from_preset("p1", MechanicGenre.MATCH_3, "Truth Match")

        # 1. Compliant concept
        compliant_res = self.service.validate_creative_against_profile(
            version_id=v.version_id,
            concept_title="Cascade Blast",
            intended_hook="Match 3 gems to trigger a mega cascade blast!",
            creative_mechanism="Chain reaction explosion",
            proposed_claims=["Can you beat level 50?"],
        )
        self.assertTrue(compliant_res.is_compliant)
        self.assertEqual(compliant_res.compliance_score, 1.0)
        self.assertEqual(len(compliant_res.violations), 0)

        # 2. Deceptive bait (Pin Pull on Match-3)
        bait_res = self.service.validate_creative_against_profile(
            version_id=v.version_id,
            concept_title="Save the King",
            intended_hook="Pull the pin to save the king from lava!",
            creative_mechanism="Pin pulling puzzle",
            proposed_claims=[],
        )
        self.assertFalse(bait_res.is_compliant)
        self.assertLess(bait_res.compliance_score, 0.7)
        self.assertTrue(any("pin_pull" in viol.lower() or "deceptive" in viol.lower() for viol in bait_res.violations))

        # 3. Prohibited do_not_generate motif (Violence/Gore)
        gore_res = self.service.validate_creative_against_profile(
            version_id=v.version_id,
            concept_title="Dark Dungeon",
            intended_hook="Watch brutal violence unfold!",
            creative_mechanism="Gory traps",
            proposed_claims=[],
        )
        self.assertFalse(gore_res.is_compliant)
        self.assertTrue(any("do_not_generate" in viol for viol in gore_res.violations))


if __name__ == "__main__":
    unittest.main()
