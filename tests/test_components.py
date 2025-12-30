"""Tests for UI components."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.table_view import render_table_view, _show_row_details
from luxin.components.detail_panel import render_detail_panel


def test_render_table_view_basic():
    """Test render_table_view with basic aggregated data."""
    agg_df = pd.DataFrame({
        'category': ['A', 'B'],
        'value': [30, 70]
    })
    agg_df.index = ['A', 'B']
    
    detail_df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    source_mapping = {
        ('A',): [0, 1],
        ('B',): [2, 3]
    }
    groupby_cols = ['category']
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
        mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        mock_st.text_input = MagicMock(return_value="")
        
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols)
        
        # Should call header
        mock_st.header.assert_called()
        # Should call dataframe for table display
        mock_st.dataframe.assert_called()


def test_render_table_view_empty():
    """Test render_table_view with empty DataFrame."""
    agg_df = pd.DataFrame()
    detail_df = pd.DataFrame()
    source_mapping = {}
    groupby_cols = []
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.text_input = MagicMock(return_value="")
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.dataframe = MagicMock()
        
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols)
        
        # Should show warning for empty data
        mock_st.warning.assert_called()


def test_render_table_view_multiindex():
    """Test render_table_view with MultiIndex."""
    agg_df = pd.DataFrame({
        'value': [30, 70]
    })
    agg_df.index = pd.MultiIndex.from_tuples([('A', 'X'), ('B', 'Y')], names=['region', 'product'])
    
    detail_df = pd.DataFrame({
        'region': ['A', 'A', 'B', 'B'],
        'product': ['X', 'X', 'Y', 'Y'],
        'value': [10, 20, 30, 40]
    })
    
    source_mapping = {
        ('A', 'X'): [0, 1],
        ('B', 'Y'): [2, 3]
    }
    groupby_cols = ['region', 'product']
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.header = MagicMock()
        mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock()))
        mock_st.dataframe = MagicMock(return_value=MagicMock(selection=MagicMock(rows=[])))
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.info = MagicMock()
        mock_st.text_input = MagicMock(return_value="")
        
        render_table_view(agg_df, detail_df, source_mapping, groupby_cols)
        
        # Should handle MultiIndex correctly
        mock_st.dataframe.assert_called()


def test_show_row_details():
    """Test _show_row_details function."""
    agg_df = pd.DataFrame({
        'value': [30, 70]
    })
    agg_df.index = ['A', 'B']
    
    detail_df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    source_mapping = {
        ('A',): [0, 1],
        ('B',): [2, 3]
    }
    groupby_cols = ['category']
    
    mock_col = MagicMock()
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        mock_st.warning = MagicMock()
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.json = MagicMock()
        mock_st.download_button = MagicMock()
        mock_st.session_state = {}
        
        from luxin.config import get_default_config
        config = get_default_config()
        
        # Mock render_detail_panel since it's called inside
        with patch('luxin.components.detail_panel.render_detail_panel') as mock_panel:
            _show_row_details(0, agg_df, detail_df, source_mapping, groupby_cols, mock_col, config)
            
            # Should show detail rows via render_detail_panel
            mock_st.subheader.assert_called()
            # render_detail_panel should be called to display the detail rows
            mock_panel.assert_called()


def test_show_row_details_no_mapping():
    """Test _show_row_details when no mapping exists."""
    agg_df = pd.DataFrame({'value': [30]})
    agg_df.index = ['A']
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    source_mapping = {}  # Empty mapping
    groupby_cols = ['category']
    
    mock_col = MagicMock()
    
    with patch('luxin.components.table_view.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.warning = MagicMock()
        
        _show_row_details(0, agg_df, detail_df, source_mapping, groupby_cols, mock_col)
        
        # Should show warning
        mock_st.warning.assert_called()


def test_render_detail_panel():
    """Test render_detail_panel function."""
    detail_rows = pd.DataFrame({
        'category': ['A', 'A'],
        'value': [10, 20]
    })
    
    with patch('luxin.components.detail_panel.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        
        render_detail_panel(detail_rows)
        
        # Should render detail panel
        mock_st.subheader.assert_called()
        mock_st.dataframe.assert_called()


def test_render_detail_panel_custom_title():
    """Test render_detail_panel with custom title."""
    detail_rows = pd.DataFrame({'value': [10, 20]})
    
    with patch('luxin.components.detail_panel.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        
        render_detail_panel(detail_rows, title="Custom Title")
        
        # Should use custom title
        mock_st.subheader.assert_called_with("🔍 Custom Title")


def test_render_detail_panel_empty():
    """Test render_detail_panel with empty DataFrame."""
    detail_rows = pd.DataFrame()
    
    with patch('luxin.components.detail_panel.st') as mock_st:
        mock_st.subheader = MagicMock()
        mock_st.caption = MagicMock()
        mock_st.dataframe = MagicMock()
        
        render_detail_panel(detail_rows)
        
        # Should still render (empty dataframe is valid)
        mock_st.dataframe.assert_called()

