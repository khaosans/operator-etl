#!/usr/bin/env python3
"""Build a single-page executive PDF from Operator-ETL-One-Pager.md."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

DOCS = Path(__file__).resolve().parent
MD_PATH = DOCS / "Operator-ETL-One-Pager.md"
PDF_PATH = DOCS / "Operator-ETL-One-Pager.pdf"

NAVY = colors.HexColor("#0F172A")
BLUE = colors.HexColor("#2563EB")
TEAL = colors.HexColor("#0D9488")
SLATE = colors.HexColor("#64748B")
BG = colors.HexColor("#F8FAFC")


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def body_style() -> ParagraphStyle:
    return ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12, textColor=NAVY, spaceAfter=4)


def h1_style() -> ParagraphStyle:
    return ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=NAVY, spaceAfter=6)


def h2_style() -> ParagraphStyle:
    return ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=11, leading=14, textColor=BLUE, spaceBefore=8, spaceAfter=4)


def build() -> None:
    text = MD_PATH.read_text(encoding="utf-8")
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )
    story = []
    in_table = False
    table_rows: list[list[str]] = []

    for line in text.splitlines():
        raw = line.rstrip()
        if raw.startswith("# "):
            story.append(Paragraph(esc(raw[2:]), h1_style()))
            continue
        if raw.startswith("## "):
            if in_table and table_rows:
                story.append(_table(table_rows))
                table_rows = []
                in_table = False
            story.append(Paragraph(esc(raw[3:]), h2_style()))
            continue
        if raw.startswith("|") and "|" in raw[1:]:
            if raw.replace("|", "").replace("-", "").replace(" ", "") == "":
                continue
            cells = [c.strip() for c in raw.strip("|").split("|")]
            if cells and cells[0].lower() != "metric" and cells[0].lower() != "plane":
                table_rows.append(cells)
                in_table = True
            continue
        if in_table and table_rows and not raw.startswith("|"):
            story.append(_table(table_rows))
            table_rows = []
            in_table = False
        if raw.startswith("```"):
            continue
        if raw.startswith("---"):
            story.append(Spacer(1, 6))
            continue
        if raw.startswith("- "):
            story.append(Paragraph(f"• {esc(raw[2:])}", body_style()))
            continue
        if raw.strip():
            story.append(Paragraph(esc(raw), body_style()))

    if table_rows:
        story.append(_table(table_rows))

    doc.build(story)
    print(f"Wrote {PDF_PATH}")


def _table(rows: list[list[str]]) -> Table:
    t = Table(rows, colWidths=[2.8 * inch, 3.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG]),
                ("GRID", (0, 0), (-1, -1), 0.25, SLATE),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return t


if __name__ == "__main__":
    build()
