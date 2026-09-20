"""
Unit tests for database module.
"""
import unittest
import tempfile
from pathlib import Path
from database.db import (
    init_db,
    get_saved_locations,
    add_saved_location,
    update_saved_location,
    delete_saved_location,
    log_route_history,
    get_route_history,
    clear_route_history,
    get_db_kpis,
)


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_smartflow.db"
        init_db(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_init_and_seed(self):
        locations = get_saved_locations(self.db_path)
        self.assertGreaterEqual(len(locations), 5)
        # Verify no hardcoded risk level was assigned in DB
        for loc in locations:
            self.assertIn("name", loc)
            self.assertIn("latitude", loc)
            self.assertIn("longitude", loc)
            self.assertNotIn("risk_level", loc)  # Must NOT be statically hardcoded

    def test_location_crud(self):
        new_id = add_saved_location(
            name="Test Point",
            address="123 Test Street",
            latitude=26.9000,
            longitude=75.8000,
            category="Hub",
            notes="Testing CRUD",
            db_path=self.db_path,
        )
        self.assertIsInstance(new_id, int)

        # Update
        updated = update_saved_location(
            loc_id=new_id,
            name="Updated Point",
            address="456 Updated Ave",
            latitude=26.9100,
            longitude=75.8100,
            category="Hub",
            notes="Updated note",
            db_path=self.db_path,
        )
        self.assertTrue(updated)

        # Delete
        deleted = delete_saved_location(new_id, self.db_path)
        self.assertTrue(deleted)

    def test_route_history_and_kpis(self):
        log_id = log_route_history(
            start_loc="A",
            dest_loc="B",
            distance_km=15.4,
            eta_min=32.0,
            normal_eta_min=20.0,
            delay_min=12.0,
            risk_score=68,
            traffic_level="MEDIUM",
            data_source="LIVE",
            db_path=self.db_path,
        )
        self.assertIsInstance(log_id, int)
        history = get_route_history(limit=10, db_path=self.db_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["start_loc"], "A")
        self.assertEqual(history[0]["risk_score"], 68)

        kpis = get_db_kpis(self.db_path)
        self.assertEqual(kpis["routes_analyzed"], 1)
        self.assertEqual(kpis["average_delay_min"], 12.0)


if __name__ == "__main__":
    unittest.main()
