"""
Unit and integration tests for worker-trends (Agent 3).
"""
import unittest
import uuid
from datetime import datetime, timezone

from services.worker_trends import (
    CollectionMethod,
    ConfidenceLevel,
    RawSnapshot,
    SourceStatus,
    SourceAdapter,
    ToSPermissionError,
    AppleChartsAdapter,
    CsvImportAdapter,
    CsvImportValidationError,
    GenreClassifier,
    EvidenceResolver,
    TrendIngestionService,
)


class TestSourceAdapters(unittest.TestCase):

    def test_tos_permission_gate(self):
        adapter = AppleChartsAdapter(is_authorized=False, tos_accepted=False)
        self.assertEqual(adapter.status, SourceStatus.REQUIRES_AUTH)
        with self.assertRaises(ToSPermissionError):
            adapter.fetch()

        adapter_no_auth = AppleChartsAdapter(is_authorized=False, tos_accepted=True)
        self.assertEqual(adapter_no_auth.status, SourceStatus.MANUAL_IMPORT_REQUIRED)
        with self.assertRaises(ToSPermissionError):
            adapter_no_auth.fetch()

    def test_apple_charts_adapter_with_fixture(self):
        fixture = [
            {"app_name": "Royal Match", "rank": 1, "category": "Puzzle", "store_url": "https://apple.com/rm"},
            {"app_name": "Gardenscapes", "rank": 2, "category": "Match-3", "store_url": "https://apple.com/gs"},
        ]
        adapter = AppleChartsAdapter(
            source_id="src_apple_001",
            is_authorized=True,
            tos_accepted=True,
            offline_fixture=fixture,
        )
        snapshot = adapter.fetch(query={"region": "us", "chart_type": "free_games"})
        self.assertEqual(snapshot.source_id, "src_apple_001")
        self.assertEqual(snapshot.region.upper(), "US")
        self.assertEqual(len(snapshot.records), 2)
        self.assertTrue(len(snapshot.raw_hash) > 0)
        self.assertEqual(snapshot.collection_method, CollectionMethod.OFFICIAL_FEED)

    def test_csv_import_adapter_valid_and_aliases(self):
        csv_content = """game_id,game_name,date,evidence_url,genre,rank
g_101,Block Blast,2026-10-25,https://ads.com/1,Puzzle,1
g_102,Monopoly GO,2026-10-25,https://ads.com/2,Board,2
"""
        adapter = CsvImportAdapter(source_id="src_csv_001")
        snapshot = adapter.parse_csv_content(csv_content)
        self.assertEqual(snapshot.source_id, "src_csv_001")
        self.assertEqual(len(snapshot.records), 2)
        self.assertEqual(snapshot.records[0]["app_name"], "Block Blast")
        self.assertEqual(snapshot.records[1]["rank"], 2)

    def test_csv_import_missing_mandatory_column(self):
        bad_csv = "game_id,genre\ng_1,Puzzle"
        adapter = CsvImportAdapter(source_id="src_csv_002")
        with self.assertRaises(CsvImportValidationError):
            adapter.parse_csv_content(bad_csv)


class TestGenreClassifier(unittest.TestCase):

    def setUp(self):
        self.classifier = GenreClassifier()

    def test_classify_match3(self):
        title = "Royal Match"
        desc = "Swap and match tiles to solve puzzles and rescue the king in castle rooms."
        res = self.classifier.classify_text(title + " " + desc)
        self.assertEqual(res.primary_genre, "Match-3")
        self.assertIn("grid_matching", res.mechanic_patterns)
        self.assertGreater(res.confidence, 0.5)

    def test_classify_merge(self):
        title = "Merge Mansion"
        desc = "Merge items on the board to discover keys and clean up grandmother's mystery estate."
        res = self.classifier.classify_text(title + " " + desc)
        self.assertEqual(res.primary_genre, "Merge")
        self.assertIn("merge_2", res.mechanic_patterns)

    def test_classify_sorting(self):
        title = "Goods Sort 3D"
        desc = "Organize, sort and match groceries on shelf triple goods puzzle."
        res = self.classifier.classify_text(title + " " + desc)
        self.assertEqual(res.primary_genre, "Sorting")
        self.assertIn("color_sorting", res.mechanic_patterns)

    def test_human_override(self):
        title = "Mystic Fusion"
        desc = "Action packed adventure with puzzle mechanics."
        res = self.classifier.classify_text(
            title + " " + desc,
            human_override={"primary_genre": "Match-3"},
        )
        self.assertEqual(res.primary_genre, "Match-3")
        self.assertEqual(res.confidence, 1.0)
        self.assertTrue(res.is_human_corrected)


class TestEvidenceAndIngestion(unittest.TestCase):

    def test_sha256_deduplication(self):
        service = TrendIngestionService()
        unique_id = str(uuid.uuid4())
        records = [{"app_name": f"Royal Match {unique_id}", "chart_rank": 1}]
        snapshot = RawSnapshot(
            source_id="src_unique_test",
            records=records,
            collection_method=CollectionMethod.CSV_UPLOAD,
        )

        snap1, is_duplicate1 = service.ingest_snapshot(snapshot)
        self.assertFalse(is_duplicate1)
        self.assertIsNotNone(snap1)

        snap2, is_duplicate2 = service.ingest_snapshot(snapshot)
        self.assertTrue(is_duplicate2)
        self.assertEqual(snap1.raw_hash, snap2.raw_hash)

    def test_recency_decay(self):
        resolver = EvidenceResolver(half_life_days=7.0)
        curr_time = datetime(2026, 10, 17, 12, 0, tzinfo=timezone.utc)
        obs_time_iso = "2026-10-10T12:00:00Z"
        decay = resolver.calculate_recency_weight(obs_time_iso, reference_date=curr_time)
        self.assertAlmostEqual(decay, 0.5, places=2)

    def test_generate_trend_report_with_provenance(self):
        service = TrendIngestionService()
        records = [
            {
                "app_name": "Royal Match",
                "category": "Match-3",
                "rank": 1,
                "region": "US",
                "evidence_url": "https://apple.com/us/apps/royal-match",
                "hook_text": "Rescue King Robert by matching colorful items",
            },
            {
                "app_name": "Candy Crush",
                "category": "Match-3",
                "rank": 2,
                "region": "US",
                "evidence_url": "https://apple.com/us/apps/candy-crush",
                "hook_text": "Sweet match 3 candies puzzle",
            },
        ]
        snapshot = RawSnapshot(
            source_id="src_apple",
            records=records,
            region="US",
            collection_method=CollectionMethod.OFFICIAL_FEED,
        )
        service.ingest_snapshot(snapshot)

        report = service.generate_trend_report(
            project_id="proj_royal",
            snapshot_ids=[snapshot.snapshot_id],
        )

        self.assertEqual(report.project_id, "proj_royal")
        self.assertGreater(len(report.signals), 0)
        for sig in report.signals:
            self.assertGreater(len(sig.evidence_refs), 0)
            self.assertIn(sig.confidence, [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH])
