"""
Service: safe email parsing (.txt / .eml).

Parses uploaded email content into a structured dict WITHOUT executing any
attachments or embedded scripts. All content is treated as untrusted input.
"""

from __future__ import annotations

import email
import re
from email import policy
from email.parser import BytesParser
from typing import Dict, List, Optional

from app.utils.exceptions import InvalidFileError
from app.services.url_service import extract_urls

ALLOWED_EXTENSIONS = {".txt", ".eml"}
ALLOWED_MIME_TYPES = {"text/plain", "message/rfc822", "application/octet-stream",
                      "text/eml"}


def validate_filename(filename: str) -> None:
    if not filename:
        raise InvalidFileError("No filename provided.")
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileError(
            f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}."
        )


def _decode_header(value: str) -> str:
    """Decode RFC2047 encoded headers (e.g. =?utf-8?q?...?=)."""
    if not value:
        return ""
    try:
        parts = email.header.decode_header(value)
        out = []
        for text, charset in parts:
            if isinstance(text, bytes):
                out.append(text.decode(charset or "utf-8", errors="replace"))
            else:
                out.append(text)
        return " ".join(out)
    except Exception:
        return value


def _extract_text_parts(message) -> tuple:
    """Walk a MIME message and collect text + html bodies and attachment count."""
    text_parts: List[str] = []
    html_parts: List[str] = []
    attachment_count = 0

    def walk(msg):
        nonlocal attachment_count
        if msg.is_multipart():
            for part in msg.get_payload():
                walk(part)
            return

        content_type = msg.get_content_type()
        disposition = str(msg.get("Content-Disposition", "")).lower()
        ctype = str(msg.get_content_type()).lower()

        if "attachment" in disposition:
            attachment_count += 1
            return

        if content_type == "text/plain":
            text_parts.append(msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="replace"))
        elif content_type == "text/html":
            html_parts.append(msg.get_payload(decode=True).decode(
                msg.get_content_charset() or "utf-8", errors="replace"))

    walk(message)
    return "\n".join(text_parts), "\n".join(html_parts), attachment_count


def parse_email_bytes(content: bytes, filename: str) -> Dict:
    """Parse raw file bytes into a structured email dict."""
    validate_filename(filename)
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == ".txt":
        text = content.decode("utf-8", errors="replace")
        urls = extract_urls(text)
        return {
            "subject": "", "sender": "", "to": "", "reply_to": "",
            "date": "", "body": text, "html_body": "", "urls": urls,
            "has_attachments": False,
        }

    # .eml — parse with the email stdlib (safe: no execution of content).
    try:
        msg = BytesParser(policy=policy.default).parsebytes(content)
    except Exception as exc:  # pragma: no cover
        raise InvalidFileError(f"Could not parse email file: {exc}")

    subject = _decode_header(str(msg.get("Subject", "")))
    sender = _decode_header(str(msg.get("From", "")))
    to = _decode_header(str(msg.get("To", "")))
    reply_to = _decode_header(str(msg.get("Reply-To", "")))
    date = str(msg.get("Date", ""))

    text_body, html_body, attachment_count = _extract_text_parts(msg)

    # Fall back to the HTML body (stripped of tags) if no plain text present.
    if not text_body.strip() and html_body.strip():
        text_body = re.sub(r"<[^>]+>", " ", html_body)
        text_body = re.sub(r"\s+", " ", text_body)

    urls = extract_urls(f"{html_body}\n{text_body}")

    return {
        "subject": subject, "sender": sender, "to": to, "reply_to": reply_to,
        "date": date, "body": text_body, "html_body": html_body,
        "urls": urls, "has_attachments": attachment_count > 0,
    }


def parse_email_text(subject: str, body: str, sender: str = "") -> Dict:
    """Build the same structured dict from directly-submitted text fields."""
    return {
        "subject": subject or "",
        "sender": sender or "",
        "to": "", "reply_to": "", "date": "",
        "body": body or "",
        "html_body": "",
        "urls": extract_urls(body or ""),
        "has_attachments": False,
    }
