#!/usr/bin/env python3
"""Build Operator ETL slide-deck PDF."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

DOCS = Path(__file__).resolve().parent
PDF_PATH = DOCS / "Operator-ETL-Slides.pdf"

# 16:9-ish slide (landscape letter)
PAGE = landscape(letter)
W, H = PAGE

NAVY = colors.HexColor("#1A2332")
BLUE = colors.HexColor("#0066FF")
GREEN = colors.HexColor("#059669")
AMBER = colors.HexColor("#D97706")
RED = colors.HexColor("#DC2626")
GRAY = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#F8FAFC")
BORDER = colors.HexColor("#CBD5E1")
WHITE = colors.white


def P(text: str, size=11, bold=False, color=NAVY, leading=None):
    return Paragraph(
        text,
        ParagraphStyle(
            "p",
            fontName="Helvetica-Bold" if bold else "Helvetica",
            fontSize=size,
            leading=leading or size + 4,
            textColor=color,
        ),
    )


class SlideDeck:
    def __init__(self, path: Path):
        self.c = canvas.Canvas(str(path), pagesize=PAGE)
        self.page = 0
        self.total = 0

    def save(self):
        self.c.save()

    def _header(self, title: str, subtitle: str = ""):
        self.page += 1
        c = self.c
        c.setFillColor(NAVY)
        c.rect(0, H - 0.55 * inch, W, 0.55 * inch, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, H - 0.58 * inch, W * 0.18, 0.03 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.5 * inch, H - 0.38 * inch, title)
        if subtitle:
            c.setFont("Helvetica", 9)
            c.setFillColor(colors.HexColor("#94A3B8"))
            c.drawRightString(W - 0.5 * inch, H - 0.38 * inch, subtitle)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 8)
        c.drawRightString(W - 0.5 * inch, 0.28 * inch, f"Slide {self.page}")
        c.drawString(0.5 * inch, 0.28 * inch, "Operator ETL  ·  v1 Specification Deck")

    def title_slide(self, title: str, subtitle: str, meta: list[str]):
        c = self.c
        self.page += 1
        c.setFillColor(NAVY)
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(BLUE)
        c.rect(0, H * 0.42, W, 0.06 * inch, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 34)
        c.drawString(0.7 * inch, H * 0.55, title)
        c.setFont("Helvetica", 18)
        c.setFillColor(colors.HexColor("#CBD5E1"))
        c.drawString(0.7 * inch, H * 0.48, subtitle)
        y = H * 0.32
        c.setFont("Helvetica", 11)
        for line in meta:
            c.drawString(0.7 * inch, y, line)
            y -= 0.22 * inch

    def bullets(self, title: str, items: list[str], subtitle: str = ""):
        self._header(title, subtitle)
        y = H - 1.0 * inch
        self.c.setFillColor(NAVY)
        for item in items:
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(0.65 * inch, y, "▸")
            self.c.setFont("Helvetica", 12)
            # wrap long lines roughly
            words = item.split()
            line = ""
            x = 0.95 * inch
            for w in words:
                test = (line + " " + w).strip()
                if self.c.stringWidth(test, "Helvetica", 12) > W - 1.2 * inch:
                    self.c.drawString(x, y, line)
                    y -= 0.28 * inch
                    line = w
                else:
                    line = test
            if line:
                self.c.drawString(x, y, line)
            y -= 0.38 * inch
            if y < 0.6 * inch:
                break
        self.c.showPage()

    def two_column(self, title: str, left_title: str, left: list[str], right_title: str, right: list[str]):
        self._header(title)
        c = self.c
        mid = W / 2
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(0.55 * inch, H - 0.95 * inch, left_title)
        c.drawString(mid + 0.05 * inch, H - 0.95 * inch, right_title)
        yl = H - 1.25 * inch
        yr = H - 1.25 * inch
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 11)
        for item in left:
            c.drawString(0.65 * inch, yl, f"• {item}")
            yl -= 0.26 * inch
        for item in right:
            c.drawString(mid + 0.15 * inch, yr, f"• {item}")
            yr -= 0.26 * inch
        c.showPage()

    def diagram_box(self, title: str, lines: list[str], subtitle: str = ""):
        self._header(title, subtitle)
        c = self.c
        box_h = len(lines) * 0.22 * inch + 0.4 * inch
        box_y = (H - box_h) / 2 - 0.1 * inch
        c.setFillColor(LIGHT)
        c.setStrokeColor(BORDER)
        c.roundRect(0.55 * inch, box_y, W - 1.1 * inch, box_h, 8, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Courier", 10)
        y = box_y + box_h - 0.28 * inch
        for line in lines:
            c.drawString(0.75 * inch, y, line)
            y -= 0.22 * inch
        c.showPage()

    def table_slide(self, title: str, headers: list[str], rows: list[list[str]], subtitle: str = ""):
        self._header(title, subtitle)
        data = [[P(h, 10, bold=True, color=WHITE) for h in headers]]
        for row in rows:
            data.append([P(c, 9) for c in row])
        col_w = (W - 1.1 * inch) / len(headers)
        t = Table(data, colWidths=[col_w] * len(headers))
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        tw, th = t.wrap(W - 1.1 * inch, H)
        t.drawOn(self.c, 0.55 * inch, H - 1.0 * inch - th)
        self.c.showPage()

    def pipeline_flow(self, title: str):
        self._header(title, "Medallion architecture")
        c = self.c
        boxes = [
            ("INTAKE\nCSV · HTTP", BLUE),
            ("BRONZE\nraw JSON", NAVY),
            ("SILVER\ntyped rows", GREEN),
            ("GOLD\nSQL marts", colors.HexColor("#7C3AED")),
            ("INSIGHTS\nCLI · UI", AMBER),
        ]
        bw = 1.35 * inch
        bh = 0.85 * inch
        start_x = 0.45 * inch
        y = H / 2 - bh / 2 + 0.15 * inch
        gap = 0.18 * inch
        xs = []
        for i, (label, color) in enumerate(boxes):
            x = start_x + i * (bw + gap)
            xs.append(x)
            c.setFillColor(color)
            c.roundRect(x, y, bw, bh, 6, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 10)
            lines = label.split("\n")
            ly = y + bh / 2 + 0.08 * inch
            for ln in lines:
                c.drawCentredString(x + bw / 2, ly, ln)
                ly -= 0.16 * inch
            if i < len(boxes) - 1:
                c.setStrokeColor(BORDER)
                c.setLineWidth(2)
                c.line(x + bw, y + bh / 2, x + bw + gap, y + bh / 2)
                c.setFillColor(GRAY)
                c.setFont("Helvetica-Bold", 14)
                c.drawString(x + bw + gap / 2 - 0.05 * inch, y + bh / 2 - 0.05 * inch, "→")

        # quarantine branch
        qx = xs[2] + bw / 2 - 0.7 * inch
        qy = y - 1.1 * inch
        c.setFillColor(RED)
        c.roundRect(qx, qy, 1.4 * inch, 0.65 * inch, 6, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(qx + 0.7 * inch, qy + 0.28 * inch, "QUARANTINE")
        c.drawCentredString(qx + 0.7 * inch, qy + 0.12 * inch, "bad rows + reason")
        c.setStrokeColor(BORDER)
        c.line(xs[2] + bw / 2, y, xs[2] + bw / 2, qy + 0.65 * inch)

        # quality gate
        c.setFillColor(LIGHT)
        c.setStrokeColor(BORDER)
        c.roundRect(0.55 * inch, 0.55 * inch, W - 1.1 * inch, 0.55 * inch, 6, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 10)
        c.drawCentredString(
            W / 2,
            0.72 * inch,
            "Quality gate: KPIs withheld if quarantine rate > 35%  ·  freshness > 7 days  ·  silver empty",
        )
        c.showPage()

    def three_planes(self, title: str):
        self._header(title, "v2 evolution — agents on top, not inside ETL")
        c = self.c
        planes = [
            ("CONTROL PLANE (v2)", "LangGraph · checkpoints · HITL · critic · tool allowlists", BLUE),
            ("POLICY PLANE (v2)", "PII scan · token vault · redacted views · spend budgets", AMBER),
            ("DATA PLANE (v1)", "Extract · bronze · silver · quarantine · gold SQL", GREEN),
        ]
        ph = 0.95 * inch
        gap = 0.15 * inch
        total = len(planes) * ph + (len(planes) - 1) * gap
        y = (H + total) / 2 - ph - 0.3 * inch
        for name, desc, color in planes:
            c.setFillColor(color)
            c.roundRect(0.7 * inch, y, W - 1.4 * inch, ph, 8, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(0.95 * inch, y + ph - 0.32 * inch, name)
            c.setFont("Helvetica", 10)
            c.drawString(0.95 * inch, y + 0.18 * inch, desc)
            y -= ph + gap
            if y > 0.8 * inch:
                c.setStrokeColor(WHITE)
                c.setLineWidth(2)
                c.line(W / 2, y + ph + gap - 0.02 * inch, W / 2, y + ph + gap + 0.12 * inch)
        c.showPage()

    def cli_mock(self, title: str):
        self._header(title, "Terminal output after etl run --source demo")
        c = self.c
        c.setFillColor(colors.HexColor("#0F172A"))
        c.roundRect(0.55 * inch, 0.55 * inch, W - 1.1 * inch, H - 1.35 * inch, 8, fill=1, stroke=0)
        lines = [
            ("$ uv run etl run --source demo", GRAY),
            ("run ok  source=demo  rows_in=21  silver=17  quarantined=4", GREEN),
            ("", WHITE),
            ("Operator ETL insights", BLUE),
            ("Quality: PASS   quarantine_rate=19.1%", GREEN),
            ("", WHITE),
            ("KPIs", BLUE),
            ("  orders       17", WHITE),
            ("  customers    10", WHITE),
            ("  revenue      1373.82", WHITE),
            ("  avg order      80.81", WHITE),
            ("", WHITE),
            ("Top SKUs", BLUE),
            ("  SKU-PRO      orders=5  revenue=967.40", WHITE),
            ("  SKU-WIDGET   orders=6  revenue=225.82", WHITE),
        ]
        c.setFont("Courier", 9.5)
        y = H - 1.55 * inch
        for text, color in lines:
            c.setFillColor(color)
            c.drawString(0.8 * inch, y, text)
            y -= 0.2 * inch
        c.showPage()

    def dashboard_mock(self, title: str):
        self._header(title, "Streamlit run inspector — etl dashboard")
        c = self.c
        # metric cards row
        cards = [("Orders", "17"), ("Customers", "10"), ("Revenue", "1373.82"), ("Gate", "PASS")]
        cw = (W - 1.3 * inch) / 4
        y = H - 1.35 * inch
        for i, (label, val) in enumerate(cards):
            x = 0.55 * inch + i * (cw + 0.08 * inch)
            c.setFillColor(LIGHT)
            c.setStrokeColor(BORDER)
            c.roundRect(x, y, cw, 0.75 * inch, 6, fill=1, stroke=1)
            c.setFillColor(GRAY)
            c.setFont("Helvetica", 9)
            c.drawString(x + 0.12 * inch, y + 0.52 * inch, label)
            c.setFillColor(NAVY if label != "Gate" else GREEN)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(x + 0.12 * inch, y + 0.18 * inch, val)

        # chart area
        c.setFillColor(WHITE)
        c.setStrokeColor(BORDER)
        c.roundRect(0.55 * inch, 0.55 * inch, (W - 1.25 * inch) * 0.58, 2.0 * inch, 6, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.7 * inch, 2.25 * inch, "Volume over time")
        # simple line chart mock
        pts = [(0.9, 1.0), (1.4, 1.3), (1.9, 1.1), (2.4, 1.6), (2.9, 1.4), (3.4, 1.8), (3.9, 1.5)]
        c.setStrokeColor(BLUE)
        c.setLineWidth(2)
        ox, oy = 0.75 * inch, 0.75 * inch
        for i in range(len(pts) - 1):
            c.line(ox + pts[i][0] * inch, oy + pts[i][1] * inch, ox + pts[i + 1][0] * inch, oy + pts[i + 1][1] * inch)

        # sku bar chart
        bx = 0.55 * inch + (W - 1.25 * inch) * 0.62
        c.setFillColor(WHITE)
        c.roundRect(bx, 0.55 * inch, (W - 1.25 * inch) * 0.36, 2.0 * inch, 6, fill=1, stroke=1)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(bx + 0.12 * inch, 2.25 * inch, "Top SKUs")
        bars = [("PRO", 0.9), ("WIDGET", 0.55), ("GADGET", 0.4)]
        by = 1.9 * inch
        for name, h in bars:
            c.setFillColor(BLUE)
            c.rect(bx + 0.2 * inch, by, 0.35 * inch, h * inch, fill=1, stroke=0)
            c.setFillColor(NAVY)
            c.setFont("Helvetica", 8)
            c.drawString(bx + 0.65 * inch, by + h * inch / 2, name)
            by -= 0.55 * inch

        # quarantine panel
        c.setFillColor(colors.HexColor("#FEF2F2"))
        c.setStrokeColor(RED)
        c.roundRect(0.55 * inch, 2.65 * inch, W - 1.1 * inch, 0.55 * inch, 6, fill=1, stroke=1)
        c.setFillColor(RED)
        c.setFont("Helvetica", 9)
        c.drawString(
            0.75 * inch,
            2.82 * inch,
            "Quarantine (4 rows): empty order_id · invalid date · negative amount · non-numeric amount",
        )
        c.showPage()

    def build_phases(self, title: str):
        self._header(title, "Implementation sequence")
        phases = [
            ("1", "Scaffold", "Repo · uv · DuckDB · CLI skeleton · source registry YAML"),
            ("2", "Data plane", "CSV/HTTP extract · bronze load · SHA-256 idempotency · run log"),
            ("3", "Transform", "Pydantic contract · silver load · quarantine table · dedupe"),
            ("4", "Gold + insights", "SQL marts · quality gate · CLI insight command"),
            ("5", "Dashboard", "Streamlit KPI cards · charts · quarantine expander · run history"),
            ("6", "Evaluate", "pytest: idempotency · quarantine · HTTP · quality gate block"),
        ]
        c = self.c
        y = H - 1.15 * inch
        for num, name, desc in phases:
            c.setFillColor(BLUE)
            c.circle(0.75 * inch, y + 0.06 * inch, 0.14 * inch, fill=1, stroke=0)
            c.setFillColor(WHITE)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(0.75 * inch, y + 0.02 * inch, num)
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(1.05 * inch, y + 0.08 * inch, name)
            c.setFont("Helvetica", 10)
            c.setFillColor(GRAY)
            c.drawString(1.05 * inch, y - 0.14 * inch, desc)
            if num != "6":
                c.setStrokeColor(BORDER)
                c.line(0.75 * inch, y - 0.28 * inch, 0.75 * inch, y - 0.48 * inch)
            y -= 0.72 * inch
        c.showPage()

    def eval_matrix(self, title: str):
        self.table_slide(
            title,
            ["Criterion", "Method", "Result"],
            [
                ["End-to-end CSV run", "etl run --source demo", "PASS"],
                ["Idempotent re-ingest", "Same file twice → 0 rows", "PASS"],
                ["Quarantine isolation", "4 bad rows → quarantine", "PASS"],
                ["Gold marts built", "KPIs + volume + SKU SQL", "PASS"],
                ["Quality gate blocks", "35% threshold test", "PASS"],
                ["HTTP JSON source", "file: + httpx mock", "PASS"],
                ["Dashboard renders", "Streamlit manual check", "PASS"],
                ["Test suite", "pytest (9 tests)", "9/9 PASS"],
            ],
            subtitle="Automated + manual acceptance",
        )

    def closing(self, title: str, lines: list[str]):
        self._header(title)
        c = self.c
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 18)
        y = H / 2 + 0.3 * inch
        for line in lines:
            c.drawCentredString(W / 2, y, line)
            y -= 0.35 * inch
        c.showPage()


def build():
    deck = SlideDeck(PDF_PATH)

    deck.title_slide(
        "Operator ETL",
        "Specification · Architecture · Build · Evaluation",
        [
            "Version 1.0  ·  August 2026",
            "Local-first medallion pipeline: intake → warehouse → insights",
            "Repository: https://github.com/khaosans/operator-etl",
        ],
    )

    deck.bullets(
        "Agenda",
        [
            "Problem & goals",
            "System specification",
            "Architecture & diagrams",
            "How it looks (CLI + dashboard)",
            "Building process",
            "Evaluation & demo results",
            "Roadmap & recommendation",
        ],
    )

    deck.bullets(
        "Problem",
        [
            "Silent bad data — invalid rows appear in dashboards without visibility",
            "No idempotency — re-running the same file double-counts records",
            "Tight coupling — each new source needs a new script",
            "Overconfident outputs — charts render when upstream data is broken",
            "No audit trail — operators can't answer what ran, when, or what failed",
        ],
    )

    deck.two_column(
        "Goals & non-goals",
        "Goals (v1)",
        [
            "Trustworthy intake — raw preserved, validate before silver",
            "Operator clarity — run logs, quarantine reasons",
            "Extensible sources via YAML registry",
            "Local-first — DuckDB on disk, no cloud required",
            "Deterministic ETL — Python + SQL, no LLM in critical path",
        ],
        "Non-goals (v1)",
        [
            "Cloud warehouse / hosted dashboard",
            "Airflow, Spark, Kafka, streaming",
            "LLM-generated insights",
            "Multi-tenant SaaS",
            "Domain adapters (Substack, finance) — later via registry",
        ],
    )

    deck.bullets(
        "Specification — one sentence",
        [
            "Drop a CSV or call an API → store raw data immutably in bronze",
            "Validate and type rows into silver; reject bad rows to quarantine",
            "Compute gold metrics in SQL; surface KPIs in CLI or dashboard",
            "Withhold insights when quality gates fail — fail closed, not optimistic",
            "New sources = one registry entry; pipeline runner stays the same",
        ],
        subtitle="What the system guarantees",
    )

    deck.pipeline_flow("Architecture diagram")

    deck.table_slide(
        "Specification — layers",
        ["Layer", "Responsibility", "Technology"],
        [
            ["Extract", "Read files/APIs, SHA-256 hash", "Python, httpx"],
            ["Bronze", "Immutable raw JSON + metadata", "DuckDB"],
            ["Transform", "Validate, type, dedupe", "Pydantic v2"],
            ["Quarantine", "Isolate bad rows + error reason", "DuckDB"],
            ["Gold", "Aggregated SQL marts", "DuckDB SQL"],
            ["Insights", "KPIs when quality passes", "CLI, Streamlit"],
            ["Orchestration", "Run logging, CLI commands", "Typer"],
        ],
    )

    deck.table_slide(
        "Specification — sources",
        ["Source", "Kind", "Input", "Purpose"],
        [
            ["demo", "csv", "samples/orders.csv", "Demo & tests"],
            ["inbox", "csv_dir", "drops/inbox/*.csv", "Operator drop folder"],
            ["http", "http", "GET JSON list", "API intake stub"],
        ],
        subtitle="pipelines/demo.yaml registry",
    )

    deck.table_slide(
        "Specification — warehouse schema",
        ["Table / mart", "Contents"],
        [
            ["ingest_files", "File hash registry (idempotency)"],
            ["pipeline_runs", "Run audit: counts, status, timestamps"],
            ["bronze_raw", "Raw JSON + _source, _ingested_at, _row_num"],
            ["silver_orders", "Validated typed business rows"],
            ["quarantine_orders", "Rejected rows + error message"],
            ["gold_kpis / gold_volume_daily / gold_top_skus", "Aggregated metrics"],
            ["gold_quality", "Quarantine rate, freshness, row counts"],
        ],
    )

    deck.table_slide(
        "Specification — silver contract",
        ["Field", "Type", "Rule"],
        [
            ["order_id", "string", "Required, non-empty, unique"],
            ["customer_id", "string", "Required"],
            ["ordered_at", "datetime", "Parseable ISO timestamp"],
            ["amount", "float", "Must be > 0"],
            ["sku", "string", "Required"],
            ["status", "string", "Required"],
        ],
        subtitle="Pydantic validation — invalid → quarantine, not crash",
    )

    deck.table_slide(
        "Specification — quality gate",
        ["Check", "Default", "On failure"],
        [
            ["Quarantine rate", "≤ 35%", "KPIs withheld"],
            ["Freshness", "≤ 7 days since ingest", "KPIs withheld"],
            ["Silver rows", "> 0", "KPIs withheld"],
        ],
        subtitle="Fail-closed — quality panel still visible when blocked",
    )

    deck.diagram_box(
        "Diagram — idempotency flow",
        [
            "  [New file] ──▶ SHA-256 hash ──▶ hash in ingest_files?",
            "                                      │",
            "                         NO ◀─────────┴─────────▶ YES → skip (0 rows)",
            "                          │",
            "                          ▼",
            "                   load bronze_raw",
            "                          │",
            "                          ▼",
            "              transform → silver OR quarantine",
        ],
        subtitle="Same file twice never double-counts",
    )

    deck.cli_mock("How it looks — CLI")

    deck.dashboard_mock("How it looks — dashboard")

    deck.build_phases("Building process")

    deck.diagram_box(
        "Building process — repo layout",
        [
            "operator-etl/",
            "  pipelines/demo.yaml     ← source registry",
            "  samples/                ← demo CSV + HTTP JSON",
            "  drops/inbox/            ← operator CSV drop",
            "  sql/marts/              ← gold SQL",
            "  src/operator_etl/       ← extract · load · transform · insights",
            "  dashboard/app.py        ← Streamlit UI",
            "  tests/                  ← pytest suite",
            "  warehouse/operator.duckdb  (gitignored)",
        ],
    )

    deck.table_slide(
        "Evaluation — success criteria",
        ["#", "Criterion", "Status"],
        [
            ["1", "CSV in drop folder runs end-to-end", "Met"],
            ["2", "Invalid rows → quarantine", "Met"],
            ["3", "KPIs: freshness, volume, SKU breakdown", "Met"],
            ["4", "Re-ingest same file → 0 duplicate rows", "Met"],
            ["5", "Quality gate blocks bad KPIs", "Met"],
            ["6", "HTTP JSON source works", "Met"],
            ["7", "Automated test coverage", "9/9 pass"],
        ],
    )

    deck.table_slide(
        "Evaluation — test matrix",
        ["Test", "Validates", "Result"],
        [
            ["test_ingest_is_idempotent", "Hash skip on re-run", "PASS"],
            ["test_quarantine_invalid_rows", "4 bad rows isolated", "PASS"],
            ["test_run_builds_gold", "KPIs + gate pass", "PASS"],
            ["test_quality_gate_blocks", "KPIs blocked > threshold", "PASS"],
            ["test_http_*", "JSON extract + warehouse", "PASS"],
            ["test_source_registry", "demo, inbox, http", "PASS"],
        ],
    )

    deck.table_slide(
        "Evaluation — demo run results",
        ["Metric", "Value"],
        [
            ["Input rows (demo CSV)", "21"],
            ["Silver (valid)", "17"],
            ["Quarantined", "4"],
            ["Quarantine rate", "19.1% → gate PASS"],
            ["Re-run same file", "0 new rows (hash skip)"],
            ["Revenue (gold)", "1373.82"],
            ["Top SKU", "SKU-PRO"],
        ],
        subtitle="etl run --source demo",
    )

    deck.three_planes("Roadmap — agentic evolution (v2)")

    deck.table_slide(
        "Roadmap",
        ["Phase", "Capability"],
        [
            ["v1.0", "Medallion ETL + CLI + dashboard (current)"],
            ["v1.1", "Real source adapters (Substack, finance CSV)"],
            ["v1.2", "Postgres/Supabase + scheduled runs"],
            ["v2.0", "LangGraph · PII gate · insight agent · critic · HITL"],
            ["v2.1", "Hosted dashboard · Langfuse observability"],
        ],
    )

    deck.bullets(
        "Recommendation",
        [
            "Adopt v1 as the deterministic data plane — boring, testable, trustworthy",
            "Confirm canonical schema for first production data source",
            "Approve quality gate thresholds before live use",
            "Add v1.1 source adapter next; defer agentic layer until metrics are stable",
            "v2 agents orchestrate on top — they never replace ETL or bypass quarantine",
        ],
        subtitle="Proposed next steps",
    )

    deck.closing(
        "Thank you",
        [
            "Operator ETL v1",
            "Intake → warehouse → insights",
            "Questions?",
        ],
    )

    deck.save()
    print(f"Wrote {PDF_PATH} ({deck.page} slides)")


if __name__ == "__main__":
    build()
