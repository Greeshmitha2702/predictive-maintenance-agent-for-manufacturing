from pydantic import BaseModel, Field
from typing import List, Literal

class RecommendationItem(BaseModel):
    id: str = Field(..., description="Unique code for the recommendation rule")
    category: Literal["TOOLING", "THERMAL", "MECHANICAL", "ELECTRICAL", "INSPECTION"]
    severity: Literal["CRITICAL", "WARNING", "INFO"]
    title: str = Field(..., description="Short scannable title")
    action: str = Field(..., description="Prescriptive action for the technician")

class RecommendationResponse(BaseModel):
    risk_level: Literal["CRITICAL", "WARNING", "ANOMALOUS", "HEALTHY"]
    urgency: str = Field(..., description="Timeframe for maintenance execution")
    root_cause_indicators: List[str] = Field(default_factory=list)
    recommendations: List[RecommendationItem] = Field(default_factory=list)
