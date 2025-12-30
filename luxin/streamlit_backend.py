"""
Streamlit backend for displaying interactive drill-down tables.
"""

import pandas as pd
from typing import Dict, Any, List


def display_streamlit(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    **kwargs
):
    """
    Display an interactive drill-down table in Streamlit using native widgets.
    
    This function is now a wrapper that uses the new modular components.
    For new code, use Inspector(df).render() instead.
    
    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        groupby_cols: List of column names used to group the data
        **kwargs: Additional options for display customization (deprecated)
    """
    try:
        import streamlit as st
    except ImportError:
        raise ImportError(
            "Streamlit is required for Streamlit backend. "
            "Install with: pip install streamlit"
        )
    
    # Use the new modular components
    from luxin.components.table_view import render_table_view
    render_table_view(agg_df, detail_df, source_mapping, groupby_cols)

