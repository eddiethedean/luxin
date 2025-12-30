"""
Utility functions for performance optimization and common operations.
"""

import pandas as pd
from typing import List, Dict, Any, Optional
from functools import lru_cache


@lru_cache(maxsize=128)
def get_cached_index_mapping(df_index: tuple) -> Dict[Any, int]:
    """
    Cache index to position mapping for faster lookups.
    
    Args:
        df_index: Tuple representation of DataFrame index
        
    Returns:
        Dictionary mapping index values to positions
    """
    # This is a placeholder for caching index lookups
    # In practice, we'd convert the index to a hashable format
    return {}


def optimize_source_mapping(source_mapping: Dict[Any, List[int]]) -> Dict[Any, List[int]]:
    """
    Optimize source mapping by ensuring indices are sorted and unique.
    
    Args:
        source_mapping: Original source mapping
        
    Returns:
        Optimized source mapping with sorted, unique indices
    """
    optimized = {}
    for key, indices in source_mapping.items():
        # Remove duplicates and sort for faster lookups
        optimized[key] = sorted(set(indices))
    return optimized


def chunk_dataframe(df: pd.DataFrame, chunk_size: int = 1000) -> List[pd.DataFrame]:
    """
    Split DataFrame into chunks for lazy loading.
    
    Args:
        df: DataFrame to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of DataFrame chunks
    """
    chunks = []
    for i in range(0, len(df), chunk_size):
        chunks.append(df.iloc[i:i + chunk_size])
    return chunks

