# Luxin Documentation

Welcome to the Luxin documentation! Luxin is a Streamlit-first Python package for interactive data exploration with drill-down capabilities.

## What is Luxin?

Luxin helps you explore aggregated data interactively through an intuitive, Streamlit-native interface. Click on aggregated rows to instantly see the underlying detail data in a side panel.

## Quick Navigation

- [Getting Started](getting-started.md) - Installation and basic usage
- [User Guide](user-guide.md) - Comprehensive usage documentation
- [API Reference](api-reference.md) - Complete API documentation
- [Examples](examples.md) - Code examples and tutorials
- [Troubleshooting](troubleshooting.md) - Common issues
- [Migration Guide](migration.md) - Upgrading from older APIs
- [Changelog](changelog.md) - Release history
- [Roadmap](roadmap.md) - Future features and development plans
- [Releasing](releasing.md) - Monorepo version alignment and PyPI checklist

## Key Features

* 🔍 **Interactive drill-down** - Click on aggregated rows to see source data instantly
* 📊 **Streamlit-native UI** - Fully integrated with Streamlit's native widgets
* 🐼 **Pandas support** - Works seamlessly with pandas DataFrames
* 🎯 **Automatic tracking** — `TrackedDataFrame` tracks source rows through `groupby().agg()`
* 🚀 **Zero-config** — sensible defaults for a working drill-down table
* 🦀 **Polars support** — optional `luxin[polars]` converters
* 🧭 **Phase 3 (v0.3.0)** — optional multi-level drill, `luxin.compare`, data-quality panel, aggregation builder (`InspectorConfig` flags; see [User Guide](user-guide.md))

## Installation

```bash
pip install luxin
```

Optional: `pip install luxin[notebook]` (Jupyter/HTML via `luxin-nb`) · `pip install luxin[polars]` · `pip install luxin[compare]` (SciPy for comparison significance tests).

**Streamlit**: use **>= 1.35** so interactive row selection works (see [Troubleshooting](troubleshooting.md)).

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

