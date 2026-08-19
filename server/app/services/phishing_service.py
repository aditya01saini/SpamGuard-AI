"""
Service: rule-based phishing detection.

A transparent, deterministic layer that inspects the email for well-known
phishing / social-engineering patterns and returns structured threat
indicators. This complements (never replaces) the ML classifier.

Terminology is intentionally careful: we report "suspicious" / "potential" /
"high-risk indicator" rather than asserting malice, because these are
heuristics, not proof.
"""

from __future__ import annotations

import re
from typing import Dict, List

# --------------------------------------------------------------------------- #
# Pattern banks (each maps to an indicator definition)
# --------------------------------------------------------------------------- #

# (name, severity, description, compiled regex list)
_PATTERNS: List[tuple] = [
    (
        "Urgent language",
        "HIGH",
        "The email pressures the recipient to take immediate action.",
        [r"\burgent\b", r"\bimmediately\b", r"\bact now\b", r"\basap\b",
         r"\bexpires?\b", r"\blast chance\b", r"\bwithin 24 hours?\b",
         r"\bhurry\b", r"\btime[- ]sensitive\b"],
    ),
    (
        "Account suspension threat",
        "HIGH",
        "Threatens that an account will be suspended, locked or terminated.",
        [r"\baccount\b.{0,30}\b(suspend\w*|terminat\w*|lock\w*|deactivat\w*)",
         r"\b(suspend\w*|terminat\w*|lock\w*|deactivat\w*).{0,30}\baccount\b"],
    ),
    (
        "Password / credential request",
        "HIGH",
        "Asks the recipient to enter or confirm passwords or credentials.",
        [r"\bpassword\b", r"\bpasscode\b", r"\bcredentials?\b", r"\bpin\b",
         r"\blog ?in\b", r"\bsign ?in\b", r"\bssn\b", r"\bcvv\b"],
    ),
    (
        "Sensitive information request",
        "HIGH",
        "Requests sensitive personal or financial information.",
        [r"\bcredit card\b", r"\bcard number\b", r"\bbank account\b",
         r"\bsocial security\b", r"\bdate of birth\b", r"\bmother's maiden\b",
         r"\bpersonal information\b", r"\baccount number\b"],
    ),
    (
        "Banking / payment request",
        "MEDIUM",
        "References banking or payment activity.",
        [r"\bbank\b", r"\bwire transfer\b", r"\bpayment\b", r"\bbilling\b",
         r"\bpaypal\b", r"\binvoice\b", r"\brefund\b", r"\btransaction\b"],
    ),
    (
        "Fake verification request",
        "HIGH",
        "Asks the user to verify an account or click a verification link.",
        [r"\bverify\b", r"\bverification\b", r"\bconfirm your\b",
         r"\bverify your\b", r"\bupdate your\b", r"\bre-activat\w*"],
    ),
    (
        "Prize / reward scam",
        "MEDIUM",
        "Offers a prize, lottery win, or unexpected reward.",
        [r"\bprize\b", r"\bwinner\b", r"\blottery\b", r"\byou have won\b",
         r"\bcongratulations!?\b", r"\bjackpot\b", r"\bclaim your\b"],
    ),
    (
        "Unusual activity claim",
        "MEDIUM",
        "Claims suspicious or unusual activity on the recipient's account.",
        [r"\bunusual activity\b", r"\bsuspicious activity\b",
         r"\bsecurity alert\b", r"\bnew sign[- ]in\b"],
    ),
    (
        "Link clicking pressure",
        "MEDIUM",
        "Pressures the recipient to click a link or open an attachment.",
        [r"\bclick (here|the link|this link)\b", r"\bopen the link\b",
         r"\bfollow the link\b", r"\bclick below\b", r"\bclick this\b"],
    ),
    (
        "Threat / legal pressure",
        "HIGH",
        "Uses threats of legal action or authority to coerce action.",
        [r"\blegal action\b", r"\blawsuit\b", r"\bwarrant\b", r"\bfbi\b",
         r"\barrest\b", r"\bprosecut\w*", r"\bpolice\b"],
    ),
    (
        "Generic greeting",
        "LOW",
        "Uses a generic greeting instead of the recipient's name.",
        [r"\bdear (customer|user|member|account holder|sir\/madam|friend)\b",
         r"\bvalued customer\b", r"\bhello (customer|user)\b"],
    ),
    (
        "Gift card / crypto request",
        "MEDIUM",
        "Requests payment via gift cards or cryptocurrency (untraceable).",
        [r"\bgift card\b", r"\bitunes\b", r"\bgoogle play card\b",
         r"\bbitcoin\b", r"\bcrypto(currency)?\b", r"\bbtc\b"],
    ),
    (
        "Job / money-mule scam",
        "MEDIUM",
        "Offers easy money, remote work, or requests to process funds.",
        [r"\bwork from home\b", r"\bjob offer\b", r"\bearn \$\b",
         r"\bper week\b.{0,30}\bfrom home\b", r"\bwire funds\b"],
    ),
    (
        "Delivery / customs fee scam",
        "MEDIUM",
        "Claims a package requires a fee or customs payment.",
        [r"\bparcel\b", r"\bshipment\b", r"\bcustoms\b", r"\bdelivery fee\b",
         r"\bpackage\b.{0,30}\bhold\b", r"\btracking\b.{0,30}\bupdate\b"],
    ),
]


