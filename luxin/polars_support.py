"""Re-exports :mod:`luxin_core.polars_support` for the ``luxin`` distribution."""

from luxin_core.polars_support import (
    POLARS_AVAILABLE,
    convert_polars_to_pandas,
    create_tracked_from_polars,
    handle_polars_in_inspector,
    is_polars_dataframe,
)

__all__ = [
    "POLARS_AVAILABLE",
    "convert_polars_to_pandas",
    "create_tracked_from_polars",
    "handle_polars_in_inspector",
    "is_polars_dataframe",
]
