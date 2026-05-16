"""Tests for aggregation builder widgets (mocked Streamlit)."""

from __future__ import annotations

from unittest.mock import patch

import pandas as pd
import pytest

from luxin.components.aggregation_builder import render_aggregation_builder
from luxin import TrackedDataFrame


@pytest.mark.streamlit
@patch("luxin.components.aggregation_builder.st")
def test_render_aggregation_builder_empty_source(mock_st):
    assert render_aggregation_builder(pd.DataFrame(), session_key_suffix="e") is None
    mock_st.info.assert_called_once()


@pytest.mark.streamlit
@patch("luxin.components.aggregation_builder.st")
def test_render_aggregation_builder_no_group_candidates(mock_st):
    df = pd.DataFrame(
        {"a": range(40), "b": range(40)}
    )  # high-cardinality numerics → no group-by candidates
    assert render_aggregation_builder(df, session_key_suffix="nogrp") is None
    mock_st.warning.assert_called()


@pytest.mark.streamlit
@patch("luxin.components.aggregation_builder.st")
def test_render_aggregation_builder_template_sum_not_applied(
    mock_st, detail_df_for_aggregation
):
    mock_st.selectbox.return_value = "starter_sum_numerics"
    mock_st.button.return_value = False
    out = render_aggregation_builder(
        detail_df_for_aggregation, session_key_suffix="tpl1"
    )
    assert out is None


@pytest.mark.streamlit
@patch("luxin.components.aggregation_builder.st")
def test_render_aggregation_builder_template_sum_applied(
    mock_st, detail_df_for_aggregation
):
    mock_st.selectbox.return_value = "starter_sum_numerics"
    mock_st.button.return_value = True

    out = render_aggregation_builder(
        detail_df_for_aggregation, session_key_suffix="tpl2"
    )

    assert isinstance(out, TrackedDataFrame)
    assert getattr(out, "_is_aggregated", False) is True
