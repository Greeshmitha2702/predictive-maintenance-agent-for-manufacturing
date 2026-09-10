from enum import Enum

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
                "tool_wear": 0,
            }
        }
    )

    type: MachineType = Field(
        ...,
        description="Machine type: L, M, or H",
    )

    air_temperature: float = Field(
        ...,
        gt=0,
        le=400,
        description="Air temperature in Kelvin",
    )

    process_temperature: float = Field(
        ...,
        gt=0,
        le=400,
        description="Process temperature in Kelvin",
    )

    rotational_speed: float = Field(
        ...,
        gt=0,
        le=10000,
        description="Rotational speed in rpm",
    )

    torque: float = Field(
        ...,
        ge=0,
        le=500,
        description="Torque in Nm",
    )

    tool_wear: float = Field(
        ...,
        ge=0,
        le=1000,
        description="Tool wear in minutes",
    )


class PredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "failure_probability": 0.12,
                "failure_predicted": False,
                "is_anomaly": False,
                "anomaly_score": 0.0,
                "model_version": "mock-0.0.0",
            }
        }
    )

    failure_probability: float = Field(
        ...,
        ge=0,
        le=1,
        description="Mock predicted probability of machine failure",
    )

    failure_predicted: bool = Field(
        ...,
        description="Mock thresholded failure prediction",
    )

    is_anomaly: bool = Field(
        ...,
        description="Placeholder anomaly flag for BE-1",
    )

    anomaly_score: float = Field(
        ...,
        description="Placeholder anomaly score for BE-1",
    )

    model_version: str = Field(
        ...,
        description="Identifier of the prediction implementation",
    )


class HealthResponse(BaseModel):
    status: str
    version: str