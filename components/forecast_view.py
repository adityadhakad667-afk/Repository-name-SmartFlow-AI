"""
Traffic Forecasting View Component for SmartFlow AI.
Displays forward-looking 3-hour and 6-hour predictive traffic trajectory timelines.

CRITICAL INVARIANT:
Explicitly labeled 'MODEL FORECAST'. Never called real-time.
"""
from typing import Any, Dict
import streamlit as st
import pandas as pd

from analytics.forecasting import generate_traffic_forecast
from .charts import plot_forecast_timeline


def render_forecast_view() -> None:
    """Render forward-looking traffic forecast interface."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🔮</span> Predictive Traffic Forecasting
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Anticipate traffic velocity, queue formation, and risk trends over upcoming operational windows.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sf-badge-ml">MODEL FORECAST</span>', unsafe_allow_html=True)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Controls
    with st.container():
        st.markdown('<div class="sf-glass-panel">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            horizon = st.radio("Forecast Window Horizon", [3, 6, 12], index=1, format_func=lambda x: f"Next {x} Hours", horizontal=True)
        with col2:
            road_type = st.selectbox("Corridor Road Type", ["Arterial", "Highway", "Urban"], index=0)
        with col3:
            weather = st.selectbox("Forecasted Weather Outlook", ["Clear", "Rain", "Fog", "Storm"], index=0)
        st.markdown('</div>', unsafe_allow_html=True)

    forecast_data = generate_traffic_forecast(
        horizon_hours=horizon,
        base_road_type=road_type,
        base_weather=weather,
    )
    points = forecast_data["points"]

    # Interactive Chart
    fig = plot_forecast_timeline(points)
    st.plotly_chart(fig, use_container_width=True)

    # Detailed Step-by-Step Table
    st.markdown("<h3 style='font-size: 1.15rem; margin: 1.5rem 0 0.8rem 0;'>⏱ Hourly Projection Breakdown</h3>", unsafe_allow_html=True)
    
    rows = []
    for p in points:
        rows.append({
            "Target Time": p["forecast_time"],
            "Hour": f"{p['hour']:02d}:00",
            "Predicted Traffic": f"{p['badge_icon']} {p['predicted_traffic']}",
            "Risk Score": f"{p['risk_score']} / 100",
            "Confidence": f"{p['confidence_pct']}%",
            "Estimated Volume": f"{p['estimated_vehicles']} veh/hr",
            "Outlook Rationale": p["ai_insight"],
        })
    df_forecast = pd.DataFrame(rows)
    st.dataframe(df_forecast, use_container_width=True, hide_index=True)

    st.markdown("""
    <div style="font-size: 0.75rem; color: #64748B; margin-top: 1rem; text-align: right;">
        * Forecast is derived by the SmartFlow temporal transition model. For current conditions, refer to Live Traffic.
    </div>
    """, unsafe_allow_html=True)
