"""Routes: /api/history (scan history CRUD)."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Response

from app.services import storage
from app.utils.exceptions import NotFoundError
from app.utils.response import ok

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("")
def list_history(
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
    classification: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    """List scans (with optional classification filter and subject search)."""
    items = storage.storage.list_scans(limit, skip, classification)

    if search:
        q = search.lower()
        items = [
            s for s in items
            if q in (s.get("email_info", {}).get("subject", "")).lower()
            or q in (s.get("email_info", {}).get("sender", "")).lower()
        ]

    # Trim heavy fields for list view.
    summary = [_list_item(s) for s in items]
    return ok({
        "scans": summary,
        "total": len(summary),
        "limit": limit,
        "skip": skip,
    })


@router.get("/{scan_id}")
def get_history(scan_id: str):
    scan = storage.storage.get_scan(scan_id)
    if not scan:
        raise NotFoundError("Scan not found.")
    return ok(scan)


@router.delete("/{scan_id}")
def delete_history(scan_id: str):
    if not storage.storage.delete_scan(scan_id):
        raise NotFoundError("Scan not found.")
    return ok({"deleted": True, "id": scan_id})


@router.get("/{scan_id}/report")
def download_report(scan_id: str):
    """Generate a downloadable PDF security report for a scan."""
    from app.services.pdf_service import generate_pdf_report

    scan = storage.storage.get_scan(scan_id)
    if not scan:
        raise NotFoundError("Scan not found.")

    pdf_bytes = generate_pdf_report(scan)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="spamguard-report-{scan_id[:8]}.pdf"'
        },
    )


def _list_item(scan: dict) -> dict:
    info = scan.get("email_info", {})
    return {
        "id": scan["_id"],
        "subject": info.get("subject", "")[:120],
        "sender": info.get("sender", ""),
        "classification": scan.get("classification"),
        "risk_score": scan.get("risk_score"),
        "risk_level": scan.get("risk_level"),
        "confidence": scan.get("confidence"),
        "timestamp": scan.get("timestamp"),
    }
