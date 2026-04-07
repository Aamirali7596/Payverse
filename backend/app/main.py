"""TaxionLab Tax MVP - FastAPI Application"""

import sys
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, check_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    print("Starting TaxionLab Tax MVP...")
    db_ok = await check_db_connection()
    if db_ok:
        await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENVIRONMENT}


# Register routers
from app.api.auth_hmrc import router as hmrc_router  # noqa: E402
from app.api.tax import router as tax_router  # noqa: E402
from app.api.ca import router as ca_router  # noqa: E402

app.include_router(hmrc_router, prefix="/api/auth")
app.include_router(tax_router, prefix="/api/tax")
app.include_router(ca_router, prefix="/api/ca")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
