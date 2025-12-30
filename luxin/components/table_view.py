"""
Table view component for displaying aggregated data with drill-down.
"""

import pandas as pd
import streamlit as st
from typing import Dict, Any, List
from luxin.components.detail_panel import render_detail_panel
from luxin.components.filters import render_filters
from luxin.components.export import render_export_buttons
from luxin.config import InspectorConfig, get_default_config
from typing import Optional


def render_table_view(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    config: Optional[InspectorConfig] = None
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
    
    # Convert index to columns for better display
    display_df = agg_df.copy()
    if isinstance(display_df.index, pd.MultiIndex):
        display_df = display_df.reset_index()
    elif display_df.index.name is not None:
        display_df = display_df.reset_index()
    
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
                key=f"luxin_table_{id(agg_df)}"
            )
        
        # Get selected row index
        selected_idx = None
        if selected_rows.selection.rows:
            # Get the first selected row index
            selected_row_num = selected_rows.selection.rows[0]
            # Map display index to original agg_df index
            if isinstance(agg_df.index, pd.MultiIndex):
                # For MultiIndex, we need to map from display_df reset_index position
                if isinstance(display_df.index, pd.RangeIndex):
                    # display_df was reset_index, so selected_row_num maps directly
                    selected_idx = selected_row_num
                else:
                    selected_idx = selected_row_num
            else:
                selected_idx = selected_row_num
        
        # Show selected row details if a row is selected
        if selected_idx is not None and selected_idx < len(agg_df):
            _show_row_details(selected_idx, agg_df, detail_df, source_mapping, groupby_cols, col2, config)
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
    selected_idx: int,
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    detail_col: Any,
    config: Optional[InspectorConfig] = None
) -> None:
    """
    Show detail rows for the selected aggregated row.
    
    Args:
        selected_idx: Index of the selected row in the aggregated DataFrame
        agg_df: The aggregated DataFrame
        detail_df: The detail DataFrame
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        detail_col: Streamlit column to render details in
    """
    with detail_col:
        st.subheader("🔍 Detail Rows")
        
        # Get the row key from the aggregated DataFrame
        if isinstance(agg_df.index, pd.MultiIndex):
            row_key = agg_df.index[selected_idx]
        else:
            row_key = (agg_df.index[selected_idx],)
        
        # Get the detail row indices
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
        
        # Filter detail DataFrame to show only relevant rows
        detail_rows = detail_df.loc[detail_indices]
        
        # Show count
        st.caption(f"Found {len(detail_rows)} detail row(s)")
        
        # Display the detail rows with pagination
        if config is None:
            config = get_default_config()
        from luxin.components.detail_panel import render_detail_panel
        render_detail_panel(
            detail_rows, 
            title="Detail Rows", 
            height=config.detail_height, 
            page_size=config.detail_page_size
        )
        
        # Show the aggregated row values for context
        with st.expander("📋 Aggregated Values"):
            agg_row = agg_df.iloc[selected_idx]
            st.json(agg_row.to_dict())
        
        # Export detail rows (if enabled)
        if config.show_export_buttons:
            with st.expander("📥 Export Detail Data", expanded=False):
                render_export_buttons(detail_rows, filename_prefix="detail_data")

