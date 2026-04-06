from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class TaxRelief(BaseModel):
    name: str
    description: str
    potential_savings: float
    eligibility: List[str] = []
    evidence_required: List[str] = []
    hmrc_reference: str = ""
    priority: int = 1
    jurisdiction: str = "uk"


class CAAdviceRequest(BaseModel):
    user_id: Optional[int] = None
    financial_data: Dict[str, Any]
    jurisdiction: str = "uk"
    tax_calculation_id: Optional[int] = None


class CAAdviceResponse(BaseModel):
    id: int
    user_id: int
    jurisdiction: str
    total_current_tax: float
    total_optimized_tax: Optional[float]
    potential_savings: Optional[float]
    reliefs: List[TaxRelief]
    action_items: List[str] = []
    time_horizon: Optional[str]
    risk_level: Optional[str]
    confidence: Optional[float]
    full_analysis: str
    created_at: datetime

    class Config:
        from_attributes = True


class CAChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    jurisdiction: str = "uk"


class CAChatResponse(BaseModel):
    response: str
    session_id: str
