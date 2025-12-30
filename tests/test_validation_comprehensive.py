"""
Comprehensive tests for validation functions, including edge cases.
"""

import pytest
import pandas as pd
from luxin.validation import (
    ValidationError,
    validate_aggregated_dataframe,
    validate_dataframe,
    validate_non_empty_dataframe
)
from luxin import TrackedDataFrame


def test_validate_aggregated_dataframe_no_source_df():
    """Test validate_aggregated_dataframe when source_df is None."""
    df = TrackedDataFrame({'a': [1, 2, 3]})
    agg = df.groupby('a').agg({'a': 'count'})
    
    # Manually remove _source_df to test validation
    agg._source_df = None
    
    with pytest.raises(ValidationError, match="no source DataFrame reference"):
        validate_aggregated_dataframe(agg)


def test_validate_aggregated_dataframe_missing_source_df_attribute():
    """Test validate_aggregated_dataframe when _source_df attribute doesn't exist."""
    df = TrackedDataFrame({'a': [1, 2, 3]})
    agg = df.groupby('a').agg({'a': 'count'})
    
    # Remove the attribute entirely
    del agg._source_df
    
    with pytest.raises(ValidationError, match="no source DataFrame reference"):
        validate_aggregated_dataframe(agg)


def test_validate_dataframe_with_tracked_dataframe():
    """Test validate_dataframe accepts TrackedDataFrame."""
    df = TrackedDataFrame({'a': [1, 2, 3]})
    # Should not raise
    validate_dataframe(df, "test_df")


def test_validate_non_empty_dataframe_with_data():
    """Test validate_non_empty_dataframe with data."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    # Should not raise
    validate_non_empty_dataframe(df, "test_df")

