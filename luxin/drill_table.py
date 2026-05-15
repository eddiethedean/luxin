"""
Manual API for creating drill-down tables from existing DataFrames (Streamlit / Jupyter routing).
"""

from typing import Any, Dict, List

import pandas as pd

from luxin.display import display_drill_table
from luxin_core.drill_table import (
    _build_source_mapping,
    build_manual_source_mapping,
    validate_manual_drill_inputs,
)


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
        groupby_cols: List of column names used to group the data
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
    source_mapping: Dict[Any, List[int]] = build_manual_source_mapping(
        agg_df, detail_df, groupby_cols
    )
    display_drill_table(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


__all__ = ["create_drill_table", "_build_source_mapping", "build_manual_source_mapping"]
