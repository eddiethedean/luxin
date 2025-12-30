"""
Input validation for luxin APIs.
"""

import pandas as pd
from typing import List, Dict, Any, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_dataframe(df: Any, name: str = "DataFrame") -> None:
    """
    Validate that input is a pandas DataFrame.
    
    Args:
        df: Object to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValidationError: If df is not a pandas DataFrame
    """
    if not isinstance(df, pd.DataFrame):
        raise ValidationError(
            f"{name} must be a pandas DataFrame. "
            f"Got {type(df).__name__}. "
            f"Use TrackedDataFrame or convert your data to pandas DataFrame first."
        )


def validate_non_empty_dataframe(df: pd.DataFrame, name: str = "DataFrame") -> None:
    """
    Validate that DataFrame is not empty.
    
    Args:
        df: DataFrame to validate
        name: Name of the parameter for error messages
        
    Raises:
        ValidationError: If DataFrame is empty
    """
    validate_dataframe(df, name)
    if len(df) == 0:
        raise ValidationError(
            f"{name} is empty. Please provide a DataFrame with at least one row."
        )


def validate_groupby_cols(groupby_cols: List[str], df: pd.DataFrame) -> None:
    """
    Validate that groupby columns exist in DataFrame.
    
    Args:
        groupby_cols: List of column names
        df: DataFrame to check columns against
        
    Raises:
        ValidationError: If any column doesn't exist
    """
    if not isinstance(groupby_cols, list) or len(groupby_cols) == 0:
        raise ValidationError(
            "groupby_cols must be a non-empty list of column names."
        )
    
    missing_cols = [col for col in groupby_cols if col not in df.columns]
    if missing_cols:
        raise ValidationError(
            f"Columns not found in DataFrame: {missing_cols}. "
            f"Available columns: {list(df.columns)}"
        )


def validate_source_mapping(
    source_mapping: Dict[Any, List[int]], 
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame
) -> None:
    """
    Validate source mapping structure and values.
    
    Args:
        source_mapping: Dictionary mapping aggregated row keys to detail row indices
        agg_df: Aggregated DataFrame
        detail_df: Detail DataFrame
        
    Raises:
        ValidationError: If mapping is invalid
    """
    if not isinstance(source_mapping, dict):
        raise ValidationError(
            "source_mapping must be a dictionary mapping aggregated row keys to detail row indices."
        )
    
    if len(source_mapping) == 0:
        raise ValidationError(
            "source_mapping is empty. Ensure aggregation tracking is enabled."
        )
    
    # Check that all indices in mapping are valid
    for key, indices in source_mapping.items():
        if not isinstance(indices, list):
            raise ValidationError(
                f"source_mapping values must be lists of indices. "
                f"Got {type(indices).__name__} for key {key}."
            )
        
        invalid_indices = [idx for idx in indices if idx not in detail_df.index]
        if invalid_indices:
            raise ValidationError(
                f"Invalid indices in source_mapping for key {key}: {invalid_indices}. "
                f"Detail DataFrame has indices: {list(detail_df.index)[:10]}..."
            )


def validate_aggregated_dataframe(df: pd.DataFrame) -> None:
    """
    Validate that DataFrame has aggregation tracking metadata.
    
    Args:
        df: DataFrame to validate
        
    Raises:
        ValidationError: If DataFrame doesn't have aggregation tracking
    """
    if not hasattr(df, '_is_aggregated') or not df._is_aggregated:
        raise ValidationError(
            "DataFrame is not aggregated or doesn't have tracking enabled. "
            "Use TrackedDataFrame.groupby().agg() to create an aggregated DataFrame with tracking."
        )
    
    if not hasattr(df, '_source_mapping') or len(df._source_mapping) == 0:
        raise ValidationError(
            "Aggregated DataFrame has no source mapping. "
            "Ensure aggregation was performed using TrackedDataFrame."
        )
    
    if not hasattr(df, '_source_df') or df._source_df is None:
        raise ValidationError(
            "Aggregated DataFrame has no source DataFrame reference. "
            "Ensure aggregation was performed using TrackedDataFrame."
        )

