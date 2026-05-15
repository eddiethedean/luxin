"""
Configuration management for luxin Inspector.
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class InspectorConfig:
    """
    Configuration options for Inspector.

    Attributes:
        show_summary_stats: Whether to show summary statistics (default: True)
        show_export_buttons: Whether to show export buttons (default: True)
        show_filters: Whether to show filter controls (default: True)
        detail_page_size: Number of rows per page in detail panel (default: 100)
        table_height: Height of the main table in pixels (default: 400)
        detail_height: Height of the detail panel in pixels (default: 300)
    """

    show_summary_stats: bool = True
    show_export_buttons: bool = True
    show_filters: bool = True
    detail_page_size: int = 100
    table_height: int = 400
    detail_height: int = 300

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "show_summary_stats": self.show_summary_stats,
            "show_export_buttons": self.show_export_buttons,
            "show_filters": self.show_filters,
            "detail_page_size": self.detail_page_size,
            "table_height": self.table_height,
            "detail_height": self.detail_height,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "InspectorConfig":
        """Create config from dictionary."""
        return cls(
            **{k: v for k, v in config_dict.items() if k in cls.__dataclass_fields__}
        )


def get_default_config() -> InspectorConfig:
    """Get default configuration."""
    return InspectorConfig()
