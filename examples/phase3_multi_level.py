"""
Phase 3 demo: multi-level drill + optional quality / builder flags.

Run with:
    streamlit run examples/phase3_multi_level.py
"""

import pandas as pd
import streamlit as st

from luxin import DrillHierarchySpec, Inspector, TrackedDataFrame
from luxin.config import InspectorConfig


def build_child(_parent_key, rows: pd.DataFrame):
    tracked = TrackedDataFrame(rows)
    return tracked.groupby("product").agg({"value": "sum"})


def main() -> None:
    st.set_page_config(page_title="Luxin Phase 3 demo", layout="wide")

    df = TrackedDataFrame(
        {
            "region": ["N", "N", "S", "S"],
            "product": ["A", "B", "A", "B"],
            "value": [10, 20, 30, 40],
        }
    )
    root = df.groupby("region").agg({"value": "sum"})

    config = InspectorConfig(
        enable_multi_level_drill=True,
        show_data_quality=True,
        show_aggregation_builder=True,
        show_comparison_entrypoint=True,
        inspector_session_key="phase3_demo",
    )

    spec = DrillHierarchySpec(
        session_key="phase3_demo",
        max_depth=4,
        level_labels=["Region", "Product"],
        next_level=build_child,
    )

    Inspector(root, config=config, drill=spec).render()


if __name__ == "__main__":
    main()
