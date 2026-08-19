"""
Service: AI analysis (Mistral) with graceful degradation.

If the Mistral API is unavailable (no key, invalid key, network error, etc.)
the analysis is still returned, but with an `available: false` flag and a
human-readable notice. The ML classification and rule-based indicators are
NEVER blocked by a Mistral failure.
"""

from __future__ import annotations

from typing import Dict

from app.ai.mistral import MistralClient, MistralError
from app.utils.logging import logger


class AIService:
    def __init__(self):
        self.client = MistralClient()

    @property
    def enabled(self) -> bool:
        return self.client.enabled

    async def analyze(self, subject: str, body: str, sender: str,
                      ml_result: Dict) -> Dict:
        """Run the Mistral analysis; degrade gracefully on any failure."""
        if not self.enabled:
            return _unavailable("Mistral API key is not configured. AI explanation is unavailable.")

        try:
            result = await self.client.analyze_email(subject, body, sender, ml_result)
            result["available"] = True
            result["provider"] = "mistral"
            return result
        except MistralError as exc:
            logger.warning("Mistral analysis unavailable: %s", exc)
            return _unavailable(str(exc))
        except Exception as exc:  # never let AI failure break the request
            logger.exception("Unexpected Mistral error")
            return _unavailable("Unexpected AI error — AI explanation is temporarily unavailable.")


def _unavailable(reason: str) -> Dict:
    return {
        "available": False,
        "reason": reason,
        "summary": "",
        "explanation": "",
        "threat_analysis": "",
        "recommendation": _fallback_recommendation(),
        "provider": None,
    }


def _fallback_recommendation() -> str:
    return (
        "Treat this email with caution. Do not click links or provide personal "
        "or financial information until the sender's identity is independently verified."
    )
