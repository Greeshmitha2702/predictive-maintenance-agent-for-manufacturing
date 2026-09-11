from fastapi import APIRouter, HTTPException, status

from schemas.prediction import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)
from services.failure_service import get_failure_service
from services.anomaly_service import get_anomaly_service


router = APIRouter(
    prefix="/api/v1",
    tags=["predictive-maintenance"],
)


API_VERSION = "0.2.0"


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version=API_VERSION,
    )


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(payload: PredictionRequest) -> PredictionResponse:
    """
    BE-2 ML Integration:
    Runs validated machine operating parameters through FailurePredictionService
    and AnomalyDetectionService loaded from real ML model artifacts.
    """
    try:
        # Extract validated request dictionary
        input_data = {
            "type": payload.type.value if hasattr(payload.type, "value") else str(payload.type),
            "air_temperature": float(payload.air_temperature),
            "process_temperature": float(payload.process_temperature),
            "rotational_speed": float(payload.rotational_speed),
            "torque": float(payload.torque),
            "tool_wear": float(payload.tool_wear),
        }

        # 1. Failure Prediction
        failure_service = get_failure_service()
        prob, failure_pred, model_ver = failure_service.predict(input_data)

        # 2. Anomaly Detection
        anomaly_service = get_anomaly_service()
        score, is_anom = anomaly_service.detect_anomaly(input_data)

        return PredictionResponse(
            failure_probability=prob,
            failure_predicted=failure_pred,
            is_anomaly=is_anom,
            anomaly_score=score,
            model_version=model_ver,
        )

    except RuntimeError as rerr:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(rerr),
        ) from rerr
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal error during ML prediction: {str(exc)}",
        ) from exc