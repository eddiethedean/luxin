"""
Manual API for creating drill-down tables from existing DataFrames (Streamlit / Jupyter routing).
"""

from __future__ import annotations

import warnings
from typing import Any, List

import pandas as pd

from luxin.display import display_drill_table
from luxin_core.drill_table import build_manual_source_mapping, validate_manual_drill_inputs
from luxin_core.utils import SourceMapping


def create_drill_table(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    groupby_cols: List[str],
    **kwargs: Any,
) -> None:
    """
    Create an interactive drill-down table from aggregated and detail DataFrames.

    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        groupby_cols: Column names aligned with ``agg_df`` index (one column when the index is flat)
        **kwargs: Additional options for display customization

    Raises:
        ValueError: If inputs are invalid

    Example:
        >>> import pandas as pd
        >>> from luxin import create_drill_table
        >>>
        >>> df = pd.DataFrame({
        ...     'category': ['A', 'A', 'B', 'B'],
        ...     'sales': [100, 200, 150, 250]
        ... })
        >>> agg_df = df.groupby('category').sum()
        >>> create_drill_table(agg_df, df, groupby_cols=['category'])
    """
    validate_manual_drill_inputs(agg_df, detail_df, groupby_cols)
    source_mapping: SourceMapping = build_manual_source_mapping(
        agg_df, detail_df, groupby_cols
    )
    display_drill_table(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


def _build_source_mapping(
    agg_df: pd.DataFrame, detail_df: pd.DataFrame, groupby_cols: List[str]
) -> SourceMapping:
    """Deprecated alias for :func:`build_manual_source_mapping`."""
    warnings.warn(
        "_build_source_mapping is deprecated; use build_manual_source_mapping.",
        DeprecationWarning,
        stacklevel=2,
    )
    return build_manual_source_mapping(agg_df, detail_df, groupby_cols)


__all__ = ["create_drill_table", "build_manual_source_mapping"]
