"""
Polars DataFrame support for luxin.
"""

from typing import Any, Dict, List, Optional, Union
import pandas as pd

try:
    import polars as pl
    POLARS_AVAILABLE = True
except ImportError:
    POLARS_AVAILABLE = False
    pl = None


def convert_polars_to_pandas(df: Union[pl.DataFrame, pd.DataFrame]) -> pd.DataFrame:
    """
    Convert Polars DataFrame to pandas DataFrame.
    
    Args:
        df: Polars or pandas DataFrame
        
    Returns:
        pandas DataFrame
    """
    if isinstance(df, pd.DataFrame):
        return df
    
    if not POLARS_AVAILABLE:
        raise ImportError(
            "Polars is not installed. Install with: pip install polars"
        )
    
    if isinstance(df, pl.DataFrame):
        return df.to_pandas()
    
    raise TypeError(f"Expected Polars or pandas DataFrame, got {type(df)}")


def create_tracked_from_polars(df: pl.DataFrame) -> pd.DataFrame:
    """
    Create a TrackedDataFrame from a Polars DataFrame.
    
    Args:
        df: Polars DataFrame
        
    Returns:
        TrackedDataFrame (pandas-based)
    """
    from luxin.tracked_df import TrackedDataFrame
    
    if not POLARS_AVAILABLE:
        raise ImportError(
            "Polars is not installed. Install with: pip install polars"
        )
    
    pandas_df = df.to_pandas()
    return TrackedDataFrame(pandas_df)


def is_polars_dataframe(df: Any) -> bool:
    """
    Check if object is a Polars DataFrame.
    
    Args:
        df: Object to check
        
    Returns:
        True if Polars DataFrame, False otherwise
    """
    if not POLARS_AVAILABLE:
        return False
    
    return isinstance(df, pl.DataFrame)


def handle_polars_in_inspector(df: Union[pl.DataFrame, pd.DataFrame]) -> pd.DataFrame:
    """
    Handle Polars DataFrame in Inspector by converting to pandas.
    
    Args:
        df: Polars or pandas DataFrame
        
    Returns:
        pandas DataFrame
    """
    if is_polars_dataframe(df):
        return convert_polars_to_pandas(df)
    return df

