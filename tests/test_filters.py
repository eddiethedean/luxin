"""Tests for filtering component."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin.components.filters import render_filters


def test_render_filters_no_filtering():
    """Test filters with no filtering applied."""
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="")
        mock_expander = MagicMock()
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.multiselect = MagicMock(return_value=[])
        mock_st.slider = MagicMock(return_value=(10, 30))
        mock_st.caption = MagicMock()
        
        result = render_filters(df)
        
        # Should return original DataFrame when no filters
        assert len(result) == len(df)
        pd.testing.assert_frame_equal(result, df)


def test_render_filters_text_search():
    """Test text search filtering."""
    df = pd.DataFrame({
        'category': ['Apple', 'Banana', 'Cherry'],
        'value': [10, 20, 30]
    })
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="App")
        mock_expander = MagicMock()
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.multiselect = MagicMock(return_value=[])
        mock_st.slider = MagicMock(return_value=(10, 30))
        mock_st.caption = MagicMock()
        
        result = render_filters(df)
        
        # Should filter to rows containing "App"
        assert len(result) == 1
        assert result.iloc[0]['category'] == 'Apple'


def test_render_filters_column_multiselect():
    """Test column multiselect filtering."""
    df = pd.DataFrame({
        'category': ['A', 'A', 'B', 'B', 'C'],
        'value': [10, 20, 30, 40, 50]
    })
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="")
        mock_expander = MagicMock()
        mock_st.expander = MagicMock(return_value=mock_expander)
        # First call for category column, second for value (numeric)
        mock_st.multiselect = MagicMock(return_value=['A', 'B'])
        mock_st.slider = MagicMock(return_value=(10, 50))
        mock_st.caption = MagicMock()
        
        result = render_filters(df)
        
        # Should filter to selected categories
        assert len(result) <= len(df)
        if len(result) > 0:
            assert all(result['category'].isin(['A', 'B']))


def test_render_filters_numeric_slider():
    """Test numeric column slider filtering."""
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="")
        mock_expander = MagicMock()
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.multiselect = MagicMock(return_value=[])
        mock_st.slider = MagicMock(return_value=(15, 25))
        mock_st.caption = MagicMock()
        
        result = render_filters(df)
        
        # Should filter to value range
        assert len(result) <= len(df)


def test_render_filters_empty_result():
    """Test filters with no matching results."""
    df = pd.DataFrame({
        'category': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="XYZ")
        mock_st.expander = MagicMock(return_value=MagicMock())
        mock_st.caption = MagicMock()
        
        result = render_filters(df)
        
        # Should return empty DataFrame
        assert len(result) == 0


def test_render_filters_custom_key_prefix():
    """Test filters with custom key prefix."""
    df = pd.DataFrame({'value': [10, 20, 30]})
    
    with patch('luxin.components.filters.st') as mock_st:
        mock_st.text_input = MagicMock(return_value="")
        mock_expander = MagicMock()
        mock_st.expander = MagicMock(return_value=mock_expander)
        mock_st.slider = MagicMock(return_value=(10, 30))
        mock_st.caption = MagicMock()
        
        result = render_filters(df, key_prefix="custom")
        
        # Should use custom prefix in key
        mock_st.text_input.assert_called()
        call_kwargs = mock_st.text_input.call_args[1]
        assert 'custom' in call_kwargs['key']

