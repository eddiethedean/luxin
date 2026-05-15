"""
luxin-core — tracked aggregations, drill hierarchy helpers, and shared dataframe utilities.
"""

from luxin_core.drill_hierarchy import DrillHierarchySpec
from luxin_core.drill_table import build_manual_source_mapping
from luxin_core.polars_support import (
    convert_polars_to_pandas,
    create_tracked_from_polars,
    handle_polars_in_inspector,
    is_polars_dataframe,
)
from luxin_core.tracked_df import TrackedDataFrame

__version__ = "0.4.0"
__all__ = [
    "DrillHierarchySpec",
    "TrackedDataFrame",
    "build_manual_source_mapping",
    "convert_polars_to_pandas",
    "create_tracked_from_polars",
    "handle_polars_in_inspector",
    "is_polars_dataframe",
]
