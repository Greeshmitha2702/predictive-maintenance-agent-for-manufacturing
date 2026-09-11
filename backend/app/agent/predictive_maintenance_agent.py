from typing import Dict, Any, Optional

from schemas.prediction import PredictionRequest, PredictionResponse
from services.failure_service import FailurePredictionService, get_failure_service
from services.anomaly_service import AnomalyDetectionService, get_anomaly_service


class PredictiveMaintenanceAgent:
    """
    Deterministic Orchestrator Layer for Predictive Maintenance analysis.
    
    Coordinates:
    1. Anomaly Detection (Isolation Forest)
    2. Failure Prediction (Classifier model)
    3. SHAP Feature Attribution (Stubbed for BE-4)
    4. Risk Assessment (Stubbed for BE-5)
    5. Preventive Maintenance Recommendations (Stubbed for BE-5)
    
    Ensures Anomaly Detection and Failure Prediction remain independent signals.
    """

    _instance: Optional["PredictiveMaintenanceAgent"] = None

    def __init__(
        self,
        failure_service: Optional[FailurePredictionService] = None,
        anomaly_service: Optional[AnomalyDetectionService] = None,
    ):
        self.failure_service = failure_service or get_failure_service()
        self.anomaly_service = anomaly_service or get_anomaly_service()

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

        # Step 3: Run SHAP Feature Attribution (Placeholder for BE-4)
        _ = self._run_shap_explanation(input_data)

        # Step 4: Run Risk Assessment (Placeholder for BE-5)
        _ = self._assess_risk_level(failure_prob)

        # Step 5: Run Recommendation Engine (Placeholder for BE-5)
        _ = self._generate_recommendations(input_data, failure_prob, is_anomaly)

        # Step 6: Construct consolidated response keeping anomaly and failure separate
        return PredictionResponse(
            failure_probability=failure_prob,
            failure_predicted=failure_pred,
            is_anomaly=is_anomaly,
            anomaly_score=anomaly_score,
            model_version=model_ver,
        )

    def _run_shap_explanation(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Placeholder for BE-4 SHAP Explainability Service integration."""
        return None

    def _assess_risk_level(self, failure_probability: float) -> str:
        """Placeholder for BE-5 Risk Assessment logic."""
        if failure_probability >= 0.70:
            return "HIGH"
        elif failure_probability >= 0.30:
            return "MEDIUM"
        return "LOW"

    def _generate_recommendations(
        self,
        input_data: Dict[str, Any],
        failure_probability: float,
        is_anomaly: bool,
    ) -> list:
        """Placeholder for BE-5 Recommendation Engine logic."""
        return []


def get_agent() -> PredictiveMaintenanceAgent:
    """Cached singleton getter for PredictiveMaintenanceAgent."""
    if PredictiveMaintenanceAgent._instance is None:
        PredictiveMaintenanceAgent._instance = PredictiveMaintenanceAgent()
    return PredictiveMaintenanceAgent._instance
