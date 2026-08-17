# Operator ETL — Cloud Run image (graph-runner + MCP)
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
COPY sql ./sql
COPY pipelines ./pipelines
COPY samples ./samples

RUN uv sync --frozen --extra gcp --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8080

# Default: graph-runner HTTP service (override in Cloud Run)
CMD ["uvicorn", "operator_etl_gcp.http.app:app", "--host", "0.0.0.0", "--port", "8080"]
