"""
SmartFlow AI - AI-Powered Real-Time Traffic Intelligence Platform
Main Application Entry Point.
"""
import os
from pathlib import Path
import streamlit as st

# Load environment variables if .env exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except Exception:
    pass

# Initialize Streamlit configuration
st.set_page_config(
    page_title="SmartFlow AI | Real-Time Traffic Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Core imports
from database.db import init_db, get_setting
from services.traffic_service import check_live_traffic_status
from components.styles import CUSTOM_CSS
from components.sidebar import render_sidebar
from components.dashboard import render_dashboard
from components.live_traffic import render_live_traffic_view
from components.ai_prediction import render_ai_prediction_view
from components.forecast_view import render_forecast_view
from components.hotspots_view import render_hotspots_view
from components.explainable_ai import render_explainable_ai_view
from components.analytics_view import render_analytics_view
from components.saved_locations import render_saved_locations_view
from components.history_view import render_history_view
from components.demo_mode import render_demo_mode_view
from components.investor_view import render_investor_view
from components.settings_view import render_settings_view

# Initialize database schema
init_db()

# Apply Dark Glassmorphism CSS design system
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Resolve API Keys from Session State, SQLite, or Environment
google_key = (
    st.session_state.get("google_api_key")
    or get_setting("GOOGLE_MAPS_API_KEY")
    or os.environ.get("GOOGLE_MAPS_API_KEY", "")
).strip()

tomtom_key = (
    st.session_state.get("tomtom_api_key")
    or get_setting("TOMTOM_API_KEY")
    or os.environ.get("TOMTOM_API_KEY", "")
).strip()

# Check system live telemetry connection status
status_info = check_live_traffic_status(google_key=google_key, tomtom_key=tomtom_key)

# Render Sidebar Navigation
selected_page = render_sidebar(status_info)

# Support programmatic navigation across modules (e.g. from Dashboard quick buttons)
if "nav_page" in st.session_state and st.session_state["nav_page"] != selected_page:
    target = st.session_state.pop("nav_page")
    selected_page = target

# Shared state for monitored locations
monitored_locs = st.session_state.get("monitored_locations", [])

# Page Routing
if "🏠 Dashboard" in selected_page:
    render_dashboard(status_info)

elif "🚦 Live Traffic" in selected_page:
    render_live_traffic_view(google_key=google_key, tomtom_key=tomtom_key)

elif "🤖 AI Prediction" in selected_page:
    render_ai_prediction_view()

elif "🔮 Traffic Forecast" in selected_page:
    render_forecast_view()

elif "🔥 Traffic Hotspots" in selected_page:
    render_hotspots_view(monitored_locations=monitored_locs, google_key=google_key)

elif "🛣 Route Advisory" in selected_page:
    render_live_traffic_view(google_key=google_key, tomtom_key=tomtom_key)

elif "📊 Analytics" in selected_page:
    render_analytics_view()

elif "🧠 Explainable AI" in selected_page:
    render_explainable_ai_view()

elif "📍 Saved Locations" in selected_page:
    monitored_locs = render_saved_locations_view(google_key=google_key)
    st.session_state["monitored_locations"] = monitored_locs

elif "📜 History" in selected_page:
    render_history_view()

elif "💼 Investor Mode" in selected_page:
    render_investor_view(status_info)

elif "🎬 Demo Mode" in selected_page:
    render_demo_mode_view()

elif "⚙ Settings" in selected_page:
    render_settings_view()

else:
    render_dashboard(status_info)
