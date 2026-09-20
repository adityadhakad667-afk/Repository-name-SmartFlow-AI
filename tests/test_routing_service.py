"""
Unit tests for Routing and Geocoding services.
Verifies offline handling, polyline decoding, and recommendation logic.
"""
import unittest
from services.routing_service import (
    decode_google_polyline,
    fetch_google_routes,
    recommend_route,
)
from services.traffic_service import check_live_traffic_status
from services.geocoding_service import geocode_address


class TestRoutingService(unittest.TestCase):
    def test_missing_api_key_handling(self):
        # Should NOT crash, should return OFFLINE status
        result = fetch_google_routes(
            origin_lat=26.9196,
            origin_lon=75.7878,
            dest_lat=26.9239,
            dest_lon=75.8267,
            api_key="",
        )
        self.assertEqual(result["status"], "OFFLINE")
        self.assertIn("Configure GOOGLE_MAPS_API_KEY", result["error"])
        self.assertEqual(len(result["routes"]), 0)

    def test_live_traffic_status_offline(self):
        status = check_live_traffic_status(google_key="", tomtom_key="")
        self.assertFalse(status["is_connected"])
        self.assertEqual(status["status_text"], "● LIVE TRAFFIC OFFLINE")

    def test_polyline_decoder(self):
        # Known polyline string for: [(38.5, -120.2), (40.7, -120.95), (43.252, -126.453)]
        test_encoded = "_p~iF~ps|U_ulLnnqC_mqNvxq`@"
        coords = decode_google_polyline(test_encoded)
        self.assertEqual(len(coords), 3)
        self.assertAlmostEqual(coords[0][0], 38.5, places=3)
        self.assertAlmostEqual(coords[0][1], -120.2, places=3)

    def test_recommend_route(self):
        routes = [
            {"route_index": 1, "eta_min": 25.0, "delay_min": 10.0, "risk_score": 60},
            {"route_index": 2, "eta_min": 28.0, "delay_min": 2.0, "risk_score": 25},
            {"route_index": 3, "eta_min": 22.0, "delay_min": 6.0, "risk_score": 45},
        ]
        fastest = recommend_route(routes, preference="Fastest")
        self.assertEqual(fastest["route_index"], 3)  # lowest eta (22 min)

        least_traffic = recommend_route(routes, preference="Least Traffic")
        self.assertEqual(least_traffic["route_index"], 2)  # lowest delay (2 min)

    def test_geocoding_cached_lookup(self):
        lat, lon, addr, err = geocode_address("Jaipur Railway Station")
        self.assertIsNone(err)
        self.assertAlmostEqual(lat, 26.9196, places=2)
        self.assertAlmostEqual(lon, 75.7878, places=2)


if __name__ == "__main__":
    unittest.main()
