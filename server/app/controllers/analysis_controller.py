"""
Controller: orchestrates a full email security analysis.

Pipeline:
    email -> parse -> ML classification -> phishing rules -> URL analysis
          -> keyword detection -> risk scoring -> Mistral AI -> persist.

The ML model is the primary classifier; Mistral is an explanation layer.
"""

from __future__ import annotations

from typing import Dict

from app.services import (
    ai_service,
    keyword_service,
    ml_service,
    phishing_service,
    risk_service,
    statistics_service,
    storage,
    url_service,
)
from app.utils.exceptions import EmptyEmailError, ModelNotAvailableError
from app.utils.helpers import new_id, utcnow_iso

# Singleton service instances (the ML service is bound at startup).
_ml = None
_ai = ai_service.AIService()


def init_ml_service(models_dir: str) -> None:
    """Bind the ML service (called from app startup after loading model)."""
    global _ml
    _ml = ml_service.MLService(models_dir)
    _ml.load()


# Indicator names that represent credential / financial-data harvesting — the
# strongest phishing signals. An email must exhibit these (or a high phishing
# probability) to be escalated from SPAM to POSSIBLE PHISHING.
_CREDENTIAL_INDICATORS = {
    "Password / credential request",
    "Sensitive information request",
    "Fake verification request",
    "Account suspension threat",
}


def _classify(ml_result: Dict, phishing_prob: float, phishing_indicators,
              urls) -> tuple:
    """Decide SAFE / SPAM / POSSIBLE PHISHING with an explainable rule.

    - ML label SPAM + credential-harvesting or strong phishing signals -> POSSIBLE PHISHING
    - ML label SPAM (otherwise)                                        -> SPAM
    - ML label SAFE + strong phishing/URL signals                      -> POSSIBLE PHISHING
    - otherwise                                                        -> SAFE
    """
    suspicious_urls = sum(1 for u in urls if u.get("suspicious"))
    harvesting = any(
        i.get("indicator") in _CREDENTIAL_INDICATORS
        for i in phishing_indicators
    )

    if ml_result["is_spam"]:
        if phishing_prob >= 0.5 or harvesting:
            return "POSSIBLE PHISHING", (
                "ML classified the email as spam and phishing indicators "
                "(credential or sensitive-information requests) are present."
            )
        return "SPAM", "ML classifier identified spam patterns in the email."

    # ML said SAFE, but strong phishing signals may warrant a re-flag.
    if phishing_prob >= 0.5 or (harvesting and suspicious_urls >= 1):
        return "POSSIBLE PHISHING", (
            "ML probability was low but strong phishing indicators were detected."
        )
    return "SAFE", "No significant spam or phishing signals were detected."


async def analyze_email(parsed: Dict, *, persist: bool = True) -> Dict:
    """Run the full analysis on a parsed email dict."""
    subject = (parsed.get("subject") or "").strip()
    body = (parsed.get("body") or "").strip()
    sender = (parsed.get("sender") or "").strip()
    html_body = parsed.get("html_body") or ""
    raw_urls = parsed.get("urls") or url_service.extract_urls(f"{html_body}\n{body}")

    if not body and not subject:
        raise EmptyEmailError("The email is empty. Please provide a subject or body.")

    if _ml is None or not _ml.is_loaded:
        raise ModelNotAvailableError("ML model is not available.")

    # 1. ML classification (primary).
    ml_result = _ml.predict(subject, body)

    # 2. Rule-based phishing detection.
    phishing_indicators = phishing_service.detect_phishing_indicators(
        subject, body, sender)
    phishing_prob = phishing_service.phishing_probability(phishing_indicators)

    # 3. URL analysis.
    urls = url_service.analyze_urls(raw_urls)

    # 4. Suspicious keywords.
    keywords = keyword_service.detect_suspicious_keywords(f"{subject}\n{subject}\n{body}")

    # 5. Risk scoring.
    risk = risk_service.compute_risk_score(
        ml_result["spam_probability"], phishing_indicators, urls, keywords)

    # 6. Email statistics.
    stats = statistics_service.compute_statistics(
        subject, body, html_body, urls, keywords, phishing_indicators, sender,
        parsed.get("has_attachments", False))

    # 7. Classification decision.
    classification, classification_reason = _classify(
        ml_result, phishing_prob, phishing_indicators, urls)

    # 8. Mistral AI explanation (graceful degradation).
    ai = await _ai.analyze(subject, body, sender, ml_result)

    # Confidence = probability of the predicted class.
    if classification == "SAFE":
        confidence = ml_result["safe_probability"]
    else:
        confidence = ml_result["spam_probability"]

    recommendation = ai.get("recommendation") if ai.get("available") \
        else _default_recommendation(classification)

    result = {
        "_id": new_id(),
        "classification": classification,
        "classification_reason": classification_reason,
        "confidence": confidence,
        "spam_probability": ml_result["spam_probability"],
        "safe_probability": ml_result["safe_probability"],
        "phishing_probability": phishing_prob,
        "risk_score": risk["score"],
        "risk_level": risk["level"],
        "risk_breakdown": risk["breakdown"],
        "suspicious_keywords": keyword_service.suspicious_keyword_names(keywords),
        "threat_indicators": phishing_indicators,
        "urls": urls,
        "statistics": stats,
        "ai_analysis": ai,
        "recommendation": recommendation,
        "model_name": ml_result["model"],
        "email_info": {
            "subject": subject,
            "sender": sender,
            "to": parsed.get("to") or "",
            "reply_to": parsed.get("reply_to") or "",
            "date": parsed.get("date") or "",
        },
        "timestamp": utcnow_iso(),
    }

    if persist:
        storage.storage.insert_scan(result)

    return result


def _default_recommendation(classification: str) -> str:
    if classification == "SAFE":
        return "This email appears safe. No action required, but stay alert for unusual requests."
    if classification == "SPAM":
        return "This appears to be spam. Do not reply or click any links; delete or mark as spam."
    return (
        "Possible phishing detected. Do not click any links or provide personal "
        "or financial information. Verify the sender through a trusted channel."
    )
