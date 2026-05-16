"""Tests for comparison Streamlit helpers (mocked ``st``)."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from luxin.components.comparison import inspect_pair, render_comparison_views
from luxin.config import InspectorConfig


@pytest.mark.streamlit
@patch("luxin.components.comparison.st")
def test_render_comparison_views_basic_layout(mock_st, sample_comparison_frames):
    left, right = sample_comparison_frames
    mock_st.columns.return_value = (MagicMock(), MagicMock())

    render_comparison_views(left, right, join_keys=["region"])

    mock_st.subheader.assert_called_once_with("Comparison mode")
    assert mock_st.dataframe.call_count >= 2
    mock_st.expander.assert_called()


@pytest.mark.streamlit
@patch("luxin.components.comparison.st")
def test_render_comparison_views_empty_join_keys(mock_st, sample_comparison_frames):
    left, right = sample_comparison_frames
    render_comparison_views(left, right, join_keys=[])
    mock_st.warning.assert_called()
    mock_st.subheader.assert_called_once()


@pytest.mark.streamlit
@patch("luxin.components.comparison.st")
def test_inspect_pair_delegates(mock_st, sample_comparison_frames):
    left, right = sample_comparison_frames
    mock_st.columns.return_value = (MagicMock(), MagicMock())

    inspect_pair(left, right, join_keys=["region"], left_label="L", right_label="R")

    assert mock_st.subheader.call_count == 1
    mock_st.caption.assert_any_call("L")
    mock_st.caption.assert_any_call("R")


@pytest.mark.streamlit
@patch("luxin.components.comparison.st")
@patch("luxin.components.comparison._maybe_run_ttests")
def test_render_comparison_significance_empty_tests(
    mock_ttest, mock_st, sample_comparison_frames
):
    left, right = sample_comparison_frames
    mock_st.columns.return_value = (MagicMock(), MagicMock())
    mock_ttest.return_value = {}

    cfg = InspectorConfig(compare_run_significance=True)
    render_comparison_views(left, right, join_keys=["region"], config=cfg)

    mock_ttest.assert_called_once()
    infos = [c.args[0] for c in mock_st.info.call_args_list if c.args]
    assert any("scipy" in str(a).lower() for a in infos)


@pytest.mark.streamlit
@patch("luxin.components.comparison.st")
@patch("luxin.components.comparison._maybe_run_ttests")
def test_render_comparison_significance_with_results(
    mock_ttest, mock_st, sample_comparison_frames
):
    left, right = sample_comparison_frames
    mock_st.columns.return_value = (MagicMock(), MagicMock())
    mock_res = SimpleNamespace(statistic=1.23, pvalue=0.04)
    mock_ttest.return_value = {"sales": mock_res}

    cfg = InspectorConfig(compare_run_significance=True)
    render_comparison_views(left, right, join_keys=["region"], config=cfg)

    mock_ttest.assert_called_once()
    assert mock_st.dataframe.call_count >= 2
