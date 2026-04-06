from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "PayVerse Tax MVP"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite+aiosqlite:///./payverse_tax_mvp.db"

    HMRC_CLIENT_ID: str = ""
    HMRC_CLIENT_SECRET: str = ""
    HMRC_SANDBOX_URL: str = "https://test-api.service.hmrc.gov.uk"
    HMRC_REDIRECT_URI: str = "http://localhost:8000/auth/hmrc/callback"
    HMRC_SCOPES: str = "read:vat write:vat read:self-assessment write:self-assessment"

    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_MODEL_CA: str = "llama3:8b"
    DEFAULT_MODEL_EXTRACTION: str = "codellama:7b"

    ENCRYPTION_KEY: str = ""

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
