"""
Deterministic Recommendation Engine — RE-2
============================================
Generates preventive-maintenance recommendations from risk level, anomaly
status, raw machine parameters and SHAP feature attributions.

Architecture boundaries:
- This engine consumes risk_level (LOW/MEDIUM/HIGH) from RiskAssessmentService.
- It does NOT calculate failure probability or risk level itself.
- It does NOT call ML models, retrain anything, or use an LLM.
- Recommendations are preventive suggestions only; they do not claim guaranteed
  physical root causes, exact failure diagnoses, or automated machine-control actions.
"""

from math import pi
from typing import Any, Dict, List, Optional

from app.schemas.recommendation import RecommendationItem, RecommendationResponse


# ---------------------------------------------------------------------------
# Operating thresholds — change values here to recalibrate rules globally.
# ---------------------------------------------------------------------------

# Tool wear (minutes) — two-tier
TOOL_WEAR_ELEVATED: float = 180.0   # Plan inspection/replacement
TOOL_WEAR_CRITICAL: float = 230.0   # Prompt inspection before continued operation

# Torque (Nm)
TORQUE_HIGH: float = 65.0

# Mechanical power (W = Nm × rad/s)
MECHANICAL_POWER_HIGH: float = 9000.0

# Process temperature (K)
PROCESS_TEMP_HIGH: float = 313.0

# Air temperature (K)
AIR_TEMP_HIGH: float = 303.0

# Temperature differential: process_temperature − air_temperature (K)
TEMP_DIFF_HIGH: float = 13.0     # Larger than expected → cooling stress
TEMP_DIFF_LOW: float = 8.0       # Smaller than expected → under-load or sensor issue

# Rotational speed (rpm)
SPEED_LOW: float = 1300.0
SPEED_HIGH: float = 2500.0

# Minimum positive SHAP contribution magnitude to be treated as a
# "meaningful" risk driver.  Contributions below this threshold are
# considered model noise.
SHAP_MIN_CONTRIBUTION: float = 0.05

# Minimum number of independent positive SHAP contributors before the
# "multi-factor risk" recommendation fires.
SHAP_MULTI_FACTOR_COUNT: int = 3


# ---------------------------------------------------------------------------
# Allowed risk level values
# ---------------------------------------------------------------------------
_VALID_RISK_LEVELS = {"LOW", "MEDIUM", "HIGH"}


# ---------------------------------------------------------------------------
# Feature-name normalisation
# ---------------------------------------------------------------------------

def _normalise_feature_name(feature: str) -> str:
    """
    Map raw feature names (including ML pipeline output names with units)
    to canonical snake_case identifiers used by rule matching sets.
    """
    normalised = feature.strip().lower()

    _ALIASES: Dict[str, str] = {
        # Raw sensor names with units (as the model may emit them)
        "tool wear [min]": "tool_wear",
        "tool_wear [min]": "tool_wear",
        "torque [nm]": "torque",
        "rotational speed [rpm]": "rotational_speed",
        "air temperature [k]": "air_temperature",
        "process temperature [k]": "process_temperature",
        # Engineered feature names
        "temperature_difference": "temperature_difference",
        "mechanical_power_w": "mechanical_power_w",
        "overstrain_index": "overstrain_index",
    }

    return _ALIASES.get(normalised, normalised.replace(" ", "_").replace("-", "_"))


# ---------------------------------------------------------------------------
# SHAP helper
# ---------------------------------------------------------------------------

def _positive_shap_features(shap_contributors: List[Any]) -> set:
    """
    Return a set of normalised feature names whose SHAP contribution
    genuinely increases failure risk.

    A feature qualifies only when:
      - direction == "increases_failure_risk", AND
      - signed contribution >= SHAP_MIN_CONTRIBUTION.

    Features with direction == "decreases_failure_risk" are never included,
    regardless of their contribution magnitude.
    """
    positive: set = set()

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
            positive.add(_normalise_feature_name(feature))

    return positive


