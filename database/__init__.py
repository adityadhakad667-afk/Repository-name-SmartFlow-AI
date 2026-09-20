"""
Database module for SmartFlow AI.
Manages SQLite connection, schema initialization, saved locations, and route history.
"""
from .db import (
    init_db,
    get_saved_locations,
    add_saved_location,
    update_saved_location,
    delete_saved_location,
    log_route_history,
    get_route_history,
    clear_route_history,
    get_setting,
    set_setting,
    get_db_kpis,
)

__all__ = [
    "init_db",
    "get_saved_locations",
    "add_saved_location",
    "update_saved_location",
    "delete_saved_location",
    "log_route_history",
    "get_route_history",
    "clear_route_history",
    "get_setting",
    "set_setting",
    "get_db_kpis",
]
