#!/usr/bin/env python3
"""Render Operator-ETL-Proposal.md to PDF."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS = Path(__file__).resolve().parent
MD_PATH = DOCS / "Operator-ETL-Proposal.md"
PDF_PATH = DOCS / "Operator-ETL-Proposal.pdf"

NAVY = colors.HexColor("#1A2332")
BLUE = colors.HexColor("#0066FF")
GRAY = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F1F5F9")
BORDER = colors.HexColor("#CBD5E1")


def build_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "DocTitle",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=26,
            leading=30,
            textColor=NAVY,
            spaceAfter=6,
            alignment=TA_LEFT,
        ),
        "subtitle": ParagraphStyle(
            "DocSubtitle",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=16,
            textColor=GRAY,
            spaceAfter=20,
        ),
        "h1": ParagraphStyle(
            "H1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=18,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=BLUE,
            spaceBefore=14,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "Bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=NAVY,
            leftIndent=18,
            bulletIndent=8,
            spaceAfter=4,
        ),
        "mono": ParagraphStyle(
            "Mono",
            parent=base["Code"],
            fontName="Courier",
            fontSize=8,
            leading=10,
            textColor=NAVY,
            backColor=LIGHT,
            borderPadding=6,
            spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            "Footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
    }


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("**", "")
    )


def inline_format(text: str) -> str:
    text = esc(text.strip())
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="9" color="#0066FF">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    return text


def parse_table(lines: list[str]) -> Table | None:
    if len(lines) < 2:
        return None
    rows = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [inline_format(c.strip()) for c in line.strip().strip("|").split("|")]
        if all(re.match(r"^[-:\s]+$", c.replace("<b>", "").replace("</b>", "")) for c in cells):
            continue
        rows.append([Paragraph(c, ParagraphStyle("cell", fontName="Helvetica", fontSize=9, leading=11)) for c in cells])
    if not rows:
        return None
    col_count = max(len(r) for r in rows)
    width = (6.5 * inch) / col_count
    table = Table(rows, colWidths=[width] * col_count, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def md_to_story(md: str, styles) -> list:
    story: list = []
    lines = md.splitlines()
    i = 0
    title_done = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue
        if stripped == "---":
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER))
            story.append(Spacer(1, 6))
            i += 1
            continue
        if stripped.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            story.append(Paragraph("<br/>".join(esc(x) for x in block), styles["mono"]))
            continue
        if stripped.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
            table = parse_table(table_lines)
            if table:
                story.append(Spacer(1, 4))
                story.append(table)
                story.append(Spacer(1, 8))
            continue
        if stripped.startswith("# "):
            text = inline_format(stripped[2:])
            if not title_done:
                story.append(Paragraph(text, styles["title"]))
                title_done = True
            else:
                story.append(PageBreak())
                story.append(Paragraph(text, styles["h1"]))
            i += 1
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(inline_format(stripped[3:]), styles["h1"]))
            i += 1
            continue
        if stripped.startswith("### "):
            story.append(Paragraph(inline_format(stripped[4:]), styles["h2"]))
            i += 1
            continue
        if stripped.startswith("- "):
            story.append(Paragraph(inline_format(stripped[2:]), styles["bullet"], bulletText="•"))
            i += 1
            continue
        if stripped.startswith("*End of document*"):
            story.append(Spacer(1, 24))
            story.append(HRFlowable(width="40%", thickness=0.5, color=BORDER, hAlign="CENTER"))
            story.append(Spacer(1, 6))
            story.append(Paragraph("End of document", styles["footer"]))
            i += 1
            continue

        story.append(Paragraph(inline_format(stripped), styles["body"]))
        i += 1

    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(inch, 0.45 * inch, "Operator ETL — Proposal v1.0")
    canvas.drawRightString(letter[0] - inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main() -> int:
    if not MD_PATH.exists():
        print(f"Missing {MD_PATH}", file=sys.stderr)
        return 1

    styles = build_styles()
    md = MD_PATH.read_text(encoding="utf-8")
    story = md_to_story(md, styles)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title="Operator ETL Proposal",
        author="Operator ETL",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Wrote {PDF_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
