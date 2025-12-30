# Luxin Roadmap

This document outlines the future direction of Luxin, including planned feature enhancements, new capabilities, and technical improvements. The roadmap is organized by phases with priorities and implementation details.

## Executive Summary

Luxin aims to become the go-to tool for interactive data exploration in Streamlit applications. Our roadmap focuses on:

- **Enhanced Visualizations**: Adding charting capabilities to make data insights more intuitive
- **Expanded Data Sources**: Supporting SQL databases, cloud storage, and APIs
- **Advanced Features**: Multi-level drill-down, comparison mode, and data quality indicators
- **Collaboration Tools**: Sharing, annotations, and user preferences
- **Enterprise Readiness**: Authentication, audit logging, and scheduled reports

## Current State

Luxin is a Streamlit-first tool for interactive drill-down data exploration with:

- **Core Features**: `Inspector` class pattern, `TrackedDataFrame` for automatic source tracking
- **UI Components**: Native Streamlit components, filtering, export, pagination
- **Data Support**: Pandas, Polars (optional), Jupyter (legacy)
- **Code Quality**: 85% test coverage, modular architecture
- **Documentation**: Comprehensive docs with examples and API reference

See the [User Guide](user-guide.md) for current capabilities and the [API Reference](api-reference.md) for detailed documentation.

## Roadmap Phases

### Phase 1: Core Enhancements (v0.3.0)

**Timeline**: Q1 2024  
**Priority**: High  
**Effort**: Medium

#### 1.1 Enhanced Visualizations

Add charting capabilities when viewing detail rows to make data insights more intuitive.

**Features**:
- Bar charts for categorical breakdowns
- Line charts for time series data
- Histograms for numeric distributions
- Auto-detection of chart types based on data

**Implementation**:
- New component: `luxin/components/charts.py` using `plotly` or `streamlit-plotly`
- Extend `InspectorConfig` with `show_charts: bool = True`
- Integrate into `luxin/components/detail_panel.py`

**Files to Create/Modify**:
- `luxin/components/charts.py` (new)
- `luxin/config.py` (add chart config options)
- `luxin/components/detail_panel.py` (integrate charts)

**Dependencies**: `plotly>=5.0.0`

#### 1.2 Advanced Filtering

Enhance filtering capabilities with more sophisticated options.

**Features**:
- Multi-level filters with AND/OR logic
- Date range pickers for temporal data
- Regex support for text filtering
- Saved filter presets
- Column-specific filter types (auto-detect appropriate widgets)

**Implementation**:
- Extend `luxin/components/filters.py` with filter builder
- Add filter preset storage/loading
- Enhance `InspectorConfig` with filter options

**Files to Create/Modify**:
- `luxin/components/filters.py` (enhance existing)
- `luxin/config.py` (add filter config)

#### 1.3 Performance Optimization

Improve performance for large datasets.

**Features**:
- Lazy loading: Load detail rows on-demand instead of all at once
- Caching: Cache filtered/aggregated results using Streamlit's caching
- Virtual scrolling: For tables with 10K+ rows

**Implementation**:
- New module: `luxin/performance.py` with caching utilities
- Integrate lazy loading into `luxin/components/table_view.py`
- Add virtual scrolling component

**Files to Create/Modify**:
- `luxin/performance.py` (new)
- `luxin/components/table_view.py` (add lazy loading)
- `luxin/utils.py` (add caching helpers)

#### 1.4 Enhanced Export

Expand export capabilities beyond CSV, JSON, and Excel.

**Features**:
- Export detail rows: Export the currently visible detail rows
- Export with filters applied: Export filtered views
- PDF export: Generate PDF reports with tables and charts

**Implementation**:
- Extend `luxin/components/export.py` with PDF generation
- Add filtered export options
- Integrate with chart exports

**Files to Create/Modify**:
- `luxin/components/export.py` (enhance existing)

**Dependencies**: `reportlab>=4.0.0` or `weasyprint` (for PDF export)

---

### Phase 2: Data Source Expansion (v0.4.0)

**Timeline**: Q2 2024  
**Priority**: Medium  
**Effort**: High

#### 2.1 SQL Database Integration

Enable direct connection to SQL databases and create TrackedDataFrame from queries.

