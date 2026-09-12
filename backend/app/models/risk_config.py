"""
Risk Assessment Configuration
==============================
All failure-probability thresholds for risk classification live here.

Interpretation:
    failure_probability in [0.0, RISK_MEDIUM_THRESHOLD)  → "LOW"
    failure_probability in [RISK_MEDIUM_THRESHOLD, RISK_HIGH_THRESHOLD) → "MEDIUM"
    failure_probability in [RISK_HIGH_THRESHOLD, 1.0]    → "HIGH"

Anomaly status is a separate independent signal and does NOT affect
the risk level produced by RiskAssessmentService.

Adjusting these values is the ONLY change needed to recalibrate risk levels.
"""

# Minimum failure probability (inclusive) to classify as MEDIUM risk.
RISK_MEDIUM_THRESHOLD: float = 0.30

# Minimum failure probability (inclusive) to classify as HIGH risk.
RISK_HIGH_THRESHOLD: float = 0.70

# Valid risk level labels.
RISK_LEVEL_LOW: str = "LOW"
RISK_LEVEL_MEDIUM: str = "MEDIUM"
RISK_LEVEL_HIGH: str = "HIGH"

# Fallback label when failure_probability is invalid or unavailable.
RISK_LEVEL_UNKNOWN: str = "UNKNOWN"
