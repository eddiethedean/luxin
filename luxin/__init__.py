"""
Luxin - Streamlit-first interactive data exploration with drill-down capabilities.
"""

from luxin.inspector import Inspector
from luxin.tracked_df import TrackedDataFrame
from luxin.drill_table import create_drill_table
from luxin.polars_support import create_tracked_from_polars, convert_polars_to_pandas, is_polars_dataframe
import warnings

__version__ = "0.2.0"
__all__ = [
    "Inspector", 
    "TrackedDataFrame", 
    "create_drill_table",
    "create_tracked_from_polars",
    "convert_polars_to_pandas",
    "is_polars_dataframe"
]


def __getattr__(name):
    """Handle deprecated imports with warnings."""
    if name == "show_drill_table":
        warnings.warn(
            "show_drill_table is deprecated. Use Inspector(df).render() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Return a function that can be called on TrackedDataFrame instances
        # This is for backward compatibility - the actual method is on TrackedDataFrame
        def _show_drill_table_wrapper(df):
            """Wrapper for backward compatibility."""
            if hasattr(df, 'show_drill_table'):
                return df.show_drill_table()
            raise AttributeError("show_drill_table can only be called on TrackedDataFrame instances")
        return _show_drill_table_wrapper
    raise AttributeError(f"module 'luxin' has no attribute '{name}'")

