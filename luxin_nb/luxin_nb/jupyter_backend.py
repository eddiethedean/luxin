"""
Jupyter notebook backend for displaying interactive drill-down tables.
"""

import pandas as pd
from typing import Any, Dict, List

from luxin_nb.display import display_drill_table


def display_jupyter(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: Dict[Any, List[int]],
    groupby_cols: List[str],
    **kwargs: Any,
) -> None:
    """Display an interactive drill-down table in Jupyter notebook."""
    display_drill_table(agg_df, detail_df, source_mapping, groupby_cols, **kwargs)


__all__ = ["display_jupyter", "display_drill_table"]
