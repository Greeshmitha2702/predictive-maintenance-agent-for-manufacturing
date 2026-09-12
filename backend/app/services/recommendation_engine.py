from math import pi
from typing import Any, Dict, List

from app.schemas.recommendation import RecommendationItem, RecommendationResponse


# Prototype operating thresholds.
# The LLD defines the rules but does not specify numeric operating thresholds,
# so these remain configurable here.
TOOL_WEAR_THRESHOLD = 200.0
TORQUE_THRESHOLD = 65.0
MECHANICAL_POWER_THRESHOLD = 9000.0

# Prototype minimum SHAP magnitude for a "strong" contributor.
SHAP_MIN_CONTRIBUTION = 0.05


def _normalise_feature_name(feature: str) -> str:
    """Normalise feature names so model/schema naming differences are handled."""
    return feature.strip().lower().replace(" ", "_").replace("-", "_")


def _positive_shap_features(shap_contributors: List[Any]) -> set[str]:
    """
    Return features that positively contribute to failure risk.

    A feature is considered relevant only when:
    - its SHAP direction says it increases failure risk, and
    - its signed contribution is sufficiently positive.
    """
    positive_features: set[str] = set()

    for contributor in shap_contributors:
        feature = getattr(contributor, "feature", None)
        contribution = getattr(contributor, "contribution", None)
        direction = getattr(contributor, "direction", None)

        if not feature or contribution is None or direction is None:
            continue

        if (
            direction == "increases_failure_risk"
            and float(contribution) >= SHAP_MIN_CONTRIBUTION
        ):
            positive_features.add(_normalise_feature_name(feature))

    return positive_features


