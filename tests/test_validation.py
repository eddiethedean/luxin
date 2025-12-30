"""Tests for input validation."""

import pytest
import pandas as pd
from luxin.validation import (
    ValidationError,
    validate_dataframe,
    validate_non_empty_dataframe,
    validate_groupby_cols,
    validate_source_mapping,
    validate_aggregated_dataframe
)
from luxin import TrackedDataFrame


def test_validate_dataframe_valid():
    """Test validation with valid DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    # Should not raise
    validate_dataframe(df)


def test_validate_dataframe_invalid():
    """Test validation with invalid input."""
    with pytest.raises(ValidationError, match="must be a pandas DataFrame"):
        validate_dataframe([1, 2, 3])


def test_validate_dataframe_list():
    """Test validation with list."""
    with pytest.raises(ValidationError):
        validate_dataframe([1, 2, 3])


def test_validate_dataframe_dict():
    """Test validation with dict."""
    with pytest.raises(ValidationError):
        validate_dataframe({'a': [1, 2, 3]})


def test_validate_non_empty_dataframe_valid():
    """Test validation with non-empty DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    # Should not raise
    validate_non_empty_dataframe(df)


def test_validate_non_empty_dataframe_empty():
    """Test validation with empty DataFrame."""
    df = pd.DataFrame()
    with pytest.raises(ValidationError, match="is empty"):
        validate_non_empty_dataframe(df)


def test_validate_groupby_cols_valid():
    """Test validation with valid groupby columns."""
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    # Should not raise
    validate_groupby_cols(['a'], df)


def test_validate_groupby_cols_missing():
    """Test validation with missing column."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    with pytest.raises(ValidationError, match="not found"):
        validate_groupby_cols(['b'], df)


def test_validate_groupby_cols_empty():
    """Test validation with empty groupby columns."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    with pytest.raises(ValidationError, match="non-empty list"):
        validate_groupby_cols([], df)


def test_validate_groupby_cols_not_list():
    """Test validation with non-list input."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    with pytest.raises(ValidationError):
        validate_groupby_cols('a', df)


def test_validate_source_mapping_valid():
    """Test validation with valid source mapping."""
    agg_df = pd.DataFrame({'value': [30]})
    agg_df.index = ['A']
    detail_df = pd.DataFrame({'category': ['A', 'A'], 'value': [10, 20]})
    source_mapping = {('A',): [0, 1]}
    
    # Should not raise
    validate_source_mapping(source_mapping, agg_df, detail_df)


def test_validate_source_mapping_empty():
    """Test validation with empty source mapping."""
    agg_df = pd.DataFrame({'value': [30]})
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    
    with pytest.raises(ValidationError, match="is empty"):
        validate_source_mapping({}, agg_df, detail_df)


def test_validate_source_mapping_not_dict():
    """Test validation with non-dict input."""
    agg_df = pd.DataFrame({'value': [30]})
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    
    with pytest.raises(ValidationError, match="must be a dictionary"):
        validate_source_mapping([], agg_df, detail_df)


def test_validate_source_mapping_invalid_indices():
    """Test validation with invalid indices."""
    agg_df = pd.DataFrame({'value': [30]})
    agg_df.index = ['A']
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    # Index 99 doesn't exist
    source_mapping = {('A',): [0, 99]}
    
    with pytest.raises(ValidationError, match="Invalid indices"):
        validate_source_mapping(source_mapping, agg_df, detail_df)


def test_validate_source_mapping_invalid_value_type():
    """Test validation with invalid value type in mapping."""
    agg_df = pd.DataFrame({'value': [30]})
    detail_df = pd.DataFrame({'category': ['A'], 'value': [10]})
    # Value should be list, not string
    source_mapping = {('A',): "invalid"}
    
    with pytest.raises(ValidationError, match="must be lists"):
        validate_source_mapping(source_mapping, agg_df, detail_df)


def test_validate_aggregated_dataframe_valid():
    """Test validation with valid aggregated DataFrame."""
    df = TrackedDataFrame({'category': ['A', 'A'], 'value': [10, 20]})
    agg = df.groupby('category').agg({'value': 'sum'})
    
    # Should not raise
    validate_aggregated_dataframe(agg)


def test_validate_aggregated_dataframe_not_aggregated():
    """Test validation with non-aggregated DataFrame."""
    df = pd.DataFrame({'category': ['A', 'A'], 'value': [10, 20]})
    
    with pytest.raises(ValidationError, match="not aggregated"):
        validate_aggregated_dataframe(df)


def test_validate_aggregated_dataframe_no_mapping():
    """Test validation with aggregated DataFrame but no mapping."""
    df = TrackedDataFrame({'category': ['A', 'A'], 'value': [10, 20]})
    agg = df.groupby('category').agg({'value': 'sum'})
    # Manually clear mapping
    agg._source_mapping = {}
    
    with pytest.raises(ValidationError, match="no source mapping"):
        validate_aggregated_dataframe(agg)

