"""
Sidebar Navigation Component for SmartFlow AI.
Manages application mode switching, connectivity badges, and quick toggles.
"""
from typing import Any, Dict
import streamlit as st


def render_sidebar(status_info: Dict[str, Any]) -> str:
    """
    Render navigation sidebar and return the selected page.
    """
    with st.sidebar:
        # Header Brand
        st.markdown("""
        <div style="padding: 0.5rem 0 1.25rem 0; border-bottom: 1px solid rgba(56, 189, 248, 0.15);">
            <div style="font-size: 1.5rem; font-weight: 800; letter-spacing: 0.04em; background: linear-gradient(135deg, #FFFFFF, #38BDF8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                ⚡ SMARTFLOW AI
            </div>
            <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 4px;">
                Real-Time Traffic Intelligence
            </div>
        </div>
        """, unsafe_allow_html=True)

        # System Connectivity Status
        is_connected = status_info.get("is_connected", False)
        status_text = status_info.get("status_text", "● LIVE TRAFFIC OFFLINE")

        if is_connected:
            badge_html = f'<span class="sf-badge-live" style="width: 100%; justify-content: center;">{status_text}</span>'
        else:
            badge_html = f'<span class="sf-badge-offline" style="width: 100%; justify-content: center;">{status_text}</span>'

        st.markdown(f"<div style='margin: 1rem 0;'>{badge_html}</div>", unsafe_allow_html=True)

        # Navigation Options
        pages = [
            "🏠 Dashboard",
            "🚦 Live Traffic",
            "🤖 AI Prediction",
            "🔮 Traffic Forecast",
            "🔥 Traffic Hotspots",
            "🛣 Route Advisory",
            "📊 Analytics",
            "🧠 Explainable AI",
            "📍 Saved Locations",
            "📜 History",
            "💼 Investor Mode",
            "🎬 Demo Mode",
            "⚙ Settings",
        ]

        selected_page = st.radio(
            "NAVIGATION",
            pages,
            label_visibility="collapsed",
            index=0,
        )

        st.markdown("---")

        # Quick Demo Mode notice if activated
        if "🎬 Demo Mode" in selected_page:
            st.markdown("""
            <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 8px; padding: 0.6rem; font-size: 0.75rem; color: #FCD34D;">
                ⚠️ <strong>DEMO MODE ACTIVE</strong><br/>
                Displaying simulated presentation traffic scenarios.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style="padding-top: 1rem; font-size: 0.7rem; color: #64748B; text-align: center;">
            SmartFlow Platform © 2026<br/>
            Engine: Hybrid ML + Real-Time v2
        </div>
        """, unsafe_allow_html=True)

        return selected_page
