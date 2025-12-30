"""
Export functionality for DataFrames.
"""

import pandas as pd
import streamlit as st
from typing import Optional
import io


def render_export_buttons(df: pd.DataFrame, filename_prefix: str = "data") -> None:
    """
    Render export buttons for DataFrame.
    
    Args:
        df: The DataFrame to export
        filename_prefix: Prefix for downloaded file names
    """
    st.subheader("📥 Export Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            label="📄 Download CSV",
            data=csv,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            key=f"export_csv_{id(df)}"
        )
    
    with col2:
        # JSON export
        json_str = df.to_json(orient='records', indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_str,
            file_name=f"{filename_prefix}.json",
            mime="application/json",
            key=f"export_json_{id(df)}"
        )
    
    with col3:
        # Excel export (if openpyxl is available)
        try:
            import openpyxl
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Download Excel",
                data=excel_buffer,
                file_name=f"{filename_prefix}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"export_excel_{id(df)}"
            )
        except ImportError:
            st.info("💡 Install openpyxl for Excel export: `pip install openpyxl`")

