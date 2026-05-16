"""
HTML drill-down table rendering for Jupyter notebooks.
"""

import html
import json
import os
import random
import re
import string
from typing import Any, List

import pandas as pd
from IPython.display import HTML, display

from luxin_core.utils import SourceMapping, finalize_source_mapping, normalize_group_key


def display_drill_table(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
    **kwargs: Any,
) -> None:
    """
    Display an interactive drill-down table in Jupyter using HTML + IPython.

    Extra keyword arguments are accepted for API compatibility with the Streamlit path
    but are currently ignored.
    """
    display(HTML(render_html(agg_df, detail_df, source_mapping, groupby_cols)))


def _inject_data_luxin_keys_into_tbody(table_html: str, escaped_keys: List[str]) -> str:
    """Add data-luxin-key to each <tr> in <tbody>, matching dataframe row order."""
    m = re.search(
        r"(<tbody[^>]*>)(.*?)(</tbody>)", table_html, flags=re.DOTALL | re.IGNORECASE
    )
    if not m or not escaped_keys:
        return table_html
    open_tb, body, close_tb = m.group(1), m.group(2), m.group(3)
    keys_iter = iter(escaped_keys)

    def replace_tr(tm: re.Match) -> str:
        ek = next(keys_iter, None)
        if ek is None:
            return tm.group(0)
        return f'<tr data-luxin-key="{ek}"'

    new_body, n = re.subn(
        r"<tr\b", replace_tr, body, flags=re.IGNORECASE, count=len(escaped_keys)
    )
    if n != len(escaped_keys):
        return table_html
    return (
        table_html[: m.start()] + open_tb + new_body + close_tb + table_html[m.end() :]
    )


def _row_tuple_key_from_agg_df(agg_df: pd.DataFrame, row_position: int) -> tuple:
    """Source-mapping style tuple for one aggregated row (same convention as table_view)."""
    if isinstance(agg_df.index, pd.MultiIndex):
        key = agg_df.index[row_position]
        raw = tuple(key) if isinstance(key, tuple) else (key,)
    else:
        raw = (agg_df.index[row_position],)
    return normalize_group_key(raw)


def _json_str_for_mapping_key(key: Any) -> str:
    parts = normalize_group_key(key)
    out: List[str] = []
    for p in parts:
        if isinstance(p, pd.Timestamp):
            out.append("__NaT__" if pd.isna(p) else p.isoformat())
        else:
            out.append(str(p))
    return "|".join(out)


def render_html(
    agg_df: pd.DataFrame,
    detail_df: pd.DataFrame,
    source_mapping: SourceMapping,
    groupby_cols: List[str],
) -> str:
    """
    Render the HTML for the drill-down table.

    Args:
        agg_df: The aggregated DataFrame to display
        detail_df: The detail DataFrame containing source rows
        source_mapping: Mapping from aggregated row keys to lists of detail index labels
        groupby_cols: List of column names used to group the data

    Returns:
        Complete HTML string for the interactive table
    """
    source_mapping = finalize_source_mapping(dict(source_mapping))

    unique_id = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    base = os.path.dirname(__file__)
    template_path = os.path.join(base, "templates", "table.html")
    css_path = os.path.join(base, "static", "table.css")
    js_path = os.path.join(base, "static", "table.js")

    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()

    with open(js_path, "r", encoding="utf-8") as f:
        javascript = f.read()

    agg_table_html = agg_df.to_html(classes="luxin-table", border=0)
    row_js_keys = [
        html.escape(
            _json_str_for_mapping_key(_row_tuple_key_from_agg_df(agg_df, i)),
            quote=True,
        )
        for i in range(len(agg_df))
    ]
    agg_table_html = _inject_data_luxin_keys_into_tbody(agg_table_html, row_js_keys)

    detail_data = detail_df.to_dict(orient="index")
    detail_data = {str(k): v for k, v in detail_data.items()}

    json_mapping = {}
    for key, indices in source_mapping.items():
        str_key = _json_str_for_mapping_key(key)
        json_mapping[str_key] = [str(idx) for idx in indices]

    javascript = javascript.replace(
        "{source_mapping}", json.dumps(json_mapping, indent=2)
    )
    javascript = javascript.replace(
        "{detail_data}", json.dumps(detail_data, indent=2, default=str)
    )
    javascript = javascript.replace("{groupby_cols}", json.dumps(groupby_cols))
    javascript = javascript.replace("{unique_id}", unique_id)

    html_out = template.replace("{css}", css)
    html_out = html_out.replace("{agg_table}", agg_table_html)
    html_out = html_out.replace("{javascript}", javascript)
    html_out = html_out.replace("{unique_id}", unique_id)

    return html_out