**Features**:
- Direct SQL queries: Connect to databases and create TrackedDataFrame from queries
- Supported databases: PostgreSQL, MySQL, SQLite, SQL Server
- Query builder: Visual query builder for non-SQL users (optional)

**Implementation**:
- New module: `luxin/data_sources/` package
- SQL connector: `luxin/data_sources/sql.py` with SQLAlchemy integration
- Helper functions for common database operations

**Files to Create/Modify**:
- `luxin/data_sources/__init__.py` (new)
- `luxin/data_sources/sql.py` (new)
- `luxin/__init__.py` (export new functions)

**Dependencies**: `sqlalchemy>=2.0.0` (optional dependency)

**Example Usage**:
```python
from luxin import Inspector, load_from_sql

# Load data directly from SQL
df = load_from_sql(
    connection_string="postgresql://user:pass@localhost/db",
    query="SELECT * FROM sales WHERE date > '2024-01-01'"
)
tracked_df = TrackedDataFrame(df)
agg = tracked_df.groupby('region').sum()
inspector = Inspector(agg)
inspector.render()
```

#### 2.2 Cloud Storage Integration

Read DataFrames directly from cloud storage.

**Features**:
- S3/Google Cloud Storage: Read DataFrames directly from cloud storage
- Parquet/CSV from URLs: Load data from remote sources
- Authentication: Support for AWS credentials, GCP service accounts

**Implementation**:
- Cloud connectors: `luxin/data_sources/cloud.py`
- Remote file loader: `luxin/data_sources/remote.py`

**Files to Create/Modify**:
- `luxin/data_sources/cloud.py` (new)
- `luxin/data_sources/remote.py` (new)

**Dependencies**: `boto3>=1.28.0` (for AWS S3, optional), `gcsfs` (for GCS, optional)

#### 2.3 API Data Sources

Fetch data from REST APIs and GraphQL endpoints.

**Features**:
- REST API connectors: Fetch data from REST APIs
- GraphQL support: Query GraphQL endpoints
- Authentication: Support for API keys, OAuth, etc.

**Implementation**:
- API connector: `luxin/data_sources/api.py`
- Helper functions for common API patterns

**Files to Create/Modify**:
- `luxin/data_sources/api.py` (new)

**Dependencies**: `requests>=2.31.0` (optional), `gql>=3.4.0` (for GraphQL, optional)

---

### Phase 3: Advanced Features (v0.5.0)

**Timeline**: Q3 2024  
**Priority**: Medium  
**Effort**: High

#### 3.1 Multi-level Drill-down

Support nested aggregations with multiple drill-down levels.

**Features**:
- Nested aggregations: Drill down multiple levels (e.g., Region → City → Store)
- Breadcrumb navigation: Show current drill-down path
- Back navigation: Return to previous aggregation levels

**Implementation**:
- Extend `Inspector` to support nested source mappings
- New component: `luxin/components/breadcrumbs.py`
- Update `luxin/components/table_view.py` for multi-level support

**Files to Create/Modify**:
- `luxin/inspector.py` (enhance for nested mappings)
- `luxin/components/table_view.py` (multi-level support)
- `luxin/components/breadcrumbs.py` (new)

**Example Usage**:
```python
# First level: by region
agg1 = df.groupby('region').sum()
inspector = Inspector(agg1)

# Drill down to city level
agg2 = detail_df.groupby(['region', 'city']).sum()
# Inspector automatically handles nested drill-down
```

#### 3.2 Comparison Mode

Compare two aggregated views side-by-side.

**Features**:
- Side-by-side comparison: Compare two aggregated views
- Diff view: Highlight differences between datasets
- Statistical comparison: Show percentage differences, significance tests

**Implementation**:
- New component: `luxin/components/comparison.py`
- Extend `Inspector` to support comparison mode

**Files to Create/Modify**:
- `luxin/components/comparison.py` (new)
- `luxin/inspector.py` (add comparison mode)

#### 3.3 Custom Aggregations UI

Build custom aggregations without writing code.

**Features**:
- Visual aggregation builder: Build custom aggregations without code
- Pre-defined templates: Common aggregation patterns (Pareto, cohort analysis)
- Custom functions: Support for user-defined aggregation functions

