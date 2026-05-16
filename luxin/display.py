"""
Route drill-down display to Streamlit (in-app) or Jupyter HTML (optional ``luxin-nb``).
"""

from typing import Any, List

import pandas as pd

from luxin_core.utils import SourceMapping

_NOTEBOOK_INSTALL_HINT = (
    "Jupyter/HTML drill-down needs the notebook extra or luxin-nb. "
    "Install with: pip install luxin[notebook]  (or pip install luxin-nb)"
)


_STREAMLIT_CONTEXT_HINT = (
    "display_drill_table needs a supported environment: run inside `streamlit run`, "
    "or in Jupyter/IPython with luxin[notebook] (or luxin-nb) installed."
)


def display_drill_table(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
    **kwargs: Any,
) -> None:
    """
    Display an interactive drill-down table.

    Detects the current execution environment (Jupyter or Streamlit) and uses
    the appropriate backend for rendering.
    """
    env = _detect_environment()

    if env == "streamlit":
        from luxin.streamlit_backend import display_streamlit

        display_streamlit(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)
        return

    if env == "unknown":
        raise ImportError(_STREAMLIT_CONTEXT_HINT)

    try:
        from luxin_nb.display import display_drill_table as display_notebook
    except ImportError as e:
        raise ImportError(_NOTEBOOK_INSTALL_HINT) from e

    display_notebook(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


def _detect_environment() -> str:
    """
    Detect the current execution environment.

    Uses Streamlit's script run context (not mere package import),
    then IPython for notebooks.

    Returns:
        'jupyter', 'streamlit', or 'unknown'
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        if get_script_run_ctx() is not None:
            return "streamlit"
    except (ImportError, AttributeError):
        pass

    try:
        from IPython import get_ipython

        if get_ipython() is not None:
            return "jupyter"
    except ImportError:
        pass

    return "unknown"


def render_html(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
) -> str:
    """Render the interactive drill-down HTML (requires ``luxin-nb``)."""
    try:
        from luxin_nb.display import render_html as _render
    except ImportError as e:
        raise ImportError(_NOTEBOOK_INSTALL_HINT) from e

    return _render(agg_df, detail_df, source_mapping, groupby_cols)


__all__ = ["display_drill_table", "render_html", "_detect_environment"]
