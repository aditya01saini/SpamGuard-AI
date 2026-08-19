"""
Service: URL extraction & analysis.

Extracts URLs from the raw email text/HTML and analyzes each one with local
heuristics only (no external threat-intelligence calls by default). Results
are phrased as *suspicious / potentially unsafe* rather than asserting a URL
is malicious.
"""

from __future__ import annotations

import re
import urllib.parse
from typing import Dict, List

URL_RE = re.compile(r"https?://[^\s<>\"'\]]+|www\.[^\s<>\"'\]]+", re.IGNORECASE)

# Common link-shortener domains.
SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "rebrand.ly", "cutt.ly", "shorturl.at", "tiny.cc", "rb.gy", "s.id",
}

# TLDs frequently (but not exclusively) associated with abuse.
RISKY_TLDS = {
    "tk", "ml", "ga", "cf", "gq", "zip", "mov", "top", "xyz", "click", "icu",
    "rest", "bar", "cn", "ru", "surf", "work", "loan", "racing", "accountant",
    "download", "stream", "gdn", "link", "mom", "men", "bid", "win", "vip",
}

SUSPICIOUS_DOMAIN_KEYWORDS = {
    "secure", "login", "signin", "account", "verify", "update", "bank",
    "paypal", "apple", "microsoft", "amazon", "support", "alert", "confirm",
    "webscr", "wallet", "billing",
}


def extract_urls(text: str) -> List[str]:
    """Extract unique URLs from text (raw body + HTML)."""
    if not text:
        return []
    urls = []
    seen = set()
    for u in URL_RE.findall(text):
        # findall returns the matched strings (no capture groups used).
        # Normalize: drop trailing punctuation that is not part of the URL.
        u = u.rstrip(".,;:!?)]}'\"")
        if u not in seen:
            seen.add(u)
            urls.append(u)
    return urls


def analyze_url(raw_url: str) -> Dict:
    """Analyze a single URL and return structured findings."""
    url = raw_url.strip()
    indicators: List[Dict] = []

    # Parse (add scheme for protocol-relative inputs like "www.x.com").
    if not url.lower().startswith(("http://", "https://")):
        url = "http://" + url
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or ""
    port = parsed.port

    protocol = parsed.scheme
    is_https = protocol.lower() == "https"
    domain = host.lower()

    def flag(name: str, severity: str, desc: str):
        indicators.append({"indicator": name, "severity": severity, "description": desc})

    # 1. Plain HTTP (not encrypted).
    if not is_https:
        flag("Insecure protocol (HTTP)", "LOW",
             "URL uses unencrypted HTTP rather than HTTPS.")

    # 2. IP-address host (common in phishing to hide the real domain).
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain):
        flag("IP-address URL", "HIGH",
             "URL uses a raw IP address instead of a domain name — a frequent "
             "phishing technique to conceal the destination.")

    # 3. URL shortener.
    if domain in SHORTENERS:
        flag("URL shortener", "MEDIUM",
             "URL uses a link-shortening service that hides the true destination.")

    # 4. Encoded / obfuscated characters.
    if re.search(r"%(2e|2f|40|3a|00)|%2e|%2f|%40", url, re.IGNORECASE):
        flag("Encoded characters", "MEDIUM",
             "URL contains percent-encoded characters that may obfuscate the "
             "destination.")

    # 5. Userinfo / @ trick (http://real-site.com@evil.com).
    if "@" in parsed.netloc and domain and "@" in url.split("//", 1)[-1].split("/", 1)[0]:
        flag("Misleading '@' in URL", "HIGH",
             "URL contains an '@' symbol, which can disguise the real domain.")

    # 6. Suspicious keywords in the domain.
    hit_keywords = [k for k in SUSPICIOUS_DOMAIN_KEYWORDS if k in domain]
    if hit_keywords:
        flag("Suspicious domain keywords", "MEDIUM",
             f"Domain contains suspicious keyword(s): {', '.join(hit_keywords)}.")

    # 7. Risky / unusual TLD.
    tld = domain.rsplit(".", 1)[-1] if "." in domain else ""
    if tld in RISKY_TLDS:
        flag("Unusual top-level domain", "LOW",
             f"Domain uses the '{tld}' TLD, which is unusual for legitimate services.")

    # 8. Numeric-heavy or very long domain.
    digits = sum(c.isdigit() for c in domain)
    if digits >= 5 and len(domain) > 0:
        flag("Numeric-heavy domain", "MEDIUM",
             "Domain contains many digits, a common pattern in auto-generated "
             "phishing domains.")
    if len(domain) > 40:
        flag("Very long domain", "LOW",
             "Domain name is unusually long.")

    # 9. Non-standard port.
    if port and port not in (80, 443):
        flag("Non-standard port", "LOW",
             f"URL uses non-standard port {port}.")

    # Severity rollup (HIGH > MEDIUM > LOW).
    order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    severity = max((i["severity"] for i in indicators), key=lambda s: order[s]) \
        if indicators else "NONE"

    return {
        "url": raw_url,
        "domain": domain,
        "protocol": protocol,
        "is_https": is_https,
        "port": port,
        "risk_indicators": indicators,
        "severity": severity,
        "suspicious": severity in ("HIGH", "MEDIUM"),
    }


def analyze_urls(raw_urls: List[str]) -> List[Dict]:
    return [analyze_url(u) for u in raw_urls]
