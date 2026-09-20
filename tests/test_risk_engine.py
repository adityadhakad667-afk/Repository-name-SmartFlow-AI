"""
Unit tests for Risk Engine.
Validates calculation boundaries, categorization, and the critical invariant:
CONFIDENCE IS NOT RISK.
"""
import unittest
from analytics.risk_engine import (
    compute_route_risk,
    classify_risk_score,
    convert_ml_prediction_to_risk,
)


class TestRiskEngine(unittest.TestCase):
    def test_free_flow_traffic(self):
        # 10 min normal, 10 min traffic (no delay)
        res = compute_route_risk(traffic_duration_sec=600, normal_duration_sec=600)
        self.assertEqual(res["traffic_level"], "LOW")
        self.assertLess(res["risk_score"], 40)
        self.assertEqual(res["delay_min"], 0.0)
        self.assertEqual(res["slowdown_pct"], 0.0)

    def test_moderate_traffic(self):
        # 10 min normal, 13 min traffic (+3 min, 30% delay)
        res = compute_route_risk(traffic_duration_sec=780, normal_duration_sec=600)
        self.assertIn(res["traffic_level"], ["LOW", "MEDIUM"])
        self.assertLess(res["risk_score"], 70)

    def test_severe_traffic(self):
        # 15 min normal, 35 min traffic (+20 min delay, >130% delay)
        res = compute_route_risk(traffic_duration_sec=2100, normal_duration_sec=900)
        self.assertEqual(res["traffic_level"], "HIGH")
        self.assertGreaterEqual(res["risk_score"], 70)
        self.assertGreaterEqual(res["slowdown_pct"], 50.0)

    def test_classify_thresholds(self):
        self.assertEqual(classify_risk_score(0)["level"], "LOW")
        self.assertEqual(classify_risk_score(39)["level"], "LOW")
        self.assertEqual(classify_risk_score(40)["level"], "MEDIUM")
        self.assertEqual(classify_risk_score(69)["level"], "MEDIUM")
        self.assertEqual(classify_risk_score(70)["level"], "HIGH")
        self.assertEqual(classify_risk_score(100)["level"], "HIGH")

    def test_confidence_is_not_risk(self):
        # 99% confidence that traffic is LOW
        confidence = 0.99
        predicted_label = "LOW"
        risk_score, level = convert_ml_prediction_to_risk(
            predicted_label=predicted_label,
            confidence=confidence,
            avg_speed=55.0,
            free_flow_speed=60.0,
        )
        # Risk score must be in the LOW range (<40), NOT 99!
        self.assertEqual(level, "LOW")
        self.assertLess(risk_score, 40)
        self.assertNotEqual(risk_score, 99)
        self.assertNotEqual(risk_score, int(confidence * 100))


if __name__ == "__main__":
    unittest.main()
