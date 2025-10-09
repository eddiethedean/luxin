# Luxin

Interactive HTML tables with drill-down capabilities for exploring aggregated data in Jupyter notebooks and Streamlit apps.

## Overview

Luxin allows you to create interactive tables that let you click on aggregated rows to see the underlying detail data. Like the magical substance from the Lightbringer series that can be shaped and manipulated, Luxin helps you shape and explore your data at different levels of granularity.

## Features

- 🔍 **Drill-down exploration**: Click on aggregated rows to see source data
- 📊 **Automatic tracking**: TrackedDataFrame automatically tracks source rows during aggregations
- 🎯 **Manual API**: Link aggregated and detail data manually for any workflow
- 📓 **Jupyter support**: Works seamlessly in Jupyter notebooks
- 🚀 **Streamlit support**: Build interactive Streamlit apps
- 🎨 **Modern UI**: Clean, responsive interface with side panel display

## Installation

```bash
pip install luxin
```

For Streamlit support:
```bash
pip install luxin[streamlit]
```

For Polars support:
```bash
pip install luxin[polars]
```

## Quick Start

### Automatic Tracking

```python
from luxin import TrackedDataFrame
import pandas as pd

# Create a TrackedDataFrame
df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

# Aggregate data - tracking is automatic
agg = df.groupby(['category']).agg({'sales': 'sum', 'profit': 'sum'})

# Display with drill-down capability
agg.show_drill_table()
```

### Manual API

```python
from luxin import create_drill_table
import pandas as pd

# Your existing workflow
df = pd.DataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

agg_df = df.groupby(['category']).sum()

# Create interactive drill-down table
create_drill_table(agg_df, df, groupby_cols=['category'])
```

## How It Works

When you aggregate data, Luxin tracks which source rows contribute to each aggregated row. When you click on a row in the displayed table, a side panel slides in showing all the detail rows that were aggregated to create that summary.

## Use Cases

- Exploring sales data by region, then drilling into individual transactions
- Analyzing error logs by error type, then viewing specific error instances
- Reviewing survey responses by category, then reading individual responses
- Investigating performance metrics by service, then examining individual requests

## License

MIT License - see LICENSE file for details.

