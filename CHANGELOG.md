# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-05-15

### Added

- **Phase 3 (advanced UX)**: multi-level drill-down with `DrillHierarchySpec`, breadcrumbs, and session-scoped stacks (`luxin_drill_*` keys plus optional `DrillHierarchySpec.session_key`).
- **`InspectorConfig` flags**: `enable_multi_level_drill`, `max_drill_depth`, `show_data_quality`, `show_aggregation_builder`, `compare_run_significance`, `show_comparison_entrypoint`, and `inspector_session_key` namespacing.
- **`luxin.components.quality_indicators`**: completeness/uniqueness-style metrics plus optional numeric outlier flags (IQR or z-score style).
- **Comparison tooling** (`luxin.compare.inspect_pair`): side-by-side tables, merged diff deltas / percent change, optional Welch t-tests when SciPy is installed (`luxin[compare]` extra).
- **Aggregation builder** expander sourced from the original inspected detail frame (`TrackedDataFrame._source_df` snapshot).
- **`luxin.DrillHierarchySpec` export for stable authoring of drill hierarchies.**

### Changed

- `Inspector(..., drill=...)` activates multi-level stacks only when `enable_multi_level_drill` is `True`; default behavior remains unchanged.
- Aggregation builder overrides stash the rebuilt `TrackedDataFrame` under `luxin_agg_override_{session}` with an explicit Clear control.

### Fixed

- **Filters**: text search uses an index-aligned boolean mask so non-`RangeIndex` tables no longer error.
- **Detail panel**: pagination uses stable `pagination_session_key` / content hash instead of `id(detail_rows)` so Streamlit reruns keep page state.
- **Drill stack**: truncating the breadcrumb stack clears all matching `luxin_drill_last_push_*` session keys (not only a fixed depth range).
- **Aggregation builder**: template mode no longer disagrees with the group-by multiselect; guard when no group-by candidates exist.
- **Comparison** (`luxin.compare`): UI and docstrings clarify Welch t-tests use pooled columns, not row-pairing by join keys.
- **CI**: GitHub Actions tests and lint also run on the **`master`** branch (default for this repo).

### Documentation

- User guide, API reference, and `examples/phase3_multi_level.py` document Phase 3 workflows.

## [0.2.1] - 2026-05-15

### Fixed

- **PyPI uploads**: drop invalid trove classifier `Framework :: Streamlit` (rejected by Warehouse with HTTP 400).
- Require **Streamlit >= 1.35** for dataframe row selection (`on_select` / `selection_mode`); surface a clear upgrade error on older versions.
- **Canonical `source_mapping` keys** so drill-down lookups work across numpy scalars, pandas timestamps, and mixed datetime representations.
- **`Inspector.render`** warns when aggregation metadata is missing or empty instead of falling through to the non-drill tip.
- **Unnamed aggregate index**: after `reset_index()`, column names align with `groupby_cols` so row selection resolves to the correct detail rows.
- **Column filters**: multiselect option sorting no longer raises on mixed-type uniques.

### Changed

- **`TrackedDataFrame.groupby`** supports column names as `str`, `list` / `tuple` of str, or a 1d ndarray of names; advanced pandas groupers (e.g. `pd.Grouper`) raise `NotImplementedError` with guidance.
- **Single-column groupby** uses a scalar `by` for pandas to avoid spurious `groups` API warnings.
- Removed the empty **`luxin[streamlit]`** optional extra; Streamlit stays a required dependency.

### Documentation

- Troubleshooting (Streamlit install / version), roadmap phase timeline note, and Polars return types clarified.

## [0.2.0] - prior

- Introduced the **`Inspector`** API; deprecated `show_drill_table` in favor of `Inspector(df).render()`. See [Migration guide](docs/migration.md).
