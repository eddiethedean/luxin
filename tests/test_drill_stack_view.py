"""Tests for multi-level drill stack table view (mocked Streamlit)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from luxin import TrackedDataFrame
from luxin.components.table_view import render_drill_stack_view
from luxin_core.drill_hierarchy import DrillHierarchySpec
from luxin.config import InspectorConfig


@pytest.mark.streamlit
@patch("luxin.components.table_view.render_export_buttons")
@patch("luxin.components.table_view.render_drill_breadcrumbs")
@patch("luxin.components.table_view.dataframe_selection_supported", return_value=True)
@patch("luxin.components.table_view.st")
def test_render_drill_stack_view_initial_stack(mock_st, _supported, mock_bc, _export):
    df = TrackedDataFrame(
        {
            "region": ["N", "N", "S"],
            "product": ["A", "B", "A"],
            "value": [1.0, 2.0, 3.0],
        }
    )
    root = df.groupby("region").agg({"value": "sum"})
    child = (
        TrackedDataFrame({"product": ["A"], "value": [1.0]})
        .groupby("product")
        .agg({"value": "sum"})
    )
    spec = DrillHierarchySpec(
        session_key="stack_render",
        children_by_parent_key={("N",): child},
    )

    sess: dict = {}
    mock_st.session_state = sess
    col1, col2 = MagicMock(), MagicMock()
    mock_st.columns.return_value = (col1, col2)
    selected = MagicMock()
    selected.selection = MagicMock(rows=[])
    mock_st.dataframe.return_value = selected

    cfg = InspectorConfig(
        show_filters=False, show_export_buttons=False, show_summary_stats=False
    )
    render_drill_stack_view(root, spec, config=cfg, widget_key_suffix="t")

    mock_bc.assert_called_once()
    mock_st.header.assert_called_once()
    mock_st.dataframe.assert_called_once()
    mock_st.info.assert_called()


@pytest.mark.streamlit
@patch("luxin.components.table_view.dataframe_selection_supported", return_value=False)
@patch("luxin.components.table_view.st")
def test_render_drill_stack_view_streamlit_too_old(mock_st, _unsupported, sample_agg):
    spec = DrillHierarchySpec(session_key="old_st", next_level=lambda k, d: None)
    render_drill_stack_view(sample_agg, spec)
    mock_st.error.assert_called_once()
