from typing import Dict, Any, Optional

from app.schemas.prediction import PredictionRequest, PredictionResponse, ExplanationResponse
from app.services.failure_service import FailurePredictionService, get_failure_service
from app.services.anomaly_service import AnomalyDetectionService, get_anomaly_service
from app.services.shap_service import ShapExplainabilityService, get_shap_service
from app.services.risk_service import RiskAssessmentService, get_risk_service


class PredictiveMaintenanceAgent:
    """
    Deterministic Orchestrator Layer for Predictive Maintenance analysis.
    
    Coordinates:
    1. Anomaly Detection (Isolation Forest)
    2. Failure Prediction (Classifier model)
    3. SHAP Feature Attribution (BE-4)
    4. Risk Assessment (BE-5 — RiskAssessmentService)
    5. Preventive Maintenance Recommendations (Stubbed for BE-6)
    
    Ensures Anomaly Detection and Failure Prediction remain independent signals.
    Risk level is derived solely from failure probability; anomaly status is preserved
    as a separate independent field.
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
        Orchestrates full machine maintenance analysis workflow.
        """
        # Convert Pydantic request to exact dictionary input
        input_data: Dict[str, Any] = {
            "type": payload.type.value if hasattr(payload.type, "value") else str(payload.type),
            "air_temperature": float(payload.air_temperature),
            "process_temperature": float(payload.process_temperature),
            "rotational_speed": float(payload.rotational_speed),
            "torque": float(payload.torque),
            "tool_wear": float(payload.tool_wear),
        }

        # Step 1: Run Anomaly Detection (Independent Signal)
        anomaly_score, is_anomaly = self.anomaly_service.detect_anomaly(input_data)

        # Step 2: Run Failure Prediction (Independent Signal)
        failure_prob, failure_pred, model_ver = self.failure_service.predict(input_data)

        # Step 3: Run SHAP Feature Attribution Explainability
        explanation = self._run_shap_explanation(input_data)

        # Step 4: Classify risk level using failure probability (independent of anomaly status)
        risk_level = self._assess_risk_level(failure_prob)

        # Step 5: Run Recommendation Engine (Placeholder for BE-6)
        _ = self._generate_recommendations(input_data, failure_prob, is_anomaly)

        # Step 6: Construct consolidated response keeping anomaly and failure separate
        return PredictionResponse(
            failure_probability=failure_prob,
            failure_predicted=failure_pred,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            risk_level=risk_level,
            model_version=model_ver,
            explanation=explanation,
        )

    def _run_shap_explanation(self, input_data: Dict[str, Any]) -> ExplanationResponse:
        """Invokes SHAP Explainability Service for failure feature contributions."""
        return self.shap_service.explain(input_data)

    def _assess_risk_level(self, failure_probability: float) -> str:
        """Delegates risk classification to RiskAssessmentService (BE-5)."""
        return self.risk_service.assess(failure_probability)

    def _generate_recommendations(
        self,
        input_data: Dict[str, Any],
        failure_probability: float,
        is_anomaly: bool,
    ) -> list:
        """Placeholder for BE-6 Recommendation Engine logic."""
        return []


def get_agent() -> PredictiveMaintenanceAgent:
    """Cached singleton getter for PredictiveMaintenanceAgent."""
    if PredictiveMaintenanceAgent._instance is None:
        PredictiveMaintenanceAgent._instance = PredictiveMaintenanceAgent()
    return PredictiveMaintenanceAgent._instance
