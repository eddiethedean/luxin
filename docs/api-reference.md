# API Reference

Complete API documentation for Luxin.

## Inspector

The main class for interactive data exploration.

### `Inspector(df, *, config=None, drill=None)`

Initialize the Inspector with a DataFrame.

**Parameters:**
- `df` (pd.DataFrame): The DataFrame to inspect. Can be a regular pandas DataFrame or a TrackedDataFrame with aggregation tracking.
- `config` (`InspectorConfig`, optional): UI / feature flags (Phase 3 adds drill, quality, builder, and comparison-related toggles).
- `drill` (`DrillHierarchySpec`, optional): Declarative multi-level drill when `InspectorConfig.enable_multi_level_drill` is `True`.

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

## InspectorConfig

Defined in **`luxin.config`** (import `InspectorConfig`, `get_default_config`).

**Typical usage:**
```python
from luxin import Inspector
from luxin.config import InspectorConfig

inspector = Inspector(agg, config=InspectorConfig(show_filters=True))
```

**Core UI fields** (defaults favor the standard drill-down experience):

| Field | Default | Description |
|-------|---------|-------------|
| `show_summary_stats` | `True` | Expander with `describe()` on the aggregate |
| `show_export_buttons` | `True` | Export controls |
| `show_filters` | `True` | Column filters on the displayed aggregate |
| `detail_page_size` | `100` | Detail panel pagination |
| `table_height` | `400` | Main table height (px) |
| `detail_height` | `300` | Detail dataframe height (px) |

**Phase 3 (v0.3.0) fields** — all default to off unless noted:

| Field | Default | Description |
|-------|---------|-------------|
| `enable_multi_level_drill` | `False` | Use `render_drill_stack_view` when `Inspector(..., drill=DrillHierarchySpec(...))` is set |
| `max_drill_depth` | `8` | Cap on stacked drill depth (with `DrillHierarchySpec.max_depth`) |
| `show_data_quality` | `False` | Quality / outlier expander next to detail rows |
| `show_aggregation_builder` | `False` | Footer expander to rebuild aggregation from the root `_source_df` snapshot |
| `show_comparison_entrypoint` | `False` | Expander with snippet for `luxin.compare.inspect_pair` |
| `compare_run_significance` | `False` | Welch t-tests in comparison UI when SciPy is installed (`luxin[compare]`) |
| `inspector_session_key` | `None` | Optional stable string for `luxin_agg_override_*` / widget keys (else `hex(id(inspector))`) |

**Methods:** `to_dict()`, `from_dict(...)`, and module helper `get_default_config()`.

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

Display the drill-down table by routing to the current environment (deprecated as the primary API).

**Note:** Prefer `Inspector(agg).render()` for Streamlit apps. This method first tries `luxin.inspector.Inspector`; if that import fails only because **`luxin`** or **Streamlit** (`streamlit` / `streamlit.*`) is missing, it falls back to **`luxin_nb.display.display_drill_table`** when **`luxin-nb`** is installed (e.g. `pip install luxin[notebook]`).

**Raises:**

- `ValueError`: If called on a non-aggregated DataFrame, or aggregation metadata (e.g. `_source_df`) is missing when the Inspector path is skipped.
- `ImportError`: When neither Streamlit/`luxin` Inspector nor the notebook extra can run (message points to `luxin[notebook]` / `luxin-nb`).

## Manual drill-down (create_drill_table)

Use when you already have an **aggregated** frame and a **detail** frame and cannot rebuild the aggregate with `TrackedDataFrame` (legacy pipelines, SQL rollups, etc.).

### `create_drill_table(agg_df, detail_df, groupby_cols, **kwargs)`

Defined in **`luxin.drill_table`**. Validates inputs, builds a source mapping with **`build_manual_source_mapping`** (see **`luxin_core.drill_table`**), then calls **`luxin.display.display_drill_table`**, which chooses **Streamlit** or **Jupyter** based on the runtime (see **`luxin.streamlit_backend.display_streamlit`** / **`luxin_nb`**).

**Parameters:**