def _compile() -> List[tuple]:
    compiled = []
    for name, severity, desc, patterns in _PATTERNS:
        compiled.append((name, severity, desc, [re.compile(p, re.IGNORECASE) for p in patterns]))
    return compiled


_COMPILED = _compile()


def detect_phishing_indicators(subject: str, body: str, sender: str = "") -> List[Dict]:
    """Return a list of threat indicators found in the email."""
    text = f"{subject}\n{subject}\n{body}"
    indicators: List[Dict] = []
    seen = set()

    for name, severity, desc, patterns in _COMPILED:
        if name in seen:
            continue
        matched = any(p.search(text) for p in patterns)
        if matched:
            seen.add(name)
            indicators.append({
                "indicator": name,
                "severity": severity,
                "category": "phishing",
                "description": desc,
            })

    # Sender-pattern checks (kept separate, operate on the sender address).
    sender_indicators = _analyze_sender(sender)
    indicators.extend(sender_indicators)

    return indicators


def _analyze_sender(sender: str) -> List[Dict]:
    """Heuristic checks on the sender address (suspicious, not conclusive)."""
    if not sender:
        return []

    out = []
    lower = sender.lower().strip()

    # Disposable / free-mail + financial keyword combo is a classic phishing tell.
    free_mail = re.search(r"@(gmail|yahoo|hotmail|outlook|aol|protonmail)\.", lower)
    brand = re.search(r"\b(paypal|bank|chase|wells|citibank|apple|microsoft|amazon|netflix|irs)\b", lower)
    if free_mail and brand:
        out.append({
            "indicator": "Suspicious sender domain",
            "severity": "MEDIUM",
            "category": "sender",
            "description": (
                "Sender uses a free webmail domain while impersonating a brand — "
                "a common phishing pattern."
            ),
        })

    # Lookalike / typo-squatting style domains (very long, or many dots/dashes).
    if sender.count("@") == 1:
        domain = sender.split("@")[1]
        if domain.count(".") >= 4 or len(domain) > 40:
            out.append({
                "indicator": "Unusual sender domain",
                "severity": "LOW",
                "category": "sender",
                "description": "Sender domain looks unusual (very long or many subdomains).",
            })

    return out


def phishing_probability(indicators: List[Dict]) -> float:
    """Estimate a phishing probability (0-1) from indicator severities.

    This is a transparent heuristic, not a calibrated probability: HIGH=0.18,
    MEDIUM=0.10, LOW=0.05, capped at 0.95."""
    weights = {"HIGH": 0.18, "MEDIUM": 0.10, "LOW": 0.05}
    score = sum(weights.get(i["severity"], 0.05) for i in indicators)
    return round(min(0.95, score), 4)
