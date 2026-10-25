"""
Unit tests for IntelligenceService.
"""

import unittest
from services.api.app.modules.intelligence.service import IntelligenceService
from worker_trends.adapters.apple_charts import AppleChartsAdapter


class TestIntelligenceService(unittest.TestCase):

    def setUp(self):
        self.service = IntelligenceService()

    def test_default_sources_and_tos(self):
        sources = self.service.list_sources()
        source_ids = [s["source_id"] for s in sources]
        self.assertIn("apple_app_store_charts", source_ids)
        self.assertIn("csv_user_import", source_ids)

        # Update ToS
        updated = self.service.update_source_tos("apple_app_store_charts", tos_accepted=False, is_authorized=True)
        self.assertEqual(updated["status"], "requires_auth")

        updated2 = self.service.update_source_tos("apple_app_store_charts", tos_accepted=True, is_authorized=True)
        self.assertEqual(updated2["status"], "active")

    def test_sync_with_adapter_and_deduplication(self):
        fixture = [
            {"app_name": "Royal Match", "rank": 1, "category": "Puzzle", "store_url": "https://apple.com/rm"},
            {"app_name": "Gardenscapes", "rank": 2, "category": "Match-3", "store_url": "https://apple.com/gs"},
        ]
        adapter = AppleChartsAdapter(offline_fixture=fixture)
        res1 = self.service.trigger_sync("apple_app_store_charts", adapter_override=adapter)
        self.assertEqual(res1["status"], "completed")
        self.assertEqual(res1["records_ingested"], 2)
        self.assertFalse(res1["was_deduplicated"])

        # Sync identical data again -> should deduplicate
        res2 = self.service.trigger_sync("apple_app_store_charts", adapter_override=adapter)
        self.assertEqual(res2["status"], "completed")
        self.assertTrue(res2["was_deduplicated"])

    def test_diff_snapshots(self):
        csv_day1 = """game_name,date,preview_url,chart_rank
App Alpha,2026-10-20,https://ads.com/1,1
App Beta,2026-10-20,https://ads.com/2,2
"""
        csv_day2 = """game_name,date,preview_url,chart_rank
App Beta,2026-10-21,https://ads.com/2,1
App Gamma,2026-10-21,https://ads.com/3,2
"""
        snap1 = self.service.import_csv(csv_day1)
        snap2 = self.service.import_csv(csv_day2)

        diff = self.service.diff_snapshots(snap1["snapshot_id"], snap2["snapshot_id"])
        self.assertIn("App Gamma", diff["new_entries"])
        self.assertIn("App Alpha", diff["dropped_entries"])
        self.assertIn("App Beta", diff["rank_shifts"])
        self.assertEqual(diff["rank_shifts"]["App Beta"]["rank_delta"], 1)  # 2 -> 1, delta = +1


if __name__ == "__main__":
    unittest.main()
