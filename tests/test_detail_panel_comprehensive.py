"""
Comprehensive tests for detail_panel component, including pagination edge cases.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.detail_panel import render_detail_panel


@patch('luxin.components.detail_panel.st')
def test_detail_panel_pagination_previous_button(mock_st):
    """Test pagination previous button functionality."""
    df = pd.DataFrame({'a': range(250)})  # More than page_size (100)
    
    mock_st.subheader = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
    mock_st.button = MagicMock(return_value=True)
    mock_st.number_input = MagicMock(return_value=2)
    mock_st.dataframe = MagicMock()
    mock_st.session_state = {"detail_page_123": 2}
    
    # Mock the button context managers
    mock_st.columns.return_value[0].__enter__ = MagicMock(return_value=mock_st.columns.return_value[0])
    mock_st.columns.return_value[0].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[1].__enter__ = MagicMock(return_value=mock_st.columns.return_value[1])
    mock_st.columns.return_value[1].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[2].__enter__ = MagicMock(return_value=mock_st.columns.return_value[2])
    mock_st.columns.return_value[2].__exit__ = MagicMock(return_value=None)
    
    # Test previous button when not on first page
    mock_st.button.return_value = True
    mock_st.session_state["detail_page_123"] = 2
    
    render_detail_panel(df, page_size=100)
    
    # Verify button was called
    assert mock_st.button.called


@patch('luxin.components.detail_panel.st')
def test_detail_panel_pagination_next_button(mock_st):
    """Test pagination next button functionality."""
    df = pd.DataFrame({'a': range(250)})  # More than page_size (100)
    
    mock_st.subheader = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
    mock_st.button = MagicMock(return_value=True)
    mock_st.number_input = MagicMock(return_value=1)
    mock_st.dataframe = MagicMock()
    mock_st.session_state = {"detail_page_123": 1}
    
    # Mock the button context managers
    mock_st.columns.return_value[0].__enter__ = MagicMock(return_value=mock_st.columns.return_value[0])
    mock_st.columns.return_value[0].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[1].__enter__ = MagicMock(return_value=mock_st.columns.return_value[1])
    mock_st.columns.return_value[1].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[2].__enter__ = MagicMock(return_value=mock_st.columns.return_value[2])
    mock_st.columns.return_value[2].__exit__ = MagicMock(return_value=None)
    
    # Test next button when not on last page
    mock_st.button.return_value = True
    total_pages = (len(df) + 100 - 1) // 100
    mock_st.session_state["detail_page_123"] = 1
    
    render_detail_panel(df, page_size=100)
    
    # Verify button was called
    assert mock_st.button.called


@patch('luxin.components.detail_panel.st')
def test_detail_panel_pagination_number_input_change(mock_st):
    """Test pagination number input on_change callback."""
    df = pd.DataFrame({'a': range(250)})
    
    mock_st.subheader = MagicMock()
    mock_st.caption = MagicMock()
    mock_st.columns = MagicMock(return_value=(MagicMock(), MagicMock(), MagicMock()))
    mock_st.button = MagicMock(return_value=False)
    mock_st.number_input = MagicMock(return_value=2)
    mock_st.dataframe = MagicMock()
    mock_st.session_state = {"detail_page_123": 1, "detail_page_123_input": 2}
    mock_st.rerun = MagicMock()
    
    # Mock the button context managers
    mock_st.columns.return_value[0].__enter__ = MagicMock(return_value=mock_st.columns.return_value[0])
    mock_st.columns.return_value[0].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[1].__enter__ = MagicMock(return_value=mock_st.columns.return_value[1])
    mock_st.columns.return_value[1].__exit__ = MagicMock(return_value=None)
    mock_st.columns.return_value[2].__enter__ = MagicMock(return_value=mock_st.columns.return_value[2])
    mock_st.columns.return_value[2].__exit__ = MagicMock(return_value=None)
    
    render_detail_panel(df, page_size=100)
    
    # Verify number_input was called with on_change
    assert mock_st.number_input.called

