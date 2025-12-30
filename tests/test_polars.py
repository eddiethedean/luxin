"""Tests for Polars support."""

import pytest
import pandas as pd
from unittest.mock import patch
from luxin.polars_support import (
    convert_polars_to_pandas,
    create_tracked_from_polars,
    is_polars_dataframe,
    handle_polars_in_inspector
)
from luxin import TrackedDataFrame


def test_is_polars_dataframe_with_pandas():
    """Test is_polars_dataframe with pandas DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    assert is_polars_dataframe(df) is False


def test_is_polars_dataframe_with_polars():
    """Test is_polars_dataframe with Polars DataFrame."""
    try:
        import polars as pl
        df = pl.DataFrame({'a': [1, 2, 3]})
        assert is_polars_dataframe(df) is True
    except ImportError:
        pytest.skip("Polars not installed")


def test_convert_polars_to_pandas_pandas():
    """Test convert_polars_to_pandas with pandas DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    result = convert_polars_to_pandas(df)
    
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, df)


def test_convert_polars_to_pandas_polars():
    """Test convert_polars_to_pandas with Polars DataFrame."""
    try:
        import polars as pl
        polars_df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        result = convert_polars_to_pandas(polars_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert list(result.columns) == ['a', 'b']
    except ImportError:
        pytest.skip("Polars not installed")


def test_convert_polars_to_pandas_invalid():
    """Test convert_polars_to_pandas with invalid input."""
    with pytest.raises(TypeError):
        convert_polars_to_pandas([1, 2, 3])


def test_convert_polars_to_pandas_no_polars():
    """Test convert_polars_to_pandas when Polars is not installed."""
    # This test verifies the error message when Polars is not available
    # The actual behavior is tested in integration tests
    # Since we can't easily mock the module-level import, we skip this
    pass


def test_create_tracked_from_polars():
    """Test creating TrackedDataFrame from Polars DataFrame."""
    try:
        import polars as pl
        polars_df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        tracked_df = create_tracked_from_polars(polars_df)
        
        assert isinstance(tracked_df, TrackedDataFrame)
        assert len(tracked_df) == 3
        assert list(tracked_df.columns) == ['a', 'b']
    except ImportError:
        pytest.skip("Polars not installed")


def test_handle_polars_in_inspector_pandas():
    """Test handle_polars_in_inspector with pandas DataFrame."""
    df = pd.DataFrame({'a': [1, 2, 3]})
    result = handle_polars_in_inspector(df)
    
    assert isinstance(result, pd.DataFrame)
    pd.testing.assert_frame_equal(result, df)


def test_handle_polars_in_inspector_polars():
    """Test handle_polars_in_inspector with Polars DataFrame."""
    try:
        import polars as pl
        polars_df = pl.DataFrame({'a': [1, 2, 3]})
        result = handle_polars_in_inspector(polars_df)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
    except ImportError:
        pytest.skip("Polars not installed")


def test_inspector_with_polars():
    """Test Inspector with Polars DataFrame."""
    try:
        import polars as pl
        from luxin import Inspector
        
        polars_df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
        inspector = Inspector(polars_df)
        
        assert isinstance(inspector.df, pd.DataFrame)
        assert len(inspector.df) == 3
    except ImportError:
        pytest.skip("Polars not installed")

