#!/usr/bin/env python3
"""Generate publication-grade PNG diagrams for Operator ETL White Paper."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / "docs" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

# Color Palette
BG_DARK = (15, 23, 42)        # #0F172A
BG_CARD = (30, 41, 59)        # #1E293B
BG_LIGHT_CARD = (51, 65, 85)  # #334155
BLUE = (37, 99, 235)          # #2563EB
TEAL = (13, 148, 136)         # #0D9488
GREEN = (5, 150, 105)         # #059669
AMBER = (217, 119, 6)         # #D97706
WHITE = (255, 255, 255)
SLATE_LIGHT = (203, 213, 225) # #CBD5E1
SLATE_MUTED = (148, 163, 184) # #94A3B8
BORDER_COLOR = (71, 85, 105)  # #475569

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    try:
        # Try standard system fonts
        font_name = "Helvetica-Bold" if bold else "Helvetica"
        return ImageFont.truetype(f"/System/Library/Fonts/{font_name}.ttc", size)
    except Exception:
        try:
            font_name = "Arial Bold.ttf" if bold else "Arial.ttf"
            return ImageFont.truetype(f"/System/Library/Fonts/Supplemental/{font_name}", size)
        except Exception:
            return ImageFont.load_default()

def draw_rounded_card(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    bg: tuple[int, int, int],
    border: tuple[int, int, int] | None = None,
    radius: int = 12,
    border_width: int = 2,
):
    x0, y0, x1, y1 = xy
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=bg, outline=border, width=border_width)

def draw_badge(
    draw: ImageDraw.ImageDraw,
    text: str,
    top_right: tuple[int, int],
    bg: tuple[int, int, int],
    font: ImageFont.ImageFont,
):
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 10, 4
    x1, y0 = top_right
    x0 = x1 - tw - pad_x * 2
    y1 = y0 + th + pad_y * 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=bg)
    draw.text((x0 + pad_x, y0 + pad_y - bbox[1]), text, fill=WHITE, font=font)

def create_three_planes_diagram() -> None:
    w, h = 1400, 600
    img = Image.new("RGB", (w, h), BG_DARK)
    draw = ImageDraw.Draw(img)

    f_title = get_font(26, bold=True)
    f_header = get_font(20, bold=True)
    f_body = get_font(15, bold=False)
    f_badge = get_font(12, bold=True)
    f_arrow = get_font(14, bold=True)

    # Title
    draw.text((50, 25), "OPERATOR ETL: THE THREE-PLANE TRUST ARCHITECTURE", fill=WHITE, font=f_title)
    draw.text((50, 60), "Decoupling deterministic data transformations from agentic orchestration and security policy", fill=SLATE_MUTED, font=f_body)

    # 3 Column Cards
    col_w = 400
    gap = 40
    y_top = 110
    card_h = 440

    # Plane 1: Control Plane
    x1 = 50
    draw_rounded_card(draw, (x1, y_top, x1 + col_w, y_top + card_h), BG_CARD, border=BLUE, radius=12, border_width=2)
    draw_badge(draw, "IMPLEMENTED", (x1 + col_w - 15, y_top + 15), BLUE, f_badge)
    draw.text((x1 + 20, y_top + 20), "CONTROL PLANE", fill=BLUE, font=f_header)
    draw.text((x1 + 20, y_top + 50), "LangGraph State Machine", fill=WHITE, font=f_body)
    
    ctrl_bullets = [
        "• Explicit state machine & checkpoints",
        "• Deterministic numeric Critic audit",
        "• Automatic HITL interrupt on anomaly",
        "• Resumable crash recovery (SQLite/PG)",
        "• Zero unconstrained chat loops"
    ]
    for idx, b in enumerate(ctrl_bullets):
        draw.text((x1 + 20, y_top + 100 + idx * 35), b, fill=SLATE_LIGHT, font=f_body)

    # Plane 2: Policy Plane
    x2 = x1 + col_w + gap
    draw_rounded_card(draw, (x2, y_top, x2 + col_w, y_top + card_h), BG_CARD, border=TEAL, radius=12, border_width=2)
    draw_badge(draw, "IMPLEMENTED", (x2 + col_w - 15, y_top + 15), TEAL, f_badge)
    draw.text((x2 + 20, y_top + 20), "POLICY PLANE", fill=TEAL, font=f_header)
    draw.text((x2 + 20, y_top + 50), "Zero-PII & Isolation Boundary", fill=WHITE, font=f_body)

    pol_bullets = [
        "• Automated regex & Presidio PII scan",
        "• Isolated AES-256 cryptographic vault",
        "• Replaces PII with synthetic tokens",
        "• LLM context & traces 100% sanitized",
        "• Fail-closed budget & spend caps"
    ]
    for idx, b in enumerate(pol_bullets):
        draw.text((x2 + 20, y_top + 100 + idx * 35), b, fill=SLATE_LIGHT, font=f_body)

    # Plane 3: Data Plane
    x3 = x2 + col_w + gap
    draw_rounded_card(draw, (x3, y_top, x3 + col_w, y_top + card_h), BG_CARD, border=GREEN, radius=12, border_width=2)
    draw_badge(draw, "IMPLEMENTED", (x3 + col_w - 15, y_top + 15), GREEN, f_badge)
    draw.text((x3 + 20, y_top + 20), "DATA PLANE", fill=GREEN, font=f_header)
    draw.text((x3 + 20, y_top + 50), "Deterministic Medallion", fill=WHITE, font=f_body)

    data_bullets = [
        "• Bronze: SHA-256 idempotent raw intake",
        "• Silver: Pydantic typed business entities",
        "• Quarantine: Dead-letter error audit",
        "• Gold: Pure SQL aggregation marts",
        "• Bit-identical replay & zero silent loss"
    ]
    for idx, b in enumerate(data_bullets):
        draw.text((x3 + 20, y_top + 100 + idx * 35), b, fill=SLATE_LIGHT, font=f_body)

    # Horizontal connectors / Footers
    draw.line([(x1 + col_w, y_top + 220), (x2, y_top + 220)], fill=BORDER_COLOR, width=3)
    draw.line([(x2 + col_w, y_top + 220), (x3, y_top + 220)], fill=BORDER_COLOR, width=3)

    img.save(ASSETS / "three-planes.png", "PNG", dpi=(300, 300))
    print(f"Generated {ASSETS / 'three-planes.png'}")

def create_mcp_flow_diagram() -> None:
    w, h = 1400, 520
    img = Image.new("RGB", (w, h), BG_DARK)
    draw = ImageDraw.Draw(img)

    f_title = get_font(26, bold=True)
    f_header = get_font(18, bold=True)
    f_body = get_font(14, bold=False)
    f_code = get_font(13, bold=False)
    f_badge = get_font(12, bold=True)

    draw.text((50, 25), "MODEL CONTEXT PROTOCOL (MCP) SECURITY BOUNDARY", fill=WHITE, font=f_title)
    draw.text((50, 60), "Agents query typed allowlisted tools; raw database access and vault decryption are denied", fill=SLATE_MUTED, font=f_body)

    # Node 1: AI Agent
    draw_rounded_card(draw, (50, 110, 350, 460), BG_CARD, border=BLUE, radius=12)
    draw.text((70, 130), "AI AGENT CLIENT", fill=BLUE, font=f_header)
    draw.text((70, 160), "Cursor / Cloud Agent", fill=WHITE, font=f_body)
    agent_lines = [
        "• Evaluates context",
        "• Requests Gold KPIs",
        "• Diagnoses quality",
        "• Drafts summary memo",
        "• Subject to token budget"
    ]
    for idx, l in enumerate(agent_lines):
        draw.text((70, 210 + idx * 35), l, fill=SLATE_LIGHT, font=f_body)

    # Node 2: MCP Server Boundary
    draw_rounded_card(draw, (430, 110, 930, 460), BG_CARD, border=TEAL, radius=12)
    draw_badge(draw, "SECURITY GATEWAY", (910, 125), TEAL, f_badge)
    draw.text((450, 130), "OPERATOR-ETL MCP SERVER", fill=TEAL, font=f_header)
    draw.text((450, 160), "Allowlist Enforcement & Validation", fill=WHITE, font=f_body)
    
    # Subcard inside MCP: Allowed Tools
    draw_rounded_card(draw, (450, 200, 670, 435), BG_DARK, border=GREEN, radius=8)
    draw.text((465, 215), "ALLOWLISTED TOOLS (OK)", fill=GREEN, font=get_font(14, bold=True))
    allowed = ["get_gold_metrics", "run_quality_sql", "get_run_status", "persist_insight"]
    for idx, t in enumerate(allowed):
        draw.text((465, 255 + idx * 40), f"✓ {t}", fill=SLATE_LIGHT, font=f_code)

    # Subcard inside MCP: Denied Capabilities
    draw_rounded_card(draw, (690, 200, 910, 435), BG_DARK, border=AMBER, radius=8)
    draw.text((705, 215), "HARD DENIALS (FAIL)", fill=AMBER, font=get_font(14, bold=True))
    denied = ["vault_decrypt", "execute_raw_sql", "read_bronze_pii", "drop_table"]
    for idx, t in enumerate(denied):
        draw.text((705, 255 + idx * 40), f"✗ {t}", fill=SLATE_LIGHT, font=f_code)

    # Node 3: Warehouse & Storage
    draw_rounded_card(draw, (1010, 110, 1350, 460), BG_CARD, border=GREEN, radius=12)
    draw.text((1030, 130), "DATA PLANE", fill=GREEN, font=f_header)
    draw.text((1030, 160), "DuckDB / BigQuery Marts", fill=WHITE, font=f_body)
    wh_lines = [
        "• gold_comment_kpis",
        "• gold_comments_by_agency",
        "• gold_comment_quality",
        "• pii_vault (ISOLATED)",
        "• bronze_raw (IMMUTABLE)"
    ]
    for idx, l in enumerate(wh_lines):
        draw.text((1030, 210 + idx * 35), l, fill=SLATE_LIGHT, font=f_body)

    # Connecting Arrows
    draw.line([(350, 280), (430, 280)], fill=BLUE, width=4)
    draw.line([(930, 280), (1010, 280)], fill=GREEN, width=4)

    img.save(ASSETS / "mcp-agent-flow.png", "PNG", dpi=(300, 300))
    print(f"Generated {ASSETS / 'mcp-agent-flow.png'}")

def create_gcp_cloud_diagram() -> None:
    w, h = 1400, 520
    img = Image.new("RGB", (w, h), BG_DARK)
    draw = ImageDraw.Draw(img)

    f_title = get_font(26, bold=True)
    f_header = get_font(18, bold=True)
    f_body = get_font(14, bold=False)
    f_badge = get_font(12, bold=True)

    draw.text((50, 25), "ENTERPRISE CLOUD ARCHITECTURE (GCP STAGING)", fill=WHITE, font=f_title)
    draw.text((50, 60), "Event-driven, serverless execution across Google Cloud Storage, Cloud Run, and BigQuery", fill=SLATE_MUTED, font=f_body)

    col_w = 380
    gap = 40
    y_top = 110
    card_h = 360

    # Stage 1: Ingestion Trigger
    x1 = 50
    draw_rounded_card(draw, (x1, y_top, x1 + col_w, y_top + card_h), BG_CARD, border=BLUE, radius=12)
    draw.text((x1 + 20, y_top + 25), "1. EVENT INTAKE", fill=BLUE, font=f_header)
    draw.text((x1 + 20, y_top + 55), "Cloud Storage & Pub/Sub", fill=WHITE, font=f_body)
    s1_items = [
        "• File dropped in gs://inbox",
        "• Cloud Storage Object Finalize",
        "• Pub/Sub topic notifications",
        "• At-least-once delivery guarantee",
        "• Dead-letter queue (DLQ) retry"
    ]
    for idx, item in enumerate(s1_items):
        draw.text((x1 + 20, y_top + 110 + idx * 35), item, fill=SLATE_LIGHT, font=f_body)

    # Stage 2: Container Execution
    x2 = x1 + col_w + gap
    draw_rounded_card(draw, (x2, y_top, x2 + col_w, y_top + card_h), BG_CARD, border=TEAL, radius=12)
    draw.text((x2 + 20, y_top + 25), "2. PIPELINE RUNNER", fill=TEAL, font=f_header)
    draw.text((x2 + 20, y_top + 55), "Cloud Run & LangGraph", fill=WHITE, font=f_body)
    s2_items = [
        "• Serverless container execution",
        "• LangGraph StateGraph runner",
        "• Secret Manager key injection",
        "• Cloud SQL PostgreSQL saver",
        "• Memory & CPU auto-scaling"
    ]
    for idx, item in enumerate(s2_items):
        draw.text((x2 + 20, y_top + 110 + idx * 35), item, fill=SLATE_LIGHT, font=f_body)

    # Stage 3: Analytical Storage
    x3 = x2 + col_w + gap
    draw_rounded_card(draw, (x3, y_top, x3 + col_w, y_top + card_h), BG_CARD, border=GREEN, radius=12)
    draw.text((x3 + 20, y_top + 25), "3. ANALYTICAL MARTS", fill=GREEN, font=f_header)
    draw.text((x3 + 20, y_top + 55), "BigQuery Lakehouse", fill=WHITE, font=f_body)
    s3_items = [
        "• etl_bronze: raw_events partitioned",
        "• etl_silver: comments partitioned",
        "• etl_quarantine: rejected records",
        "• etl_gold: audited KPI marts",
        "• IAM role-based access control"
    ]
    for idx, item in enumerate(s3_items):
        draw.text((x3 + 20, y_top + 110 + idx * 35), item, fill=SLATE_LIGHT, font=f_body)

    # Connecting Lines
    draw.line([(x1 + col_w, y_top + 180), (x2, y_top + 180)], fill=BLUE, width=4)
    draw.line([(x2 + col_w, y_top + 180), (x3, y_top + 180)], fill=TEAL, width=4)

    img.save(ASSETS / "gcp-architecture.png", "PNG", dpi=(300, 300))
    print(f"Generated {ASSETS / 'gcp-architecture.png'}")

def create_cover_hero() -> None:
    w, h = 1600, 900
    img = Image.new("RGB", (w, h), (10, 15, 30))
    draw = ImageDraw.Draw(img)

    f_huge = get_font(52, bold=True)
    f_sub = get_font(24, bold=False)
    f_tag = get_font(18, bold=True)

    # Subtle grid lines in background
    for x in range(0, w, 80):
        draw.line([(x, 0), (x, h)], fill=(20, 30, 50), width=1)
    for y in range(0, h, 80):
        draw.line([(0, y), (w, y)], fill=(20, 30, 50), width=1)

    # Glowing geometric shapes
    draw.rounded_rectangle([100, 100, 1500, 800], radius=24, outline=BLUE, width=3)
    draw.rounded_rectangle([130, 130, 1470, 770], radius=16, fill=(15, 23, 42))

    # Header tags
    draw.rounded_rectangle([180, 180, 480, 230], radius=8, fill=BLUE)
    draw.text((200, 192), "ENTERPRISE SYSTEMS SPECIFICATION", fill=WHITE, font=f_tag)

    draw.text((180, 270), "Operator ETL: Agentic Data Platform", fill=WHITE, font=f_huge)
    draw.text((180, 350), "Deterministic Medallion Warehouses · Bounded MCP Agents · Zero-PII Policy Plane", fill=SLATE_MUTED, font=f_sub)

    # 3 Pill Badges
    pills = [
        ("DATA PLANE", "Bronze ➔ Silver ➔ Gold SQL", GREEN),
        ("POLICY PLANE", "AES-256 Vault & Redaction", TEAL),
        ("CONTROL PLANE", "LangGraph + Critic Verification", BLUE)
    ]
    for idx, (p_title, p_desc, p_col) in enumerate(pills):
        px = 180 + idx * 420
        py = 460
        draw_rounded_card(draw, (px, py, px + 380, py + 220), BG_DARK, border=p_col, radius=12)
        draw.text((px + 24, py + 30), p_title, fill=p_col, font=get_font(20, bold=True))
        draw.text((px + 24, py + 75), p_desc, fill=WHITE, font=get_font(15, bold=False))
        draw.text((px + 24, py + 120), "• Fail-closed governance\n• 59 pytest test suite passing\n• Zero raw PII in agent context", fill=SLATE_LIGHT, font=get_font(13, bold=False))

    img.save(ASSETS / "cover-hero.png", "PNG", dpi=(300, 300))
    print(f"Generated {ASSETS / 'cover-hero.png'}")

if __name__ == "__main__":
    create_three_planes_diagram()
    create_mcp_flow_diagram()
    create_gcp_cloud_diagram()
    create_cover_hero()
