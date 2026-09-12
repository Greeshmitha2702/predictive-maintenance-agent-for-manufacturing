import logging
from fastapi import APIRouter, HTTPException, status

from app.agent.predictive_maintenance_agent import get_agent
from app.schemas.prediction import (
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1",
    tags=["predictive-maintenance"],
)


API_VERSION = "0.4.0"


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
    BE-4 SHAP Explainability Integration:
    Delegates analysis request to PredictiveMaintenanceAgent including SHAP feature attributions.
    """
    try:
        agent = get_agent()
        return agent.analyze_machine(payload)

    except RuntimeError as rerr:
        logger.error("Runtime error in /predict route: %s", rerr, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating prediction.",
        ) from rerr
    except Exception as exc:
        logger.error("Unexpected error in /predict route: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error while generating prediction.",
        ) from exc