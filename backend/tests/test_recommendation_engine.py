"""
Unit tests for the deterministic RecommendationEngine (RE-2).

Uses Python standard library unittest to run out-of-the-box without external dependencies.

Run with:
    cd backend
    python tests/test_recommendation_engine.py
"""

import sys
import os
import unittest
from dataclasses import dataclass
from typing import List

# Add backend/ root so that 'from app.xxx import' resolves correctly —
# matching how uvicorn runs the application.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.recommendation_engine import (
    generate_recommendations,
    TOOL_WEAR_ELEVATED,
    TOOL_WEAR_CRITICAL,
    TORQUE_HIGH,
    PROCESS_TEMP_HIGH,
    AIR_TEMP_HIGH,
    TEMP_DIFF_HIGH,
    TEMP_DIFF_LOW,
    SHAP_MIN_CONTRIBUTION,
    SHAP_MULTI_FACTOR_COUNT,
)
from app.schemas.recommendation import RecommendationResponse, RecommendationItem


@dataclass
class FakeContributor:
    """Minimal ShapContributor-compatible object for testing."""
    feature: str
    contribution: float
    direction: str


def _normal_params() -> dict:
    """Normal mid-range machine parameters that trigger no raw-threshold rules."""
    return {
        "air_temperature": 298.0,
        "process_temperature": 308.0,
        "rotational_speed": 1500.0,
        "torque": 40.0,
        "tool_wear": 100.0,
    }


def _make_pos(feature: str, contribution: float = 0.20) -> FakeContributor:
    return FakeContributor(
        feature=feature,
        contribution=contribution,
        direction="increases_failure_risk",
    )


def _make_neg(feature: str, contribution: float = -0.15) -> FakeContributor:
    return FakeContributor(
        feature=feature,
        contribution=contribution,
        direction="decreases_failure_risk",
    )


def _rec_ids(response: RecommendationResponse) -> List[str]:
    return [r.id for r in response.recommendations]


def _categories(response: RecommendationResponse) -> List[str]:
    return [r.category for r in response.recommendations]


def _severities(response: RecommendationResponse) -> List[str]:
    return [r.severity for r in response.recommendations]


