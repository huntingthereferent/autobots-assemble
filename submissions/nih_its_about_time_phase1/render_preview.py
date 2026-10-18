"""Render the Phase 1 Markdown inspection draft to a bounded PDF preview.

This previews the NIH challenge's page/font rules; it DOES NOT register, sign,
upload to NIH, evaluate scientific claims, or alter the source-owned packet.
"""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepTogether, CondPageBreak
from pypdf import PdfReader

BODY_PT = 11.3
BODY_LEADING_PT = 16.0
MAX_PAGES = 10

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "PHASE1_CONCEPT_DRAFT.md"


def normalize_text(text):
    return (text.replace("\u2013", "-").replace("\u2014", " - ")
            .replace("\u2019", "'").replace("\u2018", "'")
            .replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u2264", "<=").replace("\u2265", ">=")
            .replace("\u2026", "..."))


def inlines(s):
    """Small safe Markdown subset; preserve source text, no arbitrary HTML."""
    text = escape(normalize_text(s), quote=True)
    # Inline code before generic emphasis to avoid conflicting constructs.
    text = re.sub(r"\x60([^\x60]+)\x60", r"<font name='Helvetica'>\1</font>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", text)
    # Convert Markdown links while keeping their titles in accessible PDF text.
    # Only approved http(s) sources are linkified.
    def as_link(m):
        label, href = m.group(1), m.group(2)
        if href.startswith(("https://", "http://")):
            return '<link href="' + href + '" color="#234e73">' + label + "</link>"
        return label
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", as_link, text)
    return text


def style(name, size=BODY_PT, leading=BODY_LEADING_PT, after=6, before=0,
          bold=False, left_indent=0):
    return ParagraphStyle(
        name, fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=leading, textColor=colors.HexColor("#172536"),
        alignment=TA_LEFT, spaceBefore=before, spaceAfter=after,
        leftIndent=left_indent, rightIndent=2, allowWidows=0, allowOrphans=0,
    )


STYLES = {
    "title": style("DraftTitle", 17, 21, 7, 0, True),
    "subtitle": style("DraftSubtitle", 13, 17, 8, 0, True),
    "section": style("DraftSection", 12.5, 17.5, 8, 14, True),
    "subsection": style("DraftSubsection", 11.8, 16.5, 5, 9, True),
    "body": style("DraftBody"),
    "bullet": style("DraftBullet", left_indent=14),
    "meta": style("DraftMeta", 11.3, 16, 6, 0, False),
}


def elements(markdown):
    lines = normalize_text(markdown).splitlines()
    items = []
    pending = []

    def flush():
        if pending:
            p = " ".join(pending).strip()
            if p:
                items.append(Paragraph(inlines(p), STYLES["body"]))
            pending.clear()

    for line in lines:
        s = line.strip()
        if not s:
            flush()
            continue
        if s.startswith("# "):
            flush()
            items.append(Paragraph(inlines(s[2:]), STYLES["title"]))
        elif s.startswith("## "):
            flush()
            items.append(CondPageBreak(65))
            items.append(Paragraph(inlines(s[3:]), STYLES["subtitle"]
                             if len(items) < 3 else STYLES["section"]))
        elif s.startswith("### "):
            flush()
            items.append(CondPageBreak(55))
            items.append(Paragraph(inlines(s[4:]), STYLES["section"]))
        elif s.startswith("#### "):
            flush()
            items.append(CondPageBreak(46))
            items.append(Paragraph(inlines(s[5:]), STYLES["subsection"]))
        elif re.match(r"^[-*] ", s):
            flush()
            items.append(Paragraph("&bull;  " + inlines(s[2:]), STYLES["bullet"]))
        elif re.match(r"^[0-9]+[.] ", s):
            flush()
            items.append(Paragraph(inlines(s), STYLES["bullet"]))
        else:
            pending.append(s)
            if line.endswith("  "):  # Markdown hard break: keep the draft metadata separate
                flush()
    flush()
    return items


def page_label(canvas, doc):
    canvas.saveState()
    width, height = letter
    canvas.setStrokeColor(colors.HexColor("#d7dfe5"))
    canvas.line(55, height - 42, width - 55, height - 42)
    canvas.setFillColor(colors.HexColor("#4b5864"))
    canvas.setFont("Helvetica", 11)
    canvas.drawString(56, height - 34, "NIH Phase 1 | Concept and Feasibility | DRAFT FOR REVIEW")
    canvas.drawString(56, 39, "Not submitted to NIH - synthetic and bounded feasibility evidence")
    canvas.drawRightString(width - 56, 39, f"Page {doc.page}")
    canvas.restoreState()


def render(source: Path, output: Path):
    markdown = source.read_text(encoding="utf8")
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output), pagesize=letter,
        leftMargin=58, rightMargin=58, topMargin=62, bottomMargin=62,
        title="Temporal Evidence Availability in Biomedical KGs - Phase 1 Draft",
        author="Independent research; source-owned investigation",
    )
    doc.build(elements(markdown), onFirstPage=page_label,
              onLaterPages=page_label)
    pdf = PdfReader(str(output))
    if not (1 <= len(pdf.pages) <= MAX_PAGES):
        raise ValueError(
            f"PDF preview page count {len(pdf.pages)} exceeds official ten-page limit")
    extracted = "\n".join(page.extract_text() or "" for page in pdf.pages)
    for required in (
        "Temporal Evidence Availability", "ClinicalTrials.gov",
        "Phase 1", "Formal query rule", "Feasibility evidence",
        "NOT REGISTERED OR SUBMITTED",
    ):
        if required.lower() not in extracted.lower():
            raise ValueError(f"render lost required section: {required}")
    return {"pages": len(pdf.pages), "body_font_size_pt": BODY_PT,
            "body_leading_pt": BODY_LEADING_PT,
            "paper": "US Letter", "submitted": False, "ontology_separate": True}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, default=SOURCE)
    ap.add_argument("--output", type=Path, required=True)
    opts = ap.parse_args()
    result = render(opts.source, opts.output)
    import json
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
