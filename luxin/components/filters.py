"""
Filtering component for aggregated data tables.
"""

import math
from typing import Any, List

import pandas as pd
import pandas.api.types as pdt
import streamlit as st


def _sorted_unique_for_multiselect(series: pd.Series) -> List[Any]:
    """Lexicographically sort unique values without cross-type comparisons (Python 3 safe)."""
    vals = series.dropna().unique().tolist()
    return sorted(vals, key=lambda x: (type(x).__name__, str(x)))


def _column_uses_numeric_range_filter(series: pd.Series) -> bool:
    """Numeric columns use a range slider; other dtypes use categorical multiselect."""
    return pdt.is_numeric_dtype(series.dtype)


def render_filters(df: pd.DataFrame, key_prefix: str = "luxin_filter") -> pd.DataFrame:
    """
    Render filter controls and return filtered DataFrame.

    Args:
        df: The DataFrame to filter
        key_prefix: Prefix for Streamlit widget keys

    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()

    # Text search filter
    search_text = st.text_input(
        "🔍 Search",
        value="",
        key=f"{key_prefix}_search",
        placeholder="Search in all columns...",
    )

    if search_text:
        # Align mask to df.index so text search works with non-RangeIndex frames
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask |= (
                df[col]
                .astype(str)
                .str.contains(search_text, case=False, na=False, regex=False)
            )
        filtered_df = filtered_df[mask]

    # Column-specific filters
    with st.expander("🔧 Column Filters", expanded=False):
        for col in df.columns:
            if not _column_uses_numeric_range_filter(df[col]):
                unique_vals = _sorted_unique_for_multiselect(df[col])
                if (
                    len(unique_vals) > 0 and len(unique_vals) <= 50
                ):  # Limit to reasonable number
                    selected = st.multiselect(
                        f"Filter {col}",
                        options=unique_vals,
                        default=[],
                        key=f"{key_prefix}_col_{col}",
                    )
                    if selected:
                        filtered_df = filtered_df[filtered_df[col].isin(selected)]
            else:
                # Numeric column - use range slider
                col_min = float(df[col].min())
                col_max = float(df[col].max())
                if (
                    col_min < col_max
                    and math.isfinite(col_min)
                    and math.isfinite(col_max)
                ):
                    range_vals = st.slider(
                        f"Filter {col}",
                        min_value=col_min,
                        max_value=col_max,
                        value=(col_min, col_max),
                        key=f"{key_prefix}_col_{col}",
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= range_vals[0])
                        & (filtered_df[col] <= range_vals[1])
                    ]

    # Show filter results count
    if len(filtered_df) != len(df):
        st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")

    return filtered_df
