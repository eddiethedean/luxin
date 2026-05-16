"""Minimum Streamlit version checks for dataframe row-selection APIs."""

from __future__ import annotations

MIN_STREAMLIT_FOR_DATAFRAME_SELECTION = (1, 35, 0)


def streamlit_version_tuple() -> tuple:
    """Return parsed (major, minor, micro) for the installed Streamlit."""
    import streamlit as st  # noqa: PLC0415
    from packaging.version import Version  # noqa: PLC0415

    v = Version(getattr(st, "__version__", "0"))
    return (v.major, v.minor, v.micro)


def dataframe_selection_supported() -> bool:
    """True when ``st.dataframe`` supports ``on_select`` / ``selection_mode`` (Streamlit >= 1.35)."""
    return streamlit_version_tuple() >= MIN_STREAMLIT_FOR_DATAFRAME_SELECTION


def dataframe_selection_guard_message(
    required: tuple = MIN_STREAMLIT_FOR_DATAFRAME_SELECTION,
) -> str:
    return (
        f"Luxin's drill-down table requires Streamlit >= {required[0]}.{required[1]}.{required[2]} "
        f"(dataframe row selection APIs). Upgrade with: pip install 'streamlit>={required[0]}.{required[1]}.{required[2]}'"
    )
