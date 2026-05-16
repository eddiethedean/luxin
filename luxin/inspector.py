"""
Inspector - Main class for interactive data exploration with drill-down capabilities.
"""

import pandas as pd
import streamlit as st
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union, cast

from luxin_core.polars_support import handle_polars_in_inspector, is_polars_dataframe
from luxin_core.config import InspectorConfig, get_default_config
from luxin_core.validation import validate_dataframe, ValidationError
from luxin_core.utils import finalize_source_mapping

if TYPE_CHECKING:
    from luxin_core.drill_hierarchy import DrillHierarchySpec


class Inspector:
    """
    Inspector class for interactive drill-down data exploration.

    Similar to lavendertown's Inspector pattern, this class provides
    a Streamlit-first interface for exploring aggregated data with
    drill-down capabilities.

    Example:
        >>> import streamlit as st
        >>> from luxin import Inspector
        >>> import pandas as pd
        >>>
        >>> df = pd.read_csv("data.csv")
        >>> inspector = Inspector(df)
        >>> inspector.render()
    """

    def __init__(
        self,
        df: Union[pd.DataFrame, Any],
        config: Optional[InspectorConfig] = None,
        *,
        drill: Optional["DrillHierarchySpec"] = None,
    ) -> None:
        """
        Initialize the Inspector with a DataFrame.

        Args:
            df: The DataFrame to inspect. Can be a regular pandas DataFrame,
                Polars DataFrame, or a TrackedDataFrame with aggregation tracking.
            config: Optional configuration object. If None, uses default config.
            drill: Optional hierarchical drill specification (Phase 3) when aggregated.
        """
        # Handle Polars DataFrames
        if is_polars_dataframe(df):
            df = handle_polars_in_inspector(df)

        # Validate input
        try:
            validate_dataframe(df, "df")
        except ValidationError as e:
            raise ValueError(str(e)) from e

        self.df = df
        self.config = config if config is not None else get_default_config()
        self.drill = drill

        self._is_aggregated = False
        self._source_mapping: Dict[Any, List[int]] = {}
        self._groupby_cols: List[str] = []
        self._source_df: Optional[pd.DataFrame] = None

        self._capture_tracked_props(self.df)
        self._aggregation_builder_source = (
            self._source_df.copy() if self._source_df is not None else None
        )

    def _capture_tracked_props(self, df: Union[pd.DataFrame, Any]) -> None:
        """Refresh aggregation metadata snapshots from ``df``."""

        self._is_aggregated = bool(getattr(df, "_is_aggregated", False))
        raw_map = getattr(df, "_source_mapping", {})
        if isinstance(raw_map, dict):
            self._source_mapping = finalize_source_mapping(dict(raw_map))
        else:
            self._source_mapping = {}
        self._groupby_cols = list(getattr(df, "_groupby_cols", []))
        src = getattr(df, "_source_df", None)
        if src is None:
            self._source_df = None
        elif isinstance(src, pd.DataFrame):
            self._source_df = src
        else:
            self._source_df = pd.DataFrame(src)

    def _session_suffix(self) -> str:
        return (
            self.config.inspector_session_key
            if self.config.inspector_session_key is not None
            else hex(id(self))
        )

    def render(self) -> None:
        """
        Render the interactive drill-down interface in Streamlit.

        This method must be called within a Streamlit app context.
        It will display the aggregated data (if available) or the
        source data, with interactive drill-down capabilities.
        """
        suffix = self._session_suffix()
        override_key = f"luxin_agg_override_{suffix}"
        tracked_override = st.session_state.get(override_key)
        override_active = getattr(tracked_override, "_is_aggregated", False) is True
        if override_active:
            effective_df = tracked_override
            self._capture_tracked_props(tracked_override)
        else:
            effective_df = self.df
            self._capture_tracked_props(self.df)

        if self.config.show_comparison_entrypoint:
            with st.expander("Compare aggregates (API hint)", expanded=False):
                st.markdown(
                    "```python\n"
                    "from luxin.compare import inspect_pair\n"
                    "inspect_pair(left_agg_df, right_agg_df, ['region'], config=inspector.config)\n"
                    "```",
                    unsafe_allow_html=False,
                )

        if (
            override_active
            and self.drill is not None
            and self.config.enable_multi_level_drill
        ):
            st.info(
                "Custom aggregation replaces the inspected root frame; clearing drill stack semantics."
                " Multi-level drill is disabled until the override is cleared."
            )

        if self._is_aggregated and (
            self._source_df is None or len(self._source_mapping) == 0
        ):
            st.dataframe(effective_df, use_container_width=True)
            st.warning(
                "Aggregation metadata is incomplete: drill-down requires a non-empty "
                "source_mapping and `_source_df` from ``TrackedDataFrame.groupby().agg()`` (or equivalent). "
                "Inspecting altered or manually constructed aggregated frames may omit this tracking."
            )
            return

        if self._is_aggregated and self._source_df is not None:
            from luxin.components.table_view import (
                render_drill_stack_view,
                render_table_view,
            )

            if (
                not override_active
                and self.drill is not None
                and self.config.enable_multi_level_drill
            ):
                render_drill_stack_view(
                    cast(pd.DataFrame, effective_df),
                    self.drill,
                    config=self.config,
                    widget_key_suffix=suffix,
                )
            else:
                render_table_view(
                    agg_df=cast(pd.DataFrame, effective_df),
                    detail_df=self._source_df,
                    source_mapping=self._source_mapping,
                    groupby_cols=self._groupby_cols,
                    config=self.config,
                    widget_key_suffix=suffix,
                )

            if (
                self.config.show_aggregation_builder
                and self._aggregation_builder_source is not None
            ):
                from luxin.components.aggregation_builder import (
                    render_footer_aggregation_builder,
                )

                render_footer_aggregation_builder(
                    self._aggregation_builder_source,
                    session_key_suffix=suffix,
                )
        else:
            # Display source data only (no aggregation tracking)
            st.dataframe(self.df, use_container_width=True)
            st.info(
                "💡 Tip: To enable drill-down capabilities, use TrackedDataFrame:\n\n"
                "```python\n"
                "from luxin import TrackedDataFrame, Inspector\n"
                "df = TrackedDataFrame(your_data)\n"
                "agg = df.groupby('column').agg({'value': 'sum'})\n"
                "inspector = Inspector(agg)\n"
                "inspector.render()\n"
                "```"
            )
