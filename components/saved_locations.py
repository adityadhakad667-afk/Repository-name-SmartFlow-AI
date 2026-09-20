"""
Saved Locations & Live Batch Monitor Component for SmartFlow AI.
Manages persistent locations in SQLite and provides live real-time traffic monitoring.

CRITICAL INVARIANTS:
- Saved locations do NOT have permanent static risk levels.
- Status is computed dynamically on refresh.
- If live traffic API is offline, displays 'Live data unavailable' and NEVER invents values.
"""
from typing import Any, Dict, List, Optional
import streamlit as st
import pandas as pd

from database.db import (
    get_saved_locations,
    add_saved_location,
    delete_saved_location,
    update_saved_location,
)
from services.traffic_service import monitor_live_locations, check_live_traffic_status
from services.geocoding_service import geocode_address


def render_saved_locations_view(google_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Render Saved Locations and Live Monitor.
    Returns the list of monitored locations for use by hotspots or dashboard.
    """
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h2 style="margin: 0; font-size: 1.6rem; color: #F8FAFC; display: flex; align-items: center; gap: 8px;">
            <span>📍</span> Saved Locations & Live Batch Monitor
        </h2>
        <p style="color: #94A3B8; font-size: 0.85rem; margin-top: 4px;">
            Manage strategic transit hubs and monitor real-time road conditions across your network.
        </p>
    </div>
    """, unsafe_allow_html=True)

    status_info = check_live_traffic_status(google_key=google_key)

    tab_monitor, tab_manage = st.tabs(["🚦 Live Network Monitor", "⚙ Manage Saved Locations"])

    # 1. Live Monitor Tab
    with tab_monitor:
        locations = get_saved_locations()

        col_hdr, col_act = st.columns([1.5, 1])
        with col_hdr:
            if status_info["is_connected"]:
                st.markdown('<span class="sf-badge-live">● LIVE MONITOR ACTIVE</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="sf-badge-offline">● LIVE DATA UNAVAILABLE (API OFFLINE)</span>', unsafe_allow_html=True)
        
        with col_act:
            refresh_clicked = st.button("🔄 Refresh All Live Telemetry", use_container_width=True, type="primary")

        # Initialize or update monitored locations state
        if refresh_clicked or "monitored_locations" not in st.session_state:
            with st.spinner("Polling live corridor conditions..."):
                monitored = monitor_live_locations(locations, google_key=google_key)
                st.session_state["monitored_locations"] = monitored
        else:
            monitored = st.session_state["monitored_locations"]

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Monitored locations table
        rows = []
        for m in monitored:
            if m.get("status") == "LIVE" and m.get("risk_score") is not None:
                risk_display = f"{m['risk_score']} / 100"
                level_display = f"{m['badge_icon']} {m['traffic_level']}"
                delay_display = f"+{m['delay_min']} min"
            else:
                risk_display = "--"
                level_display = "⚪ N/A"
                delay_display = m.get("display_text", "Live data unavailable")

            rows.append({
                "Location": m["name"],
                "Address": m["address"],
                "Congestion Level": level_display,
                "Risk Score": risk_display,
                "Traffic Delay": delay_display,
                "Last Polled": m["updated_at"],
            })

        df_mon = pd.DataFrame(rows)
        st.dataframe(df_mon, use_container_width=True, hide_index=True)

        if not status_info["is_connected"]:
            st.info("💡 Note: Status shows 'Live data unavailable' because no active GOOGLE_MAPS_API_KEY is configured. Real-time values are never faked.")

    # 2. Manage Saved Locations Tab
    with tab_manage:
        st.markdown("<h3 style='font-size: 1.1rem; margin-top: 0;'>➕ Add New Strategic Location</h3>", unsafe_allow_html=True)
        
        with st.form("add_location_form"):
            c_name, c_addr, c_cat = st.columns([1.2, 1.8, 1.0])
            with c_name:
                new_name = st.text_input("Location Name", placeholder="e.g. MI Road Junction")
            with c_addr:
                new_addr = st.text_input("Address / Query", placeholder="e.g. MI Road, Jaipur")
            with c_cat:
                new_cat = st.selectbox("Category", ["Transit", "Commercial", "Business", "Shopping", "Residential", "Highway Hub"])

            new_notes = st.text_input("Operational Notes (Optional)", placeholder="e.g. Major bottleneck during evening rush")
            submitted = st.form_submit_button("Save Location & Geocode Coordinates")

            if submitted:
                if not new_name.strip() or not new_addr.strip():
                    st.error("Name and Address cannot be empty.")
                else:
                    lat, lon, resolved_addr, err = geocode_address(new_addr, api_key=google_key)
                    if err:
                        st.error(f"Geocoding Error: {err}")
                    else:
                        add_saved_location(
                            name=new_name,
                            address=resolved_addr or new_addr,
                            latitude=lat,
                            longitude=lon,
                            category=new_cat,
                            notes=new_notes,
                        )
                        st.success(f"Saved '{new_name}' at ({lat:.4f}, {lon:.4f}).")
                        # Reset monitored locations in session state to force refresh
                        st.session_state.pop("monitored_locations", None)
                        st.rerun()

        st.markdown("<h3 style='font-size: 1.1rem; margin-top: 1.5rem;'>📍 Existing Monitored Locations</h3>", unsafe_allow_html=True)
        current_locs = get_saved_locations()
        if current_locs:
            for loc in current_locs:
                col_info, col_del = st.columns([4, 1])
                with col_info:
                    st.markdown(f"""
                    <div style="background: rgba(15, 23, 42, 0.6); padding: 10px 14px; border-radius: 8px; border-left: 3px solid #38BDF8; margin-bottom: 6px;">
                        <strong style="color: #F8FAFC;">{loc['name']}</strong> <span style="font-size: 0.75rem; color: #94A3B8;">({loc['category']})</span><br/>
                        <span style="font-size: 0.8rem; color: #64748B;">{loc['address']} | Coords: {loc['latitude']:.4f}, {loc['longitude']:.4f}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑 Delete", key=f"del_loc_{loc['id']}", use_container_width=True):
                        delete_saved_location(loc["id"])
                        st.session_state.pop("monitored_locations", None)
                        st.rerun()
        else:
            st.info("No saved locations present in SQLite database.")

    return st.session_state.get("monitored_locations", [])
