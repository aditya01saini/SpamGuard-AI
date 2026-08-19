"""
Service: email statistics.

Computes simple descriptive statistics about the analyzed email for display
in the UI (word count, sentence count, URL count, HTML presence, etc.).
"""

from __future__ import annotations

import re
from typing import Dict, List


def _count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def _count_chars(text: str) -> int:
    return len(text or "")


def _count_sentences(text: str) -> int:
    if not text:
        return 0
    return len(re.findall(r"[.!?]+(?:\s|$)", text)) or (1 if text.strip() else 0)


def compute_statistics(
    subject: str,
    body: str,
    html_body: str,
    urls: List[Dict],
    suspicious_keywords: List[Dict],
    threat_indicators: List[Dict],
    sender: str,
    has_attachments: bool,
) -> Dict:
    full_text = f"{subject or ''}\n{body or ''}"
    return {
        "word_count": _count_words(full_text),
        "character_count": _count_chars(full_text),
        "sentence_count": _count_sentences(body),
        "subject_length": _count_chars(subject or ""),
        "url_count": len(urls),
        "suspicious_url_count": sum(1 for u in urls if u.get("suspicious")),
        "suspicious_keyword_count": len(suspicious_keywords),
        "threat_indicator_count": len(threat_indicators),
        "has_html": bool(html_body and html_body.strip()),
        "has_attachments": bool(has_attachments),
        "has_sender": bool(sender and sender.strip()),
    }
