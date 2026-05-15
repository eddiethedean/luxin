"""
Tests for edge cases in Polars support, including error handling.
"""

import importlib.util

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


def test_convert_polars_to_pandas_no_polars_installed():
    """Test convert_polars_to_pandas when Polars is not installed."""
    with patch("luxin.polars_support.POLARS_AVAILABLE", False):
        from luxin.polars_support import convert_polars_to_pandas

        # Type appears to be from polars.* → guide user to install the optional extra
        class _FakePolarsFrame:
            pass

        _FakePolarsFrame.__module__ = "polars.dataframe.frame"
        with pytest.raises(ImportError, match="Polars is not installed"):
            convert_polars_to_pandas(_FakePolarsFrame())

        # Generic non-pandas value → TypeError (not ImportError), same as invalid lists
        with pytest.raises(TypeError, match="Expected Polars or pandas"):
            convert_polars_to_pandas(MagicMock())


def test_create_tracked_from_polars_no_polars_installed():
    """Test create_tracked_from_polars when Polars is not installed."""
    with patch("luxin.polars_support.POLARS_AVAILABLE", False):
        from luxin.polars_support import create_tracked_from_polars

        with pytest.raises(ImportError, match="Polars is not installed"):
            create_tracked_from_polars(MagicMock())


def test_convert_polars_to_pandas_invalid_type():
    """Test convert_polars_to_pandas with invalid type."""
    from luxin.polars_support import convert_polars_to_pandas

    # Test with pandas DataFrame (should work)
    df = pd.DataFrame({"a": [1, 2, 3]})
    result = convert_polars_to_pandas(df)
    assert isinstance(result, pd.DataFrame)

    # Test with invalid type when Polars is available
    if importlib.util.find_spec("polars") is not None:
        with pytest.raises(TypeError, match="Expected Polars or pandas DataFrame"):
            convert_polars_to_pandas([1, 2, 3])  # Invalid type


def test_is_polars_dataframe_no_polars():
    """Test is_polars_dataframe when Polars is not installed."""
    with patch("luxin.polars_support.POLARS_AVAILABLE", False):
        from luxin.polars_support import is_polars_dataframe

        # Should return False when Polars not available
        assert is_polars_dataframe(pd.DataFrame({"a": [1]})) is False
        assert is_polars_dataframe([1, 2, 3]) is False


def test_handle_polars_in_inspector_with_polars():
    """Test handle_polars_in_inspector with actual Polars DataFrame."""
    if importlib.util.find_spec("polars") is None:
        pytest.skip("Polars not installed")

    import polars as pl

    from luxin.polars_support import handle_polars_in_inspector

    # Create a Polars DataFrame
    pl_df = pl.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

    # Should convert to pandas
    result = handle_polars_in_inspector(pl_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert list(result.columns) == ["a", "b"]
