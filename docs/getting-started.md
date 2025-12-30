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

## Requirements

- Python 3.8 or higher
- pandas >= 1.3.0
- streamlit >= 1.0.0

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

## Next Steps

- Read the [User Guide](user-guide.md) for comprehensive usage documentation
- Check out [Examples](examples.md) for more code samples
- Explore the [API Reference](api-reference.md) for detailed API documentation

