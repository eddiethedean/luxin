# Releasing (monorepo)

Luxin ships three coordinated packages from this repository:

| Package   | Directory   | PyPI name    |
|-----------|-------------|--------------|
| Main UI   | repo root   | `luxin`      |
| Core      | `luxin_core/` | `luxin-core` |
| Notebook  | `luxin_nb/` | `luxin-nb`   |

## Version alignment

1. Set **`project.version`** in each `pyproject.toml` (`./pyproject.toml`, `luxin_core/pyproject.toml`, `luxin_nb/pyproject.toml`) to the same **X.Y.Z**.
2. Set **`__version__`** in `luxin/__init__.py`, `luxin_core/luxin_core/__init__.py`, and `luxin_nb/luxin_nb/__init__.py` to match.
3. Ensure root `pyproject.toml` dependency **`luxin-core>=X.Y.Z,<next_minor`** matches the core package version line you are releasing.
4. Update **`CHANGELOG.md`** with user-facing notes for this release.

## Tag and publish

- Create and push an annotated git tag **`vX.Y.Z`** (for example `v0.4.0`). The release workflow validates versions against the tag.
- Publishing is driven by `.github/workflows/release-pypi.yml` (see that workflow for exact gates).

## Local verification before tagging

```bash
pip install -e ./luxin_core -e ./luxin_nb -e ".[dev,polars]"
pip install "streamlit>=1.35.0"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/ -v
ruff check luxin/ luxin_core/ luxin_nb/ tests/
black --check luxin/ luxin_core/ luxin_nb/ tests/
mypy luxin/ luxin_core/luxin_core/ luxin_nb/luxin_nb/ --ignore-missing-imports
```
