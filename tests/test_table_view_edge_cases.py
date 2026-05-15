"""
Tests for edge cases in table_view component.
"""

import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.table_view import render_table_view
from luxin.config import InspectorConfig


@patch("luxin.components.table_view.st")
@patch("luxin.components.table_view.render_filters")
@patch("luxin.components.table_view.render_export_buttons")
def test_render_table_view_with_named_index(mock_export, mock_filters, mock_st):
    """Test render_table_view with DataFrame that has named index."""
    agg_df = pd.DataFrame(
        {"value": [30, 70]},
        index=pd.Index(["A", "B"], name="category"),
    )
    detail_df = pd.DataFrame(
        {"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]}
    )
    source_mapping = {("A",): [0, 1], ("B",): [2, 3]}
    groupby_cols = ["category"]
    config = InspectorConfig()

    mock_st.header = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.session_state = {}
    mock_filters.side_effect = lambda df, key_prefix=None: df

    render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config)

    mock_st.header.assert_called()


@patch("luxin.components.table_view.st")
@patch("luxin.components.table_view.render_filters")
@patch("luxin.components.table_view.render_export_buttons")
def test_render_table_view_with_multiindex_reset(mock_export, mock_filters, mock_st):
    """Test render_table_view with MultiIndex that needs reset."""
    agg_df = pd.DataFrame({"value": [30, 70]})
    agg_df.index = pd.MultiIndex.from_tuples(
        [("A", "X"), ("B", "Y")], names=["region", "product"]
    )
    detail_df = pd.DataFrame(
        {
            "region": ["A", "A", "B", "B"],
            "product": ["X", "X", "Y", "Y"],
            "value": [10, 20, 30, 40],
        }
    )
    source_mapping = {("A", "X"): [0, 1], ("B", "Y"): [2, 3]}
    groupby_cols = ["region", "product"]
    config = InspectorConfig()

    mock_st.header = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.session_state = {}
    mock_filters.side_effect = lambda df, key_prefix=None: df

    render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config)

    mock_st.header.assert_called()


@patch("luxin.components.table_view.st")
@patch("luxin.components.table_view.render_filters")
@patch("luxin.components.table_view.render_export_buttons")
def test_render_table_view_selection_with_multiindex(
    mock_export, mock_filters, mock_st
):
    """Test row selection handling with MultiIndex."""
    agg_df = pd.DataFrame({"value": [30, 70]})
    agg_df.index = pd.MultiIndex.from_tuples(
        [("A", "X"), ("B", "Y")], names=["region", "product"]
    )
    detail_df = pd.DataFrame(
        {
            "region": ["A", "A", "B", "B"],
            "product": ["X", "X", "Y", "Y"],
            "value": [10, 20, 30, 40],
        }
    )
    source_mapping = {("A", "X"): [0, 1], ("B", "Y"): [2, 3]}
    groupby_cols = ["region", "product"]
    config = InspectorConfig()

    mock_st.header = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_selection = MagicMock()
    mock_selection.selection.rows = [0]
    mock_st.dataframe = MagicMock(return_value=mock_selection)
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.session_state = {}
    mock_filters.side_effect = lambda df, key_prefix=None: df

    render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config)

    mock_st.dataframe.assert_called()


@patch("luxin.components.table_view._show_row_details")
@patch("luxin.components.table_view.st")
@patch("luxin.components.table_view.render_filters")
@patch("luxin.components.table_view.render_export_buttons")
def test_filtered_selection_uses_visible_group_key(
    mock_export, mock_filters, mock_st, mock_details
):
    """After filtering, first displayed row maps to correct source_mapping key."""
    agg_df = pd.DataFrame(
        {"value": [10, 20, 30]},
        index=pd.Index(["A", "B", "C"], name="category"),
    )
    detail_df = pd.DataFrame(
        {
            "category": list("AABBBCCC"),
            "value": range(8),
        }
    )
    source_mapping = {("A",): [0, 1], ("B",): [2, 3, 4], ("C",): [5, 6, 7]}
    groupby_cols = ["category"]
    config = InspectorConfig()

    def _fake_filter(df, key_prefix=None):
        return df[df["category"] != "A"].reset_index(drop=True)

    mock_st.header = MagicMock()
    col2 = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), col2))
    mock_sel = MagicMock()
    mock_sel.selection.rows = [0]
    mock_st.dataframe = MagicMock(return_value=mock_sel)
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.session_state = {}
    mock_filters.side_effect = _fake_filter

    render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config)

    mock_details.assert_called_once()
    args, _kwargs = mock_details.call_args
    assert args[0] == ("B",)


@patch("luxin.components.table_view.st")
@patch("luxin.components.table_view.render_filters")
@patch("luxin.components.table_view.render_export_buttons")
def test_render_table_view_no_summary_stats(mock_export, mock_filters, mock_st):
    """Test render_table_view with summary stats disabled."""
    agg_df = pd.DataFrame({"category": ["A", "B"], "value": [30, 70]})
    detail_df = pd.DataFrame(
        {"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]}
    )
    source_mapping = {("A",): [0, 1], ("B",): [2, 3]}
    groupby_cols = ["category"]
    config = InspectorConfig(show_summary_stats=False)

    mock_st.header = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
    mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
    mock_st.expander = MagicMock(return_value=MagicMock())
    mock_st.session_state = {}
    mock_filters.side_effect = lambda df, key_prefix=None: df

    render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config)

    # Should not show summary stats
    expander_calls = [call[0][0] for call in mock_st.expander.call_args_list]
    assert "Summary Statistics" not in str(expander_calls)