**Implementation**:
- New component: `luxin/components/aggregation_builder.py`
- Template library: Common aggregation patterns

**Files to Create/Modify**:
- `luxin/components/aggregation_builder.py` (new)

#### 3.4 Data Quality Indicators

Show data quality metrics and highlight issues.

**Features**:
- Quality metrics: Show data quality scores (completeness, uniqueness, validity)
- Anomaly detection: Highlight outliers and anomalies in detail view
- Quality dashboard: Summary view of data quality issues

**Implementation**:
- New component: `luxin/components/quality_indicators.py`
- Integrate with data quality libraries or build custom

**Files to Create/Modify**:
- `luxin/components/quality_indicators.py` (new)

---

### Phase 4: Collaboration & Sharing (v0.6.0)

**Timeline**: Q4 2024  
**Priority**: Low  
**Effort**: Very High

#### 4.1 Sharing & Embedding

Enable sharing of Inspector views with others.

**Features**:
- Shareable links: Generate shareable URLs for specific views
- Embed widgets: Embed Inspector views in external websites
- Snapshot export: Export interactive HTML snapshots

**Implementation**:
- Sharing service: `luxin/sharing.py`
- Integration with Streamlit Cloud features (if applicable)

**Files to Create/Modify**:
- `luxin/sharing.py` (new)

#### 4.2 User Preferences

Persist user settings and workspace configurations.

**Features**:
- Persistent settings: Save user preferences (theme, default filters)
- Workspace management: Save and load workspace configurations
- Import/export settings: Share configurations between users

**Implementation**:
- Preferences module: `luxin/preferences.py`
- Use Streamlit session state + file storage

**Files to Create/Modify**:
- `luxin/preferences.py` (new)
- `luxin/config.py` (add preference loading)

#### 4.3 Comments & Annotations

Add collaborative features for data exploration.

**Features**:
- Row-level comments: Add notes to specific rows
- Annotations: Highlight and annotate interesting findings
- Comment threads: Discussion threads on specific data points

**Implementation**:
- Annotations component: `luxin/components/annotations.py`
- Store annotations in separate data structure

**Files to Create/Modify**:
- `luxin/components/annotations.py` (new)

---

### Phase 5: Enterprise Features (v1.0.0)

**Timeline**: 2025  
**Priority**: Low  
**Effort**: Very High

#### 5.1 Authentication & Access Control

Add user authentication and role-based access control.

**Features**:
- User roles: Admin, viewer, editor roles
- Row-level security: Filter data based on user permissions
- Integration with auth providers: Auth0, Okta, etc.

**Implementation**:
- Auth module: `luxin/auth.py`
- Security module: `luxin/security.py`

**Files to Create/Modify**:
- `luxin/auth.py` (new)
- `luxin/security.py` (new)

#### 5.2 Audit Logging

Track user interactions and data changes.

**Features**:
- Activity tracking: Log all user interactions
- Change history: Track data changes over time
- Audit reports: Generate audit trail reports

**Implementation**:
- Audit module: `luxin/audit.py`
- Logging infrastructure

**Files to Create/Modify**:
- `luxin/audit.py` (new)

#### 5.3 Scheduled Reports

Automate report generation and delivery.

**Features**:
- Automated exports: Schedule regular PDF/Excel exports
- Email delivery: Send reports via email
- Report templates: Reusable report templates

**Implementation**:
- Scheduler module: `luxin/scheduler.py`
- Background job scheduler

**Files to Create/Modify**:
- `luxin/scheduler.py` (new)

---

## Technical Improvements

### Code Quality

**Ongoing improvements**:

- **Type hints**: Complete type coverage (currently partial)
  - Add type hints to all functions and methods
  - Use `typing` module for complex types
  - Files: All source files need enhancement

- **Documentation**: Expand docstrings with examples
  - Add usage examples to all public APIs
  - Include parameter descriptions
  - Files: All source files

- **Error handling**: More specific exceptions and error messages
  - Create custom exception classes
  - Provide actionable error messages
  - Files: `luxin/validation.py`, all components

### Testing

**Enhancements**:

