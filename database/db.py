"""
SQLite Database Layer for SmartFlow AI.
Handles persistence for saved locations, search history, settings, and metrics logging.
"""
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Default database location relative to project root
DB_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = DB_DIR / "smartflow.db"


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Create and return a database connection with dictionary-like row access."""
    target = db_path or DEFAULT_DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """Initialize database schema and seed default locations if table is empty."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    # Saved Locations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            category TEXT DEFAULT 'Transit',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Route history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS traffic_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            start_loc TEXT NOT NULL,
            dest_loc TEXT NOT NULL,
            distance_km REAL,
            eta_min REAL,
            normal_eta_min REAL,
            delay_min REAL,
            risk_score INTEGER,
            traffic_level TEXT,
            data_source TEXT
        )
    """)

    # App Settings key-value table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Seed initial saved locations if empty (without any hardcoded risk ratings)
    cursor.execute("SELECT COUNT(*) FROM saved_locations")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_locations = [
            ("Jaipur Railway Station", "Gopalbari, Jaipur, Rajasthan 302001", 26.9196, 75.7878, "Transit", "Major railway junction"),
            ("Hawa Mahal", "Badi Choupad, J.D.A. Market, Jaipur, Rajasthan 302002", 26.9239, 75.8267, "Landmark", "High tourist density zone"),
            ("MI Road", "Mirza Ismail Road, Jaipur, Rajasthan 302001", 26.9167, 75.8055, "Commercial", "Central commercial corridor"),
            ("C-Scheme", "Ashok Nagar / C-Scheme, Jaipur, Rajasthan 302001", 26.9073, 75.8016, "Business", "Office & dining district"),
            ("World Trade Park", "Jawahar Lal Nehru Marg, Malviya Nagar, Jaipur 302017", 26.8532, 75.8050, "Shopping", "Major retail & arterial highway hub"),
            ("Civil Lines", "Civil Lines, Jaipur, Rajasthan 302006", 26.9080, 75.7794, "Residential/Gov", "VIP and transit artery")
        ]
        cursor.executemany("""
            INSERT INTO saved_locations (name, address, latitude, longitude, category, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, seed_locations)

    conn.commit()
    conn.close()


def get_saved_locations(db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieve all saved locations."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM saved_locations ORDER BY id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_saved_location(
    name: str,
    address: str,
    latitude: float,
    longitude: float,
    category: str = "Transit",
    notes: str = "",
    db_path: Optional[Path] = None,
) -> int:
    """Add a new saved location."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO saved_locations (name, address, latitude, longitude, category, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name.strip(), address.strip(), float(latitude), float(longitude), category.strip(), notes.strip()))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_saved_location(
    loc_id: int,
    name: str,
    address: str,
    latitude: float,
    longitude: float,
    category: str = "Transit",
    notes: str = "",
    db_path: Optional[Path] = None,
) -> bool:
    """Update an existing saved location."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE saved_locations
        SET name = ?, address = ?, latitude = ?, longitude = ?, category = ?, notes = ?
        WHERE id = ?
    """, (name.strip(), address.strip(), float(latitude), float(longitude), category.strip(), notes.strip(), loc_id))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def delete_saved_location(loc_id: int, db_path: Optional[Path] = None) -> bool:
    """Delete a saved location by ID."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM saved_locations WHERE id = ?", (loc_id,))
    affected = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return affected


def log_route_history(
    start_loc: str,
    dest_loc: str,
    distance_km: float,
    eta_min: float,
    normal_eta_min: float,
    delay_min: float,
    risk_score: int,
    traffic_level: str,
    data_source: str = "LIVE",
    db_path: Optional[Path] = None,
) -> int:
    """Log an analyzed route to history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO traffic_history 
        (start_loc, dest_loc, distance_km, eta_min, normal_eta_min, delay_min, risk_score, traffic_level, data_source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        start_loc.strip(),
        dest_loc.strip(),
        round(distance_km, 2),
        round(eta_min, 1),
        round(normal_eta_min, 1),
        round(delay_min, 1),
        int(risk_score),
        traffic_level.strip(),
        data_source.strip(),
    ))
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def get_route_history(limit: int = 100, db_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Retrieve recorded route history records ordered by most recent."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM traffic_history ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def clear_route_history(db_path: Optional[Path] = None) -> bool:
    """Clear all records from traffic_history."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM traffic_history")
    conn.commit()
    conn.close()
    return True


def get_setting(key: str, default: Optional[str] = None, db_path: Optional[Path] = None) -> Optional[str]:
    """Retrieve a setting value from SQLite."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key: str, value: str, db_path: Optional[Path] = None) -> None:
    """Insert or update a setting value in SQLite."""
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO app_settings (key, value, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP
    """, (key, value))
    conn.commit()
    conn.close()


def get_db_kpis(db_path: Optional[Path] = None) -> Dict[str, Any]:
    """Compute aggregate KPI metrics from actual database tables."""
    conn = get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM saved_locations")
    loc_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), AVG(delay_min), AVG(risk_score), SUM(distance_km) FROM traffic_history")
    hist_row = cursor.fetchone()
    history_count = hist_row[0] or 0
    avg_delay = hist_row[1] or 0.0
    avg_risk = hist_row[2] or 0.0
    total_km = hist_row[3] or 0.0

    cursor.execute("SELECT COUNT(*) FROM traffic_history WHERE risk_score >= 70")
    high_risk_routes = cursor.fetchone()[0] or 0

    conn.close()
    return {
        "locations_monitored": loc_count,
        "routes_analyzed": history_count,
        "total_km_monitored": round(total_km, 1),
        "average_delay_min": round(avg_delay, 1),
        "average_risk_score": round(avg_risk, 1),
        "active_high_risk_routes": high_risk_routes,
    }
