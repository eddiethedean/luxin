# Luxin

> A Streamlit-first Python package for interactive data exploration with drill-down capabilities. Click on aggregated rows to instantly see the underlying detail data.

[![PyPI version](https://badge.fury.io/py/luxin.svg)](https://badge.fury.io/py/luxin)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Luxin helps you explore aggregated data interactively through an intuitive, Streamlit-native interface. Perfect for data scientists, analysts, and engineers who need to drill down into summary statistics to understand the underlying data.

## ✨ Key Features

* 🔍 **Interactive drill-down** - Click on aggregated rows to see source data instantly
* 📊 **Streamlit-native UI** - Fully integrated with Streamlit's native widgets
* 🐼 **Pandas support** - Works seamlessly with pandas DataFrames
* 🎯 **Automatic tracking** - TrackedDataFrame automatically tracks source rows during aggregations
* 📓 **Jupyter support** - Also works in Jupyter notebooks (legacy HTML backend)
* 🚀 **Zero-config** - Get started with minimal setup
* 🎨 **Modern UI** - Clean, responsive interface with side-by-side detail view
* 📈 **Multi-column grouping** - Support for complex multi-level aggregations

## 📦 Installation

```bash
pip install luxin
```

For Polars support (optional):
```bash
pip install luxin[polars]
```

## 🚀 Quick Start

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame
import pandas as pd

# Load your data
df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300],
    'profit': [10, 15, 20, 25, 30]
})

# Aggregate data - tracking is automatic
agg = df.groupby(['category']).agg({'sales': 'sum', 'profit': 'sum'})

# Display with drill-down capability
inspector = Inspector(agg)
inspector.render()  # Must be called within a Streamlit app context
```

Save this as `app.py` and run `streamlit run app.py` to see the interactive dashboard.

## 📚 Usage Examples

### Basic Usage

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

# Create a TrackedDataFrame
df = TrackedDataFrame({
    'region': ['North', 'North', 'South', 'South'],
    'sales': [100, 200, 150, 250]
})

# Aggregate and inspect
agg = df.groupby('region').sum()
inspector = Inspector(agg)
inspector.render()
```

### With Regular Pandas DataFrame

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame
import pandas as pd

# Your existing workflow
df = pd.DataFrame({
    'category': ['A', 'A', 'B', 'B'],
    'sales': [100, 200, 150, 250]
})

# Convert to TrackedDataFrame for aggregation tracking
tracked_df = TrackedDataFrame(df)
agg = tracked_df.groupby('category').sum()

# Use Inspector
inspector = Inspector(agg)
inspector.render()
```

### Multi-Column Grouping

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

df = TrackedDataFrame({
    'region': ['North', 'North', 'South', 'South'],
    'product': ['A', 'B', 'A', 'B'],
    'sales': [100, 150, 200, 250]
})

# Group by multiple columns
agg = df.groupby(['region', 'product']).sum()

# Inspect with drill-down
inspector = Inspector(agg)
inspector.render()
```

## 🎯 How It Works

When you aggregate data using `TrackedDataFrame.groupby().agg()`, Luxin automatically tracks which source rows contribute to each aggregated row. When you select a row in the Inspector interface, a side panel shows all the detail rows that were aggregated to create that summary.

1. **Create TrackedDataFrame** - Wrap your data in `TrackedDataFrame`
2. **Aggregate** - Use standard pandas `groupby().agg()` operations
3. **Inspect** - Use `Inspector(agg_df).render()` to see interactive view
4. **Drill Down** - Select any aggregated row to see underlying detail data

## 💡 Use Cases

* Exploring sales data by region, then drilling into individual transactions
* Analyzing error logs by error type, then viewing specific error instances
* Reviewing survey responses by category, then reading individual responses
* Investigating performance metrics by service, then examining individual requests
* Understanding aggregated statistics by drilling into source data

## 📖 Examples

Check out the example files:

- [Basic Usage](examples/basic_usage.py) - Simple examples of Inspector API
- [Sales Analysis](examples/sales_analysis.py) - Real-world sales data exploration

Run examples with Streamlit:
```bash
streamlit run examples/basic_usage.py
streamlit run examples/sales_analysis.py
```

## 🛠️ Development

```bash
# Clone and install
git clone https://github.com/eddiethedean/luxin.git
cd luxin
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

* **🐙 GitHub Repository**: https://github.com/eddiethedean/luxin
* **📦 PyPI Package**: https://pypi.org/project/luxin/
* **🐛 Issues**: https://github.com/eddiethedean/luxin/issues

---

**Made with ❤️ for the data exploration community**
