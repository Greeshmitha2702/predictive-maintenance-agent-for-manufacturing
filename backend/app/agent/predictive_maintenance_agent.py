import logging
from typing import Dict, Any, Optional

from app.schemas.prediction import PredictionRequest, PredictionResponse, ExplanationResponse
from app.schemas.recommendation import RecommendationResponse
from app.services.failure_service import FailurePredictionService, get_failure_service
from app.services.anomaly_service import AnomalyDetectionService, get_anomaly_service
from app.services.shap_service import ShapExplainabilityService, get_shap_service
from app.services.risk_service import RiskAssessmentService, get_risk_service
from app.services.recommendation_engine import generate_recommendations

logger = logging.getLogger(__name__)


class PredictiveMaintenanceAgent:
    """
    Deterministic Orchestrator Layer for Predictive Maintenance analysis.

    Coordinates:
    1. Anomaly Detection (Isolation Forest) — AnomalyDetectionService
    2. Failure Prediction (Classifier model) — FailurePredictionService
    3. SHAP Feature Attribution — ShapExplainabilityService
    4. Risk Assessment — RiskAssessmentService
    5. Preventive Maintenance Recommendations — RecommendationEngine

    Each service is responsible for exactly one concern.
    The agent orchestrates their outputs into a single response without
    duplicating any logic.

    Anomaly Detection and Failure Prediction remain independent signals:
    - risk_level is derived solely from failure_probability (RiskAssessmentService).
    - is_anomaly is an independent flag from AnomalyDetectionService.
    - The agent never equates anomaly with failure.
    """

    _instance: Optional["PredictiveMaintenanceAgent"] = None

    def __init__(
        self,
        failure_service: Optional[FailurePredictionService] = None,
        anomaly_service: Optional[AnomalyDetectionService] = None,
        shap_service: Optional[ShapExplainabilityService] = None,
        risk_service: Optional[RiskAssessmentService] = None,
    ):
        self.failure_service = failure_service or get_failure_service()
        self.anomaly_service = anomaly_service or get_anomaly_service()
        self.shap_service = shap_service or get_shap_service()
        self.risk_service = risk_service or get_risk_service()

    def analyze_machine(self, payload: PredictionRequest) -> PredictionResponse:
        """
        Orchestrates the full machine maintenance analysis workflow.

        Flow:
          validated request
          → AnomalyDetectionService   (independent signal)
          → FailurePredictionService  (independent signal)
          → ShapExplainabilityService (feature attribution)
          → RiskAssessmentService     (failure-probability → LOW/MEDIUM/HIGH)
          → RecommendationEngine      (deterministic preventive-maintenance recs)
          → PredictionResponse
        """
        # Convert Pydantic request to a plain dict shared across all services.
        input_data: Dict[str, Any] = {
            "type": payload.type.value if hasattr(payload.type, "value") else str(payload.type),
            "air_temperature": float(payload.air_temperature),
            "process_temperature": float(payload.process_temperature),
            "rotational_speed": float(payload.rotational_speed),
            "torque": float(payload.torque),
            "tool_wear": float(payload.tool_wear),
        }

        # Step 1 — Anomaly Detection (independent signal)
        anomaly_score, is_anomaly = self.anomaly_service.detect_anomaly(input_data)

        # Step 2 — Failure Prediction (independent signal)
        failure_prob, failure_pred, model_ver = self.failure_service.predict(input_data)

        # Step 3 — SHAP Feature Attribution
        explanation: Optional[ExplanationResponse] = self._run_shap_explanation(input_data)

        # Step 4 — Risk Assessment (failure_probability → LOW / MEDIUM / HIGH)
        risk_level: str = self._assess_risk_level(failure_prob)

        # Step 5 — Recommendation Engine
        recommendations: Optional[RecommendationResponse] = self._generate_recommendations(
            input_data=input_data,
            is_anomaly=is_anomaly,
            risk_level=risk_level,
            explanation=explanation,
        )

        # Step 6 — Assemble and return the consolidated response.
        # Anomaly and failure signals are kept as separate top-level fields.
        return PredictionResponse(
            failure_probability=failure_prob,
            failure_predicted=failure_pred,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            risk_level=risk_level,
            model_version=model_ver,
            explanation=explanation,
            recommendations=recommendations,
        )

    # ------------------------------------------------------------------
    # Private orchestration helpers — one concern each, no logic duplication
    # ------------------------------------------------------------------

    def _run_shap_explanation(self, input_data: Dict[str, Any]) -> Optional[ExplanationResponse]:
        """Delegates SHAP feature attribution to ShapExplainabilityService."""
        return self.shap_service.explain(input_data)

    def _assess_risk_level(self, failure_probability: float) -> str:
        """Delegates risk classification to RiskAssessmentService."""
        return self.risk_service.assess(failure_probability)

    def _generate_recommendations(
        self,
        input_data: Dict[str, Any],
        is_anomaly: bool,
        risk_level: str,
        explanation: Optional[ExplanationResponse],
    ) -> Optional[RecommendationResponse]:
        """
        Delegates preventive-maintenance recommendations to RecommendationEngine.

        Extracts SHAP contributors from the ExplanationResponse so the engine
        can apply SHAP-aware rules without duplicating attribution logic here.

        Returns None on any unexpected error; the error is logged server-side
        and the rest of the response is still returned intact.
        """
        # Extract SHAP top_factors from the existing ExplanationResponse.
        # The engine accepts any objects exposing .feature, .contribution, .direction.
        shap_contributors = []
        if explanation is not None and explanation.top_factors:
            shap_contributors = explanation.top_factors

        # machine_params for the engine: raw API fields only (no "type" — not required by engine)
        machine_params: Dict[str, Any] = {
            "air_temperature": input_data["air_temperature"],
            "process_temperature": input_data["process_temperature"],
            "rotational_speed": input_data["rotational_speed"],
            "torque": input_data["torque"],
            "tool_wear": input_data["tool_wear"],
        }

        # Guard: skip recommendation engine if risk_level is UNKNOWN (invalid state)
        if risk_level not in {"LOW", "MEDIUM", "HIGH"}:
            logger.warning(
                "RecommendationEngine skipped: unexpected risk_level=%r", risk_level
            )
            return None

        try:
            return generate_recommendations(
                risk_level=risk_level,
                is_anomaly=is_anomaly,
                shap_contributors=shap_contributors,
                machine_params=machine_params,
            )
        except Exception as exc:
            logger.error(
                "RecommendationEngine error (non-fatal): %s", exc, exc_info=True
            )
            return None


def get_agent() -> PredictiveMaintenanceAgent:
    """Cached singleton getter for PredictiveMaintenanceAgent."""
    if PredictiveMaintenanceAgent._instance is None:
        PredictiveMaintenanceAgent._instance = PredictiveMaintenanceAgent()
    return PredictiveMaintenanceAgent._instance

