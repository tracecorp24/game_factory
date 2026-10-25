"""
Source Adapters for Trend Intelligence.
"""

try:
    from .base import SourceAdapter, ToSPermissionError
    from .apple_charts import AppleChartsAdapter
    from .csv_import import CsvImportAdapter, CsvImportValidationError
except (ImportError, ValueError):
    from adapters.base import SourceAdapter, ToSPermissionError
    from adapters.apple_charts import AppleChartsAdapter
    from adapters.csv_import import CsvImportAdapter, CsvImportValidationError

__all__ = [
    "SourceAdapter",
    "ToSPermissionError",
    "AppleChartsAdapter",
    "CsvImportAdapter",
    "CsvImportValidationError",
]
