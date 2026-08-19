"""
Service: PDF security report generation (reportlab).

Produces a downloadable, branded PDF report for a completed scan.
"""

from __future__ import annotations

import io
from datetime import datetime
from typing import Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

ACCENT = colors.HexColor("#6366f1")      # indigo
DARK = colors.HexColor("#0f172a")
MUTED = colors.HexColor("#64748b")
GOOD = colors.HexColor("#10b981")
WARN = colors.HexColor("#f59e0b")
BAD = colors.HexColor("#ef4444")


def _risk_color(level: str):
    return {
        "LOW": GOOD, "MEDIUM": WARN, "HIGH": colors.HexColor("#f97316"),
        "CRITICAL": BAD,
    }.get(level, MUTED)


def generate_pdf_report(scan: Dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=16 * mm, bottomMargin=16 * mm,
        title="SpamGuard AI Security Report",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1x", parent=styles["Title"], fontSize=22,
                        textColor=DARK, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10,
                         textColor=MUTED, spaceAfter=10)
    h2 = ParagraphStyle("h2x", parent=styles["Heading2"], fontSize=13,
                        textColor=ACCENT, spaceBefore=10, spaceAfter=4)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5,
                          leading=13, textColor=colors.HexColor("#1e293b"))
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8.5,
                           leading=11, textColor=MUTED)

    story = []
    story.append(Paragraph("SpamGuard AI — Security Report", h1))
    story.append(Paragraph("Intelligent Email Spam, Phishing &amp; Threat Analyzer", sub))

    level = scan.get("risk_level", "LOW")
    rcolor = _risk_color(level)

    # Header / verdict table.
    verdict_data = [
        ["Classification", scan.get("classification", "UNKNOWN")],
        ["Confidence", f"{scan.get('confidence', 0):.1%}"],
        ["Risk Score", f"{scan.get('risk_score', 0)} / 100"],
        ["Risk Level", level],
        ["Model", scan.get("model_name", "-")],
        ["Scanned At", _fmt_ts(scan.get("timestamp"))],
    ]
    vt = Table(verdict_data, colWidths=[38 * mm, 100 * mm])
    vt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (1, 3), (1, 3), rcolor),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(vt)

    # Email information.
    story.append(Paragraph("Email Information", h2))
    info = scan.get("email_info", {})
    story.append(Paragraph(f"<b>Subject:</b> {_esc(info.get('subject') or '(none)')}", body))
    story.append(Paragraph(f"<b>Sender:</b> {_esc(info.get('sender') or '(unknown)')}", body))
    story.append(Paragraph(f"<b>Date:</b> {_esc(info.get('date') or '-')}", body))
    story.append(Spacer(1, 4))

    # Threat indicators.
    story.append(Paragraph("Threat Indicators", h2))
    indicators = scan.get("threat_indicators", [])
    if indicators:
        for i in indicators:
            sev = i.get("severity", "LOW")
            sev_color = {
                "HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#94a3b8",
            }.get(sev, "#94a3b8")
            story.append(Paragraph(
                f"• <b>{_esc(i.get('indicator'))}</b> "
                f"[<font color='{sev_color}'>{sev}</font>] — "
                f"{_esc(i.get('description'))}", body))
    else:
        story.append(Paragraph("No threat indicators detected.", small))

    # Suspicious URLs.
    story.append(Paragraph("URL Analysis", h2))
    urls = scan.get("urls", [])
    if urls:
        for u in urls:
            story.append(Paragraph(f"• <b>{_esc(u.get('domain') or '?')}</b> "
                                   f"({u.get('protocol', '')}) — {u.get('severity', 'NONE')}",
                                   body))
            story.append(Paragraph(f"&nbsp;&nbsp;{_esc(u.get('url'))}", small))
    else:
        story.append(Paragraph("No URLs found.", small))

    # Statistics.
    story.append(Paragraph("Email Statistics", h2))
    stats = scan.get("statistics", {})
    stat_rows = [
        ("Word count", stats.get("word_count")),
        ("Character count", stats.get("character_count")),
        ("Sentence count", stats.get("sentence_count")),
        ("URL count", stats.get("url_count")),
        ("Suspicious keywords", stats.get("suspicious_keyword_count")),
        ("Threat indicators", stats.get("threat_indicator_count")),
        ("Contains HTML", "Yes" if stats.get("has_html") else "No"),
        ("Has attachments", "Yes" if stats.get("has_attachments") else "No"),
    ]
    st = Table([[k, str(v)] for k, v in stat_rows], colWidths=[60 * mm, 60 * mm])
    st.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(st)

    # AI analysis.
    ai = scan.get("ai_analysis", {})
    story.append(Paragraph("AI Analysis", h2))
    if ai.get("available"):
        story.append(Paragraph(f"<b>Summary:</b> {_esc(ai.get('summary'))}", body))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Explanation:</b> {_esc(ai.get('explanation'))}", body))
        story.append(Spacer(1, 3))
        story.append(Paragraph(f"<b>Threat analysis:</b> {_esc(ai.get('threat_analysis'))}", body))
    else:
        story.append(Paragraph("AI explanation unavailable: "
                               f"{_esc(ai.get('reason', ''))}", small))

    # Recommendation.
    story.append(Paragraph("Recommended Action", h2))
    story.append(Paragraph(_esc(scan.get("recommendation", "")), body))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "This report was generated by SpamGuard AI. Findings are heuristic and "
        "ML-based; they do not constitute a definitive determination of malice.",
        small))

    doc.build(story)
    return buf.getvalue()


def _fmt_ts(ts) -> str:
    if not ts:
        return "-"
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00")).strftime(
            "%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return str(ts)


def _esc(text) -> str:
    return (str(text or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))
