"""
Unit tests for Machine Learning pipeline, model inference, and feature attribution.
"""
import unittest
from ml.predict import predict_traffic_conditions
from ml.model import TrafficModel


class TestMLPipeline(unittest.TestCase):
    def setUp(self):
        self.model = TrafficModel()

    def test_model_loaded(self):
        self.assertTrue(self.model.is_loaded())
        self.assertIn("accuracy", self.model.metadata)
        self.assertGreaterEqual(self.model.metadata["accuracy"], 0.85)

    def test_prediction_output_contract(self):
        # Peak morning rush hour with high vehicle count
        result = predict_traffic_conditions(
            hour=9,
            day_of_week=1,
            road_type="Arterial",
            weather="Clear",
            vehicle_count=1400,
        )
        self.assertEqual(result["data_source"], "ML PREDICTION")
        self.assertIn(result["predicted_class"], ["LOW", "MEDIUM", "HIGH"])
        self.assertGreaterEqual(result["confidence_pct"], 0.0)
        self.assertLessEqual(result["confidence_pct"], 100.0)
        self.assertGreaterEqual(result["risk_score"], 0)
        self.assertLessEqual(result["risk_score"], 100)
        self.assertIn("feature_contributions", result)
        self.assertIn("ai_insight", result)

    def test_confidence_not_equal_to_risk(self):
        # Midnight low volume
        result = predict_traffic_conditions(
            hour=2,
            day_of_week=2,
            road_type="Highway",
            weather="Clear",
            vehicle_count=120,
        )
        # Even if confidence is 99%, risk must be in LOW range (<40)
        self.assertEqual(result["predicted_class"], "LOW")
        self.assertLess(result["risk_score"], 40)
        self.assertNotEqual(result["risk_score"], int(result["confidence_pct"]))


if __name__ == "__main__":
    unittest.main()
