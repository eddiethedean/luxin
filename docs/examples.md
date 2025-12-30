# Examples

Code examples and tutorials for using Luxin.

## Basic Example

Simple example showing the core functionality:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

st.title("Basic Example")

df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

agg = df.groupby(['category']).agg({
    'sales': 'sum',
    'profit': 'sum'
})

inspector = Inspector(agg)
inspector.render()
```

## Sales Analysis Example

More realistic example with sales data:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame
import pandas as pd
import numpy as np

st.title("Sales Analysis")

# Generate sample sales data
np.random.seed(42)
data = {
    'transaction_id': range(1, 101),
    'category': np.random.choice(['Electronics', 'Clothing', 'Food'], 100),
    'region': np.random.choice(['North', 'South', 'East', 'West'], 100),
    'amount': np.random.uniform(10, 500, 100).round(2),
    'quantity': np.random.randint(1, 10, 100)
}

df = TrackedDataFrame(data)

# Analyze by category
st.header("Sales by Category")
agg_category = df.groupby(['category']).agg({
    'amount': ['sum', 'mean', 'count'],
    'quantity': 'sum'
})
inspector = Inspector(agg_category)
inspector.render()

# Analyze by region and category
st.header("Sales by Region and Category")
agg_region = df.groupby(['region', 'category']).agg({
    'amount': 'sum',
    'quantity': 'sum'
})
inspector2 = Inspector(agg_region)
inspector2.render()
```

## Multi-Column Grouping

Example with multiple grouping columns:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

df = TrackedDataFrame({
    'region': ['North', 'North', 'North', 'South', 'South', 'South'],
    'product': ['A', 'A', 'B', 'A', 'B', 'B'],
    'sales': [100, 150, 200, 120, 180, 220],
    'units': [10, 15, 8, 12, 9, 11]
})

agg = df.groupby(['region', 'product']).agg({
    'sales': ['sum', 'mean'],
    'units': 'sum'
})

inspector = Inspector(agg)
inspector.render()
```

## Working with Existing DataFrames

If you already have a pandas DataFrame:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame
import pandas as pd

# Your existing workflow
df = pd.read_csv('sales_data.csv')

# Convert to TrackedDataFrame for aggregation tracking
tracked_df = TrackedDataFrame(df)

# Aggregate
agg = tracked_df.groupby('category').sum()

# Inspect
inspector = Inspector(agg)
inspector.render()
```

## Custom Aggregations

Example with custom aggregation functions:

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame
import numpy as np

df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

# Multiple aggregation functions
agg = df.groupby('category').agg({
    'sales': ['sum', 'mean', 'std', 'min', 'max'],
    'profit': ['sum', 'mean']
})

inspector = Inspector(agg)
inspector.render()
```

## Running Examples

All examples can be run with Streamlit:

```bash
streamlit run your_example.py
```

Or check out the example files in the `examples/` directory:

```bash
streamlit run examples/basic_usage.py
streamlit run examples/sales_analysis.py
```

