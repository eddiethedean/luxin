"""Tests for Streamlit version helpers."""

from unittest.mock import patch

import pytest


def test_streamlit_version_tuple_examples():
    """Regression: version strings parse via packaging (major, minor, micro)."""
    import streamlit as st
    from luxin._streamlit_compat import streamlit_version_tuple

    with patch.object(st, "__version__", "1.35.0"):
        assert streamlit_version_tuple() == (1, 35, 0)
    with patch.object(st, "__version__", "2.0.dev0"):
        assert streamlit_version_tuple() == (2, 0, 0)


def test_dataframe_selection_supported_with_modern_streamlit():
    from luxin._streamlit_compat import dataframe_selection_supported

    if not dataframe_selection_supported():
        pytest.skip("Streamlit < 1.35 in this environment")


@patch("luxin._streamlit_compat.streamlit_version_tuple", return_value=(1, 34, 0))
def test_dataframe_selection_supported_false_on_old(mock_ver):
    from luxin._streamlit_compat import dataframe_selection_supported

    assert dataframe_selection_supported() is False


@patch("luxin._streamlit_compat.streamlit_version_tuple", return_value=(1, 35, 0))
def test_dataframe_selection_supported_true(mock_ver):
    from luxin._streamlit_compat import dataframe_selection_supported

    assert dataframe_selection_supported() is True
