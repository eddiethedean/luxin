"""Tests for display module."""

from unittest.mock import MagicMock, patch

import sys

import pandas as pd

from luxin.display import _detect_environment, render_html


def test_detect_environment():
    """Test environment detection."""
    env = _detect_environment()
    assert env in ["jupyter", "streamlit", "unknown"]


@patch("streamlit.runtime.scriptrunner.get_script_run_ctx")
def test_detect_environment_prefers_active_streamlit_context(mock_ctx):
    """When ScriptRunContext exists, classify as Streamlit."""
    mock_ctx.return_value = MagicMock()
    assert _detect_environment() == "streamlit"


def test_detect_environment_jupyter_via_ipython():
    """IPython-only sessions resolve as Jupyter when not in Streamlit."""
    ip_mod = MagicMock()
    ip_mod.get_ipython = MagicMock(return_value=MagicMock())
    with patch.dict(sys.modules, {"IPython": ip_mod}):
        with patch(
            "streamlit.runtime.scriptrunner.get_script_run_ctx", return_value=None
        ):
            assert _detect_environment() == "jupyter"


def test_detect_environment_unknown_without_ctx_or_ipython():
    ip_empty = MagicMock()
    ip_empty.get_ipython = MagicMock(return_value=None)
    with patch.dict(sys.modules, {"IPython": ip_empty}):
        with patch(
            "streamlit.runtime.scriptrunner.get_script_run_ctx", return_value=None
        ):
            assert _detect_environment() == "unknown"


def test_render_html_basic():
    """Test basic HTML rendering."""
    detail_df = pd.DataFrame(
        {
            "category": ["A", "A", "B", "B"],
            "value": [10, 20, 30, 40],
        }
    )

    agg_df = detail_df.groupby("category").sum()

    source_mapping = {
        ("A",): [0, 1],
        ("B",): [2, 3],
    }

    html = render_html(agg_df, detail_df, source_mapping, ["category"])

    assert "<html>" in html
    assert "<style>" in html
    assert "<script>" in html
    assert "luxin-container" in html
    assert "detail-panel" in html
    assert 'data-luxin-key="' in html
    assert html.count('data-luxin-key="') >= 2


def test_render_html_with_multiindex():
    """Test HTML rendering with multi-index aggregation."""
    detail_df = pd.DataFrame(
        {
            "cat1": ["A", "A", "B", "B"],
            "cat2": ["X", "Y", "X", "Y"],
            "value": [10, 20, 30, 40],
        }
    )

    agg_df = detail_df.groupby(["cat1", "cat2"]).sum()

    source_mapping = {
        ("A", "X"): [0],
        ("A", "Y"): [1],
        ("B", "X"): [2],
        ("B", "Y"): [3],
    }

    html = render_html(agg_df, detail_df, source_mapping, ["cat1", "cat2"])

    assert "<html>" in html
    assert len(html) > 0
    assert 'data-luxin-key="A|X"' in html or 'data-luxin-key="A|Y"' in html
