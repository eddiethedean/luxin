"""Tests for drill breadcrumb UI (mocked Streamlit)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from luxin.components.breadcrumbs import render_drill_breadcrumbs
from luxin_core.drill_hierarchy import DrillHierarchySpec, context_from_tracked
from luxin import TrackedDataFrame


@pytest.mark.streamlit
@patch("luxin.components.breadcrumbs.st")
def test_render_drill_breadcrumbs_one_level(mock_st, sample_agg):
    spec = DrillHierarchySpec(session_key="bc_test", next_level=lambda k, d: None)
    ctx = context_from_tracked(sample_agg, label="Root")
    mock_st.columns.return_value = [MagicMock()]

    render_drill_breadcrumbs([ctx], spec)

    mock_st.caption.assert_called_once_with("Drill path")
    mock_st.columns.assert_called_once_with(1, gap="small")
    mock_st.columns.return_value[0].button.assert_called_once()


@pytest.mark.streamlit
@patch("luxin.components.breadcrumbs.st")
def test_render_drill_breadcrumbs_two_levels(mock_st):
    df = TrackedDataFrame({"region": ["N", "N", "S"], "value": [1.0, 2.0, 3.0]})
    root = df.groupby("region").agg({"value": "sum"})
    spec = DrillHierarchySpec(session_key="bc_two", next_level=lambda k, d: None)
    c1 = context_from_tracked(root, label="Root")
    c2 = context_from_tracked(root, label="Child")
    cols = [MagicMock(), MagicMock()]
    mock_st.columns.return_value = cols

    render_drill_breadcrumbs([c1, c2], spec)

    mock_st.columns.assert_called_once_with(2, gap="small")
    assert cols[0].button.call_count == 1
    assert cols[1].button.call_count == 1


@pytest.mark.streamlit
@patch("luxin.components.breadcrumbs.st")
def test_render_drill_breadcrumbs_empty_stack(mock_st):
    spec = DrillHierarchySpec(session_key="bc_empty", next_level=lambda k, d: None)
    render_drill_breadcrumbs([], spec)
    mock_st.caption.assert_not_called()
