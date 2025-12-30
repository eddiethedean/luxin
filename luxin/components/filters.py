"""
Filtering component for aggregated data tables.
"""

import pandas as pd
import streamlit as st
from typing import List, Optional, Dict, Any


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
        placeholder="Search in all columns..."
    )
    
    if search_text:
        # Search across all string columns
        mask = pd.Series([False] * len(df))
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                mask |= df[col].astype(str).str.contains(search_text, case=False, na=False)
            else:
                # For numeric columns, convert to string for search
                mask |= df[col].astype(str).str.contains(search_text, case=False, na=False)
        filtered_df = filtered_df[mask]
    
    # Column-specific filters
    with st.expander("🔧 Column Filters", expanded=False):
        for col in df.columns:
            if df[col].dtype == 'object':
                # String column - use multiselect
                unique_vals = sorted(df[col].dropna().unique().tolist())
                if len(unique_vals) > 0 and len(unique_vals) <= 50:  # Limit to reasonable number
                    selected = st.multiselect(
                        f"Filter {col}",
                        options=unique_vals,
                        default=[],
                        key=f"{key_prefix}_col_{col}"
                    )
                    if selected:
                        filtered_df = filtered_df[filtered_df[col].isin(selected)]
            elif pd.api.types.is_numeric_dtype(df[col]):
                # Numeric column - use range slider
                col_min = float(df[col].min())
                col_max = float(df[col].max())
                if col_min < col_max:
                    range_vals = st.slider(
                        f"Filter {col}",
                        min_value=col_min,
                        max_value=col_max,
                        value=(col_min, col_max),
                        key=f"{key_prefix}_col_{col}"
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= range_vals[0]) & 
                        (filtered_df[col] <= range_vals[1])
                    ]
    
    # Show filter results count
    if len(filtered_df) != len(df):
        st.caption(f"Showing {len(filtered_df)} of {len(df)} rows")
    
    return filtered_df

