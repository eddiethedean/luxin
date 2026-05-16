"""
TrackedDataFrame - A pandas DataFrame subclass that tracks source rows during aggregations.
"""

import pandas as pd
from typing import Any, Dict, List, Optional, cast

from luxin_core.utils import DetailIndexLabel


def _normalize_groupby_columns(by) -> List[str]:
    """
    Normalize ``pandas.DataFrame.groupby(by=...)`` column arguments for tracked groupby.

    Only plain column-name groupers are supported (no ``pd.Grouper``, callables, or
    level-only groupby).
    """
    if by is None:
        raise NotImplementedError(
            "TrackedDataFrame.groupby requires a non-None `by` (column name(s)). "
            "For level-only groupby, use pandas then create_drill_table()."
        )
    if isinstance(by, str):
        cols = [by]
    elif (
        hasattr(by, "tolist")
        and callable(getattr(by, "tolist"))
        and not isinstance(by, (list, tuple))
    ):  # type: ignore[unreachable]
        cols = [x for x in by.tolist()]  # type: ignore[union-attr]
    elif isinstance(by, tuple):
        cols = list(by)
    elif isinstance(by, list):
        cols = list(by)
    else:
        raise NotImplementedError(
            "TrackedDataFrame.groupby only supports column names as str, list[str], tuple[str, ...], "
            "or a 1d ndarray of strings. Grouper/time-based groupers are not supported. "
            f"Got type {type(by).__name__!r}."
        )
    if not cols:
        raise NotImplementedError(
            "TrackedDataFrame.groupby requires at least one column name."
        )
    if not all(isinstance(x, str) for x in cols):
        raise NotImplementedError(
            "TrackedDataFrame.groupby only supports grouping by column name strings."
        )
    return cast(List[str], cols)


