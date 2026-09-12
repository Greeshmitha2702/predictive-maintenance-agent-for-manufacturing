from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MachineType(str, Enum):
    """Machine type from the dataset."""

    L = "L"
    M = "M"
    H = "H"


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "M",
                "air_temperature": 298.1,
                "process_temperature": 308.6,
                "rotational_speed": 1551,
                "torque": 42.8,
                "tool_wear": 120,
            }
        }
    )

    type: MachineType = Field(..., description="Machine type: L, M, or H")
    air_temperature: float = Field(..., gt=0, le=400, description="Air temperature in Kelvin")
    process_temperature: float = Field(..., gt=0, le=400, description="Process temperature in Kelvin")
    rotational_speed: float = Field(..., gt=0, le=10000, description="Rotational speed in rpm")
    torque: float = Field(..., ge=0, le=500, description="Torque in Nm")
    tool_wear: float = Field(..., ge=0, le=1000, description="Tool wear in minutes")


class FeatureContribution(BaseModel):
    feature: str = Field(
        ...,
        description="Name of the parameter or engineered domain feature",
    )
    contribution: float = Field(
        ...,
        description="Signed SHAP contribution value for this prediction.",
    )
    direction: str = Field(
        ...,
        description="Impact direction: 'increases_failure_risk' or 'decreases_failure_risk'",
    )


class ExplanationResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "top_factors": [
                    {
                        "feature": "tool_wear",
                        "contribution": 0.24,
                        "direction": "increases_failure_risk",
                    },
                    {
                        "feature": "torque",
                        "contribution": 0.18,
                        "direction": "increases_failure_risk",
                    },
                ],
                "disclaimer": "SHAP feature attributions describe statistical model risk contributions/potential contributing factors, not guaranteed physical root causes.",
            }
        }
    )

    top_factors: List[FeatureContribution] = Field(
        default_factory=list,
        description="Top contributing features sorted by SHAP contribution magnitude",
    )
    disclaimer: str = Field(
        default="SHAP feature attributions describe statistical model risk contributions/potential contributing factors, not guaranteed physical root causes.",
        description="Standard engineering disclaimer for XAI interpretability",
    )


class PredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "failure_probability": 0.12,
                "failure_predicted": False,
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "risk_level": "LOW",
                "model_version": "Random Forest (Threshold: 0.4900)",
                "explanation": {
                    "top_factors": [
                        {
                            "feature": "tool_wear",
                            "contribution": 0.24,
                            "direction": "increases_failure_risk",
                        }
                    ],
                    "disclaimer": "SHAP feature attributions describe statistical model risk contributions/potential contributing factors, not guaranteed physical root causes.",
                },
            }
        }
    )

    failure_probability: float = Field(..., ge=0, le=1, description="Predicted probability of machine failure")
    failure_predicted: bool = Field(..., description="Thresholded binary failure prediction")
    is_anomaly: bool = Field(..., description="Boolean anomaly detection status")
    anomaly_score: float = Field(..., description="Isolation Forest decision score")
    risk_level: str = Field(..., description="Risk classification: LOW, MEDIUM, HIGH, or UNKNOWN")
    model_version: str = Field(..., description="Identifier of the prediction model implementation")
    explanation: Optional[ExplanationResponse] = Field(default=None, description="SHAP explainability results")


class HealthResponse(BaseModel):
    status: str
    version: str