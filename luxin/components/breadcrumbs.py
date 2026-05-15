"""
Clickable breadcrumbs for drill stack navigation (Streamlit).
"""

from typing import Callable, List, Optional

import streamlit as st

from luxin.drill_hierarchy import DrillLevelContext, DrillHierarchySpec, truncate_stack


def render_drill_breadcrumbs(
    stack: List[DrillLevelContext],
    spec: DrillHierarchySpec,
    *,
    on_truncate: Optional[Callable[[int], None]] = None,
) -> None:
    """
    Render one button per breadcrumb segment; jumping truncates drill stack via ``truncate_stack``.
    """
    if not stack:
        return
    st.caption("Drill path")
    cols = st.columns(max(1, len(stack)), gap="small")
    for i, ctx in enumerate(stack):
        lbl = ctx.label if ctx.label else f"Level {i}"
        btn_key = f"luxin_bc_{spec.session_key}_{i}"
        hit = cols[i].button(str(lbl), key=btn_key, use_container_width=True)
        if hit:
            new_len = i + 1
            truncate_stack(st.session_state, spec, new_len)
            if on_truncate:
                on_truncate(new_len)
            st.rerun()
