"""HMRC Sandbox API integration service."""

import httpx
from app.core.config import settings
from cryptography.fernet import Fernet


class HMRCService:
    """Wrapper for HMRC OAuth and VAT API calls."""

    def __init__(self):
        base = settings.HMRC_SANDBOX_URL.rstrip("/")
        self.auth_url = f"{base}/connect/authorise"
        self.token_url = f"{base}/oauth/token"
        self.vat_api = f"{base}/organisations/vat/read/v1"
        self.vat_submit = f"{base}/organisations/vat/write/v1"
        self.client_id = settings.HMRC_CLIENT_ID
        self.client_secret = settings.HMRC_CLIENT_SECRET
        self.redirect_uri = settings.HMRC_REDIRECT_URI
        self.scopes = settings.HMRC_SCOPES

    def get_authorization_url(self) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": self.scopes,
            "redirect_uri": self.redirect_uri,
        }
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{qs}"

    async def exchange_code(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            resp.raise_for_status()
            return resp.json()

    async def refresh_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                self.token_url,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_vat_periods(self, access_token: str) -> list:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.vat_api}/periods",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def submit_vat_return(self, access_token: str, vat_data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.vat_submit}/returns",
                json=vat_data,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json",
                },
            )
            resp.raise_for_status()
            return resp.json()

    def encrypt_token(self, token: str) -> str:
        key = settings.ENCRYPTION_KEY.encode().ljust(44, "=")[:44].encode()
        return Fernet(key).encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        key = settings.ENCRYPTION_KEY.encode().ljust(44, "=")[:44].encode()
        return Fernet(key).decrypt(encrypted_token.encode()).decode()
