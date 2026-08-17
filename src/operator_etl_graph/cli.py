from __future__ import annotations

import typer

from operator_etl.config import Settings, get_settings, set_settings
from operator_etl_graph.graph import run_graph

app = typer.Typer(no_args_is_help=True, help="Run the agentic FOIA / public comments graph pipeline.")


@app.command("run")
def run_cmd(
    source: str = typer.Option("public_comments", "--source", "-s"),
    pipeline: str = typer.Option("public_comments", "--pipeline", "-p"),
) -> None:
    settings = Settings(pipeline_name=pipeline, domain="gov")
    set_settings(settings)
    result = run_graph(source=source, settings=settings)
    typer.echo(f"status={result.get('status')}  run_id={result.get('run_id')}")
    typer.echo(f"rows_in={result.get('rows_in')}  silver={result.get('rows_silver')}  quarantined={result.get('rows_quarantined')}")
    if result.get("pii_findings"):
        typer.echo(f"pii_findings={len(result['pii_findings'])}")
    if result.get("insight_draft"):
        typer.echo("")
        typer.echo(result["insight_draft"])
    if result.get("errors"):
        typer.echo(f"errors={result['errors']}")


if __name__ == "__main__":
    app()
