"""
Historical & Comparative Analytics Component for SmartFlow AI.
Renders Plotly interactive multi-factor charts including risk distribution,
hourly volume/speed trends, road type delay comparisons, and ML performance metrics.
"""
from typing import Any, Dict
import streamlit as st
import pandas as pd

from ml.preprocessing import load_or_generate_dataset
from ml.model import TrafficModel
from database.db import get_route_history
from .charts import (
    plot_risk_distribution,
    plot_hourly_traffic_trends,
    plot_model_comparison,
)


def render_analytics_view() -> None:
    """Render comprehensive analytics dashboard."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>📊</span> Deep-Dive Traffic Intelligence Analytics
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Interactive statistical exploration of congestion distributions, velocity patterns, and ML metrics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sf-badge-ml">HISTORICAL ANALYTICS & AUDIT</span>', unsafe_allow_html=True)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    df = load_or_generate_dataset()
    model = TrafficModel()

    row1_c1, row1_c2 = st.columns(2)
    with row1_c1:
        fig_dist = plot_risk_distribution(df)
        st.plotly_chart(fig_dist, use_container_width=True)

    with row1_c2:
        fig_hourly = plot_hourly_traffic_trends(df)
        st.plotly_chart(fig_hourly, use_container_width=True)

    # Road type delay comparison
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    row2_c1, row2_c2 = st.columns(2)

    with row2_c1:
        # Delay by road type chart
        road_delays = df.groupby("road_type")["delay_min"].mean().reset_index()
        import plotly.express as px
        fig_road = px.bar(
            road_delays,
            x="road_type",
            y="delay_min",
            color="road_type",
            color_discrete_map={"Highway": "#0284C7", "Arterial": "#06B6D4", "Urban": "#38BDF8"},
            labels={"road_type": "Road Hierarchy", "delay_min": "Average Delay (min)"},
        )
        from .charts import DARK_LAYOUT
        fig_road.update_layout(
            **DARK_LAYOUT,
            title={"text": "⏱ Average Traffic Delay by Road Hierarchy", "font": {"color": "#F8FAFC", "size": 15}},
            showlegend=False,
        )
        st.plotly_chart(fig_road, use_container_width=True)

    with row2_c2:
        # ML model comparison
        comp_data = model.metadata.get("models_comparison", {})
        if comp_data:
            fig_comp = plot_model_comparison(comp_data)
            st.plotly_chart(fig_comp, use_container_width=True)
        else:
            st.info("Train ML models to view the comparative evaluation matrix.")
