"""
Unit and integration tests for Experiments and Learning Loop module.
"""

import unittest
from services.api.app.modules.experiments import (
    CausalityStatus,
    ExperimentMode,
    ExperimentService,
    LearningMemoryService,
    MetricCalculator,
    VariantVariable,
)
from services.api.app.modules.concepts.models import (
    ConceptBoard,
    CreativeHypothesis,
    HookFrameSpec,
    RankingDimensionScores,
    RankingEvaluation,
    RankingWeights,
)


class TestExperimentsModule(unittest.TestCase):

    def setUp(self):
        self.service = ExperimentService()
        self.dummy_board = ConceptBoard(
            hypothesis=CreativeHypothesis(
                game_profile_version_id="v_100",
                title="Royal Blast Original",
                audience="Casual players",
                genre="Match-3",
                intended_hook="Match 3 to rescue the king!",
                emotional_arc="Tension to relief",
                creative_mechanism="Gem blast",
                falsification_condition="CTR < 1%",
                novelty_rationale="Classic with a twist",
            ),
            hook_frame=HookFrameSpec(headline_text="Match 3 to rescue the king!"),
            ranking=RankingEvaluation(
                composite_score=0.75,
                dimension_scores=RankingDimensionScores(
                    evidence=0.7, game_fit=0.8, novelty=0.7, feasibility=0.8, hook_clarity=0.8, cost_fit=0.8
                ),
                weights_applied=RankingWeights(),
            ),
        )

    def test_zero_division_safety(self):
        # 1. Zero impressions
        res_zero_imp = MetricCalculator.calculate_metrics(impressions=0, clicks=0, installs=0, spend=50.0)
        self.assertIsNone(res_zero_imp.ctr)
        self.assertIsNone(res_zero_imp.ipm)
        self.assertIsNone(res_zero_imp.cpi)

        # 2. Positive impressions but zero installs
        res_zero_inst = MetricCalculator.calculate_metrics(impressions=1000, clicks=50, installs=0, spend=100.0)
        self.assertEqual(res_zero_inst.ctr, 0.05)
        self.assertEqual(res_zero_inst.ipm, 0.0)
        self.assertIsNone(res_zero_inst.cpi)

        # 3. Standard valid metrics
        res_valid = MetricCalculator.calculate_metrics(impressions=20000, clicks=1000, installs=200, spend=500.0)
        self.assertEqual(res_valid.ctr, 0.05)
        self.assertEqual(res_valid.ipm, 10.0)  # (200 / 20000) * 1000
        self.assertEqual(res_valid.cpi, 2.5)  # 500 / 200

    def test_single_variable_ab_plan_and_mode_badges(self):
        exp_real = self.service.create_experiment(
            project_id="proj_1",
            name="Hook A/B Test Real",
            control_board=self.dummy_board,
            variable_type=VariantVariable.HOOK,
            test_variation_description="ASMR sensory pop hook",
            mode=ExperimentMode.REAL_CAMPAIGN,
            min_sample_size=1000,
        )
        self.assertEqual(exp_real.mode_badge, "[VERIFIED REAL CAMPAIGN]")
        self.assertEqual(len(exp_real.variants), 2)
        self.assertTrue(exp_real.variants[0].is_control)
        self.assertFalse(exp_real.variants[1].is_control)
        self.assertEqual(exp_real.variants[1].variable_type, VariantVariable.HOOK)

        exp_offline = self.service.create_experiment(
            project_id="proj_1",
            name="Hook A/B Test Offline",
            control_board=self.dummy_board,
            variable_type=VariantVariable.CTA,
            test_variation_description="Endcard CTA text change",
            mode=ExperimentMode.OFFLINE,
        )
        self.assertEqual(exp_offline.mode_badge, "[SYNTHETIC / OFFLINE QA]")

    def test_premature_winner_forbidden_when_sample_size_insufficient(self):
        exp = self.service.create_experiment(
            project_id="proj_1",
            name="Sample Size Gate Test",
            control_board=self.dummy_board,
            variable_type=VariantVariable.HOOK,
            test_variation_description="Alternative hook",
            min_sample_size=1000,
        )
        c_var = exp.variants[0]
        t_var = exp.variants[1]

        # Only 200 impressions each (below min_sample_size of 1000)
        self.service.record_variant_metrics(exp.experiment_id, c_var.variant_id, impressions=200, clicks=5, installs=1, spend=10.0)
        self.service.record_variant_metrics(exp.experiment_id, t_var.variant_id, impressions=200, clicks=20, installs=4, spend=10.0)

        comp, insight = self.service.evaluate_experiment_results(exp.experiment_id)
        self.assertFalse(comp.sample_size_reached)
        self.assertIsNone(comp.winning_variant_id)
        self.assertIn("insufficient", comp.rationale.lower())
        self.assertEqual(insight.causality_status, CausalityStatus.INCONCLUSIVE)

    def test_statistically_significant_winner_declaration(self):
        exp = self.service.create_experiment(
            project_id="proj_1",
            name="Stat Sig Test",
            control_board=self.dummy_board,
            variable_type=VariantVariable.HOOK,
            test_variation_description="Winning ASMR hook",
            mode=ExperimentMode.REAL_CAMPAIGN,
            min_sample_size=1000,
        )
        c_var = exp.variants[0]
        t_var = exp.variants[1]

        # 5,000 impressions each: Control has 2% CTR, Test has 5% CTR
        self.service.record_variant_metrics(exp.experiment_id, c_var.variant_id, impressions=5000, clicks=100, installs=20, spend=100.0)
        self.service.record_variant_metrics(exp.experiment_id, t_var.variant_id, impressions=5000, clicks=250, installs=55, spend=100.0)

        comp, insight = self.service.evaluate_experiment_results(exp.experiment_id, genre_context="Match-3")
        self.assertTrue(comp.sample_size_reached)
        self.assertTrue(comp.is_statistically_significant)
        self.assertEqual(comp.winning_variant_id, t_var.variant_id)
        self.assertLess(comp.p_value, 0.001)

        # Learning insight must be verified causal because it was a controlled real campaign single-variable test
        self.assertEqual(insight.causality_status, CausalityStatus.VERIFIED_CAUSAL)
        self.assertEqual(insight.confidence, "high")
        self.assertIn("verified", insight.actionable_rule.lower())


if __name__ == "__main__":
    unittest.main()
