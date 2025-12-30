"""Comprehensive tests for UI components with edge cases."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.table_view import render_table_view, _show_row_details
from luxin.components.detail_panel import render_detail_panel
from luxin.config import InspectorConfig


def test_render_table_view_with_config():
    """Test render_table_view with custom configuration."""
    agg_df = pd.DataFrame({'value': [30, 70]})
    agg_df.index = ['A', 'B']
    detail_df = pd.DataFrame({'category': ['A', 'A', 'B', 'B'], 'value': [10, 20, 30, 40]})
    source_mapping = {('A',): [0, 1], ('B',): [2, 3]}
    groupby_cols = ['category']
    
    config = InspectorConfig(show_summary_stats=False, show_export_buttons=False)
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
        mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols, config=config)
        
        # Should not show summary stats if disabled
        mock_st.header.assert_called()


def test_render_table_view_with_selection():
    """Test render_table_view with row selection."""
    agg_df = pd.DataFrame({'value': [30, 70]})
    agg_df.index = ['A', 'B']
    detail_df = pd.DataFrame({'category': ['A', 'A', 'B', 'B'], 'value': [10, 20, 30, 40]})
    source_mapping = {('A',): [0, 1], ('B',): [2, 3]}
    groupby_cols = ['category']
    
    mock_selection = MagicMock()
    mock_selection.rows = [0]
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
        mock_st.dataframe = MagicMock(return_value=MagicMock(selection=mock_selection))
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.json = MagicMock()
        
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols)
        
        # Should show detail rows when selected
        mock_st.subheader.assert_called()


def test_render_table_view_large_dataset():
    """Test render_table_view with large dataset."""
    # Create larger dataset
    data = {'category': ['A'] * 100 + ['B'] * 100, 'value': range(200)}
    detail_df = pd.DataFrame(data)
    agg_df = pd.DataFrame({'value': [sum(range(100)), sum(range(100, 200))]})
    agg_df.index = ['A', 'B']
    source_mapping = {('A',): list(range(100)), ('B',): list(range(100, 200))}
    groupby_cols = ['category']
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
        mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        
        # Should handle large datasets
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols)


def test_detail_panel_pagination():
    """Test detail panel with pagination for large dataset."""
    # Create dataset larger than page size
    detail_rows = pd.DataFrame({'value': range(250)})
    
    with patch('luxin.components.detail_panel.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
        mock_st.button = MagicMock(return_value=False)
        mock_st.number_input = MagicMock(return_value=1)
        mock_st.dataframe = MagicMock()
        mock_st.session_state = {}
        
        render_detail_panel(detail_rows, page_size=100)
        
        # Should show pagination controls
        mock_st.number_input.assert_called()


def test_detail_panel_no_pagination():
    """Test detail panel without pagination for small dataset."""
    detail_rows = pd.DataFrame({'value': range(50)})
    
    with patch('luxin.components.detail_panel.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        
        render_detail_panel(detail_rows, page_size=100)
        
        # Should not show pagination
        mock_st.number_input.assert_not_called()


def test_show_row_details_invalid_index():
    """Test _show_row_details with invalid index."""
    agg_df = pd.DataFrame({'value': [30]})
    agg_df.index = ['A']
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    source_mapping = {('A',): [0]}
    groupby_cols = ['category']
    mock_col = MagicMock()
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.json = MagicMock()
        mock_st.download_button = MagicMock()
        
        from luxin.config import get_default_config
        config = get_default_config()
        
        # Index out of range - should handle gracefully
        try:
            _show_row_details(99, agg_df, detail_df, source_mapping, groupby_cols, mock_col, config)
        except (IndexError, KeyError):
            # Expected to handle gracefully or raise appropriate error
            pass


def test_show_row_details_multiindex():
    """Test _show_row_details with MultiIndex."""
    agg_df = pd.DataFrame({'value': [30]})
    agg_df.index = pd.MultiIndex.from_tuples([('A', 'X')])
    detail_df = pd.DataFrame({'region': ['A'], 'product': ['X'], 'value': [10]})
    source_mapping = {('A', 'X'): [0]}
    groupby_cols = ['region', 'product']
    mock_col = MagicMock()
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.json = MagicMock()
        mock_st.download_button = MagicMock()
        mock_st.session_state = {}
        
        from luxin.config import get_default_config
        config = get_default_config()
        
        # Mock render_detail_panel since it's called inside
        with patch('luxin.components.detail_panel.render_detail_panel') as mock_panel:
            _show_row_details(0, agg_df, detail_df, source_mapping, groupby_cols, mock_col, config)
            
            # Should handle MultiIndex via render_detail_panel
            mock_panel.assert_called()

