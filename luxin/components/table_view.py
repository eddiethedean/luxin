"""
Table view component for displaying aggregated data with drill-down.
"""

import hashlib

import pandas as pd
import streamlit as st
from typing import Any, List, Optional
from luxin.components.breadcrumbs import render_drill_breadcrumbs
from luxin.components.detail_panel import render_detail_panel
from luxin.components.filters import render_filters
from luxin.components.export import render_export_buttons
from luxin_core.config import InspectorConfig, get_default_config
from luxin_core.drill_hierarchy import (
    DrillHierarchySpec,
    ensure_initial_stack,
    stack_state_key,
    try_push_selected,
)
from luxin_core.utils import finalize_source_mapping, normalize_group_key, SourceMapping
from luxin._streamlit_compat import (
    dataframe_selection_guard_message,
    dataframe_selection_supported,
)

_SELECTION_UNMAPPED_MSG = (
    "Could not map the selected row to an aggregate group key. "
    "Try clearing filters, or ensure group-by columns appear in the table."
)


def _dataframe_selection_first_row(selected_rows: object) -> Optional[int]:
    """Read first selected row index from ``st.dataframe`` selection API (Streamlit >= 1.35)."""
    sel = getattr(selected_rows, "selection", None)
    if sel is None:
        return None
    rows = getattr(sel, "rows", None)
    if not rows:
        return None
    return int(rows[0])


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


def _align_display_index_columns(
    display_df: pd.DataFrame, agg_df: pd.DataFrame, groupby_cols: List[str]
) -> pd.DataFrame:
    """When ``reset_index()`` produced generic column names, rename them to ``groupby_cols``."""
    if not groupby_cols:
        return display_df
    if all(c in display_df.columns for c in groupby_cols):
        return display_df
    idx_origin_cols = [c for c in display_df.columns if c not in agg_df.columns]
    if len(idx_origin_cols) == len(groupby_cols):
        return display_df.rename(columns=dict(zip(idx_origin_cols, groupby_cols)))
    return display_df


def _row_key_from_agg_position(agg_df: pd.DataFrame, position: int) -> tuple:
    """Build source_mapping key from a positional row in agg_df (legacy path)."""
    if isinstance(agg_df.index, pd.MultiIndex):
        raw = tuple(agg_df.index[position])
    else:
        raw = (agg_df.index[position],)
    return normalize_group_key(raw)


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
        return normalize_group_key(tuple(row[c] for c in groupby_cols))
    if len(display_df) == len(agg_df) and display_df.index.equals(agg_df.index):
        return _row_key_from_agg_position(agg_df, selected_row_num)
    return None


def render_drill_stack_view(
    root_tracked_agg: Any,
    spec: DrillHierarchySpec,
    config: Optional[InspectorConfig] = None,
    *,
    widget_key_suffix: Optional[str] = None,
) -> None:
    """
    Multi-level drill: breadcrumb stack + aggregated table at current depth + detail panel.
    """
    if config is None:
        config = get_default_config()

    if not dataframe_selection_supported():
        st.error(dataframe_selection_guard_message())
        return

    ensure_initial_stack(st.session_state, spec, root_tracked_agg)
    stack = list(st.session_state[stack_state_key(spec)])
    render_drill_breadcrumbs(stack, spec)

    current = stack[-1]
    agg_df = current.agg_df
    detail_df = current.detail_df
    source_mapping = finalize_source_mapping(dict(current.source_mapping))
    groupby_cols = list(current.groupby_cols)

    st.header("📊 Aggregated Data")

    display_df = agg_df.copy()
    if isinstance(display_df.index, pd.MultiIndex):
        display_df = display_df.reset_index()
    elif display_df.index.name is not None:
        display_df = display_df.reset_index()
    else:
        display_df = _ensure_groupby_columns_in_frame(display_df, groupby_cols)

    display_df = _align_display_index_columns(display_df, agg_df, groupby_cols)

    if config.show_filters:
        if widget_key_suffix:
            filter_key = f"luxin_filter_drill_{widget_key_suffix}_{spec.session_key}_{len(stack)}"
        else:
            filter_key = f"luxin_filter_drill_{spec.session_key}_{len(stack)}"
        display_df = render_filters(display_df, key_prefix=filter_key)

    if len(display_df) > 0:
        if widget_key_suffix:
            widget_table_key = (
                f"luxin_table_{widget_key_suffix}_{spec.session_key}_{len(stack)}"
            )
        else:
            widget_table_key = f"luxin_table_{spec.session_key}_{len(stack)}"
        col1, col2 = st.columns([2, 1])
        with col1:
            selected_rows = st.dataframe(
                display_df,
                use_container_width=True,
                height=config.table_height,
                on_select="rerun",
                selection_mode="single-row",
                key=widget_table_key,
            )

        row_key: Optional[tuple] = None
        selected_row_num = _dataframe_selection_first_row(selected_rows)
        if selected_row_num is not None:
            row_key = _resolve_row_key_from_selection(
                display_df, selected_row_num, groupby_cols, agg_df
            )

        old_len = len(stack)
        if row_key is not None:
            try_push_selected(
                st.session_state,
                stack,
                row_key,
                spec,
                absolute_max_depth=config.max_drill_depth,
            )
            stack = list(st.session_state[stack_state_key(spec)])
            current = stack[-1]
            agg_df = current.agg_df
            detail_df = current.detail_df
            source_mapping = finalize_source_mapping(dict(current.source_mapping))
            groupby_cols = list(current.groupby_cols)

        detail_pagination_base = f"luxin_table_{spec.session_key}_{len(stack)}"

        if row_key is not None:
            if len(stack) > old_len:
                parent = stack[-2]
                _show_row_details(
                    row_key,
                    parent.agg_df,
                    parent.detail_df,
                    parent.source_mapping,
                    parent.groupby_cols,
                    col2,
                    config,
                    pagination_base_key=detail_pagination_base,
                )
            else:
                _show_row_details(
                    row_key,
                    agg_df,
                    detail_df,
                    source_mapping,
                    groupby_cols,
                    col2,
                    config,
                    pagination_base_key=detail_pagination_base,
                )
        else:
            with col2:
                if selected_row_num is not None:
                    st.warning(_SELECTION_UNMAPPED_MSG)
                else:
                    st.info("👆 Click on a row in the table to see detail data")
    else:
        st.warning("No data to display.")

    if config.show_export_buttons:
        with st.expander("📥 Export Data", expanded=False):
            render_export_buttons(display_df, filename_prefix="aggregated_data")

    if config.show_summary_stats and len(agg_df) > 0 and len(agg_df.columns) > 0:
        with st.expander("📈 Summary Statistics"):
            try:
                st.dataframe(agg_df.describe(), use_container_width=True)
            except ValueError:
                st.info("No statistics available for this data.")


