"""
Side-by-side comparison of two frames with optional deltas and SciPy-backed tests.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd
import streamlit as st

from luxin_core.config import InspectorConfig, get_default_config


def _with_join_columns(df: pd.DataFrame, join_keys: Sequence[str]) -> pd.DataFrame:
    out = df.copy()
    missing = [k for k in join_keys if k not in out.columns]
    if missing:
        try:
            out = out.reset_index()
        except Exception as exc:  # noqa: BLE001
            raise ValueError(
                f"Join keys {missing!r} not found as columns; ``reset_index()`` failed: {exc}"
            ) from exc
    still = [k for k in join_keys if k not in out.columns]
    if still:
        raise ValueError(f"Join keys missing after reset_index: {still!r}")
    return out


def align_for_compare(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    join_keys: Sequence[str],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Return left/right frames reindexed onto the outer union of composite keys."""
    jk = list(join_keys)
    if not jk:
        raise ValueError("join_keys must be non-empty")

    lf = _with_join_columns(left_df, jk).set_index(jk, drop=False).sort_index()
    rg = _with_join_columns(right_df, jk).set_index(jk, drop=False).sort_index()
    union_index = lf.index.union(rg.index)
    return lf.reindex(union_index), rg.reindex(union_index)


def build_diff_table(
    left: pd.DataFrame, right: pd.DataFrame, join_keys: Iterable[str]
) -> pd.DataFrame:
    """Wide diff view: shared numeric columns gain ``_left/_right/_delta/_pct_change`` fields."""
    jk = list(join_keys)
    lf, rg = align_for_compare(left, right, jk)

    value_cols = [
        c
        for c in lf.columns
        if c not in jk
        and pd.api.types.is_numeric_dtype(lf[c])
        and c in rg.columns
        and pd.api.types.is_numeric_dtype(rg[c])
    ]

    parts: Dict[str, pd.Series] = {}
    for base in jk:
        parts[base] = lf[base]

    for vc in sorted(value_cols):
        lser = lf[vc]
        rser = rg[vc]
        parts[f"{vc}_left"] = lser
        parts[f"{vc}_right"] = rser
        delta = rser.astype(float).sub(lser.astype(float), fill_value=float("nan"))
        parts[f"{vc}_delta"] = delta
        denom_ok = (lser != 0) & lser.notna()
        pct = pd.Series(float("nan"), index=lser.index)
        pct.loc[denom_ok] = (
            rser.astype(float)[denom_ok] / lser.astype(float)[denom_ok] - 1.0
        )
        parts[f"{vc}_pct_change"] = pct

    return pd.DataFrame(parts)


def _maybe_run_ttests(left: pd.DataFrame, right: pd.DataFrame, join_keys: List[str]):
    """
    Run Welch t-tests (SciPy) on each shared numeric column.

    Rows are **not** matched by ``join_keys``: each test compares the distribution
    of all non-null values in the left column to all non-null values in the right
    column after alignment (exploratory only; use paired tests externally if needed).
    """
    try:
        import scipy.stats  # noqa: WPS433
    except ImportError:
        return {}
    lf, rg = align_for_compare(left, right, join_keys)
    jk = list(join_keys)
    cols = [
        c
        for c in lf.columns
        if c not in jk
        and pd.api.types.is_numeric_dtype(lf[c])
        and c in rg.columns
        and pd.api.types.is_numeric_dtype(rg[c])
    ]
    results = {}
    for c in cols:
        a = lf[c].dropna().astype(float)
        b = rg[c].dropna().astype(float)
        if len(a) < 2 or len(b) < 2:
            continue
        results[c] = scipy.stats.ttest_ind(a, b, equal_var=False)
    return results


def render_comparison_views(
    left_df: pd.DataFrame,
    right_df: pd.DataFrame,
    *,
    join_keys: Sequence[str],
    left_label: str = "Left",
    right_label: str = "Right",
    config: Optional[InspectorConfig] = None,
) -> None:
    """Lay out aggregates plus an optional consolidated diff/expander."""

    cfg = config or get_default_config()
    st.subheader("Comparison mode")

    if not join_keys:
        st.warning("Provide non-empty join_keys for pairing rows.")
        return

    lf = _with_join_columns(left_df, list(join_keys))
    rg = _with_join_columns(right_df, list(join_keys))

    c1, c2 = st.columns(2)
    with c1:
        st.caption(left_label)
        st.dataframe(lf, use_container_width=True)
    with c2:
        st.caption(right_label)
        st.dataframe(rg, use_container_width=True)

    with st.expander("Diff table (joined keys)"):
        try:
            st.dataframe(
                build_diff_table(left_df, right_df, join_keys), use_container_width=True
            )
        except Exception as exc:  # noqa: BLE001
            st.error(f"Unable to build diff: {exc}")

    if cfg.compare_run_significance:
        with st.expander(
            "Optional significance checks (SciPy Welch t-test)", expanded=False
        ):
            st.caption(
                "Tests compare pooled column values (not row-paired by join key). "
                "For paired aggregates, run hypothesis tests outside Luxin."
            )
            tests = _maybe_run_ttests(left_df, right_df, list(join_keys))
            if not tests:
                st.info(
                    "Install scipy extras: pip install 'luxin[compare]' for pairwise t-tests."
                )
            else:
                rows = [
                    {"column": col, "statistic": res.statistic, "pvalue": res.pvalue}
                    for col, res in tests.items()
                ]
                st.dataframe(
                    pd.DataFrame(rows).set_index("column"), use_container_width=True
                )


def inspect_pair(
    left_agg: pd.DataFrame,
    right_agg: pd.DataFrame,
    join_keys: Sequence[str],
    *,
    config: Optional[InspectorConfig] = None,
    left_label: str = "Left",
    right_label: str = "Right",
) -> None:
    """Streamlit-first helper comparing two aggregates."""
    render_comparison_views(
        left_agg,
        right_agg,
        join_keys=join_keys,
        left_label=left_label,
        right_label=right_label,
        config=config,
    )
