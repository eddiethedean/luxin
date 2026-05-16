"""
Shared pytest fixtures and helpers for Luxin monorepo tests.
"""

from __future__ import annotations

from typing import Any, Dict, MutableMapping
from unittest.mock import MagicMock

import pandas as pd
import pytest

from luxin import TrackedDataFrame


@pytest.fixture
def sample_tracked_df() -> TrackedDataFrame:
    return TrackedDataFrame(
        {"category": ["A", "A", "B", "B"], "value": [10, 20, 30, 40]}
    )


@pytest.fixture
def sample_agg(sample_tracked_df: TrackedDataFrame) -> TrackedDataFrame:
    out = sample_tracked_df.groupby("category").agg({"value": "sum"})
    assert out._is_aggregated
    return out


@pytest.fixture
def streamlit_session_state() -> Dict[str, Any]:
    """Mutable dict installable as ``mock_st.session_state`` for drill stack tests."""
    return {}


def make_streamlit_mock(session_state: MutableMapping[str, Any]) -> MagicMock:
    """
    Build a MagicMock for ``streamlit`` with a real dict ``session_state``.

    Expanders are usable as context managers (no-op body).
    """
    mock_st = MagicMock()
    mock_st.session_state = session_state

    def _expander(*_a: Any, **_kw: Any) -> MagicMock:
        ctx = MagicMock()

        def _enter() -> MagicMock:
            return MagicMock()

        def _exit(*_e: Any) -> bool:
            return False

        ctx.__enter__ = _enter
        ctx.__exit__ = _exit
        return ctx

    mock_st.expander = MagicMock(side_effect=_expander)
    return mock_st


@pytest.fixture
def sample_comparison_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    left = pd.DataFrame({"region": ["N", "S"], "sales": [100.0, 200.0]})
    right = pd.DataFrame({"region": ["N", "S"], "sales": [110.0, 180.0]})
    return left, right


@pytest.fixture
def detail_df_for_aggregation() -> pd.DataFrame:
    return pd.DataFrame({"cat": ["x", "x", "y", "y"], "value": [1.0, 2.0, 3.0, 4.0]})
