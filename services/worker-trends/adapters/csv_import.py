"""
CSV Import Adapter for User-Provided Trend & Competitor Ad Data.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .base import SourceAdapter
try:
    from ..models import CollectionMethod, RawSnapshot
except (ImportError, ValueError):
    from models import CollectionMethod, RawSnapshot


class CsvImportValidationError(Exception):
    """Raised when CSV trend data fails schema or integrity validation."""
    pass


class CsvImportAdapter(SourceAdapter):
    """
    Adapter for manually uploaded or pipeline-ingested CSV ad/trend datasets.
    Validates headers, data types, and required evidence provenance fields.
    """

    REQUIRED_FIELD_ALIASES = {
        "app_name": ["app_name", "game_name", "title", "advertiser_name"],
        "observed_at": ["observed_at", "date", "created_date", "timestamp"],
        "evidence_url": ["evidence_url", "ad_url", "preview_url", "source_url"],
    }

    OPTIONAL_FIELD_ALIASES = {
        "rank": ["rank", "position", "chart_rank"],
        "category": ["category", "genre", "primary_genre"],
        "hook_text": ["hook_text", "hook", "headline", "ad_copy", "opening_hook"],
        "creative_tags": ["creative_tags", "tags", "themes", "mechanic_tags"],
        "platform": ["platform", "os", "network"],
        "region": ["region", "country", "geo"],
    }

    def __init__(
        self,
        source_id: str = "csv_user_import",
        name: str = "Manual CSV Ingestion",
        is_authorized: bool = True,
        tos_accepted: bool = True,
    ):
        super().__init__(
            source_id=source_id,
            name=name,
            collection_method=CollectionMethod.CSV_UPLOAD,
            is_authorized=is_authorized,
            tos_accepted=tos_accepted,
        )

    def _resolve_column(self, headers: List[str], candidate_keys: List[str]) -> Optional[str]:
        lower_headers = {h.strip().lower(): h for h in headers}
        for candidate in candidate_keys:
            if candidate.lower() in lower_headers:
                return lower_headers[candidate.lower()]
        return None

    def parse_csv_content(
        self,
        content: str,
        region: str = "US",
        platform: str = "Cross-Platform",
    ) -> RawSnapshot:
        self.check_authorization()

        if not content or not content.strip():
            raise CsvImportValidationError("CSV content is empty.")

        # Detect dialect safely
        sample = content[:2048]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;")
        except Exception:
            dialect = csv.excel

        reader = csv.DictReader(io.StringIO(content), dialect=dialect)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise CsvImportValidationError("CSV file has no header row.")

        # Map required columns
        column_map: Dict[str, str] = {}
        for canonical, candidates in self.REQUIRED_FIELD_ALIASES.items():
            found = self._resolve_column(fieldnames, candidates)
            if not found:
                raise CsvImportValidationError(
                    f"CSV missing mandatory column for '{canonical}'. Expected one of: {candidates}"
                )
            column_map[canonical] = found

        # Map optional columns
        for canonical, candidates in self.OPTIONAL_FIELD_ALIASES.items():
            found = self._resolve_column(fieldnames, candidates)
            if found:
                column_map[canonical] = found

        records: List[Dict[str, Any]] = []
        observed_now = datetime.now(timezone.utc).isoformat()

        for row_idx, row in enumerate(reader, start=2):
            app_name = row.get(column_map["app_name"], "").strip()
            if not app_name:
                continue  # skip empty lines

            observed_at = row.get(column_map["observed_at"], "").strip() or observed_now
            evidence_url = row.get(column_map["evidence_url"], "").strip()

            rank_val = None
            if "rank" in column_map and row.get(column_map["rank"]):
                try:
                    rank_val = int(row[column_map["rank"]].strip())
                except ValueError:
                    rank_val = None

            tags_raw = row.get(column_map.get("creative_tags", ""), "")
            creative_tags = [t.strip() for t in tags_raw.split(";") if t.strip()] if tags_raw else []

            records.append({
                "app_name": app_name,
                "observed_at": observed_at,
                "evidence_url": evidence_url,
                "rank": rank_val,
                "category": row.get(column_map.get("category", ""), "Uncategorized").strip(),
                "hook_text": row.get(column_map.get("hook_text", ""), "").strip(),
                "creative_tags": creative_tags,
                "platform": row.get(column_map.get("platform", ""), platform).strip(),
                "region": row.get(column_map.get("region", ""), region).strip(),
                "source_row": row_idx,
            })

        if not records:
            raise CsvImportValidationError("CSV file contains no valid data rows.")

        return RawSnapshot(
            source_id=self.source_id,
            collection_method=self.collection_method,
            region=region,
            platform=platform,
            records=records,
            metadata={"row_count": len(records), "dialect_delimiter": getattr(dialect, "delimiter", ",")},
        )

    def fetch(self, query: Optional[Dict[str, Any]] = None) -> RawSnapshot:
        if not query or "csv_content" not in query:
            raise CsvImportValidationError("CsvImportAdapter.fetch() requires query['csv_content'] parameter.")
        return self.parse_csv_content(
            content=query["csv_content"],
            region=query.get("region", "US"),
            platform=query.get("platform", "Cross-Platform"),
        )
