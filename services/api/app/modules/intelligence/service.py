"""
Intelligence Module Application Service.
Provides REST and workflow interfaces for trend sources, sync jobs, snapshots, and reports.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

import sys
import os

# Ensure worker-trends can be imported as worker_trends
worker_trends_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../worker-trends"))
if worker_trends_path not in sys.path:
    sys.path.insert(0, worker_trends_path)

import importlib.util
if "worker_trends" not in sys.modules:
    spec = importlib.util.spec_from_file_location("worker_trends", os.path.join(worker_trends_path, "__init__.py"))
    if spec and spec.loader:
        mod = importlib.util.module_from_spec(spec)
        sys.modules["worker_trends"] = mod
        spec.loader.exec_module(mod)

from worker_trends.adapters.base import SourceAdapter, ToSPermissionError
from worker_trends.adapters.apple_charts import AppleChartsAdapter
from worker_trends.adapters.csv_import import CsvImportAdapter
from worker_trends.ingestion import TrendIngestionService
from worker_trends.models import (
    CollectionMethod,
    RawSnapshot,
    SourceStatus,
    TrendReport,
)


class IntelligenceService:
    """
    Application service managing trend sources, synchronization pipelines,
    snapshot storage, and market intelligence generation.
    """

    def __init__(self, ingestion_service: Optional[TrendIngestionService] = None):
        self.ingestion = ingestion_service or TrendIngestionService()
        self._sources: Dict[str, Dict[str, Any]] = {}
        self._sync_jobs: List[Dict[str, Any]] = []
        self._reports: Dict[str, TrendReport] = {}
        self._init_default_sources()

    def _init_default_sources(self) -> None:
        """Register default official and manual sources."""
        self.register_source(
            source_id="apple_app_store_charts",
            name="Apple App Store Official Top Charts",
            collection_method=CollectionMethod.OFFICIAL_FEED,
            is_authorized=True,
            tos_accepted=True,
            description="Official public RSS feed of top free and grossing iPhone games.",
        )
        self.register_source(
            source_id="csv_user_import",
            name="Manual / Competitor CSV Ingestion",
            collection_method=CollectionMethod.CSV_UPLOAD,
            is_authorized=True,
            tos_accepted=True,
            description="User-uploaded competitor creative tracking and performance CSV.",
        )

    def register_source(
        self,
        source_id: str,
        name: str,
        collection_method: CollectionMethod,
        is_authorized: bool = True,
        tos_accepted: bool = True,
        description: str = "",
    ) -> Dict[str, Any]:
        source = {
            "source_id": source_id,
            "name": name,
            "collection_method": collection_method.value if hasattr(collection_method, "value") else str(collection_method),
            "is_authorized": is_authorized,
            "tos_accepted": tos_accepted,
            "status": SourceStatus.ACTIVE.value if (is_authorized and tos_accepted) else SourceStatus.MANUAL_IMPORT_REQUIRED.value,
            "description": description,
            "registered_at": datetime.now(timezone.utc).isoformat(),
        }
        self._sources[source_id] = source
        return source

    def list_sources(self) -> List[Dict[str, Any]]:
        return list(self._sources.values())

    def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        return self._sources.get(source_id)

    def update_source_tos(self, source_id: str, tos_accepted: bool, is_authorized: bool) -> Dict[str, Any]:
        if source_id not in self._sources:
            raise KeyError(f"Source '{source_id}' not found.")
        self._sources[source_id]["tos_accepted"] = tos_accepted
        self._sources[source_id]["is_authorized"] = is_authorized
        if not tos_accepted:
            new_status = SourceStatus.REQUIRES_AUTH.value
        elif not is_authorized:
            new_status = SourceStatus.MANUAL_IMPORT_REQUIRED.value
        else:
            new_status = SourceStatus.ACTIVE.value
        self._sources[source_id]["status"] = new_status
        return self._sources[source_id]

    def trigger_sync(
        self,
        source_id: str,
        adapter_override: Optional[SourceAdapter] = None,
        query_params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Trigger an immediate ingestion sync for a registered source."""
        source_meta = self._sources.get(source_id)
        if not source_meta:
            raise KeyError(f"Unknown source '{source_id}'")

        job_id = str(uuid4())
        job_record = {
            "job_id": job_id,
            "source_id": source_id,
            "status": "running",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "snapshot_id": None,
            "records_ingested": 0,
            "error": None,
        }
        self._sync_jobs.append(job_record)

        try:
            adapter: SourceAdapter
            if adapter_override:
                adapter = adapter_override
            elif source_id == "apple_app_store_charts":
                adapter = AppleChartsAdapter(
                    source_id=source_id,
                    is_authorized=source_meta["is_authorized"],
                    tos_accepted=source_meta["tos_accepted"],
                )
            elif source_id == "csv_user_import":
                adapter = CsvImportAdapter(
                    source_id=source_id,
                    is_authorized=source_meta["is_authorized"],
                    tos_accepted=source_meta["tos_accepted"],
                )
            else:
                raise ValueError(f"No built-in adapter configured for '{source_id}'")

            snapshot = adapter.fetch(query_params)
            stored_snapshot, is_duplicate = self.ingestion.ingest_snapshot(snapshot)

            job_record["status"] = "completed"
            job_record["snapshot_id"] = stored_snapshot.snapshot_id
            job_record["records_ingested"] = stored_snapshot.record_count
            job_record["was_deduplicated"] = is_duplicate
            job_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            return job_record

        except Exception as exc:
            job_record["status"] = "failed"
            job_record["error"] = str(exc)
            job_record["completed_at"] = datetime.now(timezone.utc).isoformat()
            raise

    def import_csv(
        self,
        csv_content: str,
        source_id: str = "csv_user_import",
        region: str = "US",
        platform: str = "Cross-Platform",
    ) -> Dict[str, Any]:
        """Import user CSV trend data."""
        adapter = CsvImportAdapter(source_id=source_id)
        snapshot = adapter.parse_csv_content(csv_content, region=region, platform=platform)
        stored_snapshot, is_duplicate = self.ingestion.ingest_snapshot(snapshot)
        return {
            "snapshot_id": stored_snapshot.snapshot_id,
            "record_count": stored_snapshot.record_count,
            "raw_hash": stored_snapshot.raw_hash,
            "was_deduplicated": is_duplicate,
        }

    def generate_report(
        self,
        project_id: Optional[str] = None,
        snapshot_ids: Optional[List[str]] = None,
    ) -> TrendReport:
        """Generate and cache a trend intelligence report."""
        report = self.ingestion.generate_trend_report(
            snapshot_ids=snapshot_ids,
            project_id=project_id,
        )
        self._reports[report.report_id] = report
        return report

    def get_report(self, report_id: str) -> Optional[TrendReport]:
        return self._reports.get(report_id)

    def diff_snapshots(self, snapshot_id_a: str, snapshot_id_b: str) -> Dict[str, Any]:
        """Compute differences between two trend snapshots (rank shifts, new entries)."""
        snap_a = self.ingestion._snapshots.get(snapshot_id_a)
        snap_b = self.ingestion._snapshots.get(snapshot_id_b)

        if not snap_a or not snap_b:
            raise KeyError("One or both snapshots not found for comparison.")

        apps_a = {rec.get("app_name"): rec.get("rank") for rec in snap_a.records if rec.get("app_name")}
        apps_b = {rec.get("app_name"): rec.get("rank") for rec in snap_b.records if rec.get("app_name")}

        new_entries = [name for name in apps_b if name not in apps_a]
        dropped_entries = [name for name in apps_a if name not in apps_b]

        rank_shifts = {}
        for name, rank_b in apps_b.items():
            if name in apps_a and rank_b is not None and apps_a[name] is not None:
                rank_a = apps_a[name]
                shift = rank_a - rank_b  # positive means improved rank
                if shift != 0:
                    rank_shifts[name] = {"previous_rank": rank_a, "current_rank": rank_b, "rank_delta": shift}

        return {
            "snapshot_a": snapshot_id_a,
            "snapshot_b": snapshot_id_b,
            "new_entries": new_entries,
            "dropped_entries": dropped_entries,
            "rank_shifts": rank_shifts,
            "count_a": snap_a.record_count,
            "count_b": snap_b.record_count,
        }
