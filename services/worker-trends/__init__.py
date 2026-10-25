"""
CreativeForge Intelligence Studio v3.0 - Worker Trends Package.
"""

try:
    from .models import (
        CollectionMethod,
        ConfidenceLevel,
        EvidenceRef,
        RawSnapshot,
        SourceStatus,
        TrendObservation,
        TrendReport,
        TrendSignal,
    )
    from .adapters import (
        AppleChartsAdapter,
        CsvImportAdapter,
        CsvImportValidationError,
        SourceAdapter,
        ToSPermissionError,
    )
    from .genre_classifier import ClassificationResult, GenreClassifier
    from .evidence_resolver import EvidenceResolver
    from .ingestion import TrendIngestionService
except (ImportError, ValueError):
    import sys, os
    cur_dir = os.path.dirname(__file__)
    if cur_dir not in sys.path:
        sys.path.insert(0, cur_dir)
    from models import (
        CollectionMethod,
        ConfidenceLevel,
        EvidenceRef,
        RawSnapshot,
        SourceStatus,
        TrendObservation,
        TrendReport,
        TrendSignal,
    )
    from adapters import (
        AppleChartsAdapter,
        CsvImportAdapter,
        CsvImportValidationError,
        SourceAdapter,
        ToSPermissionError,
    )
    from genre_classifier import ClassificationResult, GenreClassifier
    from evidence_resolver import EvidenceResolver
    from ingestion import TrendIngestionService

__all__ = [
    "CollectionMethod",
    "ConfidenceLevel",
    "EvidenceRef",
    "RawSnapshot",
    "SourceStatus",
    "TrendObservation",
    "TrendReport",
    "TrendSignal",
    "SourceAdapter",
    "ToSPermissionError",
    "AppleChartsAdapter",
    "CsvImportAdapter",
    "CsvImportValidationError",
    "ClassificationResult",
    "GenreClassifier",
    "EvidenceResolver",
    "TrendIngestionService",
]
