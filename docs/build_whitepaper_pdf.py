#!/usr/bin/env python3
"""Markdown-driven Operator ETL white paper PDF builder."""

from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

DOCS = Path(__file__).resolve().parent
ASSETS = DOCS / "assets"
MD_PATH = DOCS / "Operator-ETL-White-Paper.md"
PDF_PATH = DOCS / "Operator-ETL-White-Paper.pdf"

NAVY = colors.HexColor("#0F172A")
NAVY_MID = colors.HexColor("#1E293B")
BLUE = colors.HexColor("#2563EB")
TEAL = colors.HexColor("#0D9488")
GREEN = colors.HexColor("#059669")
AMBER = colors.HexColor("#D97706")
SLATE = colors.HexColor("#64748B")
BG = colors.HexColor("#F8FAFC")
WHITE = colors.white
BORDER = colors.HexColor("#E2E8F0")

PAGE_W, PAGE_H = letter
MARGIN = 0.72 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

HERO_ANCHORS = {
    "5. system architecture": "three-planes.png",
    "5.1 end-to-end flow": "three-planes.png",
    "11. mcp tool surface": "mcp-agent-flow.png",
    "12. gcp implementation": "gcp-architecture.png",
}

STATUS_COLORS = {
    "IMPLEMENTED": GREEN,
    "SPECIFIED": BLUE,
    "PARTIAL": AMBER,
}


def S(name, **kw) -> ParagraphStyle:
    d = dict(fontName="Helvetica", fontSize=10, leading=14, textColor=NAVY)
    d.update(kw)
    return ParagraphStyle(name, **d)


ST = {
    "body": S("body", alignment=TA_JUSTIFY, spaceAfter=6),
    "h1": S("h1", fontName="Helvetica-Bold", fontSize=16, leading=20, textColor=NAVY, spaceBefore=12, spaceAfter=8),
    "h2": S("h2", fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=BLUE, spaceBefore=10, spaceAfter=5),
    "h3": S("h3", fontName="Helvetica-Bold", fontSize=10.5, leading=13, textColor=NAVY_MID, spaceBefore=8, spaceAfter=4),
    "bullet": S("bullet", leftIndent=14, bulletIndent=4, spaceAfter=3),
    "caption": S("caption", fontSize=8, leading=10, textColor=SLATE, alignment=TA_CENTER, spaceAfter=8),
    "toc": S("toc", fontSize=10, leading=16, textColor=NAVY),
    "code": S("code", fontName="Courier", fontSize=7.2, leading=9, textColor=NAVY, backColor=BG, borderPadding=6, spaceAfter=8),
}


def esc(t: str) -> str:
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def fmt(t: str) -> str:
    t = esc(t.strip())
    t = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8" color="#2563EB">\1</font>', t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)
    return t


def status_badge(text: str) -> Table | None:
    m = re.search(r"\b(IMPLEMENTED|SPECIFIED|PARTIAL)\b", text)
    if not m:
        return None
    label = m.group(1)
    color = STATUS_COLORS.get(label, SLATE)
    t = Table([[Paragraph(f'<font color="#FFFFFF"><b>{label}</b></font>', S("sb", fontSize=7))]], colWidths=[0.85 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def section_header(title: str, subtitle: str = "") -> list:
    rows = [[Paragraph(fmt(title), ST["h1"])]]
    if subtitle:
        rows.append([Paragraph(fmt(subtitle), S("sub", fontSize=9, textColor=SLATE))])
    t = Table(rows, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, 0), 2, BLUE),
    ]))
    return [Spacer(1, 4), t, Spacer(1, 6)]


def hero_image(filename: str, caption: str = "") -> list:
    path = ASSETS / filename
    if not path.exists():
        return []
    img = Image(str(path), width=CONTENT_W, height=2.0 * inch)
    img.hAlign = "CENTER"
    out = [Spacer(1, 4), img]
    if caption:
        out.append(Paragraph(caption, ST["caption"]))
    return out


def parse_table(lines: list[str]) -> Table | None:
    rows_raw = []
    for line in lines:
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.match(r"^[-:\s]+$", c) for c in cells):
            continue
        rows_raw.append(cells)
    if not rows_raw:
        return None
    cs = S("cell", fontSize=8.5, leading=11)
    hcs = S("hcell", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=WHITE)
    data = []
    for i, row in enumerate(rows_raw):
        st = hcs if i == 0 else cs
        data.append([Paragraph(fmt(c), st) for c in row])
    cw = CONTENT_W / len(rows_raw[0])
    t = Table(data, colWidths=[cw] * len(rows_raw[0]), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.35, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, BG]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def collect_headings(md: str) -> list[tuple[int, str]]:
    headings = []
    for line in md.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            headings.append((2, line[3:].strip()))
        elif line.startswith("### "):
            headings.append((3, line[4:].strip()))
    return headings


def cover_page(c: canvas.Canvas, doc):
    c.saveState()
    c.setFillColor(NAVY)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    hero = ASSETS / "cover-hero.png"
    if hero.exists():
        c.drawImage(str(hero), 0, PAGE_H * 0.38, width=PAGE_W, height=PAGE_H * 0.62, preserveAspectRatio=False, mask="auto")
        c.setFillColor(NAVY)
        c.setFillAlpha(0.85)
        c.rect(0, 0, PAGE_W, PAGE_H * 0.52, fill=1, stroke=0)
        c.setFillAlpha(1)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 28)
    c.drawString(MARGIN, PAGE_H * 0.38, "Operator ETL")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawString(MARGIN, PAGE_H * 0.38 - 0.35 * inch, "Agentic Data Platform — Engineering White Paper")
    c.setFont("Helvetica", 10)
    c.drawString(MARGIN, PAGE_H * 0.38 - 0.6 * inch, "v2.1  ·  Architecture · MCP · GCP · NFRs · ADRs")
    c.setFont("Helvetica", 8)
    c.setFillColor(SLATE)
    c.drawString(MARGIN, 0.5 * inch, "IMPLEMENTED vs SPECIFIED clearly marked  ·  24/24 tests passing")
    c.restoreState()


