from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.schemas.tax import (
    DocumentUploadResponse,
    DocumentResponse,
    TaxCalculationRequest,
    TaxCalculationResponse,
)
from app.schemas.ca import CAAdviceRequest, CAAdviceResponse

__all__ = [
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "DocumentUploadResponse",
    "DocumentResponse",
    "TaxCalculationRequest",
    "TaxCalculationResponse",
    "CAAdviceRequest",
    "CAAdviceResponse",
]
