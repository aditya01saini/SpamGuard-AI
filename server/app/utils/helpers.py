"""Shared utility: small generic helpers (ID generation, time)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def new_id() -> str:
    return uuid.uuid4().hex


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
