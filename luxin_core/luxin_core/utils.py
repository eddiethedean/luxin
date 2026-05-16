"""
Utility functions for performance optimization and common operations.
"""

from __future__ import annotations

from datetime import date, datetime
from functools import lru_cache
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# Values are pandas Index labels for rows in the detail (source) frame — not necessarily ints.
DetailIndexLabel = Any

# Mapping from normalized aggregate row keys (typically tuples) to detail row labels.
SourceMapping = Dict[Any, List[DetailIndexLabel]]


@lru_cache(maxsize=128)
def get_cached_index_mapping(df_index: tuple) -> Dict[Any, int]:
    """
    Map tuple index entries to positional indices (LRU cached).

    ``df_index`` must be a tuple of **hashable** index labels (same requirement as storing
    keys in dicts using ``tuple(df.index)``). Passing unhashable elements (for example mutable
    objects) raises ``TypeError``.

    Args:
        df_index: Tuple representation of ordered index labels.

    Returns:
        Dictionary mapping each label to its first position in ``df_index``.
    """
    return {label: pos for pos, label in enumerate(df_index)}


def normalize_group_key_part(x: Any) -> Any:
    """
    Canonicalize one component of a groupby / source-mapping key so dict lookups succeed
    across numpy dtypes, timestamps, python dates, etc.
    """
    if isinstance(x, np.generic):
        if isinstance(x, np.datetime64):
            ts = pd.Timestamp(x)
            if pd.isna(ts):
                return pd.NaT
            return ts
        return x.item()
    if isinstance(x, pd.Timestamp):
        return x
    if isinstance(x, datetime):
        return pd.Timestamp(x)
    if isinstance(x, date):
        return pd.Timestamp(x)
    return x


def normalize_group_key(key: Any) -> tuple:
    """Return a canonical tuple key for ``source_mapping`` / UI selection alignment."""
    if isinstance(key, tuple):
        parts = key
    else:
        parts = (key,)
    return tuple(normalize_group_key_part(p) for p in parts)


def finalize_source_mapping(
    source_mapping: SourceMapping,
) -> SourceMapping:
    """
    Produce a canonical source mapping (normalized keys plus sorted unique label lists).

    Merges numeric/numpy-compatible keys into the same bucket (e.g. ``np.int64(1)``
    resolves with ``1``).

    Args:
        source_mapping: Mapping from aggregated row keys to lists of **detail frame index labels**
            (values passed to ``detail_df.loc[...]``).

    Returns:
        New dictionary with canonical tuple keys and sorted unique labels.

    Note:
        ``sorted(set(v))`` assumes labels within each group are mutually comparable; mixed
        incomparable types in one group can raise ``TypeError``.
    """
    merged: Dict[Any, List[DetailIndexLabel]] = {}
    for key, indices in source_mapping.items():
        nk = normalize_group_key(key)
        merged.setdefault(nk, []).extend(indices)
    return {k: sorted(set(v)) for k, v in merged.items()}


def optimize_source_mapping(
    source_mapping: SourceMapping,
) -> SourceMapping:
    """
    Optimize source mapping by ensuring labels are sorted and unique.

    Args:
        source_mapping: Original source mapping

    Returns:
        Optimized mapping with sorted, unique labels per key
    """
    optimized: Dict[Any, List[DetailIndexLabel]] = {}
    for key, indices in source_mapping.items():
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
        chunks.append(df.iloc[i : i + chunk_size])
    return chunks
