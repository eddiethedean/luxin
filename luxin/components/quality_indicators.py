"""
Data-quality helpers and lightweight Streamlit dashboard.
"""

from __future__ import annotations

from typing import List, Literal

import numpy as np
import pandas as pd
import streamlit as st


def compute_column_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-column summary: dtype, non-null count/% , nunique.

    Rows are indexed by column names.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    rows = []
    n = len(df)
    for col in df.columns:
        s = df[col]
        non_null = int(s.notna().sum())
        row = {
            "column": col,
            "dtype": str(s.dtype),
            "non_null": non_null,
            "non_null_pct": (non_null / n * 100.0) if n else 0.0,
            "nunique": int(s.nunique(dropna=True)),
        }
        rows.append(row)
    out = pd.DataFrame(rows).set_index("column")
    return out


def flag_numeric_outliers(
    df: pd.DataFrame,
    *,
    method: Literal["iqr", "zscore"] = "iqr",
    z_threshold: float = 3.0,
) -> pd.Series:
    """
    Row-level boolean mask: ``True`` when **any numeric** column is flagged.

    Numeric columns only; categorical columns are ignored silently.
    """
    if df is None or df.empty:
        return pd.Series(dtype=bool)

    masks: List[pd.Series] = []

    for col in df.columns:
        if not pd.api.types.is_numeric_dtype(df[col]):
            continue

        series = df[col]
        vals = series.dropna()
        if vals.empty:
            continue

        if method == "zscore":
            mu = float(vals.mean())
            sigma = float(vals.std(ddof=0))
            if sigma == 0:
                masks.append(pd.Series(False, index=df.index))
                continue
            z = np.abs((series.astype(float) - mu) / sigma)
            masks.append(pd.Series(z > z_threshold, index=df.index).fillna(False))
            continue

        q1 = vals.quantile(0.25)
        q3 = vals.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            masks.append(pd.Series(False, index=df.index))
            continue
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        m = ((series.astype(float) < lower) | (series.astype(float) > upper)).fillna(False)
        masks.append(m)

    if not masks:
        return pd.Series(False, index=df.index)

    out = masks[0]
    for m in masks[1:]:
        out = out | m
    return out.reindex(df.index).fillna(False)


def render_quality_dashboard(
    detail_df: pd.DataFrame,
    *,
    title: str = "Data quality",
    outlier_method: Literal["iqr", "zscore"] = "iqr",
) -> None:
    """Expandable dashboard: metrics table + short textual summary."""
    expanded = False

    if detail_df is None or detail_df.empty:
        with st.expander(title, expanded=expanded):
            st.caption("No rows to summarize.")
        return

    with st.expander(title, expanded=expanded):
        metrics = compute_column_metrics(detail_df)
        st.dataframe(metrics, use_container_width=True)

        low_complete = metrics.index[metrics["non_null_pct"] < 100.0].tolist()

        if low_complete:
            st.warning(
                f"{len(low_complete)} column(s) are not fully populated — "
                f"{', '.join(map(str, low_complete[:15]))}"
                + (" …" if len(low_complete) > 15 else "")
            )
        else:
            st.success("Non-null completeness looks solid for sampled columns.")

        outliers = flag_numeric_outliers(detail_df, method=outlier_method)
        n_flags = int(outliers.sum())
        if n_flags:
            st.warning(
                f"{n_flags} row(s) flagged by `{outlier_method}` rule on numeric fields."
                " Showing up to first 200."
            )
            st.dataframe(detail_df.loc[outliers].head(200), use_container_width=True)
