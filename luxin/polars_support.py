"""
Polars DataFrame support for luxin.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import pandas as pd

if TYPE_CHECKING:
    from luxin.tracked_df import TrackedDataFrame

try:
    import polars as _pl

    pl_runtime: Any = _pl
except ImportError:
    pl_runtime = None

POLARS_AVAILABLE = pl_runtime is not None


def convert_polars_to_pandas(df: Union[pd.DataFrame, Any]) -> pd.DataFrame:
    """
    Convert Polars DataFrame to pandas DataFrame.

    Args:
        df: Polars or pandas DataFrame

    Returns:
        pandas DataFrame
    """
    if isinstance(df, pd.DataFrame):
        return df

    if not POLARS_AVAILABLE:
        raise ImportError("Polars is not installed. Install with: pip install polars")

    assert pl_runtime is not None
    if isinstance(df, pl_runtime.DataFrame):  # type: ignore[attr-defined]
        return df.to_pandas()

    raise TypeError(f"Expected Polars or pandas DataFrame, got {type(df)}")


def create_tracked_from_polars(df: Any) -> "TrackedDataFrame":
    """
    Create a TrackedDataFrame from a Polars DataFrame.

    Args:
        df: Polars DataFrame

    Returns:
        TrackedDataFrame (pandas-based)
    """
    from luxin.tracked_df import TrackedDataFrame

    if not POLARS_AVAILABLE:
        raise ImportError("Polars is not installed. Install with: pip install polars")

    pandas_df = df.to_pandas()
    return TrackedDataFrame(pandas_df)


def is_polars_dataframe(df: Any) -> bool:
    """
    Check if object is a Polars DataFrame.

    Args:
        df: Object to check

    Returns:
        True if Polars DataFrame, False otherwise
    """
    if not POLARS_AVAILABLE:
        return False

    assert pl_runtime is not None
    return isinstance(df, pl_runtime.DataFrame)  # type: ignore[arg-type]


def handle_polars_in_inspector(df: Union[pd.DataFrame, Any]) -> pd.DataFrame:
    """
    Handle Polars DataFrame in Inspector by converting to pandas.

    Args:
        df: Polars or pandas DataFrame

    Returns:
        pandas DataFrame
    """
    if is_polars_dataframe(df):
        return convert_polars_to_pandas(df)
    return df
