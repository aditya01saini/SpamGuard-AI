"""
SpamGuard AI — FastAPI application entry point.

Loads the trained ML model once at startup, wires up CORS, routers, global
exception handling, and (optionally) serves the built React frontend.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.controllers import analysis_controller
from app.routes import analyze, history, meta
from app.utils.exceptions import AppError
from app.utils.logging import logger
from app.utils.response import fail

# Locate a built frontend (client/dist) if present, to serve the SPA.
CLIENT_DIST = Path(__file__).resolve().parents[2] / "client" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load ML model (once, at startup).
    try:
        analysis_controller.init_ml_service(settings.model_dir)
        logger.info("ML model loaded: %s", analysis_controller._ml.model_name)
    except Exception as exc:
        logger.error("Failed to load ML model: %s", exc)

    yield
    # (optional cleanup here)


app = FastAPI(
    title="SpamGuard AI",
    description="Intelligent Email Spam, Phishing & Threat Analyzer",
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------------------------------------------------- #
# CORS
# --------------------------------------------------------------------------- #
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://spam-guard-ai-seven.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------------------------------- #
# Routers
# --------------------------------------------------------------------------- #
app.include_router(analyze.router)
app.include_router(history.router)
app.include_router(meta.router)


# --------------------------------------------------------------------------- #
# Global exception handlers (never leak stack traces / secrets)
# --------------------------------------------------------------------------- #
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content=fail(exc.code, exc.message),
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=fail("validation_error", "Invalid request payload."),
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=fail("internal_error", "An unexpected error occurred."),
    )


# --------------------------------------------------------------------------- #
# Optional: serve the built React frontend (SPA)
# --------------------------------------------------------------------------- #
if CLIENT_DIST.exists():
    assets = CLIENT_DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=str(assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404,
                                content=fail("not_found", "Endpoint not found."))
        file = CLIENT_DIST / full_path
        if full_path and file.is_file():
            return FileResponse(file)
        return FileResponse(CLIENT_DIST / "index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.host, port=settings.port,
                reload=False)
