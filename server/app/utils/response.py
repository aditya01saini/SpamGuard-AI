"""Shared utility: response envelope helpers.

Every API response follows a consistent shape:

    success -> {"success": true, "data": {...}}
    error   -> {"success": false, "error": {"code": ..., "message": ...}}
"""

from __future__ import annotations

from typing import Any


def ok(data: Any) -> dict:
    return {"success": True, "data": data}


def fail(code: str, message: str, *, status_code: int = 400) -> dict:
    return {
        "success": False,
        "error": {"code": code, "message": message},
    }
