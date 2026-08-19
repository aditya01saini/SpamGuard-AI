"""
Service: transparent risk scoring.

Combines the ML spam probability, phishing indicators, suspicious URLs, and
suspicious keywords into a single 0-100 risk score. The exact contribution of
each component is returned so the score is fully explainable.

Bands:
    0-25   LOW
    26-50  MEDIUM
    51-75  HIGH
    76-100 CRITICAL
"""

from __future__ import annotations

from typing import Dict, List

BANDS = [
    (76, "CRITICAL"),
    (51, "HIGH"),
    (26, "MEDIUM"),
    (0, "LOW"),
]

SEVERITY_WEIGHT = {"HIGH": 4, "MEDIUM": 2, "LOW": 1}


def risk_level(score: float) -> str:
    for threshold, label in BANDS:
        if score >= threshold:
            return label
    return "LOW"


def _phishing_points(indicators: List[Dict]) -> float:
    points = 0.0
    for i in indicators:
        points += SEVERITY_WEIGHT.get(i.get("severity"), 1) * 2.5
    return min(25.0, points)


def _url_points(urls: List[Dict]) -> float:
    points = 0.0
    for u in urls:
        sev = u.get("severity", "NONE")
        points += SEVERITY_WEIGHT.get(sev, 0) * 2.5
        if u.get("is_https") is False:
            points += 1.0
    return min(15.0, points)


def _keyword_points(keywords: List[Dict]) -> float:
    points = sum(k.get("weight", 1) * 0.6 for k in keywords)
    return min(10.0, points)


def compute_risk_score(
    spam_probability: float,
    phishing_indicators: List[Dict],
    urls: List[Dict],
    suspicious_keywords: List[Dict],
) -> Dict:
    """Return a dict with the final score, level, and a breakdown."""
    # Base contribution from the ML model (up to 50 points).
    ml_points = round(spam_probability * 50.0, 2)

    ph_points = round(_phishing_points(phishing_indicators), 2)
    url_points = round(_url_points(urls), 2)
    kw_points = round(_keyword_points(suspicious_keywords), 2)

    total = round(min(100.0, ml_points + ph_points + url_points + kw_points))
    level = risk_level(total)

    breakdown = [
        {"component": "ML spam probability", "points": ml_points,
         "detail": f"ML model scored {spam_probability:.0%} spam probability (×50)."},
        {"component": "Phishing indicators", "points": ph_points,
         "detail": f"{len(phishing_indicators)} threat indicator(s) detected."},
        {"component": "Suspicious URLs", "points": url_points,
         "detail": f"{sum(1 for u in urls if u.get('suspicious'))} suspicious URL(s) out of {len(urls)}."},
        {"component": "Suspicious keywords", "points": kw_points,
         "detail": f"{len(suspicious_keywords)} suspicious keyword(s) detected."},
    ]

    return {
        "score": total,
        "level": level,
        "max": 100,
        "breakdown": breakdown,
    }
