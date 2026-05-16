# Luxin

> A Streamlit-first Python package for interactive data exploration with drill-down capabilities. Click on aggregated rows to instantly see the underlying detail data.

[![PyPI version](https://badge.fury.io/py/luxin.svg)](https://badge.fury.io/py/luxin)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://readthedocs.org/projects/luxin/badge/?version=latest)](https://luxin.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Documentation:** **[luxin.readthedocs.io](https://luxin.readthedocs.io/en/latest/)** (built with MkDocs from the `docs/` directory).

Luxin helps you explore aggregated data interactively through an intuitive, Streamlit-native interface. Perfect for data scientists, analysts, and engineers who need to drill down into summary statistics to understand the underlying data.

## ✨ Key Features

* 🔍 **Interactive drill-down** - Click on aggregated rows to see source data instantly
* 📊 **Streamlit-native UI** - Fully integrated with Streamlit's native widgets
* 🐼 **Pandas support** - Works seamlessly with pandas DataFrames
* 🦀 **Polars support** - Optional support for Polars DataFrames
* 🎯 **Automatic tracking** - TrackedDataFrame automatically tracks source rows during aggregations
* 📓 **Jupyter support** - Also works in Jupyter notebooks (legacy HTML backend)
* 🚀 **Zero-config** - Get started with minimal setup
* 🎨 **Modern UI** - Clean, responsive interface with side-by-side detail view
* 📈 **Multi-column grouping** - Support for complex multi-level aggregations
* 🔧 **Configurable** - Customize UI behavior with `InspectorConfig` (`luxin.config`)
* 🧭 **Phase 3 (v0.3.0)** - Optional multi-level drill (`DrillHierarchySpec`), comparison views (`luxin.compare`), data-quality panel, and aggregation builder—all feature-flagged; defaults stay backward compatible
* ✅ **Well-tested** - 85%+ test coverage with comprehensive test suite

## 📦 Installation

```bash
pip install luxin
```

Optional extras:

```bash
pip install luxin[notebook]  # Jupyter/HTML drill-down (luxin-nb)
pip install luxin[polars]    # Polars → pandas / TrackedDataFrame helpers
pip install luxin[compare]   # SciPy for optional Welch t-tests in luxin.compare.inspect_pair
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
2. **Aggregate** - Use `TrackedDataFrame.groupby()` with tracked reductions only: `.agg(...)`, `.sum()`, `.mean()`, `.count()`, `.min()`, `.max()`, `.std()`, `.var()`, `.median()`. Other pandas GroupBy APIs (e.g. `.apply()`, `.transform()`, `.pipe()`) are not supported because they cannot preserve drill lineage.
3. **Inspect** - Use `Inspector(agg_df).render()` to see interactive view
4. **Drill Down** - Select any aggregated row to see underlying detail data

**Pre-aggregated workflows:** use **`create_drill_table(agg_df, detail_df, groupby_cols)`** when the aggregate already exists (see the [User Guide](https://luxin.readthedocs.io/en/latest/user-guide/)). Manual source mapping is **NA-aware** for **`groupby(..., dropna=False)`** keys; see the [Changelog](https://luxin.readthedocs.io/en/latest/changelog/).

**Note:** **`TrackedDataFrame.show_drill_table()`** tries **`Inspector`** (Streamlit) first; if Streamlit is not importable, it attempts **`luxin_nb`** — install **`luxin[notebook]`** for Jupyter.

* Exploring sales data by region, then drilling into individual transactions
* Analyzing error logs by error type, then viewing specific error instances
* Reviewing survey responses by category, then reading individual responses
* Investigating performance metrics by service, then examining individual requests
* Understanding aggregated statistics by drilling into source data

## 📖 Examples

Check out the example files:

- [Basic Usage](https://github.com/eddiethedean/luxin/blob/master/examples/basic_usage.py) - Simple examples of Inspector API
- [Sales Analysis](https://github.com/eddiethedean/luxin/blob/master/examples/sales_analysis.py) - Real-world sales data exploration
- [Phase 3 demo](https://github.com/eddiethedean/luxin/blob/master/examples/phase3_multi_level.py) - Multi-level drill, quality panel, aggregation builder flags

Run examples with Streamlit:
```bash
streamlit run examples/basic_usage.py
streamlit run examples/sales_analysis.py
streamlit run examples/phase3_multi_level.py
```

## 📚 Documentation

Full guides and API notes live on **[Read the Docs](https://luxin.readthedocs.io/en/latest/)**:

- [Getting Started](https://luxin.readthedocs.io/en/latest/getting-started/) — Installation and basic usage
- [User Guide](https://luxin.readthedocs.io/en/latest/user-guide/) — Comprehensive usage
- [API Reference](https://luxin.readthedocs.io/en/latest/api-reference/) — Public API surface
- [Examples](https://luxin.readthedocs.io/en/latest/examples/) — Walkthroughs and patterns
- [Troubleshooting](https://luxin.readthedocs.io/en/latest/troubleshooting/) — Common issues
- [Migration Guide](https://luxin.readthedocs.io/en/latest/migration/) — Upgrading from legacy APIs
- [Changelog](https://luxin.readthedocs.io/en/latest/changelog/) — Release history
- [Roadmap](https://luxin.readthedocs.io/en/latest/roadmap/) — Planned work
- [Releasing](https://luxin.readthedocs.io/en/latest/releasing/) — Maintainers: monorepo version alignment and PyPI checklist

**Contributors:** Markdown sources are in [`docs/`](https://github.com/eddiethedean/luxin/tree/master/docs). Preview locally with `mkdocs serve` ([`mkdocs.yml`](https://github.com/eddiethedean/luxin/blob/master/mkdocs.yml)).

## 🛠️ Development

```bash
# Clone and install (monorepo: core + notebook package needed to run tests)
git clone https://github.com/eddiethedean/luxin.git
cd luxin
pip install -e ./luxin_core -e ./luxin_nb -e ".[dev]"

# Run tests (if global pytest plugins emit async-fixture errors on your machine,
# autoload is disabled — load the coverage plugin explicitly when needed):
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/

# Combined coverage for luxin + luxin_core + luxin_nb (matches CI):
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -p pytest_cov \
  --cov=luxin --cov=luxin_core --cov=luxin_nb --cov-report=term --cov-fail-under=79

# HTML report
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -p pytest_cov \
  --cov=luxin --cov=luxin_core --cov=luxin_nb --cov-report=html
```

Optional markers (see `pytest.ini`): `-m streamlit`, `-m notebook`, `-m polars`, `-m slow`.

### Test Coverage

CI enforces a minimum **combined line coverage** across `luxin`, `luxin_core`, and `luxin_nb` (`--cov-fail-under=79` in `.github/workflows/ci.yml`). The suite includes:
- Core Inspector functionality
- UI components (table view, drill stack, breadcrumbs, detail panel, filters, export, Phase 3 modules)
- Jupyter/HTML rendering (`luxin_nb`)
- Data validation and error handling
- Polars integration
- Configuration management
- Integration workflows

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

**Releasing a version:** follow the [Releasing](https://luxin.readthedocs.io/en/latest/releasing/) guide. In short: align each package’s `pyproject.toml` **`project.version`** and **`__version__`** in `luxin/__init__.py`, `luxin_core/luxin_core/__init__.py`, and `luxin_nb/luxin_nb/__init__.py`, update `CHANGELOG.md`, then create and push an annotated tag `vX.Y.Z` (for example `v0.4.1`). The tag must match those versions: the PyPI workflow checks `pyproject.toml` and `__version__` before publishing.

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](https://github.com/eddiethedean/luxin/blob/master/LICENSE) file for details.

## 📌 Current release

**v0.4.1** — **mypy**-clean `DrillHierarchySpec` / detail-panel hashing for CI; README and **PyPI** **`Documentation`** URLs emphasize **Read the Docs** (`/en/latest/`). See the [Changelog](https://luxin.readthedocs.io/en/latest/changelog/) (canonical copy also at [`CHANGELOG.md`](https://github.com/eddiethedean/luxin/blob/master/CHANGELOG.md) in the repo).

**Requirements**: **Streamlit >= 1.35** for dataframe row selection (`on_select` / `selection_mode`).

## 🗺️ Roadmap

See the [Roadmap](https://luxin.readthedocs.io/en/latest/roadmap/) for the full picture. At a glance:

- **v0.3.0**: Phase 3 shipped — optional drill hierarchy, `luxin.compare`, quality dashboard, aggregation builder
- **v0.4.x** (current packaging line): aligned PyPI packages, notebook HTML tests, CI/release hygiene (not the Phase 1 feature milestone)
- **target v0.5.0**: Phase 1 core enhancements (charts, richer filters, performance, export)
- **target v0.6.0**: Phase 2 data sources (SQL, cloud, APIs)
- **target v0.7.0**: Phase 4 collaboration & sharing
- **target v1.0.0**: Phase 5 enterprise features

## 🔗 Links

* **🐙 GitHub Repository**: https://github.com/eddiethedean/luxin
* **📦 PyPI Package**: https://pypi.org/project/luxin/
* **📚 Documentation**: https://luxin.readthedocs.io/en/latest/
* **🐛 Issues**: https://github.com/eddiethedean/luxin/issues

---

**Made with ❤️ for the data exploration community**
