"""
Detail panel component for displaying individual row details.
"""

import pandas as pd
import streamlit as st
from typing import List, Optional


def render_detail_panel(
    detail_rows: pd.DataFrame,
    title: str = "Detail Rows",
    height: int = 300,
    page_size: int = 100
) -> None:
    """
    Render a detail panel showing individual rows with pagination.
    
    Args:
        detail_rows: DataFrame containing the detail rows to display
        title: Title for the detail panel
        height: Height of the dataframe display in pixels
        page_size: Number of rows per page (for pagination)
    """
    st.subheader(f"🔍 {title}")
    st.caption(f"Total: {len(detail_rows)} row(s)")
    
    # Add pagination for large datasets
    if len(detail_rows) > page_size:
        total_pages = (len(detail_rows) + page_size - 1) // page_size
        page_key = f"detail_page_{id(detail_rows)}"
        
        if page_key not in st.session_state:
            st.session_state[page_key] = 1
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("◀ Previous", disabled=st.session_state[page_key] == 1, key=f"{page_key}_prev"):
                st.session_state[page_key] = max(1, st.session_state[page_key] - 1)
                st.rerun()
        
        with col2:
            page = st.number_input(
                "Page",
                min_value=1,
                max_value=total_pages,
                value=st.session_state[page_key],
                key=f"{page_key}_input",
                on_change=lambda: st.session_state.update({page_key: st.session_state[f"{page_key}_input"]})
            )
            st.session_state[page_key] = page
            st.caption(f"Page {page} of {total_pages}")
        
        with col3:
            if st.button("Next ▶", disabled=st.session_state[page_key] == total_pages, key=f"{page_key}_next"):
                st.session_state[page_key] = min(total_pages, st.session_state[page_key] + 1)
                st.rerun()
        
        # Get page slice
        start_idx = (st.session_state[page_key] - 1) * page_size
        end_idx = start_idx + page_size
        paginated_rows = detail_rows.iloc[start_idx:end_idx]
        
        st.dataframe(
            paginated_rows,
            use_container_width=True,
            height=height
        )
    else:
        # No pagination needed
        st.dataframe(
            detail_rows,
            use_container_width=True,
            height=height
        )

