"""
Configuration management for luxin Inspector.
"""

from typing import Any, Dict, Optional
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
        enable_multi_level_drill: Enable breadcrumb/stack drill when ``Inspector(drill=...)`` is set
        max_drill_depth: Maximum stacked drill depth (including root), default 8
        show_data_quality: Show data-quality expander alongside detail rows (default: False)
        show_aggregation_builder: Show footer expander to build a custom aggregation (default: False)
        compare_run_significance: Run optional pairwise t-tests in comparison UI (requires scipy)
        show_comparison_entrypoint: Render a compact hint/expander linking to comparison API (doc-oriented)
        inspector_session_key: Optional stable key for Streamlit ``session_state`` namespacing
    """

    show_summary_stats: bool = True
    show_export_buttons: bool = True
    show_filters: bool = True
    detail_page_size: int = 100
    table_height: int = 400
    detail_height: int = 300
    enable_multi_level_drill: bool = False
    max_drill_depth: int = 8
    show_data_quality: bool = False
    show_aggregation_builder: bool = False
    compare_run_significance: bool = False
    show_comparison_entrypoint: bool = False
    inspector_session_key: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "show_summary_stats": self.show_summary_stats,
            "show_export_buttons": self.show_export_buttons,
            "show_filters": self.show_filters,
            "detail_page_size": self.detail_page_size,
            "table_height": self.table_height,
            "detail_height": self.detail_height,
            "enable_multi_level_drill": self.enable_multi_level_drill,
            "max_drill_depth": self.max_drill_depth,
            "show_data_quality": self.show_data_quality,
            "show_aggregation_builder": self.show_aggregation_builder,
            "compare_run_significance": self.compare_run_significance,
            "show_comparison_entrypoint": self.show_comparison_entrypoint,
            "inspector_session_key": self.inspector_session_key,
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
