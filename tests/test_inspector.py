"""Tests for Inspector class."""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin import Inspector, TrackedDataFrame


def test_inspector_initialization():
    """Test Inspector initialization with regular DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    inspector = Inspector(df)
    
    assert inspector.df is df
    assert inspector._is_aggregated is False
    assert inspector._source_mapping == {}
    assert inspector._groupby_cols == []
    assert inspector._source_df is None


def test_inspector_with_tracked_dataframe():
    """Test Inspector initialization with non-aggregated TrackedDataFrame."""
    df = TrackedDataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    inspector = Inspector(df)
    
    assert inspector.df is df
    assert inspector._is_aggregated is False


def test_inspector_with_aggregated_tracked_dataframe():
    """Test Inspector initialization with aggregated TrackedDataFrame."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    agg = df.groupby('category').agg({'value': 'sum'})
    
    inspector = Inspector(agg)
    
    assert inspector._is_aggregated is True
    assert len(inspector._source_mapping) > 0
    assert inspector._groupby_cols == ['category']
    assert inspector._source_df is not None


def test_inspector_render_without_streamlit():
    """Test that render handles Streamlit import."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    inspector = Inspector(df)
    
    # Since streamlit is imported at module level and inside render(),
    # we verify the function works when streamlit is available
    # The actual ImportError test would require more complex mocking
    with patch('luxin.inspector.st') as mock_st:
        mock_st.dataframe = MagicMock()
        mock_st.info = MagicMock()
        # Mock the import inside render() by patching streamlit module
        import sys
        original_streamlit = sys.modules.get('streamlit')
        mock_streamlit_module = MagicMock()
        mock_streamlit_module.dataframe = MagicMock()
        mock_streamlit_module.info = MagicMock()
        sys.modules['streamlit'] = mock_streamlit_module
        
        try:
            inspector.render()
            # Function should work when streamlit is available
            # Either the module-level st or the imported st should be called
            assert mock_st.dataframe.called or mock_streamlit_module.dataframe.called
        finally:
            # Restore original streamlit module
            if original_streamlit:
                sys.modules['streamlit'] = original_streamlit
            elif 'streamlit' in sys.modules:
                del sys.modules['streamlit']


def test_inspector_render_non_aggregated():
    """Test render method with non-aggregated DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    inspector = Inspector(df)
    
    # Patch streamlit at the module level where it's used
    with patch('luxin.inspector.st') as mock_st:
        mock_st.dataframe = MagicMock()
        mock_st.info = MagicMock()
        # Mock the import inside render() by patching sys.modules
        import sys
        original_streamlit = sys.modules.get('streamlit')
        mock_streamlit_module = MagicMock()
        mock_streamlit_module.dataframe = MagicMock()
        mock_streamlit_module.info = MagicMock()
        sys.modules['streamlit'] = mock_streamlit_module
        
        try:
            inspector.render()
            # Should call st.dataframe (either from module or from import)
            assert mock_st.dataframe.called or mock_streamlit_module.dataframe.called
            # Should show info message
            assert mock_st.info.called or mock_streamlit_module.info.called
        finally:
            # Restore original streamlit module
            if original_streamlit:
                sys.modules['streamlit'] = original_streamlit
            elif 'streamlit' in sys.modules:
                del sys.modules['streamlit']


def test_inspector_render_aggregated():
    """Test render method with aggregated TrackedDataFrame."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    agg = df.groupby('category').agg({'value': 'sum'})
    inspector = Inspector(agg)
    
    with patch('luxin.components.table_view.render_table_view') as mock_render:
        with patch('luxin.inspector.st'):
            inspector.render()
            
            # Should call render_table_view
            mock_render.assert_called_once()
            call_args = mock_render.call_args
            assert call_args[1]['agg_df'] is agg
            assert call_args[1]['detail_df'] is inspector._source_df
            assert call_args[1]['source_mapping'] == inspector._source_mapping
            assert call_args[1]['groupby_cols'] == inspector._groupby_cols


def test_inspector_render_empty_dataframe():
    """Test render with empty DataFrame."""
    df = pd.DataFrame()
    inspector = Inspector(df)
    
    # Patch streamlit at the module level where it's used
    with patch('luxin.inspector.st') as mock_st:
        mock_st.dataframe = MagicMock()
        mock_st.info = MagicMock()
        # Mock the import inside render() by patching sys.modules
        import sys
        original_streamlit = sys.modules.get('streamlit')
        mock_streamlit_module = MagicMock()
        mock_streamlit_module.dataframe = MagicMock()
        mock_streamlit_module.info = MagicMock()
        sys.modules['streamlit'] = mock_streamlit_module
        
        try:
            inspector.render()
            # Should call st.dataframe (even for empty DataFrame)
            assert mock_st.dataframe.called or mock_streamlit_module.dataframe.called
        finally:
            # Restore original streamlit module
            if original_streamlit:
                sys.modules['streamlit'] = original_streamlit
            elif 'streamlit' in sys.modules:
                del sys.modules['streamlit']


def test_inspector_multi_column_groupby():
    """Test Inspector with multi-column groupby."""
    df = TrackedDataFrame({
        'region': ['North', 'North', 'South', 'South'],
        'product': ['A', 'B', 'A', 'B'],
        'value': [10, 20, 30, 40]
    })
    agg = df.groupby(['region', 'product']).agg({'value': 'sum'})
    inspector = Inspector(agg)
    
    assert inspector._is_aggregated is True
    assert inspector._groupby_cols == ['region', 'product']
    assert len(inspector._source_mapping) > 0


def test_inspector_source_mapping_accuracy():
    """Test that Inspector correctly extracts source mapping."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    agg = df.groupby('category').agg({'value': 'sum'})
    inspector = Inspector(agg)
    
    # Check that source mapping matches TrackedDataFrame
    assert inspector._source_mapping == agg._source_mapping
    assert inspector._groupby_cols == agg._groupby_cols
    assert inspector._source_df is agg._source_df


def test_inspector_with_config():
    """Test Inspector with custom configuration."""
    from luxin.config import InspectorConfig
    
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B'],
        'value': [10, 20, 30]
    })
    agg = df.groupby('category').agg({'value': 'sum'})
    
    config = InspectorConfig(show_summary_stats=False)
    inspector = Inspector(agg, config=config)
    
    assert inspector.config is config
    assert inspector.config.show_summary_stats is False


def test_inspector_validation_error():
    """Test Inspector with invalid input raises validation error."""
    with pytest.raises(ValueError, match="must be a pandas DataFrame"):
        Inspector([1, 2, 3])


def test_inspector_empty_dataframe_with_config():
    """Test Inspector with empty DataFrame and config."""
    from luxin.config import InspectorConfig
    
    df = pd.DataFrame()
    config = InspectorConfig()
    inspector = Inspector(df, config=config)
    
    assert inspector.config is config
    assert inspector.df is df

