# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The canonical copy for GitHub and releases also lives at the repository root as [`CHANGELOG.md`](https://github.com/eddiethedean/luxin/blob/master/CHANGELOG.md).

## [0.4.0] - 2026-05-15

Coordinated **0.4.x** releases for `luxin`, `luxin-core`, and `luxin-nb`; tests for Jupyter/HTML rendering in `luxin-nb`; release workflow checks `__version__` against the tag; CI uses **`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`** for pytest. Canonical package roots are **`luxin/`**, **`luxin_core/`**, and **`luxin_nb/`** only (historic releases: PyPI/git tags). See root [`CHANGELOG.md`](../CHANGELOG.md) for full notes.

## [0.3.0] - 2026-05-15

Phase 3 features (this release): multi-level drill (`DrillHierarchySpec` + breadcrumbs), data-quality dashboard, comparison views (`luxin.compare.inspect_pair`), aggregation builder expander, optional SciPy extra `luxin[compare]`, and new `InspectorConfig` flags.

**Fixes in this release** include filter index alignment for text search, stable detail-panel pagination keys, drill-stack push-guard cleanup on truncate, aggregation-builder template/manual consistency, and comparison significance copy clarifying pooled t-tests. CI runs on `master` as well as `main` / `develop`. See root `CHANGELOG.md` for full notes.

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

- Introduced the **`Inspector`** API; deprecated `show_drill_table` in favor of `Inspector(df).render()`. See [Migration guide](migration.md).
