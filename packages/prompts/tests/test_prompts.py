"""
Unit tests for packages.prompts registry and templates.
"""

import unittest
from packages.prompts import PromptRegistry


class TestPromptRegistry(unittest.TestCase):

    def test_registered_templates_exist(self):
        templates = PromptRegistry.list_templates()
        template_ids = [t["template_id"] for t in templates]
        expected = [
            "ideation",
            "genre_classifier",
            "style_extractor",
            "mechanic_validator",
            "heuristic_ranking",
            "learning_synthesis",
        ]
        for exp in expected:
            self.assertIn(exp, template_ids)

    def test_ideation_prompt_render(self):
        ver = PromptRegistry.get("ideation", "1.0.0")
        self.assertIsNotNone(ver.sha256)
        self.assertTrue(len(ver.sha256) == 64)

        rendered = ver.render(
            num_concepts=4,
            game_name="Royal Gems",
            genre="Match-3",
            mechanics_summary="8x8 cascade grid",
            style_tokens="3D glossy",
            brand_constraints="No violence",
            do_not_generate="Gore, pin pull",
            allowed_ad_claims="Beat level 50",
            trend_signals_json="[]",
            target_audience="Casual gamers",
            optimization_goal="IPM lift",
        )
        self.assertIn("Royal Gems", rendered["user_prompt"])
        self.assertIn("Match-3", rendered["user_prompt"])
        self.assertEqual(rendered["version"], "1.0.0")

    def test_missing_prompt_variables_raises(self):
        ver = PromptRegistry.get("genre_classifier")
        with self.assertRaises(ValueError):
            ver.render(app_title="Puzzle Game")  # missing description and tags


if __name__ == "__main__":
    unittest.main()
