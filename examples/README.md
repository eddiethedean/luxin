# Luxin Examples

Runnable **Streamlit** scripts and Jupyter notebooks demonstrating Luxin **v0.3.0**.

## Streamlit scripts

Use `Inspector(agg).render()` (recommended API). Older `create_drill_table` patterns still exist for legacy integrations but emit deprecation notices where applicable.

### `basic_usage.py`

Core flow: `TrackedDataFrame` → `groupby` → `Inspector` → `render()`.

```bash
streamlit run examples/basic_usage.py
```

### `sales_analysis.py`

Richer sales-style exploration (multi-level groupby, etc.).

```bash
streamlit run examples/sales_analysis.py
```

### `phase3_multi_level.py` (v0.3.0)

Optional Phase 3 flags: multi-level drill (`DrillHierarchySpec`), data-quality panel, aggregation builder footer, comparison API hint.

```bash
streamlit run examples/phase3_multi_level.py
```

### Optional extras

```bash
pip install 'luxin[compare]'   # SciPy for optional t-tests in luxin.compare.inspect_pair
pip install 'luxin[polars]'
```

Interactive tables require **Streamlit >= 1.35**.

## Jupyter notebooks

Notebook copies of some flows live beside these scripts (`01_getting_started.ipynb`, etc.). In notebooks you can still use `Inspector(...).render()` inside a compatible Streamlit context, or browse legacy HTML backends as documented—prefer migrating to **`Inspector`** for parity with Streamlit apps.

## Legacy snippets (avoid in new apps)

Older docs sometimes showed:

```python
agg.show_drill_table()       # deprecated; use Inspector(agg).render()
create_drill_table(...)      # legacy; prefer TrackedDataFrame + Inspector
```

See [Migration guide](../docs/migration.md).
