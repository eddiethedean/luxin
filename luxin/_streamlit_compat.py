"""Minimum Streamlit version checks for dataframe row-selection APIs."""

from __future__ import annotations

MIN_STREAMLIT_FOR_DATAFRAME_SELECTION = (1, 35, 0)


def _parse_streamlit_version(version_str: str) -> tuple:
    parts = []
    for tok in version_str.split(".")[:3]:
        digits = "".join(ch for ch in tok if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def streamlit_version_tuple() -> tuple:
    """Return parsed (major, minor, patch) for the installed Streamlit."""
    import streamlit as st  # noqa: PLC0415

    return _parse_streamlit_version(getattr(st, "__version__", "0"))


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