- `agg_df` (`pd.DataFrame`): Aggregated result; index must reflect group keys (flat index for single-column groupby, **`MultiIndex`** when grouping by multiple columns).
- `detail_df` (`pd.DataFrame`): Row-level data; must contain **`groupby_cols`**.
- `groupby_cols` (`List[str]`): Names aligned with `agg_df` index (**one** name for a flat index; **n** names matching **`agg_df.index.nlevels`** for a **`MultiIndex`**).
- `**kwargs`: Forwarded toward **`InspectorConfig`** when using the Streamlit path (see **`display_streamlit`**).

**When to prefer `TrackedDataFrame`:** Automatic lineage (`_source_mapping`, `_source_df`) from `TrackedDataFrame.groupby()` avoids recomputing masks and handles all tracked reducers consistently. Manual mapping builds masks over `detail_df`; missing-value keys with **`groupby(..., dropna=False)`** are matched in a NA-aware way as of the current **`[Unreleased]`** changelog.

### `build_manual_source_mapping(agg_df, detail_df, groupby_cols)` (`luxin_core.drill_table`)

Lower-level helper: returns a **`source_mapping`** (`dict` of normalized tuple keys to lists of detail index labels). Also available as **`luxin.drill_table.build_manual_source_mapping`** (re-export). Pair with **`validate_manual_drill_inputs`** when building UIs yourself.

## TrackedGroupBy

A wrapper around pandas GroupBy that tracks **detail index labels** during aggregation.

Only tracked reductions preserve drill lineage: ``agg(...)``, ``sum``, ``mean``, ``count``, ``min``, ``max``, ``std``, ``var``, and ``median``. Calling ``apply``, ``transform``, ``pipe``, or other pandas GroupBy APIs raises ``NotImplementedError`` or ``AttributeError`` with guidance to use ``agg``.

### `TrackedGroupBy.agg(func=None, *args, **kwargs)`

Perform aggregation while tracking source row labels for drill-down.

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
- `source_mapping` (Dict): Mapping from aggregated row keys to lists of detail index labels
- `groupby_cols` (List[str]): List of column names used to group the data

### `render_detail_panel(detail_rows, title, height, page_size, pagination_session_key)`

Render a detail panel showing individual rows (with pagination when ``len(detail_rows) > page_size``).

**Parameters:**
- `detail_rows` (pd.DataFrame): DataFrame containing the detail rows to display
- `title` (str): Title for the detail panel (default: "Detail Rows")
- `height` (int): Height of the dataframe display in pixels (default: 300)
- `page_size` (int): Rows per page when paginating (default: 100)
- `pagination_session_key` (str, optional): Stable Streamlit session/widget key prefix for pagination; if omitted, a hash of the frame contents is used

## DrillHierarchySpec

Defined in `luxin.drill_hierarchy` and exported as `luxin.DrillHierarchySpec`.

**Fields:** `session_key`, `max_depth`, `level_labels`, plus either `next_level` (`Callable[[tuple, pd.DataFrame], TrackedDataFrame]`) and/or `children_by_parent_key` mapping normalized parent keys to precomputed `TrackedDataFrame` aggregations.

## Comparison helpers

### `luxin.compare.inspect_pair`

```python
from luxin.compare import inspect_pair

inspect_pair(left_agg, right_agg, join_keys=["region"], config=inspector.config)
```

Renders two tables, a joined diff with `_left/_right/_delta/_pct_change` columns, and optional significance tests when `compare_run_significance=True` and SciPy is available (`pip install 'luxin[compare]'`).

### Package exports (`luxin`)

Stable symbols from **`luxin`** include: **`Inspector`**, **`TrackedDataFrame`**, **`DrillHierarchySpec`**, **`create_drill_table`**, Polars helpers (`create_tracked_from_polars`, `convert_polars_to_pandas`, `is_polars_dataframe`). Prefer **`InspectorConfig`** from **`luxin.config`**.

**Environment routing:** **`luxin.display.display_drill_table`** (and thus **`create_drill_table`**) dispatches to Streamlit inside `streamlit run` or to **`luxin_nb`** in Jupyter when the notebook extra is installed. **`render_html`** in **`luxin_nb`** returns HTML only.

**Deprecation:** **`from luxin import show_drill_table`** still works with a **`DeprecationWarning`** (wrapper delegates to **`TrackedDataFrame.show_drill_table`**). **`luxin.drill_table._build_source_mapping`** is deprecated in favor of **`build_manual_source_mapping`**.

