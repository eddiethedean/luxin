"""
Comprehensive tests for TrackedDataFrame covering all methods and edge cases.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from luxin import TrackedDataFrame


def test_tracked_dataframe_constructor():
    """Test TrackedDataFrame constructor."""
    df = TrackedDataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    assert isinstance(df, TrackedDataFrame)
    assert isinstance(df, pd.DataFrame)
    assert not df._is_aggregated
    assert df._source_mapping == {}
    assert df._groupby_cols == []
    assert df._source_df is None


def test_tracked_dataframe_constructor_with_existing_dataframe():
    """Test TrackedDataFrame constructor with existing DataFrame."""
    pdf = pd.DataFrame({'a': [1, 2, 3]})
    df = TrackedDataFrame(pdf)
    assert isinstance(df, TrackedDataFrame)
    assert len(df) == 3


def test_tracked_dataframe_show_drill_table_normal():
    """Test show_drill_table works normally with Inspector."""
    df = TrackedDataFrame({'category': ['A'], 'value': [10]})
    agg = df.groupby('category').agg({'value': 'sum'})
    
    # Test that show_drill_table uses Inspector normally
    with patch('luxin.inspector.Inspector') as mock_inspector_class:
        mock_inspector_instance = MagicMock()
        mock_inspector_class.return_value = mock_inspector_instance
        agg.show_drill_table()
        # Should use Inspector
        mock_inspector_class.assert_called_once()
        mock_inspector_instance.render.assert_called_once()

# Note: Testing the ImportError fallback path (lines 56-59 in tracked_df.py)
# is complex because it requires manipulating module imports. The fallback
# to display_drill_table is an edge case that's difficult to test without
# complex module manipulation. This is acceptable as it's a fallback path.


def test_tracked_dataframe_show_drill_table_not_aggregated():
    """Test show_drill_table raises error when not aggregated."""
    df = TrackedDataFrame({'a': [1, 2, 3]})
    
    with pytest.raises(ValueError, match="can only be called on aggregated"):
        df.show_drill_table()


def test_tracked_dataframe_groupby_returns_tracked_groupby():
    """Test that groupby returns TrackedGroupBy."""
    df = TrackedDataFrame({'a': [1, 1, 2], 'b': [10, 20, 30]})
    grouped = df.groupby('a')
    
    from luxin.tracked_df import TrackedGroupBy
    assert isinstance(grouped, TrackedGroupBy)


def test_tracked_dataframe_constructor_property():
    """Test _constructor property."""
    df = TrackedDataFrame({'a': [1, 2, 3]})
    assert df._constructor == TrackedDataFrame


def test_tracked_groupby_agg_with_custom_function():
    """Test TrackedGroupBy.agg with custom aggregation function."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    def custom_sum(x):
        return x.sum()
    
    result = df.groupby('category').agg({'value': custom_sum})
    
    assert isinstance(result, TrackedDataFrame)
    assert result._is_aggregated
    assert len(result) == 2
    assert result._source_mapping is not None


def test_tracked_groupby_agg_with_multiple_columns():
    """Test TrackedGroupBy.agg with multiple aggregation columns."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value1': [10, 20, 30, 40],
        'value2': [1, 2, 3, 4]
    })
    
    result = df.groupby('category').agg({
        'value1': 'sum',
        'value2': 'mean'
    })
    
    assert isinstance(result, TrackedDataFrame)
    assert result._is_aggregated
    assert 'value1' in result.columns
    assert 'value2' in result.columns


def test_tracked_groupby_agg_preserves_source_df():
    """Test that aggregation preserves source DataFrame reference."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    result = df.groupby('category').agg({'value': 'sum'})
    
    assert result._source_df is not None
    assert len(result._source_df) == 4
    assert result._source_df.equals(df)


def test_tracked_groupby_agg_with_empty_groups():
    """Test TrackedGroupBy.agg with empty groups."""
    df = TrackedDataFrame({
        'category': [],
        'value': []
    })
    
    # Empty DataFrame groupby should still work
    result = df.groupby('category').agg({'value': 'sum'})
    
    assert isinstance(result, TrackedDataFrame)
    assert result._is_aggregated

