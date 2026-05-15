"""
Table view component for displaying aggregated data with drill-down.
"""

import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional
from luxin.components.detail_panel import render_detail_panel
from luxin.components.filters import render_filters
from luxin.components.export import render_export_buttons
from luxin.config import InspectorConfig, get_default_config


def _ensure_groupby_columns_in_frame(
    display_df: pd.DataFrame, groupby_cols: List[str]
) -> pd.DataFrame:
    """Reset index so group keys appear as columns when needed for selection lookup."""
    if not groupby_cols:
        return display_df
    if all(c in display_df.columns for c in groupby_cols):
        return display_df
    out = display_df.copy()
    if isinstance(out.index, pd.MultiIndex):
        return out.reset_index()
    if out.index.name is not None:
        return out.reset_index()
    return out.reset_index()


def _row_key_from_agg_position(agg_df: pd.DataFrame, position: int) -> tuple:
    """Build source_mapping key from a positional row in agg_df (legacy path)."""
    if isinstance(agg_df.index, pd.MultiIndex):
        return tuple(agg_df.index[position])  # type: ignore[return-value]
    return (agg_df.index[position],)


def _agg_row_for_key(agg_df: pd.DataFrame, row_key: tuple) -> pd.Series:
    """Slice one aggregated row for display, matching TrackedDataFrame key conventions."""
    if isinstance(agg_df.index, pd.MultiIndex):
        return agg_df.loc[row_key]
    if len(row_key) == 1:
        return agg_df.loc[row_key[0]]
    return agg_df.loc[row_key]


def _resolve_row_key_from_selection(
    display_df: pd.DataFrame,
    selected_row_num: int,
    groupby_cols: List[str],
    agg_df: pd.DataFrame,
) -> Optional[tuple]:
    """
    Map st.dataframe selection index to a source_mapping key.

    Uses groupby column values from the displayed (possibly filtered) row when available;
    falls back to positional alignment only when the displayed table has the same rows
    and order as agg_df.
    """
    if not (0 <= selected_row_num < len(display_df)):
        return None
    display_df = _ensure_groupby_columns_in_frame(display_df, groupby_cols)
    if selected_row_num >= len(display_df):
        return None
    if groupby_cols and all(c in display_df.columns for c in groupby_cols):
        row = display_df.iloc[selected_row_num]
        return tuple(row[c] for c in groupby_cols)
    if len(display_df) == len(agg_df) and display_df.index.equals(agg_df.index):
        return _row_key_from_agg_position(agg_df, selected_row_num)
    return None


def render_table_view(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    config: Optional[InspectorConfig] = None,
) -> None:
    """
    Render the main table view with drill-down capabilities.

    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        config: Optional configuration object
    """
    if config is None:
        config = get_default_config()

    st.header("📊 Aggregated Data")

    # Convert index to columns for display and for stable group-key lookup after filtering
    display_df = agg_df.copy()
    if isinstance(display_df.index, pd.MultiIndex):
        display_df = display_df.reset_index()
    elif display_df.index.name is not None:
        display_df = display_df.reset_index()
    else:
        display_df = _ensure_groupby_columns_in_frame(display_df, groupby_cols)

    # Apply filters if enabled
    if config.show_filters:
        filter_key = f"luxin_filter_{id(agg_df)}"
        display_df = render_filters(display_df, key_prefix=filter_key)

    # Use clickable table rows with st.dataframe selection
    if len(display_df) > 0:
        # Create two columns: main table and detail panel
        col1, col2 = st.columns([2, 1])

        with col1:
            # Display the aggregated table with selection enabled
            selected_rows = st.dataframe(
                display_df,
                use_container_width=True,
                height=config.table_height,
                on_select="rerun",
                selection_mode="single-row",
                key=f"luxin_table_{id(agg_df)}",
            )

        row_key: Optional[tuple] = None
        if selected_rows.selection.rows:  # type: ignore[attr-defined]
            selected_row_num = selected_rows.selection.rows[0]  # type: ignore[attr-defined]
            row_key = _resolve_row_key_from_selection(
                display_df, selected_row_num, groupby_cols, agg_df
            )

        if row_key is not None:
            _show_row_details(
                row_key, agg_df, detail_df, source_mapping, groupby_cols, col2, config
            )
        else:
            with col2:
                st.info("👆 Click on a row in the table to see detail data")
    else:
        st.warning("No data to display.")

    # Export functionality (if enabled)
    if config.show_export_buttons:
        with st.expander("📥 Export Data", expanded=False):
            render_export_buttons(display_df, filename_prefix="aggregated_data")

    # Show summary stats below (if enabled)
    if config.show_summary_stats and len(agg_df) > 0 and len(agg_df.columns) > 0:
        with st.expander("📈 Summary Statistics"):
            try:
                st.dataframe(agg_df.describe(), use_container_width=True)
            except ValueError:
                # Empty DataFrame or no numeric columns
                st.info("No statistics available for this data.")


def _show_row_details(
    row_key: tuple,
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    detail_col: Any,
    config: Optional[InspectorConfig] = None,
) -> None:
    """
    Show detail rows for the selected aggregated row.

    Args:
        row_key: Tuple key matching ``source_mapping`` (e.g. ``('A',)`` or ``('N','P')``).
        agg_df: The aggregated DataFrame
        detail_df: The detail DataFrame
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: Column names used in the groupby operation
        detail_col: Streamlit column to render details in
    """
    with detail_col:
        st.subheader("🔍 Detail Rows")

        detail_indices = source_mapping.get(row_key, [])

        if not detail_indices:
            st.warning(
                "No detail rows found for this selection.\n\n"
                "This may happen if:\n"
                "- The aggregation was not performed using TrackedDataFrame\n"
                "- The source mapping was not properly tracked\n"
                "- The selected row doesn't have corresponding detail data"
            )
            return

        detail_rows = detail_df.loc[detail_indices]

        st.caption(f"Found {len(detail_rows)} detail row(s)")

        if config is None:
            config = get_default_config()
        render_detail_panel(
            detail_rows,
            title="Detail Rows",
            height=config.detail_height,
            page_size=config.detail_page_size,
        )

        with st.expander("📋 Aggregated Values"):
            try:
                agg_row = _agg_row_for_key(agg_df, row_key)
            except (KeyError, IndexError, TypeError):
                st.info("Could not resolve aggregated row values for this selection.")
            else:
                st.json(agg_row.to_dict())

        if config.show_export_buttons:
            with st.expander("📥 Export Detail Data", expanded=False):
                render_export_buttons(detail_rows, filename_prefix="detail_data")
