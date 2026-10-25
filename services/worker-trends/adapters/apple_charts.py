"""
Apple Charts Source Adapter.
Fetches and parses public top chart feeds from Apple App Store official RSS / Store API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import urllib.request
import json
from datetime import datetime, timezone

from .base import SourceAdapter, ToSPermissionError
try:
    from ..models import CollectionMethod, RawSnapshot, SourceStatus
except (ImportError, ValueError):
    from models import CollectionMethod, RawSnapshot, SourceStatus

logger = logging.getLogger(__name__)


class AppleChartsAdapter(SourceAdapter):
    """
    Adapter for Apple App Store Top Games charts.
    Uses official public Apple RSS marketing tools feeds or manual snapshot fallback.
    """

    def __init__(
        self,
        source_id: str = "apple_app_store_charts",
        region: str = "us",
        chart_type: str = "top-free",
        limit: int = 50,
        is_authorized: bool = True,
        tos_accepted: bool = True,
        offline_fixture: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            source_id=source_id,
            name="Apple App Store Top Charts",
            collection_method=CollectionMethod.OFFICIAL_FEED,
            is_authorized=is_authorized,
            tos_accepted=tos_accepted,
        )
        self.region = region.lower()
        self.chart_type = chart_type
        self.limit = limit
        self.offline_fixture = offline_fixture

    def _build_feed_url(self) -> str:
        return f"https://rss.applemarketingtools.com/api/v2/{self.region}/apps/{self.chart_type}/{self.limit}/apps.json"

    def fetch(self, query: Optional[Dict[str, Any]] = None) -> RawSnapshot:
        self.check_authorization()

        records: List[Dict[str, Any]] = []
        observed_at = datetime.now(timezone.utc).isoformat()
        feed_url = self._build_feed_url()

        # If offline fixture provided (e.g. for deterministic testing or offline mode)
        if self.offline_fixture is not None:
            records = self.offline_fixture
        else:
            try:
                req = urllib.request.Request(
                    feed_url,
                    headers={"User-Agent": "CreativeForge-Intelligence/3.0 (Game Studio QA)"},
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    data = json.loads(response.read().decode("utf-8"))
                    entries = data.get("feed", {}).get("results", [])
                    for rank, entry in enumerate(entries, start=1):
                        genre_names = [g.get("name", "") for g in entry.get("genres", [])]
                        records.append({
                            "app_name": entry.get("name"),
                            "bundle_id": entry.get("id"),
                            "developer": entry.get("artistName"),
                            "rank": rank,
                            "category": genre_names[0] if genre_names else "Games",
                            "all_genres": genre_names,
                            "icon_url": entry.get("artworkUrl100"),
                            "store_url": entry.get("url"),
                            "release_date": entry.get("releaseDate"),
                            "observed_at": observed_at,
                        })
            except Exception as exc:
                logger.warning(
                    "Network error fetching Apple Charts (%s). Degrading to manual_import_required.",
                    exc,
                )
                self._status = SourceStatus.MANUAL_IMPORT_REQUIRED
                raise ToSPermissionError(
                    f"Failed to fetch Apple Charts from {feed_url}: {exc}. "
                    f"Source status degraded to 'manual_import_required'."
                ) from exc

        return RawSnapshot(
            source_id=self.source_id,
            collection_method=self.collection_method,
            region=self.region.upper(),
            platform="iOS",
            created_at=observed_at,
            records=records,
            metadata={
                "feed_url": feed_url,
                "chart_type": self.chart_type,
                "limit": self.limit,
            },
        )