- **Integration tests**: End-to-end Streamlit app tests
  - Test full workflows in Streamlit context
  - Files: `tests/test_integration_streamlit.py` (new)

- **Performance tests**: Benchmark large dataset handling
  - Test with 100K+, 1M+ row datasets
  - Measure load times and memory usage
  - Files: `tests/test_performance.py` (new)

- **Visual regression tests**: Screenshot comparison for UI
  - Ensure UI consistency across changes
  - Files: `tests/test_visual_regression.py` (new)

### Developer Experience

**Improvements**:

- **CLI tool**: Command-line interface for common operations
  - Initialize new projects
  - Validate configurations
  - Files: `luxin/cli.py` (new)

- **Pre-commit hooks**: Automated code quality checks
  - Linting, formatting, type checking
  - Files: `.pre-commit-config.yaml` (new)

- **CI/CD**: Enhanced GitHub Actions workflows
  - Automated testing on multiple Python versions
  - Automated releases
  - Files: `.github/workflows/` (enhance existing)

---

## Implementation Strategy

### Quick Wins (Can start immediately)

These features provide immediate value with relatively low effort:

1. **Enhanced export** (PDF, filtered exports) - Extends existing functionality
2. **Chart visualizations** in detail panel - Uses existing plotly integration patterns
3. **Performance caching** - Leverages Streamlit's built-in caching
4. **Advanced filtering options** - Builds on existing filter component

### Medium-term (Requires planning)

These features need architectural decisions:

1. **SQL database integration** - Requires data source abstraction
2. **Multi-level drill-down** - Needs nested mapping structure
3. **Comparison mode** - Requires dual Inspector support

### Long-term (Requires architecture decisions)

These features need significant planning:

1. **Collaboration features** - Requires backend infrastructure decisions
2. **Enterprise features** - Needs security and scalability planning
3. **Authentication system** - Requires integration with auth providers

---

## Success Metrics

Track progress using these metrics:

- **Adoption**: 
  - PyPI download growth
  - GitHub stars and forks
  - Community contributions

- **Performance**: 
  - Page load time < 2s for 100K row datasets
  - Memory usage < 500MB for typical use cases
  - Smooth interactions (60fps scrolling)

- **User satisfaction**: 
  - GitHub issues/feature requests
  - User feedback and testimonials
  - Documentation page views

- **Code quality**: 
  - Maintain 85%+ test coverage
  - Zero critical security vulnerabilities
  - Type hint coverage > 90%

---

## Dependencies

### New Dependencies to Add

- `plotly>=5.0.0` - For chart visualizations
- `sqlalchemy>=2.0.0` - For SQL integration (optional)
- `reportlab>=4.0.0` or `weasyprint` - For PDF export
- `boto3>=1.28.0` - For AWS S3 support (optional)
- `gcsfs>=2023.1.0` - For Google Cloud Storage (optional)
- `requests>=2.31.0` - For API integration (optional)
- `gql>=3.4.0` - For GraphQL support (optional)

All new dependencies should be optional (except plotly for Phase 1) to keep the core package lightweight.

---

## Breaking Changes Considerations

### Phase 1-2
- **No breaking changes expected**
- All new features are additive
- Backward compatibility maintained

### Phase 3
- **May require config changes** for multi-level drill-down
- New `InspectorConfig` options
- Migration guide will be provided

### Phase 4-5
- **Likely require new API patterns**
- May deprecate some old APIs
- Comprehensive migration guides will be provided

---

## Documentation Updates

As features are added, documentation will be updated:

- **API Reference**: New components and functions
- **Migration Guides**: For breaking changes
- **Tutorial Notebooks**: For each major feature
- **Video Tutorials**: For complex features (future)
- **Examples**: Updated with new capabilities

See the [Examples](examples.md) page for current examples and the [User Guide](user-guide.md) for usage patterns.

---

## Feedback & Contributions

This roadmap is a living document and will evolve based on:

- User feedback and feature requests
- Community contributions
- Technical constraints and discoveries
- Industry trends and best practices

We welcome feedback! Please open an issue on [GitHub](https://github.com/eddiethedean/luxin/issues) to discuss roadmap items or suggest new features.

---

**Last Updated**: December 2024  
**Version**: 0.2.0 → 1.0.0 Roadmap

