"""Integration tests for full workflow."""

import pytest
import pandas as pd
from unittest.mock import patch
from luxin import Inspector, TrackedDataFrame


def test_full_workflow_tracked_dataframe_to_inspector():
    """Test complete workflow from TrackedDataFrame creation to Inspector.render()."""
    # Create TrackedDataFrame
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B', 'C'],
        'sales': [100, 150, 200, 250, 300],
        'profit': [10, 15, 20, 25, 30]
    })
    
    # Aggregate
    agg = df.groupby('category').agg({
        'sales': 'sum',
        'profit': 'sum'
    })
    
    # Verify aggregation tracking
    assert agg._is_aggregated is True
    assert len(agg._source_mapping) == 3
    assert agg._groupby_cols == ['category']
    
    # Create Inspector
    inspector = Inspector(agg)
    
    # Verify Inspector extracted tracking info
    assert inspector._is_aggregated is True
    assert inspector._source_mapping == agg._source_mapping
    assert inspector._groupby_cols == agg._groupby_cols
    assert inspector._source_df is agg._source_df
    
    # Test render (mocked)
    with patch('luxin.components.table_view.render_table_view') as mock_render:
        with patch('luxin.inspector.st'):
            inspector.render()
            mock_render.assert_called_once()


def test_full_workflow_multi_column_groupby():
    """Test complete workflow with multi-column groupby."""
    df = TrackedDataFrame({
        'region': ['North', 'North', 'South', 'South'],
        'product': ['A', 'B', 'A', 'B'],
        'sales': [100, 150, 200, 250]
    })
    
    agg = df.groupby(['region', 'product']).agg({'sales': 'sum'})
    
    assert agg._is_aggregated is True
    assert agg._groupby_cols == ['region', 'product']
    
    inspector = Inspector(agg)
    assert inspector._is_aggregated is True
    assert inspector._groupby_cols == ['region', 'product']


def test_full_workflow_with_custom_aggregations():
    """Test workflow with custom aggregation functions."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    agg = df.groupby('category').agg({
        'value': ['sum', 'mean', 'count']
    })
    
    assert agg._is_aggregated is True
    
    inspector = Inspector(agg)
    assert inspector._is_aggregated is True


def test_workflow_source_mapping_accuracy():
    """Test that source mapping is accurate through the full workflow."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    
    agg = df.groupby('category').agg({'value': 'sum'})
    
    # Verify source mapping
    assert ('A',) in agg._source_mapping
    assert set(agg._source_mapping[('A',)]) == {0, 1}
    assert ('B',) in agg._source_mapping
    assert set(agg._source_mapping[('B',)]) == {2, 3}
    
    # Inspector should preserve this
    inspector = Inspector(agg)
    assert inspector._source_mapping == agg._source_mapping
    
    # Verify detail rows match
    detail_indices_a = inspector._source_mapping[('A',)]
    detail_rows_a = inspector._source_df.loc[detail_indices_a]
    assert len(detail_rows_a) == 2
    assert detail_rows_a['value'].sum() == 30  # 10 + 20


def test_workflow_empty_dataframe():
    """Test workflow with empty DataFrame."""
    df = TrackedDataFrame()
    
    # Should handle empty DataFrame gracefully
    assert len(df) == 0
    
    inspector = Inspector(df)
    assert inspector._is_aggregated is False


def test_workflow_single_row_aggregation():
    """Test workflow with single row result."""
    df = TrackedDataFrame({
        'category': ['A', 'A', 'A'],
        'value': [10, 20, 30]
    })
    
    agg = df.groupby('category').agg({'value': 'sum'})
    
    assert len(agg) == 1
    assert agg._is_aggregated is True
    
    inspector = Inspector(agg)
    assert inspector._is_aggregated is True
    assert len(inspector._source_mapping) == 1


def test_workflow_large_dataset():
    """Test workflow with larger dataset."""
    # Create larger dataset
    data = {
        'category': ['A'] * 50 + ['B'] * 50 + ['C'] * 50,
        'value': list(range(150))
    }
    df = TrackedDataFrame(data)
    
    agg = df.groupby('category').agg({'value': 'sum'})
    
    assert len(agg) == 3
    assert agg._is_aggregated is True
    assert len(agg._source_mapping) == 3
    
    # Each category should map to 50 rows
    for key in agg._source_mapping:
        assert len(agg._source_mapping[key]) == 50
    
    inspector = Inspector(agg)
    assert inspector._is_aggregated is True