class TestRecommendationEngine(unittest.TestCase):

    def test_low_risk_normal_no_shap(self):
        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=False,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertEqual(resp.risk_level, "LOW")
        self.assertEqual(len(resp.recommendations), 1)
        self.assertEqual(resp.recommendations[0].id, "REC-LOW-000")
        self.assertEqual(resp.recommendations[0].severity, "INFO")
        self.assertIn("standard", resp.recommendations[0].action.lower())

    def test_medium_risk_fallback(self):
        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertEqual(resp.risk_level, "MEDIUM")
        self.assertIn("REC-MED-000", _rec_ids(resp))
        self.assertEqual(resp.recommendations[0].severity, "WARNING")
        self.assertGreater(len(resp.root_cause_indicators), 0)

    def test_high_risk_fallback(self):
        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=False,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertEqual(resp.risk_level, "HIGH")
        self.assertIn("REC-HIGH-000", _rec_ids(resp))
        self.assertEqual(resp.recommendations[0].severity, "CRITICAL")
        self.assertGreater(len(resp.root_cause_indicators), 0)

    def test_high_tool_wear_positive_shap(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=[_make_pos("tool_wear")],
            machine_params=params,
        )
        self.assertIn("TOOLING", _categories(resp))
        self.assertTrue(any("REC-TOOL" in rid for rid in _rec_ids(resp)))
        self.assertTrue(any("tool" in r.lower() for r in resp.root_cause_indicators))

    def test_high_tool_wear_negative_shap_no_tool_rec(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=[_make_neg("tool_wear")],
            machine_params=params,
        )
        self.assertNotIn("TOOLING", _categories(resp))
        self.assertIn("REC-MED-000", _rec_ids(resp))

    def test_critical_tool_wear_positive_shap_uses_002(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_CRITICAL + 5.0

        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=False,
            shap_contributors=[_make_pos("tool_wear")],
            machine_params=params,
        )
        self.assertIn("REC-TOOL-002", _rec_ids(resp))
        self.assertNotIn("REC-TOOL-001", _rec_ids(resp))
        self.assertEqual(resp.recommendations[0].severity, "CRITICAL")

    def test_high_torque_positive_shap(self):
        params = _normal_params()
        params["torque"] = TORQUE_HIGH + 5.0

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=[_make_pos("Torque [Nm]")],
            machine_params=params,
        )
        self.assertIn("MECHANICAL", _categories(resp))
        self.assertIn("REC-MECH-001", _rec_ids(resp))

    def test_high_torque_negative_shap_no_mechanical_rec(self):
        params = _normal_params()
        params["torque"] = TORQUE_HIGH + 5.0

        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=False,
            shap_contributors=[_make_neg("Torque [Nm]")],
            machine_params=params,
        )
        self.assertNotIn("MECHANICAL", _categories(resp))
        self.assertIn("REC-LOW-000", _rec_ids(resp))

    def test_temperature_positive_shap_with_raw_trigger(self):
        params = _normal_params()
        params["process_temperature"] = PROCESS_TEMP_HIGH + 2.0

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=[_make_pos("Process temperature [K]")],
            machine_params=params,
        )
        self.assertIn("THERMAL", _categories(resp))
        self.assertIn("REC-THRM-001", _rec_ids(resp))

    def test_temperature_negative_shap_no_thermal_rec(self):
        params = _normal_params()
        params["process_temperature"] = PROCESS_TEMP_HIGH + 2.0

        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=False,
            shap_contributors=[_make_neg("process_temperature")],
            machine_params=params,
        )
        self.assertNotIn("THERMAL", _categories(resp))

    def test_anomaly_low_risk(self):
        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=True,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertIn("REC-ANOM-001", _rec_ids(resp))
        anom_rec = next(r for r in resp.recommendations if r.id == "REC-ANOM-001")
        self.assertEqual(anom_rec.severity, "INFO")
        self.assertNotIn("REC-ANOM-HIGH-001", _rec_ids(resp))

    def test_anomaly_medium_risk(self):
        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=True,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertIn("REC-ANOM-001", _rec_ids(resp))
        anom_rec = next(r for r in resp.recommendations if r.id == "REC-ANOM-001")
        self.assertEqual(anom_rec.severity, "WARNING")

    def test_anomaly_high_risk(self):
        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=True,
            shap_contributors=[],
            machine_params=_normal_params(),
        )
        self.assertIn("REC-ANOM-HIGH-001", _rec_ids(resp))
        anom_rec = next(r for r in resp.recommendations if r.id == "REC-ANOM-HIGH-001")
        self.assertEqual(anom_rec.severity, "CRITICAL")
        self.assertNotIn("REC-ANOM-001", _rec_ids(resp))

    def test_multiple_simultaneous_positive_contributors(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0
        params["torque"] = TORQUE_HIGH + 5.0
        params["process_temperature"] = PROCESS_TEMP_HIGH + 2.0

        contributors = [
            _make_pos("tool_wear"),
            _make_pos("torque"),
            _make_pos("process_temperature"),
        ]

        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertIn("REC-MULTI-001", _rec_ids(resp))
        self.assertIn("TOOLING", _categories(resp))
        self.assertIn("MECHANICAL", _categories(resp))
        self.assertIn("THERMAL", _categories(resp))

    def test_no_duplicate_recommendation_ids(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0
        params["torque"] = TORQUE_HIGH + 5.0
        params["process_temperature"] = PROCESS_TEMP_HIGH + 2.0

        contributors = [
            _make_pos("tool_wear"),
            _make_pos("torque"),
            _make_pos("process_temperature"),
            _make_pos("rotational_speed"),
        ]

        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=True,
            shap_contributors=contributors,
            machine_params=params,
        )
        ids = _rec_ids(resp)
        self.assertEqual(len(ids), len(set(ids)), f"Duplicate IDs found: {ids}")

    def test_invalid_risk_level_raises(self):
        with self.assertRaises(ValueError):
            generate_recommendations(
                risk_level="UNKNOWN",
                is_anomaly=False,
                shap_contributors=[],
                machine_params=_normal_params(),
            )

        with self.assertRaises(ValueError):
            generate_recommendations(
                risk_level="",
                is_anomaly=False,
                shap_contributors=[],
                machine_params=_normal_params(),
            )

    def test_missing_machine_parameter_raises(self):
        params = _normal_params()
        del params["tool_wear"]

        with self.assertRaises(ValueError):
            generate_recommendations(
                risk_level="LOW",
                is_anomaly=False,
                shap_contributors=[],
                machine_params=params,
            )

    def test_shap_feature_names_with_units(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0

        contributors = [
            FakeContributor(
                feature="Tool wear [min]",
                contribution=0.30,
                direction="increases_failure_risk",
            )
        ]

        resp = generate_recommendations(
            risk_level="HIGH",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertIn("TOOLING", _categories(resp))

    def test_shap_torque_with_units(self):
        params = _normal_params()
        params["torque"] = TORQUE_HIGH + 5.0

        contributors = [
            FakeContributor(
                feature="Torque [Nm]",
                contribution=0.25,
                direction="increases_failure_risk",
            )
        ]

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertIn("MECHANICAL", _categories(resp))

    def test_decreases_direction_never_triggers_risk_recommendation(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_CRITICAL + 10.0

        contributors = [
            FakeContributor(
                feature="tool_wear",
                contribution=-0.50,
                direction="decreases_failure_risk",
            ),
            FakeContributor(
                feature="torque",
                contribution=-0.30,
                direction="decreases_failure_risk",
            ),
            FakeContributor(
                feature="process_temperature",
                contribution=-0.20,
                direction="decreases_failure_risk",
            ),
        ]

        resp = generate_recommendations(
            risk_level="MEDIUM",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertNotIn("TOOLING", _categories(resp))
        self.assertNotIn("MECHANICAL", _categories(resp))
        self.assertNotIn("THERMAL", _categories(resp))
        self.assertIn("REC-MED-000", _rec_ids(resp))

    def test_low_shap_contribution_ignored(self):
        params = _normal_params()
        params["tool_wear"] = TOOL_WEAR_ELEVATED + 5.0

        contributors = [
            FakeContributor(
                feature="tool_wear",
                contribution=SHAP_MIN_CONTRIBUTION - 0.01,
                direction="increases_failure_risk",
            )
        ]

        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertNotIn("TOOLING", _categories(resp))

    def test_urgency_matches_risk_level(self):
        for risk, expected_fragment in [
            ("HIGH", "before the next operating cycle"),
            ("MEDIUM", "24"),
            ("LOW", "standard"),
        ]:
            resp = generate_recommendations(
                risk_level=risk,
                is_anomaly=False,
                shap_contributors=[],
                machine_params=_normal_params(),
            )
            self.assertIn(expected_fragment, resp.urgency)

    def test_thermal_shap_without_raw_trigger_does_not_fire(self):
        params = _normal_params()
        params["process_temperature"] = 308.0
        params["air_temperature"] = 298.0

        contributors = [_make_pos("process_temperature")]

        resp = generate_recommendations(
            risk_level="LOW",
            is_anomaly=False,
            shap_contributors=contributors,
            machine_params=params,
        )
        self.assertNotIn("THERMAL", _categories(resp))


if __name__ == "__main__":
    unittest.main()
