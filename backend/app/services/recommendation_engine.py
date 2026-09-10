from typing import Dict, List, Any
from app.schemas.recommendation import RecommendationResponse, RecommendationItem

def generate_recommendations(
    failure_probability: float,
    is_anomaly: bool,
    top_shap_features: List[str],
    machine_params: Dict[str, float]
) -> RecommendationResponse:
    if failure_probability >= 0.70:
        risk_level = "CRITICAL"
        urgency = "Immediate line halt / priority service required"
    elif failure_probability >= 0.35:
        risk_level = "WARNING"
        urgency = "Schedule maintenance within 24–48 operating hours"
    elif is_anomaly:
        risk_level = "ANOMALOUS"
        urgency = "Perform inspection and sensor check before next shift"
    else:
        risk_level = "HEALTHY"
        urgency = "Continue standard routine inspection schedule"

    recommendations: List[RecommendationItem] = []
    root_cause_indicators: List[str] = []

    tool_wear = machine_params.get("Tool wear [min]", machine_params.get("ToolWear", 0.0))
    torque = machine_params.get("Torque [Nm]", machine_params.get("Torque", 0.0))
    rpm = machine_params.get("Rotational speed [rpm]", machine_params.get("RotationalSpeed", 0.0))
    air_temp = machine_params.get("Air temperature [K]", machine_params.get("AirTemp", 300.0))
    proc_temp = machine_params.get("Process temperature [K]", machine_params.get("ProcessTemp", 310.0))
    
    temp_diff = proc_temp - air_temp
    power_proxy = torque * (rpm * 0.10472)
    shap_set = set(top_shap_features)

    # Tool Wear Failure (TWF)
    if tool_wear >= 200 or "Tool wear [min]" in shap_set or "ToolWear" in shap_set:
        root_cause_indicators.append(f"Tool wear reached critical threshold: {tool_wear:.1f} min.")
        recommendations.append(
            RecommendationItem(
                id="REC-TOOL-001",
                category="TOOLING",
                severity="CRITICAL" if failure_probability >= 0.50 else "WARNING",
                title="Replace Cutting Tool Assembly",
                action=f"Tool wear is at {tool_wear:.1f} min. Replace cutting bit/insert immediately to avoid breakage."
            )
        )

    # Heat Dissipation Failure (HDF)
    if (temp_diff < 8.6 and proc_temp > 310) or "Temp_Diff" in shap_set or "Process temperature [K]" in shap_set:
        root_cause_indicators.append(f"Insufficient heat dissipation: Delta T is {temp_diff:.2f} K.")
        recommendations.append(
            RecommendationItem(
                id="REC-THRM-002",
                category="THERMAL",
                severity="CRITICAL" if failure_probability >= 0.50 else "WARNING",
                title="Inspect Cooling & Heat Dissipation",
                action=f"Delta T is {temp_diff:.1f} K. Flush coolant channels, check pump pressure, and clean air filters."
            )
        )

    # Mechanical Strain / Power (PWF)
    if power_proxy > 9000 or torque > 65 or "Torque [Nm]" in shap_set or "Torque" in shap_set:
        root_cause_indicators.append(f"Excessive mechanical load: Torque {torque:.1f} Nm, Power Proxy {power_proxy:.0f} W.")
        recommendations.append(
            RecommendationItem(
                id="REC-MECH-003",
                category="MECHANICAL",
                severity="CRITICAL" if failure_probability >= 0.50 else "WARNING",
                title="Inspect Drive Train & Spindle Load",
                action=f"High torque load detected ({torque:.1f} Nm). Check for mechanical binding and verify feed rate."
            )
        )

    # Anomaly
    if is_anomaly and not recommendations:
        root_cause_indicators.append("Machine telemetry deviates from baseline normal distribution.")
        recommendations.append(
            RecommendationItem(
                id="REC-ANOM-004",
                category="INSPECTION",
                severity="INFO",
                title="Calibrate Sensors and Log Vibration",
                action="Operating envelope is unusual without imminent failure. Recalibrate sensors and inspect for vibration."
            )
        )

    # Normal state
    if not recommendations:
        recommendations.append(
            RecommendationItem(
                id="REC-HLTH-000",
                category="INSPECTION",
                severity="INFO",
                title="Standard Operating Verification",
                action="All parameters within acceptable tolerances. Maintain standard shift logging."
            )
        )

    return RecommendationResponse(
        risk_level=risk_level,
        urgency=urgency,
        root_cause_indicators=root_cause_indicators,
        recommendations=recommendations
    )
