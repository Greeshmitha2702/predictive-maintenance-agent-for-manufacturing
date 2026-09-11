import logging
import math
from typing import Optional

from models.risk_config import (
    RISK_HIGH_THRESHOLD,
    RISK_MEDIUM_THRESHOLD,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_UNKNOWN,
)

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """
    Deterministic, stateless Risk Assessment module.

    Classifies machine risk into LOW / MEDIUM / HIGH based solely on
    failure probability as the primary signal.

    Design principles:
    - Anomaly status is an independent signal; it does NOT alter the risk level.
    - All thresholds are defined in models.risk_config — no magic numbers here.
    - No model retraining, no LLM, no external calls.
    - Safe handling for invalid or out-of-range failure_probability values.

    Risk classification rules (thresholds from risk_config):
        [0.0, 0.30)  → LOW
        [0.30, 0.70) → MEDIUM
        [0.70, 1.0]  → HIGH

    Disclaimer:
        Risk levels reflect statistical model output and do NOT constitute
        a guaranteed physical diagnosis or authorise automated machine control.
    """

    def assess(self, failure_probability: Optional[float]) -> str:
        """
        Classify risk level from failure probability.

        Args:
            failure_probability: Model-predicted failure probability in [0.0, 1.0].
                                 None or NaN is treated as UNKNOWN.

        Returns:
            One of: "LOW", "MEDIUM", "HIGH", "UNKNOWN".
        """
        if failure_probability is None:
            logger.warning("failure_probability is None; returning UNKNOWN risk level.")
            return RISK_LEVEL_UNKNOWN

        try:
            prob = float(failure_probability)
        except (TypeError, ValueError) as exc:
            logger.warning(
                "Cannot convert failure_probability=%r to float: %s; returning UNKNOWN.",
                failure_probability,
                exc,
            )
            return RISK_LEVEL_UNKNOWN

        if math.isnan(prob) or math.isinf(prob):
            logger.warning(
                "failure_probability is non-finite (%r); returning UNKNOWN.", prob
            )
            return RISK_LEVEL_UNKNOWN

        if not (0.0 <= prob <= 1.0):
            logger.warning(
                "failure_probability=%f is outside [0, 1]; clamping before classification.",
                prob,
            )
            prob = max(0.0, min(1.0, prob))

        if prob >= RISK_HIGH_THRESHOLD:
            return RISK_LEVEL_HIGH
        if prob >= RISK_MEDIUM_THRESHOLD:
            return RISK_LEVEL_MEDIUM
        return RISK_LEVEL_LOW


_risk_service_instance: Optional[RiskAssessmentService] = None


def get_risk_service() -> RiskAssessmentService:
    """Cached singleton getter for RiskAssessmentService."""
    global _risk_service_instance
    if _risk_service_instance is None:
        _risk_service_instance = RiskAssessmentService()
    return _risk_service_instance
