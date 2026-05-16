"""Tests for luxin_nb HTML drill-down rendering."""

import json
import re
from unittest.mock import patch

import pandas as pd
import pytest

from luxin_nb.display import (
    _inject_data_luxin_keys_into_tbody,
    _json_str_for_mapping_key,
    render_html,
)


@pytest.fixture
def fixed_unique_id():
    """Deterministic table instance id for snapshot-style assertions."""
    with patch(
        "luxin_nb.display.random.choices",
        return_value=["a", "b", "c", "d", "1", "2", "3", "4"],
    ):
        yield


def test_json_str_for_mapping_key_scalar_and_multi():
    assert _json_str_for_mapping_key(("A",)) == "A"
    assert _json_str_for_mapping_key(("A", "X")) == "A|X"


def test_json_str_for_mapping_key_timestamp():
    ts = pd.Timestamp("2024-01-15", tz="UTC")
    assert _json_str_for_mapping_key((ts,)) == ts.isoformat()


def test_inject_data_luxin_keys_into_tbody():
    table_html = "<table><tbody><tr><td>a</td></tr><tr><td>b</td></tr></tbody></table>"
    out = _inject_data_luxin_keys_into_tbody(table_html, ["k1", "k2"])
    assert out.count("data-luxin-key=") == 2
    assert 'data-luxin-key="k1"' in out
    assert 'data-luxin-key="k2"' in out


def test_inject_returns_original_when_tr_count_mismatch():
    table_html = "<table><tbody><tr><td>only</td></tr></tbody></table>"
    out = _inject_data_luxin_keys_into_tbody(table_html, ["k1", "k2"])
    assert out == table_html


def test_render_html_injects_row_keys_and_source_mapping(fixed_unique_id):
    agg_df = pd.DataFrame(
        {"value": [30, 70]}, index=pd.Index(["A", "B"], name="category")
    )
    detail_df = pd.DataFrame(
        {"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]}
    )
    source_mapping = {("A",): [0, 1], ("B",): [2, 3]}
    html_out = render_html(agg_df, detail_df, source_mapping, ["category"])

    assert html_out.count("data-luxin-key=") == 2
    assert "luxin-container-abcd1234" in html_out
    assert '"A":' in html_out and '"0"' in html_out and '"1"' in html_out
    assert '"B":' in html_out


def test_render_html_embedded_source_mapping_is_valid_json(fixed_unique_id):
    """Regression: injected ``sourceMapping`` must be valid JSON for table.js."""
    agg_df = pd.DataFrame({"value": [30, 70]}, index=pd.Index(["A", "B"]))
    detail_df = pd.DataFrame({"v": [1, 2, 3, 4]})
    source_mapping = {("A",): [0, 1], ("B",): [2, 3]}
    html_out = render_html(agg_df, detail_df, source_mapping, ["x"])
    m = re.search(
        r"const sourceMapping = (\{[\s\S]*?\});\s*\n\s*const detailData",
        html_out,
    )
    assert m is not None
    parsed = json.loads(m.group(1))
    assert parsed["A"] == ["0", "1"]
    assert parsed["B"] == ["2", "3"]


def test_render_html_multiindex_row_keys(fixed_unique_id):
    agg_df = pd.DataFrame({"value": [30]})
    agg_df.index = pd.MultiIndex.from_tuples([("R", "P")], names=["region", "product"])
    detail_df = pd.DataFrame(
        {"region": ["R"], "product": ["P"], "value": [30]},
    )
    source_mapping = {("R", "P"): [0]}
    html_out = render_html(agg_df, detail_df, source_mapping, ["region", "product"])
    assert html_out.count("data-luxin-key=") == 1
    assert 'data-luxin-key="R|P"' in html_out
