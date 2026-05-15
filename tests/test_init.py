"""
Tests for luxin.__init__ module.
"""

import re

import pytest
import warnings

from luxin import Inspector, TrackedDataFrame, create_drill_table, __version__


def test_version_pep440_three_part():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__) is not None


def test_deprecated_show_drill_table_import():
    """Test that importing show_drill_table triggers deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Import to trigger __getattr__
        import luxin

        _ = luxin.show_drill_table  # triggers __getattr__

        assert len(w) >= 1
        deprecation_warnings = [
            warning for warning in w if issubclass(warning.category, DeprecationWarning)
        ]
        assert len(deprecation_warnings) >= 1
        assert "deprecated" in str(deprecation_warnings[0].message).lower()
        assert "Inspector" in str(deprecation_warnings[0].message)


def test_getattr_with_invalid_name():
    """Test __getattr__ with invalid name raises AttributeError."""
    import luxin

    with pytest.raises(AttributeError):
        _ = luxin.nonexistent_attribute


def test_all_exports():
    """Test that all expected exports are available."""
    from luxin import (
        DrillHierarchySpec,
        create_tracked_from_polars,
        convert_polars_to_pandas,
        is_polars_dataframe,
    )

    assert DrillHierarchySpec is not None

    assert Inspector is not None
    assert TrackedDataFrame is not None
    assert create_drill_table is not None
    assert create_tracked_from_polars is not None
    assert convert_polars_to_pandas is not None
    assert is_polars_dataframe is not None
