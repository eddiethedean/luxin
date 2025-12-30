"""Tests for utility functions."""

import pytest
import pandas as pd
from luxin.utils import optimize_source_mapping, chunk_dataframe


def test_optimize_source_mapping():
    """Test source mapping optimization."""
    source_mapping = {
        ('A',): [2, 1, 0, 2],  # Has duplicates and unsorted
        ('B',): [3, 4]
    }
    
    optimized = optimize_source_mapping(source_mapping)
    
    # Should be sorted and deduplicated
    assert optimized[('A',)] == [0, 1, 2]
    assert optimized[('B',)] == [3, 4]


def test_optimize_source_mapping_empty():
    """Test optimization with empty mapping."""
    source_mapping = {}
    optimized = optimize_source_mapping(source_mapping)
    
    assert optimized == {}


def test_optimize_source_mapping_already_optimized():
    """Test optimization with already optimized mapping."""
    source_mapping = {
        ('A',): [0, 1, 2],
        ('B',): [3, 4]
    }
    
    optimized = optimize_source_mapping(source_mapping)
    
    # Should remain the same
    assert optimized == source_mapping


def test_chunk_dataframe():
    """Test DataFrame chunking."""
    df = pd.DataFrame({'a': range(2500)})
    chunks = chunk_dataframe(df, chunk_size=1000)
    
    assert len(chunks) == 3
    assert len(chunks[0]) == 1000
    assert len(chunks[1]) == 1000
    assert len(chunks[2]) == 500


def test_chunk_dataframe_small():
    """Test chunking with DataFrame smaller than chunk size."""
    df = pd.DataFrame({'a': range(50)})
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 1
    assert len(chunks[0]) == 50


def test_chunk_dataframe_empty():
    """Test chunking with empty DataFrame."""
    df = pd.DataFrame()
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 0


def test_chunk_dataframe_exact_size():
    """Test chunking with DataFrame exactly matching chunk size."""
    df = pd.DataFrame({'a': range(100)})
    chunks = chunk_dataframe(df, chunk_size=100)
    
    assert len(chunks) == 1
    assert len(chunks[0]) == 100

