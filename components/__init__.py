"""
Components module for SmartFlow AI.
Exports UI views, styles, visual elements, charts, and maps.
"""
from .styles import CUSTOM_CSS
from .sidebar import render_sidebar
from .dashboard import render_dashboard
from .live_traffic import render_live_traffic_view
from .ai_prediction import render_ai_prediction_view
from .forecast_view import render_forecast_view
from .hotspots_view import render_hotspots_view
from .explainable_ai import render_explainable_ai_view
from .analytics_view import render_analytics_view
from .saved_locations import render_saved_locations_view
from .history_view import render_history_view
from .demo_mode import render_demo_mode_view
from .investor_view import render_investor_view
from .settings_view import render_settings_view
from .risk_cards import (
    render_kpi_card,
    render_status_banner,
    render_risk_gauge_panel,
    render_why_box,
)
from .maps import create_traffic_map
from .charts import (
    plot_forecast_timeline,
    plot_feature_importances,
    plot_hourly_traffic_trends,
    plot_risk_distribution,
    plot_model_comparison,
)

__all__ = [
    "CUSTOM_CSS",
    "render_sidebar",
    "render_dashboard",
    "render_live_traffic_view",
    "render_ai_prediction_view",
    "render_forecast_view",
    "render_hotspots_view",
    "render_explainable_ai_view",
    "render_analytics_view",
    "render_saved_locations_view",
    "render_history_view",
    "render_demo_mode_view",
    "render_investor_view",
    "render_settings_view",
    "render_kpi_card",
    "render_status_banner",
    "render_risk_gauge_panel",
    "render_why_box",
    "create_traffic_map",
    "plot_forecast_timeline",
    "plot_feature_importances",
    "plot_hourly_traffic_trends",
    "plot_risk_distribution",
    "plot_model_comparison",
]
