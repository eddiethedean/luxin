"""
Manual source-mapping helpers for drill-down tables (no UI).
"""

import pandas as pd
from typing import List, Dict, Any

from luxin_core.validation import (
    ValidationError,
    validate_dataframe,
    validate_groupby_cols,
)
from luxin_core.utils import DetailIndexLabel, finalize_source_mapping, SourceMapping


def build_manual_source_mapping(
    agg_df: pd.DataFrame, detail_df: pd.DataFrame, groupby_cols: List[str]
) -> SourceMapping:
    """
    Build a mapping from aggregated row keys to detail row index labels.

    Args:
        agg_df: The aggregated DataFrame
        detail_df: The detail DataFrame
        groupby_cols: Column names matching ``agg_df`` index levels (one name when the index is flat)

    Returns:
        Mapping suitable for ``detail_df.loc[labels]`` per aggregated row key.
    """
    source_mapping: Dict[Any, List[DetailIndexLabel]] = {}

    # Handle single vs multi-index
    if isinstance(agg_df.index, pd.MultiIndex):
        # Multi-index case
        for idx in agg_df.index:
            # idx is already a tuple
            group_key = idx

            # Build filter condition
            mask = pd.Series([True] * len(detail_df))
            for col, val in zip(groupby_cols, group_key):
                mask &= detail_df[col] == val

            # Get matching indices
            matching_indices = detail_df[mask].index.tolist()
            source_mapping[group_key] = matching_indices
    else:
        # Single column groupby
        for idx in agg_df.index:
            group_key = (idx,)

            # Build filter condition
            mask = detail_df[groupby_cols[0]] == idx

            # Get matching indices
            matching_indices = detail_df[mask].index.tolist()
            source_mapping[group_key] = matching_indices

    return finalize_source_mapping(source_mapping)


# Backward-compatible alias (tests / internal)
_build_source_mapping = build_manual_source_mapping


def validate_manual_drill_inputs(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    groupby_cols: List[str],
) -> None:
    """Validate inputs for a manual drill-down table."""
    try:
        validate_dataframe(agg_df, "agg_df")
        validate_dataframe(detail_df, "detail_df")
        validate_groupby_cols(groupby_cols, detail_df)
    except ValidationError as e:
        raise ValueError(str(e)) from e

    if isinstance(agg_df.index, pd.MultiIndex):
        expected = agg_df.index.nlevels
        if len(groupby_cols) != expected:
            raise ValueError(
                f"groupby_cols length ({len(groupby_cols)}) must match "
                f"agg_df.index.nlevels ({expected}) when agg_df has a MultiIndex."
            )
    elif len(groupby_cols) != 1:
        raise ValueError(
            "When agg_df has a flat (non-MultiIndex), groupby_cols must contain "
            f"exactly one detail column name; got {len(groupby_cols)}."
        )
