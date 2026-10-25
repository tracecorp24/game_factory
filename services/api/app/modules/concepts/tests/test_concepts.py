"""
Unit and integration tests for Concepts module (ideation, heuristic ranking, and decision capture).
"""

import unittest
from services.api.app.modules.concepts import (
    ConceptService,
    ConceptRankingEngine,
    DecisionAction,
    DecisionCaptureError,
    RankingWeights,
)
from services.api.app.modules.concepts.models import CreativeHypothesis, PrimaryMetric
from services.api.app.modules.game_dna import GameProfileService, MechanicGenre
from services.worker_trends.models import EvidenceRef, TrendReport, TrendSignal


class TestConceptsModule(unittest.TestCase):

    def setUp(self):
        self.game_service = GameProfileService()
        self.profile_version = self.game_service.create_profile_from_preset(
            project_id="proj_test",
            genre=MechanicGenre.MATCH_3,
            name="Royal Castle Match",
        )
        self.trend_report = TrendReport(
            signals=[
                TrendSignal(
                    genre="Match-3",
                    mechanic_pattern="grid_matching",
                    hook_theme="ASMR Pops",
                    description="High performance from ASMR gem blasting",
                    evidence_refs=[
                        EvidenceRef(
                            source_id="apple_app_store_charts",
                            evidence_url="https://apps.apple.com/us/app/royal-match/id1482155847",
                            observed_at="2026-10-25T12:00:00Z",
                            raw_snapshot_id="snap_123",
                        )
                    ],
                )
            ]
        )
        self.concept_service = ConceptService()

    def test_ideation_generates_bounded_grounded_hypotheses(self):
        boards = self.concept_service.generate_and_rank_concepts(
            trend_report=self.trend_report,
            profile_version=self.profile_version,
            count=5,
        )
        self.assertEqual(len(boards), 5)

        for b in boards:
            h = b.hypothesis
            # Verify required hypothesis contract
            self.assertTrue(len(h.title) > 0)
            self.assertTrue(len(h.audience) > 0)
            self.assertEqual(h.genre, "Match-3")
            self.assertTrue(len(h.intended_hook) > 0)
            self.assertTrue(len(h.emotional_arc) > 0)
            self.assertGreater(len(h.evidence_refs), 0)
            self.assertTrue(len(h.creative_mechanism) > 0)
            self.assertIn(h.primary_metric, [PrimaryMetric.CTR, PrimaryMetric.IPM, PrimaryMetric.CPI_REDUCTION])
            self.assertTrue(len(h.falsification_condition) > 0)
            self.assertGreater(len(h.limitations), 0)
            self.assertTrue(len(h.novelty_rationale) > 0)

            # Verify ranking disclaimer
            self.assertFalse(b.ranking.is_calibrated)
            self.assertIn("not calibrated", b.ranking.disclaimer.lower())

    def test_heuristic_ranking_engine_formula_and_normalization(self):
        engine = ConceptRankingEngine()
        hypo = CreativeHypothesis(
            game_profile_version_id=self.profile_version.version_id,
            title="Cascade King",
            audience="Casual puzzle players",
            genre="Match-3",
            intended_hook="Blast 3 jewels to trigger a royal explosion!",
            emotional_arc="Curiosity to satisfaction",
            evidence_refs=["ref_1", "ref_2"],
            creative_mechanism="Explosive rainbow cascade",
            falsification_condition="CTR < 1.5%",
            novelty_rationale="Novel interactive chain reaction",
        )

        ranking = engine.evaluate_hypothesis(hypo, self.profile_version)
        d = ranking.dimension_scores

        # Acceptance criterion: All components strictly normalized to [0.0, 1.0]
        for name, val in [
            ("evidence", d.evidence),
            ("game_fit", d.game_fit),
            ("novelty", d.novelty),
            ("feasibility", d.feasibility),
            ("hook_clarity", d.hook_clarity),
            ("cost_fit", d.cost_fit),
        ]:
            self.assertGreaterEqual(val, 0.0, f"{name} below 0")
            self.assertLessEqual(val, 1.0, f"{name} above 1")

        # Verify composite calculation:
        # Score = 0.25*evidence + 0.20*game_fit + 0.20*novelty + 0.15*feasibility + 0.10*hook_clarity + 0.10*cost_fit
        expected = round(
            0.25 * d.evidence
            + 0.20 * d.game_fit
            + 0.20 * d.novelty
            + 0.15 * d.feasibility
            + 0.10 * d.hook_clarity
            + 0.10 * d.cost_fit,
            3,
        )
        self.assertAlmostEqual(ranking.composite_score, expected, places=3)

    def test_ranking_weights_sum_validation(self):
        # Valid weights summing to 1.0
        w_valid = RankingWeights(
            evidence=0.30,
            game_fit=0.20,
            novelty=0.20,
            feasibility=0.10,
            hook_clarity=0.10,
            cost_fit=0.10,
        )
        self.assertAlmostEqual(
            w_valid.evidence + w_valid.game_fit + w_valid.novelty + w_valid.feasibility + w_valid.hook_clarity + w_valid.cost_fit,
            1.0,
        )

        # Invalid weights not summing to 1.0
        with self.assertRaises(ValueError):
            RankingWeights(
                evidence=0.50,
                game_fit=0.50,
                novelty=0.50,
                feasibility=0.10,
                hook_clarity=0.10,
                cost_fit=0.10,
            )

    def test_decision_capture_and_workflow_envelope(self):
        boards = self.concept_service.generate_and_rank_concepts(
            trend_report=self.trend_report,
            profile_version=self.profile_version,
            count=3,
        )
        selected_board = boards[0]

        # 1. Empty reason should raise DecisionCaptureError
        with self.assertRaises(DecisionCaptureError):
            self.concept_service.record_user_decision(
                concept_id=selected_board.concept_id,
                action=DecisionAction.SELECT,
                reason="",
            )

        # 2. Valid select decision
        dec = self.concept_service.record_user_decision(
            concept_id=selected_board.concept_id,
            action=DecisionAction.SELECT,
            reason="Highest hook clarity and strong ASMR fit",
            actor="art_director_alice",
        )
        self.assertEqual(dec.action, DecisionAction.SELECT)
        self.assertEqual(dec.event_type, "CONCEPT_SELECTED")

        # 3. Build downstream workflow envelope
        payload = self.concept_service.build_workflow_envelope(dec)
        self.assertEqual(payload["event_type"], "CONCEPT_SELECTED")
        self.assertEqual(payload["concept_id"], selected_board.concept_id)
        self.assertEqual(payload["game_profile_version_id"], self.profile_version.version_id)
        self.assertIn("scene_layout", payload)
        self.assertEqual(payload["actor"], "art_director_alice")


if __name__ == "__main__":
    unittest.main()
