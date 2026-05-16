"""
Pure helpers for multi-level drill-down stacks (TrackedDataFrame + optional callback/lookup).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

import pandas as pd

from luxin_core.utils import finalize_source_mapping, normalize_group_key

# Callback: parent_agg_row_key, slice of parent's detail_df -> aggregated TrackedDataFrame
DrillCallback = Callable[[Tuple[Any, ...], pd.DataFrame], Any]
DrillLookup = Dict[Any, Any]


def _as_tracked_from_context(obj: Any) -> Any:
    if getattr(obj, "_is_aggregated", False):
        return obj
    raise TypeError(
        "Drill child must be an aggregated ``TrackedDataFrame`` with `_is_aggregated=True`."
    )


@dataclass
class DrillLevelContext:
    """
    One rendered level of the hierarchy: aggregated view + tracked detail lineage.
    """

    agg_df: pd.DataFrame
    detail_df: pd.DataFrame
    source_mapping: Dict[Any, List[Any]]
    groupby_cols: List[str]
    label: str

    def __post_init__(self) -> None:
        self.source_mapping = finalize_source_mapping(dict(self.source_mapping))


def context_from_tracked(agg_df: Any, label: str = "Root") -> DrillLevelContext:
    """Build a context from an aggregated ``TrackedDataFrame``."""
    if not getattr(agg_df, "_is_aggregated", False):
        raise ValueError(
            "``context_from_tracked`` expects an aggregated TrackedDataFrame."
        )
    raw_map = getattr(agg_df, "_source_mapping", {})
    if not isinstance(raw_map, dict):
        raw_map = {}
    detailed = getattr(agg_df, "_source_df", None)
    if detailed is None:
        raise ValueError("TrackedDataFrame missing ``_source_df``.")
    grp = getattr(agg_df, "_groupby_cols", [])
    if not grp:
        grp = []
    return DrillLevelContext(
        agg_df=agg_df,
        detail_df=pd.DataFrame(detailed),
        source_mapping=dict(raw_map),
        groupby_cols=list(grp),
        label=label,
    )


class DrillHierarchySpec:
    """
    Declarative spec for advancing from a parent aggregated row into a child aggregation.

    Either provide ``next_level`` callable or ``children_by_parent_key`` lookup of
    precomputed ``TrackedDataFrame``. Map keys are normalized to canonical tuple keys
    at construction (see :func:`luxin_core.utils.normalize_group_key`).
    """

    def __init__(
        self,
        *,
        session_key: str = "default",
        max_depth: int = 8,
        level_labels: Optional[Sequence[str]] = None,
        next_level: Optional[DrillCallback] = None,
        children_by_parent_key: Optional[DrillLookup] = None,
    ) -> None:
        self.session_key = session_key
        self.max_depth = int(max_depth)
        self.level_labels = list(level_labels) if level_labels is not None else None
        self.next_level = next_level
        if children_by_parent_key:
            self.children_by_parent_key = {
                normalize_group_key(k): v for k, v in children_by_parent_key.items()
            }
        else:
            self.children_by_parent_key = None

        if self.next_level is None and self.children_by_parent_key is None:
            raise ValueError(
                "DrillHierarchySpec requires ``next_level`` and/or ``children_by_parent_key``."
            )

    def label_for_depth(self, depth: int, default: str) -> str:
        if self.level_labels and depth < len(self.level_labels):
            return self.level_labels[depth]
        return default

    def resolve_child_for_parent_row(
        self, parent_normalized_key: Tuple[Any, ...], detail_slice: pd.DataFrame
    ) -> Optional[Any]:
        nk = normalize_group_key(parent_normalized_key)
        if self.children_by_parent_key is not None:
            cand = self.children_by_parent_key.get(nk)
            if cand is not None:
                return _as_tracked_from_context(cand)
        if self.next_level is None:
            return None
        out = self.next_level(nk, detail_slice)
        if out is None:
            return None
        return _as_tracked_from_context(out)


def stack_state_key(spec: DrillHierarchySpec) -> str:
    return f"luxin_drill_stack_{spec.session_key}"


def _clear_push_guards_from_depth(
    session_state: Any, spec: DrillHierarchySpec, from_depth: int
) -> None:
    """Remove ``luxin_drill_last_push_<session>_<d>`` keys for all ``d >= from_depth``."""
    prefix = f"luxin_drill_last_push_{spec.session_key}_"
    for k in list(session_state.keys()):
        if not isinstance(k, str) or not k.startswith(prefix):
            continue
        rest = k[len(prefix) :]
        try:
            depth = int(rest)
        except ValueError:
            continue
        if depth >= from_depth:
            session_state.pop(k, None)


def truncate_stack(session_state: Any, spec: DrillHierarchySpec, new_len: int) -> None:
    key = stack_state_key(spec)
    stack: List[DrillLevelContext] = list(session_state.get(key, []))
    if new_len <= 0:
        stack = []
        _clear_push_guards_from_depth(session_state, spec, 0)
    elif new_len < len(stack):
        stack = stack[:new_len]
        _clear_push_guards_from_depth(session_state, spec, max(0, new_len - 1))
    session_state[key] = stack


def ensure_initial_stack(
    session_state: Any, spec: DrillHierarchySpec, root: Any
) -> List[DrillLevelContext]:
    key = stack_state_key(spec)
    existing = session_state.get(key)
    if isinstance(existing, list) and existing:
        return existing
    root_ctx = context_from_tracked(root, label=spec.label_for_depth(0, "Root"))
    session_state[key] = [root_ctx]
    return session_state[key]


def try_push_selected(
    session_state: Any,
    stack: List[DrillLevelContext],
    selected_key: Tuple[Any, ...],
    spec: DrillHierarchySpec,
    *,
    absolute_max_depth: int,
) -> List[DrillLevelContext]:
    """
    Attempt to drill one level deeper on ``selected_key`` if depth allows.
    Guards repeated pushes across Streamlit reruns with per-depth session keys.
    """
    if stack is None or not stack:
        return stack or []
    if len(stack) >= min(spec.max_depth, absolute_max_depth):
        return stack

    parent_depth = len(stack) - 1
    nk = normalize_group_key(selected_key)
    push_guard = f"luxin_drill_last_push_{spec.session_key}_{parent_depth}"
    # Same selection across Streamlit reruns: skip duplicate push if child level exists
    if session_state.get(push_guard) == nk and len(stack) > parent_depth + 1:
        return stack

    current = stack[-1]
    detail_indices = current.source_mapping.get(nk, [])
    if not detail_indices:
        return stack
    slice_df = current.detail_df.loc[detail_indices]
    child = spec.resolve_child_for_parent_row(nk, slice_df)
    if child is None:
        return stack

    new_ctx = context_from_tracked(
        child, label=spec.label_for_depth(len(stack), f"Level {len(stack)}")
    )
    session_state[push_guard] = nk
    new_stack = list(stack) + [new_ctx]
    session_state[stack_state_key(spec)] = new_stack
    return new_stack
