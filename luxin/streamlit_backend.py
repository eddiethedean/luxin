"""
Streamlit backend for displaying interactive drill-down tables.
"""

import pandas as pd
from typing import List

from luxin_core.utils import SourceMapping


def display_streamlit(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
    **kwargs,
):
    """
    Display an interactive drill-down table in Streamlit using native widgets.

    This function is now a wrapper that uses the new modular components.
    For new code, use Inspector(df).render() instead.

    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Mapping from aggregated row keys to lists of detail index labels
        groupby_cols: List of column names used to group the data
        **kwargs: Forwarded into :class:`~luxin.config.InspectorConfig`; use ``config`` to pass an
                  instance explicitly. Unknown keys are ignored by ``InspectorConfig.from_dict``.
                  Use ``widget_key_suffix`` for stable ``st.dataframe`` / filter widget keys across
                  reruns (same value as :meth:`luxin.inspector.Inspector` session suffix).
    """
    try:
        import streamlit as st  # noqa: F401
    except ImportError:
        raise ImportError(
            "Streamlit is required for Streamlit backend. "
            "Install with: pip install streamlit"
        ) from None

    from luxin.components.table_view import render_table_view
    from luxin_core.config import InspectorConfig, get_default_config

    kwargs_copy = dict(kwargs)
    config_obj = kwargs_copy.pop("config", None)
    widget_key_suffix = kwargs_copy.pop("widget_key_suffix", None)
    if config_obj is None and kwargs_copy:
        config_obj = InspectorConfig.from_dict(kwargs_copy)
    if config_obj is None:
        config_obj = get_default_config()

    render_table_view(
        agg_df,
        detail_df,
        source_mapping,
        groupby_cols,
        config=config_obj,
        widget_key_suffix=widget_key_suffix,
    )
