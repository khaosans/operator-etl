from __future__ import annotations

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool, ToolAnnotations

from operator_etl.config import Settings, get_settings, set_settings
from operator_etl.load.connection import connect
from operator_etl_mcp.tools import ToolDenied, get_gold_metrics, get_run_status, run_allowlisted_sql

server = Server("operator-etl")

READ_ONLY_LOCAL = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_gold_metrics",
            description="Return gold KPI aggregates (no row-level data).",
            inputSchema={"type": "object", "properties": {"domain": {"type": "string", "default": "gov"}}, "required": []},
            annotations=READ_ONLY_LOCAL,
        ),
        Tool(
            name="run_quality_sql",
            description="Run an allowlisted quality query by id.",
            inputSchema={
                "type": "object",
                "properties": {"query_id": {"type": "string"}, "node": {"type": "string", "default": "quality_agent"}},
                "required": ["query_id"],
            },
            annotations=READ_ONLY_LOCAL,
        ),
        Tool(
            name="get_run_status",
            description="Return pipeline run audit row.",
            inputSchema={"type": "object", "properties": {"run_id": {"type": "string"}}, "required": ["run_id"]},
            annotations=READ_ONLY_LOCAL,
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    settings = get_settings()
    con = connect(settings)
    try:
        if name == "get_gold_metrics":
            domain = arguments.get("domain", "gov")
            data = get_gold_metrics(con, domain=domain)
            return [TextContent(type="text", text=json.dumps(data, default=str))]
        if name == "run_quality_sql":
            try:
                data = run_allowlisted_sql(con, arguments["query_id"], node=arguments.get("node", "quality_agent"), settings=settings)
            except ToolDenied as exc:
                return [TextContent(type="text", text=json.dumps({"error": "TOOL_DENIED", "reason": str(exc)}))]
            return [TextContent(type="text", text=json.dumps(data, default=str))]
        if name == "get_run_status":
            data = get_run_status(con, arguments["run_id"])
            return [TextContent(type="text", text=json.dumps(data, default=str))]
        return [TextContent(type="text", text=json.dumps({"error": "UNKNOWN_TOOL"}))]
    finally:
        con.close()


async def _main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    gov = Settings(pipeline_name="public_comments", domain="gov")
    set_settings(gov)
    asyncio.run(_main())


if __name__ == "__main__":
    main()
