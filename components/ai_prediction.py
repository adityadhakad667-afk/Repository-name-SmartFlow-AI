"""
AI Congestion Prediction Component for SmartFlow AI.
Runs interactive multi-factor machine learning inference using trained Random Forest/XGBoost models.

CRITICAL INVARIANT:
Explicitly labeled 'ML PREDICTION'.
Model confidence is strictly separated from physical risk score.
"""
from typing import Any, Dict
import streamlit as st
import pandas as pd

from ml.predict import predict_traffic_conditions
from .risk_cards import render_risk_gauge_panel


def render_ai_prediction_view() -> None:
    """Render Machine Learning Congestion Prediction interface."""
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>🤖</span> Machine Learning Congestion Prediction
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Forecast congestion levels using trained predictive models based on temporal rhythms, 
            vehicle concentration, road geometry, and weather factors.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sf-badge-ml">ML PREDICTION ENGINE</span>', unsafe_allow_html=True)
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Input Panel
    with st.container():
        st.markdown('<div class="sf-glass-panel">', unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.85rem; font-weight: 700; color: #38BDF8; margin-bottom: 1rem;'>⚙ SCENARIO FEATURE CONFIGURATION</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            hour = st.slider("Hour of Day (0–23)", min_value=0, max_value=23, value=9, help="Hour in 24h format (e.g. 9 for 9:00 AM, 18 for 6:00 PM)")
            day_name = st.selectbox("Day of Week", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], index=1)
            days_map = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
            day_of_week = days_map[day_name]

        with c2:
            road_type = st.selectbox("Road Infrastructure Type", ["Arterial", "Highway", "Urban"], index=0)
            weather = st.selectbox("Weather Condition", ["Clear", "Rain", "Fog", "Storm"], index=0)
            temperature = st.slider("Ambient Temperature (°C)", min_value=5.0, max_value=48.0, value=30.0, step=0.5)

        with c3:
            vehicle_count = st.slider("Vehicle Density (veh / hr)", min_value=50, max_value=2200, value=1150, step=25)
            free_flow = 90.0 if road_type == "Highway" else (60.0 if road_type == "Arterial" else 40.0)
            precip = 0.0 if weather == "Clear" else (8.0 if weather == "Storm" else 2.5)
            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 8px; font-size: 0.8rem; color: #94A3B8; margin-top: 15px;">
                Design Speed: <strong style="color: #F8FAFC;">{free_flow} km/h</strong><br/>
                Precipitation: <strong style="color: #F8FAFC;">{precip} mm</strong><br/>
                Weekend Flag: <strong style="color: #F8FAFC;">{'Yes' if day_of_week >= 5 else 'No'}</strong>
            </div>
            """, unsafe_allow_html=True)

        predict_btn = st.button("🚀 Run ML Congestion Inference", type="primary", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Run Prediction
    if predict_btn or "last_ml_prediction" not in st.session_state:
        pred_res = predict_traffic_conditions(
            hour=hour,
            day_of_week=day_of_week,
            road_type=road_type,
            weather=weather,
            temperature=temperature,
            precipitation=precip,
            vehicle_count=vehicle_count,
            free_flow_speed=free_flow,
        )
        st.session_state["last_ml_prediction"] = pred_res
    else:
        pred_res = st.session_state["last_ml_prediction"]

    # Results Section
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    res_col1, res_col2 = st.columns([1.2, 1.0])

    with res_col1:
        # Gauge clearly displaying confidence and risk score separately
        render_risk_gauge_panel(
            risk_score=pred_res["risk_score"],
            traffic_level=pred_res["traffic_level"],
            confidence_pct=pred_res["confidence_pct"],
            title=f"MODEL CONGESTION PREDICTION ({pred_res['model_name']})",
        )

        # AI Insight Box
        st.markdown(f"""
        <div style="background: rgba(6, 182, 212, 0.08); border: 1px solid rgba(6, 182, 212, 0.3); border-radius: 10px; padding: 1.1rem; margin-top: 1rem;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #38BDF8; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 6px;">
                <span>💡</span> AI EXPLANATION & INSIGHT
            </div>
            <p style="color: #E2E8F0; font-size: 0.88rem; line-height: 1.5; margin: 0;">
                {pred_res['ai_insight']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    with res_col2:
        st.markdown("""
        <div class="sf-glass-panel">
            <div style="font-size: 0.8rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; margin-bottom: 0.8rem;">
                📊 CLASS PROBABILITY DISTRIBUTION
            </div>
        """, unsafe_allow_html=True)

        probs = pred_res["probabilities"]
        for cls_name, p_val in probs.items():
            pct = round(p_val * 100, 1)
            p_color = "#10B981" if cls_name == "LOW" else ("#F59E0B" if cls_name == "MEDIUM" else "#EF4444")
            st.markdown(f"""
            <div style="margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px;">
                    <span style="font-weight: 600; color: #F8FAFC;">{cls_name}</span>
                    <span style="color: {p_color}; font-weight: 700;">{pct}%</span>
                </div>
                <div style="background: rgba(148, 163, 184, 0.15); height: 8px; border-radius: 9999px; overflow: hidden;">
                    <div style="background: {p_color}; width: {pct}%; height: 100%; border-radius: 9999px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Feature contributions for this prediction
    st.markdown("<h3 style='font-size: 1.15rem; margin-top: 1.5rem;'>🧠 Feature Influence on this Prediction</h3>", unsafe_allow_html=True)
    contribs = pred_res.get("feature_contributions", [])
    if contribs:
        c_cols = st.columns(len(contribs))
        for i, c in enumerate(contribs):
            with c_cols[i]:
                st.markdown(f"""
                <div class="sf-kpi-card" style="padding: 0.8rem 1rem;">
                    <div style="font-size: 0.72rem; color: #94A3B8;">{c['display_name']}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #38BDF8; margin: 4px 0;">{c['importance_pct']}%</div>
                    <div style="font-size: 0.7rem; color: #64748B;">{c['impact_level']} Impact</div>
                </div>
                """, unsafe_allow_html=True)
