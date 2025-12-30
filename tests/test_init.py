"""
Tests for luxin.__init__ module.
"""

import pytest
import warnings
from luxin import Inspector, TrackedDataFrame, create_drill_table


def test_deprecated_show_drill_table_import():
    """Test that importing show_drill_table triggers deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        # Import to trigger __getattr__
        import luxin
        show_drill_table = luxin.show_drill_table  # This triggers __getattr__
        
        assert len(w) >= 1
        deprecation_warnings = [warning for warning in w if issubclass(warning.category, DeprecationWarning)]
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
        Inspector,
        TrackedDataFrame,
        create_drill_table,
        create_tracked_from_polars,
        convert_polars_to_pandas,
        is_polars_dataframe
    )
    
    assert Inspector is not None
    assert TrackedDataFrame is not None
    assert create_drill_table is not None
    assert create_tracked_from_polars is not None
    assert convert_polars_to_pandas is not None
    assert is_polars_dataframe is not None

