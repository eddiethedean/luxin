"""Tests for configuration management."""

from luxin.config import InspectorConfig, get_default_config


def test_inspector_config_defaults():
    """Test default configuration values."""
    config = InspectorConfig()

    assert config.show_summary_stats is True
    assert config.show_export_buttons is True
    assert config.show_filters is True
    assert config.detail_page_size == 100
    assert config.table_height == 400
    assert config.detail_height == 300
    assert config.enable_multi_level_drill is False
    assert config.max_drill_depth == 8
    assert config.show_data_quality is False
    assert config.show_aggregation_builder is False
    assert config.compare_run_significance is False
    assert config.show_comparison_entrypoint is False
    assert config.inspector_session_key is None


def test_inspector_config_custom():
    """Test custom configuration."""
    config = InspectorConfig(
        show_summary_stats=False,
        show_export_buttons=False,
        show_filters=False,
        detail_page_size=50,
        table_height=500,
        detail_height=400,
    )

    assert config.show_summary_stats is False
    assert config.show_export_buttons is False
    assert config.show_filters is False
    assert config.detail_page_size == 50
    assert config.table_height == 500
    assert config.detail_height == 400


def test_inspector_config_to_dict():
    """Test converting config to dictionary."""
    config = InspectorConfig(show_summary_stats=False)
    config_dict = config.to_dict()

    assert isinstance(config_dict, dict)
    assert config_dict["show_summary_stats"] is False
    assert config_dict["show_export_buttons"] is True
    assert "detail_page_size" in config_dict


def test_inspector_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        "show_summary_stats": False,
        "detail_page_size": 50,
    }
    config = InspectorConfig.from_dict(config_dict)

    assert config.show_summary_stats is False
    assert config.detail_page_size == 50
    # Other values should be defaults
    assert config.show_export_buttons is True


def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()

    assert isinstance(config, InspectorConfig)
    assert config.show_summary_stats is True


def test_inspector_with_config():
    """Test Inspector with custom configuration."""
    from luxin import Inspector, TrackedDataFrame

    df = TrackedDataFrame({"category": ["A", "A", "B"], "value": [10, 20, 30]})
    agg = df.groupby("category").agg({"value": "sum"})

    config = InspectorConfig(show_summary_stats=False)
    inspector = Inspector(agg, config=config)

    assert inspector.config is config
    assert inspector.config.show_summary_stats is False
