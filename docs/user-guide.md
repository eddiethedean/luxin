# User Guide

This guide provides comprehensive documentation for using Luxin.

## Core Concepts

### TrackedDataFrame

`TrackedDataFrame` is a pandas DataFrame subclass that automatically tracks which source rows contribute to each aggregated row during groupby operations.

```python
from luxin import TrackedDataFrame

df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B'],
    'value': [10, 20, 30, 40]
})

# When you aggregate, tracking happens automatically
agg = df.groupby('category').sum()
```

### Inspector

The `Inspector` class provides the main interface for interactive data exploration. It works with both `TrackedDataFrame` and regular pandas DataFrames.

```python
from luxin import Inspector

inspector = Inspector(agg_df)
inspector.render()  # Must be called within Streamlit app context
```

## Basic Usage Patterns

### Pattern 1: Automatic Tracking (Recommended)

Use `TrackedDataFrame` for automatic source row tracking:

```python
from luxin import Inspector, TrackedDataFrame

df = TrackedDataFrame(your_data)
agg = df.groupby(['column1', 'column2']).agg({'value': 'sum'})
inspector = Inspector(agg)
inspector.render()
```

### Pattern 2: Regular DataFrame

You can also use regular pandas DataFrames, but you'll need to convert to `TrackedDataFrame` before aggregating:

```python
import pandas as pd
from luxin import Inspector, TrackedDataFrame

df = pd.DataFrame(your_data)
tracked_df = TrackedDataFrame(df)
agg = tracked_df.groupby('category').sum()
inspector = Inspector(agg)
inspector.render()
```

## Advanced Usage

### Multi-Column Grouping

Luxin fully supports multi-column groupby operations:

```python
df = TrackedDataFrame({
    'region': ['North', 'North', 'South', 'South'],
    'product': ['A', 'B', 'A', 'B'],
    'sales': [100, 150, 200, 250]
})

agg = df.groupby(['region', 'product']).sum()
inspector = Inspector(agg)
inspector.render()
```

### Custom Aggregations

You can use any pandas aggregation function:

```python
agg = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'count'],
    'profit': 'sum',
    'quantity': ['min', 'max']
})

inspector = Inspector(agg)
inspector.render()
```

### Phase 3 — multi-level drill-down (v0.3.0)

Stack additional aggregations by passing a `DrillHierarchySpec` and enabling the feature flag:

```python
from luxin import Inspector, TrackedDataFrame, DrillHierarchySpec
from luxin.config import InspectorConfig

config = InspectorConfig(enable_multi_level_drill=True, max_drill_depth=4)

def drill_region(region_key, rows):
    tracked = TrackedDataFrame(rows)
    return tracked.groupby("product").agg({"value": "sum"})

spec = DrillHierarchySpec(
    session_key="demo_sales",
    max_depth=4,
    level_labels=["Region", "Product"],
    next_level=lambda key, rows: drill_region(key, rows),
)

df = TrackedDataFrame(
    {
        "region": ["N", "N", "S"],
        "product": ["A", "B", "A"],
        "value": [10, 20, 30],
    }
)
root = df.groupby("region").agg({"value": "sum"})
Inspector(root, config=config, drill=spec).render()
```

Breadcrumbs let you jump back to any ancestor slice. Session keys are namespaced (`luxin_drill_stack_{session_key}`) to avoid collisions across inspectors.

### Phase 3 — data quality, comparison, aggregation builder (v0.3.0)

- **`show_data_quality`** — adds a metrics / outlier-focused expander beside the detail pane.
- **`show_comparison_entrypoint`** — shows a small snippet pointing at `luxin.compare.inspect_pair`.
- **`show_aggregation_builder`** — footer expander builds a new aggregation from the snapshot of the original `_source_df` gathered at `Inspector` construction; results override the main table until cleared.
- **`compare_run_significance`** — when true and SciPy is installed (`pip install 'luxin[compare]'`), comparison mode can run Welch-style t-tests across aligned numeric columns.

## UI Components

The Inspector interface includes:

- **Main table** — Aggregated rows with interactive selection (**Streamlit 1.35+**)
- **Detail panel** — Rows that rolled up into the selected aggregate
- **Summary statistics** — Optional expander with `describe()` on the aggregate
- **Filters & export** — When enabled in `InspectorConfig`
- **Phase 3 (optional)** — Breadcrumb drill stack; data-quality expander beside details; footer **Build aggregation**; API hint expander for `luxin.compare`

## Tips and Best Practices

1. **Always use TrackedDataFrame** - For automatic tracking, wrap your data in `TrackedDataFrame` before aggregating
2. **Call render() in Streamlit** - `Inspector.render()` must be called within a Streamlit app context
3. **Handle large datasets** - For very large datasets, consider filtering before aggregation
4. **Use meaningful column names** - Clear column names make the drill-down interface more intuitive

## Troubleshooting

### Inspector shows "No detail rows found"

This usually means:
- The DataFrame wasn't created using `TrackedDataFrame`
- The aggregation wasn't performed on a `TrackedDataFrame`
- The source mapping wasn't properly tracked

Solution: Ensure you use `TrackedDataFrame` from the start and perform aggregations on it.

### Streamlit errors

If you see Streamlit-related errors:
- Ensure Streamlit is installed: `pip install streamlit`
- Make sure `render()` is called within a Streamlit app context
- Check that you're running the app with `streamlit run app.py`

