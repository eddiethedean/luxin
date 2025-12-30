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
```bash
# Install Streamlit
pip install streamlit

# Or install luxin with Streamlit
pip install luxin[streamlit]
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
from luxin import Inspector, TrackedDataFrame, InspectorConfig

# Filter before aggregating
df = TrackedDataFrame(large_data)
filtered_df = df[df['date'] > '2024-01-01']  # Filter first
agg = filtered_df.groupby('category').sum()

# Use config to optimize
config = InspectorConfig(
    show_summary_stats=False,  # Disable if not needed
    detail_page_size=50  # Smaller page size
)
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

**Problem**: Multiple Inspector instances conflict with each other.

**Solution**: Inspector automatically uses unique keys based on DataFrame IDs. If you still have issues, create separate Streamlit apps or use different variable names.

## Getting Help

If you encounter issues not covered here:

1. Check the [API Reference](api-reference.md)
2. Review [Examples](examples.md)
3. Open an issue on [GitHub](https://github.com/eddiethedean/luxin/issues)

