"""
Comprehensive tests for utility functions.
"""

import pytest
import pandas as pd
from luxin.utils import get_cached_index_mapping, optimize_source_mapping, chunk_dataframe


def test_get_cached_index_mapping():
    """Test get_cached_index_mapping function."""
    # Test with empty tuple (should return empty dict)
    result = get_cached_index_mapping(())
    assert isinstance(result, dict)
    assert len(result) == 0
    
    # Test with non-empty tuple
    result = get_cached_index_mapping((1, 2, 3))
    assert isinstance(result, dict)
    
    # Test caching (same input should return same object due to lru_cache)
    result1 = get_cached_index_mapping((1, 2, 3))
    result2 = get_cached_index_mapping((1, 2, 3))
    assert result1 is result2


def test_optimize_source_mapping_with_duplicates():
    """Test optimize_source_mapping with duplicate indices."""
    source_mapping = {
        'A': [3, 1, 2, 1, 3],  # Has duplicates
        'B': [5, 4, 5, 6]
    }
    
    optimized = optimize_source_mapping(source_mapping)
    
    assert optimized['A'] == [1, 2, 3]  # Sorted and deduplicated
    assert optimized['B'] == [4, 5, 6]  # Sorted and deduplicated


def test_optimize_source_mapping_empty():
    """Test optimize_source_mapping with empty mapping."""
    result = optimize_source_mapping({})
    assert result == {}


def test_chunk_dataframe_exact_multiple():
    """Test chunk_dataframe when length is exact multiple of chunk_size."""
    df = pd.DataFrame({'a': range(1000)})
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 10
    assert all(len(chunk) == 100 for chunk in chunks)
    assert sum(len(chunk) for chunk in chunks) == 1000


def test_chunk_dataframe_remainder():
    """Test chunk_dataframe with remainder."""
    df = pd.DataFrame({'a': range(250)})
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 3
    assert len(chunks[0]) == 100
    assert len(chunks[1]) == 100
    assert len(chunks[2]) == 50  # Remainder


def test_chunk_dataframe_smaller_than_chunk():
    """Test chunk_dataframe when DataFrame is smaller than chunk_size."""
    df = pd.DataFrame({'a': range(50)})
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 1
    assert len(chunks[0]) == 50


def test_chunk_dataframe_empty():
    """Test chunk_dataframe with empty DataFrame."""
    df = pd.DataFrame()
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 0

