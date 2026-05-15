"""Tests for Streamlit version helpers."""

from unittest.mock import patch

import pytest


def test_parse_streamlit_version_rc():
    from luxin._streamlit_compat import _parse_streamlit_version

    assert _parse_streamlit_version("1.35.0") == (1, 35, 0)
    assert _parse_streamlit_version("2.0.dev0") == (2, 0, 0)


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
