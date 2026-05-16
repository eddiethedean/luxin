# Migration Guide

Guide for migrating from legacy Luxin APIs to the **`Inspector`** API (stable since **v0.2.0**) and adopting **v0.3.0** optional features where useful. **v0.4.0** coordinates monorepo packages and tooling only; no migration steps beyond staying on current pinned versions.

## Overview

Luxin **v0.2.0** introduced the `Inspector` API pattern, similar to lavendertown. The old APIs are still present but deprecated. **v0.3.0** adds optional Phase 3 features (`DrillHierarchySpec`, comparison, quality, aggregation builder)—see below and the [User Guide](user-guide.md).

## Key Changes

### Old API (v0.1.0)

```python
from luxin import TrackedDataFrame

df = TrackedDataFrame({'category': ['A', 'A', 'B'], 'value': [10, 20, 30]})
agg = df.groupby('category').sum()
agg.show_drill_table()  # Old method
```

### New API (v0.2.0+)

```python
from luxin import Inspector, TrackedDataFrame

df = TrackedDataFrame({'category': ['A', 'A', 'B'], 'value': [10, 20, 30]})
agg = df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()  # New method
```

## Migration Steps

### Step 1: Update Imports

**Old**:
```python
from luxin import TrackedDataFrame, create_drill_table
```

**New**:
```python
from luxin import Inspector, TrackedDataFrame
```

### Step 2: Replace `show_drill_table()`

**Old**:
```python
agg.show_drill_table()
```

**New**:
```python
inspector = Inspector(agg)
inspector.render()
```

### Step 3: Update `create_drill_table()` Usage

**Old**:
```python
from luxin import create_drill_table
create_drill_table(agg_df, detail_df, groupby_cols=['category'])
```

**New** (Recommended):
```python
from luxin import TrackedDataFrame, Inspector

# Convert to TrackedDataFrame first
tracked_df = TrackedDataFrame(detail_df)
agg = tracked_df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()
```

**Alternative** (pre-aggregated / manual lineage — **still supported**):

```python
from luxin import create_drill_table
create_drill_table(agg_df, detail_df, groupby_cols=['category'])
```

Use this when **`agg_df`** and **`detail_df`** come from an existing pipeline; prefer **`TrackedDataFrame`** for new code so **`Inspector`** gets full tracking without recomputing masks. **`create_drill_table`** is not deprecated; only **`from luxin import show_drill_table`** and **`_build_source_mapping`** emit **deprecation** warnings.

## New Features in v0.2.0

### Configuration Options

```python
from luxin import Inspector
from luxin.config import InspectorConfig

config = InspectorConfig(
    show_summary_stats=False,
    show_export_buttons=True,
    detail_page_size=50,
)
inspector = Inspector(agg, config=config)
inspector.render()
```

### Polars Support

```python
import polars as pl
from luxin import create_tracked_from_polars, Inspector

polars_df = pl.DataFrame(...)
tracked_df = create_tracked_from_polars(polars_df)
agg = tracked_df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()
```

### Enhanced UI Features

- Clickable table rows (no more selectbox)
- Filtering and search
- Export functionality (CSV, JSON, Excel)
- Pagination for large datasets

## Backward Compatibility

**`show_drill_table()`** on **`TrackedDataFrame`** remains available but is deprecated in favor of **`Inspector(agg).render()`**. Importing **`from luxin import show_drill_table`** issues a **`DeprecationWarning`**.

**`create_drill_table()`** remains a supported entry point for manual / pre-aggregated workflows and does **not** emit a deprecation warning. Internal alias **`_build_source_mapping`** is deprecated in favor of **`build_manual_source_mapping`**.

It is still recommended to migrate interactive apps to **`Inspector`** for:

- Streamlit-native widget integration
- **`InspectorConfig`** (filters, export, Phase 3 toggles)
- Fewer moving parts than routing through legacy **`show_drill_table`**

## Common Migration Patterns

### Pattern 1: Simple Aggregation

**Old**:
```python
df = TrackedDataFrame(data)
agg = df.groupby('category').sum()
agg.show_drill_table()
```

**New**:
```python
df = TrackedDataFrame(data)
agg = df.groupby('category').sum()
Inspector(agg).render()
```

### Pattern 2: Multi-Column GroupBy

**Old**:
```python
agg = df.groupby(['region', 'category']).sum()
agg.show_drill_table()
```

**New**:
```python
agg = df.groupby(['region', 'category']).sum()
Inspector(agg).render()
```

### Pattern 3: Custom Aggregations

**Old**:
```python
agg = df.groupby('category').agg({'value': ['sum', 'mean']})
agg.show_drill_table()
```

**New**:
```python
agg = df.groupby('category').agg({'value': ['sum', 'mean']})
Inspector(agg).render()
```

## New in v0.3.0 (optional)

These are **additive**: defaults keep `Inspector(agg).render()` behavior unchanged.

- **`DrillHierarchySpec` + `enable_multi_level_drill`** — stacked aggregations with breadcrumbs (`from luxin import DrillHierarchySpec`; config from `luxin.config`).
- **`luxin.compare.inspect_pair`** — compare two aggregates side-by-side; install **`luxin[compare]`** for optional SciPy t-tests with `compare_run_significance=True`.
- **`show_data_quality`**, **`show_aggregation_builder`**, **`show_comparison_entrypoint`** — see [User Guide](user-guide.md) and [API Reference](api-reference.md).

## Timeline

- **v0.2.0**: `Inspector` API introduced; `show_drill_table` / legacy patterns deprecated with warnings
- **v0.2.1**: Streamlit **1.35+** required for dataframe row selection; normalized drill-down keys; clearer warnings for incomplete tracking; see [CHANGELOG.md](../CHANGELOG.md)
- **v0.3.0**: Phase 3 optional features (multi-level drill, comparison, quality, aggregation builder); legacy APIs still present with deprecation warnings (removal is a future major version concern, not tied to 0.3.0)
- **v0.4.0**: `luxin`, `luxin-core`, and `luxin-nb` aligned at **0.4.x**; stronger release checks and tests for `luxin-nb` HTML rendering—no API changes from v0.3.0 for Streamlit workflows
- **Unreleased (docs / patch)**: NA-aware **`build_manual_source_mapping`** for **`dropna=False`** keys; **`show_drill_table`** falls back to **`luxin_nb`** when Streamlit cannot be imported—see root **`CHANGELOG.md`**

## Need Help?

If you encounter issues during migration:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review [Examples](examples.md)
3. Open an issue on [GitHub](https://github.com/eddiethedean/luxin/issues)

