"""Tests for manual API functions."""

import numpy as np
import pandas as pd
import pytest

from luxin import drill_table as luxin_drill_table
from luxin.drill_table import build_manual_source_mapping
from luxin_core.drill_table import validate_manual_drill_inputs


def test_build_source_mapping_single_column():
    """Test building source mapping with single groupby column."""
    detail_df = pd.DataFrame(
        {"category": ["A", "A", "B", "B", "C"], "value": [10, 20, 30, 40, 50]}
    )

    agg_df = detail_df.groupby("category").sum()

    mapping = build_manual_source_mapping(agg_df, detail_df, ["category"])

    assert len(mapping) == 3
    assert set(mapping[("A",)]) == {0, 1}
    assert set(mapping[("B",)]) == {2, 3}
    assert set(mapping[("C",)]) == {4}


def test_build_source_mapping_multi_column():
    """Test building source mapping with multiple groupby columns."""
    detail_df = pd.DataFrame(
        {
            "cat1": ["A", "A", "B", "B", "A"],
            "cat2": ["X", "Y", "X", "Y", "X"],
            "value": [10, 20, 30, 40, 50],
        }
    )

    agg_df = detail_df.groupby(["cat1", "cat2"]).sum()

    mapping = build_manual_source_mapping(agg_df, detail_df, ["cat1", "cat2"])

    assert len(mapping) == 4
    assert set(mapping[("A", "X")]) == {0, 4}
    assert set(mapping[("A", "Y")]) == {1}
    assert set(mapping[("B", "X")]) == {2}
    assert set(mapping[("B", "Y")]) == {3}


def test_build_source_mapping_empty_groups():
    """Test source mapping handles DataFrames with some empty groups."""
    detail_df = pd.DataFrame({"category": ["A", "A", "B"], "value": [10, 20, 30]})

    agg_df = detail_df.groupby("category").sum()

    mapping = build_manual_source_mapping(agg_df, detail_df, ["category"])

    assert len(mapping) == 2
    assert set(mapping[("A",)]) == {0, 1}
    assert set(mapping[("B",)]) == {2}


def test_deprecated_build_source_mapping_warns():
    detail_df = pd.DataFrame({"category": ["A"], "value": [1]})
    agg_df = detail_df.groupby("category").sum()
    with pytest.warns(DeprecationWarning, match="build_manual_source_mapping"):
        luxin_drill_table._build_source_mapping(agg_df, detail_df, ["category"])


def test_validate_manual_drill_multiindex_groupby_length_mismatch():
    detail_df = pd.DataFrame({"a": [1, 2], "b": [3, 4], "v": [1.0, 2.0]})
    agg_df = detail_df.groupby(["a", "b"]).sum()
    with pytest.raises(ValueError, match="index.nlevels"):
        validate_manual_drill_inputs(agg_df, detail_df, ["a"])


def test_validate_manual_drill_flat_index_requires_one_groupby_col():
    detail_df = pd.DataFrame({"category": ["A"], "value": [1]})
    agg_df = detail_df.groupby("category").sum()
    with pytest.raises(ValueError, match="exactly one"):
        validate_manual_drill_inputs(agg_df, detail_df, ["category", "value"])


def test_validate_manual_drill_multi_column_ok():
    detail_df = pd.DataFrame(
        {"cat1": ["A", "B"], "cat2": ["X", "Y"], "value": [1.0, 2.0]}
    )
    agg_df = detail_df.groupby(["cat1", "cat2"]).sum()
    validate_manual_drill_inputs(agg_df, detail_df, ["cat1", "cat2"])


def test_build_source_mapping_na_group_key_dropna_false_float():
    """NA group keys must match detail rows (``==`` alone fails for NaN)."""
    detail_df = pd.DataFrame(
        {"category": [np.nan, np.nan, "A", "A"], "value": [10.0, 20.0, 30.0, 40.0]}
    )
    agg_df = detail_df.groupby("category", dropna=False).sum()
    mapping = build_manual_source_mapping(agg_df, detail_df, ["category"])

    assert len(mapping) == 2
    na_keys = [k for k in mapping if len(k) == 1 and pd.isna(k[0])]
    assert len(na_keys) == 1
    assert set(mapping[na_keys[0]]) == {0, 1}
    assert set(mapping[("A",)]) == {2, 3}


def test_build_source_mapping_na_group_key_string_dtype():
    detail_df = pd.DataFrame(
        {
            "category": pd.array([pd.NA, pd.NA, "x"], dtype="string"),
            "value": [1, 2, 3],
        }
    )
    agg_df = detail_df.groupby("category", dropna=False).sum()
    mapping = build_manual_source_mapping(agg_df, detail_df, ["category"])
    assert len(mapping) == 2
    na_keys = [k for k in mapping if len(k) == 1 and pd.isna(k[0])]
    assert len(na_keys) == 1
    assert set(mapping[na_keys[0]]) == {0, 1}


def test_build_source_mapping_multiindex_one_na_level():
    detail_df = pd.DataFrame(
        {
            "cat1": [np.nan, np.nan, "A"],
            "cat2": ["X", "X", "Y"],
            "value": [1.0, 2.0, 3.0],
        }
    )
    agg_df = detail_df.groupby(["cat1", "cat2"], dropna=False).sum()
    mapping = build_manual_source_mapping(agg_df, detail_df, ["cat1", "cat2"])
    na_x_key = next(k for k in mapping if len(k) == 2 and pd.isna(k[0]) and k[1] == "X")
    assert set(mapping[na_x_key]) == {0, 1}
    assert set(mapping[("A", "Y")]) == {2}