class TrackedDataFrame(pd.DataFrame):
    """
    A pandas DataFrame subclass that automatically tracks which source rows
    contribute to each aggregated row during groupby operations.

    Only specific reductions on :class:`TrackedGroupBy` preserve lineage (mapping back to
    rows in the pre-aggregate frame): ``agg(...)``, ``sum``, ``mean``, ``count``, ``min``,
    ``max``, ``std``, ``var``, and ``median``. Other pandas GroupBy APIs (e.g. ``apply``,
    ``transform``, ``pipe``) are disabled because they do not produce tracked aggregates.

    Attributes:
        _source_mapping: Maps aggregated row keys (tuples) to lists of **index labels** in
            ``_source_df`` (suitable for ``_source_df.loc[labels]``).
        _is_aggregated: Boolean indicating if this DataFrame is an aggregation result
        _groupby_cols: List of column names used in the groupby operation
    """

    _metadata = ["_source_mapping", "_is_aggregated", "_groupby_cols", "_source_df"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._source_mapping: Dict[Any, List[DetailIndexLabel]] = {}
        self._is_aggregated = False
        self._groupby_cols: List[str] = []
        self._source_df: Optional[pd.DataFrame] = None

    @property
    def _constructor(self):
        return TrackedDataFrame

    def groupby(self, by=None, **kwargs):  # ty: ignore[invalid-method-override]
        """Override groupby to return a TrackedGroupBy object."""
        return TrackedGroupBy(self, by, **kwargs)

    def show_drill_table(self):
        """
        Display the interactive drill-down table.

        .. deprecated:: 0.2.0
            Use ``Inspector(df).render()`` (Streamlit, ``luxin`` package) instead.
        """
        if not self._is_aggregated:
            raise ValueError(
                "show_drill_table() can only be called on aggregated DataFrames. "
                "Use groupby().agg() first, or use Inspector(df).render() for the new API."
            )

        try:
            from luxin.inspector import Inspector
        except ModuleNotFoundError as exc:
            if getattr(exc, "name", "") not in ("luxin", "luxin.inspector", None):
                raise
        else:
            inspector = Inspector(self)
            inspector.render()
            return

        if self._source_df is None:
            raise ValueError(
                "show_drill_table() requires aggregation metadata including `_source_df`."
            )

        try:
            from luxin_nb.display import display_drill_table
        except ImportError as e:
            raise ImportError(
                "Jupyter drill-down requires luxin-nb. "
                "With the luxin package: pip install luxin[notebook]. "
                "Or: pip install luxin-nb"
            ) from e

        display_drill_table(
            self, self._source_df, self._source_mapping, self._groupby_cols
        )


_UNTRACKED_GROUPBY_MSG = (
    "TrackedGroupBy does not implement {name!r}: it cannot preserve drill-down lineage. "
    "Use ``.agg(...)`` or a tracked reducer such as ``.sum()`` / ``.mean()`` instead."
)


class TrackedGroupBy:
    """
    A wrapper around pandas GroupBy that tracks source row labels during aggregation.

    Arbitrary GroupBy methods are not delegated: only tracked reductions are supported.
    """

    def __init__(self, df: TrackedDataFrame, by, **kwargs):
        self.tracked_df = df
        self.by = _normalize_groupby_columns(by)
        _gb_keys = self.by[0] if len(self.by) == 1 else self.by
        self.groupby_obj = pd.DataFrame(df).groupby(_gb_keys, **kwargs)

    def agg(self, func=None, *args, **kwargs):
        """
        Perform aggregation while tracking source row labels for drill-down.
        """
        # Perform the actual aggregation on the underlying DataFrame
        result = self.groupby_obj.agg(func, *args, **kwargs)

        # Create a TrackedDataFrame from the result
        tracked_result = TrackedDataFrame(result)
        tracked_result._is_aggregated = True
        tracked_result._groupby_cols = self.by
        tracked_result._source_df = pd.DataFrame(self.tracked_df)

        # Build the source mapping (optimized for large datasets)
        source_mapping = {}

        # Get the groups and their indices
        # Use groups.items() which is more efficient than iterating separately
        groups = self.groupby_obj.groups
        for group_key, group_indices in groups.items():
            # Convert group_key to a tuple if it's not already
            if not isinstance(group_key, tuple):
                group_key = (group_key,)

            # Store the mapping using the group key
            # Convert to list only once for efficiency
            source_mapping[group_key] = (
                list(group_indices)
                if isinstance(group_indices, (list, tuple))
                else list(group_indices)
            )

        # Optimize source mapping for performance and canonical tuple keys (numpy/datetime-safe)
        from luxin_core.utils import finalize_source_mapping

        tracked_result._source_mapping = finalize_source_mapping(source_mapping)

        return tracked_result

    def sum(self, *args, **kwargs):
        """Sum aggregation with tracking."""
        return self.agg("sum", *args, **kwargs)

    def mean(self, *args, **kwargs):
        """Mean aggregation with tracking."""
        return self.agg("mean", *args, **kwargs)

    def count(self, *args, **kwargs):
        """Count aggregation with tracking."""
        return self.agg("count", *args, **kwargs)

    def min(self, *args, **kwargs):
        """Min aggregation with tracking."""
        return self.agg("min", *args, **kwargs)

    def max(self, *args, **kwargs):
        """Max aggregation with tracking."""
        return self.agg("max", *args, **kwargs)

    def std(self, *args, **kwargs):
        """Standard deviation with tracking."""
        return self.agg("std", *args, **kwargs)

    def var(self, *args, **kwargs):
        """Variance aggregation with tracking."""
        return self.agg("var", *args, **kwargs)

    def median(self, *args, **kwargs):
        """Median aggregation with tracking."""
        return self.agg("median", *args, **kwargs)

    def apply(self, *args, **kwargs):  # noqa: ANN002
        raise NotImplementedError(_UNTRACKED_GROUPBY_MSG.format(name="apply"))

    def transform(self, *args, **kwargs):  # noqa: ANN002
        raise NotImplementedError(_UNTRACKED_GROUPBY_MSG.format(name="transform"))

    def pipe(self, *args, **kwargs):  # noqa: ANN002
        raise NotImplementedError(_UNTRACKED_GROUPBY_MSG.format(name="pipe"))

    def __getattr__(self, name: str):
        """Reject delegated GroupBy calls that would drop lineage tracking."""
        raise AttributeError(_UNTRACKED_GROUPBY_MSG.format(name=name))
