"""
Inspector - Main class for interactive data exploration with drill-down capabilities.
"""

import pandas as pd
from typing import Optional, Dict, Any, List, Union
import streamlit as st
from luxin.polars_support import handle_polars_in_inspector, is_polars_dataframe
from luxin.config import InspectorConfig, get_default_config
from luxin.validation import validate_dataframe, ValidationError


class Inspector:
    """
    Inspector class for interactive drill-down data exploration.
    
    Similar to lavendertown's Inspector pattern, this class provides
    a Streamlit-first interface for exploring aggregated data with
    drill-down capabilities.
    
    Example:
        >>> import streamlit as st
        >>> from luxin import Inspector
        >>> import pandas as pd
        >>> 
        >>> df = pd.read_csv("data.csv")
        >>> inspector = Inspector(df)
        >>> inspector.render()
    """
    
    def __init__(self, df: Union[pd.DataFrame, Any], config: Optional[InspectorConfig] = None) -> None:
        """
        Initialize the Inspector with a DataFrame.
        
        Args:
            df: The DataFrame to inspect. Can be a regular pandas DataFrame,
                Polars DataFrame, or a TrackedDataFrame with aggregation tracking.
            config: Optional configuration object. If None, uses default config.
        """
        # Handle Polars DataFrames
        if is_polars_dataframe(df):
            df = handle_polars_in_inspector(df)
        
        # Validate input
        try:
            validate_dataframe(df, "df")
        except ValidationError as e:
            raise ValueError(str(e)) from e
        
        self.df = df
        self.config = config if config is not None else get_default_config()
        self._is_aggregated = False
        self._source_mapping: Dict[Any, List[int]] = {}
        self._groupby_cols: List[str] = []
        self._source_df: Optional[pd.DataFrame] = None
        
        # Check if this is a TrackedDataFrame with aggregation info
        if hasattr(df, '_is_aggregated') and df._is_aggregated:
            self._is_aggregated = True
            self._source_mapping = getattr(df, '_source_mapping', {})
            self._groupby_cols = getattr(df, '_groupby_cols', [])
            self._source_df = getattr(df, '_source_df', None)
    
    def render(self) -> None:
        """
        Render the interactive drill-down interface in Streamlit.
        
        This method must be called within a Streamlit app context.
        It will display the aggregated data (if available) or the
        source data, with interactive drill-down capabilities.
        """
        try:
            import streamlit as st
        except ImportError:
            raise ImportError(
                "Streamlit is required for Inspector.render().\n"
                "Install with: pip install streamlit\n"
                "Or install luxin with Streamlit: pip install luxin[streamlit]"
            ) from None
        
        if self._is_aggregated and self._source_df is not None:
            # Display aggregated view with drill-down
            from luxin.components.table_view import render_table_view
            render_table_view(
                agg_df=self.df,
                detail_df=self._source_df,
                source_mapping=self._source_mapping,
                groupby_cols=self._groupby_cols,
                config=self.config
            )
        else:
            # Display source data only (no aggregation tracking)
            st.dataframe(self.df, use_container_width=True)
            st.info(
                "💡 Tip: To enable drill-down capabilities, use TrackedDataFrame:\n\n"
                "```python\n"
                "from luxin import TrackedDataFrame, Inspector\n"
                "df = TrackedDataFrame(your_data)\n"
                "agg = df.groupby('column').agg({'value': 'sum'})\n"
                "inspector = Inspector(agg)\n"
                "inspector.render()\n"
                "```"
            )

