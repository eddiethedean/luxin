# Getting Started

This guide will help you get started with Luxin quickly.

## Installation

### Basic Installation

```bash
pip install luxin
```

### Optional Dependencies

For Polars support:
```bash
pip install luxin[polars]
```

For optional **SciPy**-backed statistical tests in **`luxin.compare.inspect_pair`**:
```bash
pip install luxin[compare]
```

For **Jupyter / HTML** drill-down (`luxin_nb`, used by **`create_drill_table`** and **`TrackedDataFrame.show_drill_table`** when not in Streamlit):
```bash
pip install luxin[notebook]
```

## Requirements

- Python 3.8 or higher
- pandas >= 1.3.0
- **streamlit >= 1.35** (Luxin relies on dataframe row selection: `on_select` / `selection_mode`)

## Your First Luxin App

Create a file called `app.py`:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

st.title("My First Luxin App")

# Create a TrackedDataFrame
df = TrackedDataFrame({
    'category': ['Electronics', 'Electronics', 'Clothing', 'Clothing', 'Food'],
    'product': ['Laptop', 'Mouse', 'Shirt', 'Pants', 'Apple'],
    'sales': [1000, 50, 30, 45, 2],
    'profit': [200, 10, 10, 15, 0.5]
})

# Aggregate by category
agg = df.groupby(['category']).agg({
    'sales': 'sum',
    'profit': 'sum'
})

# Display with Inspector
inspector = Inspector(agg)
inspector.render()
```

Run it with:

```bash
streamlit run app.py
```

## How It Works

1. **Create TrackedDataFrame** - Wrap your data in `TrackedDataFrame` to enable automatic tracking
2. **Aggregate** - Use standard pandas `groupby().agg()` operations
3. **Inspect** - Use `Inspector(agg_df).render()` to see the interactive view
4. **Drill Down** - Select any aggregated row to see underlying detail data

**Tip:** `Inspector` uses a stable widget key per instance so row selection and pagination survive Streamlit reruns. Recomputing `agg = df.groupby(...).agg(...)` on every run still works without losing selection; for very hot paths you can cache the aggregated frame with `st.cache_data` as usual.

## Next Steps

- Read the [User Guide](user-guide.md), including Phase 3 optional features (v0.3.0+) and coordinated **`luxin` / `luxin-core` / `luxin-nb`** releases (**v0.4.x**)
- Check out [Examples](examples.md) and run `examples/phase3_multi_level.py` with Streamlit
- Explore the [API Reference](api-reference.md) for `Inspector`, `InspectorConfig`, **`create_drill_table`**, and `DrillHierarchySpec`

