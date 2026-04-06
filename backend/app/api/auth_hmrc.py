"""HMRC OAuth authentication endpoints."""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import Optional

from app.services.hmrc_service import HMRCService

router = APIRouter()
hmrc_service = HMRCService()


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int


@router.get("/hmrc/login")
async def hmrc_login():
    """Redirect user to HMRC authorization page."""
    auth_url = hmrc_service.get_authorization_url()
    if not auth_url:
        raise HTTPException(400, "HMRC client not configured. Set HMRC_CLIENT_ID.")
    return RedirectResponse(url=auth_url)


@router.get("/hmrc/callback")
async def hmrc_callback(code: str = Query(...), state: Optional[str] = Query(None)):
    """Exchange authorization code for tokens."""
    try:
        token_data = await hmrc_service.exchange_code(code)
        return {
            "status": "success",
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "expires_in": token_data.get("expires_in", 0),
            "message": "HMRC connection successful!",
        }
    except Exception as e:
        raise HTTPException(400, f"Failed to exchange code: {str(e)}")


@router.post("/hmrc/refresh")
async def hmrc_refresh(refresh_token: str):
    """Refresh an expired access token."""
    try:
        token_data = await hmrc_service.refresh_token(refresh_token)
        return TokenResponse(**token_data)
    except Exception as e:
        raise HTTPException(400, f"Failed to refresh token: {str(e)}")


@router.get("/hmrc/test-credentials")
async def hmrc_test_credentials():
    """Return test credentials for sandbox testing."""
    return {
        "sandbox_url": "https://test-api.service.hmrc.gov.uk",
        "test_user": {
            "email": "test@example.com",
            "password": "any_password_works_in_sandbox",
            "vat_number": "123456789",
        },
        "note": "These are HMRC sandbox test credentials. No real accounts needed.",
    }
