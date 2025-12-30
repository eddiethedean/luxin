"""Tests for configuration management."""

import pytest
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
    assert config.theme == 'auto'


def test_inspector_config_custom():
    """Test custom configuration."""
    config = InspectorConfig(
        show_summary_stats=False,
        show_export_buttons=False,
        show_filters=False,
        detail_page_size=50,
        table_height=500,
        detail_height=400,
        theme='dark'
    )
    
    assert config.show_summary_stats is False
    assert config.show_export_buttons is False
    assert config.show_filters is False
    assert config.detail_page_size == 50
    assert config.table_height == 500
    assert config.detail_height == 400
    assert config.theme == 'dark'


def test_inspector_config_to_dict():
    """Test converting config to dictionary."""
    config = InspectorConfig(show_summary_stats=False)
    config_dict = config.to_dict()
    
    assert isinstance(config_dict, dict)
    assert config_dict['show_summary_stats'] is False
    assert config_dict['show_export_buttons'] is True
    assert 'detail_page_size' in config_dict


def test_inspector_config_from_dict():
    """Test creating config from dictionary."""
    config_dict = {
        'show_summary_stats': False,
        'detail_page_size': 50,
        'theme': 'light'
    }
    config = InspectorConfig.from_dict(config_dict)
    
    assert config.show_summary_stats is False
    assert config.detail_page_size == 50
    assert config.theme == 'light'
    # Other values should be defaults
    assert config.show_export_buttons is True


def test_get_default_config():
    """Test getting default configuration."""
    config = get_default_config()
    
    assert isinstance(config, InspectorConfig)
    assert config.show_summary_stats is True


def test_inspector_with_config():
    """Test Inspector with custom configuration."""
    import pandas as pd
    from luxin import Inspector, TrackedDataFrame
    
    df = TrackedDataFrame({
        'category': ['A', 'A', 'B'],
        'value': [10, 20, 30]
    })
    agg = df.groupby('category').agg({'value': 'sum'})
    
    config = InspectorConfig(show_summary_stats=False)
    inspector = Inspector(agg, config=config)
    
    assert inspector.config is config
    assert inspector.config.show_summary_stats is False

