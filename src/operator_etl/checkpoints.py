"""LangGraph checkpoint backends — sqlite (local) or postgres (any cloud)."""

from __future__ import annotations

from operator_etl.config import Settings, get_settings


def build_checkpointer(settings: Settings | None = None):
    settings = settings or get_settings()
    if settings.checkpoint_backend == "postgres":
        if not settings.checkpoint_database_url:
            raise ValueError(
                "OPERATOR_ETL_CHECKPOINT_DATABASE_URL required for postgres checkpoints"
            )
        from langgraph.checkpoint.postgres import PostgresSaver

        return PostgresSaver.from_conn_string(settings.checkpoint_database_url)

    import sqlite3

    from langgraph.checkpoint.sqlite import SqliteSaver

    settings.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(settings.checkpoint_path), check_same_thread=False)
    return SqliteSaver(conn)