def render_table_view(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
    config: Optional[InspectorConfig] = None,
    *,
    widget_key_suffix: Optional[str] = None,
) -> None:
    """
    Render the main table view with drill-down capabilities.

    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Mapping from aggregated row keys to lists of detail index labels
        groupby_cols: List of column names used to group the data
        config: Optional configuration object
    """
    if config is None:
        config = get_default_config()

    if not dataframe_selection_supported():
        st.error(dataframe_selection_guard_message())
        return

    source_mapping = finalize_source_mapping(dict(source_mapping))

    st.header("📊 Aggregated Data")

    # Convert index to columns for display and for stable group-key lookup after filtering
    display_df = agg_df.copy()
    if isinstance(display_df.index, pd.MultiIndex):
        display_df = display_df.reset_index()
    elif display_df.index.name is not None:
        display_df = display_df.reset_index()
    else:
        display_df = _ensure_groupby_columns_in_frame(display_df, groupby_cols)

    display_df = _align_display_index_columns(display_df, agg_df, groupby_cols)

    # Apply filters if enabled
    if config.show_filters:
        filter_key = (
            f"luxin_filter_{widget_key_suffix}"
            if widget_key_suffix
            else f"luxin_filter_{id(agg_df)}"
        )
        display_df = render_filters(display_df, key_prefix=filter_key)

    # Use clickable table rows with st.dataframe selection
    if len(display_df) > 0:
        # Create two columns: main table and detail panel
        table_key = (
            f"luxin_table_{widget_key_suffix}"
            if widget_key_suffix
            else f"luxin_table_{id(agg_df)}"
        )
        col1, col2 = st.columns([2, 1])

        with col1:
            # Display the aggregated table with selection enabled
            selected_rows = st.dataframe(
                display_df,
                use_container_width=True,
                height=config.table_height,
                on_select="rerun",
                selection_mode="single-row",
                key=table_key,
            )

        row_key: Optional[tuple] = None
        selected_row_num = _dataframe_selection_first_row(selected_rows)
        if selected_row_num is not None:
            row_key = _resolve_row_key_from_selection(
                display_df, selected_row_num, groupby_cols, agg_df
            )

        if row_key is not None:
            _show_row_details(
                row_key,
                agg_df,
                detail_df,
                source_mapping,
                groupby_cols,
                col2,
                config,
                pagination_base_key=table_key,
            )
        else:
            with col2:
                if selected_row_num is not None:
                    st.warning(_SELECTION_UNMAPPED_MSG)
                else:
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
    source_mapping: SourceMapping,
    groupby_cols: List[str],
    detail_col: Any,
    config: Optional[InspectorConfig] = None,
    *,
    pagination_base_key: Optional[str] = None,
) -> None:
    """
    Show detail rows for the selected aggregated row.

    Args:
        row_key: Tuple key matching ``source_mapping`` (e.g. ``('A',)`` or ``('N','P')``).
        agg_df: The aggregated DataFrame
        detail_df: The detail DataFrame
        source_mapping: Mapping from aggregated row keys to lists of detail index labels
        groupby_cols: Column names used in the groupby operation
        detail_col: Streamlit column to render details in
        pagination_base_key: Prefix for stable detail-pagination session keys (e.g. main table widget key)
    """
    with detail_col:
        nk = normalize_group_key(row_key)
        detail_indices = source_mapping.get(nk, [])

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
            pagination_session_key=(
                f"{pagination_base_key}_d_{hashlib.sha256(repr(nk).encode()).hexdigest()[:16]}"
                if pagination_base_key
                else None
            ),
        )

        if config.show_data_quality:
            from luxin.components.quality_indicators import render_quality_dashboard

            render_quality_dashboard(detail_rows)

        with st.expander("📋 Aggregated Values"):
            try:
                agg_row = _agg_row_for_key(agg_df, nk)
            except (KeyError, IndexError, TypeError):
                st.info("Could not resolve aggregated row values for this selection.")
            else:
                st.json(agg_row.to_dict())

        if config.show_export_buttons:
            with st.expander("📥 Export Detail Data", expanded=False):
                render_export_buttons(detail_rows, filename_prefix="detail_data")
