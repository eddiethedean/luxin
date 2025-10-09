# Luxin Examples

This directory contains example scripts and notebooks demonstrating how to use Luxin.

## Examples

### 1. basic_usage.py
Demonstrates the basic features of Luxin:
- Using `TrackedDataFrame` for automatic tracking
- Using `create_drill_table()` for manual API
- Multi-column groupby operations

Run with:
```bash
python basic_usage.py
```

### 2. sales_analysis.py
A more realistic example showing how to analyze sales data with drill-down capabilities:
- Analyzing sales by category
- Analyzing sales by region and category
- Finding top customers

Run with:
```bash
python sales_analysis.py
```

## Jupyter Notebooks

To see the interactive drill-down tables in action, create a Jupyter notebook and run:

```python
from luxin import TrackedDataFrame

# Create your data
df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'value': [10, 20, 30, 40, 50]
})

# Aggregate
agg = df.groupby('category').agg({'value': 'sum'})

# Display with drill-down
agg.show_drill_table()
```

Click on any row in the aggregated table to see the underlying detail rows in the side panel!

## Streamlit Apps

To use Luxin in a Streamlit app:

```python
import streamlit as st
from luxin import create_drill_table
import pandas as pd

st.title("Sales Analysis")

# Your data
df = pd.DataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'value': [10, 20, 30, 40, 50]
})

agg_df = df.groupby('category').sum()

# Display drill-down table
create_drill_table(agg_df, df, groupby_cols=['category'])
```

Run with:
```bash
streamlit run your_app.py
```

