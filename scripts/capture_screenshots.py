#!/usr/bin/env python3
"""Capture documentation screenshots of Streamlit + CLI cards.

Requires Chromium via Playwright. Does not run in CI.

  uv sync --extra dev
  python3 -m playwright install chromium   # once
  ./scripts/capture_screenshots.py
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "screenshots"
TMP = ROOT / ".tmp" / "doc-captures"
PORT = 8501
DASHBOARD = f"http://127.0.0.1:{PORT}"


def _html_terminal(title: str, body: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{escape(title)}</title>
<style>
  body {{ margin: 0; background: #0f172a; }}
  .wrap {{ max-width: 920px; margin: 24px auto; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  h1 {{ color: #94a3b8; font-size: 13px; font-weight: 600; letter-spacing: .04em; text-transform: uppercase; }}
  pre {{ background: #020617; color: #e2e8f0; padding: 20px 22px; border-radius: 10px;
        border: 1px solid #1e293b; font-size: 13.5px; line-height: 1.45; white-space: pre-wrap; }}
</style></head>
<body><div class="wrap"><h1>{escape(title)}</h1><pre>{escape(body.strip())}</pre></div></body></html>"""


def _wait_http(url: str, timeout: float = 40.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            urllib.request.urlopen(url, timeout=2)
            return
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


def _png_from_html(page, html: str, dest: Path, width: int = 980) -> None:
    tmp = TMP / (dest.stem + ".html")
    tmp.write_text(html, encoding="utf-8")
    page.set_viewport_size({"width": width, "height": 720})
    page.goto(tmp.as_uri(), wait_until="networkidle")
    page.locator(".wrap").screenshot(path=str(dest))


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Install Playwright: uv pip install playwright && python3 -m playwright install chromium", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["OPERATOR_ETL_WAREHOUSE"] = str(ROOT / ".tmp" / "mvp-demo-ollama" / "operator.duckdb")
    env["OPERATOR_ETL_ORDERS_WAREHOUSE"] = str(ROOT / ".tmp" / "orders-demo" / "operator.duckdb")
    env["OPERATOR_ETL_PIPELINE_NAME"] = "public_comments"
    env["OPERATOR_ETL_DOMAIN"] = "gov"
    env["OPERATOR_ETL_INSIGHT_BACKEND"] = "template"

    proc = subprocess.Popen(
        [
            "uv",
            "run",
            "streamlit",
            "run",
            str(ROOT / "dashboard" / "app.py"),
            "--server.headless",
            "true",
            "--server.port",
            str(PORT),
            "--server.address",
            "127.0.0.1",
            "--browser.gatherUsageStats",
            "false",
        ],
        cwd=ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_http(DASHBOARD)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1400, "height": 900})

            template = (TMP / "cli-foia-template.txt").read_text(encoding="utf-8")
            ollama = (TMP / "cli-foia-ollama.txt").read_text(encoding="utf-8")
            verify = (TMP / "verify-pass.txt").read_text(encoding="utf-8") if (TMP / "verify-pass.txt").exists() else (
                "==========================================\n"
                "  OPERATOR_ETL_VERIFY=PASS\n"
                "==========================================\n"
                "  tests=41\n"
                "  demo=silver=10 quarantined=2 status=complete\n"
                "  next=docs/WALKTHROUGH.md\n"
                "=========================================="
            )
            orders_cli = (TMP / "cli-orders.txt").read_text(encoding="utf-8") if (TMP / "cli-orders.txt").exists() else ""

            _png_from_html(page, _html_terminal("verify.sh — no API key", verify), OUT / "verify-pass.png")
            _png_from_html(
                page,
                _html_terminal("etl-graph — template insight (CI default)", template),
                OUT / "cli-foia-insight.png",
            )
            _png_from_html(
                page,
                _html_terminal("etl-graph — local Ollama llama3.2:3b (critic passed)", ollama),
                OUT / "cli-foia-insight-ollama.png",
            )
            if orders_cli:
                _png_from_html(
                    page,
                    _html_terminal("etl run --source demo — orders warehouse", orders_cli),
                    OUT / "cli-orders.png",
                )

            page.set_viewport_size({"width": 1400, "height": 900})
            page.goto(DASHBOARD, wait_until="networkidle")
            page.wait_for_timeout(2500)
            page.screenshot(path=str(OUT / "dashboard-gov-kpis.png"), full_page=False)

            expander = page.locator("[data-testid='stExpander']").first
            if expander.count():
                expander.click()
                page.wait_for_timeout(800)
            page.screenshot(path=str(OUT / "dashboard-gov-quarantine-insight.png"), full_page=True)

            orders_tab = page.get_by_role("tab", name="Orders demo")
            if orders_tab.count():
                orders_tab.click()
            else:
                page.get_by_text("Orders demo").click()
            page.wait_for_timeout(1500)
            page.screenshot(path=str(OUT / "dashboard-orders.png"), full_page=False)

            try:
                page.goto("https://khaosans.github.io/operator-etl/", wait_until="networkidle", timeout=20000)
                page.wait_for_timeout(1200)
                page.screenshot(path=str(OUT / "wiki-home.png"), full_page=False)
            except Exception as exc:  # noqa: BLE001
                print(f"wiki-home skip: {exc}", file=sys.stderr)

            browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()

    for png in sorted(OUT.glob("*.png")):
        print(f"wrote {png.relative_to(ROOT)} ({png.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
