"""Pytest fixtures: test client with mocked Mistral + in-memory storage.

Real API calls to Mistral are NEVER made during tests — the AI service is
replaced with a stub. MongoDB is swapped for the in-memory fallback.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the server/ directory is on the path so `app` and `ml` are importable.
SERVER_DIR = Path(__file__).resolve().parents[1]
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

from app.controllers import analysis_controller  # noqa: E402
from app.services import storage  # noqa: E402


class FakeAIService:
    """Stub that mimics AIService without calling the Mistral API."""

    enabled = True

    async def analyze(self, subject, body, sender, ml_result):
        return {
            "available": True,
            "provider": "mock",
            "summary": "Mock summary.",
            "explanation": "Mock explanation.",
            "threat_analysis": "Mock threat analysis.",
            "recommendation": "Mock recommendation.",
        }


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    # Swap storage for a clean in-memory store per test.
    storage.storage = storage.InMemoryStorage()
    # Swap AI service for the stub.
    analysis_controller._ai = FakeAIService()

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sample_spam():
    return {
        "subject": "URGENT: Your account has been suspended",
        "sender": "security@securebank-alerts.com",
        "body": (
            "Dear customer, we have detected unusual activity and suspended "
            "your account. Click here to verify your password and credit card "
            "number immediately: http://83.102.44.9/verify"
        ),
    }


@pytest.fixture()
def sample_safe():
    return {
        "subject": "Team lunch on Friday",
        "sender": "alice@company.com",
        "body": (
            "Hi everyone, we are having a team lunch this Friday at noon. "
            "Please let me know if you can make it. Thanks!"
        ),
    }
