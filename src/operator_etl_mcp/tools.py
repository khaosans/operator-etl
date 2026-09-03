from __future__ import annotations

import json
from pathlib import Path

import yaml

from operator_etl.config import Settings, get_settings
from telemetry.tracer import span


class ToolDenied(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


def load_allowlist(settings: Settings | None = None) -> dict:
    settings = settings or get_settings()
    path = settings.root / "sql" / "allowlist.yaml"
    with path.open() as fh:
        return yaml.safe_load(fh)


def run_allowlisted_sql(con, query_id: str, node: str = "quality_agent", settings: Settings | None = None) -> dict:
    with span("operator_etl.mcp.run_quality_sql", attributes={"query_id": query_id, "node": node}):
        spec = load_allowlist(settings)
        for entry in spec.get("queries", []):
            if entry["id"] == query_id:
                if node not in entry.get("allowed_nodes", []):
                    raise ToolDenied(f"node {node} not allowed for query {query_id}")
                rows = con.execute(entry["sql"]).fetchall()
                cols = [d[0] for d in con.description] if con.description else []
                return {"columns": cols, "rows": [list(r) for r in rows]}
        raise ToolDenied(f"query_id {query_id!r} not in allowlist")


def get_gold_metrics(con, domain: str = "gov") -> dict:
    with span("operator_etl.mcp.get_gold_metrics", attributes={"domain": domain}):
        if domain == "gov":
            row = con.execute("SELECT * FROM gold_comment_kpis").fetchone()
            if not row:
                return {}
            cols = [d[0] for d in con.description]
            return dict(zip(cols, row, strict=True))
        row = con.execute("SELECT * FROM gold_kpis").fetchone()
        if not row:
            return {}
        cols = [d[0] for d in con.description]
        return dict(zip(cols, row, strict=True))


def get_run_status(con, run_id: str) -> dict:
    """Return pipeline_runs audit row for get_run_status MCP tool."""
    with span("operator_etl.mcp.get_run_status", attributes={"run_id": run_id}):
        row = con.execute("SELECT * FROM pipeline_runs WHERE run_id = ?", [run_id]).fetchone()
        if not row:
            return {"error": "NOT_FOUND"}
        cols = [d[0] for d in con.description]
        return dict(zip(cols, row, strict=True))
