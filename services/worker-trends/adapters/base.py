"""
Base Source Adapter Interface and ToS Compliance Gate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
try:
    from ..models import CollectionMethod, RawSnapshot, SourceStatus
except (ImportError, ValueError):
    from models import CollectionMethod, RawSnapshot, SourceStatus


class ToSPermissionError(Exception):
    """Raised when source collection violates Terms of Service or lacks authorization."""
    pass


class SourceAdapter(ABC):
    """
    Abstract base class for all Trend and Market Intelligence connectors.
    Enforces strict ToS compliance: unauthorized scraping is prohibited.
    If access credentials or explicit permission are absent, gracefully degrades
    to `manual_import_required` mode without fabricating data.
    """

    def __init__(
        self,
        source_id: str,
        name: str,
        collection_method: CollectionMethod,
        is_authorized: bool = True,
        tos_accepted: bool = True,
    ):
        self.source_id = source_id
        self.name = name
        self.collection_method = collection_method
        self.is_authorized = is_authorized
        self.tos_accepted = tos_accepted
        self._status = SourceStatus.ACTIVE if (is_authorized and tos_accepted) else SourceStatus.MANUAL_IMPORT_REQUIRED

    @property
    def status(self) -> SourceStatus:
        if not self.tos_accepted:
            return SourceStatus.REQUIRES_AUTH
        if not self.is_authorized:
            return SourceStatus.MANUAL_IMPORT_REQUIRED
        return self._status

    def check_authorization(self) -> None:
        """Verify that adapter is authorized to collect data."""
        if not self.tos_accepted:
            raise ToSPermissionError(
                f"Source '{self.source_id}' Terms of Service have not been explicitly accepted."
            )
        if not self.is_authorized:
            raise ToSPermissionError(
                f"Source '{self.source_id}' is not authorized for automated scraping/fetching. "
                f"Please switch to manual import mode."
            )

    @abstractmethod
    def fetch(self, query: Optional[Dict[str, Any]] = None) -> RawSnapshot:
        """Fetch raw data and return an immutable RawSnapshot."""
        pass
