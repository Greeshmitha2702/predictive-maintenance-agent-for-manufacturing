from typing import List, Literal

from pydantic import BaseModel, Field


class ShapContributor(BaseModel):
    """Signed SHAP contribution used by recommendation rules."""

    feature: str = Field(
        ...,
        description="Feature contributing to the prediction",
    )
    contribution: float = Field(
        ...,
        description="Signed SHAP contribution; positive values increase failure risk",
    )
    direction: Literal[
        "increases_failure_risk",
        "decreases_failure_risk",
    ] = Field(
        ...,
        description="Direction of the SHAP contribution",
    )


class RecommendationItem(BaseModel):
    """Preventive-maintenance recommendation for the technician."""

    id: str = Field(
        ...,
        description="Unique recommendation rule identifier",
    )
    category: Literal[
        "TOOLING",
        "THERMAL",
        "MECHANICAL",
        "ELECTRICAL",
        "INSPECTION",
    ]
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    title: str = Field(
        ...,
        description="Short recommendation title",
    )
    action: str = Field(
        ...,
        description="Preventive action for the technician",
    )


class RecommendationResponse(BaseModel):
    """Output produced by the deterministic recommendation engine."""

    risk_level: Literal["LOW", "MEDIUM", "HIGH"]
    urgency: str = Field(
        ...,
        description="Recommended maintenance timeframe",
    )
    root_cause_indicators: List[str] = Field(
        default_factory=list,
    )
    recommendations: List[RecommendationItem] = Field(
        default_factory=list,
    )