def body_page(c: canvas.Canvas, doc):
    c.saveState()
    c.setFillColor(BLUE)
    c.rect(0, PAGE_H - 0.16 * inch, PAGE_W, 0.16 * inch, fill=1, stroke=0)
    c.setStrokeColor(BORDER)
    c.line(MARGIN, 0.5 * inch, PAGE_W - MARGIN, 0.5 * inch)
    c.setFillColor(SLATE)
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN, 0.35 * inch, "Operator ETL White Paper v2.1")
    c.drawRightString(PAGE_W - MARGIN, 0.35 * inch, f"Page {doc.page}")
    c.restoreState()


def build_toc(headings: list[tuple[int, str]]) -> list:
    story = [PageBreak()]
    story.extend(section_header("Table of Contents"))
    skip = {"document control", "terminology", "table of contents", "abstract"}
    for level, title in headings:
        key = title.lower()
        if any(s in key for s in skip):
            continue
        indent = 24 if level == 3 else 0
        num = re.match(r"^[\d.]+\s", title)
        display = title if num else title
        story.append(Paragraph(fmt(display), S(f"toc{level}", leftIndent=indent, fontSize=9 if level == 3 else 10, leading=14)))
    story.append(PageBreak())
    return story


def md_to_story(md: str) -> list:
    story: list = []
    lines = md.splitlines()
    i = 0
    skip_until_abstract = True

    while i < len(lines):
        line = lines[i]
        s = line.strip()

        if not s or s.startswith("> **PDF"):
            i += 1
            continue

        if skip_until_abstract:
            if s == "## Abstract":
                skip_until_abstract = False
                story.append(PageBreak())
                story.extend(section_header("Abstract"))
                i += 1
                abs_lines = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("#") and lines[i].strip() != "---":
                    abs_lines.append(lines[i].strip())
                    i += 1
                if abs_lines:
                    story.append(Paragraph(fmt(" ".join(abs_lines)), ST["body"]))
                continue
            i += 1
            continue

        if s == "---":
            i += 1
            continue

        if s.startswith("```"):
            block = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            story.append(Preformatted("\n".join(block), ST["code"]))
            continue

        if s.startswith("|"):
            tbl = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            t = parse_table(tbl)
            if t:
                story.append(Spacer(1, 3))
                story.append(t)
                story.append(Spacer(1, 6))
            continue

        if s.startswith("## "):
            title = s[3:].strip()
            key = title.lower()
            if title.lower() in ("document control", "terminology"):
                story.append(PageBreak())
            story.extend(section_header(title))
            badge = status_badge(title)
            for j in range(i + 1, min(i + 4, len(lines))):
                badge = status_badge(lines[j]) or badge
                if badge:
                    break
            if badge:
                story.append(badge)
                story.append(Spacer(1, 4))
            for anchor, img in HERO_ANCHORS.items():
                if anchor in key:
                    story.extend(hero_image(img, f"Fig — {title}"))
                    break
            i += 1
            continue

        if s.startswith("### "):
            title = s[4:].strip()
            story.append(Paragraph(fmt(title), ST["h2"]))
            if "status:" in title.lower() or i + 1 < len(lines):
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
                badge = status_badge(nxt) or status_badge(title)
                if badge:
                    story.append(badge)
                    story.append(Spacer(1, 3))
            i += 1
            continue

        if s.startswith("**Status:**") or s.startswith("**Status**:"):
            story.append(Paragraph(fmt(s), S("st", fontSize=9, textColor=SLATE, spaceAfter=4)))
            i += 1
            continue

        if s.startswith("- "):
            story.append(Paragraph(fmt(s[2:]), ST["bullet"], bulletText="•"))
            i += 1
            continue

        if s.startswith("*End of white paper*"):
            story.append(Spacer(1, 16))
            story.append(Paragraph("— End of white paper —", S("end", alignment=TA_CENTER, textColor=SLATE)))
            i += 1
            continue

        if set(s) <= {"─", "┌", "┐", "└", "┘", "│", "▼", "▶", "◀", "┬", "┴", "├", "┤", " ", "→"} or (
            "┌" in s or "│" in s or "─" in s
        ):
            block = []
            while i < len(lines) and (lines[i].strip() == "" or any(c in lines[i] for c in "┌│─▼▶┐└┘→")):
                if lines[i].strip():
                    block.append(lines[i])
                i += 1
                if i < len(lines) and lines[i].strip().startswith("#"):
                    break
            if block:
                story.append(Preformatted("\n".join(block), ST["code"]))
            continue

        if s.startswith("# "):
            i += 1
            continue

        story.append(Paragraph(fmt(s), ST["body"]))
        i += 1

    return story


def main():
    md = MD_PATH.read_text(encoding="utf-8")
    headings = collect_headings(md)

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        topMargin=0.8 * inch,
        bottomMargin=0.65 * inch,
    )

    story = build_toc(headings) + md_to_story(md)
    doc.build(story, onFirstPage=cover_page, onLaterPages=body_page)
    print(f"Wrote {PDF_PATH} ({doc.page} pages)")


if __name__ == "__main__":
    main()
