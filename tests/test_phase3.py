"""Phase 3 helpers (pure + light Streamlit mocks where needed)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd

from luxin import TrackedDataFrame
from luxin.components.comparison import align_for_compare, build_diff_table
from luxin.drill_hierarchy import (
    DrillHierarchySpec,
    ensure_initial_stack,
    stack_state_key,
    try_push_selected,
    truncate_stack,
)
from luxin.components.quality_indicators import (
    compute_column_metrics,
    flag_numeric_outliers,
)
from luxin.utils import normalize_group_key


def test_drill_try_push_with_callback():
    base = TrackedDataFrame(
        {
            "region": ["N", "N", "S"],
            "product": ["A", "B", "A"],
            "value": [1.0, 2.0, 3.0],
        }
    )
    root = base.groupby("region").agg({"value": "sum"})

    def builder(_key, rows):
        t = TrackedDataFrame(rows)
        return t.groupby("product").agg({"value": "sum"})

    spec = DrillHierarchySpec(session_key="t1", next_level=builder)
    session_state: dict = {}
    stack = ensure_initial_stack(session_state, spec, root)

    nk = normalize_group_key(root.index[0])

    new_stack = try_push_selected(session_state, stack, nk, spec, absolute_max_depth=6)
    assert len(new_stack) == 2

    stack_from_state = list(session_state[stack_state_key(spec)])
    again = try_push_selected(
        session_state, stack_from_state, nk, spec, absolute_max_depth=6
    )
    assert len(again) == len(stack_from_state)


def test_drill_stack_truncation_clears_counters():
    base = TrackedDataFrame({"region": ["N"], "value": [5.0]})
    root = base.groupby("region").agg({"value": "sum"})

    spec = DrillHierarchySpec(
        session_key="t2",
        next_level=lambda _k, rows: (
            TrackedDataFrame(rows).assign(x=1).groupby("region").agg({"value": "mean"})
        ),
    )
    session_state: dict = {}
    ensure_initial_stack(session_state, spec, root)
    truncate_stack(session_state, spec, new_len=1)
    assert stack_state_key(spec) in session_state


def test_comparison_diff_table_builds_columns():
    left = pd.DataFrame({"k": [1, 2], "v": [10, 20]}).set_index("k")
    right = pd.DataFrame({"k": [1, 2], "v": [11, 22]}).set_index("k")
    diff = build_diff_table(left, right, ["k"])
    assert "v_delta" in diff.columns
    assert diff.loc[1, "v_delta"] == 1.0


def test_comparison_align_union_index():
    left_small = pd.DataFrame({"k": ["a", "b"], "v": [1, 2]})
    r = pd.DataFrame({"k": ["b", "c"], "v": [3, 4]})
    la, ra = align_for_compare(left_small, r, ["k"])
    assert len(la) == 3 and len(ra) == 3


def test_quality_metrics_and_outliers():
    df = pd.DataFrame({"a": [1, 2, 3, 100.0], "b": ["x", "y", "z", "w"]})
    metrics = compute_column_metrics(df)
    assert metrics.loc["b", "non_null_pct"] == 100.0
    mask = flag_numeric_outliers(df, method="iqr")
    assert bool(mask.iloc[-1]) is True


def test_quality_dashboard_streamlit_mock(monkeypatch):
    from luxin.components import quality_indicators as qi

    mock_expander = MagicMock()
    expander_ctx = MagicMock()
    expander_ctx.__enter__.return_value = None
    expander_ctx.__exit__.return_value = None
    mock_expander.return_value = expander_ctx

    monkeypatch.setattr(qi.st, "expander", mock_expander)
    monkeypatch.setattr(qi.st, "dataframe", MagicMock())
    monkeypatch.setattr(qi.st, "success", MagicMock())
    monkeypatch.setattr(qi.st, "warning", MagicMock())

    qi.render_quality_dashboard(pd.DataFrame({"x": [1, 2]}))
    assert mock_expander.called
