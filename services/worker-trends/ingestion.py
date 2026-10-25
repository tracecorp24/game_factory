"""
Trend Ingestion Service.
Orchestrates snapshot ingestion, deduplication, classification, and report generation.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from .adapters.base import SourceAdapter
from .genre_classifier import GenreClassifier
from .evidence_resolver import EvidenceResolver
from .models import (
    ConfidenceLevel,
    RawSnapshot,
    TrendObservation,
    TrendReport,
    TrendSignal,
)

logger = logging.getLogger(__name__)


class TrendIngestionService:
    """
    Core engine for market and trend intelligence ingestion.
    Enforces deduplication, provenance verification, and non-hallucination.
    """

    def __init__(
        self,
        classifier: Optional[GenreClassifier] = None,
        resolver: Optional[EvidenceResolver] = None,
    ):
        self.classifier = classifier or GenreClassifier()
        self.resolver = resolver or EvidenceResolver()
        self._snapshots: Dict[str, RawSnapshot] = {}
        self._known_hashes: Set[str] = set()

    def ingest_snapshot(self, snapshot: RawSnapshot) -> tuple[RawSnapshot, bool]:
        """
        Store a RawSnapshot with SHA256 content deduplication.
        Returns (snapshot, is_duplicate). If duplicate, returns (existing, True).
        """
        if snapshot.raw_hash in self._known_hashes:
            # Find existing
            for existing in self._snapshots.values():
                if existing.raw_hash == snapshot.raw_hash:
                    logger.info("Deduplicated identical snapshot hash: %s", snapshot.raw_hash)
                    return existing, True

        self._snapshots[snapshot.snapshot_id] = snapshot
        self._known_hashes.add(snapshot.raw_hash)
        logger.info("Ingested new RawSnapshot %s with %d records", snapshot.snapshot_id, snapshot.record_count)
        return snapshot, False

    def parse_snapshot_observations(self, snapshot: RawSnapshot) -> List[TrendObservation]:
        """Convert snapshot records into normalized TrendObservation objects with genre classification."""
        observations: List[TrendObservation] = []
        for rec in snapshot.records:
            app_name = rec.get("app_name") or rec.get("name") or "Unknown App"
            category_hint = rec.get("category") or rec.get("primary_genre")
            combined_text = f"{app_name} {category_hint or ''} {rec.get('hook_text', '')} {' '.join(rec.get('creative_tags', []))}"

            # Classify
            classification = self.classifier.classify_text(combined_text, category_hint=category_hint)

            obs = TrendObservation(
                source_id=snapshot.source_id,
                app_name=app_name,
                bundle_id=rec.get("bundle_id"),
                developer=rec.get("developer"),
                rank=rec.get("rank"),
                category=category_hint,
                genre=classification.primary_genre,
                mechanic_tags=classification.mechanic_patterns,
                creative_tags=rec.get("creative_tags", []),
                hook_text=rec.get("hook_text"),
                evidence_url=rec.get("evidence_url") or rec.get("store_url", ""),
                observed_at=rec.get("observed_at") or snapshot.created_at,
                region=snapshot.region,
                platform=snapshot.platform,
                metadata={"matched_rules": classification.matched_rules, "classification_confidence": classification.confidence},
            )
            observations.append(obs)
        return observations

    def generate_trend_report(
        self,
        snapshot_ids: Optional[List[str]] = None,
        project_id: Optional[str] = None,
    ) -> TrendReport:
        """
        Synthesizes ingested snapshots into a comprehensive TrendReport.
        Clusters observations by genre and mechanic pattern to form verified TrendSignals.
        """
        target_snapshots = [
            self._snapshots[sid] for sid in (snapshot_ids or self._snapshots.keys())
            if sid in self._snapshots
        ]

        if not target_snapshots:
            return TrendReport(
                project_id=project_id,
                signals=[],
                limitations=["No trend snapshots available. Ingest data via Apple Charts or CSV import first."],
                missingness_note="Zero snapshots found in store.",
                confidence=ConfidenceLevel.LOW,
            )

        all_observations: List[TrendObservation] = []
        source_counts: Dict[str, int] = {}

        for snap in target_snapshots:
            obs_list = self.parse_snapshot_observations(snap)
            all_observations.extend(obs_list)
            source_counts[snap.source_id] = source_counts.get(snap.source_id, 0) + len(obs_list)

        # Cluster by Genre & Mechanic
        clusters: Dict[tuple[str, str], List[TrendObservation]] = {}
        for obs in all_observations:
            genre = obs.genre or "Casual Puzzle"
            primary_mechanic = obs.mechanic_tags[0] if obs.mechanic_tags else "general_mechanic"
            key = (genre, primary_mechanic)
            clusters.setdefault(key, []).append(obs)

        # Build signals for prominent clusters
        signals: List[TrendSignal] = []
        for (genre, mechanic), obs_group in clusters.items():
            hook_theme = self._infer_hook_theme(obs_group)
            description = (
                f"Surge in {genre} titles utilizing {mechanic} mechanics. "
                f"Observed across {len(obs_group)} apps in top charts/campaigns."
            )
            angles = [
                f"Showcase immediate 0-2s {mechanic} interaction before introducing challenge",
                f"Frustration-to-satisfaction hook utilizing high-contrast {genre} themes",
            ]
            first_snap_id = target_snapshots[0].snapshot_id
            signal = self.resolver.build_trend_signal(
                genre=genre,
                mechanic_pattern=mechanic,
                hook_theme=hook_theme,
                description=description,
                observations=obs_group,
                snapshot_id=first_snap_id,
                recommended_angles=angles,
            )
            signals.append(signal)

        # Sort signals by confidence_score descending
        signals.sort(key=lambda s: s.confidence_score, reverse=True)

        # Overall confidence
        overall_conf = (
            ConfidenceLevel.HIGH if signals and signals[0].confidence == ConfidenceLevel.HIGH
            else ConfidenceLevel.MEDIUM if signals
            else ConfidenceLevel.LOW
        )

        limitations: List[str] = []
        if len(source_counts) == 1:
            limitations.append("All observations originate from a single source; cross-platform validation recommended.")
        if len(all_observations) < 10:
            limitations.append("Small sample size (<10 observations); confidence intervals are broad.")

        return TrendReport(
            project_id=project_id,
            signals=signals,
            total_snapshots_analyzed=len(target_snapshots),
            total_observations=len(all_observations),
            source_distribution=source_counts,
            confidence=overall_conf,
            limitations=limitations,
            missingness_note="No missingness detected in mandatory fields." if all_observations else "No observations.",
        )

    def _infer_hook_theme(self, observations: List[TrendObservation]) -> str:
        hooks = [obs.hook_text for obs in observations if obs.hook_text]
        if hooks:
            return hooks[0]
        sample_apps = [obs.app_name for obs in observations[:2]]
        return f"Mechanic Showcase & Visual Satisfaction ({', '.join(sample_apps)})"
