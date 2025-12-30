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

## UI Components

The Inspector interface includes:

- **Main Table** - Displays aggregated data with row selection
- **Detail Panel** - Shows underlying detail rows when a row is selected
- **Summary Statistics** - Expandable section with descriptive statistics

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

