from fastapi import APIRouter, HTTPException, status

from schemas.prediction import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)


router = APIRouter(
    prefix="/api/v1",
    tags=["predictive-maintenance"],
)


API_VERSION = "0.1.0"


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
    BE-1 mock prediction.

    Real ML integration will be added in a later backend phase.
    """

    try:
        # --------------------------------------------------
        # MOCK LOGIC ONLY
        # --------------------------------------------------

        mock_probability = (
            (payload.tool_wear / 1000)
            + (payload.torque / 1000)
            + (0.05 if payload.type.value == "L" else 0.0)
        )

        mock_probability = min(
            0.99,
            max(0.01, mock_probability),
        )

        mock_prediction = mock_probability >= 0.5

        return PredictionResponse(
            failure_probability=round(
                mock_probability,
                4,
            ),
            failure_predicted=mock_prediction,
            is_anomaly=False,
            anomaly_score=0.0,
            model_version="mock-0.0.0",
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating prediction.",
        ) from exc