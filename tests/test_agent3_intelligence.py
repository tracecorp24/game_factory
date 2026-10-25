"""
Root test runner for Agent 3 (Trend Intelligence, Game DNA, Concepts & Experiments).
Ensures all Agent 3 acceptance criteria are continuously verified in the primary test suite.
"""

import unittest
from datetime import datetime, timezone

from packages.prompts import PromptRegistry
from services.worker_trends.models import CollectionMethod, RawSnapshot, SourceStatus
from services.worker_trends.adapters.apple_charts import AppleChartsAdapter
from services.worker_trends.adapters.csv_import import CsvImportAdapter, CsvImportValidationError
from services.worker_trends.adapters.base import ToSPermissionError
from services.worker_trends.genre_classifier import GenreClassifier
from services.worker_trends.evidence_resolver import EvidenceResolver
from services.worker_trends.ingestion import TrendIngestionService
from services.api.app.modules.intelligence.service import IntelligenceService
from services.api.app.modules.game_dna import (
    GameProfileService,
    MechanicGenre,
    StyleAnalyzer,
    MechanicValidator,
)
from services.api.app.modules.concepts import (
    ConceptService,
    ConceptRankingEngine,
    DecisionAction,
    DecisionCaptureError,
    RankingWeights,
)
from services.api.app.modules.concepts.models import CreativeHypothesis, PrimaryMetric
from services.worker_trends.models import EvidenceRef, TrendReport, TrendSignal
from services.api.app.modules.experiments import (
    CausalityStatus,
    ExperimentMode,
    ExperimentService,
    MetricCalculator,
    VariantVariable,
)
from services.api.app.modules.concepts.models import (
    ConceptBoard,
    HookFrameSpec,
    RankingDimensionScores,
    RankingEvaluation,
)


class TestAgent3CompleteSuite(unittest.TestCase):

    def test_prompt_registry_complete(self):
        templates = PromptRegistry.list_templates()
        ids = [t["template_id"] for t in templates]
        for exp in ["ideation", "genre_classifier", "style_extractor", "mechanic_validator", "heuristic_ranking", "learning_synthesis"]:
            self.assertIn(exp, ids)

    def test_trend_tos_and_evidence_acceptance(self):
        adapter = AppleChartsAdapter(is_authorized=False, tos_accepted=False)
        self.assertEqual(adapter.status, SourceStatus.REQUIRES_AUTH)
        with self.assertRaises(ToSPermissionError):
            adapter.fetch()

        resolver = EvidenceResolver()
        ingestion = TrendIngestionService(resolver=resolver)
        records = [
            {"app_name": "Royal Match", "evidence_url": "https://apple.com/app1", "observed_at": datetime.now(timezone.utc).isoformat(), "rank": 1}
        ]
        snap = RawSnapshot(source_id="apple", collection_method=CollectionMethod.OFFICIAL_FEED, records=records)
        ingestion.ingest_snapshot(snap)
        report = ingestion.generate_trend_report()
        self.assertGreater(len(report.signals), 0)
        self.assertTrue(report.signals[0].evidence_refs[0].evidence_url.startswith("http"))
        self.assertIsNotNone(report.signals[0].evidence_refs[0].observed_at)

    def test_game_dna_immutability_acceptance(self):
        service = GameProfileService()
        v1 = service.create_profile_from_preset("p_root", MechanicGenre.MATCH_3, "Royal DNA")
        frozen_v1 = service.freeze_version(v1.version_id)
        self.assertTrue(frozen_v1.is_frozen)
        orig_hash = frozen_v1.content_hash

        v2 = service.update_profile_create_new_version(
            profile_id=frozen_v1.profile_id,
            updates={"style_tokens": ["updated_cyber_gems"]},
        )
        self.assertEqual(v2.version_number, 2)
        self.assertEqual(v2.parent_version_id, frozen_v1.version_id)
        # Verify previous version remains strictly immutable
        old_v1 = service.get_version(frozen_v1.version_id)
        self.assertTrue(old_v1.is_frozen)
        self.assertEqual(old_v1.content_hash, orig_hash)

    def test_heuristic_ranking_normalization_acceptance(self):
        engine = ConceptRankingEngine()
        hypo = CreativeHypothesis(
            game_profile_version_id="gp_1",
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
        ranking = engine.evaluate_hypothesis(hypo)
        d = ranking.dimension_scores
        for val in [d.evidence, d.game_fit, d.novelty, d.feasibility, d.hook_clarity, d.cost_fit]:
            self.assertTrue(0.0 <= val <= 1.0)
        self.assertTrue(0.0 <= ranking.composite_score <= 1.0)
        self.assertFalse(ranking.is_calibrated)
        self.assertIn("not calibrated", ranking.disclaimer.lower())

    def test_zero_division_safety_acceptance(self):
        zero_res = MetricCalculator.calculate_metrics(impressions=0, clicks=0, installs=0, spend=100.0)
        self.assertIsNone(zero_res.ctr)
        self.assertIsNone(zero_res.ipm)
        self.assertIsNone(zero_res.cpi)


if __name__ == "__main__":
    unittest.main()
