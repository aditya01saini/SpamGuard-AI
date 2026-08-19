"""
Service: suspicious keyword detection.

Maintains a configurable list of high-signal keywords/phrases commonly found
in spam and phishing emails. These are *supporting* indicators only — the
primary classification is the ML model.
"""

from __future__ import annotations

import re
from typing import Dict, List

# Each entry: (keyword, weight) where weight reflects how strongly the term
# indicates spam/phishing. Used for both the keyword list and scoring.
SUSPICIOUS_KEYWORDS: Dict[str, int] = {
    # Financial / sensitive-information bait
    "prize": 3, "winner": 3, "won": 2, "lottery": 3, "claim": 2, "reward": 2,
    "free": 1, "bonus": 1, "cash": 2, "money": 1, "million": 2, "billion": 2,
    "inherit": 2, "inheritance": 2, "compensation": 2, "refund": 2,
    "unclaimed": 2, "jackpot": 3,
    # Urgency / pressure
    "urgent": 3, "immediately": 3, "act now": 3, "asap": 2, "hurry": 2,
    "expires": 2, "expire": 2, "deadline": 2, "last chance": 2, "now": 1,
    "24 hours": 2, "within 24": 2,
    # Credential / account threats
    "password": 3, "passcode": 3, "credential": 3, "login": 2, "log in": 2,
    "sign in": 2, "verify": 3, "verification": 3, "confirm": 2, "confirm your": 3,
    "account": 2, "suspended": 3, "suspend": 3, "deactivate": 3, "terminated": 3,
    "unusual activity": 3, "security alert": 3, "locked": 3, "blocked": 3,
    "reset": 2, "recover": 2, "reactivate": 2,
    # Banking / payments
    "bank": 2, "banking": 2, "wire": 2, "transfer": 2, "payment": 2,
    "paypal": 2, "credit card": 3, "card number": 3, "billing": 2, "invoice": 1,
    "overdue": 2, "balance": 1, "transaction": 2, "otp": 3, "pin": 2,
    "ssn": 3, "social security": 3, "tax": 2, "irs": 3, "cvv": 3,
    # Social engineering / impersonation
    "dear customer": 2, "dear user": 2, "valued customer": 2, "important notice": 2,
    "click here": 3, "click the link": 3, "open the link": 3, "link below": 2,
    "download": 1, "update your": 3, "update your information": 3,
    "your information": 2, "personal information": 2, "confidential": 2,
    "cease": 2, "legal action": 2, "lawsuit": 2, "warrant": 3, "fbi": 3,
    # Scam themes
    "job offer": 2, "work from home": 2, "earn": 2, "investment": 2, "investor": 2,
    "crypto": 2, "bitcoin": 2, "gift card": 3, "voucher": 2, "coupon": 1,
    "tracking": 1, "delivery": 1, "parcel": 1, "shipment": 1, "customs": 2,
    "fee": 2, "unlock": 2, "subscription": 2, "renewal": 2,
}


def detect_suspicious_keywords(text: str) -> List[Dict]:
    """Return the list of suspicious keywords found in the text (lowercased),
    each with its assigned weight and the number of occurrences."""
    lower = text.lower()
    found: Dict[str, Dict] = {}

    for keyword, weight in SUSPICIOUS_KEYWORDS.items():
        # Use word-boundary matching for multi-word phrases too.
        pattern = r"(?<![a-z])" + re.escape(keyword) + r"(?![a-z])"
        count = len(re.findall(pattern, lower))
        if count > 0:
            found[keyword] = {"keyword": keyword, "count": count, "weight": weight}

    # Sort by weight desc, then count desc, then alphabetical.
    result = sorted(
        found.values(),
        key=lambda x: (-x["weight"], -x["count"], x["keyword"]),
    )
    return result


def suspicious_keyword_names(keywords: List[Dict]) -> List[str]:
    return [k["keyword"] for k in keywords]
