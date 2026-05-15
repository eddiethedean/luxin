"""
Streamlit widgets to build tracked aggregations from the root detail frame plus light templates.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence

import pandas as pd
import streamlit as st

from luxin.tracked_df import TrackedDataFrame

AggName = str

AGG_CHOICES: List[AggName] = ["sum", "mean", "count", "min", "max", "median"]

TEMPLATE_DESCRIPTIONS: Dict[str, str] = {
    "starter_sum_numerics": "First low-cardinality column as groupby; sum all numerics.",
    "two_level_mean": "First two categorical-ish columns; mean numerics.",
    "count_all_numerics": "Up to two group columns; count each numeric column.",
}


def _infer_groupby_candidates(df: pd.DataFrame, max_candidates: int = 12) -> List[str]:
    out: List[str] = []
    for c in df.columns:
        if len(out) >= max_candidates:
            break
        ser = df[c].dropna()
        if ser.empty:
            continue
        if pd.api.types.is_numeric_dtype(df[c]):
            if ser.nunique() <= 25:
                out.append(c)
            continue
        out.append(c)
    return list(dict.fromkeys(out))


def _numeric_value_candidates(df: pd.DataFrame, group_cols: Sequence[str]) -> List[str]:
    return [
        c
        for c in df.columns
        if c not in group_cols and pd.api.types.is_numeric_dtype(df[c])
    ]


def render_aggregation_builder(
    source_df: pd.DataFrame,
    *,
    session_key_suffix: str,
    max_groupby_cols: int = 4,
) -> Optional[TrackedDataFrame]:
    """
    Render widgets; return a new aggregated ``TrackedDataFrame`` when **Apply** runs.

    ``session_key_suffix`` should be stable per Inspector instance to avoid widget collisions.
    """
    if source_df is None or source_df.empty:
        st.info("No source rows available for aggregation.")
        return None

    grp_opts = _infer_groupby_candidates(source_df)

    gb_cols = st.multiselect(
        "Group-by columns",
        options=grp_opts,
        default=grp_opts[:1],
        key=f"luxin_agg_gb_{session_key_suffix}",
        max_selections=min(max_groupby_cols, len(grp_opts)),
    )

    tmpl = st.selectbox(
        "Template",
        ["(manual)"] + sorted(TEMPLATE_DESCRIPTIONS.keys()),
        key=f"luxin_agg_tmpl_{session_key_suffix}",
    )

    vals = _numeric_value_candidates(source_df, gb_cols)
    agg_spec: Dict[str, str] = {}

    if tmpl != "(manual)":
        with st.expander("Template hint", expanded=False):
            st.caption(TEMPLATE_DESCRIPTIONS[tmpl])

    if tmpl == "starter_sum_numerics":
        gb_cols = grp_opts[:1]
        agg_spec = {c: "sum" for c in _numeric_value_candidates(source_df, gb_cols)}
        st.caption("Template locked groupby/value reducers.")

    elif tmpl == "two_level_mean":
        gb_cols = grp_opts[: min(2, len(grp_opts))]
        agg_spec = {c: "mean" for c in _numeric_value_candidates(source_df, gb_cols)}

    elif tmpl == "count_all_numerics":
        gb_cols = grp_opts[: min(2, len(grp_opts))]
        agg_spec = {c: "count" for c in _numeric_value_candidates(source_df, gb_cols)}

    elif tmpl == "(manual)":
        vals_pick = st.multiselect(
            "Value columns (numeric)",
            options=vals,
            default=vals[: min(len(vals), 6)],
            key=f"luxin_agg_vals_{session_key_suffix}",
        )
        agg_spec = {}
        for vc in vals_pick:
            choice = st.selectbox(
                f"Reducer for `{vc}`",
                AGG_CHOICES,
                index=min(AGG_CHOICES.index("sum"), len(AGG_CHOICES) - 1),
                key=f"luxin_agg_red_{session_key_suffix}_{vc}",
            )
            agg_spec[vc] = choice

    clicked = st.button("Apply aggregation", key=f"luxin_agg_apply_{session_key_suffix}")
    if not clicked:
        return None

    if not gb_cols:
        st.warning("Select at least one group-by column.")
        return None
    if not agg_spec:
        st.warning("Define which numeric columns should be aggregated.")
        return None

    tracked_src = TrackedDataFrame(pd.DataFrame(source_df))
    try:
        out = tracked_src.groupby(list(gb_cols)).agg(agg_spec)  # type: ignore[arg-type]
    except Exception as exc:  # noqa: BLE001
        st.error(f"Aggregation failed — check dtypes and reducer compatibility: {exc}")
        return None

    assert isinstance(out, TrackedDataFrame)
    return out


def render_footer_aggregation_builder(
    source_df: pd.DataFrame,
    *,
    session_key_suffix: str,
) -> None:
    """Expander wrapping :func:`render_aggregation_builder` with success messaging."""
    with st.expander("🧱 Build aggregation", expanded=False):
        if st.button("Clear custom aggregation", key=f"luxin_agg_clr_{session_key_suffix}"):
            st.session_state.pop(f"luxin_agg_override_{session_key_suffix}", None)
            st.rerun()
        rebuilt = render_aggregation_builder(source_df, session_key_suffix=session_key_suffix)
        key = f"luxin_agg_override_{session_key_suffix}"
        if rebuilt is not None:
            st.session_state[key] = rebuilt
            st.success("Applied — main table refreshes.")
            st.rerun()
