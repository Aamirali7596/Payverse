from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


class DocumentUploadResponse(BaseModel):
    document_id: int
    message: str
    status: str = "processing"


class DocumentResponse(BaseModel):
    id: int
    document_type: str
    jurisdiction: str
    file_path: str
    processed: bool
    ai_analysis: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


class TaxCalculationRequest(BaseModel):
    tax_year: str = "2024-25"
    jurisdiction: str = "uk"
    include_ca_advice: bool = True


class TaxBreakdown(BaseModel):
    employment_income: float = 0.0
    self_employment_income: float = 0.0
    dividend_income: float = 0.0
    savings_interest: float = 0.0
    property_income: float = 0.0
    other_income: float = 0.0
    total_income: float = 0.0


class TaxResult(BaseModel):
    tax_allowance: float = 12570.0
    taxable_income: float = 0.0
    tax_basic: float = 0.0
    tax_higher: float = 0.0
    tax_additional: float = 0.0
    income_tax: float = 0.0
    national_insurance: float = 0.0
    total_tax: float = 0.0
    effective_tax_rate: float = 0.0


class TaxCalculationResponse(BaseModel):
    id: int
    user_id: int
    tax_year: str
    jurisdiction: str
    income_breakdown: TaxBreakdown
    tax_result: TaxResult
    reliefs_applied: Dict[str, float] = {}
    calculation_method: str
    confidence_score: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class VATPeriod(BaseModel):
    period_key: str
    start: str
    end: str
    due: str
    status: str
    period_ended: bool


class VATSubmissionRequest(BaseModel):
    period_key: str
    vat_due_sales: float
    vat_due_acquisitions: float = 0.0
    total_vat_due: float
    vat_reclaimed: float
    net_vat_due: float
    total_sales: float
    total_purchases: float
    total_exports: float = 0.0
