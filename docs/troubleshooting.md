# Troubleshooting Guide

Common issues and solutions when using luxin.

## Inspector shows "No detail rows found"

**Problem**: When clicking on a row in the aggregated table, no detail rows are displayed.

**Possible Causes**:
1. The DataFrame wasn't created using `TrackedDataFrame`
2. The aggregation wasn't performed on a `TrackedDataFrame`
3. The source mapping wasn't properly tracked

**Solution**:
```python
# ❌ Wrong - regular pandas DataFrame
df = pd.DataFrame({'category': ['A', 'A', 'B'], 'value': [10, 20, 30]})
agg = df.groupby('category').sum()
inspector = Inspector(agg)  # Won't have tracking

# ✅ Correct - use TrackedDataFrame
from luxin import TrackedDataFrame, Inspector
df = TrackedDataFrame({'category': ['A', 'A', 'B'], 'value': [10, 20, 30]})
agg = df.groupby('category').sum()  # Tracking happens automatically
inspector = Inspector(agg)
inspector.render()
```

## Streamlit errors when calling render()

**Problem**: Getting errors when calling `Inspector.render()`.

**Possible Causes**:
1. Streamlit is not installed
2. `render()` is called outside a Streamlit app context
3. Version incompatibility

**Solution**:

Luxin declares **Streamlit** as a dependency (dataframe row selections require Streamlit **1.35+**). Upgrade with:

```bash
pip install -U streamlit
```

Make sure `render()` is called within a Streamlit app:
```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

st.title("My App")
df = TrackedDataFrame(...)
agg = df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()  # Must be in Streamlit context
```

## Performance issues with large datasets

**Problem**: Slow performance with large DataFrames (100K+ rows).

**Solutions**:
1. Use pagination (enabled by default for detail rows)
2. Filter data before aggregation
3. Use configuration to disable unnecessary features

```python
from luxin import Inspector, TrackedDataFrame
from luxin.config import InspectorConfig

config = InspectorConfig(
    show_summary_stats=False,
    detail_page_size=50,
)

df = TrackedDataFrame(large_data)
filtered_df = df[df['date'] > '2024-01-01']
agg = filtered_df.groupby('category').sum()
inspector = Inspector(agg, config=config)
inspector.render()
```

## Polars DataFrame not working

**Problem**: Polars DataFrame not recognized or converted properly.

**Solution**:
```python
# Make sure Polars is installed
pip install polars

# Convert Polars to TrackedDataFrame
import polars as pl
from luxin import create_tracked_from_polars, Inspector

polars_df = pl.DataFrame(...)
tracked_df = create_tracked_from_polars(polars_df)
agg = tracked_df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()
```

## Export functionality not working

**Problem**: Excel export button shows error or doesn't work.

**Solution**:
```bash
# Install openpyxl for Excel export
pip install openpyxl
```

CSV and JSON exports work without additional dependencies.

## Multi-column groupby issues

**Problem**: Issues with multi-column groupby operations.

**Solution**: Ensure all groupby columns exist in the DataFrame:
```python
df = TrackedDataFrame({
    'region': ['North', 'North', 'South'],
    'product': ['A', 'B', 'A'],
    'sales': [100, 200, 150]
})

# ✅ Correct - all columns exist
agg = df.groupby(['region', 'product']).sum()

# ❌ Wrong - column doesn't exist
agg = df.groupby(['region', 'category']).sum()  # 'category' doesn't exist
```

## Session state conflicts

**Problem**: Multiple Inspector or drill hierarchies collide in Streamlit `session_state`.

**Solution**: Use distinct configuration:

```python
from luxin.config import InspectorConfig

cfg = InspectorConfig(inspector_session_key="sales_tab")
inspector = Inspector(agg, config=cfg)
```

For multi-level drill, set **`DrillHierarchySpec.session_key`** per hierarchy. See also [Phase 3 in the roadmap](roadmap.md).

## Manual drill and NA group keys

**Problem:** Using **`create_drill_table`** or **`build_manual_source_mapping`**, detail rows are empty for aggregate rows whose group key contains **missing values** (`NaN`, `NaT`, `pd.NA`) with **`groupby(..., dropna=False)`**.

**Solution:** Upgrade to a release that includes the **Unreleased** fixes documented in [Changelog](changelog.md) (NA-aware masks on detail columns). Prefer **`TrackedDataFrame`** groupby when you can rebuild the aggregate so lineage is automatic.

## `show_drill_table` without Streamlit

**Problem:** Calling **`TrackedDataFrame.show_drill_table()`** in an environment where **Streamlit** is not importable.

**Behavior:** The method tries **`luxin.inspector.Inspector`** first; if that fails only because **`luxin`** or **Streamlit** is missing, it falls back to **`luxin_nb`** when installed.

**Solution:** For notebooks, run **`pip install luxin[notebook]`** (or **`luxin-nb`**) and use Jupyter/IPython. For apps, install Streamlit and use **`Inspector(agg).render()`** inside **`streamlit run`**.

## Getting Help

If you encounter issues not covered here:

1. Check the [API Reference](api-reference.md)
2. Review [Examples](examples.md)
3. Open an issue on [GitHub](https://github.com/eddiethedean/luxin/issues)

