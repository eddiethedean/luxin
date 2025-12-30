# API Reference

Complete API documentation for Luxin.

## Inspector

The main class for interactive data exploration.

### `Inspector(df: pd.DataFrame)`

Initialize the Inspector with a DataFrame.

**Parameters:**
- `df` (pd.DataFrame): The DataFrame to inspect. Can be a regular pandas DataFrame or a TrackedDataFrame with aggregation tracking.

**Example:**
```python
from luxin import Inspector, TrackedDataFrame

df = TrackedDataFrame({'category': ['A', 'B'], 'value': [10, 20]})
agg = df.groupby('category').sum()
inspector = Inspector(agg)
```

### `Inspector.render()`

Render the interactive drill-down interface in Streamlit.

**Returns:** None

**Raises:**
- `ImportError`: If Streamlit is not installed

**Example:**
```python
inspector = Inspector(agg_df)
inspector.render()  # Must be called within Streamlit app context
```

## TrackedDataFrame

A pandas DataFrame subclass that tracks source rows during aggregations.

### `TrackedDataFrame(*args, **kwargs)`

Create a new TrackedDataFrame. Accepts the same arguments as `pd.DataFrame`.

**Example:**
```python
from luxin import TrackedDataFrame

df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B'],
    'value': [10, 20, 30, 40]
})
```

### `TrackedDataFrame.groupby(by=None, **kwargs)`

Override groupby to return a `TrackedGroupBy` object that tracks source rows.

**Parameters:**
- `by`: Column name(s) to group by (same as pandas)
- `**kwargs`: Additional arguments passed to pandas groupby

**Returns:** `TrackedGroupBy` object

**Example:**
```python
grouped = df.groupby('category')
```

### `TrackedDataFrame.show_drill_table()`

Display the interactive drill-down table (deprecated).

**Note:** This method is deprecated. Use `Inspector(df).render()` instead.

**Raises:**
- `ValueError`: If called on a non-aggregated DataFrame

## TrackedGroupBy

A wrapper around pandas GroupBy that tracks source row indices during aggregation.

### `TrackedGroupBy.agg(func=None, *args, **kwargs)`

Perform aggregation while tracking source row indices.

**Parameters:**
- `func`: Aggregation function(s) (same as pandas)
- `*args, **kwargs`: Additional arguments passed to pandas agg

**Returns:** `TrackedDataFrame` with aggregation tracking enabled

**Example:**
```python
agg = df.groupby('category').agg({'value': 'sum'})
```

### Convenience Methods

`TrackedGroupBy` provides convenience methods that mirror pandas:

- `sum(*args, **kwargs)` - Sum aggregation
- `mean(*args, **kwargs)` - Mean aggregation
- `count(*args, **kwargs)` - Count aggregation
- `min(*args, **kwargs)` - Min aggregation
- `max(*args, **kwargs)` - Max aggregation
- `std(*args, **kwargs)` - Standard deviation
- `var(*args, **kwargs)` - Variance
- `median(*args, **kwargs)` - Median

**Example:**
```python
agg = df.groupby('category').sum()
```

## Components

### `render_table_view(agg_df, detail_df, source_mapping, groupby_cols)`

Render the main table view with drill-down capabilities.

**Parameters:**
- `agg_df` (pd.DataFrame): The aggregated DataFrame to display
- `detail_df` (pd.DataFrame): The detail DataFrame containing source rows
- `source_mapping` (Dict): Dictionary mapping aggregated row keys to detail row indices
- `groupby_cols` (List[str]): List of column names used to group the data

### `render_detail_panel(detail_rows, title, height)`

Render a detail panel showing individual rows.

**Parameters:**
- `detail_rows` (pd.DataFrame): DataFrame containing the detail rows to display
- `title` (str): Title for the detail panel (default: "Detail Rows")
- `height` (int): Height of the dataframe display in pixels (default: 300)

