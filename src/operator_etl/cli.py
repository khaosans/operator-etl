from __future__ import annotations

# Streamlit dashboard launcher — argv is constructed here, not from user input.
import subprocess  # nosec B404
import sys
from typing import Optional

import typer

from operator_etl.config import get_settings
from operator_etl.insights.metrics import render_insights
from operator_etl.load.duckdb import connect
from operator_etl.pipeline import ingest_source, run_pipeline
from operator_etl.sources import list_sources

app = typer.Typer(no_args_is_help=True, help="Intake files/APIs, land them in DuckDB, print insights.")


@app.command()
def ingest(
    source: str = typer.Option("demo", "--source", "-s", help="Registered source name"),
) -> None:
    """Load bronze from a source. Same file hash is skipped."""
    result = ingest_source(source)
    typer.echo(
        f"ingest {result.status}  source={result.source}  rows_in={result.rows_in}  "
        f"files_skipped={result.files_skipped}  run_id={result.run_id}"
    )


@app.command("run")
def run_cmd(
    source: str = typer.Option("demo", "--source", "-s", help="Registered source name"),
) -> None:
    """Ingest → silver/quarantine → gold marts → insights."""
    result = run_pipeline(source)
    typer.echo(
        f"run {result.status}  source={result.source}  rows_in={result.rows_in}  "
        f"silver={result.rows_silver}  quarantined={result.rows_quarantined}  "
        f"files_skipped={result.files_skipped}  run_id={result.run_id}"
    )
    if result.insights:
        typer.echo("")
        typer.echo(result.insights)


@app.command()
def insight() -> None:
    """Print gold KPIs if the quality gate passes."""
    settings = get_settings()
    if not settings.warehouse_path.exists():
        typer.echo("Warehouse missing. Run `etl run --source demo` first.", err=True)
        raise typer.Exit(1)
    con = connect(settings)
    try:
        typer.echo(render_insights(con, settings))
    finally:
        con.close()


@app.command()
def sources() -> None:
    """List sources from pipelines/demo.yaml."""
    for name in list_sources():
        typer.echo(name)


@app.command()
def dashboard() -> None:
    """Open the Streamlit run inspector."""
    import os

    settings = get_settings()
    os.environ["OPERATOR_ETL_WAREHOUSE"] = str(settings.warehouse_path)
    cmd = [sys.executable, "-m", "streamlit", "run", str(settings.dashboard_path)]
    raise typer.Exit(subprocess.call(cmd, shell=False))  # nosec B603


@app.command("hitl-approve")
def hitl_approve(
    run_id: str = typer.Argument(..., help="Pipeline run_id needing officer sign-off"),
    officer: str = typer.Option("officer", "--officer", "-o"),
    reason: str = typer.Option("approved for release review", "--reason", "-r"),
) -> None:
    """Record an officer approve decision (audit only — does not auto-publish)."""
    from operator_etl_policy.hitl import HitlStore

    decision = HitlStore().decide(run_id, "approve", officer=officer, reason=reason)
    typer.echo(f"hitl approve run_id={decision.run_id} officer={decision.officer} at={decision.decided_at}")


@app.command("hitl-reject")
def hitl_reject(
    run_id: str = typer.Argument(..., help="Pipeline run_id to reject"),
    officer: str = typer.Option("officer", "--officer", "-o"),
    reason: str = typer.Option("rejected — needs remediation", "--reason", "-r"),
) -> None:
    """Record an officer reject decision (audit only — never auto-publishes)."""
    from operator_etl_policy.hitl import HitlStore

    decision = HitlStore().decide(run_id, "reject", officer=officer, reason=reason)
    typer.echo(f"hitl reject run_id={decision.run_id} officer={decision.officer} reason={decision.reason}")


def main(argv: Optional[list[str]] = None) -> None:
    app(args=argv)


if __name__ == "__main__":
    app()