def generate_recommendations(
    risk_level: str,
    is_anomaly: bool,
    shap_contributors: List[Any],
    machine_params: Dict[str, float],
) -> RecommendationResponse:
    """
    Generate deterministic preventive-maintenance recommendations.

    Risk classification is owned by the RiskAssessment layer.
    This engine only consumes the resulting LOW/MEDIUM/HIGH risk level.

    The engine does not calculate SHAP values or use an ML model.
    """

    if risk_level not in {"LOW", "MEDIUM", "HIGH"}:
        raise ValueError(
            "risk_level must be one of: LOW, MEDIUM, HIGH"
        )

    required_fields = {
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
    }

    missing_fields = required_fields - set(machine_params.keys())

    if missing_fields:
        raise ValueError(
            "Missing required machine parameters: "
            + ", ".join(sorted(missing_fields))
        )

    # Use the actual backend API fields directly.
    air_temperature = float(machine_params["air_temperature"])
    process_temperature = float(machine_params["process_temperature"])
    rotational_speed = float(machine_params["rotational_speed"])
    torque = float(machine_params["torque"])
    tool_wear = float(machine_params["tool_wear"])

    # Engineered features defined by the project LLD.
    temperature_difference = process_temperature - air_temperature
    mechanical_power_w = torque * rotational_speed * (2 * pi / 60)
    overstrain_index = tool_wear * torque

    positive_shap = _positive_shap_features(shap_contributors)

    recommendations: List[RecommendationItem] = []
    root_cause_indicators: List[str] = []

    # ---------------------------------------------------------
    # Risk-level urgency
    # ---------------------------------------------------------
    if risk_level == "HIGH":
        urgency = "Prioritize preventive maintenance before the next operating cycle"
    elif risk_level == "MEDIUM":
        urgency = "Schedule preventive maintenance within 24–48 operating hours"
    else:
        urgency = "Continue standard preventive maintenance schedule"

    # ---------------------------------------------------------
    # Tool wear
    #
    # LLD:
    # IF tool_wear is high
    # AND tool_wear is a major positive SHAP contributor
    # THEN recommend tool inspection/replacement.
    # ---------------------------------------------------------
    tool_wear_shap = {
        "tool_wear",
        "tool_wear_min",
        "toolwear",
    }

    if (
        tool_wear >= TOOL_WEAR_THRESHOLD
        and positive_shap.intersection(tool_wear_shap)
    ):
        root_cause_indicators.append(
            f"High tool wear ({tool_wear:.1f} min) is a positive failure-risk contributor."
        )

        recommendations.append(
            RecommendationItem(
                id="REC-TOOL-001",
                category="TOOLING",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect or Replace Cutting Tool",
                action=(
                    f"Tool wear is {tool_wear:.1f} min and is contributing "
                    "positively to failure risk. Inspect the cutting tool and "
                    "replace the insert/bit if wear is confirmed."
                ),
            )
        )

    # ---------------------------------------------------------
    # Thermal conditions
    #
    # Temperature recommendation is driven by a positive SHAP
    # contribution from a temperature-related feature.
    # ---------------------------------------------------------
    temperature_shap = {
        "air_temperature",
        "process_temperature",
        "temperature_difference",
        "temp_diff",
        "process_temp",
        "air_temp",
    }

    if positive_shap.intersection(temperature_shap):
        root_cause_indicators.append(
            "Temperature-related features are positive contributors to failure risk."
        )

        recommendations.append(
            RecommendationItem(
                id="REC-THRM-002",
                category="THERMAL",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect Cooling and Thermal Conditions",
                action=(
                    f"Temperature difference is {temperature_difference:.2f} K. "
                    "Check cooling flow, coolant condition, pump operation, "
                    "airflow, and process temperature stability."
                ),
            )
        )

    # ---------------------------------------------------------
    # Mechanical load / torque / power
    #
    # Handle both operating boundaries:
    # - torque
    # - calculated mechanical power
    #
    # A measurement alone is not enough; the corresponding SHAP
    # feature must also positively contribute to failure risk.
    # ---------------------------------------------------------
    mechanical_shap = {
        "torque",
        "mechanical_power_w",
        "mechanical_power",
        "rotational_speed",
    }

    high_mechanical_load = (
        torque >= TORQUE_THRESHOLD
        or mechanical_power_w >= MECHANICAL_POWER_THRESHOLD
    )

    if high_mechanical_load and positive_shap.intersection(mechanical_shap):
        root_cause_indicators.append(
            f"High mechanical load detected "
            f"(torque {torque:.1f} Nm, mechanical power {mechanical_power_w:.0f} W)."
        )

        recommendations.append(
            RecommendationItem(
                id="REC-MECH-003",
                category="MECHANICAL",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect Mechanical Load and Drive Train",
                action=(
                    f"Torque is {torque:.1f} Nm and calculated mechanical power "
                    f"is {mechanical_power_w:.0f} W. Inspect the drive train, "
                    "spindle/load conditions, mechanical binding, and feed rate."
                ),
            )
        )

    # ---------------------------------------------------------
    # Anomaly + HIGH risk
    #
    # This recommendation MUST be generated even if another
    # recommendation has already been added.
    # ---------------------------------------------------------
    if is_anomaly and risk_level == "HIGH":
        root_cause_indicators.append(
            "Anomalous machine telemetry is combined with HIGH failure risk."
        )

        recommendations.append(
            RecommendationItem(
                id="REC-ANOM-HIGH-005",
                category="INSPECTION",
                severity="CRITICAL",
                title="Perform Prompt Machine Inspection",
                action=(
                    "Anomaly detection and HIGH failure risk are both present. "
                    "Prioritize machine inspection, verify sensor readings, "
                    "and review recent operating conditions before continued operation."
                ),
            )
        )

    # ---------------------------------------------------------
    # Anomaly without HIGH risk
    # ---------------------------------------------------------
    elif is_anomaly:
        root_cause_indicators.append(
            "Machine telemetry deviates from the expected operating baseline."
        )

        recommendations.append(
            RecommendationItem(
                id="REC-ANOM-004",
                category="INSPECTION",
                severity="WARNING" if risk_level == "MEDIUM" else "INFO",
                title="Inspect Sensors and Operating Conditions",
                action=(
                    "Review sensor readings, recalibrate sensors if necessary, "
                    "and inspect for unusual vibration or operating conditions."
                ),
            )
        )

    # ---------------------------------------------------------
    # Risk-aware fallback
    #
    # Never return a healthy/normal recommendation for HIGH risk.
    # ---------------------------------------------------------
    if not recommendations:
        if risk_level == "HIGH":
            root_cause_indicators.append(
                "HIGH failure risk requires preventive inspection even without a specific rule match."
            )

            recommendations.append(
                RecommendationItem(
                    id="REC-HIGH-000",
                    category="INSPECTION",
                    severity="CRITICAL",
                    title="Prioritize Preventive Inspection",
                    action=(
                        "Failure risk is HIGH. Perform a priority preventive "
                        "inspection and review machine operating conditions "
                        "before the next operating cycle."
                    ),
                )
            )

        elif risk_level == "MEDIUM":
            recommendations.append(
                RecommendationItem(
                    id="REC-MED-000",
                    category="INSPECTION",
                    severity="WARNING",
                    title="Schedule Preventive Inspection",
                    action=(
                        "Failure risk is MEDIUM. Schedule a preventive inspection "
                        "and continue monitoring machine parameters."
                    ),
                )
            )

        else:
            recommendations.append(
                RecommendationItem(
                    id="REC-LOW-000",
                    category="INSPECTION",
                    severity="INFO",
                    title="Continue Standard Maintenance",
                    action=(
                        "Failure risk is LOW and no specific maintenance trigger "
                        "was identified. Continue standard inspection and shift logging."
                    ),
                )
            )

    return RecommendationResponse(
        risk_level=risk_level,
        urgency=urgency,
        root_cause_indicators=root_cause_indicators,
        recommendations=recommendations,
    )