# ---------------------------------------------------------------------------
# Internal deduplication helper
# ---------------------------------------------------------------------------

def _deduplicate(items: List[RecommendationItem]) -> List[RecommendationItem]:
    """
    Remove recommendations with duplicate ids, preserving insertion order.
    When the same category fires from two rules, retain the first (higher-priority)
    occurrence.
    """
    seen_ids: set = set()
    result: List[RecommendationItem] = []
    for item in items:
        if item.id not in seen_ids:
            seen_ids.add(item.id)
            result.append(item)
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_recommendations(
    risk_level: str,
    is_anomaly: bool,
    shap_contributors: List[Any],
    machine_params: Dict[str, Any],
) -> RecommendationResponse:
    """
    Generate deterministic preventive-maintenance recommendations.

    Parameters
    ----------
    risk_level:
        One of "LOW", "MEDIUM", "HIGH" as produced by RiskAssessmentService.
    is_anomaly:
        Boolean flag from AnomalyDetectionService (independent of risk level).
    shap_contributors:
        List of ShapContributor-compatible objects with .feature, .contribution,
        and .direction attributes.
    machine_params:
        Dictionary of raw machine operating parameters keyed by API field names.

    Returns
    -------
    RecommendationResponse with urgency, root_cause_indicators, and a
    deduplicated list of RecommendationItems ordered by descending severity.
    """

    # ------------------------------------------------------------------
    # Guard: risk_level must be a known value
    # ------------------------------------------------------------------
    if risk_level not in _VALID_RISK_LEVELS:
        raise ValueError(
            f"risk_level must be one of {sorted(_VALID_RISK_LEVELS)}; got {risk_level!r}"
        )

    # ------------------------------------------------------------------
    # Guard: required machine parameters
    # ------------------------------------------------------------------
    _REQUIRED = {
        "air_temperature",
        "process_temperature",
        "rotational_speed",
        "torque",
        "tool_wear",
    }
    missing = _REQUIRED - set(machine_params.keys())
    if missing:
        raise ValueError(
            "Missing required machine parameters: " + ", ".join(sorted(missing))
        )

    # ------------------------------------------------------------------
    # Extract and type-coerce parameters
    # ------------------------------------------------------------------
    air_temperature: float = float(machine_params["air_temperature"])
    process_temperature: float = float(machine_params["process_temperature"])
    rotational_speed: float = float(machine_params["rotational_speed"])
    torque: float = float(machine_params["torque"])
    tool_wear: float = float(machine_params["tool_wear"])

    # Engineered features (consistent with ML feature engineering)
    temperature_difference: float = process_temperature - air_temperature
    mechanical_power_w: float = torque * rotational_speed * (2.0 * pi / 60.0)
    overstrain_index: float = tool_wear * torque

    # ------------------------------------------------------------------
    # SHAP: collect features that genuinely increase failure risk
    # ------------------------------------------------------------------
    positive_shap = _positive_shap_features(shap_contributors)

    recommendations: List[RecommendationItem] = []
    root_cause_indicators: List[str] = []

    # ==================================================================
    # RULE CATEGORY 1 — TOOL WEAR
    # Two tiers: ELEVATED fires on raw threshold; CRITICAL on higher raw
    # threshold.  SHAP confirmation is required for both.
    # When CRITICAL fires, ELEVATED is suppressed (higher-priority wins).
    # ==================================================================
    _TOOL_WEAR_SHAP = {"tool_wear", "tool_wear_min", "toolwear", "overstrain_index"}

    tool_shap_hit = bool(positive_shap.intersection(_TOOL_WEAR_SHAP))

    if tool_wear >= TOOL_WEAR_CRITICAL and tool_shap_hit:
        root_cause_indicators.append(
            f"Tool wear ({tool_wear:.1f} min) is in the critical range and is a "
            "positive failure-risk contributor."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-TOOL-002",
                category="TOOLING",
                severity="CRITICAL",
                title="Inspect Cutting Tool — Critical Wear Level",
                action=(
                    f"Tool wear is {tool_wear:.1f} min, which is in the critical range. "
                    "Inspect the cutting tool before continuing operation and consider "
                    "replacement if wear is confirmed by physical inspection."
                ),
            )
        )
    elif tool_wear >= TOOL_WEAR_ELEVATED and tool_shap_hit:
        root_cause_indicators.append(
            f"Tool wear ({tool_wear:.1f} min) is elevated and is a positive "
            "failure-risk contributor."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-TOOL-001",
                category="TOOLING",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect Cutting Tool — Elevated Wear",
                action=(
                    f"Tool wear is {tool_wear:.1f} min. Inspect the cutting tool "
                    "and plan replacement within the current maintenance cycle if "
                    "wear is confirmed."
                ),
            )
        )

    # ==================================================================
    # RULE CATEGORY 2 — THERMAL CONDITIONS
    # Requires at least one raw temperature boundary OR temperature
    # differential boundary to be exceeded, AND a positive SHAP hit on a
    # temperature-related feature.
    # ==================================================================
    _THERMAL_SHAP = {
        "air_temperature",
        "process_temperature",
        "temperature_difference",
        "temp_diff",
        "process_temp",
        "air_temp",
    }

    thermal_shap_hit = bool(positive_shap.intersection(_THERMAL_SHAP))

    raw_thermal_trigger = (
        process_temperature > PROCESS_TEMP_HIGH
        or air_temperature > AIR_TEMP_HIGH
        or temperature_difference > TEMP_DIFF_HIGH
        or temperature_difference < TEMP_DIFF_LOW
    )

    if raw_thermal_trigger and thermal_shap_hit:
        root_cause_indicators.append(
            f"Thermal conditions are outside expected range "
            f"(process temp {process_temperature:.1f} K, "
            f"air temp {air_temperature:.1f} K, "
            f"differential {temperature_difference:.2f} K) "
            "and temperature features are positive risk contributors."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-THRM-001",
                category="THERMAL",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect Cooling and Thermal Conditions",
                action=(
                    f"Temperature difference is {temperature_difference:.2f} K "
                    f"(process: {process_temperature:.1f} K, "
                    f"air: {air_temperature:.1f} K). "
                    "Verify cooling flow, coolant condition, pump operation, "
                    "airflow paths, and process temperature stability."
                ),
            )
        )

    # ==================================================================
    # RULE CATEGORY 3 — MECHANICAL LOAD
    # Requires torque OR mechanical power to exceed threshold, AND a
    # positive SHAP hit on a mechanical feature.
    # ==================================================================
    _MECHANICAL_SHAP = {
        "torque",
        "mechanical_power_w",
        "mechanical_power",
        "rotational_speed",
        "overstrain_index",
    }

    mechanical_shap_hit = bool(positive_shap.intersection(_MECHANICAL_SHAP))

    raw_mechanical_trigger = (
        torque >= TORQUE_HIGH
        or mechanical_power_w >= MECHANICAL_POWER_HIGH
        or rotational_speed < SPEED_LOW
        or rotational_speed > SPEED_HIGH
    )

    if raw_mechanical_trigger and mechanical_shap_hit:
        root_cause_indicators.append(
            f"High mechanical load detected "
            f"(torque {torque:.1f} Nm, "
            f"mechanical power {mechanical_power_w:.0f} W, "
            f"speed {rotational_speed:.0f} rpm)."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-MECH-001",
                category="MECHANICAL",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Inspect Mechanical Load and Drive Train",
                action=(
                    f"Torque is {torque:.1f} Nm and calculated mechanical power "
                    f"is {mechanical_power_w:.0f} W at {rotational_speed:.0f} rpm. "
                    "Inspect the drive train, spindle condition, mechanical binding, "
                    "and verify feed-rate and load setpoints."
                ),
            )
        )

    # ==================================================================
    # RULE CATEGORY 4 — MULTI-FACTOR SHAP
    # Fires when three or more independent features are positive SHAP
    # contributors, regardless of specific category.
    # This supplements (not replaces) individual category rules.
    # ==================================================================
    if len(positive_shap) >= SHAP_MULTI_FACTOR_COUNT:
        root_cause_indicators.append(
            f"Multiple operating parameters ({len(positive_shap)}) are "
            "simultaneously identified as statistical risk contributors."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-MULTI-001",
                category="INSPECTION",
                severity="CRITICAL" if risk_level == "HIGH" else "WARNING",
                title="Review Overall Operating Conditions",
                action=(
                    "Three or more operating parameters are simultaneously "
                    "contributing to the elevated failure probability. "
                    "Review overall machine operating conditions holistically "
                    "rather than targeting a single parameter."
                ),
            )
        )

    # ==================================================================
    # RULE CATEGORY 5 — ANOMALY
    # Anomaly is an independent signal from AnomalyDetectionService.
    # It does NOT alter risk_level; risk_level comes only from
    # RiskAssessmentService.
    # ==================================================================
    if is_anomaly and risk_level == "HIGH":
        # Strongest combined signal — both models raise concern simultaneously
        root_cause_indicators.append(
            "Anomalous machine telemetry is present alongside HIGH failure risk — "
            "two independent models are signalling concern."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-ANOM-HIGH-001",
                category="INSPECTION",
                severity="CRITICAL",
                title="Perform Priority Machine Inspection",
                action=(
                    "Anomaly detection and HIGH failure risk are both signalling concern. "
                    "Prioritise machine inspection, verify sensor readings, and review "
                    "recent operating conditions before continued operation. "
                    "These are independent statistical signals, not a confirmed failure diagnosis."
                ),
            )
        )
    elif is_anomaly:
        # Anomaly without HIGH risk — investigate but do not escalate to CRITICAL
        root_cause_indicators.append(
            "Machine telemetry deviates from the expected operating baseline."
        )
        recommendations.append(
            RecommendationItem(
                id="REC-ANOM-001",
                category="INSPECTION",
                severity="WARNING" if risk_level == "MEDIUM" else "INFO",
                title="Inspect Sensors and Operating Conditions",
                action=(
                    "Operating parameters are statistically unusual compared to the "
                    "training population. Review sensor readings, recalibrate if necessary, "
                    "and inspect for unusual vibration or process drift."
                ),
            )
        )

    # ==================================================================
    # RULE CATEGORY 6 — RISK-LEVEL FALLBACKS
    # Only fire when no more specific recommendation has been generated.
    # Ensure HIGH risk never returns an empty or healthy response.
    # ==================================================================
    if not recommendations:
        if risk_level == "HIGH":
            root_cause_indicators.append(
                "HIGH failure risk requires preventive inspection even without "
                "a specific parameter trigger."
            )
            recommendations.append(
                RecommendationItem(
                    id="REC-HIGH-000",
                    category="INSPECTION",
                    severity="CRITICAL",
                    title="Prioritise Preventive Inspection",
                    action=(
                        "Failure risk is HIGH. Perform a priority preventive inspection "
                        "and review machine operating conditions before the next "
                        "operating cycle."
                    ),
                )
            )

        elif risk_level == "MEDIUM":
            root_cause_indicators.append(
                "Failure risk is elevated above baseline without a specific "
                "parameter trigger."
            )
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

        else:  # LOW
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

    # ------------------------------------------------------------------
    # Urgency string — derived from risk_level, not recalculated
    # ------------------------------------------------------------------
    _URGENCY = {
        "HIGH": "Prioritise preventive maintenance before the next operating cycle",
        "MEDIUM": "Schedule preventive maintenance within 24–48 operating hours",
        "LOW": "Continue standard preventive maintenance schedule",
    }
    urgency = _URGENCY[risk_level]

    return RecommendationResponse(
        risk_level=risk_level,
        urgency=urgency,
        root_cause_indicators=root_cause_indicators,
        recommendations=_deduplicate(recommendations),
    )

