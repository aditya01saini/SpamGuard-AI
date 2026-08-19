"""Routes: /api/analytics and /api/model-info and /api/health."""

from __future__ import annotations

from fastapi import APIRouter

from app.controllers import analysis_controller
from app.services import storage
from app.utils.response import ok

router = APIRouter(prefix="/api", tags=["meta"])


@router.get("/analytics")
def analytics():
    """Dashboard analytics computed from stored scans (never hardcoded)."""
    data = storage.storage.analytics()

    # Historical trend (last 30 scans, ascending by time).
    recent = storage.storage.list_scans(30, 0, None)
    trend = [
        {
            "timestamp": s.get("timestamp"),
            "risk_score": s.get("risk_score"),
            "classification": s.get("classification"),
        }
        for s in reversed(recent)
    ]

    data["trend"] = trend
    return ok(data)


@router.get("/model-info")
def model_info():
    """Return ML model information and evaluation metrics."""
    if analysis_controller._ml is None or not analysis_controller._ml.is_loaded:
        return ok({"loaded": False, "message": "ML model not loaded."})

    metrics = analysis_controller._ml.metrics
    return ok({
        "loaded": True,
        "model_name": analysis_controller._ml.model_name,
        "metrics": metrics,
        "config": analysis_controller._ml.config,
    })


@router.get("/health")
def health():
    """Health check (includes component status)."""
    return ok({
        "status": "ok",
        "ml_loaded": analysis_controller._ml is not None
                     and analysis_controller._ml.is_loaded,
        "mistral_configured": bool(
            __import__("app.config", fromlist=["settings"]).settings.mistral_enabled
        ),
        "storage": type(storage.storage).__name__,
    })
