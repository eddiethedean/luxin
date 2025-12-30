# Luxin Documentation

Welcome to the Luxin documentation! Luxin is a Streamlit-first Python package for interactive data exploration with drill-down capabilities.

## What is Luxin?

Luxin helps you explore aggregated data interactively through an intuitive, Streamlit-native interface. Click on aggregated rows to instantly see the underlying detail data in a side panel.

## Quick Navigation

- [Getting Started](getting-started.md) - Installation and basic usage
- [User Guide](user-guide.md) - Comprehensive usage documentation
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Code examples and tutorials
- [Roadmap](roadmap.md) - Future features and development plans

## Key Features

* 🔍 **Interactive drill-down** - Click on aggregated rows to see source data instantly
* 📊 **Streamlit-native UI** - Fully integrated with Streamlit's native widgets
* 🐼 **Pandas support** - Works seamlessly with pandas DataFrames
* 🎯 **Automatic tracking** - TrackedDataFrame automatically tracks source rows during aggregations
* 🚀 **Zero-config** - Get started with minimal setup

## Installation

```bash
pip install luxin
```

## Quick Start

```python
import streamlit as st
from luxin import Inspector, TrackedDataFrame

# Create a TrackedDataFrame
df = TrackedDataFrame({
    'category': ['A', 'A', 'B', 'B', 'C'],
    'sales': [100, 150, 200, 250, 300]
})

# Aggregate data - tracking is automatic
agg = df.groupby(['category']).agg({'sales': 'sum'})

# Display with drill-down capability
inspector = Inspector(agg)
inspector.render()
```

Save this as `app.py` and run `streamlit run app.py` to see the interactive dashboard.

## Resources

* **🐙 GitHub Repository**: https://github.com/eddiethedean/luxin
* **📦 PyPI Package**: https://pypi.org/project/luxin/
* **🐛 Issues**: https://github.com/eddiethedean/luxin/issues

