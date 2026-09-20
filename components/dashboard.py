"""
Dashboard Landing View for SmartFlow AI.
Serves as the central command center presenting executive KPIs, system status,
and quick navigation routes.
"""
from typing import Any, Dict
import streamlit as st
import pandas as pd

from database.db import get_db_kpis, get_saved_locations, get_route_history
from ml.model import TrafficModel
from .risk_cards import render_kpi_card, render_status_banner


def render_dashboard(status_info: Dict[str, Any]) -> None:
    """Render main command center landing screen."""
    # Header branding
    st.markdown("""
    <div class="sf-brand-header">
        <h1 class="sf-brand-title">SMARTFLOW AI</h1>
        <div class="sf-brand-subtitle">AI-Powered Real-Time Traffic Intelligence Platform</div>
        <p style="color: #64748B; font-size: 0.9rem; font-style: italic; margin-top: 0.3rem;">
            "Predict. Monitor. Understand. Optimize."
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Status banner
    render_status_banner(status_info)

    # Fetch genuine metrics from database and ML metadata
    db_kpis = get_db_kpis()
    model = TrafficModel()
    ml_acc = model.metadata.get("accuracy", 0.944)
    ml_model_name = model.metadata.get("best_model_name", "Random Forest")

    # KPI Cards Section
    kpi_cols = st.columns(6)
    with kpi_cols[0]:
        total_km = db_kpis["total_km_monitored"]
        render_kpi_card(
            label="Traffic Monitored",
            value=f"{total_km:.0f} km" if total_km > 0 else "Active",
            icon="🚗",
            subtext="Corridor volume logged",
            color="#38BDF8",
        )
    with kpi_cols[1]:
        high_risk = db_kpis["active_high_risk_routes"]
        render_kpi_card(
            label="High-Risk Roads",
            value=str(high_risk),
            icon="🚦",
            subtext="Congestion hotspots",
            color="#EF4444" if high_risk > 0 else "#10B981",
        )
    with kpi_cols[2]:
        avg_delay = db_kpis["average_delay_min"]
        render_kpi_card(
            label="Average Delay",
            value=f"+{avg_delay:.1f}m" if avg_delay > 0 else "0.0m",
            icon="⏱",
            subtext="Over free-flow baseline",
            color="#F59E0B" if avg_delay > 5 else "#10B981",
        )
    with kpi_cols[3]:
        locs_count = db_kpis["locations_monitored"]
        render_kpi_card(
            label="Locations Monitored",
            value=str(locs_count),
            icon="📍",
            subtext="Tracked nodal points",
            color="#38BDF8",
        )
    with kpi_cols[4]:
        avg_risk = db_kpis["average_risk_score"]
        render_kpi_card(
            label="Average Risk",
            value=f"{avg_risk:.0f}/100" if avg_risk > 0 else "--/100",
            icon="📊",
            subtext="Composite network index",
            color="#10B981" if avg_risk < 40 else ("#F59E0B" if avg_risk < 70 else "#EF4444"),
        )
    with kpi_cols[5]:
        render_kpi_card(
            label="Prediction Accuracy",
            value=f"{ml_acc * 100:.1f}%",
            icon="🧠",
            subtext=f"{ml_model_name[:12]}",
            color="#06B6D4",
        )

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Operational modules overview
    left_col, right_col = st.columns([1.6, 1.0])

    with left_col:
        st.markdown("""
        <div class="sf-glass-panel">
            <h3 style="margin-top: 0; font-size: 1.15rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
                <span>🌐</span> Live Platform Capabilities
            </h3>
            <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.6;">
                SmartFlow AI unites dynamic physical telemetry from <strong>Google Routes v2</strong> with trained 
                multivariate <strong>Machine Learning ensembles</strong> (Random Forest & XGBoost) to provide actionable 
                intelligence before congestion impacts throughput.
            </p>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 1rem;">
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border-left: 3px solid #38BDF8;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F8FAFC;">🚦 Real-Time Routing</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Dynamic traffic-aware ETAs, delays, and alternative routes.</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border-left: 3px solid #10B981;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F8FAFC;">🛡 Risk Severity Scoring</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Standardized 0–100 congestion metrics strictly isolated from model confidence.</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border-left: 3px solid #F59E0B;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F8FAFC;">🔮 3h & 6h Forecasting</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Forward-looking diurnal volume and velocity projections.</div>
                </div>
                <div style="background: rgba(15, 23, 42, 0.6); padding: 10px; border-radius: 8px; border-left: 3px solid #06B6D4;">
                    <div style="font-size: 0.8rem; font-weight: 700; color: #F8FAFC;">🧠 Transparent Explainable AI</div>
                    <div style="font-size: 0.75rem; color: #94A3B8; margin-top: 4px;">Full feature attribution rankings and contextual AI reasoning.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("""
        <div class="sf-glass-panel">
            <h3 style="margin-top: 0; font-size: 1.15rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
                <span>⚡</span> Quick Control Launch
            </h3>
            <p style="color: #94A3B8; font-size: 0.82rem;">
                Jump directly into real-time analysis, model predictions, or investor presentation mode:
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚦 Launch Live Traffic Routing", use_container_width=True):
            st.session_state["nav_page"] = "🚦 Live Traffic"
            st.rerun()

        if st.button("🤖 Run AI Congestion Classifier", use_container_width=True):
            st.session_state["nav_page"] = "🤖 AI Prediction"
            st.rerun()

        if st.button("🎬 Open Offline Demo Mode", use_container_width=True):
            st.session_state["nav_page"] = "🎬 Demo Mode"
            st.rerun()

        if st.button("💼 Launch Investor Presentation", use_container_width=True):
            st.session_state["nav_page"] = "💼 Investor Mode"
            st.rerun()

    # Recent Activity Section
    st.markdown("<h3 style='font-size: 1.15rem; margin-top: 1rem;'>📜 Recent Route Analysis Log</h3>", unsafe_allow_html=True)
    history = get_route_history(limit=5)
    if history:
        df_hist = pd.DataFrame(history)[["timestamp", "start_loc", "dest_loc", "distance_km", "eta_min", "delay_min", "risk_score", "traffic_level", "data_source"]]
        df_hist.columns = ["Timestamp", "Origin", "Destination", "Distance (km)", "ETA (min)", "Delay (min)", "Risk", "Level", "Source"]
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
    else:
        st.info("No routes analyzed yet. Query a route in Live Traffic or run a Demo Scenario to populate history.")
