"""
Tests for edge cases in Polars support, including error handling.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock


def test_convert_polars_to_pandas_no_polars_installed():
    """Test convert_polars_to_pandas when Polars is not installed."""
    # Mock POLARS_AVAILABLE = False
    with patch('luxin.polars_support.POLARS_AVAILABLE', False):
        with patch('luxin.polars_support.pl', None):
            from luxin.polars_support import convert_polars_to_pandas
            
            # Should raise ImportError for non-pandas DataFrame when Polars not available
            with pytest.raises(ImportError, match="Polars is not installed"):
                convert_polars_to_pandas(MagicMock())  # Mock non-pandas, non-polars object


def test_create_tracked_from_polars_no_polars_installed():
    """Test create_tracked_from_polars when Polars is not installed."""
    with patch('luxin.polars_support.POLARS_AVAILABLE', False):
        with patch('luxin.polars_support.pl', None):
            from luxin.polars_support import create_tracked_from_polars
            
            with pytest.raises(ImportError, match="Polars is not installed"):
                create_tracked_from_polars(MagicMock())


def test_convert_polars_to_pandas_invalid_type():
    """Test convert_polars_to_pandas with invalid type."""
    from luxin.polars_support import convert_polars_to_pandas
    
    # Test with pandas DataFrame (should work)
    df = pd.DataFrame({'a': [1, 2, 3]})
    result = convert_polars_to_pandas(df)
    assert isinstance(result, pd.DataFrame)
    
    # Test with invalid type when Polars is available
    try:
        import polars as pl
        POLARS_AVAILABLE = True
    except ImportError:
        POLARS_AVAILABLE = False
    
    if POLARS_AVAILABLE:
        with pytest.raises(TypeError, match="Expected Polars or pandas DataFrame"):
            convert_polars_to_pandas([1, 2, 3])  # Invalid type


def test_is_polars_dataframe_no_polars():
    """Test is_polars_dataframe when Polars is not installed."""
    with patch('luxin.polars_support.POLARS_AVAILABLE', False):
        from luxin.polars_support import is_polars_dataframe
        
        # Should return False when Polars not available
        assert is_polars_dataframe(pd.DataFrame({'a': [1]})) is False
        assert is_polars_dataframe([1, 2, 3]) is False


def test_handle_polars_in_inspector_with_polars():
    """Test handle_polars_in_inspector with actual Polars DataFrame."""
    try:
        import polars as pl
        POLARS_AVAILABLE = True
    except ImportError:
        pytest.skip("Polars not installed")
    
    from luxin.polars_support import handle_polars_in_inspector
    
    # Create a Polars DataFrame
    pl_df = pl.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    
    # Should convert to pandas
    result = handle_polars_in_inspector(pl_df)
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    assert list(result.columns) == ['a', 'b']

